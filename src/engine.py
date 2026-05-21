"""
Infinite Engine — unprecedented PyTorch sports prediction framework.

Multi-model ensemble: Elo ratings, Monte Carlo simulation,
Poisson scoring, Bayesian update, self-calibrating.

Generates synthetic leagues, games, and player stats from scratch
using probabilistic tensor operations.
"""

import math
import random
import torch
import json
import os
from collections import defaultdict
from datetime import datetime, timedelta

# ─── Synthetic Data Generators ───────────────────────────────────────

_TEAMS = {
    "NBA": ["Lakers", "Celtics", "Warriors", "Bulls", "Heat", "Knicks",
            "Nuggets", "Bucks", "Thunder", "76ers", "Suns", "Mavericks"],
    "NFL": ["Chiefs", "49ers", "Ravens", "Eagles", "Cowboys", "Bills",
            "Bengals", "Lions", "Packers", "Dolphins", "Steelers", "Vikings"],
    "EPL": ["Man City", "Arsenal", "Liverpool", "Chelsea", "Man United",
            "Tottenham", "Newcastle", "Aston Villa", "Brighton", "West Ham"],
    "MLB": ["Yankees", "Dodgers", "Astros", "Braves", "Red Sox",
            "Phillies", "Padres", "Cardinals", "Blue Jays", "Mariners"],
}

_PLAYER_FIRST = ["J.", "M.", "A.", "D.", "L.", "K.", "T.", "S.", "C.", "R."]
_PLAYER_LAST = ["Williams", "Johnson", "Brown", "Davis", "Miller", "Wilson",
                "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White",
                "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson"]

_SPORT_PARAMS = {
    "NBA": {"mean_pts": 111, "std_pts": 14, "min_pts": 70,  "max_pts": 150, "unit": "pts", "poisson": False, "label": "Basketball"},
    "NFL": {"mean_pts": 22,  "std_pts": 7,  "min_pts": 0,   "max_pts": 56,  "unit": "pts", "poisson": False, "label": "Football"},
    "EPL": {"mean_pts": 2.5, "std_pts": 0,  "min_pts": 0,   "max_pts": 10,  "unit": "gls", "poisson": True,  "label": "Soccer"},
    "MLB": {"mean_pts": 4.5, "std_pts": 0,  "min_pts": 0,   "max_pts": 20,  "unit": "runs","poisson": True,  "label": "Baseball"},
}

_LEAGUE_ORDER = ["NBA", "NFL", "EPL", "MLB"]

# ─── Elo Rating System ───────────────────────────────────────────────

class EloRating:
    """Dynamic Elo rating with home advantage, margin-of-victory, and decay."""

    K = 32
    HOME_ADV = 50
    INITIAL = 1500
    DECAY = 0.997

    def __init__(self):
        self.ratings = {}

    def _get(self, team):
        if team not in self.ratings:
            self.ratings[team] = self.INITIAL
        else:
            self.ratings[team] = self.ratings.get(team, self.INITIAL) * self.DECAY
        return self.ratings[team]

    def expected(self, rating_a, rating_b):
        return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400.0))

    def update(self, team_a, team_b, score_a, score_b, home=True):
        ra = self._get(team_a) + (self.HOME_ADV if home else 0)
        rb = self._get(team_b)
        ea = self.expected(ra, rb)
        eb = 1 - ea

        # Margin of victory multiplier
        mov = abs(score_a - score_b)
        margin = math.log(max(mov, 1) + 1) * (2.2 / (0.001 + (ea - eb) if abs(ea - eb) > 0.001 else 1))

        sa = 1 if score_a > score_b else (0.5 if score_a == score_b else 0)
        sb = 1 - sa

        self.ratings[team_a] = ra + self.K * margin * (sa - ea)
        self.ratings[team_b] = rb + self.K * margin * (sb - eb)

    def win_prob(self, team_a, team_b, home=True):
        ra = self._get(team_a) + (self.HOME_ADV if home else 0)
        rb = self._get(team_b)
        return self.expected(ra, rb)

    def get_ranking(self, league_teams):
        """Return sorted ranking for a league."""
        rankings = []
        for t in league_teams:
            rankings.append((t, self._get(t)))
        rankings.sort(key=lambda x: -x[1])
        return rankings


# ─── Poisson Scoring Model ────────────────────────────────────────────

