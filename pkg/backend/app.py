import os
from threading import Thread
from flask          import Flask, jsonify, send_from_directory, request
from flask_cors     import CORS
from functools      import wraps
from logging_utils  import stage_log
import sys
# ---------------  domain logic  ---------------
from core.company   import handle_company_files, handle_company_urls
from core.user      import handle_user_files
from core.settings  import (
    save_email_settings, save_azure_settings, get_settings,
    clear_all_data, get_private_link_config, save_private_link_config
)
# from core.files     import get_uploaded_files
from core.leads     import get_grouped_leads, send_emails_to_leads
from core.user_chat import user_chat_bp     #  public
from core.admin     import admin_bp         #  protected
from core.report    import report_bp
from flask          import send_from_directory

# ---------------  app / conf  ---------------
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # When running as exe, _MEIPASS contains the temp folder with extracted files
        base_path = sys._MEIPASS
    except AttributeError:
        # When running in development
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

# Fixed static folder path resolution
if getattr(sys, 'frozen', False):
    # Running as EXE - frontend/build is extracted to _MEIPASS/frontend/build
    static_folder_path = resource_path('frontend/build')
else:
    # Running in development - pkg/backend/app.py, need to go to pkg/frontend/build
    current_dir = os.path.dirname(os.path.abspath(__file__))  # pkg/backend/
    pkg_dir = os.path.dirname(current_dir)  # pkg/
    static_folder_path = os.path.join(pkg_dir, 'frontend', 'build')

print("Running in EXE:", getattr(sys, 'frozen', False))
print("Static folder path:", static_folder_path)
print("Static folder exists:", os.path.exists(static_folder_path))

# Check if the static folder exists and list its contents
if os.path.exists(static_folder_path):
    print("Files in static folder:", os.listdir(static_folder_path))
    # Check specifically for index.html
    index_path = os.path.join(static_folder_path, 'index.html')
    print("index.html exists:", os.path.exists(index_path))
else:
    print("ERROR: Static folder does not exist!")
    # Try to find where the frontend files actually are
    if getattr(sys, 'frozen', False):
        print("Contents of _MEIPASS:", os.listdir(sys._MEIPASS))
        frontend_path = os.path.join(sys._MEIPASS, 'frontend')
        if os.path.exists(frontend_path):
            print("Contents of frontend folder:", os.listdir(frontend_path))

app = Flask(__name__, static_folder=static_folder_path, static_url_path="")
app.config.update(
    CHATS_DIR="data/chats",
    REPORT_PATH="data/report.xlsx",
    # Enable CORS properly
    CORS_HEADERS='Content-Type'
)

# Configure CORS with more options
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type", "X-Total-Count"]
    }
})

# ---------------  IP restriction decorator  ---------------
def restrict_to_localhost(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.remote_addr != "127.0.0.1":
            return jsonify({"error": "Access denied"}), 403
        return f(*args, **kwargs)
    return decorated

# ---------------  blueprints  ---------------
app.register_blueprint(user_chat_bp)  
app.register_blueprint(admin_bp)      
app.register_blueprint(report_bp)     

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

# @app.route("/api/uploaded-files", methods=["GET"])
# @stage_log(2)
# def api_get_uploaded_files():
#     return jsonify(get_uploaded_files())

@app.route("/api/settings/private-link", methods=["GET", "POST"])
@stage_log(2)
@restrict_to_localhost
def api_private_link():
    if request.method == "GET":
        return jsonify(get_private_link_config())
    return jsonify(save_private_link_config(request.json))

# Add OPTIONS handler for API routes
@app.route("/api/<path:path>", methods=["OPTIONS"])
def handle_api_options(path):
    return "", 204, {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization"
    }

# Temporary debug route
@app.route("/debug")
def debug():
    return jsonify({
        "static_folder": app.static_folder,
        "static_folder_exists": os.path.exists(app.static_folder),
        "static_folder_contents": os.listdir(app.static_folder) if os.path.exists(app.static_folder) else None,
        "index_html_exists": os.path.exists(os.path.join(app.static_folder, 'index.html')),
        "frozen": getattr(sys, 'frozen', False),
        "_MEIPASS": getattr(sys, '_MEIPASS', 'Not available'),
        "static_url_path": app.static_url_path
    })

# Flag to track if static files check has been performed
_static_files_checked = False

@app.before_request
def check_static_files():
    global _static_files_checked
    if not _static_files_checked:
        print("\n=== Static Files Debug Info ===")
        print(f"Static folder: {app.static_folder}")
        print(f"Static folder exists: {os.path.exists(app.static_folder)}")
        if os.path.exists(app.static_folder):
            print("Static folder contents:", os.listdir(app.static_folder))
        print("==============================\n")
        _static_files_checked = True

# ---------------  REACT SPA  ---------------
# Replace your serve_react function with this improved version:

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_react(path):
    # Handle API routes first
    if path.startswith('api/'):
        # Let the actual API route handlers deal with it
        endpoint = request.endpoint
        if endpoint and endpoint in app.view_functions:
            return app.view_functions[endpoint]()
        return jsonify({"error": "API route not found"}), 404
    
    # Try to serve static files first
    if path:
        try:
            file_path = os.path.join(app.static_folder, path)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                return send_from_directory(app.static_folder, path)
        except Exception as e:
            print(f"Error serving static file: {e}")
      # For all other routes (including /connect), serve index.html to let React handle client-side routing
    try:
        return send_from_directory(app.static_folder, 'index.html')
    except Exception as e:
        print(f"Error serving index.html: {e}")
        return jsonify({
            "error": "Failed to serve React app",
            "details": str(e),
            "static_folder": app.static_folder,
            "path_requested": path,
            "static_folder_exists": os.path.exists(app.static_folder),
            "index_exists": os.path.exists(os.path.join(app.static_folder, 'index.html'))
        }), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)