import { invokeAgent } from "./ac_client.js";

export async function initAgent(callbackUrl) {
  console.log(`> initAgent callbackUrl=${callbackUrl}`);
  const response = await invokeAgent({ cmd: "initialize", callback_url: callbackUrl });
  console.log(`> initAgent response=${JSON.stringify(response)}`);
  return response;
}

// Sends the message and passes the agent's events ({delta}, {tool}, {error}, {done}) to onEvent.
export async function handleMessage(message, onEvent) {
  console.log(`> handleMessage message=${message}`);
  let length = 0;
  const response = await invokeAgent({ cmd: "prompt", prompt: message }, (event) => {
    if (event.delta) length += event.delta.length;
    if (event.tool) console.log(`| handleMessage tool=${event.tool}`);
    if (event.error) console.error(`| handleMessage error=${event.error}`);
    onEvent(event);
  });

  if (response.streamed) {
    console.log(`| handleMessage stream ended response_length=${length}`);
    return;
  }

  // Non-streaming agent: {"status": "ok", "response": "..."}
  console.log(`> handleMessage response=${JSON.stringify(response)}`);
  if (response.status === "ok") {
    onEvent({ delta: response.response });
    onEvent({ done: true });
    return;
  }
  console.error(`| handleMessage non-ok status=${response.status} response=${JSON.stringify(response)}`);
  onEvent({ error: "Error communicating with agent. Try again." });
}
