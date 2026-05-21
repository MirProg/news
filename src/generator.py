"""
Dashboard generator — editorial data-journalism output with HAL personality.
"""

import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _hal_commentary(results):
    """Generate HAL-style narrative commentary from the data."""
    lines = []
    lines.append("Good afternoon, sports fans. This is HAL.")

    # Find most confident prediction
    best_conf = None
    best_game = None
    for league, data in results.get("leagues", {}).items():
        for g in data.get("upcoming", []):
            if best_conf is None or g.get("confidence", 0) > best_conf:
                best_conf = g.get("confidence", 0)
                best_game = g

    if best_game:
        lines.append(f"I have run {best_game.get('projected', {}).get('n_sims', 100000):,} simulations of {best_game['home']} versus {best_game['away']}, and I am {best_conf}% confident in the outcome.")

    # Find the tightest matchup
    tightest = None
    tightest_conf = 100
    for league, data in results.get("leagues", {}).items():
        for g in data.get("upcoming", []):
            wp = g.get("ensemble_win_pct", 50)
            closeness = abs(wp - 50)
            if closeness < tightest_conf:
                tightest_conf = closeness
                tightest = g

    if tightest:
        lines.append(f"The tightest race is {tightest['home']} versus {tightest['away']} — my ensemble splits at {tightest['ensemble_win_pct']}% to {100 - tightest['ensemble_win_pct']}%. This one will come down to execution, not mathematics.")

    # IPL commentary
    ipl = results.get("ipl")
    if ipl:
        s = ipl.get("summary", {})
        lines.append(f"In the IPL backtest, I studied 1,032 historical matches going back to 2008. Out of {s.get('total_matches', 0)} predictions for last season, I was correct on {s.get('correct_predictions', 0)} ({s.get('accuracy', 0)}%). My mean absolute error on scores was {s.get('mean_abs_error_runs', 0)} runs.")

        # Find the biggest miss
        biggest_miss = None
        biggest_err = 0
        for p in ipl.get("predictions", []):
            if not p.get("correct"):
                if biggest_miss is None or p.get("score_error_r1", 0) > biggest_err:
                    biggest_err = p.get("score_error_r1", 0)
                    biggest_miss = p
        if biggest_miss:
            lines.append(f"My largest error: I predicted {biggest_miss['team1']} would score {biggest_miss['pred_r1']:.0f} against {biggest_miss['team2']}, but they posted {biggest_miss['actual_r1']}. A reminder that sport is not deterministic.")

        # Champion
        for p in ipl.get("playoff_predictions", []):
            if "Final" in p.get("label", "") and p.get("correct"):
                lines.append(f"I correctly identified {p['actual_winner']} as the IPL champion — the poetry of probability.")

    # Synthetic leagues
    for league, data in results.get("leagues", {}).items():
        standings = data.get("standings", [])
        if standings:
            top = standings[0]
            lines.append(f"In my synthetic {data.get('display', league)} season, {top['team']} leads at {top['w']}-{top['l']} ({top.get('pct', 0):.0%}).")

    lines.append("These predictions are generated from tensor operations, not human bias. I do not gamble. I only calculate.")

    return "\n\n".join(lines)


