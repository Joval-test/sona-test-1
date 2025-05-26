import os
import shutil
import requests
from bs4 import BeautifulSoup
from langchain_core.documents import Document

def ensure_data_dir(path):
    os.makedirs(path, exist_ok=True)

def clear_data_dir(path):
    if os.path.exists(path):
        shutil.rmtree(path)
        os.makedirs(path)

def extract_text_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    for script in soup(["script", "style"]):
        script.decompose()
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)
    return [Document(page_content=text, metadata={"page_number": 1})] 