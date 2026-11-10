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

// Invokes the agent. A JSON response is parsed and returned.
// A streaming response (text/event-stream) is passed to onEvent one event at a time,
// and invokeAgent returns { streamed: true } once the stream ends.
export async function invokeAgent(payload, onEvent) {
  payload.user_id = USER_ID;
  const cmd = new InvokeAgentRuntimeCommand({
    agentRuntimeArn: AGENT_RUNTIME_ARN,
    payload: JSON.stringify(payload),
    contentType: "application/json",
    runtimeSessionId: SESSION_ID,
    runtimeUserId: USER_ID,
  });
  const response = await client.send(cmd);

  if ((response.contentType || "").includes("text/event-stream")) {
    await readEventStream(response.response, onEvent || (() => {}));
    return { streamed: true };
  }

  const responseText = await response.response.transformToString();
  return JSON.parse(responseText);
}

// Parses Server-Sent Events ("data: {...}" lines, events separated by a blank line).
async function readEventStream(stream, onEvent) {
  const decoder = new TextDecoder();
  let buffer = "";
  for await (const chunk of stream) {
    buffer += decoder.decode(chunk, { stream: true });
    const events = buffer.split("\n\n");
    buffer = events.pop();
    for (const event of events) {
      for (const line of event.split("\n")) {
        if (line.startsWith("data: ")) onEvent(JSON.parse(line.slice(6)));
      }
    }
  }
}
