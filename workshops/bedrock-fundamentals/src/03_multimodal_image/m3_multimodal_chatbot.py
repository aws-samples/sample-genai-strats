"""
Lab M-3: Multimodal chatbot.

The chatbot from lab T-1, with images. An image is a user message of its own, and the model replies
to it like to any other message, so you can then ask about it, or compare it with another image.
To add an image, enter /add followed by an image name or path. To see the sample images, enter /list.

Run from src/: uv run 03_multimodal_image/m3_multimodal_chatbot.py
"""
import os
from io import BytesIO
from pathlib import Path

import boto3
from PIL import Image

REGION = os.environ.get("AWS_REGION", "us-east-1")
MODEL_ID = "us.anthropic.claude-sonnet-4-6"
IMAGES_DIR = Path(__file__).resolve().parent.parent / "shared" / "images"
PROJECT_DIR = Path(__file__).resolve().parents[2]
MAX_MESSAGES = 20


# --- Amazon Bedrock

class ChatMessage:
    def __init__(self, role, message_type, text, image_bytes=None):
        self.role = role
        self.message_type = message_type  # "text" or "image"
        self.text = text
        self.image_bytes = image_bytes


def get_image_format(image_bytes):
    # Converse needs the image format: "jpeg", "png", "gif" or "webp"
    return Image.open(BytesIO(image_bytes)).format.lower()


def convert_chat_messages_to_converse_api(chat_messages):
    messages = []
    for chat_msg in chat_messages:
        if chat_msg.message_type == "image":
            messages.append({
                "role": "user",
                "content": [{
                    "image": {
                        "format": get_image_format(chat_msg.image_bytes),
                        "source": {"bytes": chat_msg.image_bytes},
                    }
                }],
            })
        else:
            messages.append({
                "role": chat_msg.role,
                "content": [{"text": chat_msg.text}],
            })
    return messages


def chat_with_model(message_history, new_text=None, new_image_bytes=None):
    bedrock = boto3.client("bedrock-runtime", region_name=REGION)

    if new_text:
        message_history.append(ChatMessage("user", "text", text=new_text))
    elif new_image_bytes:
        message_history.append(ChatMessage("user", "image", text=None, image_bytes=new_image_bytes))

    # Drop the oldest messages in user/assistant pairs. This also limits cost and keeps the request
    # within the model's limits on context size and number of images.
    number_of_messages = len(message_history)
    if number_of_messages > MAX_MESSAGES:
        del message_history[0:(number_of_messages - MAX_MESSAGES) * 2]

    messages = convert_chat_messages_to_converse_api(message_history)

    response = bedrock.converse(
        modelId=MODEL_ID,
        messages=messages,
        inferenceConfig={"maxTokens": 2000, "stopSequences": []},
    )

    output = response["output"]["message"]["content"][0]["text"]
    message_history.append(ChatMessage("assistant", "text", output))
    return output


# --- Command line

def find_image(text):
    # A sample image name like minicar.jpg, or a path to any image file
    for candidate in (IMAGES_DIR / text, PROJECT_DIR / text, Path(text).expanduser()):
        if candidate.is_file():
            return candidate.resolve()
    return None


chat_history = []  # lives for as long as the script runs. A real application would use a memory service.

print("Chat about images. To add an image, enter /add followed by an image name or path, for example:")
print("  /add minihouse.jpg")
print("To see all the sample images, enter /list. Press Enter on an empty line to exit.\n")

while True:
    input_text = input("You: ").strip()
    if not input_text:
        break

    if input_text == "/list":
        # The sample images in shared/images, which /add accepts by name
        print("\nSample images:")
        for path in sorted(IMAGES_DIR.iterdir()):
            if path.suffix.lower() in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
                print(f"  {path.name}")
        print()
        continue

    if input_text.startswith("/add "):
        image_path = find_image(input_text.removeprefix("/add ").strip())
        if not image_path:
            print("\nImage not found. Enter a sample image name like minicar.jpg, or a path to an image file.\n")
            continue
        print(f"\n[Added {image_path.name} to the conversation]")
        output = chat_with_model(chat_history, new_image_bytes=image_path.read_bytes())
    else:
        output = chat_with_model(chat_history, new_text=input_text)

    print(f"\nAssistant: {output}\n")
