import os
import json
import pandas as pd
from flask import Blueprint, jsonify, request
from .settings import get_private_link_config, get_report_path
from .leads import get_status_for_email, generate_private_link
from logging_utils import stage_log

report_bp = Blueprint('report', __name__)

@report_bp.before_request
def restrict_report_access():
    if request.remote_addr not in ('127.0.0.1', 'localhost', '::1'):
        return jsonify({'error': 'Access to report is restricted'}), 403

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

    # Replace NaN in Chat Summary with 'no chat summary yet'
    df['Chat Summary'] = df['Chat Summary'].fillna('no chat summary yet')

    df['Sent Date'] = df['Sent Date'].apply(lambda x: str(x) if pd.notna(x) else '')
    df = df.where(pd.notnull(df), None)

    return jsonify({'leads': df.to_dict(orient='records')})
