"""
Lab M-2: Image understanding.

Sends an image and a prompt to a multimodal model in one message. The same pattern covers captions,
classification, object lists, reading and translating text in images, and more: only the prompt changes.

Choose a sample image and prompt by number, or enter your own image path and prompt.

Run from src/: uv run 03_multimodal_image/m2_image_understanding.py
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


# --- Amazon Bedrock

def get_image_format(image_bytes):
    # Converse needs the image format: "jpeg", "png", "gif" or "webp"
    return Image.open(BytesIO(image_bytes)).format.lower()


def get_response_from_model(prompt_content, image_bytes):
    bedrock = boto3.client("bedrock-runtime", region_name=REGION)

    # Three content blocks: a label for the image, the image itself, and the prompt about it
    image_message = {
        "role": "user",
        "content": [
            {"text": "Image 1:"},
            {
                "image": {
                    "format": get_image_format(image_bytes), # jpeg, png, gif etc.
                    "source": {"bytes": image_bytes},  # raw bytes, no base64 encoding needed
                }
            },
            {"text": prompt_content},
        ],
    }

    response = bedrock.converse(
        modelId=MODEL_ID,
        messages=[image_message],
        inferenceConfig={"maxTokens": 2000},
    )

    return response["output"]["message"]["content"][0]["text"]


# --- Command line

prompt_options_dict = {
    "Image caption": "Please provide a brief caption for this image.",
    "Detailed description": "Please provide a thoroughly detailed description of this image.",
    "Image classification": "Please categorize this image into one of the following categories: People, Food, Other. Only return the category name.",
    "Object recognition": "Please create a comma-separated list of the items found in this image. Only return the list of items.",
    "Subject identification": "Please name the primary object in the image. Only return the name of the object in <object> tags.",
    "Writing a story": "Please write a fictional short story based on this image.",
    "Answering questions": "What emotion are the people in this image displaying?",
    "Transcribing text": "Please transcribe any text found in this image.",
    "Translating text": "Please translate the text in this image to French.",
}

image_options_dict = {
    "Food": IMAGES_DIR / "food.jpg",
    "People": IMAGES_DIR / "people.jpg",
    "Person and cat": IMAGES_DIR / "person_and_cat.jpg",
    "Room": IMAGES_DIR / "room.jpg",
    "Text in image": IMAGES_DIR / "text.png",
    "Toy": IMAGES_DIR / "toy_car.jpg",
}


def choose(options, text):
    # A number picks a sample from the list. Anything else is returned as it is.
    if text.isdigit() and 1 <= int(text) <= len(options):
        return list(options.values())[int(text) - 1]
    return text


def find_image(text):
    # A sample image name like cat.jpg, or a path to any image file
    for candidate in (IMAGES_DIR / text, PROJECT_DIR / text, Path(text).expanduser()):
        if candidate.is_file():
            return candidate.resolve()
    return None


while True:
    print("Images:")
    for number, (name, path) in enumerate(image_options_dict.items(), start=1):
        print(f"  {number}. {name} ({path.name})")
    image_input = input("\nChoose an image by number, or enter the path of your own image. Press Enter to exit: ").strip()
    if not image_input:
        break
    image_path = find_image(str(choose(image_options_dict, image_input)))
    if not image_path:
        print(f"\nImage not found: {image_input}\n")
        continue

    print("\nPrompts:")
    for number, (name, prompt) in enumerate(prompt_options_dict.items(), start=1):
        print(f"  {number}. {name}: {prompt}")
    prompt_input = input("\nChoose a prompt by number, or enter your own prompt: ").strip()
    if not prompt_input:
        break
    prompt_text = choose(prompt_options_dict, prompt_input)

    print(f"\nSending {image_path.name} and the prompt to the model...\n")
    print(get_response_from_model(prompt_content=prompt_text, image_bytes=image_path.read_bytes()) + "\n")
