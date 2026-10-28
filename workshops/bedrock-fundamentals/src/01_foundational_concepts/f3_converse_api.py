"""
Lab F-3: The Converse API.

Converse gives models the same request and response format: a list of messages, each with
a role and a list of content blocks (text, image, document, tool use, ...). The model itself keeps no
state, so to continue a conversation you send the whole message history every time.

Run from src/: uv run 01_foundational_concepts/f3_converse_api.py
"""
import json
import os
from pathlib import Path

import boto3

REGION = os.environ.get("AWS_REGION", "us-east-1")
MODEL_ID = "us.anthropic.claude-sonnet-4-6"
IMAGE_PATH = Path(__file__).resolve().parent.parent / "shared" / "images" / "image.webp"

bedrock = boto3.client("bedrock-runtime", region_name=REGION)

# 1. A basic call: one user message with one text content block
message_list = []
message_list.append({
    "role": "user",
    "content": [{"text": "How are you today?"}],
})

print("1. Basic call\n")
print("Sending prompt to the model...\n")
response = bedrock.converse(
    modelId=MODEL_ID,
    messages=message_list,
    inferenceConfig={"maxTokens": 2000},
)
response_message = response["output"]["message"]
print(json.dumps(response_message, indent=4))

input("\nPress Enter to continue...")

# 2. Add the model's response to the history, so the next call has the whole conversation
message_list.append(response_message)

# 3. A message with an image. Converse takes the raw bytes, no base64 encoding needed
with open(IMAGE_PATH, "rb") as image_file:
    image_bytes = image_file.read()

message_list.append({
    "role": "user",
    "content": [
        {"text": "Image 1:"},
        {"image": {"format": "webp", "source": {"bytes": image_bytes}}},
        {"text": "Please describe the image."},
    ],
})

print("\n3. Image description\n")
print("Sending the conversation and the image to the model...\n")
response = bedrock.converse(
    modelId=MODEL_ID,
    messages=message_list,
    inferenceConfig={"maxTokens": 2000},
)
response_message = response["output"]["message"]
print(response_message["content"][0]["text"])
message_list.append(response_message)

input("\nPress Enter to continue...")

# 4. A system prompt sets the model's behavior for the whole conversation
summary_message = {
    "role": "user",
    "content": [{"text": "Can you please summarize our conversation so far?"}],
}
message_list.append(summary_message)

print("\n4. Summary with a system prompt\n")
print("Sending the conversation and a system prompt to the model...\n")
response = bedrock.converse(
    modelId=MODEL_ID,
    messages=message_list,
    system=[{"text": "Please respond to all requests in the style of a pirate."}],
    inferenceConfig={"maxTokens": 2000},
)
response_message = response["output"]["message"]
print(response_message["content"][0]["text"])
message_list.append(response_message)

input("\nPress Enter to continue...")

# 5. Response metadata: why the model stopped, and how many tokens the call used
print("\n5. Response metadata\n")
print("Stop reason:", response["stopReason"])
print("Usage:", json.dumps(response["usage"], indent=4))
