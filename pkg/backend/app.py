import os
from threading import Thread, Timer
from flask          import Flask, jsonify, send_from_directory, request, current_app, send_file
from flask_cors     import CORS
from functools      import wraps
from logging_utils  import stage_log
import sys
import logging
import webbrowser
import pystray
from PIL import Image
import threading
import signal
import traceback
# ---------------  domain logic  ---------------
from core.company   import handle_company_files, handle_company_urls
from core.user      import handle_user_files
from core.settings  import (
    save_email_settings, save_azure_settings,
    clear_all_data, save_private_link_config, InvalidCredentialsError, ConfigurationError
)
# from core.files     import get_uploaded_files
from core.leads     import get_grouped_leads, send_emails_to_leads
from core.user_chat import user_chat_bp     #  public
from core.admin     import admin_bp         #  protected
from core.report    import report_bp
from flask          import send_from_directory
from core.agents.google_auth import GoogleAuthManager
from core.company_info_manager import CompanyInfoManager
from core.storage import Storage
from core.agents.product_extractor import ProductExtractorAgent
from core.agents.responsible_person import ResponsiblePersonAgent
from core.agents.availability import AvailabilityAgent
from core.agents.meeting_scheduler import MeetingSchedulerAgent
from core.agents.email import EmailAgent
import json

