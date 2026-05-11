import { Router } from "express";
import { invokeAgent } from "./ac_client.js";

const router = Router();

router.get("/app/callback", async (req, res) => {
  const sessionId = decodeURIComponent(req.query.session_id || "");
  console.log(`> callback session_id=${sessionId}`);
  try {
    await invokeAgent({ cmd: "completeAuth", session_id: sessionId });
  } catch (e) {
    console.error("completeAuth error", e);
  }
  res.redirect("/app");
});

export default router;
