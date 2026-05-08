import dotenv
import os
import oauth2_workflow
from pathlib import Path

dotenv.load_dotenv(
    dotenv_path=Path("./../workday.configuration")
)

def handle_integration_client_authz():
    print("-" * 20)
    print("Retrieving Integration Client configuration")

    INTEGRATION_CLIENT_ID = os.getenv("INTEGRATION_CLIENT_ID")
    INTEGRATION_CLIENT_SECRET = os.getenv("INTEGRATION_CLIENT_SECRET")
    INTEGRATION_CLIENT_AUTHZ_ENDPOINT = os.getenv("INTEGRATION_CLIENT_AUTHZ_ENDPOINT")
    INTEGRATION_CLIENT_TOKEN_ENDPOINT = os.getenv("INTEGRATION_CLIENT_TOKEN_ENDPOINT")
    INTEGRATION_CLIENT_REDIRECT_URI = os.getenv("INTEGRATION_CLIENT_REDIRECT_URI")
    AGENT_CARD_URL = os.getenv("AGENT_CARD_URL")
    AGENT_CARD_PATH = Path("./../tmp/agent_card.json")

    print(f"| INTEGRATION_CLIENT_ID={INTEGRATION_CLIENT_ID}")
    print(f"| INTEGRATION_CLIENT_SECRET={INTEGRATION_CLIENT_SECRET[:2]}...REDACTED...")
    print(f"| INTEGRATION_CLIENT_AUTHZ_ENDPOINT={INTEGRATION_CLIENT_AUTHZ_ENDPOINT}")
    print(f"| INTEGRATION_CLIENT_TOKEN_ENDPOINT={INTEGRATION_CLIENT_TOKEN_ENDPOINT}")
    print(f"| INTEGRATION_CLIENT_REDIRECT_URI={INTEGRATION_CLIENT_REDIRECT_URI}")
    print(f"| AGENT_CARD_URL={AGENT_CARD_URL}")

    print("-" * 20)
    print("Retrieving tokens")
    access_token = oauth2_workflow.acquire_tokens(
        client_name="integration_client",
        client_id=INTEGRATION_CLIENT_ID,
        client_secret=INTEGRATION_CLIENT_SECRET,
        authz_endpoint=INTEGRATION_CLIENT_AUTHZ_ENDPOINT,
        token_endpoint=INTEGRATION_CLIENT_TOKEN_ENDPOINT,
        redirect_uri=INTEGRATION_CLIENT_REDIRECT_URI,
    )

