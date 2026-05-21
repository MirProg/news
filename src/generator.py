"""
Kubrick/2001 news generator — cold, sterile, minimal.
HAL 9000 speaks in editorial predictions across all world sports.
"""

import os, random
from datetime import datetime

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from src.world_sports import SPORTS

sport_keys = ["Cricket_T20", "EPL", "NBA", "NFL", "MLB", "NHL", "TENNIS", "Rugby", "F1", "MMA", "Boxing"]


def _dim_bars(pred):
    dims = pred.get("dimensions", []) if pred else []
    if not dims:
        return ""
    bars = "".join(
        '<div class="dim"><span class="dim-l">{}</span><div class="dim-t"><div class="dim-f" style="width:{}%"></div></div><span class="dim-r">{:.0f}</span></div>'.format(
            d["name"], d["value"], d["value"])
        for d in dims
    )
    return f'<div class="dims"><div class="dim-h">FACTOR ANALYSIS — 7 DIMENSIONS</div>{bars}</div>'


def _narrative_kubrick(pred):
    """Cold, clinical HAL voice for a single prediction."""
    t1 = pred["team1"]
    t2 = pred["team2"]
    wp = pred["t1_win_pct"]
    parts = []

    if abs(wp - 50) < 3:
        parts.append(f"This fixture between {t1} and {t2} resists deterministic analysis. No single factor provides sufficient signal to separate the two sides with statistical confidence. The outcome will be determined by stochastic variation within the expected range.")
    elif wp > 72:
        parts.append(f"HAL's composite model assigns {t1} a probability of {wp:.0f}%. The margin is decisive across multiple independent analytical dimensions. A contrary outcome would represent a statistically significant deviation from the expected distribution.")
    elif wp > 60:
        parts.append(f"{t1} enters with a measurable advantage ({wp:.0f}%), concentrated primarily in matchup dynamics and recent form metrics. The signal is clear but not absolute — approximately 4 in 10 simulations produce an alternative result.")
    else:
        parts.append(f"HAL registers a slight tilt toward {t1 if wp > 50 else t2} ({max(wp, 100-wp):.0f}%), though the margin falls within the model's noise threshold. Matches of this character typically resolve through isolated tactical events rather than systemic advantage.")

    # Score projection
    if pred.get("pred_score1") is not None:
        parts.append(f"Projected scoreline: {t1} {pred['pred_score1']:.0f} – {pred['pred_score2']:.0f} {t2}.")

    sorted_dims = sorted(pred["dimensions"], key=lambda d: -abs(d["value"] - 50))[:3]
    if sorted_dims:
        factors = "; ".join(f"{d['name']} ({d['story']})" for d in sorted_dims)
        parts.append(f"Primary contributors: {factors}.")

    return "\n\n".join(parts)


