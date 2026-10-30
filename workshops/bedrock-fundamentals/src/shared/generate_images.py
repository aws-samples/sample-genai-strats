"""
Generates the sample images in shared/images used by labs F-3, M-1, M-2 and M-3.

Not a lab: run it once to create the images, then commit them. Photos are generated with Stability AI
Stable Image Core (24 images), which is only available in us-west-2. Amazon Nova Canvas, the model
used before, reached end of life on 2026-09-30. The text image is drawn with Pillow, and image.webp is a copy of one of the
photos in WebP format. Existing images are skipped, so delete an image to generate it again.

Run from src/: uv run shared/generate_images.py
"""
import base64
import json
from io import BytesIO
from pathlib import Path

import boto3
from PIL import Image, ImageDraw, ImageFont

# Text-to-image models are only available in us-west-2, not us-east-1 (2026-10-27)
REGION = "us-west-2"
MODEL_ID = "stability.stable-image-core-v1:1"
IMAGES_DIR = Path(__file__).resolve().parent / "images"
SIZE = 768
SEED = 42

# File name -> prompt. M-2 and M-3 use some of these by name, M-1 indexes all of them, so there are
# several images per search term (cat, people, house, car, food, rooms, miniatures, Christmas).
PHOTOS = {
    "food.jpg": "three street tacos with cilantro, onion and lime wedges on a wooden table, food photography",
    "pasta.jpg": "a bowl of spaghetti with tomato sauce and fresh basil on a table in an Italian restaurant",
    "pizza.jpg": "a margherita pizza on a wooden board in a rustic Italian pizzeria",
    "salad.jpg": "a fresh green salad with cherry tomatoes and avocado in a white bowl, top view",
    "people.jpg": "four friends laughing together at a picnic in a sunny park, candid photo",
    "office_meeting.jpg": "three colleagues smiling during a meeting around a table in a bright office",
    "person_and_cat.jpg": "a woman holding a tabby cat in her arms at home, smiling",
    "woman_with_cat.jpg": "a young woman sitting on a sofa petting a grey cat on her lap",
    "cat.jpg": "a tabby cat sitting on a windowsill in the sunlight",
    "two_cats.jpg": "two kittens sleeping next to each other on a knitted blanket",
    "dog.jpg": "a golden retriever running on a sandy beach",
    "house.jpg": "a traditional European-style house with a red tiled roof, white walls and flower boxes",
    "house_and_car.jpg": "a modern suburban house with a red car parked in the driveway, sunny day",
    "minihouse.jpg": "a detailed handmade miniature model of a cottage on a wooden table, close-up",
    "miniature_village.jpg": "a miniature model village with tiny houses, trees and a church, tilt-shift photo",
    "minicar.jpg": "a small blue die-cast miniature toy car on a white table, close-up",
    "toy_car.jpg": "a colorful wooden toy car on the floor of a child's playroom",
    "room.jpg": "a bright modern living room with a grey sofa, a coffee table and plants",
    "bedroom.jpg": "a cozy bedroom with a large bed, white linen and a bedside lamp",
    "christmas_living_room.jpg": "a living room decorated for Christmas with a lit Christmas tree and presents",
    "christmas_cookies.jpg": "Christmas cookies shaped like stars and trees on a plate, festive decorations",
    "beach.jpg": "a tropical beach with palm trees and turquoise water",
    "mountain.jpg": "a snow-capped mountain above a calm lake at sunrise",
    "city.jpg": "a busy city street at night with lights, shops and people walking",
}
NEGATIVE_PROMPT = "text, watermark, logo, blurry, distorted"

TEXT_IMAGE = "text.png"
TEXT_LINES = [
    "AnyCompany Coffee Shop",  # ASCII only: the default font has no accented letters
    "",
    "Open every day from 7 am to 7 pm",
    "Today's special: tomato soup",
    "and a grilled cheese sandwich",
    "",
    "Free Wi-Fi for customers",
    "Please ask our staff for the password",
]

WEBP_IMAGE = "image.webp"
WEBP_SOURCE = "minihouse.jpg"


def generate_photo(bedrock, prompt):
    body = {
        "prompt": prompt,
        "negative_prompt": NEGATIVE_PROMPT,
        "aspect_ratio": "1:1",
        "output_format": "jpeg",
        "seed": SEED,
    }
    response = bedrock.invoke_model(modelId=MODEL_ID, body=json.dumps(body))
    response_body = json.loads(response["body"].read())
    # null means success, otherwise the reason the image was filtered
    if response_body["finish_reasons"][0]:
        raise SystemExit(f"Image not generated: {response_body['finish_reasons'][0]} ({prompt})")
    image = Image.open(BytesIO(base64.b64decode(response_body["images"][0])))
    # Smaller images keep the repo small, and are plenty for the labs
    return image.resize((SIZE, SIZE))


def draw_text_image():
    image = Image.new("RGB", (SIZE, 420), "#f5efe6")
    draw = ImageDraw.Draw(image)
    title_font = ImageFont.load_default(size=48)
    font = ImageFont.load_default(size=30)
    y = 40
    for i, line in enumerate(TEXT_LINES):
        draw.text((48, y), line, fill="#3b2a1a", font=title_font if i == 0 else font)
        y += 60 if i == 0 else 38
    return image


IMAGES_DIR.mkdir(exist_ok=True)
bedrock = boto3.client("bedrock-runtime", region_name=REGION)

for file_name, prompt in PHOTOS.items():
    path = IMAGES_DIR / file_name
    if path.exists():
        print(f"  {file_name}: exists, skipped")
        continue
    generate_photo(bedrock, prompt).convert("RGB").save(path, "JPEG", quality=85)
    print(f"  {file_name}: generated")

if not (IMAGES_DIR / TEXT_IMAGE).exists():
    draw_text_image().save(IMAGES_DIR / TEXT_IMAGE, "PNG")
    print(f"  {TEXT_IMAGE}: drawn")

if not (IMAGES_DIR / WEBP_IMAGE).exists():
    Image.open(IMAGES_DIR / WEBP_SOURCE).save(IMAGES_DIR / WEBP_IMAGE, "WEBP", quality=85)
    print(f"  {WEBP_IMAGE}: converted from {WEBP_SOURCE}")
