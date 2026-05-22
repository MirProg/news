"use client";
import { useEffect, useState } from "react";

export default function ShareButtons({ title }: { title: string }) {
  const [url, setUrl] = useState("");
  useEffect(() => { setUrl(window.location.href); }, []);

  const share = async () => {
    if (navigator.share) { try { await navigator.share({ title, url }); } catch {} }
    else { navigator.clipboard.writeText(url); alert("Link copied!"); }
  };

  return (
    <div className="flex items-center gap-3 py-5 border-y border-border my-8">
      <span className="text-xs text-ink-light uppercase tracking-wider font-bold mr-2">Share</span>
      <button onClick={share} className="w-9 h-9 rounded-full border border-border flex items-center justify-center text-ink-light hover:text-brand hover:border-brand/30 transition-colors" aria-label="Share">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" /></svg>
      </button>
      <a href={`https://twitter.com/intent/tweet?text=${encodeURIComponent(`${title} — Oracle Sports`)}&url=${encodeURIComponent(url)}`} target="_blank" rel="noopener noreferrer" className="w-9 h-9 rounded-full border border-border flex items-center justify-center text-ink-light hover:text-[#1DA1F2] hover:border-[#1DA1F2]/30 transition-colors" aria-label="Share on X">
        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" /></svg>
      </a>
    </div>
  );
}
