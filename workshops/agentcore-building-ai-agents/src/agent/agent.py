import os

# When running on AgentCore, initialize OpenTelemetry before anything else is imported,
# so that the HTTP server, Strands, and AWS SDK calls are all instrumented
if os.environ.get("AGENTCORE_RUNTIME_URL"):
    import opentelemetry.instrumentation.auto_instrumentation
    print("Initializing OTEL...")
    opentelemetry.instrumentation.auto_instrumentation.initialize()

from opentelemetry import baggage, context as otel_context
from bedrock_agentcore.runtime import BedrockAgentCoreApp, RequestContext
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

l = get_logger(__name__)

model = BedrockModel(model_id="us.anthropic.claude-haiku-5-5")

tools = [
    get_return_policy, 
    get_product_info, 
    get_technical_support,
    mcp_tools_list
]

app = BedrockAgentCoreApp()
@app.entrypoint
async def invoke(payload, context: RequestContext):
    # One session ID per conversation, provided by the caller (runtimeSessionId on AgentCore)
    session_id = context.session_id

    # Tag all spans of this request with the session ID, so AgentCore Observability
    # and Evaluations can group the request's traces into a session
    otel_context.attach(baggage.set_baggage("session.id", session_id))

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
    # Locally there's no AgentCore Runtime to provide a session ID, so use one per run
    context = RequestContext(session_id=str(uuid.uuid4()))
    while True:
        print("\n" + "-" * 20)
        prompt = input("User prompt (type 'exit' to quit): ").strip()
        if prompt.lower() == "exit":
            break
        if not prompt:
            continue
        async for text_chunk in invoke({"prompt": prompt}, context):
            print(text_chunk , end="", flush=True)
        print()

if __name__ == "__main__":
    if os.environ.get("AGENTCORE_RUNTIME_URL"):
        print("Running on AgentCore, starting server...")
        app.run()
    else:
        print("Running locally...")
        asyncio.run(run_locally_async())

