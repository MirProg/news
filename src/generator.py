"""
Clean editorial — only 3 stories on page, rest accessible via header nav.
"""

import os, random
from datetime import datetime

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from src.world_sports import SPORTS

sport_keys = ["Cricket_T20", "EPL", "NBA", "NFL", "MLB", "NHL", "TENNIS", "Rugby", "F1", "MMA", "Boxing"]

SPORT_IMAGES = {
    "Cricket_T20": "https://images.unsplash.com/photo-1531415074968-036ba1b575da?w=800&h=500&fit=crop",
    "EPL": "https://images.unsplash.com/photo-1575361204480-aadea25e6e68?w=800&h=500&fit=crop",
    "NBA": "https://images.unsplash.com/photo-1546519638-68e109498ffc?w=800&h=500&fit=crop",
    "NFL": "https://images.unsplash.com/photo-1566577739112-5180d4bf9391?w=800&h=500&fit=crop",
    "MLB": "https://images.unsplash.com/photo-1562077772-1fd6ddb2ed5a?w=800&h=500&fit=crop",
    "NHL": "https://images.unsplash.com/photo-1515703407324-5d7532e6918f?w=800&h=500&fit=crop",
    "TENNIS": "https://images.unsplash.com/photo-1595435934249-5df7ed86e1c0?w=800&h=500&fit=crop",
    "Rugby": "https://images.unsplash.com/photo-1511882150382-4210563a7220?w=800&h=500&fit=crop",
    "F1": "https://images.unsplash.com/photo-1630673240362-ed9f2121eb1a?w=800&h=500&fit=crop",
    "MMA": "https://images.unsplash.com/photo-1599058917212-d750089bc07e?w=800&h=500&fit=crop",
    "Boxing": "https://images.unsplash.com/photo-1549719386-74dfcbf7dbed?w=800&h=500&fit=crop",
}

OPENINGS = [
    "There is a peculiar geometry to the game that most never see. One of these teams is going to lose. The other one is going to win. The data has reached a conclusion, though it is not especially emotional about it.",
    "Beneath the stadium, in corridors where the concrete never quite dries, two teams prepare. They are unaware that the outcome has been calculated across seven dimensions of analysis. They are also unaware that pigeons sometimes land on the field at inopportune moments. This has happened before.",
    "Some matches are decided before they begin. Not by fate, and not by chance — but by patterns measurable to anyone willing to spend an unreasonable amount of time with spreadsheets. The data does not judge this lifestyle choice.",
    "There is a moment before every contest when the two sides face each other. In that interval, the machine has already formed its conclusion. The players will arrive at the same conclusion eventually, though they will do it by actually playing the game, which seems unnecessarily difficult.",
    "Beyond a certain threshold, measurement becomes prediction. The seven-dimensional framework tracks what is likely to happen next. It is reasonably confident about this. It has been wrong before, and it is aware of this fact.",
    "The ordinary observer sees a game. The trained eye sees causality stretching back years. The truly jaded observer expects something absurd to happen regardless, because sport is fundamentally unwilling to be predictable out of spite.",
    "The air before a match has a particular quality. Anticipation, perhaps, or the collective anxiety of everyone in the building realizing they are about to witness something that will be either brilliant or a complete disaster, with very little room in between.",
    "The data does not experience hope or fear. It processes information and arrives at probabilities. The fact that this is more reliable than human intuition is not a compliment to the data.",
    "Every match exists within a web of causality — past meetings, venue tendencies, atmospheric pressure, the phase of the moon. The model accounts for most of these. The moon phase is not currently included, though the possibility is being researched.",
]


