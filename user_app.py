import streamlit as st
import os
from clients import *
from prompts import *
from vector_store import *
from langchain.schema import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
import pandas as pd
import base64
import json
import openai

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


def handle_conversation_start(button_container, company_collection, user_info):
    company_has_docs = len(company_collection.get()['ids']) > 0
    if user_info:
        if company_has_docs:
            st.session_state.show_chat = True
            st.session_state.hide_info_bar = True
            button_container.empty()
        else:
            st.error("Please upload and process at least one company file/URL")
    else:
        st.error("Please upload and process at least one user file/URL before starting the conversation.")


def handle_chat_interface(llm, embeddings, company_collection, user_info):
    
    chat_summary = st.session_state.matched_user_data["Chat Summary"]
    if chat_summary and not pd.isna(chat_summary):
        print("Chat Summary found. Asking user for continuation choice.")
        print(f"###################{chat_summary}####################")

        # Ensure the continue choice is stored
        if "continue_choice" not in st.session_state:
            st.session_state.continue_choice = None
            st.session_state.show_chat = False  # Hide chat input

        if st.session_state.continue_choice is None:
            st.chat_message("assistant", avatar=config.ICON_PATH).write(
                f"We were here last time:\n\n**{chat_summary}**\n\nDo you want to continue from this conversation or start fresh?"
            )
            user_choice = st.text_input("Type 'continue' to proceed or 'start fresh' to reset:")

            if user_choice:
                if user_choice.lower() == "continue":
                    st.session_state.continue_choice = "continue"
                    st.session_state.show_chat = True  # Show chat input

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
                    # st.session_state.messages = []  # Reset messages
                    st.session_state.show_chat = True  # Show chat input
                    st.rerun()  # Ensures UI updates
                
                else:
                    st.warning("Please type 'continue' or 'start fresh'.")
                    return  # Don't proceed if invalid input
        
        if st.session_state.continue_choice == "continue":
            print("User chose to continue. Resuming chat history.")
        
        elif st.session_state.continue_choice == "start fresh":
            print("Starting a new conversation.")
            if not st.session_state.conversation_started:
            # print("This is user info in handle chat: ",user_info)
                initial_context = query_collections("company information and user information", company_collection, user_info, embeddings,llm)
                # print("This is the initial context of the llm to work with",initial_context)
                if initial_context:
                    system_message = create_system_message(initial_context)
                    initial_messages = [system_message]
                    st.session_state.conversation_started = True

                    response = llm.invoke(initial_messages)
                    clean_response=re.sub(r'<think>.*?</think>', '', response.content, flags=re.DOTALL)
                    st.session_state.messages = initial_messages + [AIMessage(content=clean_response)]
                    st.session_state.conversation_started = True
                else:
                    st.error("No context found. Please ensure company and user information has been properly processed.")
                    st.session_state.show_chat = False

    else:
        if not st.session_state.conversation_started:
            # print("This is user info in handle chat: ",user_info)
            initial_context = query_collections("company information and user information", company_collection, user_info, embeddings,llm)
            # print("This is the initial context of the llm to work with",initial_context)
            if initial_context:
                system_message = create_system_message(initial_context)
                initial_messages = [system_message]
                st.session_state.conversation_started = True

                response = llm.invoke(initial_messages)
                clean_response=re.sub(r'<think>.*?</think>', '', response.content, flags=re.DOTALL)
                st.session_state.messages = initial_messages + [AIMessage(content=clean_response)]
                st.session_state.conversation_started = True
            else:
                st.error("No context found. Please ensure company and user information has been properly processed.")
                st.session_state.show_chat = False

    if st.session_state.get("show_chat", False):
        display_chat_history()
        handle_user_input(llm, embeddings, company_collection, user_info)

# def handle_chat_interface(llm, embeddings, company_collection, user_info):
#     if not st.session_state.conversation_started:
#         # print("This is user info in handle chat: ",user_info)
#         initial_context = query_collections("company information and user information", company_collection, user_info, embeddings,llm)
#         # print("This is the initial context of the llm to work with",initial_context)
#         if initial_context:
#             system_message = create_system_message(initial_context)
#             initial_messages = [system_message]
#             st.session_state.conversation_started = True

