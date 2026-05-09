import boto3
import os
import logging
import json
import uuid
from user_auth import USER_ID

l = logging.getLogger("aws.agentcore_client")

ac_client = boto3.client("bedrock-agentcore")

AGENT_RUNTIME_ARN = os.getenv("AGENT_RUNTIME_ARN")
SESSION_ID=str(uuid.uuid4())
l.info(f"AGENT_RUNTIME_ARN={AGENT_RUNTIME_ARN}")
l.info(f"SESSION_ID={SESSION_ID}")

def invoke_agent(payload):
    l.info("> invoke_agent")
    payload["user_id"] = USER_ID
    
    response = ac_client.invoke_agent_runtime(
        agentRuntimeArn = AGENT_RUNTIME_ARN,
        payload=json.dumps(payload),
        contentType="application/json",
        runtimeSessionId=SESSION_ID,
        runtimeUserId=USER_ID
    )
    status_code = response["ResponseMetadata"]["HTTPStatusCode"]
    l.info(f"| response.status_code={status_code}")
    response_body = response["response"].read().decode()
    # print(f">| response_body: {response_body}")
    return json.loads(response_body)

