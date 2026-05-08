import asyncio
import dotenv
import json
import os
from pathlib import Path

import httpx
from a2a.client import ClientFactory, ClientConfig, create_text_message_object
from a2a.types import AgentCard

dotenv.load_dotenv()

ACCESS_TOKEN_PATH = Path("./tmp/agent_client_access_token.txt")
AGENT_CARD_PATH = Path("./tmp/agent_card.json")
MESSAGE = "What's my name?"

print("-" * 20)
print(f"Sending message to agent: {MESSAGE}")

if not ACCESS_TOKEN_PATH.exists():
    print("ERROR: Integration client access token not found. Run start-integration-client-authz first.")
    exit(1)

if not AGENT_CARD_PATH.exists():
    print("ERROR: Agent card not found. Run retrieve-agent-card first.")
    exit(1)

access_token = ACCESS_TOKEN_PATH.read_text()
agent_card = AgentCard.model_validate(json.loads(AGENT_CARD_PATH.read_text()))

print(f"| agent_name={agent_card.name}")
print(f"| agent_url={agent_card.url}")

async def main():
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=60.0,
    ) as httpx_client:
        config = ClientConfig(httpx_client=httpx_client, streaming=False)
        client = ClientFactory(config).create(agent_card)

        message = create_text_message_object(content=MESSAGE)

        print("-" * 20)
        print("Waiting for response...")
        async for event in client.send_message(message):
            task, _ = event
            for artifact in task.artifacts or []:
                for part in artifact.parts or []:
                    text = part.root.text if hasattr(part.root, "text") else str(part.root)
                    print(f"| response={text}")


asyncio.run(main())
