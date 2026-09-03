#!/usr/bin/env python3
"""Smoke-test the MCP server deployed on AgentCore Runtime.

Reads the runtime endpoint and a Cognito access token from ./tmp, then sends
four MCP JSON-RPC requests over the AgentCore invocation URL:
  1. prompts/list
  2. resources/read -> greeting://world
  3. tools/list
  4. tools/call     -> add(2, 3)

The server is deployed in stateless mode (stateless_http=True), so no MCP
`initialize` handshake is required; AgentCore injects the Mcp-Session-Id header.

Prereqs: run `make get-cognito-token` first so tmp/cognito_access_token.txt exists.
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

from utils import read_value

# AgentCore's invocation URL is the stored runtime URL with a qualifier. The
# stored value ends in "/invocations/"; strip the trailing slash before adding
# the query string.
RUNTIME_URL = read_value("runtime_url.txt").rstrip("/") + "?qualifier=DEFAULT"
ACCESS_TOKEN = read_value("cognito_access_token.txt")

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json",
    # MCP requires this Accept value; AgentCore may reply as JSON or as SSE.
    "Accept": "application/json, text/event-stream",
}


def parse_response(raw: str) -> dict:
    """Parse a JSON-RPC response that may be plain JSON or SSE-framed."""
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # SSE framing: look for the "data:" line and parse its payload.
        for line in raw.splitlines():
            line = line.strip()
            if line.startswith("data:"):
                return json.loads(line[len("data:"):].strip())
        raise


def mcp_request(method: str, params: dict | None, req_id: int) -> dict:
    """Send a single MCP JSON-RPC request and return the parsed response."""
    body: dict = {"jsonrpc": "2.0", "id": req_id, "method": method}
    if params is not None:
        body["params"] = params

    req = urllib.request.Request(
        RUNTIME_URL,
        data=json.dumps(body).encode(),
        headers=HEADERS,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode()
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        sys.exit(f"error: '{method}' failed ({e.code}): {detail}")

    return parse_response(raw)


def show(label: str, result: dict) -> None:
    print(f"\n=== {label} ===")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    print(f"Target: {RUNTIME_URL}")

    show("list prompts", mcp_request("prompts/list", None, 1))
    show("read resource greeting://world", mcp_request("resources/read", {"uri": "greeting://world"}, 2))
    show("list tools", mcp_request("tools/list", None, 3))
    show("call tool add(2, 3)", mcp_request("tools/call", {"name": "add", "arguments": {"a": 2, "b": 3}}, 4))
