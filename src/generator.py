"""
Colorful news generator — clean, bright, editorial.
"""

import os
from datetime import datetime

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from src.world_sports import SPORTS

sport_keys = ["Cricket_T20", "EPL", "NBA", "NFL", "MLB", "NHL", "TENNIS", "Rugby", "F1", "MMA", "Boxing"]

SPORT_COLORS = {
    "Cricket_T20": "#e67e22", "EPL": "#2ecc71", "NBA": "#e74c3c", "NFL": "#3498db",
    "MLB": "#9b59b6", "NHL": "#1abc9c", "TENNIS": "#f1c40f", "Rugby": "#e74c3c",
    "F1": "#e67e22", "MMA": "#c0392b", "Boxing": "#2980b9",
}


def _dim_bars(pred):
    dims = pred.get("dimensions", []) if pred else []
    if not dims:
        return ""
    bars = "".join(
        '<div class="dim"><span class="dim-l">{}</span><div class="dim-t"><div class="dim-f" style="width:{}%"></div></div><span class="dim-r">{:.0f}</span></div>'.format(
            d["name"], d["value"], d["value"])
        for d in dims
    )
    return f'<div class="dims"><div class="dim-h">FACTOR BREAKDOWN — 7 DIMENSIONS</div>{bars}</div>'


def _narrative(pred):
    t1 = pred["team1"]; t2 = pred["team2"]; wp = pred["t1_win_pct"]
    if abs(wp - 50) < 3:
        return f"This one's too close to call. {t1} and {t2} are evenly matched across all seven analytical dimensions — head-to-head history, player matchups, venue conditions, recent form, tournament context, team sentiment, and player health. Expect a tight contest."
    if wp > 70:
        return f"All signs point to {t1}. The model sees a clear advantage ({wp:.0f}%) driven by superior matchup dynamics and recent form. Multiple dimensions align — this is one of the most confident predictions in the current cycle."
    if wp > 60:
        return f"{t1} enters as the favorite ({wp:.0f}%). The edge comes primarily from individual matchups and venue familiarity, though the margin leaves room for an upset in roughly 3 out of 10 simulations."
    return f"A slight lean toward {t1 if wp > 50 else t2} ({max(wp, 100-wp):.0f}%). This match could go either way — expect the outcome to be decided by isolated moments rather than systemic advantage."


def generate_world_news(engine, takes, backtest_results):
    by_sport = {}
    for t in takes:
        by_sport.setdefault(t["sport"], []).append(t)

    timestamp = datetime.utcnow().strftime("%B %d, %Y · %H:%M UTC")
    total_stories = len(takes)
    total_sports = len([k for k in sport_keys if k in engine.predictors])

    sport_btns = ""
    sections = ""
    for key in sport_keys:
        if key not in engine.predictors:
            continue
        sport_takes = by_sport.get(key, [])
        bt = backtest_results.get(key, {})
        color = SPORT_COLORS.get(key, "#666")

        cards = ""
        for t in sport_takes:
            pred = t.get("prediction", {})
            cat_icons = {"preview": "&#128752;", "analysis": "&#128200;", "player": "&#127939;",
                         "deep_dive": "&#128214;", "season": "&#128200;"}
            body_html = t["body"].replace("\n", "<br>")
            dims_html = _dim_bars(pred) if pred else ""

            cards += f"""
        <div class="card" style="border-top: 3px solid {color}">
          <div class="card-meta">
            <span class="card-cat">{cat_icons.get(t['category'], '&#128196;')} {t['category']}</span>
          </div>
          <h3 class="card-title">{t['title']}</h3>
          <div class="card-body">{body_html}</div>
          {dims_html}
        </div>"""

        sections += f"""
      <section class="sport" id="{key}">
        <div class="sport-hdr" style="--sc: {color}">
          <div>
            <div class="sport-name">{SPORTS[key]['name']}</div>
            <div class="sport-acc">{bt.get('accuracy', '?')}% backtest accuracy — {len(sport_takes)} stories</div>
          </div>
          <span class="sport-badge">{bt.get('accuracy', '?')}%</span>
        </div>
        <div class="grid">{cards}</div>
      </section>"""

        sport_btns += f'<button class="sb" data-target="{key}" style="--sc: {color}">{SPORTS[key]["name"]}</button>'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>World Sports Predictions — Multi-Dimensional Intelligence</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Playfair+Display:ital,wght@0,500;0,700;1,500&display=swap" rel="stylesheet">
<style>
:root {{
  --bg: #f5f3ef;
  --card: #fff;
  --card2: #faf9f6;
  --border: #e8e5df;
  --text: #1a1a18;
  --text2: #6b6a66;
  --text3: #9e9d99;
  --font: 'Inter', -apple-system, sans-serif;
  --display: 'Playfair Display', Georgia, serif;
  --mono: 'SF Mono', 'SFMono-Regular', 'Consolas', monospace;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  background: var(--bg);
  color: var(--text);
  font-family: var(--font);
  font-size: 15px;
  line-height: 1.7;
  -webkit-font-smoothing: antialiased;
}}
.container {{ max-width: 880px; margin: 0 auto; padding: 0 24px 60px; }}

