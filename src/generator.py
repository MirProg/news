"""
Dashboard generator — outputs engine results as self-contained HTML + JSON data.
"""

import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _render_standings(standings, league_display):
    rows = []
    for s in standings:
        streak = s.get("streak", "")
        w = s["w"]
        l = s["l"]
        pct = s.get("pct", 0)
        pts = s.get("pts", w)
        rows.append(f"""
        <tr>
          <td class="rank">{s['rank']}</td>
          <td class="team-cell">{s['team']}</td>
          <td>{w}-{l}</td>
          <td>{pct:.3f}</td>
          <td>{pts}</td>
          <td>{s.get('pf', 0)}</td>
          <td>{s.get('pa', 0)}</td>
          <td class="gd">{s.get('gd', 0):+d}</td>
        </tr>""")
    return f"""
    <div class="league-section">
      <h3 class="league-title">{league_display}</h3>
      <table class="standings-table">
        <thead><tr><th>#</th><th>Team</th><th>W-L</th><th>Pct</th><th>Pts</th><th>PF</th><th>PA</th><th>GD</th></tr></thead>
        <tbody>{"".join(rows)}</tbody>
      </table>
    </div>"""


def _render_games(games):
    cards = []
    for g in games:
        conf_color = "#00aa6a" if g.get("confidence", 0) > 90 else "#f5a623" if g.get("confidence", 0) > 70 else "#e05050"
        home_bar = g.get("ensemble_win_pct", 50)
        away_bar = 100 - home_bar
        cards.append(f"""
        <div class="game-card">
          <div class="game-meta">{g.get('league', '')} · {g.get('projected', {}).get('n_sims', 100000):,} sims</div>
          <div class="game-teams">
            <div class="team home">{g['home']}</div>
            <div class="vs">vs</div>
            <div class="team away">{g['away']}</div>
          </div>
          <div class="win-bar">
            <div class="bar-home" style="width:{home_bar}%">{home_bar}%</div>
            <div class="bar-away" style="width:{away_bar}%">{away_bar}%</div>
          </div>
          <div class="game-proj">
            Proj: {g.get('projected', {}).get('avg_home_score', '?')} - {g.get('projected', {}).get('avg_away_score', '?')}
          </div>
          <div class="game-conf" style="color:{conf_color}">Confidence: {g.get('confidence', 0)}%</div>
          <div class="model-breakdown">
            {''.join(f'<span class="model-tag">{k}: {v}%</span>' for k, v in g.get('models', {}).items())}
          </div>
        </div>""")
    return "".join(cards)


def _render_faceoffs(faceoffs):
    cards = []
    for f in faceoffs:
        cards.append(f"""
        <div class="faceoff-card">
          <div class="fo-league">{f.get('league', '')}</div>
          <div class="fo-players">
            <div class="fo-p">
              <span class="fo-name">{f['player_a']}</span>
              <span class="fo-stat">{f.get('stat_a', f.get('avg_a', '?'))} {f.get('stat_label', '')}</span>
              <span class="fo-pct">{f['a_win_pct']}%</span>
            </div>
            <div class="fo-vs">VS</div>
            <div class="fo-p">
              <span class="fo-name">{f['player_b']}</span>
              <span class="fo-stat">{f.get('stat_b', f.get('avg_b', '?'))} {f.get('stat_label', '')}</span>
              <span class="fo-pct">{f['b_win_pct']}%</span>
            </div>
          </div>
        </div>""")
    return "".join(cards)


def _render_players(players):
    rows = []
    for p in players:
        rows.append(f"""
        <tr>
          <td>{p.get('rank', '')}</td>
          <td class="team-cell">{p['name']}</td>
          <td>{p.get('position', '')}</td>
          <td class="stat-val">{p['stat']} {p.get('unit', '')}</td>
          <td>{p.get('games_played', '')} GP</td>
        </tr>""")
    return f"""
    <table class="player-table">
      <thead><tr><th>#</th><th>Player</th><th>Pos</th><th>Stat</th><th>GP</th></tr></thead>
      <tbody>{"".join(rows)}</tbody>
    </table>"""