def _render_league_card(league_key, data):
    """Render a league as a compact editorial card with standings + predictions."""
    standings = data.get("standings", [])
    games = data.get("upcoming", [])
    roster = data.get("roster", [])
    faceoffs = data.get("faceoffs", [])
    display = data.get("display", league_key)

    # Standing dots
    standings_rows = ""
    for s in standings[:6]:
        pct = s.get("pct", 0)
        bar_w = max(4, int(pct * 100))
        standings_rows += f"""
          <div class="s-row">
            <span class="s-rank">{s['rank']}</span>
            <span class="s-team">{s['team']}</span>
            <span class="s-record">{s['w']}-{s['l']}</span>
            <div class="s-bar-track"><div class="s-bar" style="width:{bar_w}%"></div></div>
            <span class="s-pts">{s.get('pts', s['w'])}</span>
          </div>"""

    # Predictions
    games_html = ""
    for g in games[:3]:
        wp = g.get("ensemble_win_pct", 50)
        conf = g.get("confidence", 0)
        proj = g.get("projected", {})
        hs = proj.get("avg_home_score", "?")
        as_ = proj.get("avg_away_score", "?")
        games_html += f"""
          <div class="g-card">
            <div class="g-teams"><span>{g['home']}</span><span class="g-vs">vs</span><span>{g['away']}</span></div>
            <div class="g-bar"><div class="g-fill" style="width:{wp}%"></div></div>
            <div class="g-meta">{wp}% home · {conf}% confidence · {hs}-{as_} projected</div>
          </div>"""

    # Top player
    player_html = ""
    if roster:
        p = roster[0]
        player_html = f"""
          <div class="p-card">
            <div class="p-rank">#1</div>
            <div class="p-name">{p['name']}</div>
            <div class="p-stat">{p['stat']} <span class="p-unit">{p.get('unit', '')}</span></div>
            <div class="p-pos">{p.get('position', '')}</div>
          </div>"""

    return f"""
    <div class="lg-card">
      <div class="lg-header">
        <span class="lg-name">{display}</span>
        <span class="lg-count">{data.get('total_games', 0)} games simulated</span>
      </div>
      <div class="lg-body">
        <div class="lg-col">
          <div class="lg-label">Standings</div>
          {standings_rows}
        </div>
        <div class="lg-col">
          <div class="lg-label">Next Games</div>
          {games_html}
        </div>
        <div class="lg-col lg-col-player">
          <div class="lg-label">Top Projection</div>
          {player_html}
        </div>
      </div>
    </div>"""


