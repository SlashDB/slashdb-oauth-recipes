import configparser
import json

import requests

import utils

config_file = configparser.ConfigParser()
config_file.read("config.ini")
config = config_file["config"]

service_account_info_file = config["service_account_info_file"]
slashdb_idp_id = config["slashdb_idp_id"]

with open(service_account_info_file) as f:
    service_account_info = json.load(f)

project_id = service_account_info["project_id"]
service_account_email = service_account_info["client_email"]

access_token = utils.get_access_token(service_account_info)

resp = requests.post(
    f"https://iam.googleapis.com/v1/projects/{project_id}/serviceAccounts/{service_account_email}:getIamPolicy",
    data={},
    headers={
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8",
    },
)

print(resp.text)

data = resp.json()

data["bindings"].append(
    {
        "role": "roles/iam.serviceAccountOpenIdTokenCreator",
        "members": [f"serviceAccount:{service_account_email}"],
    }
)

resp = requests.post(
    f"https://iam.googleapis.com/v1/projects/{project_id}/serviceAccounts/{service_account_email}:setIamPolicy",
    json={"policy": data},
    headers={
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8",
    },
)

print(resp.text)
