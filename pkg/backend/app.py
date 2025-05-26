from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import os
import tempfile
import pandas as pd
from core.company import handle_company_files, handle_company_urls
from core.user import handle_user_files
from core.settings import save_email_settings, save_azure_settings, get_settings, clear_all_data, get_private_link_config, save_private_link_config
from core.files import get_uploaded_files
from core.leads import get_grouped_leads, send_emails_to_leads
from core.user_chat import user_chat_bp
from core.admin import admin_bp
from core.report import report_bp

app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')
CORS(app)
app.register_blueprint(user_chat_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(report_bp)

# Dummy data for leads (replace with Excel reading logic later)
DUMMY_LEADS = [
    {"id": 1, "name": "Alice", "company": "Acme Corp", "email": "alice@acme.com", "description": "Lead 1", "source": "Webinar", "email_sent": False, "email_sent_count": 0},
    {"id": 2, "name": "Bob", "company": "Beta Inc", "email": "bob@beta.com", "description": "Lead 2", "source": "Webinar", "email_sent": True, "email_sent_count": 1},
    {"id": 3, "name": "Charlie", "company": "Gamma LLC", "email": "charlie@gamma.com", "description": "Lead 3", "source": "Conference", "email_sent": False, "email_sent_count": 0}
]

@app.route('/api/admin')
def admin_api():
    return jsonify({"message": "Admin endpoint working!"})

@app.route('/api/user')
def user_api():
    return jsonify({"message": "User endpoint working!"})

@app.route('/api/leads')
def get_leads():
    return jsonify(get_grouped_leads())

@app.route('/api/send_emails', methods=['POST'])
def send_emails():
    data = request.json
    lead_ids = data.get('lead_ids', [])
    result = send_emails_to_leads(lead_ids)
    return jsonify(result)

@app.route('/api/upload/company-files', methods=['POST'])
def upload_company_files():
    files = request.files.getlist('files')
    result = handle_company_files(files)
    return jsonify(result)

@app.route('/api/upload/company-urls', methods=['POST'])
def upload_company_urls():
    urls = request.json.get('urls', [])
    result = handle_company_urls(urls)
    return jsonify(result)

@app.route('/api/upload/user-files', methods=['POST'])
def upload_user_files():
    files = request.files.getlist('files')
    result = handle_user_files(files)
    return jsonify(result)

@app.route('/api/settings/email', methods=['POST'])
def api_save_email_settings():
    data = request.json
    result = save_email_settings(data)
    return jsonify(result)

@app.route('/api/settings/azure', methods=['POST'])
def api_save_azure_settings():
    data = request.json
    result = save_azure_settings(data)
    return jsonify(result)

@app.route('/api/settings', methods=['GET'])
def api_get_settings():
    result = get_settings()
    return jsonify(result)

@app.route('/api/clear-all', methods=['POST'])
def api_clear_all():
    result = clear_all_data()
    return jsonify(result)

@app.route('/api/uploaded-files', methods=['GET'])
def api_get_uploaded_files():
    result = get_uploaded_files()
    return jsonify(result)

@app.route('/api/settings/private-link', methods=['GET'])
def api_get_private_link():
    return jsonify(get_private_link_config())

@app.route('/api/settings/private-link', methods=['POST'])
def api_save_private_link():
    data = request.json
    return jsonify(save_private_link_config(data))

# Serve React build files in production
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000) 