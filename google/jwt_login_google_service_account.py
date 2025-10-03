import requests
import base64
import json
import configparser
import os

import utils

config_file = configparser.ConfigParser()
config_file.read("config.ini")
config = config_file["config"]

SLASHDB_URL = os.getenv('SLASHDB_URL', config["slashdb_url"])

service_account_info_file = config["service_account_info_file"]
slashdb_idp_id = config["slashdb_idp_id"]

with open(service_account_info_file) as f:
    service_account_info = json.load(f)

access_token = utils.get_access_token(service_account_info)

resp = requests.post(
    f"https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/{service_account_info['client_email']}:generateIdToken",
    headers={
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8",
    },
    json={
        "audience": "slashdb",  # It doesn't matter what you put here, but it can't be empty
        "includeEmail": "true",  # This is makes the JWT include the email claim
    },
)

if not resp.ok:
    print("Failed to get ID token: ")
    print(resp.text)
    exit(1)

data = resp.json()
id_token = data["token"]

# SlashDB expects a base64 encoded token
b64_encoded = (
    base64.encodebytes(id_token.encode("utf-8")).decode("utf-8").replace("\n", "")
)
auth_header_value = f"Bearer {b64_encoded}"


headers = {
    "Authorization": auth_header_value,
    "X-Identity-Provider-ID": slashdb_idp_id,
}
resp = requests.get(
    f"{SLASHDB_URL}/settings.json",
    headers=headers,
)
print("Authenticated as:", resp.json()["user"])

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