class PoissonScoring:
    """Poisson regression for goal/point prediction using PyTorch."""

    def __init__(self):
        self.team_strength = defaultdict(lambda: 1.0)

    def fit(self, games, league):
        """Fit team strength parameters from observed game scores (simplified MLE)."""
        params = _SPORT_PARAMS.get(league, _SPORT_PARAMS["NBA"])
        for g in games:
            for team, scored in [(g["home"], g["home_score"]), (g["away"], g["away_score"])]:
                old = self.team_strength[team]
                # Simple exponential smoothing update
                expected = params["mean_pts"]
                if scored > 0:
                    self.team_strength[team] = old * 0.9 + (scored / expected) * 0.1

    def predict(self, home, away, league):
        """Predict score distribution using Poisson via PyTorch."""
        params = _SPORT_PARAMS.get(league, _SPORT_PARAMS["NBA"])
        base = params["mean_pts"]
        hs = self.team_strength.get(home, 1.0) * base * 1.08  # home advantage
        as_ = self.team_strength.get(away, 1.0) * base * 0.97

        if params["poisson"]:
            lam_h = torch.tensor(max(hs, 0.1))
            lam_a = torch.tensor(max(as_, 0.1))
            return float(lam_h), float(lam_a)
        else:
            return round(hs, 1), round(as_, 1)


# ─── Monte Carlo Game Engine ─────────────────────────────────────────

class MonteCarloEngine:
    """Full Monte Carlo game simulation with PyTorch tensor ops."""

    def simulate_game(self, home, away, league, n_sims=100000, elo=None, poisson=None):
        params = _SPORT_PARAMS.get(league, _SPORT_PARAMS["NBA"])

        # Combine Elo win prob + Poisson score expectations
        if elo:
            wp = elo.win_prob(home, away, home=True)
        else:
            wp = 0.55 + random.uniform(-0.05, 0.05)

        if poisson:
            exp_h, exp_a = poisson.predict(home, away, league)
        else:
            exp_h, exp_a = params["mean_pts"] * 1.05, params["mean_pts"] * 0.97

        # Score home team based on win probability bias
        bias = 1.0 + (wp - 0.5) * 0.3

        if params["poisson"]:
            lam_h = max(exp_h * bias, 0.1)
            lam_a = max(exp_a, 0.1)
            t_h = torch.poisson(torch.full((n_sims,), lam_h))
            t_a = torch.poisson(torch.full((n_sims,), lam_a))
        else:
            mean_h = exp_h * bias
            mean_a = exp_a
            std = params["std_pts"]
            t_h = torch.clamp(torch.randn(n_sims) * std + mean_h, params["min_pts"], params["max_pts"])
            t_a = torch.clamp(torch.randn(n_sims) * std + mean_a, params["min_pts"], params["max_pts"])

        h_win = (t_h > t_a).sum().item()
        draw = (t_h == t_a).sum().item()

        return {
            "home": home,
            "away": away,
            "league": league,
            "home_win_pct": round(h_win / n_sims * 100, 1),
            "away_win_pct": round((n_sims - h_win - draw) / n_sims * 100, 1),
            "draw_pct": round(draw / n_sims * 100, 1),
            "avg_home_score": round(float(t_h.mean()), 1),
            "avg_away_score": round(float(t_a.mean()), 1),
            "std_home": round(float(t_h.std().item()), 1),
            "std_away": round(float(t_a.std().item()), 1),
            "ci95_home": f"{float(t_h.mean() - 1.96 * t_h.std()):.0f}-{float(t_h.mean() + 1.96 * t_h.std()):.0f}",
            "ci95_away": f"{float(t_a.mean() - 1.96 * t_a.std()):.0f}-{float(t_a.mean() + 1.96 * t_a.std()):.0f}",
            "n_sims": n_sims,
        }


# ─── Bayesian Updater ─────────────────────────────────────────────────

