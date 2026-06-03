import { invokeAgent } from "./ac_client.js";

export async function initAgent(callbackUrl) {
  console.log(`> initAgent callbackUrl=${callbackUrl}`);
  const response = await invokeAgent({ cmd: "initialize", callback_url: callbackUrl });
  console.log(`> initAgent response=${JSON.stringify(response)}`);
  return response;
}

export async function handleMessage(message) {
  console.log(`> handleMessage message=${message}`);
  const response = await invokeAgent({ cmd: "prompt", prompt: message });
  console.log(`> handleMessage response=${JSON.stringify(response)}`);
  if (response.status === "ok") {
    console.log(`| handleMessage success response_length=${response.response?.length}`);
    return response.response;
  }
  console.error(`| handleMessage non-ok status=${response.status} response=${JSON.stringify(response)}`);
  return "Error communicating with agent. Try again.";
}
