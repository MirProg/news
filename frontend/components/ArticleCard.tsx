import Link from "next/link";

interface Article {
  id: number;
  sport: string;
  headline: string;
  subheadline?: string;
  confidence_pct?: number;
  hero_image_url?: string;
  hero_image_local?: string;
  published_at?: string;
  reading_time_mins?: number;
  prediction_winner?: string;
}

const SPORT_BG: Record<string, string> = {
  football: "bg-football", basketball: "bg-basketball", cricket: "bg-cricket",
  tennis: "bg-tennis", mma: "bg-mma", f1: "bg-f1", rugby: "bg-rugby", nfl: "bg-nfl",
};

export default function ArticleCard({ article }: { article: Article }) {
  const imageUrl = article.hero_image_local || article.hero_image_url ||
    `https://images.unsplash.com/photo-1461896836934-bd45ba8fcf9b?w=600&h=340&fit=crop`;

  const date = article.published_at
    ? new Date(article.published_at).toLocaleDateString("en-GB", { day: "numeric", month: "short" })
    : "";

  return (
    <Link href={`/article/${article.id}`}>
      <article className="bg-surface border border-border rounded-xl overflow-hidden card-hover group cursor-pointer h-full flex flex-col">
        {/* Image */}
        <div className="relative aspect-[16/9] overflow-hidden">
          <div
            className="absolute inset-0 bg-cover bg-center transition-transform duration-500 group-hover:scale-105"
            style={{ backgroundImage: `url(${imageUrl})` }}
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent" />

          <span className={`absolute top-3 left-3 sport-tag ${SPORT_BG[article.sport] || 'bg-brand'}`}>
            {article.sport}
          </span>

          {/* Subtle AI badge */}
          {article.confidence_pct && (
            <div className="absolute top-3 right-3 bg-white/90 backdrop-blur-sm rounded-full px-2 py-0.5 flex items-center gap-1">
              <svg className="w-3 h-3 text-accent-warm" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
              </svg>
              <span className="text-[10px] font-bold text-ink-secondary">AI</span>
            </div>
          )}
        </div>

        {/* Content */}
        <div className="p-5 flex-1 flex flex-col">
          <h3 className="font-display font-bold text-[1.05rem] leading-snug text-ink mb-2 group-hover:text-brand transition-colors line-clamp-3">
            {article.headline}
          </h3>

          {article.subheadline && (
            <p className="text-sm text-ink-secondary leading-relaxed mb-3 line-clamp-2 flex-1">
              {article.subheadline}
            </p>
          )}

          <div className="flex items-center justify-between text-xs text-ink-light mt-auto pt-3 border-t border-border">
            <span>{date}</span>
            {article.reading_time_mins && (
              <span>{article.reading_time_mins} min read</span>
            )}
          </div>
        </div>
      </article>
    </Link>
  );
}
