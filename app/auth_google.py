import os
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests

router = APIRouter()

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar"
]

CLIENT_SECRETS_FILE = "client_secret.json"
REDIRECT_URI = "http://localhost:8080/auth/callback"

# Temporary in-memory token storage, but it's better to use DB in production later on
user_tokens = {}

@router.get("/login")
def login():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='false',
        prompt='consent'
    )
    return RedirectResponse(auth_url)

@router.get("/auth/callback")
def auth_callback(request: Request):
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    # flow.fetch_token(authorization_response=str(request.url))
    flow.fetch_token(
        authorization_response=str(request.url),
        include_client_id=True,
        authorization_response_params={"access_type": "offline"},
        **{"include_granted_scopes": "true"}
    )

    credentials = flow.credentials

    # Extract info from ID token
    id_info = google_id_token.verify_oauth2_token(
        credentials._id_token, google_requests.Request(), flow.client_config['client_id']
    )
    user_email = id_info.get("email")
    user_name = id_info.get("name")
    user_pic = id_info.get("picture")

    # Store tokens in memory (or later: a secure DB)
    user_tokens[user_email] = credentials
    print(f"TOKENS NOW: {user_tokens}")

    # Redirect to chatbot with user info as query params
    return RedirectResponse(
        url=f"/static/index.html?name={user_name}&email={user_email}&pic={user_pic}"
    )

def get_calendar_service(user_email: str):
    print(f"[auth_google] user_email passed to get_calendar_service: {user_email}")
    print(f"[auth_google] current user_tokens: {list(user_tokens.keys())}")
    creds = user_tokens.get(user_email)
    if not creds:
        raise Exception("User not logged in")
    return build("calendar", "v3", credentials=creds)
