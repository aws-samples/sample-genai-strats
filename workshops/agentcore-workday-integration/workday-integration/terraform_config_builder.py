import base64
import json
import os
from pathlib import Path
import dotenv

config_path = Path(__file__).parent.parent / "workday.configuration"
dotenv.load_dotenv(dotenv_path=config_path)

tmp_path = Path(__file__).parent.parent / "tmp"

print("-" * 20)
print("Building Terraform variables file")

WORKDAY_TENANT_ALIAS = os.environ.get("WORKDAY_TENANT_ALIAS")
print(f"| WORKDAY_TENANT_ALIAS={WORKDAY_TENANT_ALIAS}")

def get_issuer(token_file_path):
    access_token = token_file_path.read_text().strip()
    payload_segment = access_token.split(".")[1]
    payload_segment += "=" * (4 - len(payload_segment) % 4)
    jwt_payload = json.loads(base64.urlsafe_b64decode(payload_segment))
    token_issuer = jwt_payload["iss"]
    return token_issuer

# Retrieving Agent Mode
print("> Retrieving agent mode")
agent_mode = os.environ.get("MODE")
if not agent_mode:
    print("ERROR: MODE environment variable is required")
    exit(1)
print(f"| AGENT_MODE={agent_mode}")

if agent_mode=="mcp":
    print("> Retrieving MCP Agent configuration")
    token_file_path = tmp_path / "mcp_agent_access_token.txt"
    token_issuer = get_issuer(token_file_path)
    print(f"| token_issuer={token_issuer}")

    CLIENT_ID = os.environ.get("AGENT_MCP_CLIENT_ID")
    CLIENT_SECRET = os.environ.get("AGENT_MCP_CLIENT_SECRET")
    AUTHORIZATION_ENDPOINT = os.environ.get("AGENT_MCP_AUTHORIZATION_ENDPOINT")
    TOKEN_ENDPOINT = os.environ.get("AGENT_MCP_TOKEN_ENDPOINT")
    
    access_token_path = Path(__file__).parent.parent / "tmp" / "mcp_agent_access_token.txt"

elif agent_mode=="a2a":
    print("> Retrieving A2A Agent configuration")
    token_file_path = tmp_path / "a2a_agent_access_token.txt"
    token_issuer = get_issuer(token_file_path)
    print(f"| token_issuer={token_issuer}")

    CLIENT_ID = os.environ.get("A2A_AGENT_CLIENT_ID")
    CLIENT_SECRET = os.environ.get("A2A_AGENT_CLIENT_SECRET")
    AUTHORIZATION_ENDPOINT = os.environ.get("A2A_AGENT_AUTHORIZATION_ENDPOINT")
    TOKEN_ENDPOINT = os.environ.get("A2A_AGENT_TOKEN_ENDPOINT")
    
    access_token_path = Path(__file__).parent.parent / "tmp" / "a2a_agent_access_token.txt"

else:
    print("NOOP")

ACCESS_TOKEN = access_token_path.read_text().strip()
MCP_ENDPOINT = os.environ.get("AGENT_MCP_ENDPOINT")
A2A_AGENT_CARD_BASE_URL=os.environ.get("A2A_AGENT_CARD_BASE_URL").replace("TENANT_ALIAS", WORKDAY_TENANT_ALIAS)

print(f"| CLIENT_ID={CLIENT_ID}")
print(f"| CLIENT_SECRET={CLIENT_SECRET[:2]}...REDACTED...")
print(f"| AUTHORIZATION_ENDPOINT={AUTHORIZATION_ENDPOINT}")
print(f"| TOKEN_ENDPOINT={TOKEN_ENDPOINT}")
print(f"| ACCESS_TOKEN={ACCESS_TOKEN[:10]}...REDACTED...")
print(f"| MCP_ENDPOINT={MCP_ENDPOINT}")
print(f"| A2A_AGENT_CARD_BASE_URL={A2A_AGENT_CARD_BASE_URL}")

print("> Writing terraform.tfvars")
values = {
    "wd_agent_mode":agent_mode,
    "wd_agent_client_id": CLIENT_ID,
    "wd_agent_client_secret": CLIENT_SECRET,
    "wd_agent_client_issuer": token_issuer,
    "wd_agent_client_authz_endpoint": AUTHORIZATION_ENDPOINT,
    "wd_agent_client_token_endpoint": TOKEN_ENDPOINT,
    "wd_agent_access_token": ACCESS_TOKEN,
    "wd_agent_mcp_endpoint": MCP_ENDPOINT,
    "wd_agent_card_base_url": A2A_AGENT_CARD_BASE_URL
}

output_path = tmp_path / "terraform.tfvars"
output_path.parent.mkdir(parents=True, exist_ok=True)

lines = [f'{tf_var} = "{value}"' for tf_var, value in values.items()]
output_path.write_text("\n".join(lines) + "\n")
print(f"> Written to {output_path}")

