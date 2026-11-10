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
model = BedrockModel(model_id="us.anthropic.claude-sonnet-4-6", max_tokens=2048)

# Streams the response. AgentCore Runtime sends each yielded dict to the caller as one
# Server-Sent Event ("data: {...}"):
#   {"delta": "..."}   a piece of the response text
#   {"tool": "..."}    the agent started calling a tool
#   {"error": "..."}   something failed
#   {"done": true}     the response is complete
async def stream_prompt(payload):
    print(f"> stream_prompt")
    user_id = payload.get("user_id", DEFAULT_TEST_USER_ID)
    prompt = payload.get("prompt")
    print(f"| user_id={user_id}")
    print(f"| payload={payload}")

    try:
        session_manager = FileSessionManager(session_id=user_id)
        tools = await build_tools(user_id)

        agent = Agent(
            model=model,
            system_prompt=SYSTEM_PROMPT,
            session_manager=session_manager,
            tools=tools,
        )

        tool_use_ids = set()
        async for event in agent.stream_async(prompt):
            if "data" in event:
                yield {"delta": event["data"]}
            tool_use = event.get("current_tool_use")
            if tool_use and tool_use.get("toolUseId") not in tool_use_ids:
                tool_use_ids.add(tool_use.get("toolUseId"))
                print(f"| tool={tool_use.get('name')}")
                yield {"tool": tool_use.get("name")}
    except Exception as e:
        print(f"| stream_prompt error: {type(e).__name__}: {e}")
        yield {"error": f"{type(e).__name__}: {e}"}
        return

    yield {"done": True}

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

    # Returns an async generator (not awaited), so AgentCore streams it back as SSE.
    # app_entrypoint itself must not use `yield`, or every command would become a stream.
    if cmd == "prompt":
        return stream_prompt(payload)
    
    return {
        "error": "unknown command"
    }
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8080")
