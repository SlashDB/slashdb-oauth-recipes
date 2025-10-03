import configparser
import base64

import requests

import msal
import os
import atexit

cache_filename = os.path.join(  # Persist cache into this file
    os.getcwd(),
    "token_cache.json",
)
cache = msal.SerializableTokenCache()

if os.path.exists(cache_filename):
    cache.deserialize(open(cache_filename, "r").read())

atexit.register(
    lambda: open(cache_filename, "w").write(cache.serialize())
    if cache.has_state_changed
    else None
)

config_file = configparser.ConfigParser()
config_file.read("./config.ini")

config = config_file["config"]

TENANT_ID = os.getenv("SLASHDB_TENANT_ID", config["tenant_id"])
CLIENT_ID = os.getenv("SLASHDB_CLIENT_ID", config["client_id"])
SLASHDB_IDP_ID = os.getenv('SLASHDB_IDP_ID', config["slashdb_idp_id"])
SLASHDB_URL = os.getenv('SLASHDB_URL', config["slashdb_url"])

authority_url = f"https://login.microsoftonline.com/{TENANT_ID}"

app = msal.PublicClientApplication(CLIENT_ID, authority=authority_url, token_cache=cache)

result = None

# We now check the cache to see
# whether we already have some accounts that the end user already used to sign in before.
accounts = app.get_accounts()
if accounts:
    print("Using a cached token.")
    # Using the first account in cache
    chosen = accounts[0]
    # Now let's try to find a token in cache for this account
    result = app.acquire_token_silent(["email openid"], account=chosen)

if not result:
    print("Initiating interactive login.")
    # So no suitable token exists in cache. Let's get a new one from Entra ID.
    result = app.acquire_token_interactive(scopes=["email"])
if "id_token" in result:
    id_token = result["id_token"]
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
else:
    print(result.get("error"))
    print(result.get("error_description"))
    print(result.get("correlation_id"))  # You may need this when reporting a bug
