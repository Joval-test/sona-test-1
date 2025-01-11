import hashlib
import PyPDF2
import requests
from bs4 import BeautifulSoup
import streamlit as st

class DataProcessor:
    @staticmethod
    def calculate_sha256(content):
        if isinstance(content, str):
            return hashlib.sha256(content.encode()).hexdigest()
        return hashlib.sha256(content).hexdigest()

    @staticmethod
    def extract_text_from_pdf(pdf_file):
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text_content = []
        for page_num in range(len(pdf_reader.pages)):
            text = pdf_reader.pages[page_num].extract_text()
            text_content.append({
                "content": text,
                "page_number": page_num + 1
            })
        return text_content

    @staticmethod
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
            return [{"content": text, "page_number": 1}]
        except Exception as e:
            st.error(f"Error extracting text from URL: {str(e)}")
            return []