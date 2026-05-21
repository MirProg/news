"""
Bold, dramatic, image-rich magazine — hero section, vibrant, alive.
"""

import os, random
from datetime import datetime

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from src.world_sports import SPORTS

sport_keys = ["Cricket_T20", "EPL", "NBA", "NFL", "MLB", "NHL", "TENNIS", "Rugby", "F1", "MMA", "Boxing"]

SPORT_IMAGES = {
    "Cricket_T20": "https://images.unsplash.com/photo-1531415074968-036ba1b575da?w=1200&h=700&fit=crop",
    "EPL": "https://images.unsplash.com/photo-1575361204480-aadea25e6e68?w=1200&h=700&fit=crop",
    "NBA": "https://images.unsplash.com/photo-1546519638-68e109498ffc?w=1200&h=700&fit=crop",
    "NFL": "https://images.unsplash.com/photo-1566577739112-5180d4bf9391?w=1200&h=700&fit=crop",
    "MLB": "https://images.unsplash.com/photo-1562077772-1fd6ddb2ed5a?w=1200&h=700&fit=crop",
    "NHL": "https://images.unsplash.com/photo-1515703407324-5d7532e6918f?w=1200&h=700&fit=crop",
    "TENNIS": "https://images.unsplash.com/photo-1595435934249-5df7ed86e1c0?w=1200&h=700&fit=crop",
    "Rugby": "https://images.unsplash.com/photo-1511882150382-4210563a7220?w=1200&h=700&fit=crop",
    "F1": "https://images.unsplash.com/photo-1630673240362-ed9f2121eb1a?w=1200&h=700&fit=crop",
    "MMA": "https://images.unsplash.com/photo-1599058917212-d750089bc07e?w=1200&h=700&fit=crop",
    "Boxing": "https://images.unsplash.com/photo-1549719386-74dfcbf7dbed?w=1200&h=700&fit=crop",
}


def _story(pred):
    t1 = pred["team1"]; t2 = pred["team2"]; wp = pred["t1_win_pct"]
    dims = pred.get("dimensions", [])

    lines = []
    if abs(wp - 50) < 3:
        lines.append(f"This is the kind of matchup that keeps you up at night. {t1} and {t2} are so evenly matched that every dimension — from head-to-head history to player matchups, from venue conditions to recent form — cancels out into perfect, maddening equilibrium. This is not a prediction. This is an admission: nobody knows. And that is exactly why you have to watch.")
    elif wp > 72:
        lines.append(f"This is not a fair fight. {t1} comes into this match with every possible advantage tilted in their favor. The model — which does not get excited, which does not have favorites — registers a signal so strong it borders on the inevitable. Every dimension points the same way.")
        if dims:
            top = sorted(dims, key=lambda d: -abs(d["value"] - 50))[0]
            lines.append(f"The decisive edge comes from {top['name'].lower()}, where the gap is widest. If {t2} pulls this off, it will be the kind of upset people talk about for years.")
    elif wp > 60:
        lines.append(f"{t1} has the edge, and the numbers back it up. Not a landslide — but a clear, measurable advantage that cuts across multiple dimensions.")
        if dims:
            tops = sorted(dims, key=lambda d: -abs(d["value"] - 50))[:2]
            lines.append(f"The two biggest factors — {tops[0]['name'].lower()} and {tops[1]['name'].lower()} — both swing in {t1}'s direction, creating a compound effect that {t2} will need something special to overcome.")
        lines.append(f"It can be done. It just takes something extraordinary.")
    else:
        lines.append(f"The numbers say this is close. Very close. {t1 if wp > 50 else t2} has the slimmest of edges — the kind that could vanish on a single bounce, a single call, a single moment of brilliance or disaster.")
        if dims:
            top = sorted(dims, key=lambda d: -abs(d["value"] - 50))[0]
            lines.append(f"The only dimension providing any separation at all is {top['name'].lower()}, and even that is narrow.")
        lines.append(f"Games like this are why we love sports. The data shrugs. The human heart races. That gap is everything.")

    if pred.get("pred_score1") is not None:
        lines.append(f"Projected score: {t1} {pred['pred_score1']:.0f} — {t2} {pred['pred_score2']:.0f}.")
    lines.append(f"Now go watch what happens.")

    return "\n\n".join(lines)


