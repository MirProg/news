interface SourceBadgesProps { domains: string[]; }

export default function SourceBadges({ domains }: SourceBadgesProps) {
  if (!domains || domains.length === 0) return null;
  const unique = Array.from(new Set(domains.filter(Boolean)));

  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="text-xs text-ink-light font-semibold mr-1">Sources:</span>
      {unique.map((d, i) => (
        <span key={i} className="inline-flex items-center px-2.5 py-1 text-[11px] font-medium text-ink-secondary bg-surface-alt border border-border rounded-full">{d}</span>
      ))}
    </div>
  );
}
