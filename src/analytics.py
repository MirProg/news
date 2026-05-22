"""
Book Analytics Engine — implements key techniques from
"AI, Optimization, and Data Sciences in Sports" (Springer 2025):

  1. Pythagorean Weibull Method of Moments    (Ch.13 — Almeida et al.)
  2. PageRank team rankings                    (Ch.12 — Butenko et al.)
  3. K-means player clustering                 (Ch.11 — Capanema et al.)
  4. TRIMP consistency / efficiency ratio      (Ch.11)
  5. Forgotten-effects impact analysis         (Ch.10 — Gil-Lafuente)
"""

import math, random, json
from collections import defaultdict

# ─────────────────────────────────────────────────────────────────────
#  1. PYTHAGOREAN Weibull — Method of Moments  (Ch.13)
# ─────────────────────────────────────────────────────────────────────

GAMMA_CACHE = {}

def gamma_func(x):
    """Lanczos approximation of Gamma(x) for x > 0."""
    g = 7
    c = [0.99999999999980993, 676.5203681218851, -1259.1392167224028,
         771.32342877765313, -176.61502916214059, 12.507343278686905,
         -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7]
    x -= 1
    y = c[0]
    for i in range(1, g + 2):
        y += c[i] / (x + i)
    t = x + g + 0.5
    return math.sqrt(2 * math.pi) * t ** (x + 0.5) * math.exp(-t) * y


def weibull_mean(alpha, gamma, beta=0):
    return alpha * gamma_func(1 + 1/gamma) + beta


def weibull_var(alpha, gamma):
    m1 = gamma_func(1 + 1/gamma)
    m2 = gamma_func(1 + 2/gamma)
    return alpha * alpha * (m2 - m1 * m1)


def solve_weibull_params(mu, sigma2, beta=-0.5):
    """Solve for alpha, gamma from mean & variance using grid search + refinement."""
    best = None
    best_err = float('inf')
    for gamma in [g/10 for g in range(5, 35)]:
        m1 = gamma_func(1 + 1/gamma)
        if m1 <= 0: continue
        alpha = (mu - beta) / m1
        if alpha <= 0: continue
        calc_var = weibull_var(alpha, gamma)
        err = abs(calc_var - sigma2)
        if err < best_err:
            best_err = err
            best = (alpha, gamma)
    return best if best else (1.0, 1.5)


def pythagorean_mom_win_pct(rs_mean, rs_var, ra_mean, ra_var, beta=-0.5):
    """Compute Pythagorean win% using MoM Weibull (different gamma for RS/RA)."""
    a_rs, g_rs = solve_weibull_params(rs_mean, rs_var, beta)
    a_ra, g_ra = solve_weibull_params(ra_mean, ra_var, beta)
    if a_rs <= 0 or a_ra <= 0:
        return 0.5, 1.5, 1.5

    # Numerical integration: P(RS > RA) via Simpson's rule
    def f_rs(x):
        if x < beta: return 0
        z = (x - beta) / a_rs
        return (g_rs / a_rs) * (z ** (g_rs - 1)) * math.exp(-(z ** g_rs))

    def cdf_ra(x):
        if x < beta: return 0
        z = (x - beta) / a_ra
        return 1 - math.exp(-(z ** g_ra))

    lo, hi = beta, max(beta + 1, rs_mean + 4 * math.sqrt(rs_var))
    n = 200
    h = (hi - lo) / n
    total = 0.0
    for i in range(n):
        x = lo + (i + 0.5) * h
        total += f_rs(x) * cdf_ra(x) * h

    return min(0.99, max(0.01, total)), round(g_rs, 3), round(g_ra, 3)


