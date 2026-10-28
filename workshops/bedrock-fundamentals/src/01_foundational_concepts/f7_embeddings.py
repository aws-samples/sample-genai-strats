"""
Lab F-7: Embeddings.

An embeddings model turns text into a vector: a list of numbers that captures its meaning. Texts with
similar meanings get similar vectors, even in different languages. Cosine similarity measures how
close two vectors are: 1 means the same, lower means less similar.

Run from src/: uv run 01_foundational_concepts/f7_embeddings.py
"""
import json
import os
from pathlib import Path

import boto3
from numpy import dot
from numpy.linalg import norm

REGION = os.environ.get("AWS_REGION", "us-east-1")
MODEL_ID = "amazon.titan-embed-text-v2:0"
ITEMS_PATH = Path(__file__).resolve().parent.parent / "shared" / "data" / "items.txt"

bedrock = boto3.client("bedrock-runtime", region_name=REGION)


def get_embedding(text):
    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps({"inputText": text}),
        accept="application/json",
        contentType="application/json",
    )

    response_body = json.loads(response["body"].read())
    return response_body["embedding"]


class EmbedItem:
    def __init__(self, text):
        self.text = text
        self.embedding = get_embedding(text)


class ComparisonResult:
    def __init__(self, text, similarity):
        self.text = text
        self.similarity = similarity


def calculate_similarity(a, b):  # see https://en.wikipedia.org/wiki/Cosine_similarity
    return dot(a, b) / (norm(a) * norm(b))


# Get an embedding for every line of items.txt
print("Sending each line of items.txt to the embeddings model...\n")
items = []
for text in ITEMS_PATH.read_text().splitlines():
    if text.strip():
        items.append(EmbedItem(text))

# Compare every item with every other item, closest matches first
for e1 in items:
    print(f"Closest matches for '{e1.text}'")
    print("----------------")
    cosine_comparisons = []

    for e2 in items:
        similarity_score = calculate_similarity(e1.embedding, e2.embedding)
        cosine_comparisons.append(ComparisonResult(e2.text, similarity_score))

    cosine_comparisons.sort(key=lambda x: x.similarity, reverse=True)

    for c in cosine_comparisons:
        print(f"{c.similarity:.6f}\t{c.text}")

    if e1 is not items[-1]:
        input("\nPress Enter to continue...")
    print()
