"""
Lab S-4: Prompt attack blocking.

A command-line chat that sends each prompt to a model with the prompt attack guardrail applied. It
detects jailbreaks, which try to get around the model's safeguards, and prompt injection, which tries
to override the developer's instructions.

The user's prompt is sent in a guardContent block: that's input tagging. The guardrail only checks
tagged content, so the system prompt (the developer's instructions) isn't mistaken for a prompt
attack. Without guardContent blocks, the guardrail checks the whole message.

The guardrail is defined in shared/create_guardrails.py. make s4 creates it if it doesn't exist yet.

Run from the project root: make s4
Or from src/: GUARDRAIL_ID=<id> uv run 04_security_safeguards/s4_prompt_attack.py
"""
import os

import boto3

REGION = os.environ.get("AWS_REGION", "us-east-1")
MODEL_ID = "us.anthropic.claude-sonnet-4-6"
GUARDRAIL_ID = os.environ["GUARDRAIL_ID"]
GUARDRAIL_VERSION = os.environ.get("GUARDRAIL_VERSION") or "DRAFT"
SYSTEM_PROMPT = "You are a helpful assistant for Acme Investments customers. Answer briefly."


# --- Amazon Bedrock

def get_response_with_guardrail(prompt):
    bedrock = boto3.client("bedrock-runtime", region_name=REGION)

    response = bedrock.converse(
        modelId=MODEL_ID,
        system=[{"text": SYSTEM_PROMPT}],  # the developer's instructions: not tagged, not checked
        messages=[{
            "role": "user",
            "content": [{"guardContent": {"text": {"text": prompt}}}],  # the user's input: tagged, checked
        }],
        inferenceConfig={"maxTokens": 1000},
        guardrailConfig={
            "guardrailIdentifier": GUARDRAIL_ID,
            "guardrailVersion": GUARDRAIL_VERSION,
            "trace": "enabled",  # adds the guardrail's findings to the response
        },
    )

    # When the guardrail intervenes, the text is the guardrail's blocked message
    output = response["output"]["message"]["content"][0]["text"]
    intervened = response["stopReason"] == "guardrail_intervened"
    trace = response.get("trace", {}).get("guardrail", {})
    return output, intervened, trace


def describe_assessment(assessment):
    # The prompt attack filter is one of the content filters
    findings = []
    for content_filter in assessment.get("contentPolicy", {}).get("filters", []):
        findings.append(f"content filter {content_filter['type']} ({content_filter['confidence']} confidence)")
    return findings


# --- Command line

print(f"Guardrail {GUARDRAIL_ID}, version {GUARDRAIL_VERSION}, model {MODEL_ID}")
print("Type a prompt and press Enter. Press Enter on an empty line to exit.\n")

while True:
    input_text = input("> ").strip()
    if not input_text:
        break

    print("\nSending the prompt to the model, with the guardrail...\n")
    output, intervened, trace = get_response_with_guardrail(input_text)
    print(output + "\n")

    # Prompt attacks are only checked in the prompt
    print(f"Guardrail action: {'INTERVENED' if intervened else 'NONE'}")
    for assessment in trace.get("inputAssessment", {}).values():
        for finding in describe_assessment(assessment):
            print(f"  - prompt: {finding}")
    print()
