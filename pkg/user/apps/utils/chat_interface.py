import os
import re
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk
from langchain.schema import HumanMessage, AIMessage
from shared.core.prompts import create_system_message
from shared.core.vector_store import query_collections
from apps.utils.user_input import handle_user_input
from shared import config
from apps.utils.stage_logger import log_llm_response
 
# Load environment variables
load_dotenv()
 
speech_key = os.getenv("SPEECH_KEY")
speech_region = os.getenv("SPEECH_REGION")
 
if not speech_key or not speech_region:
    raise ValueError("Environment variables SPEECH_KEY and SPEECH_REGION are not set correctly.")
 
# Azure Speech SDK Configurations
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
speech_config.speech_recognition_language = "en-US"
speech_config.speech_synthesis_voice_name = 'en-US-AvaMultilingualNeural'
audio_output = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_output)
 
# Function: Text-to-Speech
def text_to_speech(text):
    speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()
    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"Speech synthesized for text: {text}")
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print(f"Speech synthesis canceled: {cancellation_details.reason}")
 
# Function: Speech-to-Text
def speech_to_text():
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    print("Speak into your microphone...")
    speech_recognition_result = speech_recognizer.recognize_once_async().get()
    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return speech_recognition_result.text
    elif speech_recognition_result.reason in [speechsdk.ResultReason.NoMatch, speechsdk.ResultReason.Canceled]:
        return None
 
# Function: Display Chat History
def display_chat_history():
    # Display all messages including the initial system message
    for message in st.session_state.messages:
        if isinstance(message, AIMessage):
            clean_response = re.sub(r'<think>.*?</think>', '', message.content, flags=re.DOTALL)
            st.chat_message("assistant", avatar=config.ICON_PATH).write(clean_response)
        elif isinstance(message, HumanMessage):
            st.chat_message("user").write(message.content)
 
# Move the function definition outside and before the handle_chat_interface function
 
