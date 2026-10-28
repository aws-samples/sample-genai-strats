"""
Deletes the guardrails created in the Security & safeguards labs, and their ID files in tmp/.

Only deletes guardrails whose names the labs use: "Guardrail-from-Console" (lab S-1),
"Guardrail-from-Code-*" (lab S-2), and "bedrock-fundamentals-*" (labs S-3 and S-4).

Run from the project root: make delete-guardrails
"""
import os
from pathlib import Path

import boto3

REGION = os.environ.get("AWS_REGION", "us-east-1")
NAME_PREFIXES = ("Guardrail-from-Console", "Guardrail-from-Code-", "bedrock-fundamentals-")
TMP_DIR = Path(__file__).resolve().parents[2] / "tmp"

bedrock = boto3.client("bedrock", region_name=REGION)

# Collect first, then delete, so the paginator doesn't skip anything
guardrails = []
for page in bedrock.get_paginator("list_guardrails").paginate():
    guardrails += [g for g in page["guardrails"] if g["name"].startswith(NAME_PREFIXES)]

for guardrail in guardrails:
    bedrock.delete_guardrail(guardrailIdentifier=guardrail["id"])  # deletes all its versions
    print(f"Deleted {guardrail['name']} ({guardrail['id']})")

for id_file in TMP_DIR.glob("*_guardrail_id.txt"):
    id_file.unlink()

print(f"Deleted {len(guardrails)} guardrails in {REGION}")
