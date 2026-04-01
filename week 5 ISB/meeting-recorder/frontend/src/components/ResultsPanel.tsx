import { useState } from "react";
import type { RecordingSession } from "../types";
import ReactMarkdown from "react-markdown";
import { format } from "date-fns";
import { Clock, Users, Bot, ListChecks, MessageSquare, FileText } from "lucide-react";
import { motion } from "framer-motion";
import { cn, formatMs } from "../lib/utils";

export function ResultsPanel({ session }: { session: RecordingSession }) {
  const [tab, setTab] = useState<"summary" | "diarization" | "transcript">("summary");

  const duration =
    session.stoppedAt && session.createdAt
      ? formatMs(new Date(session.stoppedAt).getTime() - new Date(session.createdAt).getTime())
      : "—";

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6 px-4">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          { icon: <Clock className="w-5 h-5 text-primary" />, label: "Duration", value: duration },
          { icon: <Users className="w-5 h-5 text-accent" />, label: "Speakers", value: `${session.speakerCount ?? "?"} Detected` },
          { icon: <Bot className="w-5 h-5 text-emerald-400" />, label: "Status", value: "Analyzed", valueClass: "text-emerald-400" },
        ].map(({ icon, label, value, valueClass }) => (
          <div key={label} className="bg-card/50 backdrop-blur-md border border-border/50 rounded-2xl p-5">
            <div className="flex items-center gap-3 text-muted-foreground mb-2">
              {icon}
              <span className="font-medium text-sm">{label}</span>
            </div>
            <p className={cn("text-2xl font-bold text-foreground", valueClass)}>{value}</p>
          </div>
        ))}
      </div>

      <div className="bg-card/80 backdrop-blur-xl border border-border/60 rounded-3xl overflow-hidden shadow-xl">
        <div className="flex border-b border-border/50">
          {([
            { key: "summary", icon: <ListChecks className="w-4 h-4" />, label: "AI Summary" },
            { key: "diarization", icon: <MessageSquare className="w-4 h-4" />, label: "Speaker Analysis" },
            { key: "transcript", icon: <FileText className="w-4 h-4" />, label: "Raw Transcript" },
          ] as const).map(({ key, icon, label }) => (
            <button
              key={key}
              onClick={() => setTab(key)}
              className={cn(
                "flex items-center gap-2 px-6 py-4 font-medium transition-all relative whitespace-nowrap",
                tab === key ? "text-primary" : "text-muted-foreground hover:text-foreground hover:bg-secondary/30"
              )}
            >
              {icon}{label}
              {tab === key && (
                <motion.div layoutId="tab-indicator" className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
              )}
            </button>
          ))}
        </div>

        <div className="p-6 md:p-8 min-h-[400px]">
          {tab === "summary" && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="prose prose-invert max-w-none">
              {session.summary
                ? <ReactMarkdown>{session.summary}</ReactMarkdown>
                : <p className="text-muted-foreground italic">No summary generated.</p>}
            </motion.div>
          )}
          {tab === "diarization" && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
              {session.diarization
                ? <div className="whitespace-pre-wrap text-foreground/90 font-medium leading-relaxed bg-background/50 p-6 rounded-2xl border border-border/30">{session.diarization}</div>
                : <p className="text-muted-foreground italic">No speaker analysis available.</p>}
            </motion.div>
          )}
          {tab === "transcript" && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
              {session.transcription
                ? <div className="whitespace-pre-wrap text-muted-foreground leading-relaxed bg-background/30 p-6 rounded-2xl border border-border/30 font-mono text-sm">{session.transcription}</div>
                : <p className="text-muted-foreground italic">No transcription available.</p>}
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
