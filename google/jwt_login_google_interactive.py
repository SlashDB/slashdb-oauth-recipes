import json
from flask import Flask, redirect, request
from werkzeug.serving import make_server
import requests
from threading import Thread, Event
import webbrowser
import base64
import configparser

config_file = configparser.ConfigParser()
config_file.read("config.ini")
config = config_file["config"]

service_account_info_file = config["service_account_info_file"]
slashdb_idp_id = config["slashdb_idp_id"]

with open(service_account_info_file) as f:
    service_account_info = json.load(f)

CLIENT_ID = config["client_id"]
CLIENT_SECRET = config["client_secret"]
SLASHDB_URL = config["slashdb_url"]

SERVER_PORT = 5000
REDIRECT_URI = f'http://127.0.0.1:{SERVER_PORT}/callback'
SCOPE = 'openid email'


app = Flask(__name__)
app.secret_key = '2d8Z3Z4wBFhR32OX0atmz1ES0kJ2J86C'

TOKEN_CACHE_FILE = "token_cache.json"

token_data = None

server = None

shutdown_event = Event()

@app.route('/')
def index():
    return '<a href="/login">Login with Google</a>'

@app.route('/login')
def login():
    # Redirect to Google's OAuth 2.0 server
    auth_url = (
        f"https://accounts.google.com/o/oauth2/auth?"
        f"response_type=code&"
        f"client_id={CLIENT_ID}&"
        f"redirect_uri={REDIRECT_URI}&"
        f"scope={SCOPE}&"
        f"access_type=offline&"
        "&prompt=consent"
    )

    return redirect(auth_url)

@app.route('/callback')
def callback():
    # Get the authorization code from the URL
    code = request.args.get('code')

    # Exchange the authorization code for an access token
    token_url = 'https://oauth2.googleapis.com/token'
    payload = {
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code',
    }

    response = requests.post(token_url, data=payload)
    global token_data
    token_data = response.json()

    shutdown_event.set()

    return "Authentication successful! You can close this tab now."

def run_server():
    global server
    server = make_server("127.0.0.1", SERVER_PORT, app)
    server.serve_forever()

def refresh_access_token(refresh_token):
    token_url = 'https://oauth2.googleapis.com/token'
    payload = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token',
    }

    response = requests.post(token_url, data=payload)
    return response.json()

def main():
    global server, token_data

    # try to get token from cache
    try:
        with open(TOKEN_CACHE_FILE, "r+") as file:
            token_data = json.load(file)
            print("Loaded token data from cache")
    except FileNotFoundError:
        print("No token cache, requesting interactive login")

        # run server so that user can log in through the browser
        server_thread = Thread(target=run_server)
        server_thread.start()
        webbrowser.open(f"http://127.0.0.1:{SERVER_PORT}/")
        if shutdown_event.wait():
            server.shutdown()
        server_thread.join()

    refresh_token = token_data["refresh_token"]
    token_data = refresh_access_token(refresh_token)
    token_data["refresh_token"] = refresh_token

    access_token = token_data["id_token"]

    with open(TOKEN_CACHE_FILE, "w+") as file:
        json.dump(token_data, file)

    # use the token to authenticate to slashdb
    b64_encoded = (
        base64.encodebytes(access_token.encode("utf-8")).decode("utf-8").replace("\n", "")
    )
    auth_header_value = f"Bearer {b64_encoded}"
    headers={
        "Authorization": auth_header_value,
        "X-Identity-Provider-ID": slashdb_idp_id,
    }
    resp = requests.get(
        f"{SLASHDB_URL}/settings.json",
        headers=headers,
    )
    print("Authenticated as: ", resp.json()["user"])

    # Data Discovery
    resp = requests.get(
        f"{SLASHDB_URL}/db/Chinook/Album.json?limit=2",
        headers=headers,
    )
    print(resp.json())

    # SQL Pass-thru
    resp = requests.get(
        f"{SLASHDB_URL}/query/invoices-by-year/year/2013.json?limit=3",
        headers=headers,
    )
    print(resp.json())


if __name__ == "__main__":
    main()
