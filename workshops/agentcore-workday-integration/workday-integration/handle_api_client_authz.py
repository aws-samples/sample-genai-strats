import dotenv
import os
import oauth2_workflow
from pathlib import Path

dotenv.load_dotenv(
    dotenv_path=Path("./../workday.configuration")
)

def handle_api_client_authz():
    print("-" * 20)
    print("Retrieving API Client configuration")

    API_CLIENT_ID = os.getenv("API_CLIENT_ID")
    API_CLIENT_SECRET = os.getenv("API_CLIENT_SECRET")
    API_CLIENT_AUTHZ_ENDPOINT = os.getenv("API_CLIENT_AUTHZ_ENDPOINT")
    API_CLIENT_TOKEN_ENDPOINT = os.getenv("API_CLIENT_TOKEN_ENDPOINT")
    API_CLIENT_REDIRECT_URI = os.getenv("API_CLIENT_REDIRECT_URI")
    AGENT_CARD_URL = os.getenv("AGENT_CARD_URL")
    AGENT_CARD_PATH = Path("./../tmp/agent_card.json")

    print(f"| API_CLIENT_ID={API_CLIENT_ID}")
    print(f"| API_CLIENT_SECRET={API_CLIENT_SECRET[:2]}...REDACTED...")
    print(f"| API_CLIENT_AUTHZ_ENDPOINT={API_CLIENT_AUTHZ_ENDPOINT}")
    print(f"| API_CLIENT_TOKEN_ENDPOINT={API_CLIENT_TOKEN_ENDPOINT}")
    print(f"| API_CLIENT_REDIRECT_URI={API_CLIENT_REDIRECT_URI}")
    print(f"| AGENT_CARD_URL={AGENT_CARD_URL}")

    print("-" * 20)
    print("Retrieving tokens")
    access_token = oauth2_workflow.acquire_tokens(
        client_name="api_client",
        client_id=API_CLIENT_ID,
        client_secret=API_CLIENT_SECRET,
        authz_endpoint=API_CLIENT_AUTHZ_ENDPOINT,
        token_endpoint=API_CLIENT_TOKEN_ENDPOINT,
        redirect_uri=API_CLIENT_REDIRECT_URI,
    )