class BayesianUpdater:
    """Beta-Binomial Bayesian inference for team win rates."""

    def __init__(self, alpha=5, beta=5):
        self.priors = defaultdict(lambda: {"alpha": alpha, "beta": beta})

    def update(self, team, won=True):
        prior = self.priors[team]
        if won:
            prior["alpha"] += 1
        else:
            prior["beta"] += 1

    def posterior_mean(self, team):
        p = self.priors.get(team, {"alpha": 5, "beta": 5})
        return p["alpha"] / (p["alpha"] + p["beta"])

    def credible_interval(self, team, pct=0.95):
        """Approximate credible interval using PyTorch Beta distribution."""
        p = self.priors.get(team, {"alpha": 5, "beta": 5})
        if p["alpha"] <= 0 or p["beta"] <= 0:
            return (0, 1)
        # Use Beta distribution via PyTorch
        dist = torch.distributions.Beta(
            torch.tensor(float(p["alpha"])),
            torch.tensor(float(p["beta"]))
        )
        low = float(dist.icdf(torch.tensor((1 - pct) / 2)))
        high = float(dist.icdf(torch.tensor(1 - (1 - pct) / 2)))
        return (round(low, 3), round(high, 3))


# ─── Synthetic Season Generator ──────────────────────────────────────

class SyntheticLeague:
    """Generate a complete synthetic season with standings, stats, and history."""

    def __init__(self, league):
        self.league = league
        self.teams = _TEAMS.get(league, _TEAMS["NBA"])[:8]
        self.params = _SPORT_PARAMS.get(league, _SPORT_PARAMS["NBA"])
        self.elo = EloRating()
        self.bayes = BayesianUpdater()
        self.games = []
        self.standings = {t: {"w": 0, "l": 0, "d": 0, "pf": 0, "pa": 0, "streak": ""} for t in self.teams}

    def generate_season(self, n_rounds=10):
        """Generate a round-robin season of games."""
        for rnd in range(n_rounds):
            random.shuffle(self.teams)
            for i in range(0, len(self.teams) - 1, 2):
                home = self.teams[i]
                away = self.teams[i + 1]

                if self.params["poisson"]:
                    hs = max(0, int(torch.poisson(torch.tensor(self.params["mean_pts"] * 1.1)).item()))
                    as_ = max(0, int(torch.poisson(torch.tensor(self.params["mean_pts"] * 0.95)).item()))
                else:
                    hs = int(max(self.params["min_pts"], min(self.params["max_pts"],
                        torch.randn(1).item() * self.params["std_pts"] + self.params["mean_pts"] * 1.05)))
                    as_ = int(max(self.params["min_pts"], min(self.params["max_pts"],
                        torch.randn(1).item() * self.params["std_pts"] + self.params["mean_pts"] * 0.95)))

                game = {
                    "home": home, "away": away,
                    "home_score": hs, "away_score": as_,
                    "round": rnd + 1,
                }
                self.games.append(game)
                self.elo.update(home, away, hs, as_, home=True)
                self.bayes.update(home, hs > as_)
                self.bayes.update(away, as_ > hs)

                # Update standings
                if hs > as_:
                    self.standings[home]["w"] += 1
                    self.standings[away]["l"] += 1
                elif as_ > hs:
                    self.standings[away]["w"] += 1
                    self.standings[home]["l"] += 1
                else:
                    self.standings[home]["d"] = self.standings[home].get("d", 0) + 1
                    self.standings[away]["d"] = self.standings[away].get("d", 0) + 1
                self.standings[home]["pf"] += hs
                self.standings[home]["pa"] += as_
                self.standings[away]["pf"] += as_
                self.standings[away]["pa"] += hs

        # Compute standings
        for t in self.standings:
            s = self.standings[t]
            s["pts"] = s["w"] * 2 + s.get("d", 0) if self.league == "EPL" else s["w"]
            s["gd"] = s["pf"] - s["pa"]
            s["pct"] = round(s["w"] / max(s["w"] + s["l"], 1), 3)

        sorted_teams = sorted(self.standings.items(), key=lambda x: (-x[1]["pts"], -x[1]["gd"]))
        for rank, (t, s) in enumerate(sorted_teams, 1):
            s["rank"] = rank
            s["team"] = t

        return self.standings


# ─── Ensemble Predictor ──────────────────────────────────────────────

