"""
Lab F-2: Calling a model with the InvokeModel API.

InvokeModel takes a request body in the model provider's own format. This lab uses the Amazon Nova
"messages-v1" format. Other providers (Anthropic, Meta, Mistral, ...) each have a different format.

Run from src/: uv run 01_foundational_concepts/f2_invoke_model.py
"""
import json
import os

import boto3

REGION = os.environ.get("AWS_REGION", "us-east-1")
MODEL_ID = "us.amazon.nova-2-lite-v1:0"

bedrock = boto3.client("bedrock-runtime", region_name=REGION)

prompt = "What is the largest city in New Hampshire?"

# Request body in the Amazon Nova format
body = json.dumps({
    "schemaVersion": "messages-v1",
    "messages": [
        {
            "role": "user",
            "content": [{"text": prompt}],
        }
    ],
    "inferenceConfig": {
        "maxTokens": 1024,
        "topP": 0.5,
        "topK": 20,
        "temperature": 0.0,
    },
})

print("Sending prompt to the model...\n")
response = bedrock.invoke_model(
    modelId=MODEL_ID,
    body=body,
    accept="application/json",
    contentType="application/json",
)

# The response body is a stream in the same provider-specific format
response_body = json.loads(response["body"].read())
print(response_body["output"]["message"]["content"][0]["text"])