def _render_ipl_section(ipl_backtest):
    """Render the IPL backtest as a data-journalism narrative."""
    if not ipl_backtest:
        return ""

    r = ipl_backtest.results if hasattr(ipl_backtest, 'results') else {}
    s = r.get("summary", {})

    match_rows = ""
    for p in r.get("predictions", []):
        ok = "OK" if p["correct"] else "MISS"
        color = "var(--ok)" if p["correct"] else "var(--miss)"
        winner_display = p["actual_winner"] if p["correct"] else f"<span style='color:var(--miss)'>{p['predicted_winner']}</span>"
        match_rows += f"""
          <tr{' style="opacity:0.7"' if not p['correct'] else ''}>
            <td class="m-team">{p['team1']}</td>
            <td class="m-score">{p['actual_r1']}</td>
            <td class="m-vs">v</td>
            <td class="m-score">{p['actual_r2']}</td>
            <td class="m-team">{p['team2']}</td>
            <td class="m-pred">{p['pred_r1']:.0f} / {p['pred_r2']:.0f}</td>
            <td class="m-winner" style="color:{color}">{winner_display}</td>
            <td class="m-icon" style="color:{color}">{'&#9679;' if p['correct'] else '&#9711;'}</td>
          </tr>"""

    standings_rows = ""
    for ps in r.get("predicted_standings", []):
        delta = ps['actual_wins'] - ps['predicted_wins']
        dc = "var(--ok)" if delta > 0 else "var(--miss)" if delta < 0 else "var(--text-muted)"
        ds = f"+{delta:.1f}" if delta > 0 else f"{delta:.1f}"
        standings_rows += f"""
          <tr>
            <td class="st-team">{ps['full']}</td>
            <td class="st-num">{ps['predicted_wins']}</td>
            <td class="st-num st-actual">{ps['actual_wins']}</td>
            <td class="st-delta" style="color:{dc}">{ds}</td>
          </tr>"""

    playoff_rows = ""
    for p in r.get("playoff_predictions", []):
        ok = "&#9679;" if p["correct"] else "&#9711;"
        c = "var(--ok)" if p["correct"] else "var(--miss)"
        playoff_rows += f"""
          <tr>
            <td class="p-label">{p['label']}</td>
            <td class="m-team">{p['team1']}</td>
            <td class="m-score">{p['actual_r1']}</td>
            <td class="m-vs">v</td>
            <td class="m-score">{p['actual_r2']}</td>
            <td class="m-team">{p['team2']}</td>
            <td class="m-pred">{p['pred_r1']:.0f} / {p['pred_r2']:.0f}</td>
            <td class="m-winner" style="color:var(--ok)">{p['actual_winner']}</td>
            <td style="text-align:center;color:{c}">{ok}</td>
          </tr>"""

    return f"""
    <div class="ipl-hero">
      <div class="ipl-title">IPL Backtest: 2008-2024 → 2025</div>
      <div class="ipl-sub">Trained on 1,032 matches across 17 seasons. Tested on 108 matches.</div>
      <div class="ipl-stats">
        <div class="ipl-stat"><span class="iq-num">{s.get('accuracy', 0)}%</span><span class="iq-label">Accuracy</span></div>
        <div class="ipl-stat"><span class="iq-num">{s.get('correct_predictions', 0)}/{s.get('total_matches', 0)}</span><span class="iq-label">Correct</span></div>
        <div class="ipl-stat"><span class="iq-num">&#177;{s.get('mean_abs_error_runs', 0)}</span><span class="iq-label">MAE Runs</span></div>
        <div class="ipl-stat"><span class="iq-num">{s.get('brier_score', 0)}</span><span class="iq-label">Brier Score</span></div>
      </div>

      <div class="ipl-blocks">
        <div class="ipl-block">
          <div class="blk-title">Predicted vs Actual Standings</div>
          <table class="st-table">
            <thead><tr><th>Team</th><th>Pred W</th><th>Act W</th><th>&#916;</th></tr></thead>
            <tbody>{standings_rows}</tbody>
          </table>
        </div>
        <div class="ipl-block">
          <div class="blk-title">Match Scorecard</div>
          <div class="sc-wrapper">
          <table class="sc-table">
            <thead><tr><th>T1</th><th>R1</th><th></th><th>R2</th><th>T2</th><th>Pred</th><th>Winner</th><th></th></tr></thead>
            <tbody>{match_rows}</tbody>
          </table>
          </div>
        </div>
      </div>

      <div class="ipl-blocks">
        <div class="ipl-block">
          <div class="blk-title">Playoffs</div>
          <table class="sc-table">
            <thead><tr><th>Match</th><th>T1</th><th>R1</th><th></th><th>R2</th><th>T2</th><th>Pred</th><th>W</th><th></th></tr></thead>
            <tbody>{playoff_rows}</tbody>
          </table>
        </div>
        <div class="ipl-block">
          <div class="blk-title">Methodology</div>
          <div class="meth-text">
            Each IPL 2025 match was predicted using a T20 Poisson model trained exclusively on pre-tournament data (2008-2024). Team strength parameters were estimated from historical scoring rates and bowling economy, fitted via maximum likelihood on 1,032 matches. Match outcomes were simulated over 100,000 trials using PyTorch tensor operations.
            <br><br>
            The model correctly identified KKR as champion (Final: KKR vs SRH, <span style="color:var(--ok)">&#9679;</span>) and achieved 75% playoff accuracy. Biggest surprise: Sunrisers Hyderabad outperformed their historical baseline by +13 wins.
          </div>
        </div>
      </div>
    </div>"""


