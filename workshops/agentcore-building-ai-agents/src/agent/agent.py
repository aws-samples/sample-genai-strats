import opentelemetry.instrumentation.auto_instrumentation

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent
from strands.models import BedrockModel
from tools.return_policy import get_return_policy
from tools.product_info import get_product_info
from tools.tech_support import get_technical_support
from system_prompt import SYSTEM_PROMPT
from memory_config import get_session_manager
import asyncio
import uuid
from logger import get_logger
from mcp_client import mcp_tools_list
import os

l = get_logger(__name__)

model = BedrockModel(model_id="us.anthropic.claude-sonnet-4-6")

tools = [
    get_return_policy, 
    get_product_info, 
    get_technical_support,
    mcp_tools_list
]

session_id = str(uuid.uuid4())

app = BedrockAgentCoreApp()
@app.entrypoint
async def invoke(payload, _context=None):
    user_prompt = payload.get("prompt", "Hey there!")

    l.info(f"ℹ️ user_prompt={user_prompt}")

    session_manager=get_session_manager(session_id)

    agent = Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=tools,
        session_manager=session_manager,
        callback_handler=None,
    )

    async for event in agent.stream_async(user_prompt):
        tool_use = event.get("event", {}).get("contentBlockStart", {}).get("start", {}).get("toolUse")
        if tool_use:
            print(f"\n[Tool called: {tool_use['name']}]\n")

        text_chunk = event.get("data")
        if text_chunk:
            yield text_chunk

async def run_locally_async():
    print("-" * 20)
    print("Welcome to the AwesomeCorp Customer Support Agent")
    while True:
        print("\n" + "-" * 20)
        prompt = input("User prompt (type 'exit' to quit): ").strip()
        if prompt.lower() == "exit":
            break
        if not prompt:
            continue
        async for text_chunk in invoke({"prompt": prompt}):
            print(text_chunk , end="", flush=True)
        print()

if __name__ == "__main__":
    if os.environ.get("AGENTCORE_RUNTIME_URL"):
        print("Initializing OTEL...")
        opentelemetry.instrumentation.auto_instrumentation.initialize()

        print("Running on AgentCore, starting server...")
        app.run()
    else:
        print("Running locally...")
        asyncio.run(run_locally_async())

