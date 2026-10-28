"""
Lab F-4: Inference parameters and switching models.

Because Converse uses the same format for supported models, switching models usually only means
changing the model ID. Try the same prompt with a few models, and change the inference parameters
below to see how they affect the response.

Run from src/: [MODEL_ID=<model id>] [PROMPT="<prompt>"] uv run 01_foundational_concepts/f4_inference_parameters.py
Examples:
  MODEL_ID=us.amazon.nova-pro-v1:0 uv run 01_foundational_concepts/f4_inference_parameters.py
  MODEL_ID=us.meta.llama3-3-70b-instruct-v1:0 uv run 01_foundational_concepts/f4_inference_parameters.py
  MODEL_ID=us.amazon.nova-2-lite-v1:0 PROMPT="Please write a limerick:" uv run 01_foundational_concepts/f4_inference_parameters.py
"""
import os

import boto3

REGION = os.environ.get("AWS_REGION", "us-east-1")
MODEL_ID = os.environ.get("MODEL_ID") or "us.anthropic.claude-sonnet-4-6"
PROMPT = os.environ.get("PROMPT") or "Please write a haiku:"

# maxTokens: upper limit on response length. The model stops with stopReason "max_tokens" if it hits it.
# temperature: 0 = most predictable, 1 = most varied. Some newer models don't accept both
#   temperature and topP, so this lab only sets temperature.
# stopSequences: the model stops generating as soon as it writes one of these strings.
INFERENCE_CONFIG = {
    "maxTokens": 2000,
    "temperature": 0.5,
    "stopSequences": [],
}


def get_text_response(model, input_content):
    bedrock = boto3.client("bedrock-runtime", region_name=REGION)

    message = {
        "role": "user",
        "content": [{"text": input_content}],
    }

    response = bedrock.converse(
        modelId=model,
        messages=[message],
        inferenceConfig=INFERENCE_CONFIG,
    )

    return response["output"]["message"]["content"][0]["text"], response["stopReason"]


print(f"Model: {MODEL_ID}\nPrompt: {PROMPT}\n")
print("Sending prompt to the model...\n")
text, stop_reason = get_text_response(MODEL_ID, PROMPT)
print(text)
print(f"\nStop reason: {stop_reason}")
