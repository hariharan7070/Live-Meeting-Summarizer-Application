import { Sidebar } from "../components/Sidebar";
import { ResultsPanel } from "../components/ResultsPanel";
import { Waveform } from "../components/Waveform";
import { useAudioRecorder } from "../hooks/use-audio-recorder";
import { formatDuration } from "../lib/utils";
import { Mic, Square, Loader2, RefreshCw } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function Home() {
  const { status, timeElapsed, session, errorMessage, startRecording, stopRecording, reset } = useAudioRecorder();

  const isRecording = status === "recording";
  const isProcessing = status === "processing";
  const isCompleted = status === "completed" && session;

  return (
    <div className="flex h-screen w-full bg-background overflow-hidden">
      <Sidebar currentSessionId={session?.id} />

      <main className="flex-1 overflow-y-auto">
        <div className="min-h-full flex flex-col items-center justify-center p-6 md:p-12">
          <AnimatePresence mode="wait">

            {!isProcessing && !isCompleted && (
              <motion.div key="recorder" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.95 }}
                className="flex flex-col items-center space-y-12 w-full max-w-xl mx-auto"
              >
                <div className="text-center space-y-4">
                  <h1 className="text-4xl md:text-6xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-white/60">
                    Record a Meeting
                  </h1>
                  <p className="text-lg text-muted-foreground max-w-md mx-auto">
                    Capture high-quality audio and let AI generate accurate transcripts and actionable summaries.
                  </p>
                </div>

                <div className="relative flex flex-col items-center p-12 bg-card/30 backdrop-blur-2xl border border-border/40 rounded-[3rem] shadow-2xl w-full">
                  {errorMessage && (
                    <div className="absolute top-4 left-4 right-4 bg-destructive/20 border border-destructive/50 text-red-200 px-4 py-2 rounded-xl text-center text-sm">
                      {errorMessage}
                    </div>
                  )}

                  <div className="h-24 mb-8 w-full flex items-center justify-center">
                    <Waveform active={isRecording} />
                  </div>

                  <div className="relative group">
                    {isRecording && (
                      <div className="absolute -inset-4 bg-destructive/30 rounded-full blur-2xl animate-pulse" />
                    )}
                    <button
                      onClick={isRecording ? stopRecording : startRecording}
                      className={`relative z-10 flex items-center justify-center w-32 h-32 rounded-full border-4 shadow-xl transition-all duration-300 hover:scale-105 active:scale-95
                        ${isRecording
                          ? "bg-card border-destructive text-destructive"
                          : "bg-gradient-to-br from-primary to-accent border-transparent text-white shadow-primary/25 hover:shadow-primary/40"}`}
                    >
                      {isRecording ? <Square className="w-10 h-10 fill-current" /> : <Mic className="w-12 h-12" />}
                    </button>
                  </div>

                  <div className="mt-10 h-10 flex items-center justify-center">
                    {isRecording ? (
                      <div className="flex items-center gap-3">
                        <span className="relative flex h-3 w-3">
                          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-destructive opacity-75" />
                          <span className="relative inline-flex rounded-full h-3 w-3 bg-destructive" />
                        </span>
                        <span className="text-3xl font-mono font-medium text-foreground tracking-wider">
                          {formatDuration(timeElapsed)}
                        </span>
                      </div>
                    ) : (
                      <span className="text-muted-foreground font-medium uppercase tracking-widest text-sm">Click to Start</span>
                    )}
                  </div>
                </div>
              </motion.div>
            )}

            {isProcessing && (
              <motion.div key="processing" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }}
                className="flex flex-col items-center space-y-8"
              >
                <div className="relative w-32 h-32 flex items-center justify-center">
                  <div className="absolute inset-0 rounded-full border-4 border-primary/20" />
                  <div className="absolute inset-0 rounded-full border-4 border-primary border-t-transparent animate-spin" />
                  <Loader2 className="w-10 h-10 text-primary animate-pulse" />
                </div>
                <div className="text-center space-y-2">
                  <h2 className="text-2xl font-bold">Analyzing Meeting</h2>
                  <p className="text-muted-foreground">Transcribing audio and generating insights...</p>
                </div>
              </motion.div>
            )}

            {isCompleted && session && (
              <motion.div key="completed" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="w-full pb-20 pt-8">
                <div className="flex justify-between items-center mb-8 max-w-4xl mx-auto px-4">
                  <div>
                    <h2 className="text-3xl font-bold">Session Results</h2>
                    <p className="text-muted-foreground mt-1">Review your meeting insights</p>
                  </div>
                  <button onClick={reset}
                    className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-secondary/50 hover:bg-secondary border border-border/50 text-foreground transition-all">
                    <RefreshCw className="w-4 h-4" /> New Recording
                  </button>
                </div>
                <ResultsPanel session={session} />
              </motion.div>
            )}

          </AnimatePresence>
        </div>
      </main>
    </div>
  );
}
