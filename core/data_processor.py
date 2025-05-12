from langchain_docling import DoclingLoader
from langchain_docling.loader import ExportType
import requests
from bs4 import BeautifulSoup
from langchain_core.documents import Document
import streamlit as st
import pandas as pd
import os
import tempfile
import config

def extract_text_from_pdf(pdf_file):
    loader = DoclingLoader(file_path=pdf_file, export_type=ExportType.MARKDOWN)
    docs = loader.load_and_split()
    return docs

def extract_text_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for script in soup(["script", "style"]):
            script.decompose()
            
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return [Document(
            page_content=text,
            metadata={"page_number": 1}
        )]
    except Exception as e:
        st.error(f"Error extracting text from URL: {str(e)}")
        return []

def process_company_files(files):
    for file in files:
        temp_file = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(file.getvalue())
                temp_path = temp_file.name

            docs = extract_text_from_pdf(temp_path)
            if docs:
                result = st.session_state.process_and_store_content(
                    docs,
                    st.session_state.company_collection,
                    "pdf",
                    file.name
                )
                
                if result == "success":
                    st.success(f"Successfully processed {file.name}")
                elif result == "file_exists":
                    st.warning(f"File {file.name} already exists in the database")
                else:
                    st.error(f"Failed to process {file.name}")
                    
        except Exception as e:
            st.error(f"Error processing {file.name}: {str(e)}")
        finally:
            if temp_file and os.path.exists(temp_file.name):
                os.unlink(temp_file.name)

def process_company_urls(urls):
    for url in urls.split('\n'):
        url = url.strip()
        if url:
            try:
                docs = extract_text_from_url(url)
                if docs:
                    result = st.session_state.process_and_store_content(
                        docs,
                        st.session_state.company_collection,
                        "url",
                        url
                    )
                    
                    if result == "success":
                        st.success(f"Successfully processed {url}")
                    elif result == "file_exists":
                        st.warning(f"Content from {url} already exists")
                    else:
                        st.error(f"Failed to process {url}")
            except Exception as e:
                st.error(f"Error processing {url}: {str(e)}")

def process_user_files(files):
    if not files:
        st.error("No files uploaded!")
        return

    try:
        new_dfs = []
        for file in files:
            try:
                if file.name.endswith('.csv'):
                    df = pd.read_csv(file)
                elif file.name.endswith(('.xls', '.xlsx')):
                    df = pd.read_excel(file)
                else:
                    st.error(f"Unsupported file format: {file.name}")
                    continue

                required_columns = ['ID', 'Name', 'Company', 'Email', 'Description']
                if all(col in df.columns for col in required_columns):
                    new_dfs.append((file.name, df))
                    st.session_state["file_processing_log"].append({
                        "File Name": file.name,
                        "Leads": len(df),
                        "Processed At": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                else:
                    st.error(f"File {file.name} must contain columns: {', '.join(required_columns)}")
            except Exception as e:
                st.error(f"Error reading file {file.name}: {str(e)}")

        for file_name, df in new_dfs:
            try:
                update_master_file(df, file_name)
                st.success(f"Successfully processed {file_name}")
            except Exception as e:
                st.error(f"Error updating master file with {file_name}: {str(e)}")

    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")

def update_master_file(new_data, source_file):
    os.makedirs(os.path.dirname(config.MASTER_PATH), exist_ok=True)
    
    try:
        new_data['source'] = source_file
        
        # Define the desired column order
        column_order = [
            'ID', 'Name', 'Company', 'Email', 'Description', 'source'
        ]
        
        if os.path.exists(config.MASTER_PATH):
            existing_data = pd.read_excel(config.MASTER_PATH)
            combined_df = pd.concat([existing_data, new_data], ignore_index=True)
        else:
            combined_df = new_data
        
        combined_df = combined_df.drop_duplicates(subset=['ID'], keep='last')
        combined_df = combined_df.sort_values('ID')
        
        # Reorder columns
        combined_df = combined_df[column_order]
        
        combined_df.to_excel(config.MASTER_PATH, index=False)
        st.session_state.user_data_df = combined_df
        
    except Exception as e:
        st.error(f"Error updating master file: {str(e)}")

def display_file_details(collection):
    st.subheader("Uploaded Files")

    try:
        results = collection.get()
        metadatas = results.get("metadatas", [])
        available_ids = results.get("ids", [])

        if not metadatas:
            st.info("No files found in the collection.")
            return

        files = []
        for metadata, file_id in zip(metadatas, available_ids):
            source_name = metadata.get("source_name", "Unknown_File")
            files.append({"hash": file_id, "name": source_name})

        file_df = pd.DataFrame(files)

        if "selected_files" not in st.session_state:
            st.session_state.selected_files = {}

        for _, row in file_df.iterrows():
            file_hash = row["hash"]
            if file_hash not in st.session_state.selected_files:
                st.session_state.selected_files[file_hash] = False

        global_toggle = st.checkbox("Select/Deselect All Files", key="global_toggle")
        
        if global_toggle:
            for file_hash in file_df["hash"]:
                st.session_state.selected_files[file_hash] = True
        else:
            for file_hash in file_df["hash"]:
                st.session_state.selected_files[file_hash] = False

        cols = st.columns([0.1, 0.9])
        cols[0].markdown("**Select**")
        cols[1].markdown("**File Name**")

        for _, row in file_df.iterrows():
            cols = st.columns([0.1, 0.9])
            file_hash = row["hash"]

            st.session_state.selected_files[file_hash] = cols[0].checkbox(
                "",
                value=st.session_state.selected_files[file_hash],
                key=f"file_select_{file_hash}"
            )
            cols[1].markdown(row["name"])

        selected_files = [
            file_hash for file_hash, selected in st.session_state.selected_files.items() if selected
        ]

        selected_files = [
            file_hash for file_hash in selected_files if file_hash in available_ids
        ]

        if selected_files:
            if st.button("Delete Selected Files"):
                for file_hash in selected_files:
                    collection.delete(ids=[file_hash])
                st.success(f"Deleted {len(selected_files)} files.")
                st.rerun()
        else:
            st.info("Select files to delete.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")