#             response = llm.invoke(initial_messages)
#             clean_response=re.sub(r'<think>.*?</think>', '', response.content, flags=re.DOTALL)
#             st.session_state.messages = initial_messages + [AIMessage(content=clean_response)]
#             st.session_state.conversation_started = True
#         else:
#             st.error("No context found. Please ensure company and user information has been properly processed.")
#             st.session_state.show_chat = False
    
#     display_chat_history()
#     handle_user_input(llm, embeddings, company_collection, user_info)

def display_chat_history():
    for message in st.session_state.messages[1:]:
        if isinstance(message, AIMessage):
            clean_response=re.sub(r'<think>.*?</think>', '', message.content, flags=re.DOTALL)
            st.chat_message("assistant", avatar=config.ICON_PATH).write(clean_response)
        elif isinstance(message, HumanMessage):
            st.chat_message("user").write(message.content)

def handle_user_input(llm, embeddings, company_collection, user_info):
    if st.session_state.conversation_ended:
        st.write("Conversation has ended. Please refresh the page to start a new conversation.")
    else:
        user_input = st.chat_input("Your response:")
        
        if user_input:
            st.session_state.messages.append(HumanMessage(content=user_input))
            st.chat_message("user").write(user_input)
            
            context = query_collections(user_input, company_collection, user_info, embeddings,llm)
            st.session_state.messages[0] = create_system_message(context)
            try:
                response = llm.invoke(st.session_state.messages)
                # clean_response=re.sub(r'<think>.*?</think>', '', response.content, flags=re.DOTALL)
                st.session_state.messages.append(AIMessage(content=response.content))
                st.chat_message("assistant", avatar=config.ICON_PATH).write(response.content)
                
                if "have a great day" in response.content.lower():
                    conversation=st.session_state.messages
                    messages_content = [f"{type(message).__name__}: {message.content}" 
                        for message in conversation 
                        if not isinstance(message, SystemMessage)]
                    print("\n".join(messages_content))
                    prompt_summary=f"From this conversation between the AIagent and the consumer prepare a summary of the conversation {messages_content} in 50 words, provide everything including the contact details. "
                    prompt_status = f"Based on the following conversation {messages_content}, can you categorize the user's interest level as one of the following: 'Hot':very interested, 'Warm':partially interested, or 'Cold': not interested? Give just one word answer"
                    df = st.session_state.user_data_df
                    df_userid= str(st.session_state.userid)
                    prepare_summary(llm,prompt_summary,df,df_userid)
                    prepare_status(llm,prompt_status,df,df_userid)
                    st.session_state.conversation_ended = True
                    st.rerun()
            except openai.BadRequestError as e:
                error_message = str(e)
                if "content_filter" in error_message:
                    st.error("Your message was flagged by our content policy. Please rephrase and try again.")
                    st.session_state.conversation_ended = True
                    st.rerun()
                else:
                    st.error(f"An error occurred: {error_message}")
                



def prepare_summary(llm, prompt, df, df_userid):
    summary = llm.invoke(prompt)
    print(summary.content)
    
    try:
        df['ID'] = df['ID'].astype(str)
        
        matched_row = df[df['ID'] == df_userid]
        
        if not matched_row.empty:
            # Find the index of the matched row
            index = matched_row.index[0]

            # **Replace** the existing summary with the new one
            df.at[index, 'Chat Summary'] = summary.content  
            
            save_path = config.REPORT_PATH    
            df.to_excel(save_path, index=False)
            
            name = st.session_state.user_name
            print(f"Chat summary replaced successfully for Member: {name}")
            return True

    except Exception as e:
        print(f"An error occurred: {e}")
        return False

    
# def prepare_status(llm,prompt_summary,df,df_userid):
#     status=llm.invoke(prompt_summary)
#     print(status.content)
#     try:
#         df['ID'] = df['ID'].astype(str)
#         # df_phone = str(df_phone)
        
#         matched_row = df[df['ID'] == df_userid]
            
#         if not matched_row.empty:
#             # Update the 'Status' column
#             index = matched_row.index[0]
#             if pd.notna(df.at[index, 'Chat Summary']):
#                 df.at[index, 'Status (Hot/Warm/Cold/Not Responded)'] = f" {status.content}"
#             else:
#                 df.at[index, 'Status (Hot/Warm/Cold/Not Responded)'] = status.content
#             save_path=config.REPORT_PATH    
#             df.to_excel(save_path, index=False)
#             name=st.session_state.user_name
#             print(f"Chat summary updated successfully for Member: {name}")
#             return True

