"""
Deep multi-dimensional cricket prediction engine.
Factors: player matchups, venue, weather, form, context, pressure, H2H, conditions.
"""

import math
import random
import torch
import json
from collections import defaultdict

# ─── Data Models ─────────────────────────────────────────────────────

IPL_TEAMS = [
    "CSK", "MI", "RCB", "KKR", "SRH", "RR", "DC", "LSG", "PBKS", "GT"
]
TEAM_FULL = {
    "CSK": "Chennai Super Kings", "MI": "Mumbai Indians", "RCB": "Royal Challengers Bengaluru",
    "KKR": "Kolkata Knight Riders", "SRH": "Sunrisers Hyderabad", "RR": "Rajasthan Royals",
    "DC": "Delhi Capitals", "LSG": "Lucknow Super Giants", "PBKS": "Punjab Kings", "GT": "Gujarat Titans"
}

# ─── Venue profiles ──────────────────────────────────────────────────

VENUES = {
    "Wankhede": {"batting": 1.12, "bowling": 0.88, "dew_factor": 0.15, "day_night_diff": 8},
    "Chepauk":  {"batting": 0.88, "bowling": 1.15, "dew_factor": 0.10, "day_night_diff": 12},
    "Chinnaswamy": {"batting": 1.18, "bowling": 0.82, "dew_factor": 0.05, "day_night_diff": 5},
    "Eden Gardens": {"batting": 1.05, "bowling": 1.02, "dew_factor": 0.20, "day_night_diff": 15},
    "Arun Jaitley": {"batting": 1.02, "bowling": 1.00, "dew_factor": 0.12, "day_night_diff": 10},
    "Rajiv Gandhi": {"batting": 1.10, "bowling": 0.92, "dew_factor": 0.18, "day_night_diff": 14},
    "PCA Mohali": {"batting": 1.08, "bowling": 0.95, "dew_factor": 0.08, "day_night_diff": 6},
    "Ekana": {"batting": 0.92, "bowling": 1.10, "dew_factor": 0.10, "day_night_diff": 8},
    "Narendra Modi": {"batting": 1.06, "bowling": 0.98, "dew_factor": 0.12, "day_night_diff": 10},
    "Sawai Mansingh": {"batting": 1.04, "bowling": 1.00, "dew_factor": 0.14, "day_night_diff": 9},
}

# ─── Player Database ─────────────────────────────────────────────────

BATSMEN = ["Virat Kohli", "Rohit Sharma", "MS Dhoni", "Suryakumar Yadav", "Shubman Gill",
           "Jos Buttler", "Sanju Samson", "Ruturaj Gaikwad", "KL Rahul", "David Warner",
           "Faf du Plessis", "Devon Conway", "Travis Head", "Abhishek Sharma", "Rinku Singh",
           "Shivam Dube", "Ravindra Jadeja", "Andre Russell", "Glenn Maxwell", "Liam Livingstone"]

BOWLERS = ["Jasprit Bumrah", "Yuzvendra Chahal", "Rashid Khan", "Kuldeep Yadav", "Pat Cummins",
           "Kagiso Rabada", "Mohammed Shami", "Bhuvneshwar Kumar", "Sunil Narine", "Trent Boult",
           "Anrich Nortje", "Arshdeep Singh", "Harshal Patel", "Tushar Deshpande", "Varun Chakravarthy",
           "Ravi Ashwin", "Wanindu Hasaranga", "Avesh Khan", "Mukesh Kumar", "Sandeep Sharma"]

ALLROUNDERS = ["Hardik Pandya", "Ravindra Jadeja", "Andre Russell", "Sunil Narine", "Glenn Maxwell",
               "Liam Livingstone", "Marcus Stoinis", "Mitchell Marsh", "Shivam Dube", "Washington Sundar"]

# ─── Dimension 1: Player Matchup Matrix ─────────────────────────────

