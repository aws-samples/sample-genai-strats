import asyncio
import dotenv
import json
import os
from pathlib import Path
from urllib.parse import urlparse

import httpx
from a2a.client import A2ACardResolver
dotenv.load_dotenv(
    dotenv_path=Path("./../workday.configuration")
)

def get_agent_card():
    print("-" * 20)
    print("Retrieving Agent Card (via a2a)")
    WORKDAY_TENANT_ALIAS = os.getenv("WORKDAY_TENANT_ALIAS")
    A2A_AGENT_CARD_URL = os.getenv("A2A_AGENT_CARD_URL").replace("TENANT_ALIAS", WORKDAY_TENANT_ALIAS)
    A2A_AGENT_ACCESS_TOKEN_PATH = Path("./../tmp/a2a_agent_access_token.txt")
    A2A_AGENT_ACCESS_TOKEN = A2A_AGENT_ACCESS_TOKEN_PATH.read_text()
    A2A_AGENT_CARD_PATH = Path("./../tmp/a2a_agent_card.json")

    if not WORKDAY_TENANT_ALIAS:
        print("ERROR: WORKDAY_TENANT_ALIAS not found.")
        exit(1)


    if not A2A_AGENT_ACCESS_TOKEN:
        print("ERROR: WORKDAY_ACCESS_TOKEN not found.")
        exit(1)

    print(f"| WORKDAY_TENANT_ALIAS={WORKDAY_TENANT_ALIAS}")
    print(f"| A2A_AGENT_ACCESS_TOKEN={A2A_AGENT_ACCESS_TOKEN[:10]}...REDACTED...")
    print(f"| A2A_AGENT_CARD_URL={A2A_AGENT_CARD_URL}")
    
    # Derive base_url and relative card path from the full AGENT_CARD_URL
    agent_card_url_parsed = urlparse(A2A_AGENT_CARD_URL)
    agent_card_base_url = f"{agent_card_url_parsed.scheme}://{agent_card_url_parsed.netloc}"
    agent_card_path = agent_card_url_parsed.path
 
    print(f"| agent_card_base_url={agent_card_base_url}")
    print(f"| agent_card_path={agent_card_path}")

    agent_card = asyncio.run(_get_card(A2A_AGENT_ACCESS_TOKEN, agent_card_base_url, agent_card_path))

    print("-" * 20)
    print("A2A agent card retrieved")
    print(f"| name={agent_card.name}")
    print(f"| url={agent_card.url}")

    os.makedirs("./../tmp", exist_ok=True)
    A2A_AGENT_CARD_PATH.write_text(json.dumps(agent_card.model_dump(), indent=4))
    print(f"| Agent card saved to {A2A_AGENT_CARD_PATH}")

async def _get_card(access_token, card_base_url, card_path):
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=30.0,
    ) as httpx_client:
        resolver = A2ACardResolver(httpx_client=httpx_client, base_url=card_base_url)
        agent_card = await resolver.get_agent_card(relative_card_path=card_path)
        return agent_card

if __name__=="__main__":
    get_agent_card()