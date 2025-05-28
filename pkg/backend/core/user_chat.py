import os, json, pandas as pd
from flask import Blueprint, request, jsonify, current_app
from logging_utils import stage_log
from .chat_logic import generate_user_chat_response

user_chat_bp = Blueprint("user_chat", __name__, url_prefix="/api/user_chat")

def get_chats_dir():
    chats_dir = current_app.config.get("CHATS_DIR", "data/chats")
    os.makedirs(chats_dir, exist_ok=True)
    return chats_dir

def get_report_path():
    return current_app.config.get("REPORT_PATH", "data/report.xlsx")

@stage_log(2)
def _is_valid_uuid(uuid: str) -> bool:
    report_path = get_report_path()
    if not os.path.exists(report_path):
        return False
    df = pd.read_excel(report_path, engine="openpyxl")
    return str(uuid) in df["ID"].astype(str).values

@user_chat_bp.route("/<uuid>", methods=["GET", "POST"])
@stage_log(1)
def user_chat(uuid):
    if not _is_valid_uuid(uuid):
        return jsonify({"error": "Invalid or expired chat link."}), 404

    chats_dir = get_chats_dir()
    chat_file = os.path.join(chats_dir, f"{uuid}.json")
    
    if request.method == "GET":
        # Return initial message if no chat history exists
        if not os.path.exists(chat_file):
            # Generate and save initial AI message
            ai_response = generate_user_chat_response(uuid, [])
            chat_history = [{"role": "ai", "message": ai_response}]
            with open(chat_file, "w") as f:
                json.dump(chat_history, f, ensure_ascii=False, indent=2)
            return jsonify({"history": chat_history})  # Return full history instead of just response
        else:
            # Return existing chat history
            chat_history = json.load(open(chat_file))
            return jsonify({"history": chat_history})
    
    # Handle POST request for user messages
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    chat_history = json.load(open(chat_file)) if os.path.exists(chat_file) else []
    chat_history.append({"role": "user", "message": user_message})
    
    ai_response = generate_user_chat_response(uuid, chat_history)
    chat_history.append({"role": "ai", "message": ai_response})

    with open(chat_file, "w") as f:
        json.dump(chat_history, f, ensure_ascii=False, indent=2)

    return jsonify({"response": ai_response})
