import os
import tempfile
# from docling import DoclingLoader
# from langchain_docling.loader import ExportType
from docling.document_converter import DocumentConverter
from langchain_core.documents import Document
from core.vector_store import get_company_collection, process_and_store_content
from core.utils import ensure_data_dir
from logging_utils import stage_log
import easyocr

DATA_DIR = 'data/company_files'

@stage_log(1)
def handle_company_files(files):
    ensure_data_dir(DATA_DIR)
    company_collection = get_company_collection()
    results = []
    has_error = False
    converter = DocumentConverter()
    
    for file in files:
        try:
            ext = os.path.splitext(file.filename)[1].lower()
            if ext not in ['.pdf', '.doc', '.docx']:
                results.append({
                    'file': file.filename,
                    'status': 'error',
                    'error': 'Only PDF, DOC, and DOCX files are supported'
                })
                has_error = True
                continue

            file_path = os.path.join(DATA_DIR, file.filename)
            file.save(file_path)
            
            try:
                result = converter.convert(file_path)
                docs = result.document.export_to_markdown()
                # docs = loader.load_and_split()
                if not docs:
                    raise Exception(f"No content could be extracted from the {ext.upper()} file")
                
                # Use the extension (without dot) as the type
                file_type = ext[1:]
                status = process_and_store_content(docs, company_collection, file_type, file.filename)
                if status == 'error':
                    raise Exception("Failed to process and store content")
                
                results.append({
                    'file': file.filename,
                    'status': 'success',
                    'message': f'Successfully processed and stored content from {file.filename}'
                })
                
            except Exception as e:
                results.append({
                    'file': file.filename,
                    'status': 'error',
                    'error': f"Processing error: {str(e)}"
                })
                has_error = True
                
            finally:
                # Clean up the uploaded file
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception as del_err:
                    print(f"Warning: Could not delete uploaded company file {file_path}: {del_err}")
                
        except Exception as e:
            results.append({
                'file': file.filename,
                'status': 'error',
                'error': f"Upload error: {str(e)}"
            })
            has_error = True
            
    return {
        'success': not has_error,
        'results': results
    }

@stage_log(1)
def handle_company_urls(urls):
    from core.utils import extract_text_from_url
    company_collection = get_company_collection()
    results = []
    has_error = False
    
    for url in urls:
        try:
            if not url.startswith(('http://', 'https://')):
                results.append({
                    'url': url,
                    'status': 'error',
                    'error': 'Invalid URL format'
                })
                has_error = True
                continue
                
            docs = extract_text_from_url(url)
            if not docs:
                results.append({
                    'url': url,
                    'status': 'error',
                    'error': 'No content could be extracted from the URL'
                })
                has_error = True
                continue
                
            status = process_and_store_content(docs, company_collection, 'url', url)
            if status == 'error':
                results.append({
                    'url': url,
                    'status': 'error',
                    'error': 'Failed to process and store content'
                })
                has_error = True
            else:
                results.append({
                    'url': url,
                    'status': 'success',
                    'message': f'Successfully processed and stored content from {url}'
                })
                
        except Exception as e:
            results.append({
                'url': url,
                'status': 'error',
                'error': str(e)
            })
            has_error = True
            
    return {
        'success': not has_error,
        'results': results
    }
