"""
Lab F-1: Amazon Bedrock introduction.

Lists the foundation models and the cross-region inference profiles available in your region. Bedrock
uses the "bedrock" client for control plane calls like these, and the "bedrock-runtime" client for
calling models (next labs).

Run from src/: uv run 01_foundational_concepts/f1_bedrock_intro.py
"""
import os

import boto3

REGION = os.environ.get("AWS_REGION", "us-east-1")

bedrock = boto3.client("bedrock", region_name=REGION)

# Foundation models, grouped by provider
print("Listing foundation models...\n")
models = bedrock.list_foundation_models(byOutputModality="TEXT")["modelSummaries"]
print(f"Text foundation models in {REGION}: {len(models)}\n")
for model in sorted(models, key=lambda m: (m["providerName"], m["modelId"])):
    print(f"  {model['providerName']:<12} {model['modelId']:<55} input: {', '.join(model['inputModalities'])}")

input("\nPress Enter to continue...")

# Inference profiles route requests across several regions. Newer models are only available
# through an inference profile, so their model ID starts with a geography prefix like "us."
print("\nListing cross-region inference profiles...\n")
profiles = bedrock.list_inference_profiles()["inferenceProfileSummaries"]
print(f"Cross-region inference profiles in {REGION}: {len(profiles)}\n")
for profile in sorted(profiles, key=lambda p: p["inferenceProfileId"]):
    print(f"  {profile['inferenceProfileId']:<55} {profile['inferenceProfileName']}")
