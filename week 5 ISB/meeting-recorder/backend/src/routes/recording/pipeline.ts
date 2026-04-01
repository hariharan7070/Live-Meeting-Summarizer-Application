import { db, recordingSessions } from "../../db.js";
import { eq } from "drizzle-orm";
import OpenAI from "openai";
import "dotenv/config";

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

export interface PipelineJob {
  sessionId: number;
  audioChunks: Buffer[];
}

const queue: PipelineJob[] = [];
let isRunning = false;

export function enqueuePipelineJob(job: PipelineJob): void {
  queue.push(job);
  if (!isRunning) {
    processNext().catch((err) => {
      console.error("[Pipeline] Fatal error:", err);
    });
  }
}

async function processNext(): Promise<void> {
  if (queue.length === 0) {
    isRunning = false;
    return;
  }
  isRunning = true;
  const job = queue.shift()!;
  try {
    await runPipeline(job);
  } catch (err) {
    console.error(`[Pipeline] Job ${job.sessionId} failed:`, err);
    await db
      .update(recordingSessions)
      .set({
        status: "error",
        errorMessage: err instanceof Error ? err.message : String(err),
      })
      .where(eq(recordingSessions.id, job.sessionId));
  }
  setImmediate(() => {
    processNext().catch((err) => console.error("[Pipeline] Error in next:", err));
  });
}

async function runPipeline(job: PipelineJob): Promise<void> {
  const { sessionId, audioChunks } = job;
  console.log(`[Pipeline] Session ${sessionId}: starting`);

  await db
    .update(recordingSessions)
    .set({ status: "processing" })
    .where(eq(recordingSessions.id, sessionId));

  const combinedBuffer = audioChunks.length > 0 ? Buffer.concat(audioChunks) : Buffer.alloc(0);

  let transcription = "";
  if (combinedBuffer.length > 0) {
    try {
      const { toFile } = await import("openai");
      const audioFile = await toFile(combinedBuffer, "audio.webm", { type: "audio/webm" });
      const result = await openai.audio.transcriptions.create({
        model: "whisper-1",
        file: audioFile,
        response_format: "text",
      });
      transcription = typeof result === "string" ? result : (result as any).text ?? "";
      console.log(`[Pipeline] Session ${sessionId}: transcription done (${transcription.length} chars)`);
    } catch (err) {
      console.warn(`[Pipeline] Session ${sessionId}: transcription failed, continuing empty`, err);
    }
  }

  await db
    .update(recordingSessions)
    .set({ transcription })
    .where(eq(recordingSessions.id, sessionId));

  const diarization = await runDiarization(transcription);
  await db
    .update(recordingSessions)
    .set({ diarization, speakerCount: countSpeakers(diarization) })
    .where(eq(recordingSessions.id, sessionId));

  const summary = await runSummarization(transcription, diarization);
  await db
    .update(recordingSessions)
    .set({ summary, status: "completed", completedAt: new Date() })
    .where(eq(recordingSessions.id, sessionId));

  console.log(`[Pipeline] Session ${sessionId}: completed`);
}

async function runDiarization(transcription: string): Promise<string> {
  if (!transcription.trim()) return "No speech detected.";
  const res = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [{
      role: "user",
      content: `You are a speaker diarization system. Given this meeting transcription, identify and label different speakers as Speaker 1, Speaker 2, etc. based on topic changes, perspective shifts, and natural conversation flow. Format the output as labeled segments.\n\nTranscription:\n${transcription}\n\nOutput the diarized transcript with speaker labels. If it seems like a monologue, label it as just Speaker 1.`,
    }],
  });
  return res.choices[0]?.message?.content ?? "Diarization unavailable.";
}

async function runSummarization(transcription: string, diarization: string): Promise<string> {
  if (!transcription.trim()) return "No content to summarize.";
  const res = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [{
      role: "user",
      content: `You are a meeting summarization assistant. Provide a structured summary with:\n\n1. **Meeting Overview** – 2-3 sentence overview\n2. **Key Points** – Bullet points of important topics\n3. **Action Items** – Any tasks or follow-ups\n4. **Participants** – Speaker count and contributions\n\nTranscription:\n${transcription}\n\nSpeaker Analysis:\n${diarization}\n\nProvide a clear, concise summary:`,
    }],
  });
  return res.choices[0]?.message?.content ?? "Summary unavailable.";
}

function countSpeakers(diarization: string): number {
  const matches = diarization.match(/Speaker\s+\d+/gi);
  if (!matches) return 1;
  return new Set(matches.map((s) => s.toLowerCase())).size;
}
