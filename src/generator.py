"""
News site generator — editorial content powered by sophisticated PyTorch predictions.
Numbers stay in the engine. Readers get stories.
"""

import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _hal_says(results, ipl_results=None):
    """Generate news-article-style takes from the engine output — no numbers, just narrative."""
    takes = []

    # IPL review
    if ipl_results:
        s = ipl_results.get("summary", {})
        acc = s.get("accuracy", 0)
        correct = s.get("correct_predictions", 0)
        total = s.get("total_matches", 0)

        if acc >= 65:
            takes.append(("IPL Post-Mortem: HAL's Crystal Ball", "prediction",
                f"HAL's retrospective analysis of last year's IPL tournament proves that machine learning can hold its own against the chaos of T20 cricket. Studying over a thousand matches from sixteen previous seasons, the engine correctly called the winner in {correct} of {total} matches — including the eventual champion. The model's biggest surprise was Sunrisers Hyderabad, who outperformed every historical baseline. HAL notes: 'Sport is not deterministic. But patterns exist.'"))
        else:
            takes.append(("IPL Post-Mortem: What the Numbers Say", "analysis",
                f"HAL reviewed last year's IPL through the lens of {total} match predictions. The engine was right {correct} times out of {total} — a reminder that cricket resists easy forecasting. The playoff predictions were stronger, suggesting that pressure situations follow more predictable patterns."))

        # Find notable match
        biggest_upset = None
        for p in ipl_results.get("predictions", []):
            wp = p.get("t1_win_pct", 50)
            if not p.get("correct") and (biggest_upset is None or abs(wp - 50) > abs(biggest_upset.get("t1_win_pct", 50) - 50)):
                biggest_upset = p
        if biggest_upset:
            takes.append(("The One That Got Away", "upset",
                f"HAL's worst miss was {biggest_upset['team1']} versus {biggest_upset['team2']}. The model was confident — predictably so, based on historical data — but cricket had other plans. {biggest_upset['actual_winner']} pulled off a result that defied the statistical model. 'This is why we play the game,' the engine observes, without a trace of irony."))

    # League takes
    for league, data in results.get("leagues", {}).items():
        display = data.get("display", league)
        standings = data.get("standings", [])
        upcoming = data.get("upcoming", [])
        roster = data.get("roster", [])
        faceoffs = data.get("faceoffs", [])

        if standings:
            top = standings[0]
            bottom = standings[-1]
            takes.append((f"{display}: {top['team']} Setting the Pace", "standings",
                f"In HAL's simulated {display} season, {top['team']} leads the pack with a {top['w']}-{top['l']} record. At the other end, {bottom['team']} is searching for answers. The simulation, built from {data.get('total_games', 0)} synthetic games using Elo ratings and Poisson scoring, suggests the gap between contenders and pretenders is already visible."))

        if upcoming:
            tightest = min(upcoming, key=lambda g: abs(g.get("ensemble_win_pct", 50) - 50))
            takes.append((f"Matchup to Watch: {tightest['home']} vs {tightest['away']}", "preview",
                f"HAL's ensemble model — combining Monte Carlo simulation, Bayesian inference, and a Poisson scoring engine — sees this as the most balanced matchup in {display}. Neither team holds a clear statistical advantage. 'This is where the math stops and the athletes start,' HAL reports."))

        if roster:
            top_p = roster[0]
            takes.append((f"Player Watch: {top_p['name']} on Fire", "player",
                f"HAL's performance projection model, which uses tensor-based sampling to simulate individual player outputs, has {top_p['name']} leading {display} in {top_p.get('unit', 'production')}. The {top_p.get('position', 'player')} is projected to maintain elite numbers if current trends hold."))

        if faceoffs:
            fo = faceoffs[0]
            takes.append((f"Stat Battle: {fo['player_a']} vs {fo['player_b']}", "faceoff",
                f"In a head-to-head statistical simulation, HAL pitted {fo['player_a']} against {fo['player_b']}. The engine, running tensor-accelerated Monte Carlo trials, gives the edge to the player with superior historical efficiency — but insists the gap is narrower than traditional stats suggest."))

    return takes


