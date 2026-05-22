"use client";
import { useState, useEffect } from "react";
import Link from "next/link";

interface LeaderboardItem {
  id: number; sport: string; headline: string; confidence_pct: number;
  prediction_winner: string; resolved: number; prediction_correct: number | null;
}

interface OracleRecord { total: number; correct: number; pct: number; }

export default function ConfidenceLeaderboard() {
  const [data, setData] = useState<{ predictions: LeaderboardItem[], record: OracleRecord } | null>(null);

  useEffect(() => {
    async function f() { try { const r = await fetch("/api/meta/leaderboard"); if (r.ok) setData(await r.json()); } catch {} }
    f();
  }, []);

  if (!data) return null;

  return (
    <div className="bg-surface border border-border rounded-xl overflow-hidden">
      <div className="p-5 border-b border-border">
        <h3 className="font-display font-bold text-ink text-lg">AI Track Record</h3>
        <div className="mt-3 flex items-center gap-4">
          <div className="flex-1 bg-surface-alt rounded-lg p-3 text-center">
            <p className="font-display text-2xl font-bold text-brand">{data.record.pct}%</p>
            <p className="text-[10px] text-ink-light uppercase tracking-wider font-semibold">Accuracy</p>
          </div>
          <div className="flex-1 bg-surface-alt rounded-lg p-3 text-center">
            <p className="font-display text-2xl font-bold text-ink">{data.record.correct}<span className="text-ink-light text-sm">/{data.record.total}</span></p>
            <p className="text-[10px] text-ink-light uppercase tracking-wider font-semibold">Correct</p>
          </div>
        </div>
      </div>

      <div className="divide-y divide-border">
        {data.predictions.map((p) => (
          <Link key={p.id} href={`/article/${p.id}`} className="block p-4 hover:bg-surface-alt transition-colors group">
            <p className="font-display font-bold text-sm text-ink mb-1 group-hover:text-brand transition-colors line-clamp-2 leading-snug">
              {p.headline}
            </p>
            <div className="flex items-center justify-between text-xs mt-2">
              <span className="text-ink-secondary">Pick: <span className="font-semibold text-ink">{p.prediction_winner}</span></span>
              {p.resolved === 1 ? (
                p.prediction_correct === 1 ? (
                  <span className="text-success font-semibold text-[10px] bg-success/10 px-2 py-0.5 rounded-full">Correct</span>
                ) : (
                  <span className="text-danger font-semibold text-[10px] bg-danger/10 px-2 py-0.5 rounded-full">Missed</span>
                )
              ) : (
                <span className="text-ink-light text-[10px] bg-surface-alt px-2 py-0.5 rounded-full">Pending</span>
              )}
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
