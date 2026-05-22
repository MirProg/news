import type { Metadata } from "next";
import { Outfit, Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/Navbar";
import LiveTicker from "@/components/LiveTicker";

const outfit = Outfit({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
  variable: "--font-display",
  display: "swap",
});

const inter = Inter({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-body",
  display: "swap",
});

const jetbrains = JetBrains_Mono({
  subsets: ["latin"],
  weight: ["400", "700"],
  variable: "--font-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Oracle Sports — AI-Powered Sports Journalism",
  description: "In-depth match previews, player stories, and AI-powered analysis that goes beyond the surface. The future of sports journalism.",
  keywords: "sports news, match previews, AI analysis, football, NBA, cricket, player profiles",
  openGraph: {
    title: "Oracle Sports — Smart Sports Journalism",
    description: "In-depth stories and intelligent match analysis. We don't just cover sports — we understand them.",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${outfit.variable} ${inter.variable} ${jetbrains.variable}`}>
      <body className="bg-bg text-ink font-body antialiased">
        <LiveTicker />
        <Navbar />
        <main className="min-h-screen">{children}</main>

        {/* Footer */}
        <footer className="bg-surface-dark text-ink-on-dark mt-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 py-16">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-10">
              {/* Brand */}
              <div className="md:col-span-2">
                <h3 className="font-display text-2xl font-bold mb-3">
                  Oracle <span className="text-brand">Sports</span>
                </h3>
                <p className="text-ink-light text-sm leading-relaxed max-w-md">
                  AI-powered sports journalism that goes beyond scores and stats. We tell the stories the numbers whisper and give you analysis that actually means something.
                </p>
              </div>

              {/* Sports */}
              <div>
                <h4 className="font-display font-bold text-sm uppercase tracking-wider mb-4 text-ink-light">Sports</h4>
                <ul className="space-y-2 text-sm text-ink-light">
                  {["Football", "Basketball", "Cricket", "Tennis", "MMA", "F1"].map(s => (
                    <li key={s}><a href={`/sport/${s.toLowerCase()}`} className="hover:text-white transition-colors">{s}</a></li>
                  ))}
                </ul>
              </div>

              {/* About */}
              <div>
                <h4 className="font-display font-bold text-sm uppercase tracking-wider mb-4 text-ink-light">About</h4>
                <ul className="space-y-2 text-sm text-ink-light">
                  <li>How Our AI Works</li>
                  <li>Prediction Track Record</li>
                  <li>Editorial Standards</li>
                </ul>
              </div>
            </div>

            <div className="mt-12 pt-8 border-t border-white/10 flex items-center justify-between text-xs text-ink-light">
              <p>&copy; 2026 Oracle Sports. Built with AI, written with care.</p>
              <p>Predictions are analysis, not financial advice.</p>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
