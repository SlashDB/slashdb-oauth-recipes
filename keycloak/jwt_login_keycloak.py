import base64
import requests
import os

import configparser

config_file = configparser.ConfigParser()
config_file.read("./config.ini")

config = config_file["config"]

KEYCLOAK_URL = os.getenv("SLASHDB_KEYCLOAK_URL", config["keycloak_url"])
REALM_NAME = os.getenv("SLASHDB_KEYCLOAK_REALM_NAME", config["realm_name"])
CLIENT_ID = os.getenv("SLASHDB_CLIENT_ID", config["client_id"])
USERNAME = os.getenv("SLASHDB_KEYCLOAK_USERNAME", config["username"])
PASSWORD = os.getenv("SLASHDB_KEYCLOAK_PASSWORD", config["password"])
SLASHDB_IDP_ID = os.getenv('SLASHDB_IDP_ID', config["slashdb_idp_id"])
SLASHDB_URL = os.getenv('SLASHDB_URL', config["slashdb_url"])

# Endpoint for the token request
TOKEN_URL = f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/token"


def get_jwt() -> str:
    payload = {
        "client_id": CLIENT_ID,
        "username": USERNAME,
        "password": PASSWORD,
        # This uses a "Direct Access Grant" flow
        "grant_type": "password",
    }

    response = requests.post(TOKEN_URL, data=payload)

    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("access_token")
        return access_token
    else:
        print("Failed to get token from Keycloak:")
        print(response.text)
        exit(1)


if __name__ == "__main__":
    jwt = get_jwt()
    b64_encoded = (
        base64.encodebytes(jwt.encode("utf-8")).decode("utf-8").replace("\n", "")
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
