import os
from mcp.client.streamable_http import streamablehttp_client
from strands.tools.mcp import MCPClient
from logger import get_logger
from identity_helper import get_token

l = get_logger(__name__)

GATEWAY_URL = os.environ.get("GATEWAY_URL")
l.info(f"mcp_client :: GATEWAY_URL={GATEWAY_URL}")
mcp_tools_list = []

if not GATEWAY_URL:
    l.info("⚠️ GATEWAY_URL not set - gateway tools disabled")
elif not (gateway_token := get_token()):
    l.info("⚠️ Could not retrieve gateway token - gateway tools disabled")
else:
    mcp_client = MCPClient(lambda: streamablehttp_client(
        GATEWAY_URL,
        headers={"Authorization": f"Bearer {gateway_token}"}
    ))
    mcp_client.start()
    mcp_tools_list = mcp_client.list_tools_sync()
    l.info(f"✅ Retrieved {len(mcp_tools_list)} tools from gateway")
