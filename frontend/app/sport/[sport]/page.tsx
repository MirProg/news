import ArticleCard from "@/components/ArticleCard";

async function getSportArticles(sport: string) {
  try {
    const res = await fetch(`http://localhost:4000/api/articles/sport/${sport}?limit=24`, { next: { revalidate: 60 } });
    if (!res.ok) return { articles: [] };
    return res.json();
  } catch { return { articles: [] }; }
}

export async function generateMetadata({ params }: { params: Promise<{ sport: string }> }) {
  const { sport } = await params;
  const name = sport.charAt(0).toUpperCase() + sport.slice(1);
  return { title: `${name} News & Analysis | Oracle Sports` };
}

export default async function SportPage({ params }: { params: Promise<{ sport: string }> }) {
  const { sport } = await params;
  const data = await getSportArticles(sport);
  const articles = data.articles || [];
  const sportName = sport.charAt(0).toUpperCase() + sport.slice(1);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-12">
      <header className="mb-10">
        <h1 className="font-display font-extrabold text-4xl text-ink tracking-tight mb-3">{sportName}</h1>
        <p className="text-lg text-ink-secondary max-w-2xl">The latest stories, match previews, and AI-powered analysis from the world of {sportName.toLowerCase()}.</p>
      </header>

      {articles.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {articles.map((a: any) => <div key={a.id} className="h-full"><ArticleCard article={a} /></div>)}
        </div>
      ) : (
        <div className="py-20 text-center bg-surface border border-border rounded-xl">
          <h2 className="font-display text-2xl font-bold text-ink mb-2">No stories yet</h2>
          <p className="text-ink-secondary">Our AI is working on {sportName.toLowerCase()} coverage. Check back soon!</p>
        </div>
      )}
    </div>
  );
}
