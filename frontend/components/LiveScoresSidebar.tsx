"use client";
import { useState, useEffect } from "react";

interface Match {
  sport: string; home: string; away: string;
  homeAbbr: string; awayAbbr: string; startTime: string;
}

const SPORT_DOT: Record<string, string> = {
  football: "#16A34A", basketball: "#EA580C", cricket: "#2563EB",
  tennis: "#CA8A04", mma: "#DC2626", f1: "#E11D48", rugby: "#7C3AED", nfl: "#0369A1",
};

export default function LiveScoresSidebar() {
  const [upcoming, setUpcoming] = useState<Match[]>([]);

  useEffect(() => {
    async function f() { try { const r = await fetch("/api/scores/upcoming"); if (r.ok) { const d = await r.json(); setUpcoming(d.matches?.slice(0, 6) || []); } } catch {} }
    f();
  }, []);

  if (upcoming.length === 0) return null;

  return (
    <div className="bg-surface border border-border rounded-xl overflow-hidden">
      <div className="p-5 border-b border-border">
        <h3 className="font-display font-bold text-ink text-lg">Coming Up</h3>
        <p className="text-xs text-ink-light mt-0.5">Next 48 hours</p>
      </div>
      <div className="divide-y divide-border">
        {upcoming.map((m, i) => {
          const d = new Date(m.startTime);
          return (
            <div key={i} className="p-4 hover:bg-surface-alt transition-colors">
              <div className="flex items-center justify-between mb-2">
                <span className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full" style={{ background: SPORT_DOT[m.sport] || '#888' }} />
                  <span className="text-[10px] uppercase tracking-wider text-ink-light font-bold">{m.sport}</span>
                </span>
                <span className="text-[10px] text-ink-light font-mono">
                  {d.toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric' })} · {d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
              <p className="text-sm font-semibold text-ink">{m.home} <span className="text-ink-light font-normal">vs</span> {m.away}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
