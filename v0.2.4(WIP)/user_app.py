import streamlit as st
import os
from clients import *
from prompts import *
from vector_store import *
from langchain.schema import HumanMessage, AIMessage, SystemMessage
import pandas as pd
import base64

def initialize_session_state():
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'conversation_started' not in st.session_state:
        st.session_state.conversation_started = False
    if 'conversation_ended' not in st.session_state:
        st.session_state.conversation_ended = False
    if 'phone_number' not in st.session_state:
        st.session_state.phone_number = ''
    if 'user_name' not in st.session_state:
        st.session_state.user_name = ''
    if 'show_chat' not in st.session_state:
        st.session_state.show_chat = False
    if 'hide_info_bar' not in st.session_state:
        st.session_state.hide_info_bar = False
    if 'company_collection' not in st.session_state:
        st.session_state.company_collection = None
    if 'user_collection' not in st.session_state:
        st.session_state.user_collection = None
    if 'user_data_df' not in st.session_state:
        st.session_state.user_data_df = None
    if 'matched_user_data' not in st.session_state:
        st.session_state.matched_user_data = None
    if "phone_number_entered" not in st.session_state:
        st.session_state.phone_number_entered = False
    # if 'input_interface_visible' not in st.session_state:
    #     st.session_state.input_interface_visible = True
    if 'age_warning_confirmed' not in st.session_state:
        st.session_state.age_warning_confirmed = False


    

# def handle_conversation_start(button_container, company_collection, user_collection):
#     company_has_docs = len(company_collection.get()['ids']) > 0
#     user_has_docs = len(user_collection.get()['ids']) > 0
#     user_data_uploaded = st.session_state.user_data_df is not None
#     phone_provided = bool(st.session_state.phone_number)

#     if not all([company_has_docs, user_data_uploaded, phone_provided]):
#         missing = []
#         if not company_has_docs:
#             missing.append("company information")
#         if not user_data_uploaded:
#             missing.append("user data file")
#         if not phone_provided:
#             missing.append("phone number")
#         st.error(f"Please provide {', '.join(missing)} before starting the conversation.")
#         return False
    
#     if st.session_state.matched_user_data is not None:
#         age = st.session_state.matched_user_data['Age']
        
#         # If age warning is already confirmed or not needed, start chat immediately
#         if age >= 20 or st.session_state.age_warning_confirmed:
#             initialize_chat(button_container)
#             return True
            
#         # Show age warning if needed
#         if age < 20 and not st.session_state.age_warning_confirmed:
#             col1, col2, col3 = st.columns([1, 2, 1])
#             with col2:
#                 st.warning("⚠ Warning: User age is below 20. Would you like to proceed?")
#                 if st.button("Yes, proceed anyway", key="proceed_button"):
#                     st.session_state.age_warning_confirmed = True
#                     initialize_chat(button_container)
#                     return True
#             return False
#     else:
#         col1, col2, col3 = st.columns([1, 2, 1])
#         with col2:
#             if st.button("Start conversation without user data", key="start_no_data"):
#                 initialize_chat(button_container)
#                 return True
#         return False

# def handle_chat_interface(llm, embeddings, company_collection, user_collection):
    
#     if not st.session_state.conversation_started:
#         initial_context = query_collections("company information and user information", company_collection, user_collection, embeddings)
#         if initial_context:
#             system_message = create_system_message(initial_context)
#             initial_messages = [system_message]
#             st.session_state.conversation_started = True

#             response = llm(initial_messages)
#             st.session_state.messages = initial_messages + [AIMessage(content=response.content)]
#             print(st.session_state.messages)
#             st.session_state.conversation_started = True
#         else:
#             st.error("No context found. Please ensure company and user information has been properly processed.")
#             st.session_state.show_chat = False
    
#     display_chat_history()
#     handle_user_input(llm, embeddings, company_collection, user_collection)

def handle_conversation_start(button_container, company_collection, user_collection):
    company_has_docs = len(company_collection.get()['ids']) > 0
    user_has_docs = len(user_collection.get()['ids']) > 0

    if company_has_docs and user_has_docs:
        st.session_state.show_chat = True
        st.session_state.hide_info_bar = True
        button_container.empty()
    else:
        st.error("Please upload and process at least one company file/URL and one user file/URL before starting the conversation.")

def handle_chat_interface(llm, embeddings, company_collection, user_collection):
    if not st.session_state.conversation_started:
        initial_context = query_collections("company information and user information", company_collection, user_collection, embeddings)
        if initial_context:
            system_message = create_system_message(initial_context)
            initial_messages = [system_message]
            st.session_state.conversation_started = True

            response = llm(initial_messages)
            st.session_state.messages = initial_messages + [AIMessage(content=response.content)]
            st.session_state.conversation_started = True
        else:
            st.error("No context found. Please ensure company and user information has been properly processed.")
            st.session_state.show_chat = False
    
    display_chat_history()
    handle_user_input(llm, embeddings, company_collection, user_collection)

def display_chat_history():
    for message in st.session_state.messages[1:]:
        if isinstance(message, AIMessage):
            st.chat_message("assistant", avatar=config.ICON_PATH).write(message.content)
        elif isinstance(message, HumanMessage):
            st.chat_message("user").write(message.content)