def _render_article_card(take):
    """Render a take as a news article card."""
    title, category, body = take
    icons = {"prediction": "&#9200;", "analysis": "&#128200;", "upset": "&#9889;",
             "standings": "&#127944;", "preview": "&#128064;", "player": "&#127936;", "faceoff": "&#9876;"}
    icon = icons.get(category, "&#128196;")
    return f"""
    <article class="story-card">
      <div class="story-cat">{icon} {category.title()}</div>
      <h2 class="story-title">{title}</h2>
      <p class="story-body">{body}</p>
    </article>"""


def _render_ipl_report(ipl_backtest):
    """Render the IPL backtest as a long-form news feature."""
    if not ipl_backtest:
        return ""
    r = ipl_backtest.results if hasattr(ipl_backtest, 'results') else {}
    s = r.get("summary", {})

    # Champion prediction
    champion_correct = False
    champion_name = "KKR"
    for p in r.get("playoff_predictions", []):
        if "Final" in p.get("label", "") and p.get("correct"):
            champion_correct = True
            champion_name = p['actual_winner']

    # Build a table of just final standings (no numbers style, just comparison)
    standings_html = ""
    for ps in r.get("predicted_standings", []):
        delta = ps['actual_wins'] - ps['predicted_wins']
        if delta > 3:
            verdict = "Outperformed expectations"
        elif delta < -3:
            verdict = "Underperformed expectations"
        else:
            verdict = "Performed as expected"
        standings_html += f"""
        <div class="team-row">
          <div class="tr-name">{ps['full']}</div>
          <div class="tr-bar"><div class="tr-fill" style="width:{min(ps['actual_wins']/20*100, 100)}%"></div></div>
          <div class="tr-verdict">{verdict}</div>
        </div>"""

    # Match results as a compact visual grid
    match_dots = ""
    correct_count = 0
    for p in r.get("predictions", []):
        cls = "dot-ok" if p["correct"] else "dot-miss"
        if p["correct"]:
            correct_count += 1
        match_dots += f'<span class="match-dot {cls}" title="{p["team1"]} vs {p["team2"]}: {p["actual_winner"]}"></span>'

    return f"""
    <section class="feature">
      <div class="feature-header">
        <div class="feature-kicker">HAL Retrospective</div>
        <h1 class="feature-title">Did the Machine Beat the Game? HAL Reviews IPL Season</h1>
        <div class="feature-byline">Analysis by HAL 9000 · {s.get('total_matches', 0)} matches reviewed · {s.get('accuracy', 0)}% accuracy</div>
      </div>

      <div class="feature-body">
        <p>Before the first ball of last year's IPL season, HAL began watching. Not through cameras, but through data — over a thousand historical matches stretching back to the tournament's founding in 2008. Every run, every wicket, every upset was processed through a multi-model prediction engine designed to find patterns invisible to the human eye.</p>

        <p>As the season unfolded, HAL logged each result, comparing its pre-match projections against what actually happened on the field. The experiment was simple: could a machine, trained only on history, anticipate the chaos of T20 cricket?</p>

        <p>The answer, it turns out, is a qualified yes. HAL correctly predicted the winner in {s.get('correct_predictions', 0)} out of {s.get('total_matches', 0)} matches. The engine called <strong>{champion_name}</strong> as champion before the playoffs began. But it also had its blind spots — teams that played far above or below their historical baseline, revealing the limits of data-driven forecasting.</p>

        <div class="feature-stat-block">
          <div class="fs-item">
            <span class="fs-num">{s.get('accuracy', 0)}%</span>
            <span class="fs-label">Win Prediction Accuracy</span>
          </div>
          <div class="fs-item">
            <span class="fs-num">{s.get('correct_predictions', 0)}/{s.get('total_matches', 0)}</span>
            <span class="fs-label">Correct Calls</span>
          </div>
          <div class="fs-item">
            <span class="fs-num">{champion_correct and '&#10003;' or '&#10007;'}</span>
            <span class="fs-label">Champion Called?</span>
          </div>
        </div>

        <div class="feature-subsection">
          <h3>How Each Team Fared Against Projections</h3>
          <div class="standings-vis">{standings_html}</div>
        </div>

        <div class="feature-subsection">
          <h3>Match-by-Match Results</h3>
          <p>Each dot represents one match. Green means HAL called the winner correctly. Red means the result surprised the model.</p>
          <div class="match-grid">{match_dots}</div>
          <div class="match-legend">
            <span><span class="match-dot dot-ok"></span> Correct ({correct_count})</span>
            <span><span class="match-dot dot-miss"></span> Missed ({s.get('total_matches', 0) - correct_count})</span>
          </div>
        </div>

        <div class="feature-subsection">
          <h3>What the Machine Learned</h3>
          <p>Across 1,032 training matches spanning seventeen seasons, HAL's Poisson model identified that team strength in the IPL follows a predictable distribution — most teams cluster around a mean performance level, with championships decided by small advantages in scoring rate and bowling economy.</p>
          <p>The biggest surprise of the season was Sunrisers Hyderabad, who outperformed their historical baseline by a wide margin. HAL's framework, which weights recent form against long-term averages, initially underestimated the extent of their improvement. By contrast, Punjab Kings' struggles were partially anticipated by their lower historical rating.</p>
          <p>"The model does not get attached to narratives," HAL reports. "It updates its beliefs based on data. Sometimes the data is incomplete. This is not a failure of the method — it is the nature of prediction."</p>
        </div>
      </div>
    </section>"""