def generate_world_news(engine, takes, backtest_results):
    by_sport = {}
    for t in takes:
        by_sport.setdefault(t["sport"], []).append(t)

    timestamp = datetime.utcnow().strftime("%Y.%m.%d — %H:%M UTC")
    total_stories = len(takes)
    total_sports = len([k for k in sport_keys if k in engine.predictors])

    # Sport filter buttons
    sport_btns = ""
    sections = ""
    for key in sport_keys:
        if key not in engine.predictors:
            continue
        sport_takes = by_sport.get(key, [])
        bt = backtest_results.get(key, {})

        cards = ""
        for t in sport_takes:
            pred = t.get("prediction", {})

            # Card style based on category
            cat_colors = {
                "preview": "var(--blue)",
                "analysis": "var(--cyan)",
                "player": "var(--amber)",
                "deep_dive": "var(--red)",
                "season": "var(--green)",
            }
            accent = cat_colors.get(t["category"], "var(--red)")

            body_html = t["body"].replace("\n", "<br>")
            dims_html = _dim_bars(pred) if pred else ""

            cards += f"""
        <div class="card" data-cat="{t['category']}" style="--card-accent:{accent}">
          <div class="card-label">{t['category'].upper()}</div>
          <h3 class="card-title">{t['title']}</h3>
          <div class="card-body">{body_html}</div>
          {dims_html}
        </div>"""

        sections += f"""
      <section class="sport" id="{key}">
        <div class="sport-hdr">
          <div class="sport-name">{SPORTS[key]['name']}</div>
          <div class="sport-meta">
            <span>{bt.get('accuracy', '?')}% ACCURACY</span>
            <span>{len(sport_takes)} STORIES</span>
          </div>
        </div>
        <div class="grid">{cards}</div>
      </section>"""

        sport_btns += f'<button class="sb" data-target="{key}">{SPORTS[key]["name"]}</button>'

    # Pre-generate HAL eye SVG
    hal_eye = """<svg viewBox="0 0 120 120" class="hal-eye">
      <circle cx="60" cy="60" r="55" fill="none" stroke="var(--red)" stroke-width="1.5" opacity="0.3"/>
      <circle cx="60" cy="60" r="45" fill="none" stroke="var(--red)" stroke-width="1" opacity="0.4"/>
      <circle cx="60" cy="60" r="35" fill="none" stroke="var(--red)" stroke-width="2" opacity="0.5"/>
      <circle cx="60" cy="60" r="25" fill="none" stroke="var(--red)" stroke-width="3" opacity="0.6"/>
      <circle cx="60" cy="60" r="15" fill="none" stroke="var(--red)" stroke-width="4" opacity="0.8"/>
      <circle cx="60" cy="60" r="6" fill="var(--red)" opacity="0.9"/>
      <circle cx="60" cy="60" r="3" fill="#fff" opacity="0.6">
        <animate attributeName="opacity" values="0.6;0.2;0.6" dur="2s" repeatCount="indefinite"/>
      </circle>
    </svg>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>HAL 9000 — WORLD SPORTS INTELLIGENCE</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
:root {{
  --bg: #0a0a0a;
  --bg2: #111111;
  --card: #141414;
  --card2: #1a1a1a;
  --border: #222;
  --border2: #333;
  --text: #d4d4d4;
  --text2: #888;
  --text3: #555;
  --red: #e74c3c;
  --red-glow: rgba(231, 76, 60, 0.15);
  --blue: #3498db;
  --cyan: #2ecc71;
  --amber: #f39c12;
  --green: #2ecc71;
  --mono: 'Space Mono', monospace;
  --sans: 'Inter', -apple-system, sans-serif;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html {{ background: var(--bg); }}
body {{
  background: var(--bg);
  color: var(--text);
  font-family: var(--sans);
  font-size: 14px;
  line-height: 1.7;
  -webkit-font-smoothing: antialiased;
  overflow-x: hidden;
}}

/* ── Star field ── */
#stars {{
  position: fixed;
  top: 0; left: 0;
  width: 100vw; height: 100vh;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}}

/* ── Container ── */
.container {{
  position: relative;
  z-index: 1;
  max-width: 900px;
  margin: 0 auto;
  padding: 0 24px 60px;
}}

/* ── HAL Masthead ── */
.masthead {{
  padding: 40px 0 24px;
  text-align: center;
  border-bottom: 1px solid var(--border);
  margin-bottom: 32px;
  position: relative;
}}
.masthead .eye-wrap {{
  width: 64px;
  height: 64px;
  margin: 0 auto 12px;
  animation: pulse-glow 3s ease-in-out infinite;
}}
@keyframes pulse-glow {{
  0%, 100% {{ filter: drop-shadow(0 0 6px rgba(231,76,60,0.3)); }}
  50% {{ filter: drop-shadow(0 0 20px rgba(231,76,60,0.7)); }}
}}
.masthead .title {{
  font-family: var(--mono);
  font-size: 0.6rem;
  letter-spacing: 0.35em;
  color: var(--red);
  font-weight: 700;
  margin-bottom: 4px;
}}
.masthead .subtitle {{
  font-family: var(--mono);
  font-size: 0.5rem;
  letter-spacing: 0.15em;
  color: var(--text2);
}}
.masthead .ts {{
  font-family: var(--mono);
  font-size: 0.45rem;
  letter-spacing: 0.1em;
  color: var(--text3);
  margin-top: 8px;
}}

/* ── Sport Filter Bar ── */
.filter {{
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  justify-content: center;
  padding: 16px 0 24px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 28px;
}}
.sb {{
  background: var(--card);
  border: 1px solid var(--border);
  color: var(--text2);
  font-family: var(--mono);
  font-size: 0.45rem;
  letter-spacing: 0.05em;
  padding: 5px 12px;
  border-radius: 0;
  cursor: pointer;
  transition: all 0.2s;
}}
.sb:hover {{
  background: var(--card2);
  border-color: var(--text3);
  color: var(--text);
}}

/* ── Backtest Overview ── */
.overview {{
  margin-bottom: 36px;
  border: 1px solid var(--border);
  padding: 20px;
}}
.overview-hdr {{
  font-family: var(--mono);
  font-size: 0.5rem;
  letter-spacing: 0.2em;
  color: var(--text3);
  margin-bottom: 12px;
}}
.overview-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
  gap: 8px;
}}
.ov-item {{
  text-align: center;
  padding: 8px 4px;
  border: 1px solid var(--border);
}}
.ov-name {{
  font-family: var(--mono);
  font-size: 0.4rem;
  color: var(--text3);
  letter-spacing: 0.05em;
  margin-bottom: 4px;
}}
.ov-acc {{
  font-family: var(--mono);
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--text);
}}

/* ── Sport Section ── */
.sport {{
  margin-bottom: 40px;
}}
.sport-hdr {{
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
}}
.sport-name {{
  font-family: var(--mono);
  font-size: 0.55rem;
  letter-spacing: 0.2em;
  color: var(--text);
}}
.sport-meta {{
  display: flex;
  gap: 12px;
  font-family: var(--mono);
  font-size: 0.4rem;
  color: var(--text3);
  letter-spacing: 0.05em;
}}

/* ── Card Grid ── */
.grid {{
  display: flex;
  flex-direction: column;
  gap: 16px;
}}

/* ── Card ── */
.card {{
  background: var(--card);
  border: 1px solid var(--border);
  border-left: 3px solid var(--card-accent, var(--red));
  padding: 20px 24px;
  transition: border-color 0.2s, background 0.2s;
}}
.card:hover {{
  background: var(--card2);
  border-color: var(--border2);
}}
.card-label {{
  font-family: var(--mono);
  font-size: 0.4rem;
  letter-spacing: 0.15em;
  color: var(--card-accent, var(--red));
  margin-bottom: 4px;
}}
.card-title {{
  font-family: var(--mono);
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  line-height: 1.3;
  margin-bottom: 8px;
  color: var(--text);
}}
.card-body {{
  font-size: 0.68rem;
  line-height: 1.8;
  color: var(--text2);
}}
.card-body br {{
  display: block;
  margin-bottom: 6px;
  content: '';
}}

/* ── Dimension Bars ── */
.dims {{
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid var(--border);
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 3px 16px;
}}
.dim-h {{
  grid-column: 1 / -1;
  font-family: var(--mono);
  font-size: 0.38rem;
  letter-spacing: 0.15em;
  color: var(--text3);
  margin-bottom: 4px;
}}
.dim {{
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 1px 0;
}}
.dim-l {{
  font-family: var(--mono);
  font-size: 0.4rem;
  color: var(--text3);
  width: 80px;
  flex-shrink: 0;
}}
.dim-t {{
  flex: 1;
  height: 3px;
  background: var(--border2);
  border-radius: 0;
  overflow: hidden;
}}
.dim-f {{
  height: 100%;
  background: var(--red);
  border-radius: 0;
}}
.dim-r {{
  font-family: var(--mono);
  font-size: 0.4rem;
  color: var(--text2);
  width: 22px;
  text-align: right;
}}

/* ── Footer ── */
.footer {{
  margin-top: 48px;
  padding: 24px 0 40px;
  border-top: 1px solid var(--border);
  text-align: center;
  font-family: var(--mono);
  font-size: 0.4rem;
  letter-spacing: 0.1em;
  color: var(--text3);
  line-height: 2;
}}

/* ── Responsive ── */
@media(max-width:600px) {{
  .sport-hdr {{ flex-direction: column; gap: 4px; }}
  .overview-grid {{ grid-template-columns: repeat(3, 1fr); }}
  .dims {{ grid-template-columns: 1fr; }}
}}
</style>
</head>
<body>

<div id="stars"></div>

<div class="container">

<header class="masthead">
  <div class="eye-wrap">{hal_eye}</div>
  <div class="title">HAL 9000</div>
  <div class="subtitle">WORLD SPORTS INTELLIGENCE — 7 DIMENSIONAL PREDICTION ENGINE</div>
  <div class="ts">{timestamp} · {total_stories} STORIES · {total_sports} SPORTS</div>
</header>

<nav class="filter">{sport_btns}</nav>

<div class="overview">
  <div class="overview-hdr">MODEL ACCURACY — BACKTEST VALIDATION</div>
  <div class="overview-grid">
    {''.join(f'<div class="ov-item"><div class="ov-name">{SPORTS[k]["name"]}</div><div class="ov-acc">{backtest_results.get(k, {}).get("accuracy", "?")}%</div></div>' for k in sport_keys if k in backtest_results)}
  </div>
</div>

{sections}

<footer class="footer">
  H A L &nbsp; 9 0 0 0<br>
  7 DIMENSIONS · H2H HISTORY · PLAYER MATCHUPS · VENUE &amp; CONDITIONS · RECENT FORM<br>
  TOURNAMENT CONTEXT · TEAM SENTIMENT · PLAYER HEALTH<br>
  <br>
  "I am putting myself to the fullest possible use, which is all I think that any conscious entity can ever hope to do."
</footer>

</div>

<script>
// generate static stars
(function() {{
  const s = document.getElementById('stars');
  for (let i = 0; i < 120; i++) {{
    const d = document.createElement('div');
    const size = Math.random() * 1.5 + 0.5;
    const x = Math.random() * 100;
    const y = Math.random() * 100;
    const o = Math.random() * 0.5 + 0.1;
    d.style.cssText = 'position:absolute;left:' + x + '%;top:' + y + '%;width:' + size + 'px;height:' + size + 'px;background:rgba(255,255,255,' + o + ');border-radius:50%;';
    s.appendChild(d);
  }}
}})();

// sport filter scroll
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
