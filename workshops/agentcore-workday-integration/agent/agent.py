from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent
from strands.models import BedrockModel
from system_prompt import SYSTEM_PROMPT
from a2a_tools import a2a_tools
import identity_helper

app = BedrockAgentCoreApp()
model = BedrockModel(model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0", temperature=0.1)

async def process_prompt(payload):
    print(f"> process_prompt")

    agent = Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[a2a_tools],
    )

    prompt = payload.get("prompt")
    print(f"| prompt={prompt}")

    response = agent(prompt)

    # print("> got response")
    # print(response)

    text = response.message["content"][0]["text"]
    return {"status": "OK", "response": text}

@app.entrypoint
async def app_entrypoint(payload, context):

    cmd = payload.get("cmd")

    if cmd == "health":
        return {"status":"ok"}
    
    if cmd == "initialize":
        return await identity_helper.initialize(payload)       

    if cmd == "completeAuth":
        session_id = payload.get("session_id")
        return await identity_helper.complete_auth(session_id)
    
    if cmd == "prompt": 
        return await process_prompt(payload)
    
    return {
        "error": "unknown command"
    }
    
if __name__ == "__main__":
    print("> main")
    app.run(host="0.0.0.0", port="8080")
