import os
from threading import Thread, Timer
from flask          import Flask, jsonify, send_from_directory, request, current_app, send_file
from flask_cors     import CORS
from functools      import wraps
# from logging_utils  import stage_log
import sys
import logging
import webbrowser
import pystray
from PIL import Image
import threading
import signal
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

# Configure Flask logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------  app / conf  ---------------
def create_app():
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_dir = sys._MEIPASS
        static_folder_path = os.path.join(base_dir, 'frontend', 'build')
    else:
        # Running in development
        current_dir = os.path.dirname(os.path.abspath(__file__))
        pkg_dir = os.path.dirname(current_dir)
        static_folder_path = os.path.join(pkg_dir, 'frontend', 'build')
    
    logger.info(f"Running as executable: {getattr(sys, 'frozen', False)}")
    logger.info(f"Static folder path: {static_folder_path}")
    logger.info(f"Static folder exists: {os.path.exists(static_folder_path)}")

    app = Flask(__name__, 
                static_folder=static_folder_path,
                static_url_path='')

    # Enable CORS
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Register blueprints
    app.register_blueprint(user_chat_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(report_bp)

    # @app.before_request
    # def log_request_info():
    #     logger.info('Headers: %s', request.headers)
    #     logger.info('Body: %s', request.get_data())
    #     logger.info('Path: %s', request.path)

    # API Routes
    @app.route("/api/leads", methods=['GET'])
    def api_leads():
        # logger.info("API: /api/leads called")
        try:
            result = get_grouped_leads()
            # logger.info(f"API leads result: {result}")
            return jsonify(result)
        except Exception as e:
            # logger.error(f"Error in /api/leads: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/send_emails", methods=["POST"])
    def send_emails():
        try:
            if not request.json or not request.json.get("lead_ids"):
                return jsonify({"error": "No lead IDs provided"}), 400
            result = send_emails_to_leads(request.json.get("lead_ids", []))
            if not result.get('success'):
                return jsonify(result), 500
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/upload/company-files", methods=["POST"])
    def upload_company_files():
        try:
            if not request.files:
                return jsonify({"error": "No files provided"}), 400
            result = handle_company_files(request.files.getlist("files"))
            if not result.get('success'):
                return jsonify(result), 500
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/upload/company-urls", methods=["POST"])
    def upload_company_urls():
        try:
            if not request.json or not request.json.get("urls"):
                return jsonify({"error": "No URLs provided"}), 400
            result = handle_company_urls(request.json.get("urls", []))
            if not result.get('success'):
                return jsonify(result), 500
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/upload/user-files", methods=["POST"])
    #@stage_log(1)
    def upload_user_files():
        try:
            if not request.files:
                return jsonify({"error": "No files provided"}), 400
            result = handle_user_files(request.files.getlist("files"))
            if not result.get('success'):
                return jsonify(result), 500
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/settings", methods=["GET"])
    def api_get_settings():
        # logger.info("API: /api/settings called")
        return jsonify(get_settings())

    @app.route("/api/settings/email", methods=["POST"])
    def api_save_email_settings():
        data = request.json
        result = save_email_settings(data)
        return jsonify(result)

    @app.route("/api/settings/azure", methods=["POST"])
    def api_save_azure_settings():
        data = request.json
        result = save_azure_settings(data)
        return jsonify(result)

    @app.route("/api/settings/private-link", methods=["POST"]) 
    def api_save_private_link_settings():
        data = request.json
        result = save_private_link_config(data)
        return jsonify(result)

    @app.route("/api/clear-all", methods=["POST"])
    def api_clear_all():
        result = clear_all_data()
        return jsonify({"message": "All data cleared successfully"} if result else {"message": "Failed to clear data"})

    # Serve static files
    @app.route('/static/<path:path>')
    def serve_static(path):
        # logger.info(f"Serving static file: {path}")
        try:
            return send_from_directory(os.path.join(app.static_folder, 'static'), path)
        except Exception as e:
            # logger.error(f"Error serving static file {path}: {e}")
            return jsonify({"error": f"Failed to serve static file: {str(e)}"}), 500

    # Serve other assets (like favicon.ico)
    @app.route('/<path:filename>')
    def serve_asset(filename):
        # logger.info(f"Serving asset: {filename}")
        try:
            if os.path.exists(os.path.join(static_folder_path, filename)):
                return send_from_directory(static_folder_path, filename)
            return send_file(os.path.join(static_folder_path, 'index.html'))
        except Exception as e:
            # logger.error(f"Error serving asset {filename}: {e}")
            return jsonify({"error": f"Failed to serve asset: {str(e)}"}), 500

    # Serve React App
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        if path.startswith('api/'):
            return jsonify({"error": "API endpoint not found"}), 404
        
        if path.startswith('static/'):
            return app.send_static_file(path)
            
        return app.send_static_file('index.html')

    @app.errorhandler(404)
    def not_found(e):
        return app.send_static_file('index.html')

    @app.after_request
    def add_header(response):
        # Disable caching for all routes
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    return app

# Create the app
app = create_app()

def open_browser():
    webbrowser.open('http://localhost:5000')

def create_tray_icon(stop_function):
    try:
        # Create white background
        icon_size = (64, 64)
        background = Image.new('RGBA', icon_size, 'white')
        
        # Load and resize logo
        if getattr(sys, 'frozen', False):
            # When running as executable
            icon_path = os.path.join(sys._MEIPASS, 'logo_transparent.png')
        else:
            # When running in development
            icon_path = os.path.join(os.path.dirname(__file__), 'logo_transparent.png')
            
        logger.info(f"Loading tray icon from: {icon_path}")
        if os.path.exists(icon_path):
            logo = Image.open(icon_path)
            logo = logo.resize(icon_size, Image.Resampling.LANCZOS)
            background.paste(logo, (0, 0), logo)
        else:
            logger.error(f"Logo file not found at: {icon_path}")
            
    except Exception as e:
        logger.error(f"Error creating tray icon: {e}")
        # Fallback to simple colored icon
        background = Image.new('RGB', (64, 64), 'white')
    
    def quit_window(icon, item):
        icon.stop()
        stop_function()

    menu = pystray.Menu(
        pystray.MenuItem("Caze BizCon AI", None, enabled=False),
        pystray.MenuItem("Open", lambda: webbrowser.open('http://localhost:5000')),
        pystray.MenuItem("Exit", quit_window)
    )
    
    icon = pystray.Icon(
        "Caze BizConAI",
        background,
        menu=menu
    )
    return icon

if __name__ == "__main__":
    logger.info("\n=== Starting Flask App ===")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Static folder: {app.static_folder}")
    
    # Check if index.html exists and is readable
    index_path = os.path.join(app.static_folder, 'index.html')
    logger.info(f"Checking index.html at: {index_path}")
    if os.path.exists(index_path):
        try:
            with open(index_path, 'r') as f:
                logger.info("Successfully opened index.html")
                content = f.read(100)  
                # logger.info(f"First 100 chars of index.html: {content}")
        except Exception as e:
            logger.error(f"Error reading index.html: {e}")
    else:
        logger.error("index.html not found!")
        
    # logger.info("Static folder contents:")
    # if os.path.exists(app.static_folder):
    #     for root, dirs, files in os.walk(app.static_folder):
    #         level = root.replace(app.static_folder, '').count(os.sep)
    #         indent = ' ' * 4 * level
    #         logger.info(f"{indent}{os.path.basename(root)}/")
    #         subindent = ' ' * 4 * (level + 1)
    #         for f in files:
    #             logger.info(f"{subindent}{f}")
    
    # logger.info("\nRegistered routes:")
    # for rule in app.url_map.iter_rules():
    #     logger.info(f"Route: {rule.rule} - Methods: {rule.methods}")
    # logger.info("=========================\n")
    
    # Disable reloader when running as executable
    # use_reloader = not getattr(sys, 'frozen', False)
    
    server_running = threading.Event()
    server_running.set()

    def stop_server():
        server_running.clear()
        os.kill(os.getpid(), signal.SIGINT)

    # Create and start system tray icon
    icon = create_tray_icon(stop_server)
    icon_thread = threading.Thread(target=icon.run)
    icon_thread.daemon = True
    icon_thread.start()

    # Open browser after delay
    Timer(1.5, open_browser).start()
    
    try:
        app.run(
            debug=True, 
            port=5000, 
            use_reloader=False,
            host='0.0.0.0'
        )
    finally:
        if icon_thread.is_alive():
            icon.stop()