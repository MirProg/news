import HeroArticle from "@/components/HeroArticle";
import ArticleCard from "@/components/ArticleCard";
import LiveScoresSidebar from "@/components/LiveScoresSidebar";
import ConfidenceLeaderboard from "@/components/ConfidenceLeaderboard";
import NewsWire from "@/components/NewsWire";

async function getArticles() {
  try {
    const res = await fetch("http://localhost:4000/api/articles?limit=13", { next: { revalidate: 60 } });
    if (!res.ok) return { articles: [] };
    return res.json();
  } catch {
    return { articles: [] };
  }
}

export default async function Home() {
  const data = await getArticles();
  const articles = data.articles || [];
  const heroArticle = articles[0];
  const gridArticles = articles.slice(1, 7);
  const moreArticles = articles.slice(7);

  return (
    <>
      {heroArticle ? (
        <HeroArticle article={heroArticle} />
      ) : (
        /* Empty state — welcoming, not dark */
        <section className="bg-gradient-to-br from-brand via-brand-dark to-surface-dark text-white py-28 px-6 text-center">
          <div className="max-w-2xl mx-auto animate-fade-in">
            <div className="w-16 h-16 rounded-2xl bg-white/15 flex items-center justify-center mx-auto mb-6">
              <span className="font-display font-bold text-3xl">O</span>
            </div>
            <h1 className="font-display font-extrabold text-4xl sm:text-5xl mb-4 tracking-tight">
              Welcome to Oracle Sports
            </h1>
            <p className="text-xl text-white/80 leading-relaxed mb-6">
              AI-powered sports journalism that tells the stories behind the stats.
              In-depth match previews, player profiles, and predictions that go beyond the surface.
            </p>
            <p className="text-white/50 text-sm">
              Articles will appear here once the engine starts generating content.
            </p>
          </div>
        </section>
      )}

      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-14">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
          <div className="lg:col-span-8">
            {gridArticles.length > 0 && (
              <>
                <div className="flex items-center gap-4 mb-8">
                  <h2 className="font-display font-bold text-2xl text-ink">Latest Stories</h2>
                  <div className="h-px bg-border flex-1" />
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mb-12">
                  {gridArticles.map((article: any) => (
                    <div key={article.id} className="h-full"><ArticleCard article={article} /></div>
                  ))}
                </div>
              </>
            )}

            {moreArticles.length > 0 && (
              <>
                <div className="flex items-center gap-4 mb-8">
                  <h2 className="font-display font-bold text-2xl text-ink">More From Oracle</h2>
                  <div className="h-px bg-border flex-1" />
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  {moreArticles.map((article: any) => (
                    <div key={article.id} className="h-full"><ArticleCard article={article} /></div>
                  ))}
                </div>
              </>
            )}
          </div>

          <div className="lg:col-span-4 space-y-8">
            <NewsWire />
            <ConfidenceLeaderboard />
            <LiveScoresSidebar />
          </div>
        </div>
      </div>
    </>
  );
}
