import asyncio
from strands import Agent
from strands.models import BedrockModel
from strands.session.file_session_manager import FileSessionManager
from system_prompt import SYSTEM_PROMPT
from mcp_tools import build_tools

USER_ID = "chat-local"
model = BedrockModel(model_id="us.anthropic.claude-sonnet-4-6")

async def main():
    mcp_server_url = input("MCP Server URL: ").strip()
    bearer_token = input("Bearer Token: ").strip()

    print("Connecting to MCP server...")
    tools = await build_tools(USER_ID, mcp_server_url=mcp_server_url, bearer_token=bearer_token)

    agent = Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        session_manager=FileSessionManager(session_id=USER_ID),
        tools=tools,
    )

    print("Ready. Type your question or 'quit' to exit.\n")
    while True:
        try:
            prompt = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not prompt or prompt.lower() == "quit":
            break
        response = agent(prompt)
        print(f"\nAgent: {response.message['content'][0]['text']}\n")

if __name__ == "__main__":
    asyncio.run(main())