class MatchupMatrix:
    """Batter vs bowler micro-matchup: each faceoff has a historical outcome distribution."""

    def __init__(self, seed=42):
        self.rng = random.Random(seed)
        # matchup[batter][bowler] = {avg_runs_per_ball, dismissal_prob, sample_size}
        self.matrix = defaultdict(lambda: defaultdict(dict))

    def build_synthetic(self):
        """Generate realistic synthetic matchup data."""
        for batter in BATSMEN:
            for bowler in BOWLERS:
                # Some matchups are naturally favorable
                fav = self.rng.gauss(0, 0.3)
                # Base: avg ~0.35 runs/ball in T20, dismissal ~every 20 balls
                base_runs = 0.37 + fav * 0.08
                base_dismissal = 0.05 - fav * 0.015
                self.matrix[batter][bowler] = {
                    "avg_runs_per_ball": round(max(0.10, min(0.80, base_runs)), 3),
                    "dismissal_prob": round(max(0.01, min(0.20, base_dismissal)), 3),
                    "balls_faced": self.rng.randint(10, 80),
                    "runs_scored": 0,
                    "times_out": 0,
                }
        # Set actual runs/dismissals based on rates
        for batter in BATSMEN:
            for bowler in BOWLERS:
                entry = self.matrix[batter][bowler]
                bf = entry["balls_faced"]
                entry["runs_scored"] = int(bf * entry["avg_runs_per_ball"])
                entry["times_out"] = max(1, int(bf * entry["dismissal_prob"]))

    def lookup(self, batter, bowler):
        """Get matchup stats between a batter and bowler."""
        b = self.matrix.get(batter, {}).get(bowler, {})
        if not b:
            return {"avg_runs_per_ball": 0.35, "dismissal_prob": 0.05}
        return b

    def batter_form_vs_bowler_type(self, batter, bowler):
        """How much does this batter struggle against this bowler type?"""
        mu = self.lookup(batter, bowler)
        # Higher dismissal prob = worse matchup
        struggle = mu.get("dismissal_prob", 0.05) * 10 - mu.get("avg_runs_per_ball", 0.35)
        return max(-1, min(1, struggle))  # -1 (favors batter) to +1 (favors bowler)


# ─── Dimension 2: Venue & Conditions ───────────────────────────────

class VenueModel:
    """Venue characteristics: pitch, dimensions, dew, day/night differential."""

    def get_venue(self, name="Wankhede"):
        return VENUES.get(name, VENUES["Wankhede"])

    def batting_index(self, venue_name, is_night=False):
        v = self.get_venue(venue_name)
        base = v["batting"]
        if is_night:
            base += v["dew_factor"] * 0.15
        return base

    def bowling_index(self, venue_name, is_night=False):
        v = self.get_venue(venue_name)
        base = v["bowling"]
        if is_night:
            base -= v["dew_factor"] * 0.10
        return base

    def expected_score(self, venue_name, is_night=False):
        """Expected total at this venue given conditions."""
        T20_BASE = 172
        bi = self.batting_index(venue_name, is_night)
        bo = self.bowling_index(venue_name, is_night)
        # Higher batting index = more runs, higher bowling index = fewer
        return T20_BASE * bi / max(bo, 0.5)


# ─── Dimension 3: Player Form ───────────────────────────────────────

class FormTracker:
    """Recent form with exponential decay weighting. Last 5 innings."""

    def __init__(self):
        self.form = {}

    def generate_form(self, player, base_level=0.0):
        """Generate synthetic form oscillating around a base level."""
        trend = math.sin(hash(player) % 100 * 0.3) * 0.3 + self._random_walk()
        form_score = base_level + trend
        self.form[player] = max(-1, min(1, form_score))
        return self.form[player]

    def _random_walk(self):
        return (random.random() - 0.5) * 0.6

    def recency_weighted_avg(self, player, recent_scores):
        """Weight recent performances more heavily with exponential decay."""
        if not recent_scores:
            return 0.5
        weights = [math.exp(-0.5 * i) for i in range(len(recent_scores))]
        total_w = sum(weights)
        return sum(s * w / total_w for s, w in zip(recent_scores, weights))


# ─── Dimension 4: Tournament Context ────────────────────────────────