# Configure Flask logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------  app / conf  ---------------
@stage_log(2)
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
    @stage_log(2)
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
    @stage_log(2)
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
    @stage_log(2)
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
    @stage_log(2)
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
    @stage_log(2)
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

    # @app.route("/api/settings", methods=["GET"])
    # @stage_log(2)
    # def api_get_settings():
    #     # logger.info("API: /api/settings called")
    #     return jsonify(get_settings())

    @app.route("/api/settings/email", methods=["POST"])
    @stage_log(2)
    def api_save_email_settings():
        data = request.json
        try:
            save_email_settings(data)
            return jsonify({"success": True, "message": "Email settings saved successfully"}), 200
        except InvalidCredentialsError as e:
            return jsonify({"error": str(e)}), 400
        except ConfigurationError as e:
            return jsonify({"error": str(e)}), 500
        except Exception as e:
            return jsonify({"error": "An unexpected error occurred: " + str(e)}), 500

    @app.route("/api/settings/azure", methods=["POST"])
    @stage_log(2)
    def api_save_azure_settings():
        data = request.json
        try:
            save_azure_settings(data)
            return jsonify({"success": True, "message": "Azure settings saved successfully"}), 200
        except InvalidCredentialsError as e:
            return jsonify({"error": str(e)}), 400
        except ConfigurationError as e:
            return jsonify({"error": str(e)}), 500
        except Exception as e:
            return jsonify({"error": "An unexpected error occurred: " + str(e)}), 500

    @app.route("/api/settings/private-link", methods=["POST"]) 
    @stage_log(2)
    def api_save_private_link_settings():
        data = request.json
        try:
            save_private_link_config(data)
            return jsonify({"success": True, "message": "Private link settings saved successfully"}), 200
        except ConfigurationError as e:
            return jsonify({"error": str(e)}), 500
        except Exception as e:
            return jsonify({"error": "An unexpected error occurred: " + str(e)}), 500

    @app.route("/api/clear-all", methods=["POST"])
    @stage_log(2)
    def api_clear_all():
        try:
            clear_all_data()
            return jsonify({"message": "All data cleared successfully"}), 200
        except ConfigurationError as e:
            return jsonify({"error": str(e)}), 500
        except Exception as e:
            return jsonify({"error": "An unexpected error occurred: " + str(e)}), 500

    @app.route("/api/schedule_meeting", methods=["POST"])
    @stage_log(2)
    def api_schedule_meeting():
        data = request.json
        chat_summary = data.get("chat_summary", "")
        lead_email = data.get("lead_email", "")
        lead_name = data.get("lead_name", "")
        if not chat_summary or not lead_email or not lead_name:
            return jsonify({"success": False, "error": "Missing required fields."}), 400
        try:
            result = orchestrate_meeting_flow(chat_summary, lead_email, lead_name)
            return jsonify(result), 200
        except (MeetingSchedulingError, ConfigurationError) as e:
            logger.error(f"Meeting scheduling error: {e}")
            return jsonify({"success": False, "error": str(e)}), 400
        except Exception as e:
            logger.error(f"An unexpected error occurred during meeting scheduling: {e}")
            return jsonify({"success": False, "error": "An unexpected error occurred during meeting scheduling: " + str(e)}), 500

    

    # Serve static files
    @app.route('/static/<path:path>')
    @stage_log(3)
    def serve_static(path):
        # logger.info(f"Serving static file: {path}")
        try:
            return send_from_directory(os.path.join(app.static_folder, 'static'), path)
        except Exception as e:
            # logger.error(f"Error serving static file {path}: {e}")
            return jsonify({"error": f"Failed to serve static file: {str(e)}"}), 500

    # Serve other assets (like favicon.ico)
    @app.route('/<path:filename>')
    @stage_log(3)
    def serve_asset(filename):
        # logger.info(f"Serving asset: {filename}")
        try:
            if os.path.exists(os.path.join(static_folder_path, filename)):
                return send_from_directory(static_folder_path, filename)
            return send_file(os.path.join(static_folder_path, 'index.html'))
        except Exception as e:
            # logger.error(f"Error serving asset {filename}: {e}")
            return jsonify({"error": f"Failed to serve asset: {str(e)}"}), 500

    # Catch-all for unmatched /api/* routes to return JSON 404
    @app.route('/api/<path:path>')
    @stage_log(3)
    def catch_all_api(path):
        return jsonify({"error": "API endpoint not found"}), 404

    # Serve React App
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    @stage_log(3)
    def catch_all(path):
        if path.startswith('api/'):
            return jsonify({"error": "API endpoint not found"}), 404
        
        if path.startswith('static/'):
            return app.send_static_file(path)
            
        return app.send_static_file('index.html')

    @app.errorhandler(404)
    @stage_log(3)
    def not_found(e):
        return app.send_static_file('index.html')

    @app.after_request
    @stage_log(4)
    def add_header(response):
        # Disable caching for all routes
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    storage = Storage()
    company_info_manager = CompanyInfoManager(storage)
    product_extractor = ProductExtractorAgent()
    responsible_person_agent = ResponsiblePersonAgent(storage)
    availability_agent = AvailabilityAgent()
    meeting_scheduler = MeetingSchedulerAgent()
    email_agent = EmailAgent()

    @app.route("/api/company_info", methods=["GET"])
    @stage_log(2)
    def get_company_info():
        return jsonify(company_info_manager.get_company_info())

    @app.route("/api/company_info", methods=["POST"])
    @stage_log(2)
    def set_company_info():
        data = request.json
        company_info_manager.set_company_info(data)
        return jsonify({"success": True})

    @app.route("/api/products", methods=["GET"])
    @stage_log(2)
    def get_products():
        return jsonify({"products": company_info_manager.get_products()})

    @app.route("/api/products", methods=["POST"])
    @stage_log(2)
    def set_products():
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        data = request.get_json()
        if data is None:
            return jsonify({"error": "Invalid JSON"}), 400
        if data.get("extract"):
            company_info = data.get("company_info", "")
            products = product_extractor.extract_products(company_info)
            return jsonify({"products": products})
        products = data.get("products", [])
        company_info_manager.set_products(products)
        return jsonify({"success": True})

    @app.route("/api/responsible_person", methods=["GET"])
    @stage_log(2)
    def get_responsible_person():
        product_name = request.args.get("product_name")
        if not product_name:
            return jsonify({"error": "Missing product_name"}), 400
        return jsonify(company_info_manager.get_responsible_person(product_name))

    @app.route("/api/responsible_person", methods=["POST"])
    @stage_log(2)
    def set_responsible_person():
        data = request.json
        product_name = data.get("product_name")
        person = data.get("person")
        if not product_name or not person:
            return jsonify({"error": "Missing product_name or person"}), 400
        company_info_manager.set_responsible_person(product_name, person)
        return jsonify({"success": True})

    # Global error handler for API endpoints to always return JSON
    @app.errorhandler(Exception)
    def handle_api_exceptions(error):
        from werkzeug.exceptions import HTTPException
        # Only intercept API routes
        if request.path.startswith('/api/'):
            code = 500
            if isinstance(error, HTTPException):
                code = error.code
                description = error.description
            else:
                description = str(error)
            # Optionally log the traceback for debugging
            current_app.logger.error(f"API Exception: {description}\n{traceback.format_exc()}")
            return jsonify({"error": description}), code
        # For non-API routes, use default error handling
        raise error

    return app

