import os
import re
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from pkg.shared.core.prompts import create_system_message
from pkg.shared.core.vector_store import query_collections
from pkg.user.components.user_input import handle_user_input
from pkg.user.components.summary_status import prepare_summary, prepare_status
from pkg.shared import config
from pkg.shared.core.stage_logger import stage_log
# from pkg.user.components.speech_utils import text_to_speech, speech_to_text  # Keep import for future use

# Load environment variables
load_dotenv()

# Initialize session state variables
if 'chat_mode' not in st.session_state:
    st.session_state.chat_mode = "Text"

# Function: Display Chat History
@stage_log(stage=1)
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
 

    if st.session_state.get("show_chat", False):
        # Remove all styling
        # st.markdown("""
        #     <style>
        #     .stChatMessage {
        #         white-space: normal !important;
        #         word-wrap: break-word !important;
        #     }
        #     .stChatMessage p {
        #         display: block !important;
        #         unicode-bidi: normal !important;
        #         writing-mode: horizontal-tb !important;
        #     }
        #  my message             .voice-button {
        #         font-size: 24px !important;
        #         padding: 20px 40px !important;
        #         border-radius: 50px !important;
        #         background-color: #BE232F !important;
        #         margin: 20px auto !important;
        #         display: block !important;
        #     }
        #     </style>
        # """, unsafe_allow_html=True)
       
        # Initialize the main container for sidebar and messages only
        main_container = st.container()
       
        with main_container:
            # Create sidebar first
            with st.sidebar:
                st.markdown("### Chat Settings")
                # Commenting out voice/text mode selection but keeping initialization
                # previous_mode = st.session_state.chat_mode
                # st.session_state.chat_mode = st.radio("Choose Mode:", ["Voice", "Text"], index=0)
                
                if st.button("End Conversation", type="primary", use_container_width=True):
                    st.session_state.conversation_ended = True
                    st.session_state.show_chat = False
                    st.chat_message("assistant", avatar=config.ICON_PATH).write("Conversation ended. Have a great day!")
           
            # Create chat area for messages only
            chat_container = st.container()
            with chat_container:
                # Display existing messages
                if st.session_state.messages:
                    display_chat_history()
        
        # IMPORTANT: Place chat input OUTSIDE of all containers
        # This ensures it stays at the bottom
        if not st.session_state.conversation_ended:
            if st.session_state.chat_mode == "Text":
                # Use Streamlit's native chat input outside of any containers
                user_input = st.chat_input("Your response:")
                
                if user_input:
                    # Process the user input
                    st.session_state.messages.append(HumanMessage(content=user_input))
                    st.chat_message("user").write(user_input)
                    
                    context = query_collections(user_input, company_collection, user_info, embeddings, llm)
                    st.session_state.messages[0] = create_system_message(context)
                    try:
                        response = llm.invoke(st.session_state.messages)
                        st.session_state.messages.append(AIMessage(content=response.content))
                        st.chat_message("assistant", avatar=config.ICON_PATH).write(response.content)
                        
                        if "have a great day" in response.content.lower():
                            # Handle conversation ending
                            conversation = st.session_state.messages
                            messages_content = [f"{type(message).__name__}: {message.content}" 
                                for message in conversation 
                                if not isinstance(message, SystemMessage)]
                            print("\n".join(messages_content))
                            prompt_summary = f"From this conversation between the AI agent and the consumer prepare a summary of the conversation {messages_content} in 50 words, provide everything including the contact details."
                            prompt_status = f"Based on the following conversation {messages_content}, can you categorize the user's interest level as one of the following: 'Hot': very interested, 'Warm': partially interested, or 'Cold': not interested? Give just one word answer"
                            df = st.session_state.user_data_df
                            df_userid = str(st.session_state.userid)
                            prepare_summary(llm, prompt_summary, df, df_userid)
                            prepare_status(llm, prompt_status, df, df_userid)
                            st.session_state.conversation_ended = True
                            st.session_state.show_chat = False  # Hide chat input
                            st.rerun()
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
                # Commenting out voice mode section
                # else:  # Voice mode
                #     bottom_container = st.container()
                #     with bottom_container:
                #         st.markdown("<div style='position: fixed; bottom: 0; left: 0; right: 0; padding: 20px;'>", unsafe_allow_html=True)
                #         if st.button("🎤 Click to Speak", key="voice_button", help="Click to speak", use_container_width=True):
                #             with st.spinner("Listening..."):
                #                 user_input = speech_to_text()
                #                 if user_input:
                #                     st.chat_message("user").write(user_input)
                #                     st.session_state.messages.append(HumanMessage(content=user_input))
                #                     response = llm.invoke(st.session_state.messages)
                #                     clean_response = re.sub(r'<think>.*?</think>', '', response.content, flags=re.DOTALL)
                #                     st.session_state.messages.append(AIMessage(content=clean_response))
                #                     st.chat_message("assistant", avatar=config.ICON_PATH).write(clean_response)
                #                     text_to_speech(clean_response)
                #                     if "Have a great day" in clean_response:
                #                         st.session_state.conversation_ended = True
                #                         st.session_state.show_chat = False
                #                         st.rerun()
                #                 else:
                #                     st.warning("No input detected. Please try speaking again.")
                #         st.markdown("</div>", unsafe_allow_html=True)
 