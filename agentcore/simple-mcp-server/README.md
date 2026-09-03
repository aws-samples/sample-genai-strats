# Simple MCP Server on Amazon Bedrock AgentCore Runtime

A minimal [Model Context Protocol](https://modelcontextprotocol.io) (MCP) server,
deployed to **Amazon Bedrock AgentCore Runtime** and secured with **Amazon Cognito**
(OAuth 2.0 `client_credentials`). Infrastructure is managed with Terraform.

The server exposes one of each MCP primitive:

| Primitive | Name | Description |
|-----------|------|-------------|
| Tool | `add(a, b)` | Adds two integers |
| Prompt | `review_code(code, language="python")` | Returns a code-review prompt |
| Resource | `greeting://{name}` | Returns `Hello, {name}!` |

It runs as a **stateless** streamable-HTTP server (`stateless_http=True`), which is the
mode AgentCore Runtime expects - the platform injects the `Mcp-Session-Id` header, so
clients are not required to perform an MCP `initialize` handshake.

## Architecture

```
MCP client ──(Bearer token)──▶ AgentCore Runtime ──▶ container: server.py (0.0.0.0:8000/mcp)
                 ▲                    │
                 │                    └─ validates JWT via Cognito discovery URL (inbound auth)
          Cognito (OAuth2                pulls code zip from S3 at deploy time
        client_credentials)
```

- AgentCore Runtime only proxies to the container's `/mcp` path; the invocation URL is
  `https://bedrock-agentcore.<region>.amazonaws.com/runtimes/<encoded-arn>/invocations?qualifier=DEFAULT`.
- Inbound auth is a **custom JWT authorizer** pointed at the Cognito discovery URL, scoped
  to the app client.
- The server code is packaged as a zip and uploaded to S3; the runtime loads it from there.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Python 3.13
- [Terraform](https://developer.hashicorp.com/terraform) ≥ 1.x
- AWS credentials configured (`AWS_PROFILE` / `AWS_REGION`) with permission to create
  Cognito, S3, IAM, and Bedrock AgentCore resources

## Project layout

```
simple-mcp-server/
├── src/                    # The MCP server
│   ├── server.py           # Tool, prompt, resource + stateless HTTP entrypoint
│   └── pyproject.toml      # Runtime dependency: mcp[cli]
├── scripts/                # Helper scripts (stdlib-only, run via uv)
│   ├── get-cognito-token.py  # Fetch an OAuth token, save to tmp/
│   ├── test-remote-mcp.py    # Smoke-test the deployed runtime
│   └── utils.py              # Shared helpers (reads values from tmp/)
├── terraform/              # Infrastructure
│   ├── providers.tf        # AWS provider + random project prefix
│   ├── cognito.tf          # User pool, resource server, app client
│   ├── s3.tf               # Code bucket + content-addressed zip object
│   └── agentcore_runtime.tf# IAM role, least-privilege policy, agent runtime
├── tmp/                    # Generated at deploy time (gitignored — holds secrets for demo purposes)
└── Makefile
```

> **`tmp/` contains secrets** (Cognito client secret, access tokens) and generated
> values (runtime ARN/URL, the code zip). It is gitignored — never commit it.

## Quick start

```bash
# 1. Package the server code + dependencies into a zip under tmp/
make build-package

# 2. Deploy all infrastructure (Cognito, S3, IAM, AgentCore Runtime)
make deploy

# 3. Fetch an OAuth access token (saved to tmp/cognito_access_token.txt)
make get-cognito-token

# 4. Smoke-test the deployed server (lists prompts, reads a resource, lists + calls tools)
make test-remote-mcp
```

> Run `make build-package` **before** `make deploy` — Terraform hashes the zip to
> content-address its S3 key, so the file must exist first.

## Makefile targets

| Target | What it does |
|--------|--------------|
| `build-package` | Installs deps for `aarch64-manylinux2014` / py3.13 and zips them with `server.py` into `tmp/mcp_server_package/mcp_server.zip` |
| `deploy` | `terraform init && terraform apply --auto-approve` |
| `destroy` | `terraform destroy --auto-approve` and removes `tmp/` |
| `test-local` | `uv sync && uv run server.py` — runs the server locally on `0.0.0.0:8000` |
| `get-cognito-token` | Runs `scripts/get-cognito-token.py` to fetch and save an access token |
| `test-remote-mcp` | Runs `scripts/test-remote-mcp.py` to smoke-test the deployed runtime |

## Authentication

The Cognito app client uses the OAuth 2.0 **client credentials** grant (machine-to-machine),
with access tokens configured for the maximum lifetime (24 hours). To get a token manually:

```bash
make get-cognito-token          # prints the token JSON and writes tmp/cognito_access_token.txt
```

Under the hood it reads `client_id`, `client_secret`, `scopes`, and `token_endpoint` from
`tmp/` and POSTs to the Cognito token endpoint with HTTP Basic auth.

## Invoking the runtime

Clients call the AgentCore invocation URL with a bearer token and an MCP JSON-RPC payload:

```bash
TOKEN=$(cat tmp/cognito_access_token.txt)
URL="$(cat tmp/runtime_url.txt | sed 's:/*$::')?qualifier=DEFAULT"

curl -s -X POST "$URL" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"add","arguments":{"a":2,"b":3}}}'
```

`scripts/test-remote-mcp.py` wraps exactly this flow for the four core operations.

## Local development

```bash
make test-local
# Server on http://0.0.0.0:8000/mcp — connect with any MCP client (e.g. MCP Inspector)
```

## Cleanup

```bash
make destroy    # tears down all AWS resources and deletes tmp/
```
