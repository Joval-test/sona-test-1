import os
import pandas as pd
from logging_utils import stage_log

COMPANY_DIR = 'data/company_files'
USER_DIR = 'data/user_files'
MASTER_PATH = 'data/master_leads.xlsx'

@stage_log(2)
def get_uploaded_files():
    company_files = os.listdir(COMPANY_DIR) if os.path.exists(COMPANY_DIR) else []
    user_files = os.listdir(USER_DIR) if os.path.exists(USER_DIR) else []
    leads = []
    if os.path.exists(MASTER_PATH):
        df = pd.read_excel(MASTER_PATH)
        leads = df.to_dict(orient='records')
    return {
        'company_files': company_files,
        'user_files': user_files,
        'leads': leads
    }
