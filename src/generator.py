"""
Bold, dramatic, image-rich magazine — hero section, vibrant, alive.
"""

import os, random
from datetime import datetime

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from src.world_sports import SPORTS

sport_keys = ["Cricket_T20", "EPL", "NBA", "NFL", "MLB", "NHL", "TENNIS", "Rugby", "F1", "MMA", "Boxing"]

SPORT_IMAGES = {
    "Cricket_T20": [
        "https://images.unsplash.com/photo-1531415074968-036ba1b575da?w=1200&h=700&fit=crop",
        "https://images.unsplash.com/photo-1587280501635-68a0e82cd5ff?w=1200&h=700&fit=crop",
        "https://images.unsplash.com/photo-1624526267942-ab0ff8a3e972?w=1200&h=700&fit=crop",
    ],
    "EPL": [
        "https://images.unsplash.com/photo-1575361204480-aadea25e6e68?w=1200&h=700&fit=crop",
        "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=1200&h=700&fit=crop",
        "https://images.unsplash.com/photo-1459865264687-595d652de67e?w=1200&h=700&fit=crop",
    ],
    "NBA": [
        "https://images.unsplash.com/photo-1546519638-68e109498ffc?w=1200&h=700&fit=crop",
        "https://images.unsplash.com/photo-1504450758481-7338eba7524a?w=1200&h=700&fit=crop",
        "https://images.unsplash.com/photo-1519861531473-9200262188bf?w=1200&h=700&fit=crop",
    ],
    "NFL": [
        "https://images.unsplash.com/photo-1566577739112-5180d4bf9391?w=1200&h=700&fit=crop",
        "https://images.unsplash.com/photo-1552332386-f8e00a1a2ed1?w=1200&h=700&fit=crop",
        "https://images.unsplash.com/photo-1507226983735-a838615193b0?w=1200&h=700&fit=crop",
    ],
    "MLB": [
        "https://images.unsplash.com/photo-1562077772-1fd6ddb2ed5a?w=1200&h=700&fit=crop",
        "https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=1200&h=700&fit=crop",
        "https://images.unsplash.com/photo-1518541395164-3f0b36f65f3c?w=1200&h=700&fit=crop",
    ],
    "NHL": [
        "https://images.unsplash.com/photo-1515703407324-5d7532e6918f?w=1200&h=700&fit=crop",
        "https://images.unsplash.com/photo-1511227499331-25c621db940e?w=1200&h=700&fit=crop",
    ],
    "TENNIS": [
        "https://images.unsplash.com/photo-1595435934249-5df7ed86e1c0?w=1200&h=700&fit=crop",
        "https://images.unsplash.com/photo-1531313849054-7c2732a2ab5b?w=1200&h=700&fit=crop",
        "https://images.unsplash.com/photo-1622279457486-28f470ae0d4a?w=1200&h=700&fit=crop",
    ],
    "Rugby": [
        "https://images.unsplash.com/photo-1511882150382-4210563a7220?w=1200&h=700&fit=crop",
        "https://images.unsplash.com/photo-1560272564-c83b66b1ad12?w=1200&h=700&fit=crop",
    ],
    "F1": [
        "https://images.unsplash.com/photo-1630673240362-ed9f2121eb1a?w=1200&h=700&fit=crop",
        "https://images.unsplash.com/photo-1582653291997-079a1c04e1a1?w=1200&h=700&fit=crop",
        "https://images.unsplash.com/photo-1535982330050-f1c2fb79ff78?w=1200&h=700&fit=crop",
    ],
    "MMA": [
        "https://images.unsplash.com/photo-1599058917212-d750089bc07e?w=1200&h=700&fit=crop",
        "https://images.unsplash.com/photo-1578301978693-85fa9c0320b9?w=1200&h=700&fit=crop",
    ],
    "Boxing": [
        "https://images.unsplash.com/photo-1549719386-74dfcbf7dbed?w=1200&h=700&fit=crop",
        "https://images.unsplash.com/photo-1461896836934-bd45ba8fcf9b?w=1200&h=700&fit=crop",
    ],
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

    tossup_bodies = [
        f"These two sides could play a hundred times and split the results down the middle. Every metric, every angle, every past encounter points to a single conclusion: nobody knows. The last meeting went down to the wire. The one before that was decided in stoppage time. This is the kind of fixture where you do not look away, not even for a second.",
        f"The numbers say {wp:.0f}% either way. That is not indecision — it is honesty. {t1} and {t2} match up so evenly that the outcome will be decided by something beyond data. A deflection. A decision. A moment of brilliance that no model could have predicted. Those moments define sport.",
        f"Here is what makes this matchup impossible to call: {t1} dominates in transition while {t2} controls the half-court game. Their strengths cancel out, their weaknesses never quite align, and the result is a statistical deadlock. Games like this rarely go to the favorite. They go to whoever wants it more in the final five minutes.",
        f"The model spent thousands of iterations on this fixture and produced a shrug. When the data refuses to pick a side, it means the game will be decided by intangibles — effort, adjustments, composure under pressure. {t1} has the talent. {t2} has the belief. Neither advantage is enough on its own.",
        f"Dead even across every dimension. Form is identical. Head-to-head history is a wash. Even the venue barely tilts the needle. This is the kind of game where the opening kickoff feels fraudulent — how can something so unpredictable start with something so routine?",
    ]
    lock_bodies = [
        f"{t1} at {wp:.0f}% is not a prediction — it is a formality. The gap between these sides has widened with every passing week. {t2} would need a perfect game to stay competitive. Perfection is rare in sport. Rarer still when the opponent is this dominant.",
        f"The model does not do hyperbole. When it says {wp:.0f}%, it means {t1} wins that many simulations out of a hundred. The other {100-wp:.0f} simulations involve {t2} playing flawlessly and {t1} having an anomalous off night. That is not a strategy. That is a hope.",
        f"Some games are contests. This one is a coronation. {t1} enters with advantages in form, fitness, and matchup history. {t2} enters with hope. Hope is a wonderful thing. It just does not show up in the box score.",
        f"Every dimension the model tracks points to {t1}. The offense is sharper. The defense is tighter. The transition game is faster. {t2} can try to slow the tempo, shorten the game, keep it close. That works for a while. It rarely works for four quarters.",
        f"There is a reason the projection is this lopsided: {t1} has been here before, against this opponent, and they have the mental edge of knowing exactly what works. {t2} has the motivation of being counted out. Motivation matters. Just not enough to close a {wp:.0f}% gap.",
    ]
    edge_bodies = [
        f"{t1} has a clear edge — {wp:.0f}% in the projection — but clear is not the same as certain. The model sees {t1} controlling the key phases of play, dictating tempo, forcing {t2} into uncomfortable positions. Yet {t2} has the weapons to flip the script if they find the right matchup.",
        f"The math likes {t1} at {wp:.0f}%. The math is not always right, but it is right more often than gut feeling. {t2} can win this game — they have the talent and the system — but they will need to execute at a level they have not consistently reached this season.",
        f"This is the kind of game where the edge is real but fragile. {t1} at {wp:.0f}% has the better numbers across the board. But sports are not played on spreadsheets. One good run, one hot streak, one moment where the math stops mattering — that is all {t2} needs.",
        f"The projection favors {t1} at {wp:.0f}%, and the reasons are specific: they win the turnover battle, they convert in transition, they defend the areas {t2} likes to attack. The blueprint for a {t1} victory is clear. The blueprint for a {t2} upset requires them to defy their own tendencies.",
        f"There is a gap here, measured at {wp:.0f}%. It is big enough to matter but small enough to disappear if {t1} gets careless. Carelessness happens more than you think. The model accounts for it. That is why this number is {wp:.0f}% and not higher.",
    ]
    lean_bodies = [
        f"Slight lean toward {t1 if wp > 50 else t2} at {wp:.0f}%. The margins are razor-thin — a deflection, a decision, a moment of individual genius could flip everything. This is the kind of game that reminds you why sport matters. Not because of certainty. Because of the beautiful, agonizing uncertainty of not knowing.",
        f"{t1 if wp > 50 else t2} goes in as the narrowest of favorites — the kind of favorite that feels more like a coin toss dressed up in statistics. The only separation comes in one or two dimensions where a slight imbalance exists. But 'slight' is doing a lot of work in that sentence.",
        f"The model sees a {wp:.0f}% edge for {t1 if wp > 50 else t2}. That is barely a whisper above a coin flip. Games like these are won in the details — who wins the fifty-fifty balls, who makes the extra pass, who blinks first in the closing minutes.",
        f"A {wp:.0f}% lean is the model's way of saying 'I guess?' {t1 if wp > 50 else t2} has the faintest advantage in one or two dimensions, but the margin is so small that home crowd noise could negate it. This is the kind of game where you watch with your hand over your mouth.",
        f"The edge is so small ({wp:.0f}%) that it barely qualifies as an edge. These games usually come down to which team makes fewer mistakes in the final stretch. {t1 if wp > 50 else t2} has the discipline edge. The other side has the desperation edge. Discipline usually wins. Usually.",
    ]

    if abs(wp - 50) < 3:
        lines.append(random.choice(tossup_bodies))
        if sorted_dims:
            lines.append(f"If there is a weakness to be found, it might live in the {sorted_dims[0]['name'].lower().replace('&', 'and')}, where one side has shown the faintest crack. But faint cracks have a way of disappearing when the lights are brightest.")
    elif wp > 72:
        lines.append(random.choice(lock_bodies))
        if sorted_dims:
            lines.append(f"The key battleground is the {sorted_dims[0]['name'].lower().replace('&', 'and')}, where {t1} holds a decisive edge. This is where games are won, where opposition attacks go to die, where {t2} will need to find something they simply did not have last time.")
    elif wp > 60:
        lines.append(random.choice(edge_bodies))
        if len(sorted_dims) >= 2:
            d1 = sorted_dims[0]['name'].lower().replace('&', 'and')
            d2 = sorted_dims[1]['name'].lower().replace('&', 'and')
            lines.append(f"The foundations of this advantage rest on two pillars: {d1} and {d2}. In both areas, {t1} has shown consistent superiority. Not overwhelming. Just enough.")
    else:
        lines.append(random.choice(lean_bodies))
        if sorted_dims:
            lines.append(f"The only real separation comes in the {sorted_dims[0]['name'].lower().replace('&', 'and')}, where a slight imbalance suggests one side might have the faintest edge. But 'might' is doing a lot of work in that sentence.")

    if pred.get("pred_score1") is not None:
        lines.append(f"If you need a number to hold onto: {t1} {pred['pred_score1']:.0f}, {t2} {pred['pred_score2']:.0f}. But numbers are just numbers. The game is the game.")

    return "\n\n".join(lines)


def generate_world_news(engine, takes, backtest_results, analytics=None):
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
    feed_items = ""
    seen_nav = set()

    for i, (conf, key, t) in enumerate(scored):
        pred = t.get("prediction", {})
        choices = SPORT_IMAGES.get(key, [])
        img = random.choice(choices) if choices else ""
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
            # Article feed items
            feed_items += f"""
  <article class="compact" id="{sect_id}">
    <div class="compact-img" style="background-image:url('{img}')"></div>
    <div class="compact-content">
      <p class="compact-label">{label}</p>
      <h3 class="compact-title">{title}</h3>
      <div class="compact-body"><p>{body[:200]}…</p></div>
    </div>
  </article>"""

    # ─── Book Analytics HTML ─────────────────────
    analytics_html = ""
    if analytics:
        sp_links = "".join(
            f'<span class="al-sport">{SPORTS[k]["name"]}</span>'
            for k in sport_keys if k in analytics and analytics[k].get("page_rank")
        )
        analytics_html = f"""
    <div class="analytics-lab">
      <div class="al-inner">
        <h2 class="al-head">Book Lab</h2>
        <p class="al-sub">AI, Optimization &amp; Data Sciences in Sports</p>
        <div class="al-grid">
          <div class="al-card">
            <h3>Pythagorean Weibull MoM</h3>
            <p>Independent Weibull distributions for runs scored/allowed, solved via Method of Moments. Win probability via 2D numerical integration. <em>Ch.13</em></p>
          </div>
          <div class="al-card">
            <h3>PageRank Rankings</h3>
            <p>Eigenvector centrality on win/loss networks. Quality-over-quantity: beating a strong opponent counts more than beating a weak one. <em>Ch.12</em></p>
          </div>
          <div class="al-card">
            <h3>K-Means Player Clusters</h3>
            <p>Unsupervised learning on player stats, games played, and form metrics. PEI efficiency ratio separates stars from rotation players. <em>Ch.11</em></p>
          </div>
          <div class="al-card">
            <h3>TRIMP Consistency</h3>
            <p>Game-to-game output variability measured via coefficient of variation. Higher consistency = more predictable team performance. <em>Ch.11</em></p>
          </div>
        </div>
        <p class="al-sports">Available for: {sp_links}</p>
      </div>
    </div>"""

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
  padding: 12px 28px;
  background: #1a1a16;
  border-bottom: 1px solid #2a2a26;
  font-family: var(--font);
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}}
.top .logo {{ font-weight: 800; font-size: 0.8rem; color: #fff; }}
.top .logo span {{ color: var(--red); }}
.top-nav {{ display: flex; gap: 4px; flex-wrap: wrap; justify-content: flex-end; }}
.nav-link {{
  color: #666; text-decoration: none; padding: 4px 10px;
  font-size: 0.55rem; letter-spacing: 0.05em;
  transition: color 0.15s, background 0.15s;
  border-radius: 2px;
}}
.nav-link:hover {{ color: #ddd; background: rgba(255,255,255,0.05); }}

.feature {{ cursor: pointer; transition: opacity 0.2s; }}
.feature:hover {{ opacity: 0.95; }}

/* Hero */
.hero {{
  position: relative;
  min-height: 90vh;
  display: flex; align-items: flex-end;
  background-size: cover; background-position: center;
  margin-bottom: 4px;
  background-color: #1a1a16;
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

/* Article feed (compact stories) */
.feed {{ max-width: 900px; margin: 0 auto; padding: 24px 28px; }}
.feed-head {{
  font-size: 0.6rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.12em; color: var(--text3); margin-bottom: 16px;
  padding-bottom: 8px; border-bottom: 2px solid var(--text);
}}
.compact {{
  display: flex; gap: 20px; padding: 20px 0;
  align-items: flex-start; cursor: pointer;
  border-bottom: 1px solid #e8e6e0;
  transition: opacity 0.15s;
}}
.compact:hover {{ opacity: 0.8; }}
.compact-img {{
  width: 160px; height: 110px; flex-shrink: 0;
  background-size: cover; background-position: center; border-radius: 2px;
  background-color: #eae6df;
}}
.compact-content {{ flex: 1; min-width: 0; }}
.compact-label {{
  font-size: 0.5rem; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.1em; color: var(--red); margin-bottom: 4px;
}}
.compact-title {{
  font-family: var(--display); font-size: 1rem; font-weight: 700;
  line-height: 1.25; margin-bottom: 6px;
}}
.compact-body p {{ font-size: 0.8rem; color: var(--text2); line-height: 1.6; }}

/* Book Analytics */
.analytics-lab {{
  background: #1a1a16; color: #c0c4cc; padding: 48px 28px;
}}
.al-inner {{ max-width: 900px; margin: 0 auto; }}
.al-head {{
  font-family: var(--display); font-size: 1.2rem; font-weight: 700;
  color: #fff; margin-bottom: 4px;
}}
.al-sub {{ font-size: 0.65rem; color: #6b7494; margin-bottom: 24px; }}
.al-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }}
.al-card {{
  background: #22221e; padding: 18px; border-radius: 2px;
}}
.al-card h3 {{ font-size: 0.7rem; font-weight: 700; color: #8aabff; margin-bottom: 6px; }}
.al-card p {{ font-size: 0.65rem; color: #8a8e9e; line-height: 1.6; }}
.al-card em {{ color: #6b7494; font-style: italic; }}
.al-sports {{ font-size: 0.6rem; color: #5c6278; margin-top: 16px; }}
.al-sport {{ display: inline-block; margin: 2px 4px; padding: 2px 8px; background: #22221e; border-radius: 2px; }}

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
  .compact {{ flex-direction: column; gap: 10px; }}
  .compact-img {{ width: 100%; height: 180px; }}
  .feed {{ padding: 16px; }}
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

{f'<div class="feed"><p class="feed-head">More Stories</p>{feed_items}</div>' if feed_items else ''}

{analytics_html if analytics else ''}

<footer class="footer">
  <strong>Beyond the Game</strong> &middot; Predictions by <strong>HAL 9000</strong><br>
  Seven dimensions &middot; Head-to-Head History &middot; Player Matchups &middot; Venue & Conditions &middot; Recent Form &middot; Tournament Context &middot; Sentiment &middot; Player Health<br>
  {len(scored)} stories across {len(seen_nav)} sports &middot; Published daily
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
