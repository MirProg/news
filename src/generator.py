"""
Dark, atmospheric story-driven layout — Lovecraft, Hitchcock, Kubrick.
Only 2-3 featured stories on page, rest in header nav.
No numbers overwhelming. Pure storytelling with aesthetic imagery.
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

# Atmospheric story templates — Lovecraft / Hitchcock / Kubrick / Pratchett voice
STORY_OPENINGS = [
    "There is a peculiar geometry to the game that most never see. The angles between players, the silent arithmetic of positioning, the patterns that repeat across seasons like a signal buried in static. Or, to put it more simply: one team is probably going to lose, and the data knows which one.",
    "The stadium is a study in contrasts: blinding light above, deep shadow below. In the tunnels beneath the stands, the air tastes of metal and grass. Two teams prepare to step into the arena, unaware that the outcome has already been calculated by seven dimensions of analysis — none of which account for the possibility that someone might trip over their own shoelace.",
    "Some matches are decided before a single play unfolds. Not by fate, nor by chance — but by forces measurable and predictable to those who know where to look. The patterns are there, embedded in the data like fossils in stone, waiting to be read by someone who has way too much time on their hands and access to a very large spreadsheet.",
    "Consider the space between two opponents at the moment of engagement. That interval, measured in fractions of a second and degrees of angle, contains more information about the outcome than any pundit's intuition. The machine sees it. The crowd feels it. The players, statistically speaking, are mostly just hoping nobody makes a really embarrassing mistake on live television.",
    "There is a threshold beyond which measurement becomes prediction. Beyond that threshold lie the seven dimensions — a framework that maps not just what happened, but what will happen. And what will happen tonight has been mapped with unsettling precision, assuming the universe doesn't decide to throw in a rogue gust of wind just to keep things interesting.",
    "The ordinary observer sees a game. The trained eye sees a chain of causality stretching back years — past meetings, venue histories, atmospheric conditions, the accumulated weight of every similar moment that came before. Tonight is not an isolated event. It never was. Though the post-match analysis will still find a way to blame the referee.",
    "Something is about to unfold on the field. The air has that quality — that anticipation that precedes the irreversible. Every factor has been weighed. Every variable accounted for. The only thing left is the event itself, and the quiet, unshakeable knowledge that sport has a sense of humor.",
]


def _story(pred):
    """Write an atmospheric, literary narrative — no percentages, no bullet points."""
    t1 = pred["team1"]; t2 = pred["team2"]; wp = pred["t1_win_pct"]
    dims = pred.get("dimensions", [])
    sorted_dims = sorted(dims, key=lambda d: -abs(d["value"] - 50))

    opening = random.choice(STORY_OPENINGS)

    if abs(wp - 50) < 3:
        body = opening
        body += f" This is the rare matchup where the dimensions refuse to align. {t1} and {t2} occupy opposite poles of every measurable axis, yet the composite reads as a perfect equilibrium — a balance so precise it feels deliberate, as though the universe itself conspired to create uncertainty. The model, for all its resolution, can only offer a single honest word: unknown. Which is its way of saying it has no idea, and you should probably just watch the game like a normal person."
    elif wp > 72:
        body = opening
        body += f" {t1} enters this contest carrying an advantage so comprehensive it borders on the absolute. Every dimension the machine tracks — from the granular history of individual player matchups to the macro patterns of venue behavior — converges on the same conclusion."
        if sorted_dims:
            d = sorted_dims[0]
            body += f" The strongest signal radiates from {d['name'].lower()}, where the asymmetry is most pronounced. The gap between these two sides, measured across all seven axes, creates a gravitational field from which {t2} will struggle to escape. The model does not say 'upset.' The model says 'mathematically unlikely.' The model has never been to a party and does not understand the appeal of dramatic narratives."
    elif wp > 60:
        body = opening
        body += f" {t1} holds a measurable advantage — not the kind that guarantees outcome, but the kind that tilts probability across enough individual moments to matter."
        if len(sorted_dims) >= 2:
            body += f" Two dimensions in particular — {sorted_dims[0]['name'].lower()} and {sorted_dims[1]['name'].lower()} — form the backbone of this edge, each contributing a subtle but persistent bias toward {t1}. In the aggregate, these biases compound into a force that {t2} must consciously overcome."
        body += f" It is not impossible. It is merely improbable. Which, as any historian of sport will tell you, is precisely when the improbable tends to show up, grinning, with questionable fashion sense."
    else:
        body = opening
        body += f" The signal here is faint — a whisper where one might expect a voice. {t1 if wp > 50 else t2} registers barely above parity, an edge so slender it approaches the threshold of noise."
        if sorted_dims:
            body += f" What little separation exists comes from {sorted_dims[0]['name'].lower()}, where a single dimension manages to produce just enough distinction to register."
        body += f" Matches like these belong not to prediction, but to the chaotic and beautiful unpredictability that makes sport what it is. The model admits, in its own silent, tensorial way, that it is guessing. It hopes you will not hold this against it."

    if pred.get("pred_score1") is not None:
        body += f" The projected score suggests {t1} {pred['pred_score1']:.0f}, {t2} {pred['pred_score2']:.0f}."
    else:
        body += f" The projection favors {t1 if wp > 50 else t2}, but by a margin that offers no guarantees."

    body += " What unfolds between the opening whistle and the final moment will be determined not by data, but by the thousand infinitesimal choices that data can only describe, never dictate. The model is smart. But it has never once kicked a ball, swung a bat, or been hit in the face by a professional boxer. That counts for something."

    return body


def _dim_bars(pred):
    dims = pred.get("dimensions", []) if pred else []
    if not dims:
        return ""
    bars = "".join(
        '<div class="dim"><span class="dim-l">{}</span><div class="dim-t"><div class="dim-f" style="width:{}%"></div></div></div>'.format(
            d["name"], d["value"])
        for d in dims
    )
    return f'<div class="dims">{bars}</div>'


def generate_world_news(engine, takes, backtest_results):
    by_sport = {}
    for t in takes:
        by_sport.setdefault(t["sport"], []).append(t)

    timestamp = datetime.utcnow().strftime("%d %B %Y")
    total_stories = len(takes)

    # Pick top 3 most confident predictions for featured stories
    featured = []
    for key in sport_keys:
        if key not in engine.predictors:
            continue
        for t in by_sport.get(key, []):
            pred = t.get("prediction", {})
            conf = abs(pred.get("t1_win_pct", 50) - 50) if pred else 0
            featured.append((conf, key, t))
    featured.sort(key=lambda x: -x[0])

    # Build navigation and full sections
    nav_items = ""
    hidden_sections = ""

    for i, (conf, key, t) in enumerate(featured):
        if i >= 3:
            break

        pred = t.get("prediction", {})
        img = SPORT_IMAGES.get(key, "")
        body = _story(pred) if pred else ""
        dims = _dim_bars(pred) if pred else ""
        spec = SPORTS[key]

        story_html = f"""
      <section class="featured" id="sport-{key}" style="--img:url('{img}')">
        <div class="featured-bg"></div>
        <div class="featured-content">
          <p class="featured-label">{spec['name']}</p>
          <h2 class="featured-title">{t['title']}</h2>
          <div class="featured-body"><p>{body}</p></div>
          {dims}
        </div>
      </section>"""

        # Put first featured story on page, rest in hidden sections
        if i == 0:
            featured_main = story_html
        else:
            hidden_sections += story_html
            nav_items += f'<a class="nav-link" href="#sport-{key}" data-key="{key}">{spec["name"]}</a>'

    # Remaining sports go in hidden sections too
    for key in sport_keys:
        if key not in engine.predictors:
            continue
        # Check if already featured
        already = any(f[1] == key for f in featured[:3])
        if already:
            continue

        sport_takes = by_sport.get(key, [])
        if not sport_takes:
            continue

        img = SPORT_IMAGES.get(key, "")
        spec = SPORTS[key]
        t = sport_takes[0]
        pred = t.get("prediction", {})
        body = _story(pred) if pred else ""
        dims = _dim_bars(pred) if pred else ""

        hidden_sections += f"""
      <section class="featured" id="sport-{key}" style="--img:url('{img}')">
        <div class="featured-bg"></div>
        <div class="featured-content">
          <p class="featured-label">{spec['name']}</p>
          <h2 class="featured-title">{t['title']}</h2>
          <div class="featured-body"><p>{body}</p></div>
          {dims}
        </div>
      </section>"""

        nav_items += f'<a class="nav-link" href="#sport-{key}" data-key="{key}">{spec["name"]}</a>'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Seven Dimensions — {timestamp}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500&family=Playfair+Display:ital,wght@0,600;0,700;1,500;1,600&family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}

:root {{
  --bg: #f7f5f0;
  --bg2: #efede8;
  --text: #1a1a18;
  --text2: #5a5852;
  --text3: #9a9892;
  --border: #e0ddd6;
  --red: #b83535;
  --red-dim: rgba(184,53,53,0.08);
  --font-body: 'Cormorant Garamond', Georgia, serif;
  --font-display: 'Playfair Display', Georgia, serif;
  --font-ui: 'Inter', -apple-system, sans-serif;
}}

body {{
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-body);
  font-size: 17px;
  line-height: 1.7;
  -webkit-font-smoothing: antialiased;
  overflow-x: hidden;
}}

.container {{ max-width: 100%; margin: 0 auto; }}

/* ═══ Top Navigation ═══ */
.top-bar {{
  position: fixed; top: 0; left: 0; right: 0; z-index: 100;
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 28px;
  background: linear-gradient(to bottom, rgba(247,245,240,0.98) 60%, transparent);
  font-family: var(--font-ui);
  font-size: 0.7rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}}
.top-bar .logo {{
  font-family: var(--font-display);
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: var(--text);
}}
.top-bar .logo em {{ font-style: italic; color: var(--red); }}
.top-bar .nav-wrap {{
  display: flex;
  gap: 2px;
  flex-wrap: wrap;
  justify-content: flex-end;
}}
.top-bar .sep {{
  color: var(--text3);
  margin: 0 6px;
  font-family: var(--font-ui);
  font-size: 0.5rem;
}}
.nav-link {{
  color: var(--text3);
  padding: 3px 8px;
  text-decoration: none;
  transition: color 0.2s;
  font-size: 0.55rem;
  letter-spacing: 0.06em;
}}
.nav-link:hover {{ color: var(--text); }}
.nav-link.active {{ color: var(--red); }}

/* ═══ Featured Story — Full Bleed ═══ */
.featured {{
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: flex-end;
  overflow: hidden;
  border-bottom: none;
}}
.featured-bg {{
  position: absolute;
  inset: 0;
  background-image: var(--img);
  background-size: cover;
  background-position: center;
  filter: brightness(0.65) saturate(0.9);
  transition: transform 0.8s ease, filter 0.8s ease;
}}
.featured:hover .featured-bg {{
  transform: scale(1.02);
  filter: brightness(0.7) saturate(1);
}}
.featured::after {{
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(247,245,240,0.95) 0%, rgba(247,245,240,0.15) 45%, rgba(247,245,240,0.3) 100%);
  pointer-events: none;
}}
.featured-content {{
  position: relative; z-index: 2;
  max-width: 720px;
  padding: 60px 40px 80px;
}}
.featured-label {{
  font-family: var(--font-ui);
  font-size: 0.6rem;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--red);
  margin-bottom: 8px;
}}
.featured-title {{
  font-family: var(--font-display);
  font-size: 2.2rem;
  font-weight: 700;
  line-height: 1.15;
  margin-bottom: 16px;
  letter-spacing: -0.01em;
}}
.featured-body p {{
  font-size: 0.9rem;
  line-height: 1.75;
  color: var(--text2);
  max-width: 620px;
}}
.featured-body p + p {{ margin-top: 12px; }}

/* Dims */
.dims {{
  margin-top: 20px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 4px 20px;
  max-width: 600px;
}}
.dim {{ display: flex; align-items: center; gap: 8px; padding: 2px 0; }}
.dim-l {{
  font-family: var(--font-ui);
  font-size: 0.5rem;
  letter-spacing: 0.05em;
  color: var(--text3);
  width: 70px;
  flex-shrink: 0;
}}
.dim-t {{
  flex: 1;
  height: 2px;
  background: var(--border);
  overflow: hidden;
}}
.dim-f {{
  height: 100%;
  background: var(--red);
  transition: width 1s ease;
}}

/* ═══ Footer ═══ */
.footer {{
  padding: 24px 40px 32px;
  text-align: center;
  font-family: var(--font-ui);
  font-size: 0.55rem;
  color: var(--text3);
  letter-spacing: 0.06em;
  line-height: 2;
  border-top: 1px solid var(--border);
}}

/* ═══ Responsive ═══ */
@media(max-width:700px) {{
  .top-bar {{ padding: 10px 16px; flex-direction: column; gap: 6px; }}
  .top-bar .nav-wrap {{ justify-content: center; }}
  .featured-content {{ padding: 40px 20px 60px; }}
  .featured-title {{ font-size: 1.5rem; }}
  .featured-body p {{ font-size: 0.85rem; }}
  .dims {{ grid-template-columns: 1fr 1fr; }}
}}
</style>
</head>
<body>

<div class="top-bar">
  <span class="logo">The Seven <em>Dimensions</em></span>
  <div class="nav-wrap">
    <span class="sep">&#8212;</span>
    {nav_items}
    <span class="sep">&#8212;</span>
    <span class="nav-link" style="color:var(--text3);cursor:default;">{timestamp}</span>
  </div>
</div>

<div class="container">

{featured_main}

{hidden_sections}

<footer class="footer">
  Seven dimensions &middot; Head-to-Head History &middot; Player Matchups &middot; Venue &amp; Conditions &middot; Recent Form<br>
  Tournament Context &middot; Sentiment &middot; Player Health<br>
  <span style="color:var(--text3)">Published daily &middot; PyTorch engine &middot; {total_stories} stories</span>
</footer>

</div>

<script>
(function() {{
  // Smooth scroll for nav links
  document.querySelectorAll('.nav-link[href^="#"]').forEach(function(a) {{
    a.addEventListener('click', function(e) {{
      e.preventDefault();
      var el = document.getElementById(this.getAttribute('href').slice(1));
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