/* Masthead */
.masthead {{
  padding: 36px 0 20px;
  margin-bottom: 24px;
  border-bottom: 2px solid var(--text);
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}}
.masthead .logo {{
  font-family: var(--display);
  font-size: 1.6rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.1;
}}
.masthead .logo em {{ font-style: italic; color: #c0392b; }}
.masthead .tagline {{ font-size: 0.7rem; color: var(--text3); font-family: var(--mono); margin-top: 2px; letter-spacing: 0.02em; }}
.masthead .ts {{ font-size: 0.6rem; color: var(--text3); font-family: var(--mono); text-align: right; }}

/* Filter */
.filter {{ display: flex; gap: 5px; flex-wrap: wrap; padding: 14px 0 20px; border-bottom: 1px solid var(--border); margin-bottom: 28px; }}
.sb {{
  background: var(--card);
  border: 1px solid var(--border);
  color: var(--text2);
  font-family: var(--mono);
  font-size: 0.6rem;
  padding: 5px 14px;
  cursor: pointer;
  transition: all 0.15s;
  border-radius: 4px;
}}
.sb:hover {{ background: var(--sc, #eee); color: #fff; border-color: var(--sc, #eee); }}

/* Overview */
.overview {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 8px;
  margin-bottom: 32px;
}}
.ov-item {{
  background: var(--card);
  border: 1px solid var(--border);
  padding: 10px 6px;
  text-align: center;
  border-radius: 6px;
  position: relative;
  overflow: hidden;
}}
.ov-item::before {{
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: var(--ov-c, #ddd);
}}
.ov-name {{ font-size: 0.55rem; color: var(--text2); font-family: var(--mono); letter-spacing: 0.03em; margin-bottom: 3px; }}
.ov-acc {{ font-size: 1rem; font-weight: 700; font-family: var(--mono); }}

/* Sport section */
.sport {{ margin-bottom: 36px; }}
.sport-hdr {{
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 14px; padding-bottom: 8px;
  border-bottom: 2px solid var(--sc, var(--border));
}}
.sport-name {{ font-family: var(--display); font-size: 1.15rem; font-weight: 700; letter-spacing: -0.01em; }}
.sport-acc {{ font-size: 0.6rem; color: var(--text3); font-family: var(--mono); margin-top: 2px; }}
.sport-badge {{
  background: var(--sc, #eee);
  color: #fff;
  font-family: var(--mono);
  font-size: 0.65rem;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 4px;
}}

/* Grid */
.grid {{ display: flex; flex-direction: column; gap: 14px; }}

/* Card */
.card {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 22px 24px;
  transition: box-shadow 0.2s;
}}
.card:hover {{ box-shadow: 0 2px 12px rgba(0,0,0,0.05); }}
.card-meta {{ font-size: 0.6rem; color: var(--text3); font-family: var(--mono); margin-bottom: 4px; }}
.card-cat {{ letter-spacing: 0.06em; }}
.card-title {{ font-size: 1.05rem; font-weight: 600; line-height: 1.25; margin-bottom: 8px; letter-spacing: -0.01em; }}
.card-body {{ font-size: 0.82rem; color: var(--text2); line-height: 1.75; }}
.card-body br {{ display: block; margin-bottom: 6px; content: ''; }}

/* Dims */
.dims {{ margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--border); display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 2px 16px; }}
.dim-h {{ grid-column: 1 / -1; font-size: 0.55rem; font-weight: 600; letter-spacing: 0.04em; color: var(--text3); margin-bottom: 4px; font-family: var(--mono); }}
.dim {{ display: flex; align-items: center; gap: 6px; padding: 2px 0; }}
.dim-l {{ font-size: 0.6rem; color: var(--text2); width: 90px; flex-shrink: 0; }}
.dim-t {{ flex: 1; height: 5px; background: var(--border); border-radius: 3px; overflow: hidden; }}
.dim-f {{ height: 100%; background: #c0392b; border-radius: 3px; }}
.dim-r {{ font-size: 0.55rem; font-family: var(--mono); color: var(--text2); width: 24px; text-align: right; }}

/* Footer */
.footer {{
  margin-top: 48px; padding: 24px 0 40px;
  border-top: 1px solid var(--border);
  text-align: center;
  font-size: 0.6rem; color: var(--text3); font-family: var(--mono);
}}
.footer em {{ font-style: italic; color: var(--text2); }}

@media(max-width:600px) {{
  .masthead {{ flex-direction: column; align-items: flex-start; gap: 4px; }}
  .masthead .ts {{ text-align: left; }}
  .overview {{ grid-template-columns: repeat(3, 1fr); }}
}}
</style>
</head>
<body>
<div class="container">

<header class="masthead">
  <div>
    <div class="logo">World Sports <em>Predictions</em></div>
    <div class="tagline">7-dimensional deep intelligence — PyTorch powered</div>
  </div>
  <div class="ts">{timestamp}<br>{total_stories} stories · {total_sports} sports</div>
</header>

<nav class="filter">{sport_btns}</nav>

<div class="overview">
  {''.join(f'<div class="ov-item" style="--ov-c: {SPORT_COLORS.get(k, "#666")}"><div class="ov-name">{SPORTS[k]["name"]}</div><div class="ov-acc">{backtest_results.get(k, {}).get("accuracy", "?")}%</div></div>' for k in sport_keys if k in backtest_results)}
</div>

{sections}

<footer class="footer">
  Predictions use 7 dimensions: Head-to-Head History (18%), Player Matchups (22%), Venue &amp; Conditions (15%),
  Recent Form (15%), Tournament Context (10%), Team Sentiment (10%), Player Health (10%).<br>
  <em>Numbers stay in the engine. Stories go on the page.</em>
</footer>

</div>
<script>
document.querySelectorAll('.sb').forEach(b => {{
  b.addEventListener('click', () => {{
    const el = document.getElementById(b.dataset.target);
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
