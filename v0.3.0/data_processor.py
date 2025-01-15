import hashlib
from docling_loader import DoclingPDFLoader
import requests
from bs4 import BeautifulSoup
import tempfile
from langchain_core.documents import Document
import streamlit as st

def calculate_sha256(content):
    if isinstance(content, str):
        return hashlib.sha256(content.encode()).hexdigest()
    return hashlib.sha256(content).hexdigest()

def extract_text_from_pdf(pdf_file):
    loader = DoclingPDFLoader(pdf_file)
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