interface AftermathProps { html: string; correct: boolean | null; }

export default function AftermathSection({ html, correct }: AftermathProps) {
  if (!html) return null;

  return (
    <div className={`my-10 rounded-xl overflow-hidden border ${correct ? 'border-success/30 bg-success/5' : 'border-border bg-surface-alt'}`}>
      <div className="p-6 sm:p-8">
        <div className="flex items-center gap-3 mb-5">
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${correct ? 'bg-success/15 text-success' : 'bg-ink-light/15 text-ink-secondary'}`}>
            {correct ? (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
            ) : (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
            )}
          </div>
          <div>
            <h2 className="font-display font-bold text-xl text-ink">After the Final Whistle</h2>
            <p className="text-xs text-ink-secondary">
              {correct ? "Our AI got this one right." : "Our AI missed this one. Here's what happened."}
            </p>
          </div>
        </div>
        <div className="article-body prose max-w-none text-ink/85" dangerouslySetInnerHTML={{ __html: html }} />
      </div>
    </div>
  );
}
