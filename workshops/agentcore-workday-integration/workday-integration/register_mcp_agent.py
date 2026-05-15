import json
import requests
from pathlib import Path
from handle_api_client_authz import handle_api_client_authz
import random
import string
import os
import dotenv

dotenv.load_dotenv(
    dotenv_path=Path("./../workday.configuration")
)

output_path = Path(__file__).parent.parent / "tmp" / "custom_agent_card.json"

if output_path.exists():
    existing = json.loads(output_path.read_text())
    existing_name = existing.get("name", "unknown")
    print("-" * 20)
    print("Custom agent card already available.")
    print(f"| name={existing_name}")
    print(f"| path={output_path}")
    print("-" * 20)
    print("To create a new one:")
    print(f"  1. Archive your agent in Workday (agent name: {existing_name})")
    print(f"  2. Delete {output_path}")
    print(f"  3. Run 'make register-agent' again")
    exit(0)

AGENT_REGISTRATION_ENDPOINT = "https://us.agent.workday.com/asor/v1/agentDefinition"
PAYLOAD_PATH = Path(__file__).parent / "register_agent_payload.json"
WORKDAY_TENANT_ALIAS=os.getenv("WORKDAY_TENANT_ALIAS")

print("> Getting access token")
access_token = handle_api_client_authz()

payload = json.loads(PAYLOAD_PATH.read_text())
random_suffix = "".join(random.choices(string.ascii_letters + string.digits, k=8))
agent_name = f"aws-custom-agent-{random_suffix}"
payload["name"] = payload["name"].replace("AGENT_NAME_PLACEHOLDER", agent_name)

print("-" * 20)
print(f"Registering agent")
print(f"| agent name={agent_name}")
print(f"| AGENT_REGISTRATION_ENDPOINT={AGENT_REGISTRATION_ENDPOINT}")
print(f"| WORKDAY_TENANT_ALIAS={WORKDAY_TENANT_ALIAS}")

response = requests.post(
    AGENT_REGISTRATION_ENDPOINT,
    json=payload,
    headers={
        "Authorization": f"Bearer {access_token}",
        "wd-agent-tenant-alias": WORKDAY_TENANT_ALIAS,
        "Content-Type": "application/json",
    },
)
response.raise_for_status()
response_json = response.json()

print(f"| status={response.status_code}")
print(f"| name={response_json.get('name')}")
print(f"| url={response_json.get('url')}")

output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(json.dumps(response_json, indent=4))
print(f"| saved to {output_path}")

