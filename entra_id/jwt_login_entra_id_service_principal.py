import requests
import base64
import configparser
import os

config_file = configparser.ConfigParser()
config_file.read("./config.ini")

config = config_file["config"]

TENANT_ID = os.getenv("SLASHDB_TENANT_ID", config["tenant_id"])
CLIENT_ID = os.getenv("SLASHDB_CLIENT_ID", config["client_id"])
CLIENT_SECRET = os.getenv("SLASHDB_CLIENT_SECRET", config["client_secret"])
SLASHDB_IDP_ID = os.getenv('SLASHDB_IDP_ID', config["slashdb_idp_id"])
SLASHDB_URL = os.getenv('SLASHDB_URL', config["slashdb_url"])

token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"

resp = requests.post(
    token_url,
    data={
        "client_id": CLIENT_ID,
        "scope": f"{CLIENT_ID}/.default",
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials",
    },
)

if not resp.ok:
    print("Failed to get id_token:")
    print(resp.text)
    exit(1)

data = resp.json()

id_token = data["access_token"]

# SlashDB expects a base64 encoded token
b64_encoded = (
    base64.encodebytes(id_token.encode("utf-8")).decode("utf-8").replace("\n", "")
)
auth_header_value = f"Bearer {b64_encoded}"


headers = {
    "Authorization": auth_header_value,
    "X-Identity-Provider-ID": SLASHDB_IDP_ID,
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
