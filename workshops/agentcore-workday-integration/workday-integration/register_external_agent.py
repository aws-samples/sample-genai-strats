import json
import requests
from pathlib import Path
# from handle_api_client_authz import handle_api_client_authz
import random
import string
import os
import dotenv

dotenv.load_dotenv(
    dotenv_path=Path("./../workday.configuration")
)

input_path = Path(__file__).parent.parent / "workday-integration" / f"register_external_agent_payload.json"
output_path = Path(__file__).parent.parent / "tmp" / f"external_agent_registration_response.json"

# if output_path.exists():
#     existing = json.loads(output_path.read_text())
#     existing_name = existing.get("name", "unknown")
#     print("-" * 20)
#     print("Agent card already available.")
#     print(f"| name={existing_name}")
#     print(f"| path={output_path}")
#     print("-" * 20)
#     print("To create a new one:")
#     print(f"  1. Archive your agent in Workday (agent name: {existing_name})")
#     print(f"  2. Delete {output_path}")
#     print(f"  3. Run 'make register-agent' again")
#     exit(0)

AGENT_REGISTRATION_ENDPOINT = "https://eu.agent.workday.com/asor/v1/agentDefinition"
WORKDAY_ACCESS_TOKEN = os.getenv("WORKDAY_ACCESS_TOKEN")
WORKDAY_TENANT_ALIAS=os.getenv("WORKDAY_TENANT_ALIAS")

# print("> Getting access token")
# access_token = handle_api_client_authz()

payload = json.loads(input_path.read_text())
random_suffix = "".join(random.choices(string.ascii_letters + string.digits, k=8))
# agent_name = f"{AGENT_TYPE}-agent-{random_suffix}"
# payload["name"] = payload["name"].replace("AGENT_NAME_PLACEHOLDER", agent_name)

print("-" * 20)
print(f"Registering agent")
print(f"| agent name={payload["name"]}")
print(f"| AGENT_REGISTRATION_ENDPOINT={AGENT_REGISTRATION_ENDPOINT}")
print(f"| WORKDAY_TENANT_ALIAS={WORKDAY_TENANT_ALIAS}")

response = requests.post(
    AGENT_REGISTRATION_ENDPOINT,
    json=payload,
    headers={
        "Authorization": f"Bearer {WORKDAY_ACCESS_TOKEN}",
        "wd-agent-tenant-alias": WORKDAY_TENANT_ALIAS,
        "Content-Type": "application/json",
    },
)
print(f"| status={response.status_code}")
print(f"| body={response.text}")
response.raise_for_status()
response_json = response.json()

print(f"| name={response_json.get('name')}")
print(f"| url={response_json.get('url')}")

output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(json.dumps(response_json, indent=4))

print("| Agent registration success")
