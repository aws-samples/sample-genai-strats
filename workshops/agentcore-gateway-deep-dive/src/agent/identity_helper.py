import requests
import os
from logger import get_logger

l = get_logger(__name__)


def get_token() -> str | None:
    client_id     = os.environ.get("COGNITO_CLIENT_ID")
    client_secret = os.environ.get("COGNITO_CLIENT_SECRET")
    token_endpoint = os.environ.get("COGNITO_TOKEN_ENDPOINT")
    scope         = os.environ.get("COGNITO_SCOPE")

    if not all([client_id, client_secret, token_endpoint, scope]):
        l.warning("⚠️ Cognito env vars not set - gateway tools disabled")
        return None

    l.info(f"COGNITO_CLIENT_ID={client_id}")
    l.info(f"COGNITO_TOKEN_ENDPOINT={token_endpoint}")
    l.info(f"COGNITO_SCOPE={scope}")

    response = requests.post(
        token_endpoint,
        data={
            "grant_type":    "client_credentials",
            "client_id":     client_id,
            "client_secret": client_secret,
            "scope":         scope,
        },
    )
    response.raise_for_status()
    return response.json()["access_token"]
