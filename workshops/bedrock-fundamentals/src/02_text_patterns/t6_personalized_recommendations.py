"""
Lab T-6: Personalized recommendations.

Finds the AWS services that best match the user's requirements with an embeddings search, then asks
the model to explain how each match addresses those requirements. The app shows the matching services
first, then the model's explanation for each one.

Before you start, create the database: uv run shared/populate_collections.py
Run from src/: uv run 02_text_patterns/t6_personalized_recommendations.py
"""
import os
import textwrap
from pathlib import Path

import boto3
import chromadb
from chromadb.utils.embedding_functions import AmazonBedrockEmbeddingFunction

REGION = os.environ.get("AWS_REGION", "us-east-1")
MODEL_ID = "us.anthropic.claude-sonnet-4-6"
EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v2:0"
CHROMA_PATH = Path(__file__).resolve().parents[2] / "tmp" / "chroma"


# --- Amazon Bedrock and Chroma

def get_collection(path, collection_name):
    session = boto3.Session(region_name=REGION)
    embedding_function = AmazonBedrockEmbeddingFunction(session=session, model_name=EMBEDDING_MODEL_ID)

    client = chromadb.PersistentClient(path=str(path))
    return client.get_collection(collection_name, embedding_function=embedding_function)


def get_vector_search_results(collection, question):
    return collection.query(query_texts=[question], n_results=3)


def get_matching_services(question):
    collection = get_collection(CHROMA_PATH, "services_collection")
    search_results = get_vector_search_results(collection, question)

    # The description was embedded. The name and URL were stored as metadata, and come back with each match.
    return [
        {"description": document, "name": metadata["name"], "url": metadata["url"]}
        for document, metadata in zip(search_results["documents"][0], search_results["metadatas"][0])
    ]


def get_personalized_recommendation(question, description):
    bedrock = boto3.client("bedrock-runtime", region_name=REGION)

    message = {
        "role": "user",
        "content": [
            {"text": description},
            {"text": "Based on the service description above, please summarize how it addresses the following requirements:"},
            {"text": question},
        ],
    }

    response = bedrock.converse(
        modelId=MODEL_ID,
        messages=[message],
        inferenceConfig={"maxTokens": 2000, "stopSequences": []},
    )

    return response["output"]["message"]["content"][0]["text"]


# --- Command line

print("Name some key features you need from a cloud service. Press Enter on an empty line to exit.\n")

while True:
    input_text = input("> ").strip()
    if not input_text:
        break

    # 1. Find the services closest to the requirements, and show them
    print("\nSearching the service catalog...\n")
    services = get_matching_services(question=input_text)
    for number, service in enumerate(services, start=1):
        print(f"{number}. {service['name']} ({service['url']})")

    # 2. One model call per service: explain how it meets the requirements
    input("\nPress Enter to ask the model how each service meets your requirements...")
    for number, service in enumerate(services, start=1):
        print(f"\n{number}. {service['name']} ({service['url']})\n")
        summary = get_personalized_recommendation(question=input_text, description=service["description"])
        print(textwrap.indent(summary, "   ") + "\n")