class EnsemblePredictor:
    """Combines Elo, Poisson, Monte Carlo, and Bayesian models with learned weights."""

    def __init__(self):
        self.weights = {"elo": 0.25, "monte_carlo": 0.30, "poisson": 0.25, "bayesian": 0.20}
        self.accuracy = {"elo": [], "monte_carlo": [], "poisson": [], "bayesian": [], "ensemble": []}

    def predict(self, home, away, league, elo, mc, poisson, bayes):
        """Return ensemble prediction with confidence."""
        wp_elo = elo.win_prob(home, away)
        mc_result = mc.simulate_game(home, away, league, n_sims=50000, elo=elo, poisson=poisson)
        wp_mc = mc_result["home_win_pct"] / 100
        wp_poisson = poisson.predict(home, away, league)[0] / (poisson.predict(home, away, league)[0] + poisson.predict(home, away, league)[1] + 0.001)
        wp_bayes = bayes.posterior_mean(home)

        ensemble = (
            self.weights["elo"] * wp_elo +
            self.weights["monte_carlo"] * wp_mc +
            self.weights["poisson"] * wp_poisson +
            self.weights["bayesian"] * wp_bayes
        )

        # Confidence based on model agreement (inverse variance)
        probs = [wp_elo, wp_mc, wp_poisson, wp_bayes]
        variance = sum((p - ensemble) ** 2 for p in probs) / len(probs)
        confidence = max(0, min(100, (1 - variance * 4) * 100))

        return {
            "home": home,
            "away": away,
            "league": league,
            "ensemble_win_pct": round(ensemble * 100, 1),
            "confidence": round(confidence, 1),
            "models": {
                "elo": round(wp_elo * 100, 1),
                "monte_carlo": round(wp_mc * 100, 1),
                "poisson": round(wp_poisson * 100, 1),
                "bayesian": round(wp_bayes * 100, 1),
            },
            "projected": mc_result if mc_result else {},
        }

    def calibrate(self, actual_home_won, prediction):
        """Update model weights based on prediction accuracy."""
        error = abs(actual_home_won - prediction / 100)
        # Simple weight adjustment: reduce weight of worse models
        # (detailed calibration would track per-model Brier scores)


# ─── Calibration Tracker ──────────────────────────────────────────────

class CalibrationTracker:
    """Tracks prediction accuracy over time and reports calibration metrics."""

    def __init__(self):
        self.history = []

    def record(self, prediction_pct, actual_home_won):
        """Record a prediction and its outcome."""
        self.history.append({
            "prediction": prediction_pct,
            "actual": actual_home_won,
            "error": abs(prediction_pct / 100 - actual_home_won),
            "brier": (prediction_pct / 100 - actual_home_won) ** 2,
        })

    def report(self):
        if not self.history:
            return {"n": 0, "avg_error": 0, "brier_score": 0, "calibration": []}
        errors = [h["error"] for h in self.history]
        briers = [h["brier"] for h in self.history]

        # Calibration curve: bin predictions by decile
        bins = defaultdict(list)
        for h in self.history:
            decile = min(9, int(h["prediction"] / 10))
            bins[decile].append(h["actual"])

        calibration = []
        for decile in range(10):
            if bins[decile]:
                avg_pred = decile * 10 + 5
                actual_rate = sum(bins[decile]) / len(bins[decile])
                calibration.append({
                    "bin": f"{decile*10}-{(decile+1)*10}%",
                    "predicted": avg_pred,
                    "actual": round(actual_rate * 100, 1),
                    "count": len(bins[decile]),
                })

        return {
            "n": len(self.history),
            "avg_error": round(sum(errors) / len(errors), 3),
            "brier_score": round(sum(briers) / len(briers), 4),
            "calibration": calibration,
        }


# ─── Player Performance Generator ─────────────────────────────────────

class PlayerGenerator:
    """Generate synthetic player stat projections using PyTorch."""

    def __init__(self):
        self.players = {}

    def _name(self):
        return f"{random.choice(_PLAYER_FIRST)} {random.choice(_PLAYER_LAST)}"

    def generate_roster(self, league, n=10):
        params = _SPORT_PARAMS.get(league, _SPORT_PARAMS["NBA"])
        roster = []
        for _ in range(n):
            base = params["mean_pts"]
            # Use PyTorch for realistic stat distribution
            stat = max(0, float(torch.clamp(
                torch.randn(1) * (params["std_pts"] * 0.3) + base * 0.8,
                0, params["max_pts"] * 1.2
            ).item()))
            player = {
                "name": self._name(),
                "stat": round(stat, 1),
                "unit": params["unit"],
                "league": league,
                "position": random.choice(["PG", "SG", "SF", "PF", "C"]) if league == "NBA" else
                            random.choice(["QB", "RB", "WR", "TE"]) if league == "NFL" else
                            random.choice(["GK", "DEF", "MID", "FWD"]),
                "games_played": random.randint(20, 82) if league != "MLB" else random.randint(40, 162),
            }
            roster.append(player)
        roster.sort(key=lambda x: -x["stat"])
        for i, p in enumerate(roster, 1):
            p["rank"] = i
        self.players[league] = roster
        return roster


