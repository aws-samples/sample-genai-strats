# Lambda Web Function → AgentCore Runtime


A ChatGPT-style chat app hosted on an [AWS Lambda Web Function](https://docs.aws.amazon.com/lambda/latest/dg/web-functions.html), backed by a [Strands](https://strandsagents.com) agent running on **Amazon Bedrock AgentCore Runtime**. 

![](./chat-interface.png)

The agent's response is streamed token by token from the model, through AgentCore Runtime and the Web Function, to the browser.

## Architecture

![](./arch.png)

## Prerequisites

- AWS CLI v2, configured with credentials for the target account (used to log in to ECR when pushing the agent image)
- Terraform
- Docker (builds the agent's `linux/arm64` image)
- Node.js 24 and npm
- Access to Claude Sonnet 5.5 in Amazon Bedrock. The agent uses the `us.anthropic.claude-sonnet-5-5` cross-Region inference profile, so deploy to a US Region.
- For local development only: Python 3.13, [uv](https://docs.astral.sh/uv/), and [nodemon](https://nodemon.io)

## Deploy

```bash
make deploy
```

This provisions:

- An ECR repository with the agent image, built locally and pushed
- An AgentCore runtime that runs the agent, with an IAM role that can invoke the configured model through its inference profile
- A versioned S3 bucket for the webapp code, with a bucket policy that lets the Lambda service read it
- An execution role for the Web Function that can write its logs and invoke only this agent runtime
- The Web Function, a revision built from the uploaded code, and one endpoint (`default`) that routes all traffic to that revision. Each code change creates a new revision, and the endpoint switches to it.

When it finishes, Terraform prints the URL of the chat UI:

```
webapp_url = "https://<endpoint-domain>.lambda-web.<region>.on.aws/"
```

## Run locally (for development)

Run the agent on port 8080:

```bash
make run-agent-local
```

Run the webapp on port 3000, at <http://localhost:3000>. It reads the runtime ARN from `tmp/agent_runtime_arn.txt`, so it talks to the **deployed** agent runtime, not the local agent:

```bash
make run-webapp-local
```

## Security considerations

This is a demo, not a production-ready deployment:

- **The endpoint is public.** It uses the `ApplicationManaged` auth type, and the webapp has no sign-in, so anyone with the URL can chat with the agent, and each message invokes the model in your account. Destroy the stack when you're done, or add authentication or a rate limit (`throttle_config.rate_limit` on the endpoint in `terraform/webapp.tf`).
- **All users share one AgentCore session.** The webapp generates the session ID once, at startup. The agent keeps no conversation history, so nothing leaks between users today, but this must change before you add memory.
- **The agent returns the request headers and payload** in its first event, for demonstration purposes. The UI doesn't display them, but they're visible in the browser's network tools.

## Teardown

```bash
make destroy
```
