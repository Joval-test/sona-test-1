import hashlib
# from docling_loader import DoclingPDFLoader
from langchain_docling import DoclingLoader
from langchain_docling.loader import ExportType
import requests
from bs4 import BeautifulSoup
from langchain_core.documents import Document
import streamlit as st
import pandas as pd

def calculate_sha256(content):
    if isinstance(content, str):
        return hashlib.sha256(content.encode()).hexdigest()
    return hashlib.sha256(content).hexdigest()

def extract_text_from_pdf(pdf_file):
    loader = DoclingLoader(file_path=pdf_file,export_type=ExportType.MARKDOWN)
    docs = loader.load_and_split()
    print(docs)
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
        
        print("\n\n<<URL PARSED TEXT>>\n\n"+text)
        return [Document(
            page_content=text,
            metadata={"page_number": 1}
        )]
    except Exception as e:
        st.error(f"Error extracting text from URL: {str(e)}")
        return []
    

def display_file_details(collection):
    """
    Display all uploaded files with checkboxes and support for selection and deletion.

    Args:
        collection: The ChromaDB collection instance.
    """
    st.subheader("Uploaded Files")

    try:
        # Fetch all files from the collection
        results = collection.get()
        metadatas = results.get("metadatas", [])
        available_ids = results.get("ids", [])  # Fetch IDs for validation

        if not metadatas:
            st.info("No files found in the collection.")
            return

        # Prepare data for display
        files = []
        for metadata, file_id in zip(metadatas, available_ids):
            source_name = metadata.get("source_name", "Unknown_File")
            files.append({"hash": file_id, "name": source_name})

        # Create a DataFrame for the files
        file_df = pd.DataFrame(files)

        # Initialize session state for selected files if not already done
        if "selected_files" not in st.session_state:
            st.session_state.selected_files = {}

        # Ensure all file hashes are initialized in session state
        for _, row in file_df.iterrows():
            file_hash = row["hash"]
            if file_hash not in st.session_state.selected_files:
                st.session_state.selected_files[file_hash] = False

        # Global "Select/Deselect All Files" toggle
        global_toggle = st.checkbox(
            "Select/Deselect All Files Globally", key="global_toggle"
        )
        if global_toggle:
            for file_hash in file_df["hash"]:
                st.session_state.selected_files[file_hash] = True
        else:
            for file_hash in file_df["hash"]:
                st.session_state.selected_files[file_hash] = False

        # Display table headers
        cols = st.columns([0.1, 0.9])
        cols[0].markdown("**Select**")
        cols[1].markdown("**File Name**")

        # Display each file row with a checkbox
        for _, row in file_df.iterrows():
            cols = st.columns([0.1, 0.9])
            file_hash = row["hash"]

            st.session_state.selected_files[file_hash] = cols[0].checkbox(
                "",
                value=st.session_state.selected_files[file_hash],
                key=f"file_select_{file_hash}"  # Unique key using file hash
            )
            cols[1].markdown(row["name"])

        # Collect all selected files
        selected_files = [
            file_hash for file_hash, selected in st.session_state.selected_files.items() if selected
        ]

        # Ensure selected files exist in the collection
        selected_files = [
            file_hash for file_hash in selected_files if file_hash in available_ids
        ]

        # Display the "Delete Selected Files" button
        if selected_files:
            if st.button("Delete Selected Files"):
                for file_hash in selected_files:
                    collection.delete(ids=[file_hash])
                st.success(f"Deleted {len(selected_files)} valid files.")
                st.rerun()
        else:
            st.info("Select to delete files.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.exception(e)







    
    
# def get_all_files(collection):
#     """
#     Retrieve metadata for all unique files in the ChromaDB collection.

#     Args:
#         collection: ChromaDB collection instance.

#     Returns:
#         List[Dict]: List of files with metadata (e.g., [{"id": "file_id", "name": "file_name"}]).
#     """
#     results = collection.get()  # Fetch all data
#     files = {}
#     for metadata in results["metadatas"]:
#         file_id = metadata["file_id"]
#         if file_id not in files:
#             files[file_id] = {"id": file_id, "name": f"File {file_id[:8]}"}  # Customize name as needed
#     return list(files.values())



# def delete_file_by_id(file_id, collection):
#     """
#     Delete all chunks of a file from the ChromaDB collection.

#     Args:
#         file_id: Unique ID of the file to delete.
#         collection: ChromaDB collection instance.

#     Returns:
#         None
#     """
#     # Find all chunk IDs for the file
#     chunk_ids = collection.get(
#         where={"file_id": file_id}
#     )["ids"]

#     if chunk_ids:
#         collection.delete(ids=chunk_ids)
