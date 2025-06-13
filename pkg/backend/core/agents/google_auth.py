import os
import pickle
from flask import url_for, redirect, request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request as GoogleRequest

SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS_FILE = 'credentials.json'  # Place this in your backend root
TOKEN_FILE = 'token.pickle'

class GoogleAuthManager:
    def __init__(self):
        self.credentials = None

    def start_auth(self):
        flow = Flow.from_client_secrets_file(
            CREDENTIALS_FILE,
            scopes=SCOPES,
            redirect_uri=url_for('google_auth_callback', _external=True)
        )
        auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline', include_granted_scopes='true')
        return redirect(auth_url)

    def handle_callback(self):
        flow = Flow.from_client_secrets_file(
            CREDENTIALS_FILE,
            scopes=SCOPES,
            redirect_uri=url_for('google_auth_callback', _external=True)
        )
        flow.fetch_token(authorization_response=request.url)
        creds = flow.credentials
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
        return redirect('/')

    def get_credentials(self):
        creds = None
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(GoogleRequest())
                with open(TOKEN_FILE, 'wb') as token:
                    pickle.dump(creds, token)
            else:
                return None
        return creds 