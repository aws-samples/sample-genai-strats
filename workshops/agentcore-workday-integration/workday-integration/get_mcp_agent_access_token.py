import os
import dotenv
from oauth2_workflow import acquire_tokens

print("> Loading configuration...")
dotenv.load_dotenv("./../workday.configuration")
CLIENT_ID = os.getenv("AGENT_MCP_CLIENT_ID")
CLIENT_SECRET = os.getenv("AGENT_MCP_CLIENT_SECRET", "")
AUTHORIZATION_ENDPOINT = os.getenv("AGENT_MCP_AUTHORIZATION_ENDPOINT")
TOKEN_ENDPOINT = os.getenv("AGENT_MCP_TOKEN_ENDPOINT")
REDIRECT_URL = os.getenv("AGENT_MCP_REDIRECT_URL")

print(f"| CLIENT_ID={CLIENT_ID}")
print(f"| CLIENT_SECRET={CLIENT_SECRET[:2]}...REDACTED...")
print(f"| AUTHORIZATION_ENDPOINT={AUTHORIZATION_ENDPOINT}")
print(f"| TOKEN_ENDPOINT={TOKEN_ENDPOINT}")
print(f"| REDIRECT_URL={REDIRECT_URL}")

print("-" * 20)
print("\nIMPORTANT: Before proceeding, ensure your agent \nis configured with the following Redirect URI:")
print(f"\n{REDIRECT_URL}")
input("\nPress Enter to continue...")

acquire_tokens(
    client_name="mcp_agent",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET, 
    authz_endpoint=AUTHORIZATION_ENDPOINT, 
    token_endpoint=TOKEN_ENDPOINT,
    redirect_uri=REDIRECT_URL
)