def handle_chat_interface(llm, embeddings, company_collection, user_info):
    if st.session_state.conversation_ended:
        st.write("Conversation has ended. Please refresh the page to start a new conversation.")
        return
 
    # Initialize messages list if it doesn't exist
    if 'messages' not in st.session_state:
        st.session_state.messages = []
 
    chat_summary = st.session_state.matched_user_data.get("Chat Summary")
 
    if chat_summary and not pd.isna(chat_summary):
        if "continue_choice" not in st.session_state:
            st.session_state.continue_choice = None
            st.session_state.show_chat = False  # Hide chat initially
 
        if st.session_state.continue_choice is None:
            st.chat_message("assistant", avatar=config.ICON_PATH).write(
                f"We were here last time:\n\n**{chat_summary}**\n\nDo you want to continue from this conversation or start fresh?"
            )
            user_choice = st.text_input("Type 'continue' to proceed or 'start fresh' to reset:")
 
            if user_choice:
                if user_choice.lower() == "continue":
                    st.session_state.continue_choice = "continue"
                    st.session_state.show_chat = True  # Show chat input after choice
                    # Restore past context as a system message
                    system_message = create_system_message(f"Previous Chat Summary: {chat_summary}")
                    st.session_state.messages.append(system_message)
 
                    # Trigger the LLM with past context
                    response = llm.invoke(st.session_state.messages)
                    clean_response = re.sub(r'<think>.*?</think>', '', response.content, flags=re.DOTALL)
 
                    # Store AI response
                    st.session_state.messages.append(AIMessage(content=clean_response))
                    st.chat_message("assistant", avatar=config.ICON_PATH).write(clean_response)
                   
                    st.rerun()  # Ensures UI updates
               
                elif user_choice.lower() == "start fresh":
                    st.session_state.continue_choice = "start fresh"
                    st.session_state.show_chat = True  # Show chat input after choice
                    st.rerun()  # Ensures UI updates
               
                else:
                    st.warning("Please type 'continue' or 'start fresh'.")
                    st.session_state.show_chat = False  # Keep chat hidden for invalid input
                    return
       
        if st.session_state.continue_choice == "continue":
            print("User chose to continue. Resuming chat history.")
       
        elif st.session_state.continue_choice == "start fresh":
            print("Starting a new conversation.")
            if not st.session_state.conversation_started:
                print("This is user info in handle chat: ", user_info)
                initial_context = query_collections("company information and user information", company_collection, user_info, embeddings, llm)
                print("This is the initial context of the llm to work with", initial_context)
                if initial_context:
                    system_message = create_system_message(initial_context)
                    initial_messages = [system_message]
                    st.session_state.conversation_started = True
 
                    response = llm.invoke(initial_messages)
                    clean_response = re.sub(r'<think>.*?</think>', '', response.content, flags=re.DOTALL)
                    st.session_state.messages = initial_messages + [AIMessage(content=clean_response)]
                    st.session_state.conversation_started = True
                    st.session_state.show_chat = True
                else:
                    st.error("No context found. Please ensure company and user information has been properly processed.")
                    st.session_state.show_chat = False
               
    else:
        if not st.session_state.conversation_started:
            print("This is user info in handle chat: ", user_info)
            initial_context = query_collections("company information and user information", company_collection, user_info, embeddings, llm)
            print("This is the initial context of the llm to work with", initial_context)
            if initial_context:
                system_message = create_system_message(initial_context)
                initial_messages = [system_message]
                st.session_state.conversation_started = True
 
                response = llm.invoke(initial_messages)
                clean_response = re.sub(r'<think>.*?</think>', '', response.content, flags=re.DOTALL)
                print(clean_response)
                st.session_state.messages = initial_messages + [AIMessage(content=clean_response)]
                st.session_state.conversation_started = True
                st.session_state.show_chat = True  # Ensure chat bar is visible
            else:
                st.error("No context found. Please ensure company and user information has been properly processed.")
                st.session_state.show_chat = False
 
    # Add voice/text mode selection
    # Add chat interface
    if st.session_state.get("show_chat", False):
        # Style for proper text display
        st.markdown("""
            <style>
            .stChatMessage {
                white-space: normal !important;
                word-wrap: break-word !important;
            }
            .stChatMessage p {
                display: block !important;
                unicode-bidi: normal !important;
                writing-mode: horizontal-tb !important;
            }
 my message             .voice-button {
                font-size: 24px !important;
                padding: 20px 40px !important;
                border-radius: 50px !important;
                background-color: #BE232F !important;
                margin: 20px auto !important;
                display: block !important;
            }
            </style>
        """, unsafe_allow_html=True)
       
        # Initialize the main container
        main_container = st.container()
       
        with main_container:
            # Create sidebar first
            with st.sidebar:
                st.markdown("### Chat Settings")
                if 'chat_mode' not in st.session_state:
                    st.session_state.chat_mode = "Text"
               
                previous_mode = st.session_state.get('chat_mode', 'Text')
                st.session_state.chat_mode = st.radio("Choose Mode:", ["Voice", "Text"], index=0)
               
                # Handle mode change - speak last AI message when switching to voice
                if previous_mode != "Voice" and st.session_state.chat_mode == "Voice":
                    if st.session_state.messages:
                        for message in reversed(st.session_state.messages):
                            if isinstance(message, AIMessage):
                                clean_response = re.sub(r'<think>.*?</think>', '', message.content, flags=re.DOTALL)
                                text_to_speech(clean_response)
                                break
               
                if st.button("End Conversation", type="primary", use_container_width=True):
                    st.session_state.conversation_ended = True
                    st.session_state.show_chat = False
                    st.chat_message("assistant", avatar=config.ICON_PATH).write("Conversation ended. Have a great day!")
           
            # Create chat area
            chat_container = st.container()
            with chat_container:
                # Display existing messages
                if st.session_state.messages:
                    display_chat_history()
               
                # Create input area
                if not st.session_state.conversation_ended:
                    if st.session_state.chat_mode == "Text":
                        # Create bottom container for input
                        bottom_container = st.container()
                        with bottom_container:
                            st.markdown("<div style='position: fixed; bottom: 0; left: 0; right: 0; padding: 20px;'>", unsafe_allow_html=True)
                            cols = st.columns([8, 1])
                            with cols[0]:
                                handle_user_input(llm, embeddings, company_collection, user_info)
                            with cols[1]:
                                if st.button("🎤", help="Click to speak"):
                                    with st.spinner("Listening..."):
                                        user_input = speech_to_text()
                                        if user_input:
                                            # Add message to chat history first
                                            st.chat_message("user").write(user_input)
                                            st.session_state.messages.append(HumanMessage(content=user_input))
                                           
                                            # Get AI response
                                            response = llm.invoke(st.session_state.messages)
                                            clean_response = re.sub(r'<think>.*?</think>', '', response.content, flags=re.DOTALL)
                                           
                                            # Add AI response to chat history
                                            st.session_state.messages.append(AIMessage(content=clean_response))
                                            st.chat_message("assistant", avatar=config.ICON_PATH).write(clean_response)
                                            st.rerun()
                            st.markdown("</div>", unsafe_allow_html=True)
                    else:  # Voice mode
                        # Create bottom container for input
                        bottom_container = st.container()
                        with bottom_container:
                            st.markdown("<div style='position: fixed; bottom: 0; left: 0; right: 0; padding: 20px;'>", unsafe_allow_html=True)
                            if st.button("🎤 Click to Speak", key="voice_button", help="Click to speak", use_container_width=True):
                                with st.spinner("Listening..."):
                                    user_input = speech_to_text()
                                    if user_input:
                                        st.chat_message("user").write(user_input)
                                        st.session_state.messages.append(HumanMessage(content=user_input))
                                        response = llm.invoke(st.session_state.messages)
                                        clean_response = re.sub(r'<think>.*?</think>', '', response.content, flags=re.DOTALL)
                                        st.session_state.messages.append(AIMessage(content=clean_response))
                                        st.chat_message("assistant", avatar=config.ICON_PATH).write(clean_response)
                                        text_to_speech(clean_response)
                                        
                                        # Check if the response contains the ending phrase
                                        if "Have a great day" in clean_response:
                                            st.session_state.conversation_ended = True
                                            st.session_state.show_chat = False
                                            st.rerun()
                                    else:
                                        st.warning("No input detected. Please try speaking again.")
                            st.markdown("</div>", unsafe_allow_html=True)
 