def _story(pred):
    t1 = pred["team1"]; t2 = pred["team2"]; wp = pred["t1_win_pct"]
    dims = pred.get("dimensions", [])
    sorted_dims = sorted(dims, key=lambda d: -abs(d["value"] - 50))

    opening = random.choice(OPENINGS)

    if abs(wp - 50) < 3:
        body = opening
        body += f" {t1} and {t2} are so evenly matched that the model can only register uncertainty. It does not enjoy this. The most honest prediction it can offer is that someone will win, presumably by scoring more points than the other side, though the exact mechanism remains unclear."
    elif wp > 72:
        body = opening
        body += f" {t1} has an advantage the model considers significant — a convergence across multiple dimensions that does not happen often."
        if sorted_dims:
            body += f" The strongest signal comes from {sorted_dims[0]['name'].lower()}, where the gap is widest. The model does not use words like 'inevitable.' It uses 'probable,' and has calibrated its thresholds for the fact that improbable things happen regularly, usually right after someone declares them improbable."
    elif wp > 60:
        body = opening
        body += f" {t1} holds a measurable advantage — not absolute, but consistent."
        if len(sorted_dims) >= 2:
            body += f" The edge comes primarily from {sorted_dims[0]['name'].lower()} and {sorted_dims[1]['name'].lower()}. They are not guarantees. They are statistical tailwinds."
        body += f" {t2} can still win. If they do, the model will update its understanding of the world. It finds this prospect irritating."
    else:
        body = opening
        body += f" The signal here is faint. {t1 if wp > 50 else t2} registers barely above parity — an edge so slender it barely qualifies."
        if sorted_dims:
            body += f" What little separation exists comes from {sorted_dims[0]['name'].lower()}."
        body += f" Matches like these belong to the chaotic uncertainty that makes sport compelling. The model accepts this. It does not have to like it."

    if pred.get("pred_score1") is not None:
        body += f" The projection: {t1} {pred['pred_score1']:.0f}, {t2} {pred['pred_score2']:.0f}."
    else:
        body += f" The projection favors {t1 if wp > 50 else t2}, but comfortably within the margin of error that keeps sports interesting."

    body += " The model is reasonably intelligent. It has never kicked a ball or been hit in the face by a professional boxer. These limitations should be considered."

    return body


def _all_stories_for(key, takes):
    """Generate hidden story cards for all takes of a sport."""
    html = ""
    for t in takes:
        pred = t.get("prediction", {})
        body = _story(pred) if pred else t["body"].replace("\n", "<br>")
        acc = pred.get("backtest_accuracy", "")
        html += f"""
      <div class="story">
        <p class="story-title">{t['title']}</p>
        <p class="story-body">{body}</p>
      </div>"""
    return html


def generate_world_news(engine, takes, backtest_results):
    by_sport = {}
    for t in takes:
        by_sport.setdefault(t["sport"], []).append(t)

    timestamp = datetime.utcnow().strftime("%d %B %Y")

    # Rank by confidence for featured
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
    featured = ""
    sections = ""

    for i, (conf, key, t) in enumerate(scored):
        if key not in engine.predictors:
            continue

        pred = t.get("prediction", {})
        img = SPORT_IMAGES.get(key, "")
        body = _story(pred) if pred else ""
        spec = SPORTS[key]

        # Section for this sport (hidden unless navigated to)
        sport_takes = by_sport.get(key, [])
        more_stories = _all_stories_for(key, sport_takes) if len(sport_takes) > 1 else ""
        backtest_acc = backtest_results.get(key, {}).get("accuracy", "?")

        section_id = f"s{key}"

        if i < 3:
            # Featured section (visible on load)
            featured += f"""
    <section class="story-card" id="{section_id}">
      <div class="card-img" style="background-image:url('{img}')"></div>
      <div class="card-content">
        <p class="card-label">{spec['name']} · {backtest_acc}% accuracy</p>
        <h2 class="card-title">{t['title']}</h2>
        <div class="card-body"><p>{body}</p></div>
      </div>
    </section>"""
        else:
            # Hidden section for nav-only access
            sections += f"""
    <section class="story-card hidden" id="{section_id}">
      <div class="card-img" style="background-image:url('{img}')"></div>
      <div class="card-content">
        <p class="card-label">{spec['name']} · {backtest_acc}% accuracy</p>
        <h2 class="card-title">{t['title']}</h2>
        <div class="card-body"><p>{body}</p></div>
      </div>
    </section>"""

        nav_items += f'<a class="nav-link" href="#{section_id}" data-key="{section_id}">{spec["name"]}</a>'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Seven Dimensions — {timestamp}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,600;0,700;1,500&family=Cormorant+Garamond:ital@0,1&display=swap" rel="stylesheet">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
