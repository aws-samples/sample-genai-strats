# Simple AI Agent using Strands Agents SDK

A simple sample AI agent deployed on [AWS Bedrock AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agents-tools-runtime.html) using the [Strands Agents](https://github.com/strands-agents/strands-agents) framework and Claude Haiku 4.5.

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- AWS CLI configured with appropriate credentials
- Terraform
- Docker
- jq

## Project Structure

```
.
├── Makefile                              # Build, deploy, and test targets
├── README.md
├── src/
│   └── agent/
│       ├── main.py                      # AgentCore runtime entrypoint
│       ├── pyproject.toml               # Python dependencies
│       ├── uv.lock                      # Locked dependency versions
│       └── Dockerfile                   # Container image definition
├── terraform/
│   ├── main.tf                          # Module wiring
│   ├── providers.tf                     # Provider config and shared random prefix
│   ├── agentcore_runtime.tf             # IAM role + AgentCore runtime resource
│   └── bootstrap/
│       └── bootstrap.tf                 # ECR repo + writes account/region/repo to tmp/
└── tmp/                                 # Generated at deploy time (gitignored)
    ├── aws_account_id.txt
    ├── aws_region.txt
    ├── ecr_repo_url.txt
    └── agent_runtime_arn.txt
```

## Setup

### 1. Bootstrap

Creates the ECR repository and writes account/region/repo values to `tmp/`:

```bash
make bootstrap
```

### 2. Log in to ECR

```bash
make login-to-ecr
```

### 3. Build and push the container image

```bash
make build-and-push-agent
```

### 4. Deploy the infrastructure

```bash
make deploy-infra
```

This creates:
- IAM role with ECR pull, Bedrock, CloudWatch, and X-Ray permissions
- AgentCore agent runtime pointing to the ECR image digest
- `tmp/agent_runtime_arn.txt` with the runtime ARN

### 5. Test the runtime

```bash
make test-agent
```

Sends `{"prompt": "pizza recipe in one sentence"}` to the runtime and prints the response to `tmp/invoke_output.txt`.

#### AWS CLI call:

```bash
PAYLOAD=$(echo '{"prompt": "pizza recipe in one sentence"}' | base64)

aws bedrock-agentcore invoke-agent-runtime \
    --agent-runtime-arn "arn:aws:bedrock-agentcore:{region}:{account}:runtime/{id}" \
    --payload "$PAYLOAD" \
    --content-type "application/json" \
    --no-cli-pager \
    tmp/invoke_output.txt
```

#### Response:

```json
{
  "agent_response_text": "Mix 2 cups flour, 1 tsp yeast, 1 tsp salt, 1 tbsp olive oil, and 3/4 cup warm water; knead, rest 1 hour, top with sauce and cheese, bake at 475°F for 12 minutes.",
  "request_headers": {
    "x-amzn-bedrock-agentcore-runtime-session-id": "b9c24f1c-eefc-4d88-9196-7d33f1391518",
    "content-type": "application/json"
    ...REDACTED...
  },
  "request_payload": {
    "prompt": "pizza recipe in one sentence"
  }
}
```

## Teardown

```bash
make destroy
```

Destroys all Terraform-managed resources and deletes the `tmp/` directory.