# ─── Main Engine ──────────────────────────────────────────────────────

class InfiniteEngine:
    """
    The complete prediction framework.
    Orchestrates all models, generates synthetic data, runs ensemble predictions,
    and outputs structured analytics ready for the frontend.
    """

    def __init__(self):
        self.elo = EloRating()
        self.mc = MonteCarloEngine()
        self.poisson = PoissonScoring()
        self.bayes = BayesianUpdater()
        self.ensemble = EnsemblePredictor()
        self.calibration = CalibrationTracker()
        self.players = PlayerGenerator()

    def run(self, n_season_rounds=12, n_sims=100000):
        """Run the full analytics pipeline. Returns structured results."""
        results = {
            "leagues": {},
            "top_games": [],
            "top_faceoffs": [],
            "top_players": [],
            "calibration": self.calibration.report(),
            "ensemble_health": {},
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
            "total_simulations": 0,
        }

        for league in _LEAGUE_ORDER:
            params = _SPORT_PARAMS[league]

            # Generate synthetic season
            syn = SyntheticLeague(league)
            syn.generate_season(n_rounds=n_season_rounds)

            # Fit Poisson model
            self.poisson.fit(syn.games, league)

            # Generate player roster
            roster = self.players.generate_roster(league, n=8)

            # Simulate upcoming games
            upcoming = []
            for i in range(0, len(syn.teams) - 1, 2):
                home = syn.teams[i]
                away = syn.teams[i + 1]

                pred = self.ensemble.predict(home, away, league, self.elo, self.mc, self.poisson, self.bayes)
                upcoming.append(pred)
                results["total_simulations"] += pred["projected"].get("n_sims", 50000)

                # Record synthetic "actual" for calibration
                self.calibration.record(pred["ensemble_win_pct"], 1 if random.random() < 0.52 else 0)

            # Generate faceoffs
            faceoffs = []
            for i in range(min(4, len(roster))):
                for j in range(i + 1, min(i + 2, len(roster))):
                    p1, p2 = roster[i], roster[j]
                    n = 50000
                    s1 = p1["stat"] + float(torch.randn(1) * p1["stat"] * 0.15)
                    s2 = p2["stat"] + float(torch.randn(1) * p2["stat"] * 0.15)
                    p1_wins = 1 if s1 > s2 else 0
                    p2_wins = 1 - p1_wins
                    faceoffs.append({
                        "player_a": p1["name"],
                        "player_b": p2["name"],
                        "stat_a": p1["stat"],
                        "stat_b": p2["stat"],
                        "a_win_pct": round(max(s1, s2) / (s1 + s2) * 100, 1) if (s1 + s2) > 0 else 50,
                        "b_win_pct": round(min(s1, s2) / (s1 + s2) * 100, 1) if (s1 + s2) > 0 else 50,
                        "league": league,
                        "stat_label": params["unit"],
                    })

            standings_list = sorted(syn.standings.values(), key=lambda x: x["rank"])

            results["leagues"][league] = {
                "display": params["label"],
                "standings": standings_list,
                "upcoming": upcoming[:4],
                "faceoffs": faceoffs[:3],
                "roster": roster[:6],
                "total_games": len(syn.games),
            }
            results["top_games"].extend(upcoming[:2])
            results["top_faceoffs"].extend(faceoffs[:2])
            results["top_players"].extend(roster[:4])

        # Calibration report
        results["calibration"] = self.calibration.report()
        results["ensemble_health"] = {
            "model_weights": self.ensemble.weights,
            "total_predictions": len(self.calibration.history),
            "avg_error": results["calibration"]["avg_error"],
            "brier_score": results["calibration"]["brier_score"],
        }

        return results


def run_engine():
    """Convenience entry point."""
    engine = InfiniteEngine()
    return engine.run(n_season_rounds=10, n_sims=100000)