def pythag_analysis(team_name, games, league_mean, league_std):
    """Full Pythagorean analysis for one team across a list of game dicts."""
    if not games:
        return None
    rs = [g.get("score1", 0) for g in games if g.get("team1") == team_name]
    rs += [g.get("score2", 0) for g in games if g.get("team2") == team_name]
    ra = [g.get("score2", 0) for g in games if g.get("team1") == team_name]
    ra += [g.get("score1", 0) for g in games if g.get("team2") == team_name]
    if len(rs) < 5:
        return None

    rs_mean = sum(rs) / len(rs)
    ra_mean = sum(ra) / len(ra)
    rs_var = sum((r - rs_mean)**2 for r in rs) / len(rs)
    ra_var = sum((r - ra_mean)**2 for r in ra) / len(ra)

    actual_wins = sum(1 for g in games if g.get("winner") == team_name)
    actual_win_pct = actual_wins / max(1, len(games))

    mom_wp, g_rs, g_ra = pythagorean_mom_win_pct(rs_mean, rs_var, ra_mean, ra_var)
    pred_wins = mom_wp * len(games)

    return {
        "team": team_name,
        "n_games": len(games),
        "actual_wins": actual_wins,
        "actual_win_pct": round(actual_win_pct, 3),
        "rs_mean": round(rs_mean, 2),
        "ra_mean": round(ra_mean, 2),
        "rs_var": round(rs_var, 2),
        "ra_var": round(ra_var, 2),
        "gamma_rs": g_rs,
        "gamma_ra": g_ra,
        "mom_wp": round(mom_wp, 3),
        "pred_wins": round(pred_wins, 1),
        "win_diff": round(pred_wins - actual_wins, 1),
        "lucky": pred_wins < actual_wins,
    }


# ─────────────────────────────────────────────────────────────────────
#  2. PAGERANK RANKINGS  (Ch.12)
# ─────────────────────────────────────────────────────────────────────

def page_rank_teams(games, teams, damping=0.85, max_iter=100, tol=1e-6):
    """PageRank for team ranking based on win/loss network."""
    n = len(teams)
    idx = {t: i for i, t in enumerate(teams)}
    M = [[0.0] * n for _ in range(n)]

    out_degree = [0] * n
    for g in games:
        w = g.get("winner")
        if w == "draw" or w is None:
            continue
        t1, t2 = g.get("team1"), g.get("team2")
        if t1 is None or t2 is None:
            continue
        loser = t2 if w == t1 else t1
        i, j = idx.get(t1), idx.get(t2)
        if i is None or j is None:
            continue
        # Winner links to loser: "defeated by" logic
        if w == t1:
            M[j][i] += 1.0
            out_degree[i] += 1
        else:
            M[i][j] += 1.0
            out_degree[j] += 1

    # Normalize columns
    for j in range(n):
        col_sum = sum(M[i][j] for i in range(n))
        if col_sum > 0:
            for i in range(n):
                M[i][j] /= col_sum

    # Teleport
    for i in range(n):
        for j in range(n):
            M[i][j] = M[i][j] * damping + (1 - damping) / n

    # Power iteration
    ranks = [1.0 / n] * n
    for _ in range(max_iter):
        new_ranks = [0.0] * n
        for i in range(n):
            new_ranks[i] = sum(M[i][j] * ranks[j] for j in range(n))
        err = sum(abs(new_ranks[i] - ranks[i]) for i in range(n))
        ranks = new_ranks
        if err < tol:
            break

    ranked = sorted([(teams[i], ranks[i]) for i in range(n)], key=lambda x: -x[1])
    return [(t, round(r, 6), rank+1) for rank, (t, r) in enumerate(ranked)]


# ─────────────────────────────────────────────────────────────────────
#  3. K-MEANS PLAYER CLUSTERING  (Ch.11)
# ─────────────────────────────────────────────────────────────────────

def kmeans_players(players, k=3, max_iter=50):
    """K-means clustering using stat, games_played, and form features."""
    if len(players) < k:
        k = max(1, len(players))
    pts = [(p.get("stat", 0), p.get("games_played", 0), p.get("form", 0)) for p in players]
    if not pts:
        return [], []

    rng = random.Random(42)
    centroids = rng.sample(pts, k) if len(pts) >= k else pts[:]

    for _ in range(max_iter):
        clusters = [[] for _ in range(k)]
        for p, pt in zip(players, pts):
            dists = [abs(pt[0] - c[0]) + abs(pt[1] - c[1]) * 0.1 + abs(pt[2] - c[2]) * 5 for c in centroids]
            clusters[dists.index(min(dists))].append(p)
        new_centroids = []
        for c in clusters:
            if not c:
                new_centroids.append(rng.choice(pts))
            else:
                avg_s = sum(p.get("stat", 0) for p in c) / len(c)
                avg_g = sum(p.get("games_played", 0) for p in c) / len(c)
                avg_f = sum(p.get("form", 0) for p in c) / len(c)
                new_centroids.append((avg_s, avg_g, avg_f))
        if all(abs(new_centroids[i][0] - centroids[i][0]) < 0.1 for i in range(k)):
            break
        centroids = new_centroids

    labels = []
    for p in players:
        pt = (p.get("stat", 0), p.get("games_played", 0), p.get("form", 0))
        dists = [abs(pt[0] - c[0]) + abs(pt[1] - c[1]) * 0.1 + abs(pt[2] - c[2]) * 5 for c in centroids]
        labels.append(dists.index(min(dists)))

    all_stats = [p.get("stat", 0) for p in players]
    mean_s = sum(all_stats) / len(all_stats) if all_stats else 50
    std_s = (sum((s - mean_s)**2 for s in all_stats) / len(all_stats))**0.5 if len(all_stats) > 1 else 1

    profiles = []
    for ci in range(k):
        members = [p for p, l in zip(players, labels) if l == ci]
        if not members:
            profiles.append(f"Cluster {ci+1}")
            continue
        avg_s = sum(m.get("stat", 0) for m in members) / len(members)
        avg_f = sum(m.get("form", 0) for m in members) / len(members)
        if avg_s > mean_s + std_s:
            label = f"Star ({len(members)} players)"
        elif avg_s > mean_s:
            label = f"Core ({len(members)} players)"
        else:
            label = f"Rotation ({len(members)} players)"
        profiles.append(label)

    return labels, profiles