def generate_world_news(engine, takes, backtest_results):
    by_sport = {}
    for t in takes:
        by_sport.setdefault(t["sport"], []).append(t)

    timestamp = datetime.utcnow().strftime("%B %d, %Y")

    scored = []
    for key in sport_keys:
        if key not in engine.predictors:
            continue
        for t in by_sport.get(key, []):
            pred = t.get("prediction", {})
            conf = abs(pred.get("t1_win_pct", 50) - 50) if pred else 0
            scored.append((conf, key, t))
    scored.sort(key=lambda x: -x[0])

    nav_items = ""
    all_sections = ""

    for i, (conf, key, t) in enumerate(scored):
        pred = t.get("prediction", {})
        img = SPORT_IMAGES.get(key, "")
        body = _story(pred) if pred else ""
        spec = SPORTS[key]
        sect_id = f"s{key}"

        label = f"{spec['name']} · {backtest_results.get(key, {}).get('accuracy', '?')}% accuracy"

        if i == 0:
            # Hero section — full bleed with overlay
            all_sections += f"""
  <section class="hero" id="{sect_id}" style="background-image:url('{img}')">
    <div class="hero-overlay"></div>
    <div class="hero-content">
      <p class="hero-label">{label}</p>
      <h1 class="hero-title">{t['title']}</h1>
      <div class="hero-body"><p>{body[:200]}…</p></div>
    </div>
  </section>"""
        elif i < 5:
            # Secondary stories — image on left, text on right
            all_sections += f"""
  <section class="feature" id="{sect_id}">
    <div class="feature-img" style="background-image:url('{img}')"></div>
    <div class="feature-content">
      <p class="feature-label">{label}</p>
      <h2 class="feature-title">{t['title']}</h2>
      <div class="feature-body"><p>{body}</p></div>
    </div>
  </section>"""
        else:
            # Compact list items
            all_sections += f"""
  <section class="compact" id="{sect_id}">
    <div class="compact-img" style="background-image:url('{img}')"></div>
    <div class="compact-content">
      <p class="compact-label">{label}</p>
      <h3 class="compact-title">{t['title']}</h3>
      <div class="compact-body"><p>{body[:150]}…</p></div>
    </div>
  </section>"""

        nav_items += f'<a class="nav-link" href="#{sect_id}" data-key="{sect_id}">{spec["name"]}</a>'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Beyond the Game — {timestamp}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Playfair+Display:ital,wght@0,700;0,900;1,700;1,900&display=swap" rel="stylesheet">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
:root {{
  --bg: #f4f2ed;
  --card: #ffffff;
  --text: #1a1a16;
  --text2: #55534e;
  --text3: #999792;
  --red: #d42a2a;
  --font: 'Inter', -apple-system, sans-serif;
  --display: 'Playfair Display', Georgia, serif;
}}
body {{
  background: var(--bg); color: var(--text);
  font-family: var(--font); font-size: 15px; line-height: 1.7;
  -webkit-font-smoothing: antialiased;
}}
.container {{ max-width: 100%; margin: 0 auto; }}

/* Top bar */
.top {{
  position: fixed; top: 0; left: 0; right: 0; z-index: 100;
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 28px;
  background: rgba(244,242,237,0.95);
  border-bottom: 1px solid #ddd;
  font-family: var(--font);
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}}
.top .logo {{ font-weight: 800; font-size: 0.75rem; }}
.top .logo span {{ color: var(--red); }}
.top-nav {{ display: flex; gap: 2px; flex-wrap: wrap; justify-content: flex-end; }}
.nav-link {{
  color: #888; text-decoration: none; padding: 3px 10px;
  font-size: 0.55rem; letter-spacing: 0.05em;
  transition: color 0.15s;
}}
.nav-link:hover {{ color: var(--red); }}

