import { Router } from "express";
import { db, recordingSessions } from "../../db.js";
import { eq, desc } from "drizzle-orm";
import { enqueuePipelineJob } from "./pipeline.js";
import { initSession, addChunk, clearSession, hasSession } from "./store.js";

const router = Router();

function parseId(param: string | string[] | undefined): number | null {
  const raw = Array.isArray(param) ? param[0] : param;
  if (!raw) return null;
  const n = parseInt(raw, 10);
  return isNaN(n) ? null : n;
}

router.post("/recording/start", async (_req, res) => {
  const [session] = await db
    .insert(recordingSessions)
    .values({ status: "recording" })
    .returning();
  initSession(session.id);
  console.log(`[API] Started session ${session.id}`);
  res.status(201).json(session);
});

router.post("/recording/:sessionId/chunk", async (req, res) => {
  const sessionId = parseId(req.params["sessionId"]);
  if (!sessionId) { res.status(400).json({ error: "Invalid session ID" }); return; }

  const [session] = await db.select().from(recordingSessions).where(eq(recordingSessions.id, sessionId));
  if (!session) { res.status(404).json({ error: "Session not found" }); return; }
  if (session.status !== "recording") { res.status(409).json({ error: `Session is not recording (${session.status})` }); return; }

  const { audioBase64 } = req.body as { audioBase64?: string };
  if (!audioBase64) { res.status(400).json({ error: "audioBase64 is required" }); return; }

  const chunk = Buffer.from(audioBase64, "base64");
  if (!hasSession(sessionId)) initSession(sessionId);
  const chunkIndex = addChunk(sessionId, chunk);

  res.json({ received: true, chunkIndex });
});

router.post("/recording/:sessionId/stop", async (req, res) => {
  const sessionId = parseId(req.params["sessionId"]);
  if (!sessionId) { res.status(400).json({ error: "Invalid session ID" }); return; }

  const [session] = await db.select().from(recordingSessions).where(eq(recordingSessions.id, sessionId));
  if (!session) { res.status(404).json({ error: "Session not found" }); return; }
  if (session.status !== "recording") { res.status(409).json({ error: `Session is not recording (${session.status})` }); return; }

  const audioChunks = clearSession(sessionId);
  const [updated] = await db
    .update(recordingSessions)
    .set({ status: "processing", stoppedAt: new Date() })
    .where(eq(recordingSessions.id, sessionId))
    .returning();

  console.log(`[API] Stopped session ${sessionId}, ${audioChunks.length} chunks, starting pipeline`);
  enqueuePipelineJob({ sessionId, audioChunks });

  res.json(updated);
});

router.get("/recording/:sessionId", async (req, res) => {
  const sessionId = parseId(req.params["sessionId"]);
  if (!sessionId) { res.status(400).json({ error: "Invalid session ID" }); return; }

  const [session] = await db.select().from(recordingSessions).where(eq(recordingSessions.id, sessionId));
  if (!session) { res.status(404).json({ error: "Session not found" }); return; }

  res.json(session);
});

router.get("/recording", async (_req, res) => {
  const sessions = await db.select().from(recordingSessions).orderBy(desc(recordingSessions.createdAt));
  res.json(sessions);
});

export default router;
