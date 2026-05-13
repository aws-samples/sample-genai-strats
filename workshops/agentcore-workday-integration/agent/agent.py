from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands.session.file_session_manager import FileSessionManager
from strands import Agent
from strands.models import BedrockModel
from system_prompt import SYSTEM_PROMPT
from a2a_tools import build_tools
import identity_helper
from identity_helper import DEFAULT_TEST_USER_ID

app = BedrockAgentCoreApp()
model = BedrockModel(model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0", temperature=0.1)

async def process_prompt(payload):
    print(f"> process_prompt")
    user_id = payload.get("user_id", DEFAULT_TEST_USER_ID)
    prompt = payload.get("prompt")
    print(f"| user_id={user_id}")
    print(f"| payload={payload}")

    session_manager = FileSessionManager(session_id=user_id)

    agent = Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        session_manager=session_manager,
        tools=build_tools(user_id),
    )

    response = agent(prompt)

    # print("> got response")
    # print(response)

    text = response.message["content"][0]["text"]
    return {"status": "ok", "response": text}

@app.entrypoint
async def app_entrypoint(payload, context):
    cmd = payload.get("cmd")

    if cmd == "health":
        print("> health")
        return {"status":"ok"}

    if cmd == "initialize":
        return await identity_helper.initialize(payload)

    if cmd == "completeAuth":
        return await identity_helper.complete_auth(payload)

    if cmd == "prompt":
        return await process_prompt(payload)
    
    return {
        "error": "unknown command"
    }
    
if __name__ == "__main__":
    print("> main")
    app.run(host="0.0.0.0", port="8080")
