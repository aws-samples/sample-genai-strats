"""
Creates the local Chroma vector database used by the RAG and embeddings search labs
(T3, T4, T5, T6), in tmp/chroma.

- bedrock_faqs_collection: one document per question and answer in data/bedrock_faqs.json
- services_collection: one document per AWS service in data/aws_services.json, with its name and URL

Chroma calls Amazon Titan Text Embeddings to get a vector for every document. Running the script
again rebuilds both collections from scratch.

Run from src/: uv run shared/populate_collections.py
"""
import json
import os
from pathlib import Path

import boto3
import chromadb
from chromadb.utils.embedding_functions import AmazonBedrockEmbeddingFunction

REGION = os.environ.get("AWS_REGION", "us-east-1")
EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v2:0"
DATA_DIR = Path(__file__).resolve().parent / "data"
CHROMA_PATH = Path(__file__).resolve().parents[2] / "tmp" / "chroma"


def recreate_collection(client, name, embedding_function):
    if name in [collection.name for collection in client.list_collections()]:
        client.delete_collection(name)
    return client.create_collection(name, embedding_function=embedding_function)


session = boto3.Session(region_name=REGION)
embedding_function = AmazonBedrockEmbeddingFunction(session=session, model_name=EMBEDDING_MODEL_ID)
client = chromadb.PersistentClient(path=str(CHROMA_PATH))

# Bedrock FAQs: each question and its answer are one chunk
faqs = json.loads((DATA_DIR / "bedrock_faqs.json").read_text())
collection = recreate_collection(client, "bedrock_faqs_collection", embedding_function)
collection.add(
    ids=[f"faq-{i}" for i in range(len(faqs))],
    documents=[f"{faq['question']}\n{faq['answer']}" for faq in faqs],
)
print(f"bedrock_faqs_collection: {collection.count()} documents")

# AWS services: the description is embedded, the name and URL are stored as metadata
services = json.loads((DATA_DIR / "aws_services.json").read_text())
collection = recreate_collection(client, "services_collection", embedding_function)
collection.add(
    ids=[f"service-{i}" for i in range(len(services))],
    documents=[service["description"] for service in services],
    metadatas=[{"name": service["name"], "url": service["url"]} for service in services],
)
print(f"services_collection: {collection.count()} documents")

print(f"\nChroma database is in {CHROMA_PATH}")
