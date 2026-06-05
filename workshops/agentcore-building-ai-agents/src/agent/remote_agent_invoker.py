import boto3
import base64
import json
import uuid

AGENT_RUNTIME_ARN_FILE = "../../tmp/agent_runtime_arn.txt"
AGENT_RUNTIME_ARN = open(AGENT_RUNTIME_ARN_FILE).read().strip()
session_id = str(uuid.uuid4())

def invoke_remote_agent(prompt: str):
    client = boto3.client("bedrock-agentcore")
    payload = json.dumps({"prompt": prompt})

    response = client.invoke_agent_runtime(
        agentRuntimeArn=AGENT_RUNTIME_ARN,
        runtimeSessionId=session_id,
        payload=payload,
        contentType="application/json",
    )
    buffer = ""
    for chunk in response["response"].iter_chunks(chunk_size=16):
        buffer += chunk.decode() if isinstance(chunk, bytes) else chunk
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            if line.startswith("data: "):
                yield json.loads(line[len("data: "):])

def run():
    print("-" * 20)
    print("Welcome to the AwesomeCorp Customer Support Agent (remote)")
    print(f"AgentCore Runtime ARN: {AGENT_RUNTIME_ARN}")
    while True:
        print("\n" + "-" * 20)
        prompt = input("User prompt (type 'exit' to quit): ").strip()

        if prompt.lower() == "exit":
            break
        if not prompt:
            continue

        print("Sending prompt to the agent running on AgentCore...")
        print()
        for chunk in invoke_remote_agent(prompt):
            print(chunk, end="", flush=True)
        print()

if __name__ == "__main__":
    run()
