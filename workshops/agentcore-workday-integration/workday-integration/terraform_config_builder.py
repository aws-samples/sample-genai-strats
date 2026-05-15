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

# Retrieving Agent Mode
print("> Retrieving agent mode")
agent_mode = os.environ.get("MODE")
if not agent_mode:
    print("ERROR: MODE environment variable is required")
    exit(1)
print(f"| agent_mode={agent_mode}")

# Decode JWT from API client access token and extract issuer
print("> Retrieving Issuer from API Client access token")
access_token = (tmp_path / "api_client_access_token.txt").read_text().strip()
payload_segment = access_token.split(".")[1]
payload_segment += "=" * (4 - len(payload_segment) % 4)
jwt_payload = json.loads(base64.urlsafe_b64decode(payload_segment))
agent_client_issuer = jwt_payload["iss"]
print(f"| agent_client_issuer={agent_client_issuer}")

# Extract authz and token endpoints from agent card
print("> Retrieving authz/token endpoints from Agent Card")
agent_card = json.loads((tmp_path / "a2a_agent_card.json").read_text())
oauth_flows = agent_card["securitySchemes"]["WorkdayOAuth"]["flows"]["authorizationCode"]
agent_client_authz_endpoint = oauth_flows["authorizationUrl"]
agent_client_token_endpoint = oauth_flows["tokenUrl"]
print(f"| agent_client_authz_endpoint={agent_client_authz_endpoint}")
print(f"| agent_client_token_endpoint={agent_client_token_endpoint}")

print("> Writing terraform.tfvars")
values = {
    "wd_agent_mode":agent_mode,
    "wd_agent_client_id": os.environ["A2A_AGENT_CLIENT_ID"],
    "wd_agent_client_secret": os.environ["A2A_AGENT_CLIENT_SECRET"],
    "wd_agent_client_issuer": agent_client_issuer,
    "wd_agent_client_authz_endpoint": agent_client_authz_endpoint,
    "wd_agent_client_token_endpoint": agent_client_token_endpoint,
}

output_path = tmp_path / "terraform.tfvars"
output_path.parent.mkdir(parents=True, exist_ok=True)

lines = [f'{tf_var} = "{value}"' for tf_var, value in values.items()]
output_path.write_text("\n".join(lines) + "\n")
print(f"> Written to {output_path}")
