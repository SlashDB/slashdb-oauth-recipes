import subprocess
import json

import requests
import base64
import configparser

config_file = configparser.ConfigParser()
config_file.read("./config.ini")

config = config_file["config"]

SLASHDB_IDP_ID = config["slashdb_idp_id"]
SLASHDB_URL = config["slashdb_url"]


def get_access_token() -> str:
    try:
        # Run the command and capture the output
        result = subprocess.run(
            ["az", "account", "get-access-token"],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(
                f"Failed to get access token, az return error code {result.returncode}."
            )
            print(result.stderr)
            exit(1)

        # Parse the JSON output
        access_token_info = json.loads(result.stdout)
        return access_token_info["accessToken"]

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        exit(1)


id_token = get_access_token()

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
