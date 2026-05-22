"use client";
import { useState } from "react";
import Link from "next/link";

const SPORTS = [
  { key: "all", label: "All Sports", color: "text-brand" },
  { key: "football", label: "Football", color: "text-football" },
  { key: "basketball", label: "Basketball", color: "text-basketball" },
  { key: "cricket", label: "Cricket", color: "text-cricket" },
  { key: "tennis", label: "Tennis", color: "text-tennis" },
  { key: "mma", label: "MMA", color: "text-mma" },
  { key: "f1", label: "F1", color: "text-f1" },
  { key: "rugby", label: "Rugby", color: "text-rugby" },
];

export default function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <nav className="sticky top-0 z-50 glass border-b border-border shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2.5 group">
            <div className="w-9 h-9 rounded-lg bg-brand flex items-center justify-center group-hover:scale-105 transition-transform">
              <span className="text-white font-display font-bold text-base">O</span>
            </div>
            <div>
              <span className="font-display font-bold text-lg text-ink tracking-tight">
                Oracle <span className="text-brand">Sports</span>
              </span>
            </div>
          </Link>

          {/* Desktop Sport Tabs */}
          <div className="hidden md:flex items-center gap-0.5">
            {SPORTS.map((sport) => (
              <Link
                key={sport.key}
                href={sport.key === "all" ? "/" : `/sport/${sport.key}`}
                className="px-3 py-2 text-sm font-semibold text-ink-secondary hover:text-ink hover:bg-surface-alt transition-all duration-200 rounded-lg"
              >
                {sport.label}
              </Link>
            ))}
          </div>

          {/* Search + Mobile */}
          <div className="flex items-center gap-2">
            <Link
              href="/search"
              className="p-2.5 rounded-lg text-ink-secondary hover:text-brand hover:bg-brand-light transition-colors"
              aria-label="Search"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </Link>

            <button
              onClick={() => setMenuOpen(!menuOpen)}
              className="md:hidden p-2 text-ink-secondary hover:text-ink rounded-lg"
              aria-label="Menu"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                {menuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {menuOpen && (
        <div className="md:hidden border-t border-border bg-surface animate-fade-in">
          <div className="px-4 py-3 space-y-1">
            {SPORTS.map((sport) => (
              <Link
                key={sport.key}
                href={sport.key === "all" ? "/" : `/sport/${sport.key}`}
                onClick={() => setMenuOpen(false)}
                className="block px-4 py-2.5 text-sm font-semibold text-ink-secondary hover:text-ink hover:bg-surface-alt transition-all rounded-lg"
              >
                {sport.label}
              </Link>
            ))}
          </div>
        </div>
      )}
    </nav>
  );
}
