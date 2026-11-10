from strands.tools import tool
from a2a.client import ClientFactory, ClientConfig, A2ACardResolver, create_text_message_object
from a2a.types import AgentCard
from pathlib import Path
import json
import httpx
import identity_helper
import os

_access_token = None
_agent_card = None
_context_ids: dict[str, str] = {}

A2A_AGENT_CARD_BASE_URL = os.environ.get("A2A_AGENT_CARD_BASE_URL")
print(f"> A2A_AGENT_CARD_BASE_URL={A2A_AGENT_CARD_BASE_URL}")

# Cache the token and the card, but NOT the httpx.AsyncClient: Strands runs each tool
# call on its own event loop, and a client created on one loop fails on the next
# ("bound to a different event loop" / "Event loop is closed").
async def _get_access_token(user_id):
    global _access_token
    if not _access_token:
        _access_token = await identity_helper.get_access_token(None, None, user_id)
        print(f"| access_token={_access_token[:10]}...REDACTED...")
    return _access_token

def _new_httpx_client(access_token):
    return httpx.AsyncClient(
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=httpx.Timeout(120, connect=5.0),
    )

async def _get_agent_card(user_id):
    global _agent_card
    print("> a2a::_get_agent_card")
    async with _new_httpx_client(await _get_access_token(user_id)) as httpx_client:
        agent_resolver = A2ACardResolver(
            httpx_client=httpx_client, base_url=A2A_AGENT_CARD_BASE_URL
        )
        print("| retrieving agent card")
        _agent_card = await agent_resolver.get_agent_card()
    print("| agent card retrieved successfully")


async def build_tools(user_id: str):
    print("> a2a::build_tools")

    if not _agent_card:
        await _get_agent_card(user_id)

    @tool
    async def send_message_to_workday_agent(prompt: str):
        """
        This tool servers to address all queries about HR topics
        """
        print(f"> send_message_to_workday_agent user_id={user_id} prompt={prompt} ")
        
        async with _new_httpx_client(await _get_access_token(user_id)) as httpx_client:
            a2a_config = ClientConfig(httpx_client=httpx_client, streaming=False)
            a2a_factory = ClientFactory(a2a_config)
            a2a_client = a2a_factory.create(_agent_card)

            a2a_message = create_text_message_object(content=prompt)
            if user_id in _context_ids:
                a2a_message.context_id = _context_ids[user_id]
                print(f"| injected context_id={a2a_message.context_id}")

            print(f"> Sending the A2A message...")
            try:
                a2a_resp = await _collect_response(a2a_client, a2a_message, user_id)
                print(f"| send_message success")
            except Exception as e:
                print(f"| send_message error: {type(e).__name__}: {e}")
                raise

        return a2a_resp

    return [send_message_to_workday_agent]

async def _collect_response(client, message, user_id: str) -> str:
    parts = []
    async for event in client.send_message(message):
        task, _ = event

        if task.context_id:
            _context_ids[user_id] = task.context_id
            print(f"| stored context_id={task.context_id}")

        for artifact in task.artifacts or []:
            for part in artifact.parts or []:
                text = part.root.text if hasattr(part.root, "text") else str(part.root)
                print(f"| resp.part.text={text}")
                parts.append(text)
    return "\n".join(parts)