# ─────────────────────────────────────────────────────────────────────
#  4. TRIMP CONSISTENCY / EFFICIENCY RATIO  (Ch.11)
# ─────────────────────────────────────────────────────────────────────

def efficiency_ratio(player_stat, league_avg, games_played, max_games):
    """Compute a PEI-style efficiency: output per unit opportunity."""
    if games_played == 0:
        return 0
    usage = games_played / max(1, max_games)
    relative_output = player_stat / max(0.1, league_avg)
    pei = relative_output / max(0.1, usage)
    return round(pei, 3)


def trimp_consistency(scores):
    """Simulate TRIMP consistency: std of game-to-game output."""
    if len(scores) < 3:
        return 1.0
    mu = sum(scores) / len(scores)
    var = sum((s - mu)**2 for s in scores) / len(scores)
    cv = math.sqrt(var) / max(0.01, mu)  # coefficient of variation
    consistency = max(0, 1.0 - cv)
    return round(consistency, 3)


# ─────────────────────────────────────────────────────────────────────
#  5. FORGOTTEN EFFECTS ANALYSIS  (Ch.10)
# ─────────────────────────────────────────────────────────────────────

def forgotten_effects(direct_matrix, interaction_matrix, obj_interaction):
    """Compute second-generation effects using max-min convolution."""
    n_prop = len(direct_matrix)
    n_obj = len(direct_matrix[0]) if direct_matrix else 0
    if n_prop == 0 or n_obj == 0:
        return direct_matrix

    # Max-min: [P] ∘ [M] ∘ [O]
    pm = [[0.0] * n_obj for _ in range(n_prop)]
    for i in range(n_prop):
        for k in range(n_obj):
            vals = []
            for j in range(len(interaction_matrix[i])):
                if j < len(pm):
                    vals.append(min(interaction_matrix[i][j], direct_matrix[j][k] if j < len(direct_matrix) else 0))
            pm[i][k] = max(vals) if vals else 0

    result = [[0.0] * n_obj for _ in range(n_prop)]
    for i in range(n_prop):
        for k in range(n_obj):
            vals = []
            for j in range(len(obj_interaction)):
                if j < len(pm[i]):
                    vals.append(min(pm[i][j], obj_interaction[j][k] if j < len(obj_interaction) and k < len(obj_interaction[j]) else 0))
            result[i][k] = max(vals) if vals else 0

    return result


# ─────────────────────────────────────────────────────────────────────
#  ORCHESTRATOR – run all analytics for a WorldSportsEngine
# ─────────────────────────────────────────────────────────────────────

