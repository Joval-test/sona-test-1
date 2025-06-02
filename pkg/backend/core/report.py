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

    # Remove any processing: just drop duplicates if you want, or even skip that
    df = df.drop_duplicates(subset=['Email'], keep='last')
    df = df.where(pd.notnull(df), None)  # Replace NaN with None for JSON

    # Ensure all NaN are replaced with None for JSON serialization
    leads = df.to_dict(orient='records')
    for lead in leads:
        for k, v in lead.items():
            if isinstance(v, float) and pd.isna(v):
                lead[k] = None

    return jsonify({'leads': leads})

