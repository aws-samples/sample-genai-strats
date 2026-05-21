from mcp.client.streamable_http import streamablehttp_client
from strands.tools.mcp import MCPClient
import identity_helper
import os

from identity_helper import get_access_token

mcp_tools = {}
mcp_clients = {}

MCP_ENDPOINT = os.environ.get("MCP_ENDPOINT")
print(f"> MCP_ENDPOINT={MCP_ENDPOINT}")

async def build_tools(user_id):
    print(f"> mcp::build_tools user_id={user_id}")

    if user_id in mcp_tools and user_id in mcp_clients:
        print(f"| existing MCP client/tools found for user_id={user_id}")
        return mcp_tools[user_id]
    
    print(f"| MCP client/tools for user_id={user_id} not found, creating...")

    access_token = await identity_helper.get_access_token(None, None, user_id)
    print(f"| access_token={access_token[:10]}...REDACTED...")

    mcp_client = MCPClient(
        lambda: streamablehttp_client(  
            url=MCP_ENDPOINT,
            headers={"Authorization":f"Bearer {access_token}"}
            )
    )
    mcp_client.start() 
    tools = mcp_client.list_tools_sync()
    print(f"| retrieved {len(tools)} tools")
    mcp_clients[user_id] = mcp_client
    mcp_tools[user_id] = tools
    return mcp_tools[user_id]
