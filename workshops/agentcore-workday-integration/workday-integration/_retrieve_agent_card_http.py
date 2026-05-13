import dotenv
import os
import requests
from pathlib import Path
import json

dotenv.load_dotenv()

AGENT_CARD_URL = os.getenv("AGENT_CARD_URL")
ACCESS_TOKEN_PATH = Path("./../tmp/api_client_access_token.txt")
AGENT_CARD_PATH = Path("./../tmp/agent_card.json")

print("-" * 20)
print(f"Retrieving Agent Card")
print(f"| AGENT_CARD_URL={AGENT_CARD_URL}")

if not ACCESS_TOKEN_PATH.exists():
    print("ERROR: API client access token not found. Run start-api-client-authz first.")
    exit(1)

access_token = ACCESS_TOKEN_PATH.read_text()

response = requests.get(
    AGENT_CARD_URL,
    headers={"Authorization": f"Bearer {access_token}"},
)
response.raise_for_status()

agent_card = response.json()
agent_name = agent_card["name"]
agent_url = agent_card["url"]

print("-" * 20)
print("Agent card retrieved")
print(f"| agent_name={agent_name}")
print(f"| agent_url={agent_url}")

os.makedirs("./../tmp", exist_ok=True)
AGENT_CARD_PATH.write_text(json.dumps(agent_card, indent=2))
print(f"| Agent card saved to ./tmp")
