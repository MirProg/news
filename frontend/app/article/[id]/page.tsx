import { notFound } from "next/navigation";
import ArticleBody from "@/components/ArticleBody";
import PredictionBox from "@/components/PredictionBox";
import AudioPlayer from "@/components/AudioPlayer";
import SourceBadges from "@/components/SourceBadges";
import AftermathSection from "@/components/AftermathSection";
import RelatedArticles from "@/components/RelatedArticles";
import ShareButtons from "@/components/ShareButtons";

const SPORT_BG: Record<string, string> = {
  football: "bg-football", basketball: "bg-basketball", cricket: "bg-cricket",
  tennis: "bg-tennis", mma: "bg-mma", f1: "bg-f1", rugby: "bg-rugby", nfl: "bg-nfl",
};

async function getArticle(id: string) {
  try {
    const res = await fetch(`http://localhost:4000/api/articles/${id}`, { next: { revalidate: 60 } });
    if (!res.ok) return null;
    return res.json();
  } catch { return null; }
}

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const data = await getArticle(id);
  if (!data?.article) return { title: "Article Not Found" };
  return { title: `${data.article.headline} | Oracle Sports`, description: data.article.subheadline };
}

export default async function ArticlePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const data = await getArticle(id);
  if (!data?.article) notFound();

  const { article, related } = data;
  const imageUrl = article.hero_image_local || article.hero_image_url || `https://images.unsplash.com/photo-1461896836934-bd45ba8fcf9b?w=1200&h=630&fit=crop`;
  const date = article.published_at ? new Date(article.published_at).toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" }) : "";

  return (
    <article className="min-h-screen bg-bg">
      {/* Hero */}
      <header className="relative w-full h-[55vh] min-h-[380px] flex items-end">
        <div className="absolute inset-0 bg-cover bg-center" style={{ backgroundImage: `url(${imageUrl})` }} />
        <div className="absolute inset-0 bg-gradient-hero" />
        <div className="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 w-full pb-10 animate-slide-up">
          <div className="flex items-center gap-3 mb-5">
            <span className={`sport-tag ${SPORT_BG[article.sport] || 'bg-brand'}`}>{article.sport}</span>
            <span className="text-white/70 text-sm">{date}</span>
            {article.reading_time_mins && <span className="text-white/50 text-sm ml-auto">{article.reading_time_mins} min read</span>}
          </div>
          <h1 className="font-display font-extrabold text-3xl sm:text-4xl md:text-5xl text-white leading-[1.12] tracking-tight mb-4">{article.headline}</h1>
          {article.subheadline && <p className="text-lg text-white/80 leading-relaxed max-w-3xl">{article.subheadline}</p>}
        </div>
      </header>

      {/* Body */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-10">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
          <div className="lg:col-span-8">
            {article.audio_path && <AudioPlayer src={article.audio_path} />}
            <PredictionBox winner={article.prediction_winner} confidence={article.confidence_pct} edge={article.edge_summary} />
            <ArticleBody html={article.body_html} />

            {article.resolved === 1 && article.aftermath_html && (
              <AftermathSection html={article.aftermath_html} correct={article.prediction_correct === 1} />
            )}

            <div className="mt-10 pt-6 border-t border-border space-y-4">
              <SourceBadges domains={article.source_domains} />
              {article.tags?.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-3">
                  {article.tags.map((tag: string, i: number) => (
                    <span key={i} className="text-xs text-ink-secondary px-3 py-1 bg-surface-alt border border-border rounded-full">#{tag}</span>
                  ))}
                </div>
              )}
            </div>
            <ShareButtons title={article.headline} />
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-4">
            <div className="bg-surface border border-border rounded-xl p-5 sticky top-20">
              <h3 className="font-display font-bold text-lg text-ink mb-4">Match Info</h3>
              <div className="space-y-4 text-sm">
                <div>
                  <p className="text-xs text-ink-light uppercase tracking-wider font-semibold mb-0.5">Matchup</p>
                  <p className="font-semibold text-ink">{article.team_home} vs {article.team_away}</p>
                </div>
                <div>
                  <p className="text-xs text-ink-light uppercase tracking-wider font-semibold mb-0.5">When</p>
                  <p className="text-ink">{new Date(article.match_date).toLocaleString('en-GB', { weekday: 'short', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })}</p>
                </div>
                {article.confidence_pct && (
                  <div>
                    <p className="text-xs text-ink-light uppercase tracking-wider font-semibold mb-1.5">AI Confidence</p>
                    <div className="h-2.5 bg-surface-alt rounded-full overflow-hidden">
                      <div className="h-full bg-brand rounded-full" style={{ width: `${article.confidence_pct}%` }} />
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
        <RelatedArticles articles={related} />
      </div>
    </article>
  );
}
