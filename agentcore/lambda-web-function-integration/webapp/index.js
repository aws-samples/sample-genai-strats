import express from "express";
import path from "node:path";
import { randomUUID, timingSafeEqual, createHmac } from "node:crypto";
import { BedrockAgentCoreClient, InvokeAgentRuntimeCommand } from "@aws-sdk/client-bedrock-agentcore";
import { SecretsManagerClient, GetSecretValueCommand } from "@aws-sdk/client-secrets-manager";

const AGENT_RUNTIME_ARN = process.env.AGENT_RUNTIME_ARN;
const DEMO_LOGIN_SECRET_ARN = process.env.DEMO_LOGIN_SECRET_ARN;
const SESSION_SIGNING_KEY_ARN = process.env.SESSION_SIGNING_KEY_ARN;

for (const [name, value] of Object.entries({ AGENT_RUNTIME_ARN, DEMO_LOGIN_SECRET_ARN, SESSION_SIGNING_KEY_ARN })) {
  if (!value) {
    console.error(`${name} env var is required`);
    process.exit(1);
  }
}

const agentcore = new BedrockAgentCoreClient();
const secretsManager = new SecretsManagerClient();
async function loadSecret(arn) {
  const { SecretString } = await secretsManager.send(new GetSecretValueCommand({ SecretId: arn }));
  if (!SecretString) {
    console.error(`Secret ${arn} has no string value`);
    process.exit(1);
  }
  return SecretString;
}
const DEMO_LOGIN_SECRET = await loadSecret(DEMO_LOGIN_SECRET_ARN);
const SESSION_SIGNING_KEY = await loadSecret(SESSION_SIGNING_KEY_ARN);

// Session tokens are "<sessionId>.<HMAC>", signed with the key above. The browser gets one from
// /connect (after the login secret) and presents it on every chat request, so the login secret
// only travels once. The sessionId is a UUID, so splitting on the last "." is unambiguous.
function issueSessionToken(sessionId) {
  const signature = createHmac("sha256", SESSION_SIGNING_KEY).update(sessionId).digest("base64url");
  return `${sessionId}.${signature}`;
}
function verifySessionToken(token) {
  const dot = token.lastIndexOf(".");
  if (dot < 0) return null;
  const sessionId = token.slice(0, dot);
  const provided = Buffer.from(token.slice(dot + 1));
  const expected = Buffer.from(createHmac("sha256", SESSION_SIGNING_KEY).update(sessionId).digest("base64url"));
  if (provided.length !== expected.length || !timingSafeEqual(provided, expected)) return null;
  return sessionId;
}

const MAX_PROMPT_LENGTH = 100;

const app = express();
app.use(express.json());

app.use(express.static(path.join(import.meta.dirname, "static")));

// Require the demo login secret (sent in the request body). Constant-time comparison avoids
// leaking the secret through response timing.
function requireLoginSecret(req, res, next) {
  const provided = Buffer.from(req.body?.secret ?? "");
  const expected = Buffer.from(DEMO_LOGIN_SECRET);
  if (provided.length !== expected.length || !timingSafeEqual(provided, expected)) {
    return res.status(401).json({ error: "Invalid or missing login secret" });
  }
  next();
}

// Require a valid signed session token (set by /connect). Puts the sessionId on the request.
function requireSessionToken(req, res, next) {
  const sessionId = verifySessionToken(req.get("x-session-token") ?? "");
  if (!sessionId) {
    return res.status(401).json({ error: "Invalid or missing session token" });
  }
  req.sessionId = sessionId;
  next();
}

// Mint a fresh signed session token. Guarded by the login secret, so the browser only sends the
// secret here; afterwards it authenticates with the token. The token lives only in the browser's
// memory for the page view and is not persisted.
app.post("/connect", requireLoginSecret, (req, res) => {
  res.json({ sessionToken: issueSessionToken(randomUUID()) });
});

// Invoke the agent and stream its SSE response back to the browser as it arrives.
app.post("/api/chat", requireSessionToken, async (req, res) => {
  const { prompt } = req.body ?? {};
  const sessionId = req.sessionId;
  if (!prompt) {
    return res.status(400).json({ error: "Missing required field: 'prompt'" });
  }
  if (prompt.length > MAX_PROMPT_LENGTH) {
    return res.status(400).json({ error: `'prompt' must be at most ${MAX_PROMPT_LENGTH} characters` });
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