#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return False


def prepare_status(llm, prompt_summary, df, df_userid):
    status = llm.invoke(prompt_summary)
    print(status.content)
    try:
        # Ensure 'ID' is treated as a string
        df['ID'] = df['ID'].astype(str)

        # Ensure 'Status (Hot/Warm/Cold/Not Responded)' column is cast to object
        if 'Status (Hot/Warm/Cold/Not Responded)' in df.columns:
            df['Status (Hot/Warm/Cold/Not Responded)'] = df['Status (Hot/Warm/Cold/Not Responded)'].astype(object)
        else:
            df['Status (Hot/Warm/Cold/Not Responded)'] = None  # Initialize if column doesn't exist

        # Find the matching row by 'ID'
        matched_row = df[df['ID'] == df_userid]

        if not matched_row.empty:
            # Update the 'Status (Hot/Warm/Cold/Not Responded)' column
            index = matched_row.index[0]
            if pd.notna(df.at[index, 'Status (Hot/Warm/Cold/Not Responded)']):
                df.at[index, 'Status (Hot/Warm/Cold/Not Responded)'] = f" {status.content}"
            else:
                df.at[index, 'Status (Hot/Warm/Cold/Not Responded)'] = status.content

            # Save the updated DataFrame to an Excel file
            save_path = config.REPORT_PATH
            df.to_excel(save_path, index=False)

            # Get user name from session state
            name = st.session_state.user_name
            print(f"Status updated successfully for Member: {name}")
            return True

    except Exception as e:
        print(f"An error occurred: {e}")
        return False
                
                
def load_user_data():
    data_path=config.REPORT_PATH
    if(os.path.exists(data_path)):
        print("data path opened")
        df = pd.read_excel(data_path)
        st.session_state.user_data_df = df
    else:
        print("File path doesnt exist")
        # st.warning("You do not have access to this chat please contact the admin for access.")
    
def match_user_data():
    """Match custom URL with user data and store in vector DB."""
    if st.session_state.user_data_df is None:
        return None
    df = st.session_state.user_data_df
    
    if df.empty:
        st.error("No message has been sent to any user")
    else:
        if "user" in st.query_params: 
            user_id =  st.query_params["user"]
            print(f"This is the user_id {user_id}")
            if user_id:
                user_id = str(user_id)
                st.session_state.userid=user_id
                matched_user = df[df['ID'].astype(str) == user_id]
                
                if not matched_user.empty:
                    user_data = matched_user.iloc[0]
                    st.session_state.matched_user_data = {
                        'Status': user_data['Status (Hot/Warm/Cold/Not Responded)'],
                        'ID': user_data['ID'],
                        'Name': user_data['Name'],
                        'Company': user_data['Company'],
                        'Email': user_data['Email'],
                        'Age': int(user_data['Age']),
                        'Description': user_data['Description'],
                        'Source': user_data['source'],
                        'Connected': user_data['Connected'],
                        'Chat Summary': user_data['Chat Summary']
                    }
                    st.session_state.user_name = user_data['Name']

                    # Create a document for the matched user data
                    user_doc = Document(
                        page_content=(
                            f"Status: {user_data['Status (Hot/Warm/Cold/Not Responded)']}\n"
                            f"ID: {user_data['ID']}\n"
                            f"Name: {user_data['Name']}\n"
                            f"Company: {user_data['Company']}\n"
                            f"Email: {user_data['Email']}\n"
                            f"Age: {user_data['Age']}\n"
                            f"Description: {user_data['Description']}\n"
                            f"Source: {user_data['source']}\n"
                            f"Connected: {user_data['Connected']}\n"
                            f"Chat Summary: {user_data['Chat Summary']}"                 
                        ),
                        metadata={"source_type": "user_data", "source_name": "user_list"}
                    )
                    
                    return user_doc.page_content
        else:
            st.session_state.matched_user_data = None
            return False
    
    
               
# def match_user_data(phone):
#     """Match phone number with user data and store in vector DB."""
#     if st.session_state.user_data_df is None:
#         return None
#     print("This is the phone given for matching",phone)
#     df = st.session_state.user_data_df
#     if df.empty:
#         st.error("No message has been send to any user")
#     else:
#         df['Phone Number'] = df['Phone Number'].astype(str)
#         phone = str(phone)

