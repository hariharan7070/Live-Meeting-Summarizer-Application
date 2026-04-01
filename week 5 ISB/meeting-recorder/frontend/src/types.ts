export interface RecordingSession {
  id: number;
  status: "idle" | "recording" | "processing" | "completed" | "error";
  transcription: string | null;
  diarization: string | null;
  summary: string | null;
  speakerCount: number | null;
  createdAt: string;
  stoppedAt: string | null;
  completedAt: string | null;
  errorMessage: string | null;
}
