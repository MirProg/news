"use client";
import { useState, useEffect } from "react";

interface Score {
  sport: string;
  home: string;
  away: string;
  homeScore: string;
  awayScore: string;
  status: string;
  state: string;
}

const SPORT_COLORS: Record<string, string> = {
  football: "#16A34A",
  basketball: "#EA580C",
  cricket: "#2563EB",
  tennis: "#CA8A04",
  mma: "#DC2626",
  f1: "#E11D48",
  rugby: "#7C3AED",
  nfl: "#0369A1",
};

export default function LiveTicker() {
  const [scores, setScores] = useState<Score[]>([]);

  useEffect(() => {
    async function fetchScores() {
      try {
        const res = await fetch("/api/scores/live");
        if (res.ok) {
          const data = await res.json();
          setScores(data.scores || []);
        }
      } catch { /* silent */ }
    }
    fetchScores();
    const interval = setInterval(fetchScores, 60000);
    return () => clearInterval(interval);
  }, []);

  if (scores.length === 0) {
    return (
      <div className="bg-surface-dark h-9 flex items-center justify-center">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-brand animate-pulse-dot" />
          <span className="text-[11px] uppercase tracking-widest text-ink-light font-semibold">
            Oracle Sports Live
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-surface-dark h-9 overflow-hidden">
      <div className="flex items-center h-full">
        <div className="flex-shrink-0 px-4 flex items-center gap-2 border-r border-white/10 h-full">
          <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse-dot" />
          <span className="text-[11px] uppercase tracking-widest text-white/60 font-semibold hidden sm:inline">
            Live
          </span>
        </div>
        <div className="flex-1 overflow-hidden">
          <div className="flex animate-ticker-scroll whitespace-nowrap">
            {[...scores, ...scores].map((s, i) => (
              <span key={i} className="inline-flex items-center px-5 text-xs">
                <span
                  className="w-1.5 h-1.5 rounded-full mr-2"
                  style={{ background: SPORT_COLORS[s.sport] || '#666' }}
                />
                <span className="text-white font-semibold">{s.home}</span>
                <span className="text-accent-warm mx-2 font-bold">{s.homeScore} - {s.awayScore}</span>
                <span className="text-white font-semibold">{s.away}</span>
                <span className="text-white/40 ml-2 text-[10px]">{s.status}</span>
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
