import Link from "next/link";

interface Article {
  id: number;
  sport: string;
  team_home: string;
  team_away: string;
  headline: string;
  subheadline?: string;
  confidence_pct?: number;
  prediction_winner?: string;
  hero_image_url?: string;
  hero_image_local?: string;
  reading_time_mins?: number;
}

const SPORT_COLORS: Record<string, string> = {
  football: "bg-football", basketball: "bg-basketball", cricket: "bg-cricket",
  tennis: "bg-tennis", mma: "bg-mma", f1: "bg-f1", rugby: "bg-rugby", nfl: "bg-nfl",
};

export default function HeroArticle({ article }: { article: Article }) {
  const imageUrl = article.hero_image_local || article.hero_image_url ||
    `https://images.unsplash.com/photo-1461896836934-bd45ba8fcf9b?w=1200&h=630&fit=crop`;

  return (
    <Link href={`/article/${article.id}`}>
      <section className="relative min-h-[75vh] flex items-end overflow-hidden group cursor-pointer">
        <div
          className="absolute inset-0 bg-cover bg-center transition-transform duration-700 group-hover:scale-[1.03]"
          style={{ backgroundImage: `url(${imageUrl})` }}
        />
        <div className="absolute inset-0 bg-gradient-hero" />

        <div className="relative z-10 max-w-4xl px-6 sm:px-10 pb-14 pt-40 animate-fade-in">
          {/* Tags Row */}
          <div className="flex items-center gap-3 mb-5">
            <span className={`sport-tag ${SPORT_COLORS[article.sport] || 'bg-brand'}`}>
              {article.sport}
            </span>
            {article.reading_time_mins && (
              <span className="text-white/60 text-sm">
                {article.reading_time_mins} min read
              </span>
            )}
            {article.confidence_pct && (
              <span className="text-white/70 text-sm font-medium flex items-center gap-2">
                <svg className="w-3.5 h-3.5 text-accent-warm" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
                AI Prediction Inside
              </span>
            )}
          </div>

          <h1 className="font-display font-extrabold text-4xl sm:text-5xl md:text-[3.5rem] text-white leading-[1.1] tracking-tight mb-4">
            {article.headline}
          </h1>

          {article.subheadline && (
            <p className="text-lg text-white/85 max-w-2xl leading-relaxed">
              {article.subheadline}
            </p>
          )}

          <div className="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-white/90 bg-white/10 px-4 py-2 rounded-lg backdrop-blur-sm group-hover:bg-white/20 transition-colors">
            Read Full Story
            <svg className="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </div>
        </div>
      </section>
    </Link>
  );
}
