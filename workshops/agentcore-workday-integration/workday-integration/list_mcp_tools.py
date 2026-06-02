import os
import json
import httpx
import dotenv
from pathlib import Path

dotenv.load_dotenv("./../workday.configuration")

MCP_ENDPOINT = os.getenv("AGENT_MCP_ENDPOINT")
ACCESS_TOKEN_PATH = Path("./../tmp/mcp_agent_access_token.txt")

print(f"> MCP_ENDPOINT={MCP_ENDPOINT}")

if not ACCESS_TOKEN_PATH.exists():
    print(f"ERROR: Access token not found at {ACCESS_TOKEN_PATH}")
    print("Run 'make get-mcp-agent-access-token' first.")
    exit(1)

access_token = ACCESS_TOKEN_PATH.read_text().strip()
print(f"| access_token={access_token[:10]}...REDACTED...")

payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
}

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
}

print("> Calling MCP tools/list...")
print("-" * 40)

response = httpx.post(MCP_ENDPOINT, json=payload, headers=headers, timeout=30)
response.raise_for_status()

content_type = response.headers.get("content-type", "")

if "text/event-stream" in content_type:
    # SSE response — extract the first data line with a result
    result = None
    for line in response.text.splitlines():
        if line.startswith("data:"):
            data = json.loads(line[len("data:"):].strip())
            if "result" in data:
                result = data["result"]
                break
else:
    data = response.json()
    result = data.get("result")

if result is None:
    print(f"Unexpected response: {response.text}")
    exit(1)

tools = result.get("tools", [])
print(f"Found {len(tools)} tools:\n")

for tool in tools:
    name = tool.get("name", "")
    description = tool.get("description", "")
    print(f"  [{name}]")
    if description:
        print(f"    {description}")
    print()
