import { drizzle } from "drizzle-orm/node-postgres";
import { pgTable, serial, text, timestamp, integer } from "drizzle-orm/pg-core";
import pg from "pg";
import "dotenv/config";

const { Pool } = pg;

if (!process.env.DATABASE_URL) {
  throw new Error("DATABASE_URL must be set in .env");
}

export const pool = new Pool({ connectionString: process.env.DATABASE_URL });
export const db = drizzle(pool);

export const recordingSessions = pgTable("recording_sessions", {
  id: serial("id").primaryKey(),
  status: text("status").notNull().default("idle"),
  transcription: text("transcription"),
  diarization: text("diarization"),
  summary: text("summary"),
  speakerCount: integer("speaker_count"),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  stoppedAt: timestamp("stopped_at", { withTimezone: true }),
  completedAt: timestamp("completed_at", { withTimezone: true }),
  errorMessage: text("error_message"),
});

export type RecordingSession = typeof recordingSessions.$inferSelect;
