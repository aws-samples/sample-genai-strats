"""
Lab T-5: Chatbot with RAG.

A chatbot that decides by itself when it needs to look something up. Retrieval is offered to the
model as a tool. When the model calls it, it also rewrites the user's message into a clear search
query, for example "Which models?" becomes "Which models are available in Amazon Bedrock?".
Each time the model uses the tool, the app prints the query and the FAQ entries it found.

Before you start, create the database: uv run shared/populate_collections.py
Run from src/: uv run 02_text_patterns/t5_rag_chatbot.py
"""
import itertools
import os
from pathlib import Path

import boto3
import chromadb
from chromadb.utils.embedding_functions import AmazonBedrockEmbeddingFunction

REGION = os.environ.get("AWS_REGION", "us-east-1")
MODEL_ID = "us.anthropic.claude-sonnet-4-6"
EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v2:0"
CHROMA_PATH = Path(__file__).resolve().parents[2] / "tmp" / "chroma"
MAX_MESSAGES = 20


# --- Amazon Bedrock and Chroma

class ChatMessage:
    def __init__(self, role, text):
        self.role = role
        self.text = text


def get_collection(path, collection_name):
    session = boto3.Session(region_name=REGION)
    embedding_function = AmazonBedrockEmbeddingFunction(session=session, model_name=EMBEDDING_MODEL_ID)

    client = chromadb.PersistentClient(path=str(path))
    return client.get_collection(collection_name, embedding_function=embedding_function)


def get_vector_search_results(collection, question):
    return collection.query(query_texts=[question], n_results=4)


def get_tools():
    return [
        {
            "toolSpec": {
                "name": "get_amazon_bedrock_information",
                "description": "Retrieve information about Amazon Bedrock, a managed service for hosting generative AI models.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The retrieval-augmented generation query used to look up information in a repository of FAQs about Amazon Bedrock.",
                            }
                        },
                        "required": ["query"],
                    }
                },
            }
        }
    ]


def convert_chat_messages_to_converse_api(chat_messages):
    messages = []
    for chat_msg in chat_messages:
        messages.append({
            "role": chat_msg.role,
            "content": [{"text": chat_msg.text}],
        })
    return messages


def get_text(response_message):
    # A response can have several content blocks, for example text followed by a toolUse
    return "".join(block["text"] for block in response_message["content"] if "text" in block)


def call_model(bedrock, messages, tool_list):
    return bedrock.converse(
        modelId=MODEL_ID,
        messages=messages,
        inferenceConfig={"maxTokens": 2000, "stopSequences": []},
        toolConfig={"tools": tool_list},
    )


def run_tools(response_message):
    # Run every search the model asked for. One response can ask for several.
    tool_results = []
    for content_block in response_message["content"]:
        if "toolUse" in content_block:
            tool_use_block = content_block["toolUse"]

            if tool_use_block["name"] == "get_amazon_bedrock_information":
                collection = get_collection(CHROMA_PATH, "bedrock_faqs_collection")

                query = tool_use_block["input"]["query"]
                print(f"\n[Searching the FAQs for: {query}]")

                search_results = get_vector_search_results(collection, query)
                flattened_results_list = list(itertools.chain(*search_results["documents"]))
                rag_content = "\n\n".join(flattened_results_list)
                for document in flattened_results_list:
                    print(f"[Found: {document.splitlines()[0]}]")  # the first line of each entry is the question

                tool_results.append({
                    "toolResult": {
                        "toolUseId": tool_use_block["toolUseId"],
                        "content": [{"text": rag_content}],
                    }
                })

    return tool_results


def chat_with_model(message_history, new_text=None):
    bedrock = boto3.client("bedrock-runtime", region_name=REGION)
    tool_list = get_tools()

    message_history.append(ChatMessage("user", text=new_text))

    number_of_messages = len(message_history)
    if number_of_messages > MAX_MESSAGES:
        del message_history[0:(number_of_messages - MAX_MESSAGES) * 2]

    messages = convert_chat_messages_to_converse_api(message_history)

    response = call_model(bedrock, messages, tool_list)

    # As long as the model asks for the tool, run the searches and send back the results. The model
    # can search again after it sees the results. When it stops asking, its response is the answer.
    while response["stopReason"] == "tool_use":
        response_message = response["output"]["message"]
        messages.append(response_message)
        messages.append({"role": "user", "content": run_tools(response_message)})

        response = call_model(bedrock, messages, tool_list)

    output = get_text(response["output"]["message"])
    message_history.append(ChatMessage("assistant", output))
    return output


# --- Command line

chat_history = []  # lives for as long as the script runs

print("Chat about Amazon Bedrock. Press Enter on an empty line to exit.\n")

while True:
    input_text = input("You: ").strip()
    if not input_text:
        break

    output = chat_with_model(message_history=chat_history, new_text=input_text)
    print(f"\nAssistant: {output}\n")
