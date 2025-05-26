import os
import tempfile
from langchain_docling import DoclingLoader
from langchain_docling.loader import ExportType
from langchain_core.documents import Document
from core.vector_store import get_company_collection, process_and_store_content
from core.utils import ensure_data_dir

DATA_DIR = 'data/company_files'

def handle_company_files(files):
    ensure_data_dir(DATA_DIR)
    company_collection = get_company_collection()
    results = []
    for file in files:
        try:
            file_path = os.path.join(DATA_DIR, file.filename)
            file.save(file_path)
            loader = DoclingLoader(file_path=file_path, export_type=ExportType.MARKDOWN)
            docs = loader.load_and_split()
            status = process_and_store_content(docs, company_collection, 'pdf', file.filename)
            # Delete the uploaded file after successful processing
            if status != 'error':
                try:
                    os.remove(file_path)
                except Exception as del_err:
                    print(f"Warning: Could not delete uploaded company file {file_path}: {del_err}")
            results.append({'file': file.filename, 'status': status})
        except Exception as e:
            results.append({'file': file.filename, 'status': 'error', 'error': str(e)})
    return {'success': True, 'results': results}

def handle_company_urls(urls):
    from core.utils import extract_text_from_url
    company_collection = get_company_collection()
    results = []
    for url in urls:
        try:
            docs = extract_text_from_url(url)
            status = process_and_store_content(docs, company_collection, 'url', url)
            results.append({'url': url, 'status': status})
        except Exception as e:
            results.append({'url': url, 'status': 'error', 'error': str(e)})
    return {'success': True, 'results': results} 