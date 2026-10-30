"""
Indexes the sample images for lab M-1 in the local Chroma database, in tmp/chroma.

Each image in shared/images is sent to Amazon Titan Multimodal Embeddings. The vector is stored in
images_collection, with the image's file name as the document. Running the script again rebuilds the
collection from scratch.

Run from src/: uv run shared/populate_image_collection.py
"""
import base64
import json
import os
from pathlib import Path

import boto3
import chromadb

REGION = os.environ.get("AWS_REGION", "us-east-1")
EMBEDDING_MODEL_ID = "amazon.titan-embed-image-v1"
IMAGES_DIR = Path(__file__).resolve().parent / "images"
CHROMA_PATH = Path(__file__).resolve().parents[2] / "tmp" / "chroma"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}

bedrock = boto3.client("bedrock-runtime", region_name=REGION)


def get_image_vector(image_path):
    response = bedrock.invoke_model(
        modelId=EMBEDDING_MODEL_ID,
        body=json.dumps({"inputImage": base64.b64encode(image_path.read_bytes()).decode("utf-8")}),
        accept="application/json",
        contentType="application/json",
    )
    return json.loads(response["body"].read())["embedding"]


client = chromadb.PersistentClient(path=str(CHROMA_PATH))
if "images_collection" in [collection.name for collection in client.list_collections()]:
    client.delete_collection("images_collection")
collection = client.create_collection("images_collection")

image_paths = sorted(path for path in IMAGES_DIR.iterdir() if path.suffix.lower() in IMAGE_SUFFIXES)
for image_path in image_paths:
    print(f"  {image_path.name}")
    collection.add(
        ids=[image_path.name],
        embeddings=[get_image_vector(image_path)],
        documents=[image_path.name],
    )

print(f"\nimages_collection: {collection.count()} images, in {CHROMA_PATH}")
