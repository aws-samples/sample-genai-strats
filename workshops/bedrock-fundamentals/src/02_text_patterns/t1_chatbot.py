"""
Lab T-1: Chatbot.

Models have no memory. The app keeps the chat history and sends all of it with every new message.
To stay within the model's context window, it drops the oldest messages once there are more than
MAX_MESSAGES. Replies are streamed with ConverseStream (lab F-6), so they appear as they're written.

Run from src/: uv run 02_text_patterns/t1_chatbot.py
"""
import os

import boto3

REGION = os.environ.get("AWS_REGION", "us-east-1")
MODEL_ID = "us.anthropic.claude-sonnet-4-6"
MAX_MESSAGES = 20


# --- Amazon Bedrock

class ChatMessage:
    def __init__(self, role, text):
        self.role = role
        self.text = text


def convert_chat_messages_to_converse_api(chat_messages):
    messages = []
    for chat_msg in chat_messages:
        messages.append({
            "role": chat_msg.role,
            "content": [{"text": chat_msg.text}],
        })
    return messages


def chat_with_model(message_history, new_text, streaming_callback):
    bedrock = boto3.client("bedrock-runtime", region_name=REGION)

    message_history.append(ChatMessage("user", text=new_text))

    # Drop the oldest user and assistant messages in pairs, so the history still starts with a user message
    number_of_messages = len(message_history)
    if number_of_messages > MAX_MESSAGES:
        del message_history[0:(number_of_messages - MAX_MESSAGES) * 2]

    messages = convert_chat_messages_to_converse_api(message_history)

    response = bedrock.converse_stream(
        modelId=MODEL_ID,
        messages=messages,
        inferenceConfig={"maxTokens": 2000, "stopSequences": []},
    )

    # Show each chunk as it arrives, and keep the whole reply for the history
    output = ""
    for event in response["stream"]:
        if "contentBlockDelta" in event:
            chunk = event["contentBlockDelta"]["delta"]["text"]
            streaming_callback(chunk)
            output += chunk

    message_history.append(ChatMessage("assistant", output))


# --- Command line

def print_chunk(chunk):
    print(chunk, end="", flush=True)  # no line break, and show the chunk right away


chat_history = []  # lives for as long as the script runs

print("Chat with the model. Press Enter on an empty line to exit.\n")

while True:
    input_text = input("You: ").strip()
    if not input_text:
        break

    print("\nAssistant: ", end="")
    chat_with_model(message_history=chat_history, new_text=input_text, streaming_callback=print_chunk)
    print("\n")
