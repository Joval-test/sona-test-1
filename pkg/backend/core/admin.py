import os
import json
import pandas as pd
from flask import Blueprint, request, jsonify
from logging_utils import stage_log

CHATS_DIR = 'data/chats'
REPORT_PATH = 'data/report.xlsx'

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
def restrict_admin_routes():
    if request.remote_addr not in ('127.0.0.1', 'localhost', '::1'):
        return jsonify({'error': 'Admin access restricted'}), 403

@admin_bp.route('/api/admin/chat_history/<uuid>', methods=['GET'])
@stage_log(2)
def get_chat_history(uuid):
    chat_file = os.path.join(CHATS_DIR, f'{uuid}.json')
    if not os.path.exists(chat_file):
        return jsonify({'history': []})
    with open(chat_file, 'r') as f:
        chat_history = json.load(f)
    return jsonify({'history': chat_history})

@admin_bp.route('/api/admin/mark_lead', methods=['POST'])
@stage_log(1)
def mark_lead():
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
