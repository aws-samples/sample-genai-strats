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

def retrieve_agent_card():
    print("-" * 20)
    print("Retrieving Agent Card (via a2a)")
    AGENT_CARD_URL = os.getenv("AGENT_CARD_URL")
    ACCESS_TOKEN_PATH = Path("./../tmp/integration_client_access_token.txt")
    access_token = ACCESS_TOKEN_PATH.read_text()
    AGENT_CARD_PATH = Path("./../tmp/agent_card.json")

    if not ACCESS_TOKEN_PATH.exists():
        print("ERROR: Integration client access token not found.")
        exit(1)

    print(f"| AGENT_CARD_URL={AGENT_CARD_URL}")
    print(f"| access_token={access_token[:10]}...REDACTED...")

    # Derive base_url and relative card path from the full AGENT_CARD_URL
    agent_card_url_parsed = urlparse(AGENT_CARD_URL)
    agent_card_base_url = f"{agent_card_url_parsed.scheme}://{agent_card_url_parsed.netloc}"
    agent_card_path = agent_card_url_parsed.path
 
    # print(f"| agent_card_base_url={agent_card_base_url}")
    # print(f"| agent_card_path={agent_card_path}")

    agent_card = asyncio.run(_get_card(access_token, agent_card_base_url, agent_card_path))

    print("-" * 20)
    print("Agent card retrieved")
    print(f"| name={agent_card.name}")
    print(f"| url={agent_card.url}")

    os.makedirs("./../tmp", exist_ok=True)
    AGENT_CARD_PATH.write_text(json.dumps(agent_card.model_dump(), indent=4))
    print(f"| Agent card saved to {AGENT_CARD_PATH}")

async def _get_card(access_token, card_base_url, card_path):
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=30.0,
    ) as httpx_client:
        resolver = A2ACardResolver(httpx_client=httpx_client, base_url=card_base_url)
        agent_card = await resolver.get_agent_card(relative_card_path=card_path)
        return agent_card