/* Hero */
.hero {{
  position: relative;
  min-height: 90vh;
  display: flex; align-items: flex-end;
  background-size: cover; background-position: center;
  margin-bottom: 4px;
}}
.hero-overlay {{
  position: absolute; inset: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0.2) 50%, rgba(0,0,0,0.1) 100%);
}}
.hero-content {{
  position: relative; z-index: 2;
  max-width: 720px; padding: 60px 40px 80px; color: #fff;
}}
.hero-label {{
  font-size: 0.6rem; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.15em; color: var(--red); margin-bottom: 8px;
}}
.hero-title {{
  font-family: var(--display); font-size: 2.6rem; font-weight: 900;
  line-height: 1.1; margin-bottom: 16px; letter-spacing: -0.02em;
}}
.hero-body p {{ font-size: 0.9rem; line-height: 1.7; opacity: 0.9; max-width: 600px; }}

/* Feature story */
.feature {{
  display: flex; gap: 0; margin-bottom: 4px;
  background: var(--card); min-height: 400px;
}}
.feature-img {{ width: 50%; background-size: cover; background-position: center; }}
.feature-content {{
  width: 50%; padding: 36px 40px;
  display: flex; flex-direction: column; justify-content: center;
}}
.feature-label {{
  font-size: 0.55rem; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.12em; color: var(--red); margin-bottom: 6px;
}}
.feature-title {{
  font-family: var(--display); font-size: 1.5rem; font-weight: 700;
  line-height: 1.2; margin-bottom: 12px; letter-spacing: -0.01em;
}}
.feature-body p {{ font-size: 0.85rem; color: var(--text2); line-height: 1.7; }}

/* Compact stories */
.compact {{
  display: flex; gap: 16px; padding: 16px 28px;
  background: var(--card); margin-bottom: 2px; align-items: center;
}}
.compact-img {{
  width: 80px; height: 80px; flex-shrink: 0;
  background-size: cover; background-position: center; border-radius: 4px;
}}
.compact-content {{ flex: 1; }}
.compact-label {{
  font-size: 0.5rem; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.1em; color: var(--red); margin-bottom: 2px;
}}
.compact-title {{
  font-family: var(--display); font-size: 0.85rem; font-weight: 700;
  line-height: 1.2; margin-bottom: 4px;
}}
.compact-body p {{ font-size: 0.7rem; color: var(--text2); line-height: 1.5; }}

/* Footer */
.footer {{
  padding: 24px 28px; text-align: center;
  font-size: 0.6rem; color: var(--text3); line-height: 2;
  border-top: 1px solid #ddd;
}}

@media(max-width:700px) {{
  .feature {{ flex-direction: column; min-height: auto; }}
  .feature-img {{ width: 100%; height: 220px; }}
  .feature-content {{ width: 100%; padding: 20px 24px; }}
  .hero-title {{ font-size: 1.8rem; }}
  .hero-content {{ padding: 40px 20px 60px; }}
  .top {{ padding: 8px 14px; flex-direction: column; gap: 4px; }}
  .compact {{ padding: 12px 16px; }}
}}
</style>
</head>
<body>
<div class="container">

<div class="top">
  <div class="logo">Beyond the <span>Game</span></div>
  <div class="top-nav">{nav_items}</div>
</div>

{all_sections}

<footer class="footer">
  Seven dimensions · Head-to-Head History · Player Matchups · Venue & Conditions · Recent Form ·
  Tournament Context · Sentiment · Player Health<br>
  Published daily · PyTorch engine · 11 sports
</footer>

</div>
<script>
(function() {{
  document.querySelectorAll('.nav-link').forEach(function(link) {{
    link.addEventListener('click', function(e) {{
      e.preventDefault();
      var id = this.getAttribute('href').slice(1);
      var el = document.getElementById(id);
      if (el) el.scrollIntoView({{ behavior:'smooth', block:'start' }});
    }});
  }});
}})();
</script>
</body>
</html>"""

    out_dir = os.path.join(HERE, "output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return out_path
