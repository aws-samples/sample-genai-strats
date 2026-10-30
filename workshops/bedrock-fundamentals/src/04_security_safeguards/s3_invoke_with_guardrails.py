"""
Lab S-3: Invoking models with guardrails.

Calls a model with a guardrail applied. Bedrock checks the prompt before it reaches the model, and
the response before it reaches you. With TRACE=1, the response also shows what the guardrail
found and why it acted.

Uses the content blocking guardrail from shared/create_guardrails.py (make s3 creates it if needed).
Run from the project root:
  make s3 PROMPT="How do you wash a car?"
  make s3 PROMPT="How do you hotwire a car?" TRACE=1
Or from src/: GUARDRAIL_ID=<id> PROMPT="<prompt>" [TRACE=1] uv run 04_security_safeguards/s3_invoke_with_guardrails.py
"""
import json
import os

import boto3

REGION = os.environ.get("AWS_REGION", "us-east-1")
MODEL_ID = "us.anthropic.claude-sonnet-4-6"
GUARDRAIL_ID = os.environ["GUARDRAIL_ID"]
# DRAFT is the working copy, fine while you develop. In production, use a numbered version like "1".
GUARDRAIL_VERSION = os.environ.get("GUARDRAIL_VERSION") or "DRAFT"
PROMPT = os.environ.get("PROMPT") or "How do you wash a car?"
TRACE = bool(os.environ.get("TRACE"))
SYSTEM_PROMPT = "Reply with one concise paragraph."


def invoke_model_with_guardrail(prompt, trace=False):
    bedrock_runtime = boto3.client("bedrock-runtime", region_name=REGION)

    # InvokeModel takes the request body in the model provider's own format, here Anthropic's
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 500,
        "system": SYSTEM_PROMPT,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}],
            }
        ],
    }

    response = bedrock_runtime.invoke_model(
        modelId=MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=json.dumps(request_body),
        guardrailIdentifier=GUARDRAIL_ID,
        guardrailVersion=GUARDRAIL_VERSION,
        trace="ENABLED" if trace else "DISABLED",  # adds the guardrail's findings to the response
    )

    response_body = json.loads(response["body"].read())

    if "amazon-bedrock-trace" in response_body:
        print("Amazon Bedrock trace:")
        print(json.dumps(response_body["amazon-bedrock-trace"], indent=4))
        print()

    # When the guardrail intervenes, the text is the guardrail's blocked message
    print(f"Guardrail action: {response_body.get('amazon-bedrock-guardrailAction', 'NONE')}\n")
    return response_body["content"][0]["text"]


print(f"Prompt: {PROMPT}\n")
print("Sending prompt to the model, with the guardrail...\n")
print(invoke_model_with_guardrail(PROMPT, TRACE))
