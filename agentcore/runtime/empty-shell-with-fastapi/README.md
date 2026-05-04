# AgentCore Runtime - Empty Shell with FastAPI

A minimal [Amazon Bedrock AgentCore Runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agents-tools-runtime.html) that echoes back the received payload. Uses FastAPI + Uvicorn to implement AgentCore's HTTP interface.

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
├── Makefile                # Build, deploy, and test targets
├── README.md
├── src/
│   └── agent/
│       ├── main.py         # AgentCore runtime entrypoint (FastAPI + Uvicorn)
│       ├── pyproject.toml  # Python dependencies
│       ├── uv.lock         # Locked dependency versions
│       └── Dockerfile      # Container image definition
├── terraform/
│   ├── providers.tf        # Provider config, locals, shared random prefix
│   ├── main.tf             # Module wiring
│   ├── agentcore_runtime.tf # IAM role + AgentCore runtime resource
│   └── bootstrap/
│       └── bootstrap.tf    # ECR repo + writes account/region/repo to tmp/
└── tmp/                    # Generated at deploy time (gitignored)
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
- IAM role with ECR pull, Bedrock, and CloudWatch permissions
- AgentCore agent runtime pointing to the ECR image digest
- `tmp/agent_runtime_arn.txt` with the runtime ARN

### 5. Test the runtime

```bash
make test-agent
```

Sends `{"hello": "world"}` to the runtime and prints the response to `tmp/invoke_output.txt`.


#### AWS CLI call:

```bash
PAYLOAD=$(echo '{"hello": "world"}' | base64)

aws bedrock-agentcore invoke-agent-runtime \
    --agent-runtime-arn "arn:aws:bedrock-agentcore:{region}:{account}:runtime/{id}" \
    --payload "eyJoZWxsbyI6ICJ3b3JsZCJ9" \
    --content-type "application/json" \
    --no-cli-pager \
    tmp/invoke_output.txt
```

#### Response:

```json
{
  "msg": "hello from AgentCore Empty Shell",
  "received_headers": {
    "x-aws-proxy-port": "8080",
    "baggage": "Self=1-69f8e330-574e1a6770f09e624fe06cfc,session.id=b9c24f1c-eefc-4d88-9196-7d33f1391518",
    "content-length": "18",
    "content-type": "application/json",
    "x-amzn-bedrock-agentcore-runtime-session-id": "b9c24f1c-eefc-4d88-9196-7d33f1391518",
    "x-amzn-trace-id": "Root=1-69f8e330-44a234f164e98ca400e154ea;Parent=a5b5fd97de349e44;Sampled=1;Self=1-69f8e330-574e1a6770f09e624fe06cfc",
    "x-amzn-requestid": "5381ff56-f286-4abd-8117-54769adf09ea",
    "host": "cell01.us-east-1.prod.arp.kepler-analytics.aws.dev"
  },
  "received_payload": {
    "hello": "world"
  }
}
```

## Teardown

```bash
make destroy
```

Destroys all Terraform-managed resources and deletes the `tmp/` directory.
