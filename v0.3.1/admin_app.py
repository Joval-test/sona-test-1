import streamlit as st
import langchain
import base64
import tempfile
import config
from data_processor import *
from vector_store import process_and_store_content, clear_collections
from clients import *
import pandas as pd
from config import *
from streamlit_option_menu import option_menu
from datetime import datetime
from io import BytesIO
import json

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
    if "file_processing_log" not in st.session_state:
        st.session_state["file_processing_log"] = []
    
    
    if 'send_user_data_df' not in st.session_state:
        st.session_state.send_user_data_df = None
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
                help="Upload Excel (.xlsx/.xls) or CSV file with columns: ID, Name, Company, Phone Number, Age, Description",
                accept_multiple_files=True, 
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
        text-align: left; /* Align text to the left */
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
        st.session_state.page = "Report"
    
    if st.sidebar.button("🛠️ Settings"):
        st.session_state.page = "Settings"

    if st.sidebar.button("❔ Help"):
        st.session_state.page = "Help"
    
    if st.session_state.page == "Connect":
        setup_header()
    elif st.session_state.page == "Report":
        file_path=config.REPORT_PATH
        connect_report(file_path)
    elif st.session_state.page == "Settings":
        settings()
        display_processing_log()
    elif st.session_state.page == "Help":
        help()    
    st.sidebar.write("")
    st.sidebar.write("")
    st.sidebar.write("")
    st.sidebar.write("")
    st.sidebar.image(config.CAZE_PATH, use_container_width=True)
    
    
