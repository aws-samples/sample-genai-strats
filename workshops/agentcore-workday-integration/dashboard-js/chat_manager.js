import { invokeAgent } from "./ac_client.js";

export async function initAgent(callbackUrl) {
  console.log(`> initAgent callbackUrl=${callbackUrl}`);
  const response = await invokeAgent({ cmd: "initialize", callback_url: callbackUrl });
  console.log(`> initAgent response=${JSON.stringify(response)}`);
  if (response.status === "ok") return null;
  return response.auth_url;
}

export async function handleMessage(message) {
  console.log(`> handleMessage message=${message}`);
  const response = await invokeAgent({ cmd: "prompt", prompt: message });
  console.log(`> handleMessage response=${JSON.stringify(response)}`);
  if (response.status === "ok") return response.response;
  return "Error communicating with agent. Try again.";
}
