"""
Lab T-2: Document summarization.

The Converse API accepts documents (PDF, Word, Excel, HTML, text, ...) as content blocks, next to
your prompt. This app sends a PDF with the user's instructions for the summary, and streams the
summary with ConverseStream (lab F-6), so it appears as it's written.

Run from src/: uv run 02_text_patterns/t2_summarization.py
"""
import os
from pathlib import Path

import boto3

REGION = os.environ.get("AWS_REGION", "us-east-1")
MODEL_ID = "us.anthropic.claude-sonnet-4-6"
DOCUMENT_PATH = Path(__file__).resolve().parent.parent / "shared" / "documents" / "anycompany-leadership-principles.pdf"


# --- Amazon Bedrock

def get_summary(input_text, streaming_callback):
    doc_bytes = DOCUMENT_PATH.read_bytes()

    doc_message = {
        "role": "user",
        "content": [
            {
                "document": {
                    "name": "Document 1",  # letters, numbers, spaces, hyphens, parentheses and brackets only
                    "format": "pdf",
                    "source": {"bytes": doc_bytes},  # raw bytes, no base64 encoding needed
                }
            },
            {"text": input_text},
        ],
    }

    bedrock = boto3.client("bedrock-runtime", region_name=REGION)

    response = bedrock.converse_stream(
        modelId=MODEL_ID,
        messages=[doc_message],
        inferenceConfig={"maxTokens": 2000},
    )

    for event in response["stream"]:
        if "contentBlockDelta" in event:
            streaming_callback(event["contentBlockDelta"]["delta"]["text"])


# --- Command line

def print_chunk(chunk):
    print(chunk, end="", flush=True)  # no line break, and show the chunk right away


print(f"Document: {DOCUMENT_PATH.name}")
print("How would you like the document summarized? Press Enter on an empty line to exit.\n")

while True:
    input_text = input("> ").strip()
    if not input_text:
        break

    print("\nSending the document and your instructions to the model...\n")
    get_summary(input_text, streaming_callback=print_chunk)
    print("\n")