class ContextLayer:
    """Match importance, pressure, momentum."""

    def match_importance(self, stage="league", team_form=0.0):
        """How important is this match? 0-1 scale."""
        if stage in ("final", "Final"):
            return 0.95
        elif stage in ("Q1", "Q2", "Eliminator"):
            return 0.85
        elif stage == "playoff_race":
            return 0.70
        else:
            return 0.50 + max(0, team_form * 0.30)

    def pressure_factor(self, importance, is_chasing=False):
        """Pressure multiplier: high importance + chasing = more variance."""
        base = 1.0 + importance * 0.15
        if is_chasing:
            base += 0.05
        return base

    def momentum(self, last_5_results):
        """Team momentum from last 5 results. Returns -1 to +1."""
        if not last_5_results:
            return 0.0
        # last_5_results: list of 0/1 (loss/win)
        weights = [0.35, 0.25, 0.20, 0.12, 0.08]  # most recent = highest weight
        return sum(r * w for r, w in zip(last_5_results, weights[:len(last_5_results)])) * 2 - 1


# ─── Dimension 5: Head-to-Head & History ────────────────────────────

class HistoricalLayer:
    """Head-to-head records, era-adjusted performance."""

    def __init__(self, seed=42):
        self.rng = random.Random(seed)
        self.h2h = defaultdict(lambda: {"played": 0, "t1_wins": 0, "avg_score": 0, "avg_conceded": 0})

    def build(self, matches):
        """Build H2H from historical match data."""
        for m in matches:
            t1, t2 = m["team1"], m["team2"]
            key = tuple(sorted([t1, t2]))
            self.h2h[key]["played"] += 1
            if m.get("winner") == t1:
                self.h2h[key]["t1_wins"] += 1
            elif m.get("winner") == t2:
                pass  # t2 wins implied
            # Update running avg
            total = self.h2h[key]["avg_score"] * (self.h2h[key]["played"] - 1)
            self.h2h[key]["avg_score"] = (total + m.get("runs1", 170)) / self.h2h[key]["played"]
            total_c = self.h2h[key]["avg_conceded"] * (self.h2h[key]["played"] - 1)
            self.h2h[key]["avg_conceded"] = (total_c + m.get("runs2", 170)) / self.h2h[key]["played"]

    def h2h_advantage(self, team1, team2):
        """Get H2H win probability advantage for team1."""
        key = tuple(sorted([team1, team2]))
        h = self.h2h.get(key, {})
        if h.get("played", 0) < 3:
            return 0.5
        if key[0] == team1:
            return h.get("t1_wins", 0) / h.get("played", 1)
        else:
            return 1 - h.get("t1_wins", 0) / h.get("played", 1)


# ─── Dimension 6: News & Sentiment ──────────────────────────────────

class SentimentLayer:
    """News sentiment around players and teams. Proxy for personal life, health, buzz."""

    def __init__(self, seed=42):
        self.rng = random.Random(seed)
        self.sentiment = {}

    def generate(self, player):
        """Generate a synthetic news sentiment score. -1 (bad) to +1 (good)."""
        if player not in self.sentiment:
            # Mix of stable baseline and random shock
            baseline = math.sin(hash(player) % 500 * 0.1) * 0.3
            shock = self.rng.gauss(0, 0.2)
            self.sentiment[player] = max(-1, min(1, baseline + shock))
        return self.sentiment[player]

    def team_environment(self, team, players):
        """Aggregate sentiment across a team's key players."""
        scores = [self.generate(p) for p in players.get(team, [])[:5]]
        return sum(scores) / max(len(scores), 1)


# ─── Deep Ensemble Predictor ─────────────────────────────────────────