def generate_dashboard(results, engine=None):
    """Generate self-contained HTML dashboard with embedded JSON data."""

    cal = results.get("calibration", {})
    health = results.get("ensemble_health", {})
    cal_rows = ""
    for c in cal.get("calibration", []):
        bar_w = min(c["actual"] / max(c["predicted"], 0.01) * 100, 200)
        cal_rows += f"""
        <tr>
          <td>{c['bin']}</td>
          <td>{c['predicted']}%</td>
          <td>{c['actual']}%</td>
          <td><div class="cal-bar" style="width:{bar_w}px;background:var(--accent);height:6px;border-radius:3px"></div></td>
          <td>{c['count']}</td>
        </tr>"""

    # Build league sections
    standings_html = ""
    games_html = ""
    faceoffs_html = ""
    players_html = ""

    for league_key, data in results.get("leagues", {}).items():
        standings_html += _render_standings(data.get("standings", []), data.get("display", league_key))
        games_html += _render_games(data.get("upcoming", []))
        faceoffs_html += _render_faceoffs(data.get("faceoffs", []))
        players_html += f"""
        <div class="player-section">
          <h4 class="league-title-sm">{data.get("display", league_key)}</h4>
          {_render_players(data.get("roster", []))}
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Infinite Engine — Sports Prediction Framework</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{--bg:#080810;--bg-card:#0d0d1a;--bg-card-hover:#111122;--text:#e0e0ee;--text-secondary:#8888aa;--text-muted:#555577;--accent:#4a6aff;--accent-glow:rgba(74,106,255,0.15);--green:#00cc88;--red:#ff4466;--amber:#ffaa33;--border:#1a1a2e;--radius:8px;--font:'Inter',sans-serif;--mono:'JetBrains Mono',monospace}}
body{{background:var(--bg);color:var(--text);font-family:var(--font);font-size:14px;line-height:1.6;-webkit-font-smoothing:antialiased;min-height:100vh}}
.container{{max-width:1280px;margin:0 auto;padding:0 24px}}

/* Header */
.header{{padding:24px 0 16px;border-bottom:1px solid var(--border);margin-bottom:24px}}
.header h1{{font-size:1.6rem;font-weight:800;letter-spacing:-0.03em}}
.header h1 .accent{{color:var(--accent)}}
.header .sub{{font-size:0.75rem;color:var(--text-secondary);font-family:var(--mono);margin-top:4px}}
.header .stats-row{{display:flex;gap:24px;margin-top:12px;flex-wrap:wrap}}
.header .stat-chip{{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);padding:6px 14px;font-size:0.7rem;font-family:var(--mono);color:var(--text-secondary)}}
.header .stat-chip strong{{color:var(--text);font-weight:600}}

/* Grid */
.dashboard-grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:24px}}
@media(max-width:900px){{.dashboard-grid{{grid-template-columns:1fr}}}}
.full-width{{grid-column:1/-1}}

/* Card */
.card{{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);padding:20px;position:relative}}
.card h2{{font-size:0.8rem;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;color:var(--text-muted);margin-bottom:14px;font-family:var(--mono)}}

/* Standings table */
.standings-table{{width:100%;border-collapse:collapse;font-size:0.75rem}}
.standings-table th{{text-align:left;padding:6px 8px;color:var(--text-muted);font-weight:500;font-size:0.65rem;font-family:var(--mono);border-bottom:1px solid var(--border);text-transform:uppercase;letter-spacing:0.05em}}
.standings-table td{{padding:5px 8px;border-bottom:1px solid var(--border-light);color:var(--text-secondary)}}
.standings-table .team-cell{{color:var(--text);font-weight:500}}
.standings-table .rank{{color:var(--text-muted);font-family:var(--mono);font-size:0.65rem}}
.standings-table .gd{{font-family:var(--mono)}}
.standings-table tr:hover td{{background:var(--bg-card-hover)}}
.league-title{{font-size:0.7rem;font-weight:600;color:var(--accent);margin-bottom:8px;font-family:var(--mono)}}
.league-section{{margin-bottom:20px}}
.league-section:last-child{{margin-bottom:0}}

/* Game cards */
.game-card{{background:var(--bg);border:1px solid var(--border);border-radius:var(--radius);padding:14px;margin-bottom:10px}}
.game-card:last-child{{margin-bottom:0}}
.game-meta{{font-size:0.6rem;color:var(--text-muted);font-family:var(--mono);margin-bottom:6px}}
.game-teams{{display:flex;align-items:center;gap:10px;margin-bottom:8px}}
.game-teams .team{{font-weight:600;font-size:0.82rem;flex:1}}
.game-teams .team.away{{text-align:right}}
.game-teams .vs{{color:var(--text-muted);font-size:0.65rem;font-family:var(--mono)}}
.win-bar{{display:flex;height:16px;border-radius:4px;overflow:hidden;margin-bottom:6px;font-size:0.55rem;font-weight:600}}
.bar-home{{background:var(--accent);display:flex;align-items:center;justify-content:center;color:#fff;transition:width 0.5s}}
.bar-away{{background:var(--red);display:flex;align-items:center;justify-content:center;color:#fff;transition:width 0.5s}}
.game-proj{{font-size:0.7rem;color:var(--text-secondary);margin-bottom:3px}}
.game-conf{{font-size:0.65rem;font-weight:500;margin-bottom:4px;font-family:var(--mono)}}
.model-breakdown{{display:flex;gap:4px;flex-wrap:wrap}}
.model-tag{{background:var(--bg-card);border:1px solid var(--border);padding:1px 6px;border-radius:3px;font-size:0.55rem;color:var(--text-muted);font-family:var(--mono)}}

/* Faceoffs */
.faceoff-card{{background:var(--bg);border:1px solid var(--border);border-radius:var(--radius);padding:12px;margin-bottom:8px;display:flex;flex-direction:column}}
.fo-league{{font-size:0.55rem;color:var(--text-muted);font-family:var(--mono);margin-bottom:4px}}
.fo-players{{display:flex;align-items:center;gap:8px}}
.fo-p{{flex:1;display:flex;flex-direction:column}}
.fo-p:last-child{{text-align:right;align-items:flex-end}}
.fo-name{{font-weight:600;font-size:0.78rem}}
.fo-stat{{font-size:0.7rem;color:var(--accent);font-family:var(--mono)}}
.fo-pct{{font-size:0.85rem;font-weight:700;margin-top:2px}}
.fo-vs{{color:var(--text-muted);font-family:var(--mono);font-weight:600;font-size:0.65rem}}

/* Player table */
.player-table{{width:100%;border-collapse:collapse;font-size:0.75rem}}
.player-table th{{text-align:left;padding:6px 8px;color:var(--text-muted);font-weight:500;font-size:0.65rem;font-family:var(--mono);border-bottom:1px solid var(--border);text-transform:uppercase}}
.player-table td{{padding:5px 8px;border-bottom:1px solid var(--border-light);color:var(--text-secondary)}}
.player-table .stat-val{{color:var(--accent);font-weight:600;font-family:var(--mono)}}
.player-section{{margin-bottom:16px}}
.league-title-sm{{font-size:0.65rem;font-weight:600;color:var(--accent);margin-bottom:6px;font-family:var(--mono);text-transform:uppercase;letter-spacing:0.05em}}

/* Calibration */
.cal-table{{width:100%;border-collapse:collapse;font-size:0.72rem}}
.cal-table th{{text-align:left;padding:4px 8px;color:var(--text-muted);font-weight:500;font-size:0.6rem;font-family:var(--mono);border-bottom:1px solid var(--border);text-transform:uppercase}}
.cal-table td{{padding:4px 8px;border-bottom:1px solid var(--border-light);color:var(--text-secondary);font-family:var(--mono)}}
.cal-bar{{transition:width 0.5s}}

/* Health */
.health-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:10px}}
.health-item{{background:var(--bg);border:1px solid var(--border);border-radius:var(--radius-sm);padding:10px;text-align:center}}
.health-item .value{{font-size:1.1rem;font-weight:700;color:var(--text);font-family:var(--mono)}}
.health-item .label{{font-size:0.6rem;color:var(--text-muted);font-family:var(--mono);margin-top:2px;text-transform:uppercase;letter-spacing:0.05em}}

/* Timestamp */
.timestamp{{text-align:center;padding:20px 0;font-size:0.65rem;color:var(--text-muted);font-family:var(--mono);border-top:1px solid var(--border);margin-top:24px}}

/* Calibration header */
.cal-header{{display:flex;gap:20px;margin-bottom:14px;flex-wrap:wrap}}
.cal-stat{{font-size:0.75rem}}
.cal-stat .num{{color:var(--text);font-weight:600;font-family:var(--mono)}}
.cal-stat .lbl{{color:var(--text-muted);font-size:0.65rem}}
</style>
</head>
<body>
<div class="container">

<div class="header">
  <h1><span class="accent">Infinite</span> Engine</h1>
  <div class="sub">PyTorch Sports Prediction Framework · Multi-Model Ensemble · Self-Calibrating</div>
  <div class="stats-row">
    <span class="stat-chip"><strong>{results.get('total_simulations', 0):,}</strong> Monte Carlo trials</span>
    <span class="stat-chip"><strong>{len(results.get('leagues', {}))}</strong> leagues</span>
    <span class="stat-chip"><strong>{sum(len(v.get('roster', [])) for v in results.get('leagues', {}).values())}</strong> athletes tracked</span>
    <span class="stat-chip"><strong>{sum(len(v.get('upcoming', [])) for v in results.get('leagues', {}).values())}</strong> active predictions</span>
    <span class="stat-chip"><strong>{results.get('timestamp', '')}</strong></span>
  </div>
</div>

<div class="dashboard-grid">
  <div class="card">
    <h2>Standings</h2>
    {standings_html}
  </div>

  <div class="card">
    <h2>Upcoming Predictions</h2>
    <div style="max-height:600px;overflow-y:auto;padding-right:4px">
    {games_html}
    </div>
  </div>

  <div class="card full-width">
    <h2>Player Projections &amp; Stat Leaderboards</h2>
    <div class="dashboard-grid">
      {players_html}
    </div>
  </div>

  <div class="card full-width">
    <h2>Player Face-offs</h2>
    <div class="dashboard-grid" style="grid-template-columns:repeat(auto-fill,minmax(280px,1fr))">
      {faceoffs_html}
    </div>
  </div>

  <div class="card full-width">
    <h2>Calibration &amp; Model Health</h2>
    <div class="cal-header">
      <div class="cal-stat"><span class="num">{health.get('total_predictions', 0)}</span> <span class="lbl">predictions tracked</span></div>
      <div class="cal-stat"><span class="num">{health.get('avg_error', 0)}</span> <span class="lbl">avg error</span></div>
      <div class="cal-stat"><span class="num">{health.get('brier_score', 0)}</span> <span class="lbl">Brier score</span></div>
    </div>
    <div class="health-grid" style="margin-bottom:14px">
      {''.join(f'<div class="health-item"><div class="value">{v}%</div><div class="label">{k}</div></div>' for k, v in health.get('model_weights', {}).items())}
    </div>
    <table class="cal-table">
      <thead><tr><th>Bin</th><th>Predicted</th><th>Actual</th><th>Calibration</th><th>Count</th></tr></thead>
      <tbody>{cal_rows}</tbody>
    </table>
  </div>
</div>

<div class="timestamp">
  INFINITE ENGINE v1.0 — Generated {results.get('timestamp', '')} — Next cycle in 60 minutes
</div>

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
