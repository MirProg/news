"""
Smithsonian-inspired design — clean editorial magazine layout.
"""

import os, random
from datetime import datetime

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from src.world_sports import SPORTS

sport_keys = ["Cricket_T20", "EPL", "NBA", "NFL", "MLB", "NHL", "TENNIS", "Rugby", "F1", "MMA", "Boxing"]

SPORT_COLORS = {
    "Cricket_T20": "#c0392b", "EPL": "#27ae60", "NBA": "#e74c3c", "NFL": "#2980b9",
    "MLB": "#8e44ad", "NHL": "#16a085", "TENNIS": "#d4a017", "Rugby": "#c0392b",
    "F1": "#d35400", "MMA": "#2c3e50", "Boxing": "#2c3e50",
}


def _narrative(pred):
    t1 = pred["team1"]; t2 = pred["team2"]; wp = pred["t1_win_pct"]
    if abs(wp - 50) < 3:
        return f"This one's too close to call. {t1} and {t2} are evenly matched across all seven analytical dimensions."
    if wp > 70:
        return f"All signs point to {t1}. The model sees a clear advantage ({wp:.0f}%) driven by superior matchup dynamics and recent form across multiple dimensions."
    if wp > 60:
        return f"{t1} enters as the favorite ({wp:.0f}%), with the edge coming primarily from individual matchups and venue familiarity."
    return f"A slight lean toward {t1 if wp > 50 else t2} ({max(wp, 100-wp):.0f}%). Expect this one to be decided by isolated moments rather than systemic advantage."


def _dim_bars(pred):
    dims = pred.get("dimensions", []) if pred else []
    if not dims:
        return ""
    bars = "".join(
        '<div class="dim"><span class="dim-l">{}</span><div class="dim-t"><div class="dim-f" style="width:{}%"></div></div><span class="dim-r">{:.0f}</span></div>'.format(
            d["name"], d["value"], d["value"])
        for d in dims
    )
    return f'<div class="dims"><h4 class="dim-h">Factor Analysis</h4>{bars}</div>'


def generate_world_news(engine, takes, backtest_results):
    by_sport = {}
    for t in takes:
        by_sport.setdefault(t["sport"], []).append(t)

    timestamp = datetime.utcnow().strftime("%B %d, %Y")
    total_stories = len(takes)

    # Hero story: first take from first sport
    hero_sport = sport_keys[0]
    hero_takes = by_sport.get(hero_sport, [])
    hero = hero_takes[0] if hero_takes else None
    hero_html = ""
    if hero:
        pred = hero.get("prediction", {})
        acc = backtest_results.get(hero_sport, {}).get("accuracy", "?")
        hero_html = f"""
    <div class="hero">
      <div class="hero-text">
        <p class="hero-cat" style="color:{SPORT_COLORS.get(hero_sport, '#333')}">{SPORTS[hero_sport]['name']}</p>
        <h1 class="hero-title">{hero['title']}</h1>
        <p class="hero-body">{_narrative(pred)[:220]}</p>
        <p class="hero-meta">Backtest accuracy: {acc}% &middot; {SPORTS[hero_sport]['name']} &middot; 7 dimensions</p>
      </div>
    </div>"""

    # Sections
    nav_links = ""
    sections = ""
    for key in sport_keys:
        if key not in engine.predictors:
            continue
        sport_takes = by_sport.get(key, [])
        bt = backtest_results.get(key, {})
        color = SPORT_COLORS.get(key, "#333")

        cards = ""
        for t in sport_takes:
            pred = t.get("prediction", {})
            body_html = _narrative(pred) if pred else t["body"].replace("\n", "<br>")[:200]
            dims_html = _dim_bars(pred) if pred else ""

            cards += f"""
          <article class="story">
            <h2 class="story-title"><a href="#">{t['title']}</a></h2>
            <p class="story-body">{body_html}</p>
            {dims_html}
          </article>"""

        sections += f"""
      <section class="sport-section" id="{key}">
        <div class="section-head">
          <h2 class="section-name" style="border-left-color:{color}">{SPORTS[key]['name']}</h2>
          <span class="section-acc">{bt.get('accuracy', '?')}% accuracy &middot; {len(sport_takes)} stories</span>
        </div>
        <div class="story-list">{cards}</div>
      </section>"""

        nav_links += f'<a class="nav-link" href="#{key}" style="--nav-c:{color}">{SPORTS[key]["name"]}</a>'

    # Overview badges
    overview = "".join(
        f'<div class="ov-item" style="--ov-c:{SPORT_COLORS.get(k, "#666")}"><span class="ov-name">{SPORTS[k]["name"]}</span><span class="ov-acc">{backtest_results.get(k, {}).get("accuracy", "?")}%</span></div>'
        for k in sport_keys if k in backtest_results
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>World Sports Predictions — {timestamp}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,600;0,700;1,500;1,600&display=swap" rel="stylesheet">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  font-family: 'Inter', -apple-system, sans-serif;
  font-size: 16px; line-height: 1.6;
  color: #222; background: #fafafa;
  -webkit-font-smoothing: antialiased;
}}
a {{ color: inherit; text-decoration: none; }}
.container {{ max-width: 960px; margin: 0 auto; padding: 0 20px 40px; }}