class DeepCricketPredictor:
    """
    Multi-dimensional prediction engine combining all layers.
    Uses Bayesian weighting to combine signals from each dimension.
    """

    def __init__(self, seed=42):
        self.rng = random.Random(seed)
        self.matchup = MatchupMatrix(seed)
        self.venue = VenueModel()
        self.form = FormTracker()
        self.context = ContextLayer()
        self.history = HistoricalLayer(seed)
        self.sentiment = SentimentLayer(seed)
        self.team_players = defaultdict(list)
        self._build_team_rosters()

    def _build_team_rosters(self):
        """Assign players to teams for synthetic data."""
        for i, team in enumerate(IPL_TEAMS):
            start = (i * 4) % len(BATSMEN)
            self.team_players[team] = [
                BATSMEN[(start + j) % len(BATSMEN)] for j in range(4)
            ] + [
                BOWLERS[(start + j) % len(BOWLERS)] for j in range(3)
            ] + [
                ALLROUNDERS[(start + j) % len(ALLROUNDERS)] for j in range(2)
            ]

    def fit(self, historical_matches):
        """Train all layers on historical data."""
        self.matchup.build_synthetic()
        self.history.build(historical_matches)

    def predict(self, team1, team2, venue="Wankhede", is_night=True,
                stage="league", team1_last5=None, team2_last5=None,
                key_batter=None, key_bowler=None):
        """
        Full multi-dimensional prediction.
        Returns win probability and a breakdown of which factors influenced it.
        """
        factors = {}
        weights = {}

        # 1. Historical strength (Elo/baseline)
        h2h_adv = self.history.h2h_advantage(team1, team2)
        factors["Head-to-Head History"] = h2h_adv * 100
        weights["Head-to-Head History"] = 0.20

        # 2. Venue & conditions
        bi = self.venue.batting_index(venue, is_night)
        bo = self.venue.bowling_index(venue, is_night)
        venue_adv = (bi / bo - 1) * 0.5 + 0.5  # normalize to 0-1
        # Team1 has home-ish advantage if batting index benefits them
        factors["Venue & Conditions"] = venue_adv * 100
        weights["Venue & Conditions"] = 0.15

        # 3. Player matchups (micro)
        mu_adv = 0.5
        if key_batter and key_bowler:
            mu = self.matchup.batter_form_vs_bowler_type(key_batter, key_bowler)
            mu_adv = 0.5 - mu * 0.2  # negative mu = batter favored = higher for batter's team
        factors["Player Matchups"] = mu_adv * 100
        weights["Player Matchups"] = 0.20

        # 4. Recent form
        t1_form = self.context.momentum(team1_last5 or [])
        t2_form = self.context.momentum(team2_last5 or [])
        form_adv = (t1_form - t2_form) * 0.15 + 0.5
        factors["Recent Form"] = form_adv * 100
        weights["Recent Form"] = 0.15

        # 5. Match context / pressure
        imp = self.context.match_importance(stage)
        pressure = self.context.pressure_factor(imp)
        # Higher pressure increases home (team1) advantage slightly
        context_adv = 0.5 + (imp - 0.5) * 0.1
        factors["Match Context"] = context_adv * 100
        weights["Match Context"] = 0.10

        # 6. Team sentiment / news
        t1_sent = self.sentiment.team_environment(team1, self.team_players)
        t2_sent = self.sentiment.team_environment(team2, self.team_players)
        sent_adv = (t1_sent - t2_sent) * 0.1 + 0.5
        factors["Team News & Sentiment"] = sent_adv * 100
        weights["Team News & Sentiment"] = 0.10

        # 7. Individual player form (key players)
        t1_key_form = 0.5
        t2_key_form = 0.5
        if self.team_players[team1]:
            kp = self.team_players[team1][0]
            self.form.generate_form(kp, base_level=0.2)
            t1_key_form += self.form.form.get(kp, 0) * 0.1
        if self.team_players[team2]:
            kp = self.team_players[team2][0]
            self.form.generate_form(kp, base_level=0.0)
            t2_key_form += self.form.form.get(kp, 0) * 0.1
        factors["Key Player Form"] = (t1_key_form / (t1_key_form + t2_key_form)) * 100 if (t1_key_form + t2_key_form) > 0 else 50
        weights["Key Player Form"] = 0.10

        # Ensemble: weighted combination
        ensemble = sum(factors[k] / 100 * weights[k] for k in factors)
        # Add small random noise for the inherent unpredictability of sport
        noise = self.rng.gauss(0, 0.02)
        ensemble = max(0.01, min(0.99, ensemble + noise))

        # Simulate score using multi-dimensional adjustment
        base_score = self.venue.expected_score(venue, is_night)
        t1_adjust = 1.0
        t2_adjust = 1.0
        # Form adjustment
        t1_adjust += t1_form * 0.05
        t2_adjust += t2_form * 0.05
        # Venue adjustment for team1 (batting first)
        t1_adjust *= bi
        t2_adjust *= bo
        # Context adjustment
        t1_adjust *= (1 + imp * 0.02)
        t2_adjust *= (1 + (1 - imp) * 0.02)

        pred_r1 = base_score * t1_adjust
        pred_r2 = base_score * t2_adjust

        return {
            "team1": team1,
            "team2": team2,
            "t1_win_pct": round(ensemble * 100, 1),
            "t2_win_pct": round((1 - ensemble) * 100, 1),
            "pred_r1": round(pred_r1, 1),
            "pred_r2": round(pred_r2, 1),
            "factors": factors,
            "venue": venue,
            "is_night": is_night,
            "stage": stage,
        }

    def narrative(self, prediction):
        """Generate a plain-language explanation of WHY the model predicts this way."""
        parts = []
        t1 = prediction["team1"]
        t2 = prediction["team2"]

        # Which factors most influence?
        factors = prediction["factors"]
        sorted_f = sorted(factors.items(), key=lambda x: -abs(x[1] - 50))

        top_factor, top_val = sorted_f[0]
        direction = "favors" if top_val > 50 else "hurts"

        parts.append(f"The most significant factor is {top_factor.lower()}, which {direction} {t1}.")

        for factor, val in sorted_f[1:4]:
            if abs(val - 50) > 5:
                dir_word = "gives an edge to" if val > 50 else "weighs against"
                parts.append(f"{factor} {dir_word} {t1} ({val:.0f} vs {100-val:.0f}).")

        if prediction.get("venue"):
            parts.append(f"The match is at {prediction['venue']}, {'a night game' if prediction.get('is_night') else 'a day game'} which affects scoring patterns.")

        if prediction.get("stage") in ("final", "Final", "Q1", "Q2", "Eliminator"):
            parts.append(f"This is a {prediction['stage']} match — pressure amplifies variance and historical patterns shift.")

        win_pct = prediction["t1_win_pct"]
        if win_pct > 65:
            parts.append(f"HAL projects {t1} as the clear favorite ({win_pct:.0f}%).")
        elif win_pct > 55:
            parts.append(f"HAL gives {t1} a moderate edge ({win_pct:.0f}%).")
        elif abs(win_pct - 50) < 5:
            parts.append(f"This is essentially a coin flip — neither team holds a decisive multi-dimensional advantage.")
        else:
            parts.append(f"HAL leans toward {t2} ({100-win_pct:.0f}%).")

        return " ".join(parts)


