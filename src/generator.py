"""
News site generator — editorial stories from the multi-dimensional sports engine.
"""

import json, os
from datetime import datetime

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from src.world_sports import SPORTS


def generate_world_news(engine, takes, backtest_results):
    """Generate a news site with multi-sport editorial content."""

    # Group takes by sport
    by_sport = {}
    for t in takes:
        by_sport.setdefault(t["sport"], []).append(t)

    timestamp = datetime.utcnow().strftime("%B %d, %Y at %H:%M UTC")

    # Header navigation
    sport_nav = "".join(
        f'<span class="nav-sport" data-sport="{key}">{SPORTS[key]["name"]}</span>'
        for key in ["Cricket_T20", "EPL", "NBA", "NFL", "MLB", "NHL", "TENNIS"]
    )

    # Render articles for each sport
    sections = ""
    for key in ["Cricket_T20", "EPL", "NBA", "NFL", "MLB", "NHL", "TENNIS"]:
        sport_takes = by_sport.get(key, [])
        if not sport_takes:
            continue

        bt = backtest_results.get(key, {})
        articles = ""
        for t in sport_takes:
            pred = t.get("prediction", {})
            dims = pred.get("dimensions", []) if pred else []
            dim_bars = "".join(
                '<div class="dim-row"><span class="dim-label">{}</span><div class="dim-track"><div class="dim-fill" style="width:{}%"></div></div><span class="dim-val">{:.0f}%</span></div>'.format(
                    d["name"], d["value"], d["value"])
                for d in dims
            ) if dims else ""

            cat_icon = {"preview": "&#128065;", "analysis": "&#128200;", "player": "&#127936;",
                        "deep_dive": "&#128214;", "season": "&#128200;"}.get(t["category"], "&#128196;")

            articles += f"""
            <article class="story" data-sport="{key}">
              <div class="story-meta">
                <span class="story-cat">{cat_icon} {t['category']}</span>
                <span class="story-sport">{SPORTS[key]['name']}</span>
              </div>
              <h2 class="story-title">{t['title']}</h2>
              <div class="story-body">{t['body'].replace(chr(10), '<br>')}</div>
              {f'<div class="story-dims"><div class="dims-title">Factor Analysis</div>{dim_bars}</div>' if dim_bars else ''}
            </article>"""

        sections += f"""
        <div class="sport-section" id="sport-{key}">
          <div class="section-header">
            <h2 class="section-title">{SPORTS[key]['name']}</h2>
            <span class="section-acc">Backtest: {bt.get('accuracy', '?')}% accuracy</span>
          </div>
          <div class="story-grid">{articles}</div>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>HAL 9000 — World Sports Intelligence</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Prata&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{--bg:#f8f7f4;--card:#fff;--text:#1c1c1a;--text2:#5a5a56;--text3:#9a9a96;--accent:#1a3a8a;--accent2:#d4e0ff;--ok:#1a7a3a;--miss:#c04040;--border:#e2e1dd;--radius:8px;--font:'Inter',sans-serif;--display:'Prata',Georgia,serif;--mono:'JetBrains Mono',monospace}}
body{{background:var(--bg);color:var(--text);font-family:var(--font);font-size:16px;line-height:1.7;-webkit-font-smoothing:antialiased}}
.container{{max-width:800px;margin:0 auto;padding:0 20px}}

/* Masthead */
.masthead{{padding:24px 0 14px;border-bottom:2px solid var(--text);margin-bottom:20px}}
.masthead .logo{{font-family:var(--display);font-size:1.5rem;letter-spacing:-0.02em}}
.masthead .logo .accent{{color:var(--accent)}}
.masthead .sub{{font-size:0.7rem;color:var(--text2);font-family:var(--mono);margin-top:2px}}
.masthead .date{{font-size:0.65rem;color:var(--text3);font-family:var(--mono);margin-top:4px}}

/* Sport nav */
.sport-nav{{display:flex;gap:6px;flex-wrap:wrap;padding:12px 0;border-bottom:1px solid var(--border);margin-bottom:24px}}
.nav-sport{{font-size:0.7rem;font-weight:500;color:var(--text2);padding:4px 12px;border-radius:20px;border:1px solid var(--border);cursor:pointer;transition:all 0.15s;font-family:var(--mono)}}
.nav-sport:hover{{background:var(--accent);color:#fff;border-color:var(--accent)}}

/* Section */
.sport-section{{margin-bottom:36px}}
.section-header{{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:14px}}
.section-title{{font-family:var(--display);font-size:1.2rem;font-weight:400;letter-spacing:-0.01em}}
.section-acc{{font-size:0.6rem;color:var(--text3);font-family:var(--mono)}}

/* Story grid */
.story-grid{{display:grid;gap:14px}}
.story{{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:20px}}
.story-meta{{display:flex;gap:10px;align-items:center;margin-bottom:6px;font-size:0.6rem}}
.story-cat{{color:var(--text3);font-family:var(--mono);text-transform:uppercase;letter-spacing:0.06em}}
.story-sport{{background:var(--accent2);color:var(--accent);padding:1px 8px;border-radius:3px;font-weight:500}}
.story-title{{font-size:1.05rem;font-weight:600;line-height:1.25;margin-bottom:8px;letter-spacing:-0.01em}}
.story-body{{font-size:0.82rem;color:var(--text2);line-height:1.7}}
.story-body br{{margin-bottom:6px;display:block;content:''}}

/* Dimension bars */
.story-dims{{margin-top:12px;padding-top:10px;border-top:1px solid var(--border)}}
.dims-title{{font-size:0.6rem;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;color:var(--text3);margin-bottom:6px;font-family:var(--mono)}}
.dim-row{{display:flex;align-items:center;gap:8px;padding:2px 0;font-size:0.68rem}}
.dim-label{{width:120px;color:var(--text2);font-size:0.62rem}}
.dim-track{{flex:1;height:5px;background:var(--border);border-radius:3px;overflow:hidden}}
.dim-fill{{height:100%;background:var(--accent);border-radius:3px}}
.dim-val{{width:30px;text-align:right;font-family:var(--mono);color:var(--text2);font-size:0.6rem}}

/* Footer */
.footer{{border-top:1px solid var(--border);padding:20px 0 32px;margin-top:10px;text-align:center;font-size:0.62rem;color:var(--text3);font-family:var(--mono)}}
</style>
</head>
<body>
<div class="container">

<header class="masthead">
  <div class="logo"><span class="accent">HAL</span> 9000 Intelligence</div>
  <div class="sub">7-Dimensional Sports Prediction · PyTorch Engine · Multi-Sport</div>
  <div class="date">{timestamp} · {len(takes)} stories across {len(engine.predictors)} sports</div>
</header>

<nav class="sport-nav">{sport_nav}</nav>

{sections}

<footer class="footer">
  HAL 9000 — Predictions use 7 dimensions: Head-to-Head History, Player Matchups (22% weight),
  Venue &amp; Conditions (15%), Recent Form (15%), Tournament Context (10%),
  Team News Sentiment (10%), Player Health (10%).
  <br><br>
  Numbers stay in the engine. Stories go on the page.
</footer>

</div>

<script>
document.querySelectorAll('.nav-sport').forEach(btn => {{
  btn.addEventListener('click', function() {{
    const sport = this.dataset.sport;
    document.getElementById('sport-' + sport)?.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
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
