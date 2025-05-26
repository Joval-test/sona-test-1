import os
import json
import pandas as pd
from flask import Blueprint, request, jsonify

CHATS_DIR = 'data/chats'
REPORT_PATH = 'data/report.xlsx'
API_KEY = 'your-secret-key'  # Change for production

admin_bp = Blueprint('admin', __name__)

def require_api_key():
    key = request.headers.get('X-API-KEY')
    if key != API_KEY:
        return jsonify({'error': 'Unauthorized'}), 401

@admin_bp.route('/api/admin/chat_history/<uuid>', methods=['GET'])
def get_chat_history(uuid):
    auth = require_api_key()
    if auth: return auth
    chat_file = os.path.join(CHATS_DIR, f'{uuid}.json')
    if not os.path.exists(chat_file):
        return jsonify({'history': []})
    with open(chat_file, 'r') as f:
        chat_history = json.load(f)
    return jsonify({'history': chat_history})

@admin_bp.route('/api/admin/mark_lead', methods=['POST'])
def mark_lead():
    auth = require_api_key()
    if auth: return auth
    data = request.json
    uuid = data.get('uuid')
    status = data.get('status')
    summary = data.get('summary')
    contact = data.get('contact', '')
    if not os.path.exists(REPORT_PATH):
        return jsonify({'error': 'No report found'}), 404
    df = pd.read_excel(REPORT_PATH)
    idx = df[df['ID'].astype(str) == str(uuid)].index
    if not idx.empty:
        df.at[idx[0], 'Status (Hot/Warm/Cold/Not Responded)'] = status
        df.at[idx[0], 'Chat Summary'] = summary
        if contact:
            df.at[idx[0], 'Contact'] = contact
        df.to_excel(REPORT_PATH, index=False)
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Lead not found'}), 404 