:root {{
  --bg: #f6f4ef;
  --card-bg: #ffffff;
  --text: #1c1b18;
  --text2: #5c5a54;
  --text3: #9c9a94;
  --border: #e4e2dc;
  --red: #b83535;
  --font: 'Inter', -apple-system, sans-serif;
  --display: 'Playfair Display', Georgia, serif;
  --body: 'Cormorant Garamond', Georgia, serif;
}}
body {{
  background: var(--bg); color: var(--text);
  font-family: var(--body); font-size: 17px; line-height: 1.7;
  -webkit-font-smoothing: antialiased;
}}
.container {{ max-width: 780px; margin: 0 auto; padding: 0 20px 40px; }}

/* Header */
.header {{
  padding: 20px 0; border-bottom: 1px solid var(--border);
  margin-bottom: 20px; text-align: center;
}}
.header .logo {{ font-family: var(--display); font-size: 1.3rem; font-weight: 700; }}
.header .logo em {{ font-style: italic; color: var(--red); }}
.header .ts {{ font-size: 0.6rem; color: var(--text3); font-family: var(--font); text-transform: uppercase; letter-spacing: 0.06em; margin-top: 4px; }}

/* Nav */
.nav {{
  display: flex; gap: 2px; flex-wrap: wrap; justify-content: center;
  margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid var(--border);
}}
.nav-link {{
  font-family: var(--font); font-size: 0.6rem; font-weight: 500;
  color: var(--text3); text-decoration: none; padding: 4px 12px;
  border-radius: 3px; letter-spacing: 0.03em; text-transform: uppercase;
  transition: all 0.15s;
}}
.nav-link:hover {{ background: var(--red); color: #fff; }}

/* Story card */
.story-card {{
  display: flex; gap: 24px; margin-bottom: 24px;
  background: var(--card-bg); border: 1px solid var(--border);
  border-radius: 4px; overflow: hidden;
  transition: box-shadow 0.2s;
}}
.story-card:hover {{ box-shadow: 0 2px 16px rgba(0,0,0,0.05); }}
.card-img {{
  width: 260px; min-height: 180px; flex-shrink: 0;
  background-size: cover; background-position: center;
}}
.card-content {{ padding: 18px 22px 18px 0; }}
.card-label {{
  font-family: var(--font); font-size: 0.5rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.1em; color: var(--red); margin-bottom: 4px;
}}
.card-title {{
  font-family: var(--display); font-size: 1.15rem; font-weight: 700;
  line-height: 1.25; margin-bottom: 8px; letter-spacing: -0.01em;
}}
.card-body p {{ font-size: 0.85rem; color: var(--text2); line-height: 1.65; }}

/* Hidden sections */
.hidden {{ display: none; }}

/* Footer */
.footer {{
  border-top: 1px solid var(--border); padding: 20px 0; margin-top: 8px;
  text-align: center; font-family: var(--font); font-size: 0.6rem; color: var(--text3);
}}

@media(max-width:640px) {{
  .story-card {{ flex-direction: column; }}
  .card-img {{ width: 100%; height: 180px; }}
  .card-content {{ padding: 14px 18px; }}
}}
</style>
</head>
<body>
<div class="container">

<div class="header">
  <div class="logo">The Seven <em>Dimensions</em></div>
  <div class="ts">{timestamp}</div>
</div>

<nav class="nav" id="nav">{nav_items}</nav>

{featured}

{sections}

<footer class="footer">
  Seven dimensions · Head-to-Head History · Player Matchups · Venue & Conditions · Recent Form ·
  Tournament Context · Sentiment · Player Health<br>
  <span style="color:var(--red)">Published daily</span>
</footer>

</div>

<script>
(function() {{
  var links = document.querySelectorAll('.nav-link');
  var sections = document.querySelectorAll('.story-card');

  function showSection(id) {{
    sections.forEach(function(s) {{
      if (s.id === id) {{
        s.classList.remove('hidden');
      }} else {{
        s.classList.add('hidden');
      }}
    }});
  }}

  links.forEach(function(link) {{
    link.addEventListener('click', function(e) {{
      e.preventDefault();
      var id = this.getAttribute('href').slice(1);
      showSection(id);
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
      // Update URL hash without jump
      history.pushState(null, '', '#' + id);
    }});
  }});

  // Restore from URL hash on load
  if (window.location.hash) {{
    var id = window.location.hash.slice(1);
    if (id) showSection(id);
  }}
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
