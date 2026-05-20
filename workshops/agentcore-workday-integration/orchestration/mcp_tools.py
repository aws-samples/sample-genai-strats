from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client

MCP_SERVER_URL = "https://api.us.wcp.workday.com/orchestrate/v1/apps/agentactionsfororchestrate_ynzjmg/mcp"

async def build_tools(user_id: str, mcp_server_url: str = MCP_SERVER_URL, bearer_token: str = None):
    print(f"> mcp build_tools: connecting to {mcp_server_url}")

    mcp_client = MCPClient(lambda: streamablehttp_client(
        mcp_server_url,
        headers={"Authorization": f"Bearer {bearer_token}"},
    ))

    mcp_client.start()
    tools = mcp_client.list_tools_sync()
    print(f"| discovered {len(tools)} MCP tools: {[t.tool_name for t in tools]}")
    return tools
