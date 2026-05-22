"use client";
import { useState, useRef, useEffect } from "react";

export default function AudioPlayer({ src }: { src: string }) {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [playing, setPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    const onTime = () => { setCurrentTime(audio.currentTime); setProgress(audio.duration ? (audio.currentTime / audio.duration) * 100 : 0); };
    const onLoaded = () => setDuration(audio.duration);
    const onEnded = () => setPlaying(false);
    audio.addEventListener("timeupdate", onTime);
    audio.addEventListener("loadedmetadata", onLoaded);
    audio.addEventListener("ended", onEnded);
    return () => { audio.removeEventListener("timeupdate", onTime); audio.removeEventListener("loadedmetadata", onLoaded); audio.removeEventListener("ended", onEnded); };
  }, []);

  const toggle = () => { const a = audioRef.current; if (!a) return; playing ? a.pause() : a.play(); setPlaying(!playing); };
  const seek = (e: React.MouseEvent<HTMLDivElement>) => { const a = audioRef.current; if (!a?.duration) return; const r = e.currentTarget.getBoundingClientRect(); a.currentTime = ((e.clientX - r.left) / r.width) * a.duration; };
  const fmt = (s: number) => `${Math.floor(s / 60)}:${Math.floor(s % 60).toString().padStart(2, "0")}`;

  return (
    <div className="bg-surface-alt border border-border rounded-xl p-4 my-6 flex items-center gap-4">
      <audio ref={audioRef} src={src} preload="metadata" />
      <button onClick={toggle} className="w-10 h-10 flex items-center justify-center rounded-full bg-brand hover:bg-brand-dark transition-colors flex-shrink-0" aria-label={playing ? "Pause" : "Play"}>
        {playing ? (
          <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24"><rect x="6" y="4" width="4" height="16" /><rect x="14" y="4" width="4" height="16" /></svg>
        ) : (
          <svg className="w-4 h-4 text-white ml-0.5" fill="currentColor" viewBox="0 0 24 24"><polygon points="5,3 19,12 5,21" /></svg>
        )}
      </button>
      <div className="flex-1">
        <div className="h-2 bg-border rounded-full cursor-pointer" onClick={seek}>
          <div className="h-full bg-brand rounded-full transition-all" style={{ width: `${progress}%` }} />
        </div>
        <div className="flex justify-between mt-1">
          <span className="text-[10px] font-mono text-ink-light">{fmt(currentTime)}</span>
          <span className="text-[10px] font-mono text-ink-light">{fmt(duration)}</span>
        </div>
      </div>
      <span className="text-[10px] text-ink-light uppercase tracking-wider font-semibold hidden sm:block">Listen</span>
    </div>
  );
}