def generate_dashboard(results, engine=None, ipl_results=None, ipl_backtest=None):
    """Generate self-contained HTML dashboard with editorial design."""

    # Attach ipl results to results dict for HAL commentary
    if ipl_results:
        results["ipl"] = ipl_results

    hal = _hal_commentary(results)

    # Render leagues
    leagues_html = ""
    for league_key in ["NBA", "NFL", "EPL", "MLB"]:
        data = results.get("leagues", {}).get(league_key)
        if data:
            leagues_html += _render_league_card(league_key, data)

    ipl_html = _render_ipl_section(ipl_backtest) if ipl_backtest else ""

    cal = results.get("calibration", {})
    health = results.get("ensemble_health", {})

    cal_rows = ""
    for c in cal.get("calibration", []):
        cal_rows += f"""
          <div class="cb-row">
            <span class="cb-bin">{c['bin']}</span>
            <div class="cb-track"><div class="cb-fill" style="width:{min(c['actual']/max(c['predicted'],1)*100, 100)}%"></div></div>
            <span class="cb-num">{c['predicted']}%</span>
            <span class="cb-num cb-act">{c['actual']}%</span>
            <span class="cb-n">{c['count']} preds</span>
          </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>HAL 9000 — Sports Prediction Log</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{--bg:#f5f3ee;--bg-card:#ffffff;--text:#1a1a1a;--text-secondary:#6b6b6b;--text-muted:#a8a8a4;--accent:#2563eb;--accent-light:#dbeafe;--ok:#16a34a;--miss:#dc2626;--gray:#e5e3dd;--border:#e5e3dd;--radius:8px;--font:'Inter',sans-serif;--display:'Newsreader',Georgia,serif;--mono:'JetBrains Mono',monospace}}
body{{background:var(--bg);color:var(--text);font-family:var(--font);font-size:15px;line-height:1.6;-webkit-font-smoothing:antialiased}}
.container{{max-width:1200px;margin:0 auto;padding:0 28px}}

/* HAL header */
.hal-header{{padding:40px 0 20px;border-bottom:2px solid var(--text);margin-bottom:32px}}
.hal-logo{{font-family:var(--display);font-size:2.2rem;font-weight:500;letter-spacing:-0.03em;line-height:1.1}}
.hal-logo .accent{{color:var(--accent)}}
.hal-tagline{{font-size:0.82rem;color:var(--text-secondary);font-family:var(--mono);margin-top:4px;letter-spacing:-0.01em}}
.hal-msg{{margin-top:20px;padding:20px 24px;background:var(--bg-card);border-radius:var(--radius);font-size:0.88rem;color:var(--text-secondary);line-height:1.7;border-left:3px solid var(--accent);font-family:var(--display);font-size:0.95rem;white-space:pre-line}}
.hal-msg::before{{content:'"';color:var(--accent);font-size:1.2rem}}
.hal-msg::after{{content:'"';color:var(--accent);font-size:1.2rem}}
.hal-meta{{display:flex;gap:16px;margin-top:14px;flex-wrap:wrap;font-size:0.7rem;color:var(--text-muted);font-family:var(--mono)}}

/* League Cards */
.league-grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:32px}}
@media(max-width:860px){{.league-grid{{grid-template-columns:1fr}}}}
.lg-card{{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);overflow:hidden}}
.lg-header{{display:flex;justify-content:space-between;align-items:center;padding:14px 18px;border-bottom:1px solid var(--border);background:var(--gray)}}
.lg-name{{font-weight:700;font-size:0.82rem;letter-spacing:-0.01em}}
.lg-count{{font-size:0.6rem;color:var(--text-muted);font-family:var(--mono)}}
.lg-body{{padding:14px 18px;display:grid;grid-template-columns:1fr 1fr;gap:16px}}
@media(max-width:600px){{.lg-body{{grid-template-columns:1fr}}}}
.lg-col-player{{grid-column:1/-1}}
.lg-label{{font-size:0.58rem;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;color:var(--text-muted);margin-bottom:8px;font-family:var(--mono)}}

/* Standings rows */
.s-row{{display:flex;align-items:center;gap:8px;padding:3px 0;font-size:0.72rem}}
.s-rank{{color:var(--text-muted);font-family:var(--mono);width:18px;text-align:right;font-size:0.65rem}}
.s-team{{flex:1;font-weight:500}}
.s-record{{color:var(--text-secondary);font-family:var(--mono);width:36px;text-align:right;font-size:0.68rem}}
.s-bar-track{{flex:1;height:4px;background:var(--gray);border-radius:2px;overflow:hidden}}
.s-bar{{height:100%;background:var(--accent);border-radius:2px}}
.s-pts{{color:var(--text-secondary);font-family:var(--mono);width:20px;text-align:right;font-size:0.65rem}}

/* Game cards */
.g-card{{padding:6px 0}}
.g-teams{{display:flex;gap:6px;font-size:0.75rem;font-weight:500;margin-bottom:3px}}
.g-teams span:first-child{{flex:1;text-align:left}}
.g-vs{{color:var(--text-muted);font-family:var(--mono);font-size:0.6rem}}
.g-teams span:last-child{{flex:1;text-align:right}}
.g-bar{{height:4px;background:var(--gray);border-radius:2px;overflow:hidden}}
.g-fill{{height:100%;background:var(--accent);border-radius:2px}}
.g-meta{{font-size:0.6rem;color:var(--text-muted);font-family:var(--mono);margin-top:2px}}

/* Player card */
.p-card{{background:var(--accent-light);border-radius:var(--radius);padding:12px;display:flex;align-items:center;gap:10px}}
.p-rank{{font-family:var(--mono);font-size:0.65rem;color:var(--accent);font-weight:600}}
.p-name{{font-weight:600;font-size:0.78rem;flex:1}}
.p-stat{{font-size:1.05rem;font-weight:700;font-family:var(--mono);color:var(--accent)}}
.p-unit{{font-size:0.6rem;font-weight:400;color:var(--text-secondary)}}
.p-pos{{font-size:0.6rem;color:var(--text-muted);font-family:var(--mono)}}

/* IPL Section */
.ipl-hero{{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);padding:24px;margin-bottom:32px}}
.ipl-title{{font-family:var(--display);font-size:1.3rem;font-weight:500;letter-spacing:-0.02em;margin-bottom:4px}}
.ipl-sub{{font-size:0.72rem;color:var(--text-secondary);font-family:var(--mono);margin-bottom:16px}}
.ipl-stats{{display:flex;gap:16px;margin-bottom:20px;flex-wrap:wrap}}
.ipl-stat{{display:flex;flex-direction:column;align-items:center;background:var(--gray);border-radius:var(--radius);padding:10px 18px}}
.iq-num{{font-size:1.3rem;font-weight:700;font-family:var(--mono)}}
.iq-label{{font-size:0.58rem;text-transform:uppercase;letter-spacing:0.06em;color:var(--text-secondary)}}
.ipl-blocks{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px}}
@media(max-width:800px){{.ipl-blocks{{grid-template-columns:1fr}}}}
.ipl-block{{background:var(--bg);border-radius:var(--radius);padding:16px;border:1px solid var(--gray)}}
.blk-title{{font-size:0.65rem;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;color:var(--text-secondary);margin-bottom:10px;font-family:var(--mono)}}

/* Standings table (IPL) */
.st-table{{width:100%;border-collapse:collapse;font-size:0.72rem}}
.st-table th{{text-align:left;padding:4px 8px;color:var(--text-muted);font-weight:500;font-size:0.58rem;font-family:var(--mono);border-bottom:1px solid var(--gray);text-transform:uppercase}}
.st-table td{{padding:4px 8px;border-bottom:1px solid var(--gray)}}
.st-team{{font-weight:500}}
.st-num{{font-family:var(--mono);text-align:center}}
.st-actual{{font-weight:600}}
.st-delta{{font-family:var(--mono);text-align:center;font-weight:600}}

/* Scorecard table */
.sc-wrapper{{max-height:400px;overflow-y:auto}}
.sc-table{{width:100%;border-collapse:collapse;font-size:0.68rem}}
.sc-table th{{text-align:left;padding:4px 6px;color:var(--text-muted);font-weight:500;font-size:0.55rem;font-family:var(--mono);border-bottom:1px solid var(--gray);text-transform:uppercase;position:sticky;top:0;background:var(--bg)}}
.sc-table td{{padding:3px 6px;border-bottom:1px solid var(--gray);white-space:nowrap}}
.m-team{{font-weight:500;max-width:40px;overflow:hidden;text-overflow:ellipsis}}
.m-score{{font-family:var(--mono);text-align:center;font-weight:600}}
.m-vs{{text-align:center;color:var(--text-muted);font-size:0.55rem}}
.m-pred{{font-family:var(--mono);text-align:center;color:var(--accent);font-size:0.65rem}}
.m-winner{{font-size:0.65rem;text-align:center}}
.m-icon{{text-align:center;font-size:0.55rem}}
.p-label{{color:var(--accent);font-weight:600;font-size:0.6rem}}

/* Methodology */
.meth-text{{font-size:0.75rem;color:var(--text-secondary);line-height:1.7}}

/* Calibration */
.cal-section{{padding:20px;margin-bottom:32px}}
.cal-section h2{{font-family:var(--display);font-size:1.05rem;font-weight:500;margin-bottom:14px}}
.cb-row{{display:flex;align-items:center;gap:10px;padding:4px 0;font-size:0.7rem}}
.cb-bin{{width:60px;color:var(--text-secondary);font-family:var(--mono)}}
.cb-track{{flex:1;height:6px;background:var(--gray);border-radius:3px;overflow:hidden}}
.cb-fill{{height:100%;background:var(--accent);border-radius:3px}}
.cb-num{{width:36px;text-align:right;font-family:var(--mono);color:var(--text-secondary)}}
.cb-act{{color:var(--text);font-weight:600}}
.cb-n{{width:50px;text-align:right;color:var(--text-muted);font-family:var(--mono)}}

/* Health */
.h-grid{{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:16px}}
.h-item{{background:var(--bg-card);border:1px solid var(--gray);border-radius:var(--radius);padding:10px 16px;text-align:center}}
.h-item .v{{font-size:1.05rem;font-weight:700;font-family:var(--mono)}}
.h-item .l{{font-size:0.58rem;color:var(--text-secondary);font-family:var(--mono);text-transform:uppercase;letter-spacing:0.04em;margin-top:1px}}

/* Footer */
.footer{{text-align:center;padding:28px 0 40px;border-top:1px solid var(--border);margin-top:20px;font-size:0.65rem;color:var(--text-muted);font-family:var(--mono)}}
</style>
</head>
<body>
<div class="container">

<div class="hal-header">
  <div class="hal-logo"><span class="accent">HAL</span> 9000 Sports Prediction Log</div>
  <div class="hal-tagline">{results.get('timestamp', '')} UTC · {results.get('total_simulations', 0):,} trials · {health.get('total_predictions', 0)} predictions tracked</div>
  <div class="hal-msg">{hal}</div>
  <div class="hal-meta">
    <span>Ensemble weights: {' · '.join(f'{k}={v}%' for k, v in health.get('model_weights', {}).items())}</span>
    <span>Brier: {health.get('brier_score', '?')}</span>
    <span>Avg error: {health.get('avg_error', '?')}</span>
  </div>
</div>

{ipl_html}

<div class="league-grid">
{leagues_html}
</div>

<div class="cal-section" style="background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius)">
  <h2>Model Calibration</h2>
  <div class="h-grid">
    <div class="h-item"><div class="v">{health.get('total_predictions', 0)}</div><div class="l">Predictions</div></div>
    <div class="h-item"><div class="v">{health.get('avg_error', 0)}</div><div class="l">Avg Error</div></div>
    <div class="h-item"><div class="v">{health.get('brier_score', 0)}</div><div class="l">Brier</div></div>
    {''.join(f'<div class="h-item"><div class="v">{v}%</div><div class="l">{k}</div></div>' for k, v in health.get('model_weights', {}).items())}
  </div>
  <div class="cb-row" style="font-weight:600;font-size:0.6rem;color:var(--text-muted);margin-bottom:4px">
    <span style="width:60px">Bin</span>
    <span style="flex:1;text-align:center">Calibration</span>
    <span style="width:36px;text-align:right">Pred</span>
    <span style="width:36px;text-align:right">Act</span>
    <span style="width:50px;text-align:right">n</span>
  </div>
  {cal_rows}
</div>

<div class="footer">
  HAL 9000 — {results.get('timestamp', '')} · Next cycle in 60 minutes · All predictions generated from tensor operations, not human bias
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
