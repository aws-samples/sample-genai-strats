import { randomUUID } from "crypto";
import { BedrockAgentCoreClient, InvokeAgentRuntimeCommand } from "@aws-sdk/client-bedrock-agentcore";
import { USER_ID } from "./user_auth.js";

const AGENT_RUNTIME_ARN = process.env.AGENT_RUNTIME_ARN;

if (!AGENT_RUNTIME_ARN) {
  console.error("ERROR: AGENT_RUNTIME_ARN environment variable is not set");
  process.exit(1);
}

const client = new BedrockAgentCoreClient();
export const SESSION_ID = randomUUID();

console.log(`AGENT_RUNTIME_ARN=${AGENT_RUNTIME_ARN}`);
console.log(`SESSION_ID=${SESSION_ID}`);

export async function invokeAgent(payload) {
  payload.user_id = USER_ID;
  const cmd = new InvokeAgentRuntimeCommand({
    agentRuntimeArn: AGENT_RUNTIME_ARN,
    payload: JSON.stringify(payload),
    contentType: "application/json",
    runtimeSessionId: SESSION_ID,
    runtimeUserId: USER_ID,
  });
  const response = await client.send(cmd);
  const chunks = [];
  for await (const chunk of response.response) chunks.push(chunk);
  return JSON.parse(Buffer.concat(chunks).toString());
}
