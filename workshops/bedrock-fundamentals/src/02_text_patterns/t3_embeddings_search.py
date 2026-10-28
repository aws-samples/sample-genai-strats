"""
Lab T-3: Embeddings search.

The retrieval half of RAG on its own: the question is matched against the Amazon Bedrock FAQs, and
the closest matches are shown directly, without calling a text model. Useful to check what a RAG app
would retrieve. The lower the distance, the closer the match.

Before you start, create the database: uv run shared/populate_collections.py
Run from src/: uv run 02_text_patterns/t3_embeddings_search.py
"""
import os
import textwrap
from pathlib import Path

import boto3
import chromadb
from chromadb.utils.embedding_functions import AmazonBedrockEmbeddingFunction

REGION = os.environ.get("AWS_REGION", "us-east-1")
EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v2:0"
CHROMA_PATH = Path(__file__).resolve().parents[2] / "tmp" / "chroma"


# --- Amazon Bedrock and Chroma

def get_collection(path, collection_name):
    session = boto3.Session(region_name=REGION)
    embedding_function = AmazonBedrockEmbeddingFunction(session=session, model_name=EMBEDDING_MODEL_ID)

    client = chromadb.PersistentClient(path=str(path))
    return client.get_collection(collection_name, embedding_function=embedding_function)


def get_vector_search_results(collection, question):
    return collection.query(query_texts=[question], n_results=4)


def get_similarity_search_results(question):
    collection = get_collection(CHROMA_PATH, "bedrock_faqs_collection")
    search_results = get_vector_search_results(collection, question)

    # One query text, so the first (and only) list of results
    return [
        {"distance": round(distance, 4), "content": document}
        for document, distance in zip(search_results["documents"][0], search_results["distances"][0])
    ]


# --- Command line

print("Ask a question about Amazon Bedrock. Press Enter on an empty line to exit.\n")

while True:
    input_text = input("> ").strip()
    if not input_text:
        break

    print("\nSearching the vector database...\n")
    for number, result in enumerate(get_similarity_search_results(question=input_text), start=1):
        print(f"{number}. Distance: {result['distance']}")
        print(textwrap.indent(result["content"], "   ") + "\n")
