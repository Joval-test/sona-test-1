import streamlit as st
import langchain
import base64
import tempfile
import config
from data_processor import extract_text_from_pdf, extract_text_from_url
from vector_store import process_and_store_content, clear_collections
from clients import *
import pandas as pd
from config import *
from workspace import *
from streamlit_option_menu import option_menu

def initialize_session_state():
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'conversation_started' not in st.session_state:
        st.session_state.conversation_started = False
    if 'conversation_ended' not in st.session_state:
        st.session_state.conversation_ended = False
    if 'company_info' not in st.session_state:
        st.session_state.company_info = ""
    if 'user_info' not in st.session_state:
        st.session_state.user_info = ""
    if 'company_files_processed' not in st.session_state:
        st.session_state.company_files_processed = 0
    if 'user_files_processed' not in st.session_state:
        st.session_state.user_files_processed = 0
    if 'show_chat' not in st.session_state:
        st.session_state.show_chat = False
    if 'hide_info_bar' not in st.session_state:
        st.session_state.hide_info_bar = False
    if 'company_collection' not in st.session_state:
        st.session_state.company_collection = None
    if 'user_collection' not in st.session_state:
        st.session_state.user_collection = None
    
    
    # if 'user_data_df' not in st.session_state:
    #     st.session_state.user_data_df = None
    if 'input_phone_number' not in st.session_state:
        st.session_state.input_phone_number = ""
    if 'matched_user_data' not in st.session_state:
        st.session_state.matched_user_data = None
    if 'input_interface_visible' not in st.session_state:
        st.session_state.input_interface_visible = True
    if 'age_warning_confirmed' not in st.session_state:
        st.session_state.age_warning_confirmed = False
def setup_company_section():
    st.header("Company Information")
    company_source = st.radio("Select company info source:", ["PDF", "URL"], key="company_source")
    
    if company_source == "PDF":
        company_files = st.file_uploader("Upload company information PDFs", type="pdf", accept_multiple_files=True, key="company_files")
        
        if company_files and st.button("Process Company Files", key="process_company_files"):
            process_company_files(company_files)
    
    elif company_source == "URL":
        company_urls = st.text_area("Enter company website URLs (one per line):", key="company_urls")
        if company_urls and st.button("Process Company URLs", key="process_company_urls"):
            process_company_urls(company_urls)

def setup_user_section():
    st.header("User Information")
    user_files = st.file_uploader(
                label="",  # Remove default label
                type=['xlsx', 'xls', 'csv'],
                help="Upload Excel (.xlsx/.xls) or CSV file with columns: ID, Name, Company, Phone Number, Age, Description"
            )
    if user_files and st.button("Process User Files", key="process_user_files"):
            process_user_files(user_files)
    


def setup_sidebar():
    st.markdown(
    """
    <style>
    /* Sidebar content styling */
    [data-testid="stSidebarContent"] {
        background-color: white;
        secondary-background-colour: grey;
    }
    
    /* Styling for st.button elements */
    [data-testid="stSidebar"] button {
        background-color: black; 
        color: white; 
        padding: 10px; 
        border-radius: 5px; 
        font-weight: bold;
        width: 100%; /* Full width */
        display: block; /* Stack buttons vertically */
        text-align: middle; /* Align text to the left */
        margin-bottom: 10px; /* Spacing between buttons */
        border: none; /* Remove default borders */
        outline: none; /* Remove focus outlines */
    }

    /* Button hover effect */
    [data-testid="stSidebar"] button:hover {
        background-color: grey; /* Change background color on hover */
    }
    </style>
    """,
    unsafe_allow_html=True
)
    st.sidebar.image(config.LOGO_PATH, width=300)
    
    st.sidebar.write("")
    st.sidebar.write("")
    if "page" not in st.session_state:
        st.session_state.page="Connect"
    if st.sidebar.button("📊 Connect"):
        st.session_state.page = "Connect"

    if st.sidebar.button("💻 Report"):
        st.session_state.page = "Workspace"
    
    if st.sidebar.button("🛠️ Settings"):
        st.session_state.page = "Settings"

    if st.sidebar.button("❔ Help"):
        st.session_state.page = "Help"
    
    if st.session_state.page == "Connect":
        setup_header()
    elif st.session_state.page == "Workspace":
        connect_report()
    elif st.session_state.page == "Settings":
        settings()
    elif st.session_state.page == "Help":
        help()    
    st.sidebar.write("")
    st.sidebar.write("")
    st.sidebar.write("")
    st.sidebar.write("")
    st.sidebar.image(config.CAZE_PATH, use_container_width=True)
    
    
