import { useQuery } from "@tanstack/react-query";
import type { RecordingSession } from "../types";
import { useRoute, Link } from "wouter";
import { Sidebar } from "../components/Sidebar";
import { ResultsPanel } from "../components/ResultsPanel";
import { Loader2, ArrowLeft, AlertCircle } from "lucide-react";
import { motion } from "framer-motion";

async function fetchSession(id: number): Promise<RecordingSession> {
  const res = await fetch(`/api/recording/${id}`);
  if (!res.ok) throw new Error("Session not found");
  return res.json();
}

export default function SessionView() {
  const [, params] = useRoute("/session/:id");
  const sessionId = params?.id ? parseInt(params.id, 10) : 0;

  const { data: session, isLoading, isError } = useQuery({
    queryKey: ["recording-session", sessionId],
    queryFn: () => fetchSession(sessionId),
    enabled: !!sessionId,
    refetchInterval: (query) => query.state.data?.status === "processing" ? 2000 : false,
  });

  return (
    <div className="flex h-screen w-full bg-background overflow-hidden">
      <Sidebar currentSessionId={sessionId} />

      <main className="flex-1 overflow-y-auto p-6 md:p-12">
        <div className="max-w-4xl mx-auto mb-8">
          <Link href="/" className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors mb-6">
            <ArrowLeft className="w-4 h-4" /> Back to Recorder
          </Link>
        </div>

        {isLoading ? (
          <div className="flex flex-col items-center justify-center h-[50vh]">
            <Loader2 className="w-8 h-8 animate-spin text-primary mb-4" />
            <p className="text-muted-foreground">Loading session...</p>
          </div>
        ) : isError || !session ? (
          <div className="flex flex-col items-center justify-center h-[50vh] text-center">
            <div className="w-16 h-16 rounded-full bg-destructive/10 flex items-center justify-center mb-4">
              <AlertCircle className="w-8 h-8 text-destructive" />
            </div>
            <h3 className="text-xl font-bold">Session Not Found</h3>
            <p className="text-muted-foreground mt-2">This recording doesn't exist or was deleted.</p>
          </div>
        ) : session.status === "processing" ? (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-col items-center justify-center h-[40vh] space-y-6">
            <div className="relative w-24 h-24">
              <div className="absolute inset-0 rounded-full border-4 border-primary/20" />
              <div className="absolute inset-0 rounded-full border-4 border-primary border-t-transparent animate-spin" />
            </div>
            <div className="text-center">
              <h3 className="text-xl font-bold">AI is working...</h3>
              <p className="text-muted-foreground mt-2 max-w-sm">Generating transcript, detecting speakers, creating summary. Page auto-updates.</p>
            </div>
          </motion.div>
        ) : (
          <div className="pb-20">
            <div className="max-w-4xl mx-auto mb-8">
              <h2 className="text-3xl font-bold">Session #{session.id}</h2>
            </div>
            <ResultsPanel session={session} />
          </div>
        )}
      </main>
    </div>
  );
}
