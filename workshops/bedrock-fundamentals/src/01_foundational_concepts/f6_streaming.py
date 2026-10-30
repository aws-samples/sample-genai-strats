"""
Lab F-6: The streaming API.

ConverseStream returns the response as a stream of events, so you can show the text as it's
generated instead of waiting for the whole response.

Run from src/: uv run 01_foundational_concepts/f6_streaming.py
"""
import os

import boto3

REGION = os.environ.get("AWS_REGION", "us-east-1")
MODEL_ID = "us.anthropic.claude-sonnet-4-6"


def chunk_handler(chunk):
    print(chunk, end="", flush=True)


def get_streaming_response(prompt, streaming_callback):
    bedrock = boto3.client("bedrock-runtime", region_name=REGION)

    message = {
        "role": "user",
        "content": [{"text": prompt}],
    }

    response = bedrock.converse_stream(
        modelId=MODEL_ID,
        messages=[message],
        inferenceConfig={"maxTokens": 2000},
    )

    # Text arrives in contentBlockDelta events. Other events mark the start and end of the
    # message and carry metadata such as token usage.
    for event in response["stream"]:
        if "contentBlockDelta" in event:
            streaming_callback(event["contentBlockDelta"]["delta"]["text"])


prompt = "Tell me a story about two puppies and two kittens who became best friends:"

print("Sending prompt to the model...\n")
get_streaming_response(prompt, chunk_handler)
print("\n")
