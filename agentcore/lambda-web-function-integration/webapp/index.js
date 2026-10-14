import express from "express";
import path from "node:path";
import { randomUUID } from "node:crypto";
import { BedrockAgentCoreClient, InvokeAgentRuntimeCommand } from "@aws-sdk/client-bedrock-agentcore";

const AGENT_RUNTIME_ARN = process.env.AGENT_RUNTIME_ARN;

if (!AGENT_RUNTIME_ARN) {
  console.error("AGENT_RUNTIME_ARN env var is required");
  process.exit(1);
}

// arn:aws:bedrock-agentcore:<region>:<account>:runtime/<id>
const agentRegion = AGENT_RUNTIME_ARN.split(":")[3];
const agentcore = new BedrockAgentCoreClient({ region: agentRegion });

// For demo purposes only, using same AgentCore runtime session per server process.
const sessionId = randomUUID();

const app = express();
app.use(express.json());

app.use(express.static(path.join(import.meta.dirname, "static")));

// Invoke the agent and stream its SSE response back to the browser as it arrives.
app.post("/api/chat", async (req, res) => {
  const { prompt } = req.body ?? {};
  if (!prompt) {
    return res.status(400).json({ error: "Missing required field: 'prompt'" });
  }

  // Stop the agent invocation if the browser goes away mid-stream.
  const abortController = new AbortController();
  res.on("close", () => {
    if (!res.writableEnded) abortController.abort();
  });

  res.writeHead(200, {
    "Content-Type": "text/event-stream",
    "Cache-Control": "no-cache",
    Connection: "keep-alive",
    "X-Accel-Buffering": "no",
  });
  res.flushHeaders();

  try {
    const command = new InvokeAgentRuntimeCommand({
      agentRuntimeArn: AGENT_RUNTIME_ARN,
      runtimeSessionId: sessionId,
      contentType: "application/json",
      accept: "text/event-stream",
      payload: new TextEncoder().encode(JSON.stringify({ prompt })),
    });
    const agentResponse = await agentcore.send(command, { abortSignal: abortController.signal });

    // The agent already emits SSE frames ("data: {...}\n\n"), so pass the bytes through as-is.
    for await (const chunk of agentResponse.response) {
      res.write(chunk);
    }
  } catch (err) {
    if (abortController.signal.aborted) return;
    console.error("Agent invocation failed:", err);
    res.write(`data: ${JSON.stringify({ type: "error", error: err.message })}\n\n`);
  }
  res.end();
});

const [HOSTNAME, PORT] = (process.env.AWS_LAMBDA_HTTP_ENDPOINT || 'localhost:3000').split(':');
app.listen(PORT, HOSTNAME, () => {
  console.log(`webapp listening on http://localhost:${PORT}`);
  console.log(`agent runtime: ${AGENT_RUNTIME_ARN}`);
});
