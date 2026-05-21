# Infinite Brief

the news, but we mixed it together — AI-powered news mashups and scrollytelling briefings.

Runs 24/7 on GitHub Actions free tier.

## What makes it unique

| Feature | Description |
|---------|-------------|
| **Scrollytelling READ mode** | Top story unfolds as you scroll — multiple AI perspectives revealed progressively |
| **PLAY mode mashups** | Drag stories together → HAL generates creative crossovers (Infinite Craft-style) |
| **Multi-perspective AI** | Every article gets 4 AI viewpoints: Analyst, Strategist, Contrarian, Prediction |
| **Executive briefing** | AI-generated daily summary connecting the day's top stories |
| **Trend tracking** | "Hot" badges on stories appearing across multiple hourly runs |
| **Semantic dedup** | Same story from different sources automatically merged |
| **First Discovery** | Be the first to mash two stories together — tracked per device |
| **Shareable mashups** | One-click copy to share HAL's crossovers (Wordle-style) |

## Architecture

```
.github/workflows/daily.yml   ← Cron: hourly → GitHub Pages
src/
├── pipeline.py                ← Orchestrator (10 stages)
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
├── mashup.py                  ← HAL-powered crossover generator
└── generator.py               ← Jinja2 → interactive HTML SPA
templates/index.html           ← Site SPA template
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
```

### Run locally

```bash
python src/pipeline.py
# Open output/index.html
```

## Design Philosophy

- **Not AI slop** — The AI has a personality (HAL), the design is indie/retro, and absurdity is a feature not a bug
- **Creative toy, not news aggregator** — The PLAY mode makes news consumption active, not passive
- **Transparency** — Every mashup shows its "recipe" (which two stories went in)
- **Scarcity** — Only ~15 mashups per hour, new combos every cycle

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
