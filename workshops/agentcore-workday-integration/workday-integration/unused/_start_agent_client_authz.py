import dotenv
import os

import oauth2_workflow

dotenv.load_dotenv()

# --- Retrieve configuration ---
print("-" * 20)
print("Retrieving Agent Client configuration")

AGENT_CLIENT_ID = os.getenv("AGENT_CLIENT_ID")
AGENT_CLIENT_SECRET = os.getenv("AGENT_CLIENT_SECRET")
AGENT_CLIENT_AUTHZ_ENDPOINT = os.getenv("AGENT_CLIENT_AUTHZ_ENDPOINT")
AGENT_CLIENT_TOKEN_ENDPOINT = os.getenv("AGENT_CLIENT_TOKEN_ENDPOINT")
AGENT_CLIENT_REDIRECT_URI = os.getenv("AGENT_CLIENT_REDIRECT_URI")

print(f"| AGENT_CLIENT_ID={AGENT_CLIENT_ID}")
print(f"| AGENT_CLIENT_SECRET={AGENT_CLIENT_SECRET[:2]}...REDACTED...")
print(f"| AGENT_CLIENT_AUTHZ_ENDPOINT={AGENT_CLIENT_AUTHZ_ENDPOINT}")
print(f"| AGENT_CLIENT_TOKEN_ENDPOINT={AGENT_CLIENT_TOKEN_ENDPOINT}")
print(f"| AGENT_CLIENT_REDIRECT_URI={AGENT_CLIENT_REDIRECT_URI}")

# --- Acquire tokens ---
oauth2_workflow.acquire_tokens(
    client_name="agent_client",
    client_id=AGENT_CLIENT_ID,
    client_secret=AGENT_CLIENT_SECRET,
    authz_endpoint=AGENT_CLIENT_AUTHZ_ENDPOINT,
    token_endpoint=AGENT_CLIENT_TOKEN_ENDPOINT,
    redirect_uri=AGENT_CLIENT_REDIRECT_URI,
)
