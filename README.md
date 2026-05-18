# AIBrief — Multi-Perspective AI News

AI-curated AI & tech news with **multi-perspective reasoning**. Runs 24/7 on GitHub Actions free tier.

## What makes it unique

| Feature | Description |
|---------|-------------|
| **Multi-perspective AI** | Every article gets 4 AI viewpoints: Analyst, Strategist, Contrarian, Prediction |
| **Executive briefing** | AI-generated daily summary connecting the day's top stories |
| **Trend tracking** | "Hot" badges on stories appearing across multiple hourly runs |
| **Semantic dedup** | Same story from different sources automatically merged |
| **Full AI rewriting** | Downloaded text → AI-rewritten unique content |
| **SEO keywords** | Auto-extracted tags per article |
| **Transparent** | Every article labeled "AI Generated" with link to original |

## Architecture

```
.github/workflows/daily.yml   ← Cron: hourly → GitHub Pages
src/
├── pipeline.py                ← Orchestrator (9 stages)
├── config.py                  ← RSS feeds + API keys
├── fetcher.py                 ← RSS parsing
├── content_fetcher.py         ← Full text via trafilatura
├── dedup.py                   ← Jaccard similarity dedup
├── ai_writer.py               ← OpenAI/Claude rewriting
├── local_ai.py                ← Optional local AI (transformers)
├── reasoning.py               ← Multi-perspective analysis
├── keywords.py                ← SEO keyword extraction
├── briefing.py                ← Executive briefing generation
├── trends.py                  ← Cross-run trend tracking
└── generator.py               ← Jinja2 → static HTML
templates/index.html           ← Site template
output/index.html              ← Generated site
```

## Quick Start

```bash
git clone https://github.com/YOUR_USER/ai-brief.git
cd ai-brief
pip install -r requirements.txt
```

### Set API keys (optional — without these, site uses raw summaries)

```bash
set OPENAI_API_KEY=sk-...     # or ANTHROPIC_API_KEY
set AI_PROVIDER=openai        # or "anthropic"
```

### Run locally

```bash
python src/pipeline.py
# Open output/index.html
```

## Deploy (GitHub Pages)

1. Push to GitHub
2. Add secrets: `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
3. Settings → Pages → Source: GitHub Actions
4. Site auto-updates every hour at `YOUR_USER.github.io/ai-brief`

## Commercial Strategy

- **Display ads** (Carbon, AdSense) on the template
- **Newsletter** via the promo box → ConvertKit/Substack
- **Affiliate links** for AI tools in article content
- **Sponsorships** from AI/DevTool companies
