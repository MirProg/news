import ArticleCard from "./ArticleCard";

interface Article {
  id: number; sport: string; headline: string; subheadline?: string;
  confidence_pct?: number; hero_image_url?: string; hero_image_local?: string;
  published_at?: string; reading_time_mins?: number;
}

export default function RelatedArticles({ articles }: { articles: Article[] }) {
  if (!articles || articles.length === 0) return null;

  return (
    <div className="mt-16 pt-10 border-t border-border">
      <h3 className="font-display font-bold text-2xl text-ink mb-6 flex items-center gap-4">
        You Might Also Like
        <div className="h-px bg-border flex-1" />
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {articles.map((a) => <div key={a.id} className="h-full"><ArticleCard article={a} /></div>)}
      </div>
    </div>
  );
}
