"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { useSearchParams, useRouter } from "next/navigation";

export default function SearchPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const initialQuery = searchParams.get("q") || "";
  const [query, setQuery] = useState(initialQuery);
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => { if (initialQuery.length >= 2) performSearch(initialQuery); }, [initialQuery]);

  const performSearch = async (q: string) => {
    if (q.length < 2) { setResults([]); return; }
    setLoading(true);
    try { const r = await fetch(`/api/articles/search?q=${encodeURIComponent(q)}`); if (r.ok) { const d = await r.json(); setResults(d.results || []); } } catch { setResults([]); }
    finally { setLoading(false); }
  };

  const onSubmit = (e: React.FormEvent) => { e.preventDefault(); if (query.trim()) { router.push(`/search?q=${encodeURIComponent(query.trim())}`); performSearch(query.trim()); } };

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-12 min-h-[70vh]">
      <h1 className="font-display font-extrabold text-3xl text-ink mb-8">Search Stories</h1>
      <form onSubmit={onSubmit} className="relative mb-10">
        <input type="text" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search teams, sports, or headlines..." className="w-full bg-surface border-2 border-border text-ink px-5 py-4 rounded-xl text-lg focus:outline-none focus:border-brand transition-colors" autoFocus />
        <button type="submit" className="absolute right-3 top-1/2 -translate-y-1/2 p-2 text-ink-light hover:text-brand transition-colors">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
        </button>
      </form>

      {loading ? (
        <div className="flex items-center justify-center py-20"><span className="w-3 h-3 rounded-full bg-brand animate-pulse-dot" /></div>
      ) : results.length > 0 ? (
        <div className="space-y-3">
          <p className="text-sm text-ink-secondary mb-4 font-semibold">{results.length} results</p>
          {results.map((a) => (
            <Link key={a.id} href={`/article/${a.id}`} className="block bg-surface border border-border p-5 rounded-xl hover:border-brand/30 hover:shadow-sm transition-all group">
              <div className="flex items-center gap-2 mb-1.5">
                <span className="text-[10px] font-bold uppercase tracking-wider text-ink-light bg-surface-alt px-2 py-0.5 rounded">{a.sport}</span>
                <span className="text-xs text-ink-light">{a.team_home} vs {a.team_away}</span>
              </div>
              <h3 className="font-display font-bold text-lg text-ink group-hover:text-brand transition-colors">{a.headline}</h3>
              {a.subheadline && <p className="text-sm text-ink-secondary line-clamp-2 mt-1">{a.subheadline}</p>}
            </Link>
          ))}
        </div>
      ) : query.length >= 2 ? (
        <div className="text-center py-20">
          <h2 className="font-display text-2xl font-bold text-ink mb-2">No results found</h2>
          <p className="text-ink-secondary">Try different keywords or check back later for new content.</p>
        </div>
      ) : null}
    </div>
  );
}
