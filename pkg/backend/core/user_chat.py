import os
import json
import pandas as pd
from flask import Blueprint, request, jsonify
from .chat_logic import generate_user_chat_response

CHATS_DIR = 'data/chats'
REPORT_PATH = 'data/report.xlsx'
os.makedirs(CHATS_DIR, exist_ok=True)

user_chat_bp = Blueprint('user_chat', __name__)

def is_valid_uuid(uuid):
    if not os.path.exists(REPORT_PATH):
        return False
    df = pd.read_excel(REPORT_PATH)
    return str(uuid) in df['ID'].astype(str).values

@user_chat_bp.route('/api/user_chat/<uuid>', methods=['POST'])
def user_chat(uuid):
    if not is_valid_uuid(uuid):
        return jsonify({'error': 'Invalid or expired chat link.'}), 404

    data = request.json
    user_message = data.get('message', '')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    chat_file = os.path.join(CHATS_DIR, f'{uuid}.json')
    if os.path.exists(chat_file):
        with open(chat_file, 'r') as f:
            chat_history = json.load(f)
    else:
        chat_history = []

    chat_history.append({'role': 'user', 'message': user_message})

    # Use modular chat logic for AI response
    ai_response = generate_user_chat_response(uuid, chat_history)

    chat_history.append({'role': 'ai', 'message': ai_response})

    with open(chat_file, 'w') as f:
        json.dump(chat_history, f)

    return jsonify({'response': ai_response}) 