#         matched_user = df[df['Phone Number'] == phone]
#         # print("Matched User:",matched_user)
#         if not matched_user.empty:
#             user_data = matched_user.iloc[0]
#             st.session_state.matched_user_data = {
#                 'Status': user_data['Status (Hot/Warm/Cold/Not Responded)'],
#                 'ID': user_data['ID'],
#                 'Name': user_data['Name'],
#                 'Company': user_data['Company'],
#                 'Phone Number': user_data['Phone Number'],
#                 'Age': int(user_data['Age']),  # Ensure age is an integer
#                 'Description': user_data['Description'],
#                 'Source': user_data['source'],
#                 'Connected': user_data['Connected'],
#                 'Chat Summary': user_data['Chat Summary']
#             }
#             st.session_state.user_name = user_data['Name']
#             # print(user_data['Name'])

#             # Create a document for the matched user data
#             user_doc = Document(
#                 page_content=(
#                     f"Status: {user_data['Status (Hot/Warm/Cold/Not Responded)']}\n"
#                     f"ID: {user_data['ID']}\n"
#                     f"Name: {user_data['Name']}\n"
#                     f"Company: {user_data['Company']}\n"
#                     f"Phone Number: {user_data['Phone Number']}\n"
#                     f"Age: {user_data['Age']}\n"
#                     f"Description: {user_data['Description']}\n"
#                     f"Source: {user_data['source']}\n"
#                     f"Connected: {user_data['Connected']}\n"
#                     f"Chat Summary: {user_data['Chat Summary']}"
#                 ),
#                 metadata={"source_type": "user_data", "source_name": "user_list"}
#             )
#             # description = extract_fields(user_doc)
            
#             # Process and store the content in the vector database
#             return user_doc.page_content
#         else:
#             st.session_state.matched_user_data = None
#             return False

def extract_fields(document):
    lines = document.page_content.split("\n")
    description = None
    # chat_summary = None

    for line in lines:
        if line.startswith("Description:"):
            description = line.replace("Description: ", "").strip()
        if line.startswith("Name"):
            name=line.replace("Name","").strip
        # if line
            
    print (description)
        # elif line.startswith("Chat Summary:"):
        #     chat_summary = line.replace("Chat Summary: ", "").strip()

    return description


def initialize_chat(button_container):
    st.session_state.conversation_started = True
    st.session_state.show_chat = True
    st.session_state.email_entered = True
    st.session_state.input_interface_visible = False
    button_container.empty()
    
    
def get_llm_function():
    config_file_path = "config.json"
    
    # Load the selected LLM from the JSON config
    with open(config_file_path, "r") as file:
        config = json.load(file)
    
    selected_llm = config["llm"]
    
    # Map LLM names to their initialization functions
    llm_functions = {
        "Azure OpenAI": initialize_llm_azure,
        "Llama 3.1": initialize_llm_llama,
        "Phi3.5":initialize_llm_phi,
        "Mistral":initialize_llm_mistral,
        "Deepseek": initialize_llm_deepseek
    }

    # Return the corresponding function or raise an error
    if selected_llm in llm_functions:
        return llm_functions[selected_llm]
    else:
        raise ValueError(f"Invalid LLM selected in config: {selected_llm}")

def main():
    try:
    
        embeddings = initialize_embeddings_azure()
        company_collection = initialize_collections(embeddings)
        
        initialize_session_state()
        
        st.session_state.company_collection = company_collection
        # st.session_state.user_collection = user_collection
        
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
    
        # phone_number = st.text_input("Enter your phone number", value=st.session_state.phone_number)
        
        llm_function = get_llm_function()
        print(llm_function)
        load_user_data()
        
        # Call the function to initialize the selected LLM
        llm = llm_function()
        
        st.session_state.userid = None
        # st.session_state.phone_number_entered = True
        
        # print(phone_number)

        button_container = st.empty()
        user_content=match_user_data()
        
        print("This is user content in main",user_content)

        if user_content:
            handle_conversation_start(button_container, company_collection, user_content)

            if st.session_state.show_chat:
                handle_chat_interface(llm, embeddings, company_collection, user_content)
            else:
                st.error("ERROR: No matched user found.")
                
                
        if st.session_state.matched_user_data == None:
            st.warning("You do not have access to this chat please contact the admin for access.")
        
    except ValueError as e:
        print(str(e))
        

if __name__ == "__main__":
    main()