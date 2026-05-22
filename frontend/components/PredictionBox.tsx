interface PredictionProps {
  winner?: string;
  bet?: string;
  confidence?: number;
  oddsHome?: number;
  oddsAway?: number;
  oddsDraw?: number;
  edge?: string;
}

export default function PredictionBox({ winner, confidence, edge }: PredictionProps) {
  if (!winner) return null;

  const confidenceLabel = confidence && confidence >= 75 ? "High Confidence"
    : confidence && confidence >= 55 ? "Moderate Confidence"
    : "Close Call";

  const barColor = confidence && confidence >= 75 ? "bg-success"
    : confidence && confidence >= 55 ? "bg-brand"
    : "bg-accent-warm";

  return (
    <div className="bg-brand-light/60 border border-brand/15 rounded-xl overflow-hidden my-8">
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center gap-2 mb-5">
          <div className="w-8 h-8 rounded-lg bg-brand/10 flex items-center justify-center">
            <svg className="w-4 h-4 text-brand" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <div>
            <h3 className="font-display font-bold text-ink text-sm">What Our AI Thinks</h3>
            <p className="text-xs text-ink-secondary">Based on form, stats, and historical patterns</p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          {/* Pick */}
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-ink-secondary mb-1">Our Pick</p>
            <p className="font-display font-bold text-xl text-ink">{winner}</p>
          </div>

          {/* Confidence */}
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-ink-secondary mb-1">Confidence Level</p>
            <div className="flex items-center gap-3">
              <div className="flex-1 h-2.5 bg-white rounded-full overflow-hidden">
                <div className={`h-full rounded-full ${barColor} transition-all`} style={{ width: `${confidence || 50}%` }} />
              </div>
              <span className="text-sm font-semibold text-ink-secondary whitespace-nowrap">{confidenceLabel}</span>
            </div>
          </div>
        </div>

        {/* Edge — written as editorial insight, not betting edge */}
        {edge && (
          <div className="mt-5 pt-5 border-t border-brand/10">
            <p className="text-xs font-semibold uppercase tracking-wider text-ink-secondary mb-2">The Key Insight</p>
            <p className="text-sm text-ink/80 leading-relaxed">{edge}</p>
          </div>
        )}
      </div>
    </div>
  );
}