/* Header */
.top-bar {{
  background: #222; color: #fff; padding: 8px 0;
  font-size: 0.65rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.08em;
  text-align: center;
}}
.masthead {{
  border-bottom: 1px solid #ddd; padding: 18px 0 14px; margin-bottom: 24px;
  display: flex; justify-content: space-between; align-items: flex-end;
}}
.masthead .logo {{ font-family: 'Playfair Display', Georgia, serif; font-size: 1.5rem; font-weight: 700; }}
.masthead .logo em {{ font-style: italic; color: #c0392b; }}
.masthead .ts {{ font-size: 0.7rem; color: #999; text-align: right; }}

/* Nav */
.sport-nav {{
  display: flex; gap: 4px; flex-wrap: wrap;
  padding-bottom: 18px; margin-bottom: 24px; border-bottom: 1px solid #eee;
}}
.nav-link {{
  font-size: 0.7rem; font-weight: 500; color: #666; letter-spacing: 0.02em;
  padding: 4px 12px; border-radius: 3px; transition: all 0.15s;
}}
.nav-link:hover {{ background: var(--nav-c, #eee); color: #fff; }}

/* Hero */
.hero {{
  margin-bottom: 28px; padding-bottom: 24px; border-bottom: 1px solid #eee;
}}
.hero-cat {{ font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 6px; }}
.hero-title {{ font-family: 'Playfair Display', Georgia, serif; font-size: 1.6rem; font-weight: 700; line-height: 1.2; margin-bottom: 8px; letter-spacing: -0.01em; }}
.hero-body {{ font-size: 0.9rem; color: #555; line-height: 1.7; max-width: 700px; }}
.hero-meta {{ font-size: 0.65rem; color: #aaa; margin-top: 8px; font-family: 'Inter', monospace; }}

/* Overview grid */
.overview {{
  display: grid; grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 6px; margin-bottom: 28px;
}}
.ov-item {{
  background: #fff; border: 1px solid #eee; border-radius: 4px;
  padding: 8px 4px; text-align: center; font-size: 0.6rem;
  border-top: 3px solid var(--ov-c, #ddd);
}}
.ov-name {{ color: #888; display: block; margin-bottom: 2px; }}
.ov-acc {{ font-weight: 700; font-size: 0.8rem; }}

/* Sport section */
.sport-section {{ margin-bottom: 28px; }}
.section-head {{
  display: flex; justify-content: space-between; align-items: baseline;
  margin-bottom: 12px; padding-bottom: 6px; border-bottom: 1px solid #eee;
}}
.section-name {{
  font-family: 'Playfair Display', Georgia, serif; font-size: 1.1rem;
  font-weight: 700; padding-left: 10px; border-left: 3px solid #333;
}}
.section-acc {{ font-size: 0.65rem; color: #aaa; }}

/* Story list */
.story-list {{ display: flex; flex-direction: column; gap: 0; }}
.story {{
  padding: 14px 0; border-bottom: 1px solid #f0f0f0;
}}
.story:last-child {{ border-bottom: none; }}
.story-title {{ font-size: 0.9rem; font-weight: 600; margin-bottom: 4px; line-height: 1.3; }}
.story-body {{ font-size: 0.75rem; color: #666; line-height: 1.6; }}

/* Dimensional analysis */
.dims {{ margin-top: 8px; padding-top: 6px; border-top: 1px solid #f0f0f0; display: flex; flex-wrap: wrap; gap: 2px 20px; }}
.dim-h {{ width: 100%; font-size: 0.6rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; color: #bbb; margin-bottom: 2px; }}
.dim {{ display: inline-flex; align-items: center; gap: 5px; font-size: 0.6rem; }}
.dim-l {{ color: #999; width: 70px; }}
.dim-t {{ width: 60px; height: 4px; background: #eee; border-radius: 2px; overflow: hidden; }}
.dim-f {{ height: 100%; background: #c0392b; border-radius: 2px; }}
.dim-r {{ color: #999; font-family: monospace; width: 20px; text-align: right; }}

/* Footer */
.footer {{
  border-top: 1px solid #ddd; padding: 20px 0; margin-top: 12px;
  text-align: center; font-size: 0.65rem; color: #aaa; line-height: 2;
}}

@media(max-width:600px) {{
  .masthead {{ flex-direction: column; align-items: flex-start; gap: 4px; }}
  .overview {{ grid-template-columns: repeat(4, 1fr); }}
  .dims {{ flex-direction: column; gap: 1px; }}
}}
</style>
</head>
<body>

<div class="top-bar">Multi-Dimensional Sports Prediction Engine &middot; 7 Factors &middot; 11 Sports</div>

<div class="container">

<header class="masthead">
  <div class="logo">World Sports <em>Predictions</em></div>
  <div class="ts">{timestamp}<br>{total_stories} stories across {len(sport_keys)} sports</div>
</header>

<nav class="sport-nav">{nav_links}</nav>

{hero_html}

<div class="overview">{overview}</div>

{sections}

<footer class="footer">
  Predictions based on 7 dimensions: Head-to-Head History (18%), Player Matchups (22%), Venue &amp; Conditions (15%),
  Recent Form (15%), Tournament Context (10%), Sentiment (10%), Player Health (10%)
  <br>Data: synthetic historical models &middot; PyTorch Monte Carlo engine
</footer>

</div>
<script>
document.querySelectorAll('.nav-link').forEach(a => {{
  a.addEventListener('click', e => {{
    e.preventDefault();
    const el = document.querySelector(a.getAttribute('href'));
    if (el) el.scrollIntoView({{ behavior:'smooth', block:'start' }});
  }});
}});
</script>
</body>
</html>"""

    out_dir = os.path.join(HERE, "output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return out_path
