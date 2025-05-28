import os
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from functools import wraps
from logging_utils import stage_log

# ---------------  domain logic  ---------------
from core.company  import handle_company_files, handle_company_urls
from core.user     import handle_user_files
from core.settings import (
    save_email_settings, save_azure_settings, get_settings,
    clear_all_data, get_private_link_config, save_private_link_config
)
from core.files    import get_uploaded_files
from core.leads    import get_grouped_leads, send_emails_to_leads
from core.user_chat import user_chat_bp     #  public
from core.admin     import admin_bp         #  protected
from core.report    import report_bp

# ---------------  app / conf  ---------------
app = Flask(__name__, static_folder="../frontend/build", static_url_path="/")
app.config.update(CHATS_DIR="data/chats", REPORT_PATH="data/report.xlsx")
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ---------------  IP restriction decorator  ---------------
def restrict_to_localhost(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.remote_addr != "127.0.0.1":
            return jsonify({"error": "Access denied"}), 403
        return f(*args, **kwargs)
    return decorated

# ---------------  blueprints  ---------------
app.register_blueprint(user_chat_bp)  # /api/user_chat/...
app.register_blueprint(admin_bp)      # /api/admin/... (IP restricted inside admin_bp)
app.register_blueprint(report_bp)     # /api/report/... (IP restricted inside report_bp)

# ---------------  PUBLIC api with restrictions  ---------------
@app.route("/api/leads")
@stage_log(2)
@restrict_to_localhost
def get_leads():
    return jsonify(get_grouped_leads())

@app.route("/api/send_emails", methods=["POST"])
@stage_log(1)
def send_emails():
    lead_ids = (request.json or {}).get("lead_ids", [])
    return jsonify(send_emails_to_leads(lead_ids))

@app.route("/api/upload/company-files", methods=["POST"])
@stage_log(1)
def upload_company_files():
    return jsonify(handle_company_files(request.files.getlist("files")))

@app.route("/api/upload/company-urls", methods=["POST"])
@stage_log(1)
def upload_company_urls():
    return jsonify(handle_company_urls(request.json.get("urls", [])))

@app.route("/api/upload/user-files", methods=["POST"])
@stage_log(1)
def upload_user_files():
    return jsonify(handle_user_files(request.files.getlist("files")))

@app.route("/api/settings/email", methods=["POST"])
@stage_log(2)
@restrict_to_localhost
def api_save_email_settings():
    return jsonify(save_email_settings(request.json))

@app.route("/api/settings/azure", methods=["POST"])
@stage_log(2)
@restrict_to_localhost
def api_save_azure_settings():
    return jsonify(save_azure_settings(request.json))

@app.route("/api/settings", methods=["GET"])
@stage_log(2)
@restrict_to_localhost
def api_get_settings():
    return jsonify(get_settings())

@app.route("/api/clear-all", methods=["POST"])
@stage_log(1)
def api_clear_all():
    return jsonify(clear_all_data())

@app.route("/api/uploaded-files", methods=["GET"])
@stage_log(2)
def api_get_uploaded_files():
    return jsonify(get_uploaded_files())

@app.route("/api/settings/private-link", methods=["GET", "POST"])
@stage_log(2)
@restrict_to_localhost
def api_private_link():
    if request.method == "GET":
        return jsonify(get_private_link_config())
    return jsonify(save_private_link_config(request.json))

# ---------------  REACT SPA  ---------------
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
@stage_log(4)
def serve_react(path):
    target = os.path.join(app.static_folder, path)
    return send_from_directory(app.static_folder,
        path if path and os.path.exists(target) else "index.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
