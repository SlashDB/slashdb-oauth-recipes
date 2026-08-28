import base64
import requests
import os

import configparser

config_file = configparser.ConfigParser()
config_file.read("./config.ini")

config = config_file["config"]

CLIENT_ID = os.getenv("OKTA_CLIENT_ID", config["client_id"])
CLIENT_SECRET = os.getenv("OKTA_CLIENT_SECRET", config["client_secret"])
SLASHDB_IDP_ID = os.getenv("SLASHDB_IDP_ID", config["slashdb_idp_id"])
SLASHDB_URL = os.getenv("SLASHDB_URL", config["slashdb_url"])

# Endpoint for the token request
TOKEN_URL = os.getenv("OKTA_TOKEN_URL", config["token_url"])


def get_jwt() -> str:
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        # It requires okta API services app.
        "grant_type": "client_credentials"
    }

    response = requests.post(TOKEN_URL, data=payload)

    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("id_token")
        return access_token
    else:
        print("Failed to get token from Okta:")
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
