import boto3
import json
import uuid
import os

session = boto3.session.Session()
region = session.region_name or os.environ['AWS_REGION']
print(f"Region: {region}")

class RemoteTransport:
    def __init__(self, agent_runtime_arn: str):
        self.agent_runtime_arn = agent_runtime_arn
        self.session_id = str(uuid.uuid4())
        self.client = boto3.client("bedrock-agentcore", region_name=region)

    def _invoke(self, cmd: dict) -> dict:
        response = self.client.invoke_agent_runtime(
            agentRuntimeArn=self.agent_runtime_arn,
            runtimeSessionId=self.session_id,
            contentType="application/json",
            accept="application/json",
            payload=json.dumps(cmd).encode(),
        )
        return json.loads(response["response"].read())

    def initialize(self) -> str | None:
        result = self._invoke({"cmd": "initialize"})
        return result.get("auth_url")

    def complete_auth(self, session_id: str) -> None:
        self._invoke({"cmd": "completeAuth", "session_id": session_id})

    def send_prompt(self, prompt: str) -> str:
        result = self._invoke({"cmd": "prompt", "prompt": prompt})
        return result.get("response", result.get("error", "No response"))