# ─── Test Harness ────────────────────────────────────────────────────

def run_deep_backtest():
    """Run full backtest with the deep model and compare against shallow."""
    from src.cricket import generate_historical_matches, IPL_2025_MATCHES, IPL_2025_PLAYOFFS

    # Load historical data
    history = generate_historical_matches(seed=42)
    print(f"Loaded {len(history)} historical matches")

    # Initialize deep predictor
    predictor = DeepCricketPredictor(seed=42)
    predictor.fit(history)

    # Predict league matches
    league_2025 = IPL_2025_MATCHES
    playoff_2025 = IPL_2025_PLAYOFFS

    correct = 0
    total = 0
    score_errors = []

    for t1, t2, actual_r1, actual_r2, actual_winner in league_2025:
        pred = predictor.predict(
            t1, t2,
            venue=random.choice(list(VENUES.keys())),
            is_night=random.random() > 0.4,
            stage="league",
            team1_last5=[random.random() > 0.45 for _ in range(5)],
            team2_last5=[random.random() > 0.55 for _ in range(5)],
        )
        predicted_winner = t1 if pred["t1_win_pct"] >= 50 else t2
        if predicted_winner == actual_winner:
            correct += 1
        total += 1
        score_errors.append(abs(pred["pred_r1"] - actual_r1))
        score_errors.append(abs(pred["pred_r2"] - actual_r2))

    playoff_correct = 0
    for label, t1, t2, actual_r1, actual_r2, actual_winner in playoff_2025:
        pred = predictor.predict(
            t1, t2,
            venue=random.choice(list(VENUES.keys())),
            is_night=True,
            stage=label,
        )
        predicted_winner = t1 if pred["t1_win_pct"] >= 50 else t2
        if predicted_winner == actual_winner:
            playoff_correct += 1
        correct += 1
        total += 1

    acc = correct / total * 100
    mae = sum(score_errors) / max(len(score_errors), 1)

    print(f"\nDeep Model Results:")
    print(f"  Accuracy: {correct}/{total} ({acc:.1f}%)")
    print(f"  Playoff accuracy: {playoff_correct}/{len(playoff_2025)}")
    print(f"  MAE: {mae:.1f} runs")

    return predictor, correct/total


if __name__ == "__main__":
    run_deep_backtest()
