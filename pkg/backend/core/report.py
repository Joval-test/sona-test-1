from flask import Blueprint, jsonify
import pandas as pd
import os
from .settings import get_private_link_config, get_report_path
from .leads import get_status_for_email, generate_private_link

report_bp = Blueprint('report', __name__)

@report_bp.route('/api/report', methods=['GET'])
def get_report():
    report_path = get_report_path()
    if not os.path.exists(report_path):
        return jsonify({'leads': []})
    try:
        df = pd.read_excel(report_path)
    except Exception as e:
        print(f"Error reading report.xlsx: {e}")
        return jsonify({'leads': []})
    required_columns = {
        'Name': '',
        'Company': '',
        'Email': '',
        'ID': '',
        'Sent Date': pd.NaT,
        'Chat Summary': '',
        'Private Link': '',
        'Status': 'Not Responded'
    }
    for col, default in required_columns.items():
        if col not in df.columns:
            df[col] = default
    df = df.drop_duplicates(subset=['Email'], keep='last')
    df['Lead Status'] = df['Email'].apply(get_status_for_email)
    if 'Private Link' not in df.columns or df['Private Link'].isna().any():
        df['Private Link'] = df['ID'].apply(generate_private_link)
        df.to_excel(report_path, index=False)
    # Convert dates to string for JSON, handle NaT
    df['Sent Date'] = df['Sent Date'].apply(lambda x: str(x) if pd.notna(x) else '')
    # Replace NaN/None with empty string for all columns
    df = df.where(pd.notnull(df), None)
    return jsonify({'leads': df.to_dict(orient='records')}) 