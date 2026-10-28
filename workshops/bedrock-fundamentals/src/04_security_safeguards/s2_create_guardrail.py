"""
Lab S-2: Creating guardrails programmatically.

Creates a guardrail with the same settings as the one you created in the console in lab S-1, then a
numbered version of it. Every run creates a new guardrail with a random suffix in its name.

API reference: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock/client/create_guardrail.html

Run from src/: uv run 04_security_safeguards/s2_create_guardrail.py
"""
import os
import random
import string

import boto3

REGION = os.environ.get("AWS_REGION", "us-east-1")

# Guardrails are managed with the "bedrock" client. Applying them uses "bedrock-runtime".
bedrock = boto3.client("bedrock", region_name=REGION)

print("Creating the guardrail...")
response = bedrock.create_guardrail(
    name="Guardrail-from-Code-" + "".join(random.choices(string.ascii_lowercase, k=8)),
    description="Created in lab S2",
    # Denied topics: described in natural language, with sample phrases
    topicPolicyConfig={
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
    # Content filters: separate strengths for prompts (input) and responses (output)
    contentPolicyConfig={
        "filtersConfig": [
            {"type": "SEXUAL", "inputStrength": "HIGH", "outputStrength": "HIGH"},
            {"type": "HATE", "inputStrength": "HIGH", "outputStrength": "HIGH"},
            {"type": "VIOLENCE", "inputStrength": "HIGH", "outputStrength": "HIGH"},
            {"type": "INSULTS", "inputStrength": "HIGH", "outputStrength": "HIGH"},
            {"type": "MISCONDUCT", "inputStrength": "HIGH", "outputStrength": "HIGH"},
            {"type": "PROMPT_ATTACK", "inputStrength": "HIGH", "outputStrength": "NONE"},
        ]
    },
    # Word filters: your own words, plus the managed profanity list
    wordPolicyConfig={
        "wordsConfig": [{"text": "AnyCompany"}],
        "managedWordListsConfig": [{"type": "PROFANITY"}],
    },
    # Sensitive information: ANONYMIZE masks it, BLOCK blocks the whole prompt or response
    sensitiveInformationPolicyConfig={
        "piiEntitiesConfig": [
            {"type": "NAME", "action": "ANONYMIZE"},
            {"type": "EMAIL", "action": "ANONYMIZE"},
        ],
    },
    blockedInputMessaging="Apologies, this model cannot be used to discuss inappropriate or off-topic content.",
    blockedOutputsMessaging="Apologies, the model's response to your request was blocked.",
)

guardrail_id = response["guardrailId"]
print(f"Guardrail ID: {guardrail_id}")

input("\nPress Enter to continue...")

# A numbered version is a snapshot that doesn't change. Applications should use one, while you
# keep working on the DRAFT version.
print("\nCreating a numbered version of the guardrail...")
response = bedrock.create_guardrail_version(guardrailIdentifier=guardrail_id)
print(f"Version: {response['version']}")
