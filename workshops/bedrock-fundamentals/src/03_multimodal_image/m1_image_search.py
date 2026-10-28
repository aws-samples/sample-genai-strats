"""
Lab M-1: Image search.

Amazon Titan Multimodal Embeddings puts text and images in the same vector space. The sample images
are indexed in a local Chroma database, so you can search them with a text description, or find
images similar to another image. The results are image paths, which you can open in VS Code.

Before you start, index the images: uv run shared/populate_image_collection.py
Run from src/: uv run 03_multimodal_image/m1_image_search.py
"""
import base64
import json
import os
from pathlib import Path

import boto3
import chromadb

REGION = os.environ.get("AWS_REGION", "us-east-1")
EMBEDDING_MODEL_ID = "amazon.titan-embed-image-v1"
IMAGES_DIR = Path(__file__).resolve().parent.parent / "shared" / "images"
PROJECT_DIR = Path(__file__).resolve().parents[2]
CHROMA_PATH = PROJECT_DIR / "tmp" / "chroma"


# --- Amazon Bedrock and Chroma

def get_multimodal_vector(input_image_base64=None, input_text=None):
    bedrock = boto3.client("bedrock-runtime", region_name=REGION)

    # Text, an image, or both
    request_body = {}
    if input_text:
        request_body["inputText"] = input_text
    if input_image_base64:
        request_body["inputImage"] = input_image_base64

    response = bedrock.invoke_model(
        modelId=EMBEDDING_MODEL_ID,
        body=json.dumps(request_body),
        accept="application/json",
        contentType="application/json",
    )

    response_body = json.loads(response["body"].read())
    return response_body["embedding"]


def get_collection(path, collection_name):
    # No embedding function: we create the vectors ourselves and pass them to Chroma
    client = chromadb.PersistentClient(path=str(path))
    return client.get_collection(collection_name)


def get_vector_search_results(collection, query_embedding):
    return collection.query(query_embeddings=[query_embedding], n_results=4)


def get_similarity_search_results(search_term=None, search_image=None):
    # InvokeModel takes JSON, so images are base64-encoded here (unlike Converse, which takes raw bytes)
    search_image_base64 = base64.b64encode(search_image).decode("utf-8") if search_image else None
    query_embedding = get_multimodal_vector(input_text=search_term, input_image_base64=search_image_base64)

    collection = get_collection(CHROMA_PATH, "images_collection")
    search_results = get_vector_search_results(collection, query_embedding)

    # Each document is the file name of an image in shared/images. The lower the distance, the closer the match.
    return [
        (IMAGES_DIR / file_name, distance)
        for file_name, distance in zip(search_results["documents"][0], search_results["distances"][0])
    ]


# --- Command line

def find_image(text):
    # A sample image name like cat.jpg, or a path to any image file
    for candidate in (IMAGES_DIR / text, PROJECT_DIR / text, Path(text).expanduser()):
        if candidate.is_file():
            return candidate.resolve()
    return None


print("Describe the images you're looking for, or enter an image name or path to find similar images.")
print("Press Enter on an empty line to exit.\n")

while True:
    input_text = input("> ").strip()
    if not input_text:
        break

    image_path = find_image(input_text)
    if image_path:
        print(f"\nFinding images similar to {image_path.name}...\n")
        results = get_similarity_search_results(search_image=image_path.read_bytes())
    else:
        print("\nSearching for images that match the description...\n")
        results = get_similarity_search_results(search_term=input_text)

    for number, (path, distance) in enumerate(results, start=1):
        print(f"{number}. {path}  (distance {distance:.4f})")
    print()
