import os
import pandas as pd
from core.utils import ensure_data_dir
from logging_utils import stage_log

DATA_DIR = 'data/user_files'
MASTER_PATH = 'data/master_leads.xlsx'
REQUIRED_COLUMNS = ['ID', 'Name', 'Company', 'Email', 'Description']

@stage_log(1)
def handle_user_files(files):
    ensure_data_dir(DATA_DIR)
    results = []
    for file in files:
        try:
            file_path = os.path.join(DATA_DIR, file.filename)
            file.save(file_path)
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            valid_rows = df.dropna(subset=REQUIRED_COLUMNS)
            if not valid_rows.empty:
                valid_rows['source'] = file.filename
                update_master_file(valid_rows)
                # Delete the uploaded file after processing
                try:
                    os.remove(file_path)
                except Exception as del_err:
                    print(f"Warning: Could not delete uploaded file {file_path}: {del_err}")
                results.append({'file': file.filename, 'status': 'success', 'leads': len(valid_rows)})
            else:
                results.append({'file': file.filename, 'status': 'no_valid_rows'})
        except Exception as e:
            results.append({'file': file.filename, 'status': 'error', 'error': str(e)})
    return {'success': True, 'results': results}

@stage_log(2)
def update_master_file(new_data):
    if os.path.exists(MASTER_PATH):
        existing = pd.read_excel(MASTER_PATH)
        combined = pd.concat([existing, new_data], ignore_index=True)
        combined = combined.drop_duplicates(subset=['ID'], keep='last')
    else:
        combined = new_data
    combined.to_excel(MASTER_PATH, index=False)
