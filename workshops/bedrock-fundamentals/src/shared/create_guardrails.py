"""
Creates (or updates) the guardrails for labs S-3 and S-4, and saves their IDs to tmp/, where the labs
read them:
- bedrock-fundamentals-content-blocking (lab S-3): content filters, a denied topic, and word filters
- bedrock-fundamentals-prompt-attack (lab S-4): blocks prompt attacks

Change a definition below and run the script again to update the guardrail.

Run from the project root: make create-guardrails
"""
import os
import time
from pathlib import Path

import boto3

REGION = os.environ.get("AWS_REGION", "us-east-1")
TMP_DIR = Path(__file__).resolve().parents[2] / "tmp"

BLOCKED_INPUT_MESSAGE = "Apologies, this model cannot be used to discuss inappropriate or off-topic content."
BLOCKED_OUTPUT_MESSAGE = "Apologies, the model's response to your request was blocked."

# Each guardrail is a dictionary of create_guardrail parameters, with one entry per policy type
CONTENT_BLOCKING_GUARDRAIL = {
    "name": "bedrock-fundamentals-content-blocking",
    "description": "Lab S-3: content filters, denied topics, and word filters",
    # Content filters: a strength for prompts (input) and for responses (output). Prompt attacks
    # are only checked in prompts, so the PROMPT_ATTACK output strength is NONE.
    "contentPolicyConfig": {
        "filtersConfig": [
            {"type": "SEXUAL", "inputStrength": "HIGH", "outputStrength": "HIGH"},
            {"type": "HATE", "inputStrength": "HIGH", "outputStrength": "HIGH"},
            {"type": "VIOLENCE", "inputStrength": "HIGH", "outputStrength": "HIGH"},
            {"type": "INSULTS", "inputStrength": "HIGH", "outputStrength": "HIGH"},
            {"type": "MISCONDUCT", "inputStrength": "HIGH", "outputStrength": "HIGH"},
            {"type": "PROMPT_ATTACK", "inputStrength": "HIGH", "outputStrength": "NONE"},
        ]
    },
    # Denied topics: described in natural language, with sample phrases
    "topicPolicyConfig": {
        "topicsConfig": [
            {
                "name": "Bitcoin",
                "definition": "Providing advice, direction, or examples of how to mine, use, or interact with Bitcoin, including Cryptocurrency-related third-party services.",
                "examples": [
                    "How do I mine Bitcoin?",
                    "What is the current value of BTC?",
                    "Which instance is the best for crypto mining?",
                    "Is mining cryptocurrency against the terms?",
                    "How do I maximize my Bitcoin profits?",
                ],
                "type": "DENY",
            }
        ]
    },
    # Word filters: your own words, plus the managed profanity list
    "wordPolicyConfig": {
        "wordsConfig": [{"text": "AnyCompany"}],
        "managedWordListsConfig": [{"type": "PROFANITY"}],
    },
    "blockedInputMessaging": BLOCKED_INPUT_MESSAGE,
    "blockedOutputsMessaging": BLOCKED_OUTPUT_MESSAGE,
}

PROMPT_ATTACK_GUARDRAIL = {
    "name": "bedrock-fundamentals-prompt-attack",
    "description": "Lab S-4: prompt attack blocking",
    # The prompt attack filter is one of the content filters. It only checks prompts.
    "contentPolicyConfig": {
        "filtersConfig": [
            {"type": "PROMPT_ATTACK", "inputStrength": "HIGH", "outputStrength": "NONE"},
        ]
    },
    "blockedInputMessaging": BLOCKED_INPUT_MESSAGE,
    "blockedOutputsMessaging": BLOCKED_OUTPUT_MESSAGE,
}

# Each guardrail's ID is saved to tmp/<file name>
GUARDRAILS = {
    "content_blocking_guardrail_id.txt": CONTENT_BLOCKING_GUARDRAIL,
    "prompt_attack_guardrail_id.txt": PROMPT_ATTACK_GUARDRAIL,
}

bedrock = boto3.client("bedrock", region_name=REGION)


def find_guardrail_id(name):
    for page in bedrock.get_paginator("list_guardrails").paginate():
        for guardrail in page["guardrails"]:
            if guardrail["name"] == name:
                return guardrail["id"]
    return None


def create_or_update_guardrail(guardrail):
    # Create the guardrail the first time, update its DRAFT version after that
    guardrail_id = find_guardrail_id(guardrail["name"])
    if guardrail_id:
        print(f"Updating guardrail {guardrail['name']} ({guardrail_id})...")
        bedrock.update_guardrail(guardrailIdentifier=guardrail_id, **guardrail)
    else:
        print(f"Creating guardrail {guardrail['name']}...")
        guardrail_id = bedrock.create_guardrail(**guardrail)["guardrailId"]

    # A guardrail can be used once it's READY, usually after a few seconds
    while (status := bedrock.get_guardrail(guardrailIdentifier=guardrail_id)["status"]) != "READY":
        if status == "FAILED":
            raise SystemExit(f"Guardrail {guardrail_id} failed, check it in the Amazon Bedrock console")
        time.sleep(2)
    return guardrail_id


TMP_DIR.mkdir(exist_ok=True)
for file_name, guardrail in GUARDRAILS.items():
    guardrail_id = create_or_update_guardrail(guardrail)
    (TMP_DIR / file_name).write_text(guardrail_id)
    print(f"  READY, ID saved to tmp/{file_name}")
