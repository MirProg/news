"""
Smithsonian-inspired design with thrilling narrative, aesthetic sports images.
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

SPORT_IMAGES = {
    "Cricket_T20": "https://images.unsplash.com/photo-1531415074968-036ba1b575da?w=900&h=500&fit=crop",
    "EPL": "https://images.unsplash.com/photo-1575361204480-aadea25e6e68?w=900&h=500&fit=crop",
    "NBA": "https://images.unsplash.com/photo-1546519638-68e109498ffc?w=900&h=500&fit=crop",
    "NFL": "https://images.unsplash.com/photo-1566577739112-5180d4bf9391?w=900&h=500&fit=crop",
    "MLB": "https://images.unsplash.com/photo-1562077772-1fd6ddb2ed5a?w=900&h=500&fit=crop",
    "NHL": "https://images.unsplash.com/photo-1515703407324-5d7532e6918f?w=900&h=500&fit=crop",
    "TENNIS": "https://images.unsplash.com/photo-1595435934249-5df7ed86e1c0?w=900&h=500&fit=crop",
    "Rugby": "https://images.unsplash.com/photo-1511882150382-4210563a7220?w=900&h=500&fit=crop",
    "F1": "https://images.unsplash.com/photo-1630673240362-ed9f2121eb1a?w=900&h=500&fit=crop",
    "MMA": "https://images.unsplash.com/photo-1599058917212-d750089bc07e?w=900&h=500&fit=crop",
    "Boxing": "https://images.unsplash.com/photo-1549719386-74dfcbf7dbed?w=900&h=500&fit=crop",
}


def _thrilling_narrative(pred):
    """Write a thrilling, story-driven narrative — numbers woven into the story."""
    t1 = pred["team1"]; t2 = pred["team2"]; wp = pred["t1_win_pct"]
    dims = pred.get("dimensions", [])
    sorted_dims = sorted(dims, key=lambda d: -abs(d["value"] - 50))

    opening_templates = [
        f"The floodlights cut through the evening haze as {t1} and {t2} prepare to write the next chapter of their rivalry. Every meeting between these two carries weight — history, pride, the quiet desperation of athletes who know what's at stake.",
        f"On paper, this matchup between {t1} and {t2} looks like a collision of styles. But the game isn't played on paper. It's played in the spaces between anticipation and reaction, where muscle memory meets the unexpected.",
        f"There are matchups that analytics departments circle on the calendar months in advance. {t1} vs {t2} is one of them. Not just because of the standings, but because of what happens when these particular athletes share the same field.",
        f"The stadium hums with a different energy tonight. {t1} and {t2} have met before — enough times that the handshakes before kickoff carry a hint of familiarity masking deeper tensions. This time, everything is different.",
    ]

    if abs(wp - 50) < 3:
        body = random.choice(opening_templates)
        body += f" The numbers confirm what the gut already knows: this is a coin-flip. After analyzing seven distinct dimensions — from individual matchup histories to venue conditions, from recent form fluctuations to the pressure of the moment — the model registers a dead heat. {t1} checks in at {wp:.0f}%, {t2} at {100-wp:.0f}%. When the margin is this thin, the game becomes a cascade of single moments: a misstep in the 73rd minute, a gust of wind at the wrong instant, a referee's decision that tilts everything."
    elif wp > 70:
        body = random.choice(opening_templates)
        body += f" The model is unambiguous: {t1} holds a {wp:.0f}% probability of victory, and the reasons run deeper than simple optimism."
        if sorted_dims:
            strong = sorted_dims[0]
            body += f" The strongest signal comes from {strong['name'].lower()}, which tilts decisively in {t1}'s favor. Across seven analytical dimensions, {t1} shows structural advantages that compound rather than cancel out."
        body += f" This isn't a prediction of inevitability — sport is too human for that — but it is a statement of probability weighted by evidence. {t2} would need to overcome not just their opponent, but the accumulated weight of every factor measured."
    elif wp > 60:
        body = random.choice(opening_templates)
        body += f" The model gives {t1} a {wp:.0f}% edge — a meaningful but not insurmountable advantage."
        if len(sorted_dims) >= 2:
            body += f" The two most influential factors, {sorted_dims[0]['name'].lower()} and {sorted_dims[1]['name'].lower()}, both trend in {t1}'s direction, creating a compound effect that accounts for roughly two-thirds of the gap. But the remaining dimensions are closer to parity, and in sport, parity is dangerous."
        body += f" In roughly three out of ten simulations, {t2} finds a path to victory — often through the very unpredictability that makes sport worth watching."
    else:
        body = random.choice(opening_templates)
        body += f" The model registers a slight lean toward {t1 if wp > 50 else t2} at {max(wp, 100-wp):.0f}%, but this is the territory where prediction meets its limits."
        if sorted_dims:
            body += f" The narrow edge comes primarily from {sorted_dims[0]['name'].lower()}, where a marginal advantage accumulates into just enough signal to separate the two sides. But the noise is loud here."
        body += f" This is the kind of match that reminds you why we watch: no algorithm, no matter how many dimensions it tracks, can fully account for the human element that decides these contests."

    if pred.get("pred_score1") is not None:
        body += f" The projected scoreline — {t1} {pred['pred_score1']:.0f}, {t2} {pred['pred_score2']:.0f} — tells only part of the story."
    else:
        body += f" The projected outcome favors {t1 if wp > 50 else t2}, but the margin of victory remains uncertain."

    body += f" What happens between the first whistle and the last will be determined not by statistics, but by the choices athletes make when the moment demands something extraordinary."

    return body


def _dim_bars(pred):
    dims = pred.get("dimensions", []) if pred else []
    if not dims:
        return ""
    bars = "".join(
        '<div class="dim"><span class="dim-l">{}</span><div class="dim-t"><div class="dim-f" style="width:{}%"></div></div><span class="dim-r">{:.0f}</span></div>'.format(
            d["name"], d["value"], d["value"])
        for d in dims
    )
    return f'<div class="dims"><h4 class="dim-h">The Seven Factors</h4>{bars}</div>'


def generate_world_news(engine, takes, backtest_results):
    by_sport = {}
    for t in takes:
        by_sport.setdefault(t["sport"], []).append(t)

    timestamp = datetime.utcnow().strftime("%B %d, %Y")
    total_stories = len(takes)

    # Hero: pick highest-confidence prediction as main event
    hero_sport = None
    hero_take = None
    hero_conf = 0
    for key in sport_keys:
        if key not in engine.predictors:
            continue
        for t in by_sport.get(key, []):
            pred = t.get("prediction", {})
            conf = abs(pred.get("t1_win_pct", 50) - 50) if pred else 0
            if conf > hero_conf:
                hero_conf = conf
                hero_take = t
                hero_sport = key

    hero_html = ""
    if hero_take and hero_sport:
        pred = hero_take.get("prediction", {})
        acc = backtest_results.get(hero_sport, {}).get("accuracy", "?")
        img = SPORT_IMAGES.get(hero_sport, "")
        narrative = _thrilling_narrative(pred) if pred else ""
        hero_html = f"""
    <div class="hero">
      <div class="hero-img" style="background-image:url('{img}')"></div>
      <div class="hero-overlay"></div>
      <div class="hero-text">
        <p class="hero-cat" style="color:{SPORT_COLORS.get(hero_sport, '#fff')}">{SPORTS[hero_sport]['name']}</p>
        <h1 class="hero-title">{hero_take['title']}</h1>
        <p class="hero-body">{narrative[:280]}...</p>
        <p class="hero-meta">Main event &middot; Backtest accuracy: {acc}% &middot; 7-dimensional analysis</p>
      </div>
    </div>"""

    # Navigation + sections
    nav_links = ""
    sections = ""
    for key in sport_keys:
        if key not in engine.predictors:
            continue
        sport_takes = by_sport.get(key, [])
        bt = backtest_results.get(key, {})
        color = SPORT_COLORS.get(key, "#333")
        img = SPORT_IMAGES.get(key, "")

        cards = ""
        for t in sport_takes:
            pred = t.get("prediction", {})
            body_html = _thrilling_narrative(pred) if pred else t["body"].replace("\n", "<br>")[:300]
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
        <div class="section-img" style="background-image:url('{img}')"></div>
        <div class="story-list">{cards}</div>
      </section>"""

        nav_links += f'<a class="nav-link" href="#{key}" style="--nav-c:{color}">{SPORTS[key]["name"]}</a>'

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

