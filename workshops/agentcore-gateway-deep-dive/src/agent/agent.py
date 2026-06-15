import asyncio
import os
from strands import Agent
from strands.models import BedrockModel
from system_prompt import SYSTEM_PROMPT
from mcp_client import mcp_tools_list
from logger import get_logger

l = get_logger(__name__)

model = BedrockModel(model_id="us.anthropic.claude-sonnet-4-6")

agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[mcp_tools_list],
)

async def run_locally_async():
    print("-" * 40)
    print("Welcome to AgentCore AI Pizzeria!")
    print("-" * 40)
    print("Available MCP tools:")
    for tool in mcp_tools_list:
        print(f"| - {tool.tool_name}")
    print("-" * 40)
    while True:
        print()
        prompt = input("You (type 'exit' to quit): ").strip()
        if prompt.lower() in ("exit", "quit"):
            break
        if not prompt:
            continue
        async for event in agent.stream_async(prompt):
            tool_use = (
                event.get("event", {})
                .get("contentBlockStart", {})
                .get("start", {})
                .get("toolUse")
            )
            if tool_use:
                print(f"\n[Tool called: {tool_use['name']}]\n")

            # text_chunk = event.get("data")
            # if text_chunk:
            #     print(text_chunk, end="", flush=True)
        print()


if __name__ == "__main__":
    asyncio.run(run_locally_async())
