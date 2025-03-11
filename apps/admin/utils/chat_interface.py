import streamlit as st
import re
import pandas as pd
from langchain.schema import HumanMessage, AIMessage
from core.prompts import create_system_message
from core.vector_store import query_collections
from apps.admin.utils.user_input import handle_user_input
import config

def handle_chat_interface(llm, embeddings, company_collection, user_info):
    if st.session_state.conversation_ended:
        st.write("Conversation has ended. Please refresh the page to start a new conversation.")
        return

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
                    # st.session_state.messages = []  # Reset messages
                    st.session_state.show_chat = True  # Show chat input
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
        display_chat_history()
        if not st.session_state.conversation_ended:
            handle_user_input(llm, embeddings, company_collection, user_info)

def display_chat_history():
    for message in st.session_state.messages[1:]:
        if isinstance(message, AIMessage):
            clean_response = re.sub(r'<think>.*?</think>', '', message.content, flags=re.DOTALL)
            st.chat_message("assistant", avatar=config.ICON_PATH).write(clean_response)
        elif isinstance(message, HumanMessage):
            st.chat_message("user").write(message.content)