#!/usr/bin/env python3
"""
Infinite Engine Pipeline:
1. Run PyTorch Monte Carlo simulations across NBA/NFL/EPL/MLB
2. Generate synthetic seasons with Elo ratings, standings, player stats
3. Ensemble predictions (Elo + Poisson + MC + Bayesian)
4. Self-calibration tracking
5. Generate analytics dashboard

Runs 24/7 via GitHub Actions cron.
"""

import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

from src.engine import InfiniteEngine


def main():
    print("=" * 60)
    print("  INFINITE ENGINE — Unprecedented Sports Prediction Framework")
    print("  PyTorch Multi-Model Ensemble | Elo | Monte Carlo | Poisson | Bayesian")
    print("=" * 60)

    os.makedirs(os.path.join(HERE, "output"), exist_ok=True)
    os.makedirs(os.path.join(HERE, "data"), exist_ok=True)

    print("\n[1/2] Running Infinite Engine simulations...")
    engine = InfiniteEngine()
    results = engine.run(n_season_rounds=10, n_sims=100000)

    total_sims = results.get('total_simulations', 0)
    total_preds = len(engine.calibration.history)
    n_leagues = len(results.get('leagues', {}))

    print(f"  {n_leagues} leagues simulated")
    print(f"  {total_sims:,} Monte Carlo trials")
    print(f"  {total_preds} ensemble predictions")
    print(f"  Brier score: {results['calibration']['brier_score']}")
    print(f"  Avg prediction error: {results['calibration']['avg_error']}")

    print("\n[2/2] Generating analytics dashboard...")
    from src.generator import generate_dashboard
    out_path = generate_dashboard(results, engine)

    print(f"\n  Dashboard generated: {out_path}")

    # Print top predictions
    print("\n  Top Predictions:")
    for league, data in results['leagues'].items():
        for g in data['upcoming'][:2]:
            print(f"    {g['home']} vs {g['away']}: {g['ensemble_win_pct']}% (conf: {g['confidence']}%)")

    print("\n" + "=" * 60)
    print("  Engine running. Predictions online.")
    print("=" * 60)


if __name__ == "__main__":
    main()
