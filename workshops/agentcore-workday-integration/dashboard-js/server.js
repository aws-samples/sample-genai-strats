import "dotenv/config";
import express from "express";
import cors from "cors";
import { fileURLToPath } from "url";
import { dirname, join } from "path";
import callbackRouter from "./callback_router.js";
import { initAgent, handleMessage } from "./chat_manager.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
const PORT = process.env.PORT || 8081;

const app = express();

app.use((req, res, next) => {
  const host = (req.headers["host"] || "").split(":")[0];
  const isLocal = ["localhost", "127.0.0.1", "0.0.0.0"].includes(host);
  req.publicScheme = isLocal ? "http" : "https";
  next();
});

app.use(cors());
app.use(express.json());
app.use("/app", express.static(join(__dirname, "static")));

app.use(callbackRouter);

app.get("/", (req, res) => res.redirect("/app"));
app.get("/app", (req, res) => res.sendFile(join(__dirname, "static", "index.html")));

app.post("/app/api/init", async (req, res) => {
  const callbackUrl = `${req.publicScheme}://${req.headers["host"]}/app/callback`;
  console.log(`> init callbackUrl=${callbackUrl}`);
  try {
    const response = await initAgent(callbackUrl);
    return res.json(response);
  } catch (e) {
    console.error("init error", e);
    return res.status(500).json({ error: e.message });
  }
});

app.post("/app/api/chat", async (req, res) => {
  const { message } = req.body;
  console.log(`> chat message=${message}`);
  try {
    const response = await handleMessage(message);
    return res.json({ response });
  } catch (e) {
    console.error("chat error", e);
    return res.status(500).json({ error: e.message });
  }
});

const WORKSHOP_APP_CLOUDFRONT_DOMAIN = process.env.WORKSHOP_APP_CLOUDFRONT_DOMAIN;
app.listen(PORT, "0.0.0.0", () => {
  console.log(`> dashboard listening on http://localhost:${PORT}/app`);
  if (WORKSHOP_APP_CLOUDFRONT_DOMAIN){
    console.log(`> dashboard listening on https://${WORKSHOP_APP_CLOUDFRONT_DOMAIN}/app`);
  }
});
