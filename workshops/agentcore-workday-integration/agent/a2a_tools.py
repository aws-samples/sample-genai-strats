from strands.tools import tool
from a2a.client import ClientFactory, ClientConfig, create_text_message_object
from a2a.types import AgentCard
from pathlib import Path
import json
import httpx
import identity_helper

AGENT_CARD = Path("./agent_card.json").read_text()
agent_card_json = json.loads(AGENT_CARD)

agent_card = AgentCard.model_validate(agent_card_json)
# print(f"agent_card={agent_card}"")
print(f"agent_card.name={agent_card.name}")
print(f"agent_card.url={agent_card.url}")

_context_ids: dict[str, str] = {}

def build_tools(user_id: str):

    @tool
    async def send_message_to_workday(prompt: str):
        """
        This tool servers to address all queries about HR topics
        """
        print(f"> send_message_to_workday user_id={user_id} prompt={prompt} ")
        
        access_token = await identity_helper.get_access_token(None, None, user_id)
        print(f"| access_token={access_token[:10]}...REDACTED...")

        async with httpx.AsyncClient(
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=60.0,
        ) as httpx_client:
            config = ClientConfig(httpx_client=httpx_client, streaming=False)
            client = ClientFactory(config).create(agent_card)

            message = create_text_message_object(content=prompt)

            if user_id in _context_ids:
                message.context_id = _context_ids[user_id]
                print(f"| injected context_id={message.context_id}")

            print("-" * 20)
            print("Waiting for A2A response...")

            try:
                resp = await _collect_response(client, message, user_id)
                print(f"| send_message success")
            except Exception as e:
                print(f"| send_message error: {type(e).__name__}: {e}")
                raise

        return resp

    return [send_message_to_workday]

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

