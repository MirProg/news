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


OPENINGS = [
    "Some nights, the stadium breathes differently. The air holds something — anticipation, dread, the quiet hum of inevitability. Tonight is one of those nights.",
    "They have played this fixture a dozen times. Every meeting tells a slightly different story, but the chapters are beginning to form a coherent narrative.",
    "The tunnel is where games are won before they start. In the dim light, two sets of eyes meet. One side knows something the other doesn't.",
    "Sport is memory in motion. Every pass, every tackle, every goal writes itself into the collective recall of those who witness it. Tonight adds another paragraph.",
    "There is a stillness before the storm. The warm-up ends. The crowd finds its voice. On the field, twenty-two figures wait for permission to become heroes or villains.",
    "The history between these two is written in scar tissue. Close losses. Narrow victories. The kind of rivalry that does not need a trophy to matter.",
    "Forget the standings. Forget the form guide. Some matches exist outside the context of a season — they are self-contained stories with their own gravity.",
    "The best games are not played on paper. They are played in the space between expectation and reality, where the unexpected lives and thrives.",
    "A season is a long novel. But some matches are chapters so dense, so rich with consequence, that they demand to be read on their own.",
    "The floodlights cast long shadows. In those shadows, players become something more than themselves — they become the embodiment of every hope and fear in the building.",
    "There are matches you watch. And there are matches you remember where you were. This one has the feel of the latter.",
    "The opening whistle is still minutes away. But the game has already begun — in the tunnels, in the mind, in the quiet calculation that separates confidence from doubt.",
    "Every rivalry has a heartbeat. Some are steady. Others, like this one, are arrhythmic — unpredictable, dangerous, impossible to chart.",
    "The great moments in sport are not planned. They emerge from the chaos, born of instinct and circumstance and the refusal to accept the script.",
    "Ask any player about the big moments and they will tell you: time slows down. The noise fades. What remains is pure, unfiltered reaction. Tonight demands that kind of focus.",
    "They say form is temporary, class is permanent. Tonight, these two sides test that theory under the brightest lights.",
    "There is a poetry to the way a team moves when everything clicks. Each player anticipates the other, the ball becomes an extension of will. It is rare. It is beautiful. And it might just happen tonight.",
    "The dressing room before a big game is a place of strange silences and louder-than-usual jokes. Every player copes differently. But they all feel the same weight.",
    "Victory has a thousand fathers, but defeat is an orphan. Tonight's loser will walk off alone, replaying the one moment that slipped away.",
    "In the stands, they wear scarves and wave flags and scream until their voices crack. They believe. And sometimes — just sometimes — belief is enough to bend the arc of a game.",
    "The best teams do not rely on luck. They create their own fortune through movement, through pressure, through the relentless application of will.",
    "There are patterns in the way great sides play — rhythms that repeat, sequences that feel choreographed. When those patterns click, the game becomes art.",
    "Every fixture carries echoes of those that came before. The same pitch, the same goals, the same ghosts of past triumphs and disasters. Tonight adds to the archive.",
    "The beauty of sport is its refusal to follow a script. The underdog wins. The favorite crumbles. The ball takes a deflection that changes everything. Tonight could be that night.",
    "Pressure is a privilege. To be in a moment that matters means you have earned the right to be there. Both these sides have earned it.",
    "There is a reason they play the game instead of letting a computer decide. Some things cannot be calculated. The rest is heart, nerve, and the will to do something extraordinary.",
    "The best rivalries are built on respect and resentment in equal measure. These two have plenty of both.",
    "Some players rise to the occasion. Others let the occasion swallow them. Tonight separates the ones who belong from the ones who are still learning.",
    "The crowd is the twelfth player. When they roar, the home side finds an extra step. When they fall silent, the away team knows they have done something right.",
    "A single moment can define a career. A goal, a save, a tackle, a miss — these are the fragments that memory holds onto. Tonight offers those moments to everyone on the pitch.",
    "The pitch is the same size for everyone. The rules are the same. What separates the winners from the losers is what happens in the spaces between the rules.",
    "Some teams build. Others attack. The great ones know when to do both. Tonight tests which philosophy prevails.",
    "There is a difference between wanting to win and expecting to win. One of these sides has crossed that threshold. The other is still searching for the door.",
    "The beauty of sport is that the ball does not remember last week's result. Every game is a fresh start, a clean slate, a new chance to write something worth remembering.",
    "In the end, it comes down to moments. A header. A save. A decision that takes a tenth of a second and lives forever. Tonight is full of those moments, waiting to happen.",
]


