import React from 'react';

async function getNewsWire() {
  try {
    const res = await fetch("http://localhost:4000/api/articles/news?limit=8", { next: { revalidate: 60 } });
    if (!res.ok) return { news: [] };
    return res.json();
  } catch {
    return { news: [] };
  }
}

export default async function NewsWire() {
  const data = await getNewsWire();
  const news = data.news || [];

  if (news.length === 0) return null;

  return (
    <div className="bg-surface border border-border rounded-xl overflow-hidden mb-8">
      <div className="bg-surface-alt border-b border-border px-5 py-4">
        <h2 className="font-display font-bold text-lg text-ink flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-accent-warm animate-pulse"></span>
          Live News Wire
        </h2>
      </div>
      <div className="divide-y divide-border">
        {news.map((item: any) => (
          <a
            key={item.id}
            href={item.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex gap-4 p-5 hover:bg-surface-hover transition-colors group"
          >
            {item.og_image && (
              <div
                className="w-24 h-24 sm:w-32 sm:h-24 rounded-lg bg-cover bg-center shrink-0 border border-border"
                style={{ backgroundImage: `url(${item.og_image})` }}
              />
            )}
            <div className="flex flex-col justify-center flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1.5">
                <span className="text-[10px] font-bold uppercase tracking-wider text-ink-secondary bg-surface-alt px-2 py-0.5 rounded-sm">
                  {item.source_domain}
                </span>
                <span className="text-[10px] text-ink-light">
                  {item.pub_date ? new Date(item.pub_date).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' }) : ''}
                </span>
              </div>
              <h3 className="font-display font-bold text-ink group-hover:text-brand transition-colors line-clamp-2 text-sm sm:text-base leading-snug">
                {item.title}
              </h3>
              {item.summary && (
                <p className="text-xs text-ink-secondary mt-1.5 line-clamp-1 sm:line-clamp-2">
                  {item.summary}
                </p>
              )}
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}