# Create the app
app = create_app()

@stage_log(2)
def open_browser():
    webbrowser.open('http://localhost:5000')

@stage_log(2)
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

@stage_log(2)
def orchestrate_meeting_flow(chat_summary: str, lead_email: str, lead_name: str, send_email: bool = True) -> dict:
    # 1. Extract product from chat summary
    company_info = storage.get_company_info().get('info', '')
    products = product_extractor.extract_products(company_info)
    if not products:
        raise MeetingSchedulingError("No products found in company info.")
    # For demo, pick the first product
    product = products[0]
    # 2. Find responsible person (with fallback)
    responsible = responsible_person_agent.get_responsible_person(product)
    if responsible.get('email', '').startswith('default-'):
        logger.warning(f"No responsible person set for product '{product}'. Using default: {responsible}")
    # 3. Check availability
    slots = availability_agent.check_availability(lead_email, responsible['email'])
    if not slots:
        raise MeetingSchedulingError("No available slots found.")
    slot = slots[0]
    # 4. Schedule meeting
    meeting_link = meeting_scheduler.create_meeting(slot, [lead_email, responsible['email']])
    if not meeting_link:
        raise MeetingSchedulingError("Failed to create meeting link.")
    # 5. Prepare email
    details = {
        'subject': f'Meeting Scheduled for {product}',
        'body': f'Hi {lead_name}, your meeting for {product} is scheduled with {responsible["name"]}.'
    }
    email_content = f"Hi {lead_name}, your meeting for {product} is scheduled with {responsible['name']} at {slot}. Meeting Link: {meeting_link}"
    email_sent = False
    if send_email:
        email_sent = email_agent.send_meeting_invite(lead_email, meeting_link, details)
        if not email_sent:
            raise MeetingSchedulingError("Failed to send meeting invite email.")
    return {
        "success": True,
        "meeting_link": meeting_link,
        "slot": slot,
        "responsible": responsible,
        "product": product,
        "email_content": email_content,
        "email_sent": email_sent
    }

# --- New Endpoints for Meeting Proposal/Review/Send ---
from flask import abort
import pandas as pd
import json

@app.route("/api/generate_meeting_proposal", methods=["POST"])
@stage_log(2)
def api_generate_meeting_proposal():
    data = request.json
    lead_id = data.get("lead_id")
    if not lead_id:
        return jsonify({"success": False, "error": "Missing lead_id"}), 400
    REPORT_PATH = 'data/report.xlsx'
    if not os.path.exists(REPORT_PATH):
        raise ConfigurationError("No report found: report.xlsx does not exist.")
    try:
        df = pd.read_excel(REPORT_PATH)
    except Exception as e:
        raise ConfigurationError(f"Failed to read report file: {e}")

    mask = df['ID'].astype(str) == str(lead_id)
    if not mask.any():
        raise MeetingSchedulingError("Lead not found in report.")
    chat_summary = df.loc[mask, 'Chat Summary'].iloc[0]
    lead_email = df.loc[mask, 'Email'].iloc[0]
    lead_name = df.loc[mask, 'Name'].iloc[0]
    
    result = orchestrate_meeting_flow(chat_summary, lead_email, lead_name, send_email=False)
    
    df.loc[mask, 'Pending Meeting Email'] = result['email_content']
    df.loc[mask, 'Pending Meeting Info'] = json.dumps(result)
    df.loc[mask, 'Meeting Email Sent'] = 'No'
    df.to_excel(REPORT_PATH, index=False)
    return jsonify({"success": True, "meeting_info": result})

