import json
import sys
import uuid
from pathlib import Path
import boto3

TMP = Path(__file__).resolve().parent.parent / "tmp"

def read(name):
    path = TMP / name
    return path.read_text().strip() if path.exists() else ""


def write(name, content):
    (TMP / name).write_text(content)


# All inputs are read once, here at startup. Functions reference these only.
USER_ID = str(uuid.uuid4())
RETURN_URL = "http://localhost:12345/"
WORKLOAD_IDENTITY_NAME = read("workload_identity_name.txt")
CREDENTIAL_PROVIDER_NAME = read("credential_provider_name.txt")

client = boto3.client("bedrock-agentcore")

def get_workload_access_token():
    print("> Getting workload access token for user federation...")
    resp = client.get_workload_access_token_for_user_id(
        workloadName=WORKLOAD_IDENTITY_NAME,
        userId=USER_ID,
    )
    workload_access_token = resp["workloadAccessToken"]
    print(f"| workload_access_token={workload_access_token[:20]}...")
    return workload_access_token

def start_oauth2_workflow():
    print(f"> Starting authentication workflow for '{CREDENTIAL_PROVIDER_NAME}'...")
    workload_access_token = get_workload_access_token()
    resp = client.get_resource_oauth2_token(
        resourceCredentialProviderName=CREDENTIAL_PROVIDER_NAME,
        workloadIdentityToken=workload_access_token,
        scopes=[],
        oauth2Flow="USER_FEDERATION",
        resourceOauth2ReturnUrl=RETURN_URL,
    )
    # print(json.dumps(resp, indent=2, default=str))

    status_code = resp["ResponseMetadata"]["HTTPStatusCode"]
    authz_url = resp["authorizationUrl"]
    session_uri = resp["sessionUri"]
    print(f"| status_code={status_code}")
    print(f"| authz_url={authz_url}")
    print(f"| session_uri={session_uri}")
    return session_uri

def complete_auth(session_uri):
    print(f"> Finishing authentication workflow for '{CREDENTIAL_PROVIDER_NAME}'...")
    resp = client.complete_resource_token_auth(
        sessionUri=session_uri,
        userIdentifier={"userId": USER_ID},
    )
    # print(json.dumps(resp, indent=2, default=str))

    status_code = resp["ResponseMetadata"]["HTTPStatusCode"]
    print(f"| status_code={status_code}")

def get_resource_token():
    print(f"> Getting resource token from '{CREDENTIAL_PROVIDER_NAME}'...")
    workload_access_token = get_workload_access_token()
    resp = client.get_resource_oauth2_token(
        resourceCredentialProviderName=CREDENTIAL_PROVIDER_NAME,
        workloadIdentityToken=workload_access_token,
        scopes=[],
        oauth2Flow="USER_FEDERATION",
        resourceOauth2ReturnUrl=RETURN_URL,
    )
    # print(json.dumps(resp, indent=2, default=str))
    status_code = resp["ResponseMetadata"]["HTTPStatusCode"]
    access_token = resp["accessToken"]
    print(f"| status_code={status_code}")
    print(f"| access_token={access_token}")
    return access_token


session_uri = start_oauth2_workflow()
input("\nOpen authz_url in your browser and log in, then press Enter to continue...")
complete_auth(session_uri)
get_resource_token()


