import requests
import time

import jwt

def get_access_token(service_account_info):
    private_key = service_account_info["private_key"]
    service_account_email = service_account_info["client_email"]

    now = int(time.time())
    issued_at = now
    expiration_time = now + 3600

    payload = {
        "iss": service_account_email,
        "aud": "https://www.googleapis.com/oauth2/v4/token",
        "iat": issued_at,
        "exp": expiration_time,
        "scope": "https://www.googleapis.com/auth/cloud-platform",  # This is the scope needed to get an id_token
    }

    signed_jwt = jwt.encode(
        payload,
        private_key,
        algorithm="RS256",
    )

    resp = requests.post(
        "https://www.googleapis.com/oauth2/v4/token",
        data={
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": signed_jwt,
        },
    )

    if not resp.ok:
        print("Failed to get access_token: ")
        print(resp.text)
        exit(1)

    data = resp.json()

    access_token = data["access_token"]
    return access_token