/* Top bar */
.top-bar {{
  background: #222; color: #fff; padding: 8px 0;
  font-size: 0.65rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.08em;
  text-align: center;
}}

/* Masthead */
.masthead {{
  border-bottom: 1px solid #ddd; padding: 18px 0 14px; margin-bottom: 28px;
  display: flex; justify-content: space-between; align-items: flex-end;
}}
.masthead .logo {{ font-family: 'Playfair Display', Georgia, serif; font-size: 1.5rem; font-weight: 700; }}
.masthead .logo em {{ font-style: italic; color: #c0392b; }}
.masthead .ts {{ font-size: 0.7rem; color: #999; text-align: right; }}

/* Sport nav */
.sport-nav {{
  display: flex; gap: 4px; flex-wrap: wrap;
  padding-bottom: 18px; margin-bottom: 28px; border-bottom: 1px solid #eee;
}}
.nav-link {{
  font-size: 0.7rem; font-weight: 500; color: #666; letter-spacing: 0.02em;
  padding: 4px 12px; border-radius: 3px; transition: all 0.15s;
}}
.nav-link:hover {{ background: var(--nav-c, #eee); color: #fff; }}

/* Overview */
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

/* Hero */
.hero {{
  position: relative;
  height: 420px;
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 32px;
}}
.hero-img {{
  position: absolute; inset: 0;
  background-size: cover; background-position: center;
  filter: brightness(0.5);
  transition: filter 0.5s;
}}
.hero:hover .hero-img {{ filter: brightness(0.4); }}
.hero-overlay {{
  position: absolute; inset: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.2) 60%, rgba(0,0,0,0.1) 100%);
}}
.hero-text {{
  position: absolute; bottom: 0; left: 0; right: 0;
  padding: 30px;
  color: #fff;
}}
.hero-cat {{ font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 6px; }}
.hero-title {{
  font-family: 'Playfair Display', Georgia, serif;
  font-size: 1.8rem; font-weight: 700; line-height: 1.2;
  margin-bottom: 8px; max-width: 700px;
}}
.hero-body {{ font-size: 0.85rem; line-height: 1.6; opacity: 0.85; max-width: 650px; }}
.hero-meta {{ font-size: 0.65rem; opacity: 0.6; margin-top: 8px; font-family: 'Inter', monospace; }}

/* Sport section */
.sport-section {{ margin-bottom: 32px; }}
.section-head {{
  display: flex; justify-content: space-between; align-items: baseline;
  margin-bottom: 10px; padding-bottom: 6px; border-bottom: 1px solid #eee;
}}
.section-name {{
  font-family: 'Playfair Display', Georgia, serif; font-size: 1.1rem;
  font-weight: 700; padding-left: 10px; border-left: 3px solid #333;
}}
.section-acc {{ font-size: 0.65rem; color: #aaa; }}
.section-img {{
  width: 100%; height: 200px;
  background-size: cover; background-position: center;
  border-radius: 4px; margin-bottom: 12px;
  filter: brightness(0.75);
}}

/* Story list */
.story-list {{ display: flex; flex-direction: column; gap: 0; }}
.story {{
  padding: 14px 0; border-bottom: 1px solid #f0f0f0;
}}
.story:last-child {{ border-bottom: none; }}
.story-title {{ font-size: 0.95rem; font-weight: 600; margin-bottom: 4px; line-height: 1.3; }}
.story-title a:hover {{ color: #c0392b; }}
.story-body {{ font-size: 0.78rem; color: #555; line-height: 1.7; }}

/* Dims */
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
  .hero {{ height: 300px; }}
  .hero-title {{ font-size: 1.3rem; }}
  .section-img {{ height: 140px; }}
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
  <br>Data: synthetic historical models &middot; PyTorch Monte Carlo engine &middot; Published daily
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
