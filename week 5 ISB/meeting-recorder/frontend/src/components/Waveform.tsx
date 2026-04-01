import { motion } from "framer-motion";

const bars = Array.from({ length: 24 }).map((_, i) => ({
  id: i,
  baseHeight: 10 + Math.random() * 20,
  activeHeight: 20 + Math.random() * 40,
  delay: Math.random() * 0.5,
}));

export function Waveform({ active }: { active: boolean }) {
  return (
    <div className="flex items-center justify-center gap-1 h-20 w-full">
      {bars.map((bar) => (
        <motion.div
          key={bar.id}
          className="w-1.5 rounded-full bg-destructive"
          animate={{
            height: active ? [bar.baseHeight, bar.activeHeight, bar.baseHeight] : 4,
            opacity: active ? [0.6, 1, 0.6] : 0.3,
          }}
          transition={{
            duration: 0.8 + Math.random() * 0.5,
            repeat: active ? Infinity : 0,
            delay: active ? bar.delay : 0,
            ease: "easeInOut",
          }}
        />
      ))}
    </div>
  );
}
