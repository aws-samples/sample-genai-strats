"""
Lab T-4: Retrieval-Augmented Generation (RAG).

A question and answer app. The question is turned into a vector with Amazon Titan Text Embeddings
and matched against Amazon Bedrock FAQs in a local Chroma database. The closest matches are added
to the prompt, so the model can base its answer on that content, which makes made-up answers less likely.
The app shows the search results first, then streams the model's answer.

Before you start, create the database: uv run shared/populate_collections.py
Run from src/: uv run 02_text_patterns/t4_rag.py
"""
import itertools
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
    return collection.query(query_texts=[question], n_results=4)


def get_search_results(question):
    collection = get_collection(CHROMA_PATH, "bedrock_faqs_collection")
    search_results = get_vector_search_results(collection, question)

    # Chroma returns a list of results for each query text. We sent one query, so flatten the list.
    return list(itertools.chain(*search_results["documents"]))


def get_rag_response(question, search_results, streaming_callback):
    bedrock = boto3.client("bedrock-runtime", region_name=REGION)

    rag_content = "\n\n".join(search_results)

    message = {
        "role": "user",
        "content": [
            {"text": rag_content},
            {"text": "Based on the content above, please answer the following question:"},
            {"text": question},
        ],
    }

    response = bedrock.converse_stream(
        modelId=MODEL_ID,
        messages=[message],
        inferenceConfig={"maxTokens": 2000, "stopSequences": []},
    )

    for event in response["stream"]:
        if "contentBlockDelta" in event:
            streaming_callback(event["contentBlockDelta"]["delta"]["text"])


# --- Command line

def print_chunk(chunk):
    print(chunk, end="", flush=True)  # no line break, and show the chunk right away


print("Ask a question about Amazon Bedrock. Press Enter on an empty line to exit.\n")

while True:
    input_text = input("> ").strip()
    if not input_text:
        break

    # 1. Find the FAQ entries closest to the question, and show them
    print("\nSearching the vector database...\n")
    search_results = get_search_results(question=input_text)
    for number, result in enumerate(search_results, start=1):
        print(f"{number}. " + textwrap.indent(result, "   ").lstrip() + "\n")

    # 2. Send the search results and the question to the model, and stream its answer
    input("Press Enter to send the search results and your question to the model...")
    print("\nStreaming the answer...\n")
    get_rag_response(question=input_text, search_results=search_results, streaming_callback=print_chunk)
    print("\n")
