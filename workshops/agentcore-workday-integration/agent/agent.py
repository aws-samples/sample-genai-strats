from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands.session.file_session_manager import FileSessionManager
from strands import Agent
from strands.models import BedrockModel
import identity_helper
from identity_helper import DEFAULT_TEST_USER_ID
import os

print("> Starting agent...")

AGENT_MODE = os.environ.get("AGENT_MODE")
print(f"| Starting with AGENT_MODE={AGENT_MODE}")

if AGENT_MODE=="a2a":
    from system_prompt_a2a import SYSTEM_PROMPT
    from a2a_tools import build_tools
elif AGENT_MODE=="mcp":
    from system_prompt_mcp import SYSTEM_PROMPT
    from mcp_tools import build_tools
else:
    print(f"| Unrecognized AGENT_MODE={AGENT_MODE}. Stopping.")
    exit(1)

app = BedrockAgentCoreApp()
model = BedrockModel(model_id="us.anthropic.claude-sonnet-4-6")

async def process_prompt(payload):
    print(f"> process_prompt")
    user_id = payload.get("user_id", DEFAULT_TEST_USER_ID)
    prompt = payload.get("prompt")
    print(f"| user_id={user_id}")
    print(f"| payload={payload}")

    session_manager = FileSessionManager(session_id=user_id)
    tools = await build_tools(user_id)

    agent = Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        session_manager=session_manager,
        tools=tools,
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
    app.run(host="0.0.0.0", port="8080")