@app.route("/api/review_meeting_email", methods=["POST"])
@stage_log(2)
def api_review_meeting_email():
    data = request.json
    lead_id = data.get("lead_id")
    if not lead_id:
        return jsonify({"success": False, "error": "Missing lead_id"}), 400
    REPORT_PATH = 'data/report.xlsx'
    if not os.path.exists(REPORT_PATH):
        raise ConfigurationError("No report found: report.xlsx does not exist.")
    try:
        df = pd.read_excel(REPORT_PATH)
    except Exception as e:
        raise ConfigurationError(f"Failed to read report file: {e}")
    
    mask = df['ID'].astype(str) == str(lead_id)
    if not mask.any():
        raise MeetingSchedulingError("Lead not found in report.")
    email_content = df.loc[mask, 'Pending Meeting Email'].iloc[0]
    meeting_info = df.loc[mask, 'Pending Meeting Info'].iloc[0]
    if not email_content:
        raise MeetingSchedulingError("No pending meeting email content found for this lead.")
    if not meeting_info:
        raise MeetingSchedulingError("No pending meeting info found for this lead.")
    
    return jsonify({"success": True, "email_content": email_content, "meeting_info": meeting_info})

@app.route("/api/send_meeting_email", methods=["POST"])
@stage_log(2)
def api_send_meeting_email():
    data = request.json
    lead_id = data.get("lead_id")
    if not lead_id:
        return jsonify({"success": False, "error": "Missing lead_id"}), 400
    REPORT_PATH = 'data/report.xlsx'
    if not os.path.exists(REPORT_PATH):
        raise ConfigurationError("No report found: report.xlsx does not exist.")
    try:
        df = pd.read_excel(REPORT_PATH)
    except Exception as e:
        raise ConfigurationError(f"Failed to read report file: {e}")

    mask = df['ID'].astype(str) == str(lead_id)
    if not mask.any():
        raise MeetingSchedulingError("Lead not found in report.")
    meeting_info_json = df.loc[mask, 'Pending Meeting Info'].iloc[0]
    if not meeting_info_json:
        raise MeetingSchedulingError("No pending meeting info.")
    try:
        meeting_info = json.loads(meeting_info_json)
    except json.JSONDecodeError:
        raise MeetingSchedulingError("Invalid JSON for pending meeting info.")
    lead_email = df.loc[mask, 'Email'].iloc[0]
    # Actually send the email
    details = {
        'subject': f"Meeting Scheduled for {meeting_info.get('product', '')}",
        'body': meeting_info.get('email_content', '')
    }
    meeting_link = meeting_info.get('meeting_link', '')
    email_sent = email_agent.send_meeting_invite(lead_email, meeting_link, details)
    if email_sent:
        df.loc[mask, 'Meeting Email Sent'] = 'Yes'
        df.to_excel(REPORT_PATH, index=False)
        return jsonify({"success": True})
    else:
        raise MeetingSchedulingError("Failed to send email.")

DEFAULT_RESPONSIBLE_PATH = "data/default_responsible_person.json"

def load_default_responsible():
    if os.path.exists(DEFAULT_RESPONSIBLE_PATH):
        with open(DEFAULT_RESPONSIBLE_PATH, "r") as f:
            try:
                data = json.load(f)
                return {
                    "name": data.get("name", "Default Owner"),
                    "email": data.get("email", "default-owner@yourcompany.com")
                }
            except Exception:
                pass
    return {"name": "Default Owner", "email": "default-owner@yourcompany.com"}

def save_default_responsible(name, email):
    os.makedirs(os.path.dirname(DEFAULT_RESPONSIBLE_PATH), exist_ok=True)
    with open(DEFAULT_RESPONSIBLE_PATH, "w") as f:
        json.dump({"name": name, "email": email}, f)

@app.route("/api/default_responsible_person", methods=["GET", "POST"])
def api_default_responsible_person():
    if request.method == "GET":
        return jsonify(load_default_responsible())
    elif request.method == "POST":
        data = request.get_json()
        name = data.get("name", "Default Owner")
        email = data.get("email", "default-owner@yourcompany.com")
        save_default_responsible(name, email)
        return jsonify({"success": True, "name": name, "email": email})
    else:
        return jsonify({"error": "Method not allowed"}), 405

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
            host='0.0.0.0',
            use_reloader=False
        )
    finally:
        if icon_thread.is_alive():
            icon.stop() 