def _story(pred):
    t1 = pred["team1"]; t2 = pred["team2"]; wp = pred["t1_win_pct"]
    dims = pred.get("dimensions", [])
    sorted_dims = sorted(dims, key=lambda d: -abs(d["value"] - 50))

    opening = random.choice(OPENINGS)
    lines = [opening]

    if abs(wp - 50) < 3:
        lines.append(f"These two sides could play a hundred times and split the results down the middle. Every metric, every angle, every past encounter points to a single conclusion: nobody knows. The last meeting went down to the wire. The one before that was decided in stoppage time. This is the kind of fixture where you do not look away, not even for a second.")
        if sorted_dims:
            lines.append(f"If there is a weakness to be found, it might live in the {sorted_dims[0]['name'].lower().replace('&', 'and')}, where one side has shown the faintest crack. But faint cracks have a way of disappearing when the lights are brightest.")

    elif wp > 72:
        lines.append(f"{t1} walks onto the pitch with the kind of swagger that comes from knowing they have answers for everything {t2} can throw at them. The last outing was a statement — controlled, composed, relentless. They dismantled {t2}'s game plan piece by piece, and the memory of that night still lingers.")
        if sorted_dims:
            lines.append(f"The key battleground is the {sorted_dims[0]['name'].lower().replace('&', 'and')}, where {t1} holds a decisive edge. This is where games are won, where opposition attacks go to die, where {t2} will need to find something they simply did not have last time.")
        lines.append(f"Can {t2} turn it around? Of course. That is why we watch. But the mountain is steep, and the climbing gear is at home.")

    elif wp > 60:
        lines.append(f"{t1} has the edge, and it is not hard to see why. They move with purpose, defend with structure, attack with intent. Against {t2}, they have found ways to impose their style — not always decisively, but often enough to matter.")
        if len(sorted_dims) >= 2:
            d1 = sorted_dims[0]['name'].lower().replace('&', 'and')
            d2 = sorted_dims[1]['name'].lower().replace('&', 'and')
            lines.append(f"The foundations of this advantage rest on two pillars: {d1} and {d2}. In both areas, {t1} has shown consistent superiority. Not overwhelming. Just enough.")
        lines.append(f"{t2} has the tools to disrupt this. They have players capable of individual brilliance, of turning a game on its head in a single moment. But they will need to be at their absolute best — and even then, it might not be enough.")

    else:
        lines.append(f"{t1 if wp > 50 else t2} goes in as the narrowest of favorites — the kind of favorite that feels more like a coin toss dressed up in statistics. The margins are razor-thin. A deflection here, a decision there, a moment of individual genius or collective error — any of it could decide the outcome.")
        if sorted_dims:
            lines.append(f"The only real separation comes in the {sorted_dims[0]['name'].lower().replace('&', 'and')}, where a slight imbalance suggests one side might have the faintest edge. But 'might' is doing a lot of work in that sentence.")
        lines.append(f"This is the kind of game that reminds you why sport matters. It is not about certainty. It is about the beautiful, agonizing uncertainty of not knowing what happens next.")

    if pred.get("pred_score1") is not None:
        lines.append(f"If you need a number to hold onto: {t1} {pred['pred_score1']:.0f}, {t2} {pred['pred_score2']:.0f}. But numbers are just numbers. The game is the game.")

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
    seen_nav = set()

    for i, (conf, key, t) in enumerate(scored):
        pred = t.get("prediction", {})
        img = SPORT_IMAGES.get(key, "")
        body = _story(pred) if pred else ""
        spec = SPORTS[key]
        sect_id = f"s{key}"

        # Clean title — remove HAL/model/data references
        raw_title = t['title']
        title = raw_title.replace(": HAL Makes a Call", "").replace("HAL Makes a Call", "").replace("HAL's Multi-Dimensional Model Is Performing in ", "").replace("How ", "").replace(" Through HAL's Eyes", "").replace("Beyond the Score: Why ", "The Hidden Factor: ").replace(" Matters", "").replace("Player Watch: ", "Spotlight on ").replace(" in the Spotlight", "").replace("  ", " ").strip()
        if title == raw_title:
            title = raw_title.replace("HAL Makes a Call", "The Big One").replace("HAL's Multi-Dimensional Model Is Performing in ", "").replace("Through HAL's Eyes", "Unfolds")
        title = title.replace("HAL", "The Game").strip()
        # Fallback if title becomes empty or weird
        if not title or len(title) < 5:
            title = f"{t1 if pred else ''} vs {t2 if pred else ''}"[:60]

        label = f"{spec['name']} · {backtest_results.get(key, {}).get('accuracy', '?')}% accuracy"

        # Unique nav links only
        if key not in seen_nav:
            seen_nav.add(key)
            nav_items += f'<a class="nav-link" href="#{sect_id}" data-key="{sect_id}">{spec["name"]}</a>'

        if i == 0:
            # Hero section — full bleed with overlay
            all_sections += f"""
  <section class="hero" id="{sect_id}" style="background-image:url('{img}')">
    <div class="hero-overlay"></div>
    <div class="hero-content">
      <p class="hero-label">{label}</p>
      <h1 class="hero-title">{title}</h1>
      <div class="hero-body"><p>{body}</p></div>
    </div>
  </section>"""
        elif i < 5:
            # Secondary stories — image on left, text on right
            all_sections += f"""
  <section class="feature" id="{sect_id}">
    <div class="feature-img" style="background-image:url('{img}')"></div>
    <div class="feature-content">
      <p class="feature-label">{label}</p>
      <h2 class="feature-title">{title}</h2>
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
      <h3 class="compact-title">{title}</h3>
      <div class="compact-body"><p>{body[:150]}…</p></div>
    </div>
  </section>"""

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