def connect_report(file_path):
    """Display, select, delete, and update rows from an Excel file with dynamic button visibility."""
    # Ensure the file exists
    if os.path.exists(file_path):
            st.session_state.send_user_data_df = pd.read_excel(file_path)
            if st.session_state.send_user_data_df.empty:
                st.error(" Upload user information in the Settings section.")
                return
    else:
        st.error("No users found in the database. Upload user information in the Settings section.")
        return

    # Load the Excel file
    data = pd.read_excel(file_path)

    # Add default "Not Responded" value to the first column if not already set
    if "Status (Hot/Warm/Cold/Not Responded)" in data.columns:
        data["Status (Hot/Warm/Cold/Not Responded)"].fillna("Not Responded", inplace=True)
    else:
        st.error("The required column 'Status (Hot/Warm/Cold/Not Responded)' is missing in the file.")
        return

    # Standardize status values to ensure consistent filtering
    data["Status (Hot/Warm/Cold/Not Responded)"] = data["Status (Hot/Warm/Cold/Not Responded)"].str.strip().str.title()

    # Initialize session state for selection if not already set
    if "selected_users" not in st.session_state:
        st.session_state.selected_users = {index: False for index in data.index}

    # Display data grouped by status
    statuses = ["Hot", "Warm", "Cold", "Not Responded"]
    for status in statuses:
        st.markdown(f"### {status} Leads")
        status_data = data[data["Status (Hot/Warm/Cold/Not Responded)"] == status]

        if not status_data.empty:
            st.dataframe(status_data)

            # Download button for each status group
            output = BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                status_data.to_excel(writer, index=False, sheet_name=f"{status} Data")
            output.seek(0)

            st.download_button(
                label=f"Download {status} Leads",
                data=output,
                file_name=f"{status.lower()}_leads.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        else:
            st.info(f"No {status} leads available.")

    # Identify selected rows
    selected_indices = [idx for idx, selected in st.session_state.selected_users.items() if selected]

    # Buttons for actions
    if selected_indices:
        st.markdown("### Actions for Selected Rows")

        # Button to delete selected rows
        if st.button("Delete Selected Rows"):
            updated_data = data.drop(selected_indices)

            # Save the updated data back to the Excel file
            with pd.ExcelWriter(file_path, engine="xlsxwriter") as writer:
                updated_data.to_excel(writer, index=False, sheet_name="Updated Data")

            st.success(f"{len(selected_indices)} rows have been deleted.")
            st.rerun()

        # Button to download selected rows
        selected_data = data.iloc[selected_indices]
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            selected_data.to_excel(writer, index=False, sheet_name="Selected Data")
        output.seek(0)

        st.download_button(
            label="Download Selected Rows",
            data=output,
            file_name="selected_users.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    # Button to delete all rows
    if st.button("Delete All Rows"):
        df=pd.read_excel(file_path)
        headers = df.columns.tolist()
        with pd.ExcelWriter(file_path, engine="xlsxwriter") as writer:
            pd.DataFrame().to_excel(writer, index=False, sheet_name="Updated Data")

        with pd.ExcelWriter(file_path, engine="xlsxwriter") as writer:
            empty_df = pd.DataFrame(columns=headers)
            empty_df.to_excel(writer, index=False, sheet_name="Updated Data")

        st.success("All rows have been deleted")
        st.rerun()

    # Button to download all rows
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        data.to_excel(writer, index=False, sheet_name="All Data")
    output.seek(0)

    st.download_button(
        label="Download All Rows",
        data=output,
        file_name="all_users.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )



def update_selection_state(index):
    """Update the selection state for the row."""
    # Toggle the selection state for the specific row
    st.session_state[f"user_select_{index}"] = not st.session_state[f"user_select_{index}"]
    st.session_state.selected_users[index] = st.session_state[f"user_select_{index}"]



    
    
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
        model_options = ["Azure OpenAI", "Llama 3.1", "Mistral"]
        selected_model = st.selectbox("Select LLM Model:", model_options)
        
        if st.button("Save Configuration"):
            st.success(f"LLM updated to {selected_model} successfully!")
            print(f"Before update: {config.llm}")
            update_llm_in_config(selected_model)
            print(f"After update: {config.llm}")
        
    setup_company_section()
    if not len(st.session_state.company_collection.get()['ids']) > 0:
        st.warning("Company information not available")
    else:
        display_file_details(st.session_state.company_collection)
    
    setup_user_section()
    if st.button("Clear All Data"):
        if clear_collections(st.session_state.company_collection):
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
    
def update_llm_in_config(selected_model):
    config_file_path = "config.json"
    with open(config_file_path, "r") as file:
        config = json.load(file)

    config["llm"] = selected_model

    with open(config_file_path, "w") as file:
        json.dump(config, file, indent=4)

    print(f"Updated LLM in config.json: {selected_model}")


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
            print(f"Process result {result}")
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


def process_user_files(user_files):
    """
    Processes multiple uploaded files, displays file details (name, rows, time),
    and persists this information across UI changes.
    """
    if not user_files:
        st.error("No files uploaded!")
        return

    try:
        new_dfs = []  # List to hold valid dataframes

        for file in user_files:
            try:
                # Determine file type and read it into a dataframe
                if file.name.endswith('.csv'):
                    df = pd.read_csv(file)
                elif file.name.endswith(('.xls', '.xlsx')):
                    df = pd.read_excel(file)
                else:
                    st.error(f"Unsupported file format: {file.name}")
                    continue

                # Ensure the file contains the required columns
                required_columns = ['ID', 'Name', 'Company', 'Phone Number', 'Age', 'Description']
                if all(col in df.columns for col in required_columns):
                    new_dfs.append((file.name, df))  # Add the dataframe along with file name

                    # Log the processing details
                    processing_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state["file_processing_log"].append({
                        "File Name": file.name,
                        "Leads": len(df),
                        "Processed At": processing_time
                    })
                else:
                    st.error(f"File {file.name} must contain columns: {', '.join(required_columns)}")
            except Exception as file_error:
                st.error(f"Error reading file {file.name}: {str(file_error)}")

        # Process all valid dataframes
        for file_name, df in new_dfs:
            try:
                update_master_file(df, file_name)  # Pass dataframe and source file name
                st.success(f"Successfully processed and updated master file with {file_name}!")
            except Exception as update_error:
                st.error(f"Error updating master file with {file_name}: {str(update_error)}")

    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        
def display_processing_log():
    if st.session_state["file_processing_log"]:
        st.markdown("### Processed Files Log")
        log_df = pd.DataFrame(st.session_state["file_processing_log"])
        st.table(log_df)  # Display as a table
    else:
        st.info("No files processed yet.")


def handle_processing_result(result, source_type, name):
    if result == "file_exists":
        st.warning(f"{source_type} file already exists: {name}")
    elif result == "success":
        st.success(f"Processed {source_type.lower()} file successfully: {name}")
    else:
        st.error(f"Failed to process {source_type.lower()} file: {name}")


def update_master_file(new_data, source_file):
    """Update the single master Excel file with new data and add source column."""
    master_file = config.MASTER_PATH
    os.makedirs('data', exist_ok=True)
    
    try:
        # Add source column to the new data
        new_data['source'] = source_file  # Add the filename as the source
        
        # Read existing data if file exists
        if os.path.exists(master_file):
            existing_data = pd.read_excel(master_file)
            # Combine existing and new data
            combined_df = pd.concat([existing_data, new_data], ignore_index=True)
        else:
            combined_df = new_data
        
        # Remove duplicates based on ID, keeping the latest version
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


def generate_custom_user_url(user_id):
    """Generate a custom URL for each user."""
    base_link=config.BASE_LINK
    return f"{base_link}?user={user_id}"

def save_selected_users_to_excel(selected_data, file_path):
    """Save selected user data to an Excel file, appending new selections if the file exists."""
    selected_data["Connected"] = "Yes"  # Add 'Connected' column
    selected_data.insert(0, "Status (Hot/Warm/Cold/Not Responded)", "")  # Empty column for status
    selected_data["Chat Summary"] = ""  # Empty column for chat summary
    selected_data["Custom URL"] = selected_data["ID"].apply(generate_custom_user_url)

    # Check if the file exists
    if os.path.exists(file_path):
        # Load existing data
        existing_data = pd.read_excel(file_path)

        # Append new data
        combined_data = pd.concat([existing_data, selected_data], ignore_index=True)

        # Remove duplicates (if necessary, based on a column like "ID")
        combined_data.drop_duplicates(subset=["ID"], inplace=True)
    else:
        combined_data = selected_data

    # Save the combined data back to the file
    with pd.ExcelWriter(file_path, engine="xlsxwriter") as writer:
        combined_data.to_excel(writer, index=False, sheet_name="Selected Users")

    st.success(f"File successfully saved to: {file_path}")

def show_user_data_modal():
    """Show user data in a proper table format with persistent checkboxes, separated by source."""

    # Button to show data
    if st.button("Show Uploaded User Data"):
        st.session_state.show_user_data = True

    if "user_data_df" not in st.session_state:
        master_file = config.MASTER_PATH
        if os.path.exists(master_file):
            st.session_state.user_data_df = pd.read_excel(master_file)
            if st.session_state.user_data_df.empty:
                st.error("Upload user information in the Settings section.")
                return
        else:
            st.error("No users found in the database. Upload user information in the Settings section.")
            return

    if "selected_users" not in st.session_state:
        st.session_state.selected_users = {index: False for index in st.session_state.user_data_df.index}

    if "source_toggles" not in st.session_state:
        st.session_state.source_toggles = {}

    if "show_user_data" not in st.session_state:
        st.session_state.show_user_data = False

    if st.session_state.get("show_user_data", False):
        user_df = st.session_state.user_data_df

        if "source" not in user_df.columns:
            st.error("The 'source' column is missing in the uploaded data.")
            return

        st.markdown("## User Data Overview")

        global_select_all = st.checkbox("Select/Deselect All Users Globally")

        if global_select_all:
            for index in user_df.index:
                st.session_state.selected_users[index] = True
            for source in user_df["source"].unique():
                st.session_state.source_toggles[source] = True
        else:
            for index in user_df.index:
                st.session_state.selected_users[index] = False
            for source in user_df["source"].unique():
                st.session_state.source_toggles[source] = False

        grouped_data = user_df.groupby("source")

        for source, group in grouped_data:
            st.markdown(f"### Users from Source: {source}")
            if source not in st.session_state.source_toggles:
                st.session_state.source_toggles[source] = False

            source_toggle = st.checkbox(
                f"Select/Deselect All Users from {source}",
                value=st.session_state.source_toggles[source],
                key=f"source_toggle_{source}",
            )
            for index in group.index:
                st.session_state.selected_users[index] = source_toggle
            st.session_state.source_toggles[source] = source_toggle

            # Table headers
            cols = st.columns([0.1, 0.1, 0.2, 0.2, 0.2, 0.1])
            cols[0].markdown("**Select**")
            cols[1].markdown("**ID**")
            cols[2].markdown("**Name**")
            cols[3].markdown("**Company**")
            cols[4].markdown("**Phone Number**")
            cols[5].markdown("**Age**")

            # Display each row for the current source group with individual checkboxes
            for index, row in group.iterrows():
                # Create columns for the row
                cols = st.columns([0.1, 0.1, 0.2, 0.2, 0.2, 0.1])

                # Ensure that the current user's selection state exists in st.session_state
                if index not in st.session_state.selected_users:
                    st.session_state.selected_users[index] = False

                is_selected = st.session_state.selected_users[index]
                st.session_state.selected_users[index] = cols[0].checkbox(
                    "",
                    value=is_selected,
                    key=f"user_select_{index}"
                )

                # Render other columns with user data
                cols[1].markdown(str(row["ID"]))
                cols[2].markdown(row["Name"])
                cols[3].markdown(row["Company"])
                cols[4].markdown(str(row["Phone Number"]))
                cols[5].markdown(str(row["Age"]))

        # Collect all selected rows globally
        selected_rows = [
            index for index, selected in st.session_state.selected_users.items() if selected
        ]

        # Ensure the selected rows are valid indices in the DataFrame
        valid_selected_rows = [index for index in selected_rows if index in user_df.index]

        # Display the "Send Message" button for globally selected users
        if valid_selected_rows:
            if st.button("Send Message to All Selected Users"):
                selected_data = user_df.loc[valid_selected_rows]
                st.success(f"Selected {len(valid_selected_rows)} users globally.")

                # Save the Excel file to the specified path
                file_path = config.REPORT_PATH
                save_selected_users_to_excel(selected_data, file_path)
        else:
            st.error("No valid users selected.")





def main():
    langchain.debug = True
    initialize_session_state()
    embeddings = initialize_embeddings()
    company_collection = initialize_collections(embeddings)

    st.session_state.company_collection = company_collection
    # st.session_state.user_collection = user_collection
    
    setup_sidebar()

if __name__ == "__main__":
    main()