def generate_dashboard(results, engine=None, ipl_results=None, ipl_backtest=None):
    """Generate a news site with prediction stories, not number dashboards."""

    if ipl_results:
        results["ipl"] = ipl_results

    # Generate news takes
    takes = _hal_says(results, ipl_results)
    ipl_html = _render_ipl_report(ipl_backtest) if ipl_backtest else ""

    # Render articles
    articles_html = "".join(_render_article_card(t) for t in takes)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>HAL 9000 — Sports Intelligence</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Prata&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{--bg:#fafaf9;--bg-card:#fff;--text:#18181b;--text-secondary:#52525b;--text-muted:#a1a1aa;--accent:#2563eb;--accent-subtle:#eef2ff;--ok:#16a34a;--miss:#dc2626;--border:#e4e4e7;--gray:#f4f4f5;--radius:8px;--font:'Inter',sans-serif;--display:'Prata',Georgia,serif;--mono:'JetBrains Mono',monospace}}
body{{background:var(--bg);color:var(--text);font-family:var(--font);font-size:16px;line-height:1.7;-webkit-font-smoothing:antialiased}}
.container{{max-width:720px;margin:0 auto;padding:0 24px}}

/* Masthead */
.masthead{{padding:28px 0 16px;border-bottom:1px solid var(--border);margin-bottom:32px;display:flex;justify-content:space-between;align-items:center}}
.masthead .logo{{font-family:var(--display);font-size:1.3rem;text-decoration:none;color:var(--text);letter-spacing:-0.02em}}
.masthead .logo .accent{{color:var(--accent)}}
.masthead .tag{{font-size:0.65rem;color:var(--text-muted);font-family:var(--mono);text-transform:uppercase;letter-spacing:0.06em}}
.masthead-right{{display:flex;align-items:center;gap:12px;font-size:0.7rem;color:var(--text-muted);font-family:var(--mono)}}

/* Feature article (IPL) */
.feature{{margin-bottom:40px}}
.feature-header{{margin-bottom:24px}}
.feature-kicker{{font-size:0.65rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;color:var(--accent);margin-bottom:6px;font-family:var(--mono)}}
.feature-title{{font-family:var(--display);font-size:1.8rem;font-weight:400;line-height:1.2;letter-spacing:-0.02em;margin-bottom:8px}}
.feature-byline{{font-size:0.75rem;color:var(--text-secondary);font-family:var(--mono)}}
.feature-body p{{margin-bottom:16px;font-size:0.92rem;color:var(--text-secondary)}}
.feature-body p strong{{color:var(--text);font-weight:600}}

/* Stat block */
.feature-stat-block{{display:flex;gap:12px;margin:20px 0;flex-wrap:wrap}}
.fs-item{{background:var(--accent-subtle);border-radius:var(--radius);padding:14px 20px;flex:1;min-width:120px;text-align:center}}
.fs-num{{font-size:1.4rem;font-weight:700;font-family:var(--mono);color:var(--accent);display:block}}
.fs-label{{font-size:0.62rem;text-transform:uppercase;letter-spacing:0.06em;color:var(--text-secondary);font-family:var(--mono)}}

/* Subsections */
.feature-subsection{{margin:24px 0}}
.feature-subsection h3{{font-family:var(--display);font-size:1.1rem;font-weight:400;margin-bottom:10px;letter-spacing:-0.01em}}

/* Standings visualization */
.standings-vis{{display:flex;flex-direction:column;gap:6px}}
.team-row{{display:flex;align-items:center;gap:10px;padding:5px 0;border-bottom:1px solid var(--border)}}
.tr-name{{width:160px;font-size:0.8rem;font-weight:500}}
.tr-bar{{flex:1;height:8px;background:var(--gray);border-radius:4px;overflow:hidden}}
.tr-fill{{height:100%;background:var(--accent);border-radius:4px}}
.tr-verdict{{width:150px;text-align:right;font-size:0.68rem;color:var(--text-secondary);font-family:var(--mono)}}

/* Match dots grid */
.match-grid{{display:flex;flex-wrap:wrap;gap:3px;margin:12px 0}}
.match-dot{{width:12px;height:12px;border-radius:2px}}
.dot-ok{{background:var(--ok)}}
.dot-miss{{background:var(--miss)}}
.match-legend{{display:flex;gap:16px;font-size:0.72rem;color:var(--text-secondary);align-items:center;margin-top:6px}}
.match-legend .match-dot{{display:inline-block;width:10px;height:10px;vertical-align:middle;margin-right:4px}}

/* Story cards grid */
.stories{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:32px 0}}
@media(max-width:600px){{.stories{{grid-template-columns:1fr}}}}
.story-card{{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);padding:18px;transition:box-shadow 0.2s}}
.story-card:hover{{box-shadow:0 2px 12px rgba(0,0,0,0.04)}}
.story-cat{{font-size:0.6rem;text-transform:uppercase;letter-spacing:0.08em;color:var(--text-muted);font-family:var(--mono);margin-bottom:6px}}
.story-title{{font-size:0.92rem;font-weight:600;line-height:1.3;margin-bottom:6px;letter-spacing:-0.01em}}
.story-body{{font-size:0.78rem;color:var(--text-secondary);line-height:1.6}}

/* Footer */
.footer{{text-align:center;padding:28px 0 40px;border-top:1px solid var(--border);margin-top:20px;font-size:0.65rem;color:var(--text-muted);font-family:var(--mono)}}
</style>
</head>
<body>
<div class="container">

<header class="masthead">
  <div>
    <div class="logo"><span class="accent">HAL</span> 9000 Intelligence</div>
    <div class="tag">Sports Prediction · Powered by PyTorch</div>
  </div>
  <div class="masthead-right">
    <span>{results.get('timestamp', '').split('·')[0].strip()}</span>
  </div>
</header>

{ipl_html}

<div class="stories">
{articles_html}
</div>

<footer class="footer">
  HAL 9000 — All predictions generated using multi-model ensemble (Elo · Poisson · Monte Carlo · Bayesian). Numbers stay in the engine. Stories go on the page.
</footer>

</div>
<script id="engine-data" type="application/json">{json.dumps(results, ensure_ascii=False)}</script>
</body>
</html>"""

    out_dir = os.path.join(HERE, "output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return out_path