def handle_user_input(llm, embeddings, company_collection, user_collection):
    if st.session_state.conversation_ended:
        st.write("Conversation has ended. Please refresh the page to start a new conversation.")
    else:
        user_input = st.chat_input("Your response:")
        
        if user_input:
            st.session_state.messages.append(HumanMessage(content=user_input))
            st.chat_message("user").write(user_input)
            
            context = query_collections(user_input, company_collection, user_collection, embeddings)
            st.session_state.messages[0] = create_system_message(context)
        
            response = llm(st.session_state.messages)
            st.session_state.messages.append(AIMessage(content=response.content))
            st.chat_message("assistant", avatar=config.ICON_PATH).write(response.content)
            
            if "have a great day" in response.content.lower():
                messages=st.session_state.messages
                # print(messages)
                prompt=f"Can you provide a summary of this conversation so far?{messages}"
                summary=llm.invoke(prompt)
                print(summary.content)
                df = st.session_state.user_data_df
                df_phone= str(st.session_state.phone_number)
                df_name=str(st.session_state.user_name)
                create_workspace_file(df_name,df_phone,summary.content)
                st.session_state.conversation_ended = True
                st.rerun()


                
                
def create_workspace_file(df_name,df_phone,info):
    filename = f"{df_name}_{df_phone}"
    workspace_dir = 'workspaces' 

    if not os.path.exists(workspace_dir):
        os.makedirs(workspace_dir)
        
    file_path = os.path.join(workspace_dir, f"{filename}.txt")

    with open(file_path, 'w') as file:
        file.write(info)

    print(f"File created at: {file_path}")
                
def load_user_data():
    data_path=config.REPORT_PATH
    df = pd.read_excel(data_path)
    st.session_state.user_data_df = df
               
def match_user_data(phone):
    """Match phone number with user data and store in vector DB."""
    if st.session_state.user_data_df is None:
        return None

    df = st.session_state.user_data_df
    # Convert phone numbers to strings for comparison
    df['Phone Number'] = df['Phone Number'].astype(str)
    phone = str(phone)

    matched_user = df[df['Phone Number'] == phone]
    if not matched_user.empty:
        user_data = matched_user.iloc[0]
        st.session_state.matched_user_data = {
            'Status': user_data['Status'],
            'ID': user_data['ID'],
            'Name': user_data['Name'],
            'Company': user_data['Company'],
            'Phone Number': user_data['Phone Number'],
            'Age': int(user_data['Age']),  # Ensure age is an integer
            'Description': user_data['Description'],
            'Source': user_data['Source'],
            'Connected': user_data['Connected'],
            'Chat Summary': user_data['Chat Summary']
        }
        st.session_state.user_name = user_data['Name']

        # Create a document for the matched user data
        user_doc = Document(
            page_content=(
                f"Status: {user_data['Status']}\n"
                f"ID: {user_data['ID']}\n"
                f"Name: {user_data['Name']}\n"
                f"Company: {user_data['Company']}\n"
                f"Phone Number: {user_data['Phone Number']}\n"
                f"Age: {user_data['Age']}\n"
                f"Description: {user_data['Description']}\n"
                f"Source: {user_data['Source']}\n"
                f"Connected: {user_data['Connected']}\n"
                f"Chat Summary: {user_data['Chat Summary']}"
            ),
            metadata={"source_type": "user_data", "source_name": "user_list"}
        )

        # Process and store the content in the vector database
        process_and_store_content(
            [user_doc],
            st.session_state.user_collection,
            "user_data",
            "user_list"
        )
        return True
    else:
        st.session_state.matched_user_data = None
        return False


def initialize_chat(button_container):
    st.session_state.conversation_started = True
    st.session_state.show_chat = True
    st.session_state.phone_number_entered = True
    st.session_state.input_interface_visible = False
    button_container.empty()


def main():
    llm = initialize_llm()
    embeddings = initialize_embeddings()
    company_collection, user_collection = initialize_collections(embeddings)
    
    initialize_session_state()
    load_user_data()
    
    st.session_state.company_collection = company_collection
    st.session_state.user_collection = user_collection
    
    with open(config.ICON_PATH, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()

    st.write("")
    st.write("")
    st.write("")
    image_and_heading_html = f"""
    <div style="display: flex; justify-content:center;background:white">
        <img src="data:image/png;base64,{encoded_image}" style="width: 75px; height: 75px; object-fit: contain; position: relative; left: -37px;">
        <h1 style="font-size: 2rem; margin: 0; z-index: 2; position: relative; left: -32px; top: -5px; color: #BE232F;">
                Caze <span style="color: #304654;">BizConAI</span>
    </div>
    """
    st.markdown(image_and_heading_html, unsafe_allow_html=True)
 
    phone_number = st.text_input("Enter your phone number", value=st.session_state.phone_number)
    
    st.session_state.phone_number = phone_number
    st.session_state.phone_number_entered = True
    
    print(phone_number)

    button_container = st.empty()
    match_user_data(phone_number)

    if phone_number:
        handle_conversation_start(button_container, company_collection, user_collection)

        if st.session_state.show_chat:
            handle_chat_interface(llm, embeddings, company_collection, user_collection)
        else:
            st.error("ERROR: No matched user found.")

if __name__ == "__main__":
    main()