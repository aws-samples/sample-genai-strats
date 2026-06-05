import asyncio
import requests
from logger import get_logger
import os
import boto3
from bedrock_agentcore.services.identity import IdentityClient

l = get_logger(__name__)

region = boto3.session.Session().region_name
identity_client = IdentityClient(region)
CREDENTIAL_PROVIDER_NAME = os.environ.get("CREDENTIAL_PROVIDER_NAME")

def get_token():
    l.info(f"> get_token")
    
    if not CREDENTIAL_PROVIDER_NAME:
        return _get_token_from_cognito_endpoint()
    else:
        return _get_token_from_agentcore_identity_credential_provider()

def _get_token_from_cognito_endpoint():
    l.info(f"> _get_token_from_cognito_endpoint")
    COGNITO_CLIENT_ID = os.environ.get("COGNITO_CLIENT_ID")
    COGNITO_CLIENT_SECRET = os.environ.get("COGNITO_CLIENT_SECRET")
    COGNITO_TOKEN_ENDPOINT = os.environ.get("COGNITO_TOKEN_ENDPOINT")
    COGNITO_SCOPE = os.environ.get("COGNITO_SCOPE")

    l.info(f"COGNITO_CLIENT_ID={COGNITO_CLIENT_ID}")
    l.info(f"COGNITO_CLIENT_SECRET={COGNITO_CLIENT_SECRET[:2]}...REDACTED")
    l.info(f"COGNITO_TOKEN_ENDPOINT={COGNITO_TOKEN_ENDPOINT}")
    l.info(f"COGNITO_SCOPE={COGNITO_SCOPE}")

    _required = [COGNITO_CLIENT_ID, COGNITO_CLIENT_SECRET, COGNITO_TOKEN_ENDPOINT, COGNITO_SCOPE]
    if not all(_required):
        l.warning("⚠️ One or more required env vars are missing")
        return None

    l.info(f"> sending request")
    response = requests.post(
        COGNITO_TOKEN_ENDPOINT,
        data={
            "grant_type":    "client_credentials",
            "client_id":     COGNITO_CLIENT_ID,
            "client_secret": COGNITO_CLIENT_SECRET,
            "scope":         COGNITO_SCOPE,
        },
    )
    
    l.info(f"| response.status_code={response.status_code}")
    response.raise_for_status()
    access_token = response.json()["access_token"]
    return access_token



def _get_token_from_agentcore_identity_credential_provider():
    l.info(f"> _get_token_from_agentcore_identity_credential_provider")

    WORKLOAD_ID_NAME = os.environ.get("WORKLOAD_ID_NAME")
    COGNITO_SCOPE = os.environ.get("COGNITO_SCOPE")

    l.info(f"CREDENTIAL_PROVIDER_NAME={CREDENTIAL_PROVIDER_NAME}")
    l.info(f"WORKLOAD_ID_NAME={WORKLOAD_ID_NAME}")
    l.info(f"COGNITO_SCOPE={COGNITO_SCOPE}")

    _required = [CREDENTIAL_PROVIDER_NAME, WORKLOAD_ID_NAME, COGNITO_SCOPE]
    if not all(_required):
        l.warning("⚠️ One or more required env vars are missing")
        return None

    l.info("Getting workload access token...")
    response = identity_client.get_workload_access_token(workload_name=WORKLOAD_ID_NAME)
    workload_access_token = response.get("workloadAccessToken")
    l.info(f"| workload_access_token={workload_access_token[:10]}...REDACTED...")

    l.info("Getting resource access token...")
    resource_access_token = asyncio.run(identity_client.get_token(
        provider_name=CREDENTIAL_PROVIDER_NAME,
        scopes=[COGNITO_SCOPE],
        auth_flow="M2M",
        agent_identity_token=workload_access_token
    ))
    l.info(f"| resource_access_token={resource_access_token[:10]}...REDACTED...")
    return resource_access_token
