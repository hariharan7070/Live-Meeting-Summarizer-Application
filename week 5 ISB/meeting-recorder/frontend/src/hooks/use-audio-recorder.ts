import { useState, useRef, useEffect, useCallback } from "react";
import type { RecordingSession } from "../types";
import { useQueryClient } from "@tanstack/react-query";

export type RecorderStatus = "idle" | "recording" | "processing" | "completed" | "error";

export function useAudioRecorder() {
  const [status, setStatus] = useState<RecorderStatus>("idle");
  const [timeElapsed, setTimeElapsed] = useState(0);
  const [session, setSession] = useState<RecordingSession | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const timerRef = useRef<number | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const sessionIdRef = useRef<number | null>(null);
  const queryClient = useQueryClient();

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      streamRef.current?.getTracks().forEach((t) => t.stop());
    };
  }, []);

  const startRecording = useCallback(async () => {
    try {
      setErrorMessage(null);
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const startRes = await fetch("/api/recording/start", { method: "POST" });
      if (!startRes.ok) throw new Error("Failed to start recording session");
      const sessionData: RecordingSession = await startRes.json();
      sessionIdRef.current = sessionData.id;
      setSession(sessionData);

      const options = MediaRecorder.isTypeSupported("audio/webm")
        ? { mimeType: "audio/webm" }
        : undefined;
      const mediaRecorder = new MediaRecorder(stream, options);
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = async (e) => {
        if (e.data.size > 0 && sessionIdRef.current) {
          const reader = new FileReader();
          reader.readAsDataURL(e.data);
          reader.onloadend = async () => {
            const base64data = (reader.result as string).split(",")[1];
            try {
              await fetch(`/api/recording/${sessionIdRef.current}/chunk`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                  audioBase64: base64data,
                  format: mediaRecorder.mimeType.includes("webm") ? "webm" : "mp4",
                }),
              });
            } catch (err) {
              console.error("Failed to upload chunk", err);
            }
          };
        }
      };

      mediaRecorder.start(1000);
      setStatus("recording");
      setTimeElapsed(0);
      timerRef.current = window.setInterval(() => setTimeElapsed((p) => p + 1), 1000);
      queryClient.invalidateQueries({ queryKey: ["recording-sessions"] });
    } catch (err) {
      setStatus("error");
      setErrorMessage(err instanceof Error ? err.message : "Microphone access denied.");
    }
  }, [queryClient]);

  const stopRecording = useCallback(async () => {
    if (!mediaRecorderRef.current || !sessionIdRef.current) return;
    mediaRecorderRef.current.stop();
    streamRef.current?.getTracks().forEach((t) => t.stop());
    if (timerRef.current) clearInterval(timerRef.current);
    setStatus("processing");

    try {
      const res = await fetch(`/api/recording/${sessionIdRef.current}/stop`, { method: "POST" });
      if (!res.ok) throw new Error("Failed to stop recording");
      const updated: RecordingSession = await res.json();
      setSession(updated);
      pollStatus(sessionIdRef.current!);
      queryClient.invalidateQueries({ queryKey: ["recording-sessions"] });
    } catch (err) {
      setStatus("error");
      setErrorMessage("Error stopping recording.");
    }
  }, [queryClient]);

  const pollStatus = useCallback((id: number) => {
    const interval = window.setInterval(async () => {
      try {
        const res = await fetch(`/api/recording/${id}`);
        const data: RecordingSession = await res.json();
        if (data.status === "completed" || data.status === "error") {
          clearInterval(interval);
          setSession(data);
          setStatus(data.status);
          if (data.status === "error") setErrorMessage(data.errorMessage || "Processing failed.");
          queryClient.invalidateQueries({ queryKey: ["recording-sessions"] });
        }
      } catch (err) {
        console.error("Polling error", err);
      }
    }, 2000);
  }, [queryClient]);

  const reset = useCallback(() => {
    setStatus("idle");
    setSession(null);
    setTimeElapsed(0);
    setErrorMessage(null);
    sessionIdRef.current = null;
  }, []);

  return { status, timeElapsed, session, errorMessage, startRecording, stopRecording, reset };
}