def run_all_analytics(engine):
    """Run all book analytics on the engine's sports data and predictions."""
    results = {}

    for key, pred in engine.predictors.items():
        data = pred.data
        sport_results = {}

        # --- Pythagorean MoM (for MLB, NBA, NHL — scoring sports) ---
        if key in ("MLB", "NBA", "NHL", "EPL", "Cricket_T20", "Rugby"):
            teams = data.teams
            games = data.history
            if games and teams:
                league_games = len(games)
                total_scores = []
                for g in games:
                    if "score1" in g:
                        total_scores.append(g.get("score1", 0))
                        total_scores.append(g.get("score2", 0))
                league_mean = sum(total_scores) / max(1, len(total_scores))
                league_var = sum((s - league_mean)**2 for s in total_scores) / max(1, len(total_scores))

                team_pythag = []
                for team in teams:
                    analysis = pythag_analysis(team, games, league_mean, math.sqrt(league_var))
                    if analysis:
                        team_pythag.append(analysis)

                team_pythag.sort(key=lambda x: -x["mom_wp"])
                sport_results["pythagorean"] = {
                    "league": key,
                    "league_mean": round(league_mean, 2),
                    "teams": team_pythag,
                    "avg_gamma_rs": round(sum(t["gamma_rs"] for t in team_pythag) / max(1, len(team_pythag)), 3),
                    "avg_gamma_ra": round(sum(t["gamma_ra"] for t in team_pythag) / max(1, len(team_pythag)), 3),
                }

        # --- PageRank ---
        if data.teams and data.history:
            pr = page_rank_teams(data.history, data.teams)
            sport_results["page_rank"] = [(t, r, rk) for t, r, rk in pr]

        # --- K-means player clusters (using engine-derived dimension data) ---
        if data.players and data.players.get("all"):
            spec = data.spec
            total_games = len(data.history)
            max_games = max(total_games, 82)
            base_stat = spec.get("mean", 70)
            if base_stat <= 0:
                base_stat = 100

            players_data = []
            for p in data.players["all"]:
                form = data.dims["form"].form.get(p, 0)
                health = data.dims["health"].health.get(p, 0)
                sentiment = data.dims["sentiment"].sentiment.get(p, 0)

                stat = base_stat * (0.6 + (form + 1) * 0.2)
                stat = min(spec.get("max", base_stat * 2), max(spec.get("min", 0), stat))

                health_factor = (health + 1) / 2
                gp = int(max_games * (0.2 + 0.6 * health_factor))

                players_data.append({
                    "name": p,
                    "stat": round(stat, 1),
                    "games_played": gp,
                    "form": round(form, 3),
                    "health": round(health, 3),
                    "sentiment": round(sentiment, 3),
                })

            league_avg = sum(p["stat"] for p in players_data) / max(1, len(players_data))
            labels, profiles = kmeans_players(players_data)
            player_clusters = []
            for p, l in zip(players_data, labels):
                player_clusters.append({
                    "name": p["name"],
                    "stat": p["stat"],
                    "games": p["games_played"],
                    "cluster": l,
                    "pei": efficiency_ratio(p["stat"], league_avg, p["games_played"], max_games),
                })
            sport_results["player_clusters"] = {
                "profiles": profiles,
                "players": player_clusters,
            }

        # --- TRIMP consistency (simulate game-by-game scores) ---
        if games:
            team_consistency = {}
            for team in (data.teams or [])[:10]:
                team_scores = []
                for g in games:
                    if g.get("team1") == team:
                        team_scores.append(g.get("score1", 0))
                    if g.get("team2") == team:
                        team_scores.append(g.get("score2", 0))
                if team_scores:
                    team_consistency[team] = {
                        "consistency": trimp_consistency(team_scores),
                        "avg_score": round(sum(team_scores) / len(team_scores), 1),
                        "n_games": len(team_scores),
                    }
            sport_results["trimp_consistency"] = team_consistency

        # --- Forgotten Effects (synthetic Ch.10 example) ---
        direct = [
            [0.8, 0.2, 0.3],
            [0.7, 0.4, 0.2],
            [0.5, 0.1, 0.1],
            [0.3, 0.6, 0.4],
            [0.6, 0.3, 0.7],
        ]
        interaction = [
            [1.0, 0.3, 0.2, 0.4, 0.5],
            [0.3, 1.0, 0.1, 0.6, 0.4],
            [0.2, 0.1, 1.0, 0.3, 0.1],
            [0.4, 0.6, 0.3, 1.0, 0.5],
            [0.5, 0.4, 0.1, 0.5, 1.0],
        ]
        obj_interact = [
            [1.0, 0.2, 0.3],
            [0.2, 1.0, 0.6],
            [0.3, 0.6, 1.0],
        ]
        fe_result = forgotten_effects(direct, interaction, obj_interact)
        property_names = ["Home Advantage", "Player Form", "Head-to-Head", "Momentum", "Fitness"]
        objective_names = ["Win Probability", "Revenue", "Fan Attendance"]
        sport_results["forgotten_effects"] = {
            "properties": property_names,
            "objectives": objective_names,
            "direct": direct,
            "result": [[round(v, 3) for v in row] for row in fe_result],
        }

        results[key] = sport_results

    return results
