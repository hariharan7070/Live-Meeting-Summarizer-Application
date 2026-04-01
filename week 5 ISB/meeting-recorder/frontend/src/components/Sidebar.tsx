import { useQuery } from "@tanstack/react-query";
import type { RecordingSession } from "../types";
import { format } from "date-fns";
import { Mic, FileAudio, Loader2, AlertCircle, CheckCircle2 } from "lucide-react";
import { cn } from "../lib/utils";
import { Link, useLocation } from "wouter";

async function fetchSessions(): Promise<RecordingSession[]> {
  const res = await fetch("/api/recording");
  return res.json();
}

export function Sidebar({ currentSessionId }: { currentSessionId?: number | null }) {
  const { data: sessions, isLoading } = useQuery({
    queryKey: ["recording-sessions"],
    queryFn: fetchSessions,
    refetchInterval: 5000,
  });
  const [location] = useLocation();

  return (
    <div className="w-72 border-r border-border/50 bg-card/50 backdrop-blur-xl h-full flex flex-col shrink-0">
      <div className="p-6 border-b border-border/50 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-primary/20 flex items-center justify-center border border-primary/30">
          <Mic className="w-5 h-5 text-primary" />
        </div>
        <div>
          <h2 className="font-bold text-lg text-foreground" style={{ fontFamily: "var(--font-display)" }}>MeetRecord</h2>
          <p className="text-xs text-muted-foreground">AI Powered Summaries</p>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground px-2">Recent Sessions</h3>

        {isLoading ? (
          <div className="flex justify-center p-8"><Loader2 className="w-6 h-6 animate-spin text-primary/50" /></div>
        ) : !sessions?.length ? (
          <div className="text-center p-6 bg-background/50 rounded-2xl border border-dashed border-border/50">
            <FileAudio className="w-8 h-8 text-muted-foreground/50 mx-auto mb-2" />
            <p className="text-sm text-muted-foreground">No recordings yet.</p>
          </div>
        ) : (
          sessions.map((s) => {
            const isActive = currentSessionId === s.id || location === `/session/${s.id}`;
            return (
              <Link key={s.id} href={`/session/${s.id}`}
                className={cn(
                  "block p-4 rounded-2xl border transition-all duration-200",
                  isActive
                    ? "bg-primary/10 border-primary/30 shadow-md"
                    : "bg-background/40 border-border/50 hover:bg-card hover:border-border"
                )}
              >
                <div className="flex justify-between items-start mb-1">
                  <span className="text-sm font-medium text-foreground">Session #{s.id}</span>
                  <StatusBadge status={s.status} />
                </div>
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>{format(new Date(s.createdAt), "MMM d, h:mm a")}</span>
                  {(s.speakerCount ?? 0) > 0 && (
                    <span className="bg-secondary/80 px-2 py-0.5 rounded-full">
                      {s.speakerCount} {s.speakerCount === 1 ? "Speaker" : "Speakers"}
                    </span>
                  )}
                </div>
              </Link>
            );
          })
        )}
      </div>

      <div className="p-4 border-t border-border/50">
        <Link href="/" className="flex items-center justify-center w-full py-3 rounded-xl bg-secondary text-secondary-foreground font-medium hover:bg-secondary/80 transition-colors">
          New Recording
        </Link>
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const base = "flex items-center gap-1.5 text-[10px] uppercase font-bold tracking-wider px-2 py-1 rounded-full border";
  switch (status) {
    case "recording":
      return <span className={cn(base, "text-destructive bg-destructive/10 border-destructive/20 animate-pulse")}><span className="w-1.5 h-1.5 rounded-full bg-destructive" />Live</span>;
    case "processing":
      return <span className={cn(base, "text-primary bg-primary/10 border-primary/20")}><Loader2 className="w-3 h-3 animate-spin" />Processing</span>;
    case "completed":
      return <span className={cn(base, "text-emerald-500 bg-emerald-500/10 border-emerald-500/20")}><CheckCircle2 className="w-3 h-3" />Done</span>;
    case "error":
      return <span className={cn(base, "text-red-400 bg-red-400/10 border-red-400/20")}><AlertCircle className="w-3 h-3" />Failed</span>;
    default:
      return null;
  }
}