def connect_report():
    with open(config.ICON_PATH, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()
        image_and_heading_html = f"""
        <div style="display: flex; justify-content:center;background:white">
            <img src="data:image/png;base64,{encoded_image}" style="width: 75px; height: 75px; object-fit: contain; position: relative; left: -37px;">
            <h1 style="font-size: 2rem; margin: 0; z-index: 2; position: relative; left: -32px; top: -5px; color: #BE232F;">
                    Caze <span style="color: #304654;">BizConAI</span>
        </div>
        """
        st.markdown(image_and_heading_html, unsafe_allow_html=True)
        files = get_files_in_folder(WORKSPACES_FOLDER)
        if not files:
            # Show message if folder is empty
            st.sidebar.info("No chats available.")
            st.info("No chats available.")
        else:
            selected_file = st.selectbox("Select a file", options=files, index=0)

            if selected_file:
                # Display the selected file's content
                file_path = os.path.join(WORKSPACES_FOLDER, selected_file)
                st.subheader(f"Contents of {selected_file}")
                file_content = read_file_content(file_path)
                st.text_area("File Content", file_content, height=400)
    
    
def settings():
    with open(config.ICON_PATH, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()
        image_and_heading_html = f"""
        <div style="display: flex; justify-content:center;background:white">
            <img src="data:image/png;base64,{encoded_image}" style="width: 75px; height: 75px; object-fit: contain; position: relative; left: -37px;">
            <h1 style="font-size: 2rem; margin: 0; z-index: 2; position: relative; left: -32px; top: -5px; color: #BE232F;">
                    Caze <span style="color: #304654;">BizConAI</span>
        </div>
        """
        st.markdown(image_and_heading_html, unsafe_allow_html=True)
    setup_company_section()
    setup_user_section()
    if st.button("Clear All Data"):
        if clear_collections(st.session_state.company_collection, st.session_state.user_collection):
            st.rerun()
        # if st.session_state.company_files_processed > 1 and st.session_state.user_files_processed > 1:
        #     send_chroma_to_flask(PERSIST_DIRECTORY)
    
def help():
    with open(config.ICON_PATH, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()
        image_and_heading_html = f"""
        <div style="display: flex; justify-content:center;background:white">
            <img src="data:image/png;base64,{encoded_image}" style="width: 75px; height: 75px; object-fit: contain; position: relative; left: -37px;">
            <h1 style="font-size: 2rem; margin: 0; z-index: 2; position: relative; left: -32px; top: -5px; color: #BE232F;">
                    Caze <span style="color: #304654;">BizConAI</span>
        </div>
        """
        st.markdown(image_and_heading_html, unsafe_allow_html=True)
        st.write("THIS IS THE HELP SECTION")
    
    

def setup_header():
    if not st.session_state.hide_info_bar:
        st.info("👈 Let's start by uploading the informations of the company and the user.")
    with open(config.ICON_PATH, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()
    image_and_heading_html = f"""
    <div style="display: flex; justify-content:center;background:white">
        <img src="data:image/png;base64,{encoded_image}" style="width: 75px; height: 75px; object-fit: contain; position: relative; left: -37px;">
        <h1 style="font-size: 2rem; margin: 0; z-index: 2; position: relative; left: -32px; top: -5px; color: #BE232F;">
                Caze <span style="color: #304654;">BizConAI</span>
    </div>
    """
    st.markdown(image_and_heading_html, unsafe_allow_html=True)
    st.write("")
    show_user_data_modal()

def process_company_files(files):
    st.info(f"Processing {len(files)} company file(s)...")
    progress_bar = st.progress(0)
    total_files = len(files)
    
    for idx, file in enumerate(files):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(file.getvalue())
                temp_file_path = temp_file.name
            
            content = extract_text_from_pdf(temp_file_path)
            result = process_and_store_content(content, st.session_state.company_collection, "pdf", file.name)
            
            handle_processing_result(result, "Company", file.name)
            if result in ["file_exists", "success"]:
                st.session_state.company_files_processed += 1
                
        except Exception as e:
            st.error(f"Error processing company file {file.name}: {e}")
        progress_bar.progress((idx + 1) / total_files)
    st.success("All company files have been processed!")

def process_company_urls(urls):
    for url in urls.split('\n'):
        if url.strip():
            content = extract_text_from_url(url.strip())
            result = process_and_store_content(content, st.session_state.company_collection, "url", url.strip())
            handle_processing_result(result, "Company", url.strip())

def process_user_files(user_files):      #need more work to do
    # st.info(f"Processing len{(user_files)} user file(s)...")
    print(type(user_files))
    # progress_bar = st.progress(0)
    # total_files = len(user_files)
    
    if user_files:
                try:
                    # Process all uploaded files
                    new_dfs = []
                    if user_files:
                        if user_files.name.endswith('.csv'):
                            df = pd.read_csv(user_files)
                        else:
                            df = pd.read_excel(user_files)
                        
                        required_columns = ['ID', 'Name', 'Company', 'Phone Number', 'Age', 'Description']
                        if all(col in df.columns for col in required_columns):
                            new_dfs.append(df)
                        else:
                            st.error(f"File {user_files.name} must contain columns: ID, Name, Company, Phone Number, Age, Description")
                            return
                    
                    if new_dfs:
                        # Combine new dataframes
                        new_data = pd.concat(new_dfs, ignore_index=True)
                        
                        update_master_file(new_data)
                        
                        st.success(f"Successfully processed files!")
                        
                except Exception as e:
                    st.error(f"Error processing files: {str(e)}")


def handle_processing_result(result, source_type, name):
    if result == "file_exists":
        st.warning(f"{source_type} file already exists: {name}")
    elif result == "success":
        st.success(f"Processed {source_type.lower()} file successfully: {name}")
    else:
        st.error(f"Failed to process {source_type.lower()} file: {name}")


def update_master_file(new_data):
    """Update the single master Excel file with new data"""
    master_file = 'data/master_user_data.xlsx'
    os.makedirs('data', exist_ok=True)
    
    try:
        # Read existing data if file exists
        if os.path.exists(master_file):
            existing_data = pd.read_excel(master_file)
            # Combine existing and new data
            combined_df = pd.concat([existing_data, new_data], ignore_index=True)
        else:
            combined_df = new_data
        
        # Remove duplicates based on ID, keeping the latest version (comment this line if IDs are unique across nultiple documents)
        combined_df = combined_df.drop_duplicates(subset=['ID'], keep='last')
        
        # Sort by ID
        combined_df = combined_df.sort_values('ID')
        
        # Save to Excel
        combined_df.to_excel(master_file, index=False)
        
        # Update session state
        st.session_state.user_data_df = combined_df
        st.session_state.master_file = master_file
        
    except Exception as e:
        st.error(f"Error updating master file: {str(e)}")

def show_user_data_modal():
    """Show user data in a proper table format with persistent checkboxes"""
    if st.button("Show Uploaded User Data"):
        # Keep the data visible after clicking the button
        st.session_state.show_user_data = True

        
        master_file=os.path.join(os.getcwd(),"data","master_user_data.xlsx")
        df=pd.read_excel(master_file)
        if df is not None:
            st.session_state.user_data_df = df
            user_df = st.session_state.user_data_df

            st.markdown("Current User Data")

            # Initialize checkbox state if not already set
            if "selected_users" not in st.session_state:
                st.session_state.selected_users = {index: False for index in user_df.index}

            # Table headers
            cols = st.columns([0.1, 0.1, 0.2, 0.2, 0.2, 0.1])
            cols[0].markdown("**Select**")
            cols[1].markdown("**ID**")
            cols[2].markdown("**Name**")
            cols[3].markdown("**Company**")
            cols[4].markdown("**Phone Number**")
            cols[5].markdown("**Age**")

            # Display each row with checkboxes
            for index, row in user_df.iterrows():
                cols = st.columns([0.1, 0.1, 0.2, 0.2, 0.2, 0.1])

                # Initialize checkbox state only once
                if f"user_select_{index}" not in st.session_state:
                    st.session_state[f"user_select_{index}"] = False

                # Checkbox for selection (no state modification after creation)
                checked = cols[0].checkbox(
                    "", key=f"user_select_{index}", value=st.session_state[f"user_select_{index}"]
                )

                # Update selection state safely
                st.session_state.selected_users[index] = checked

                # Display user data
                cols[1].markdown(str(row["ID"]))
                cols[2].markdown(row["Name"])
                cols[3].markdown(row["Company"])
                cols[4].markdown(str(row["Phone Number"]))
                cols[5].markdown(str(row["Age"]))

            # Button to process selected users
            if st.button("Send Message to Selected Users"):
                selected_rows = [
                    index for index, selected in st.session_state.selected_users.items() if selected
                ]

                if selected_rows:
                    selected_data = user_df.loc[selected_rows]
                    st.success(f"Selected {len(selected_rows)} users.")
                    st.dataframe(selected_data)
                else:
                    st.warning("No users selected.")
        else:
            st.error("No users found in the database.Upload user information in the upload section")





def main():
    langchain.debug = True
    
    initialize_session_state()
    # setup_header()
    # llm = initialize_llm()
    embeddings = initialize_embeddings()
    company_collection, user_collection = initialize_collections(embeddings)

    st.session_state.company_collection = company_collection
    st.session_state.user_collection = user_collection
    
    setup_sidebar()

if __name__ == "__main__":
    main()