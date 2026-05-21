#!/usr/bin/env python3
"""
Infinite Engine Pipeline:
1. PyTorch Monte Carlo simulations across NBA/NFL/EPL/MLB
2. Multi-model ensemble predictions (Elo + Poisson + MC + Bayesian)
3. IPL backtest: train on 2008-2024, predict last year's tournament
4. Side-by-side scorecard comparison
5. Analytics dashboard

Runs 24/7 via GitHub Actions cron.
"""

import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

from src.engine import InfiniteEngine
from src.cricket import IPLBacktest


def main():
    print("=" * 60)
    print("  INFINITE ENGINE — Unprecedented Sports Prediction Framework")
    print("  PyTorch | Elo | Monte Carlo | Poisson | Bayesian | IPL Backtest")
    print("=" * 60)

    os.makedirs(os.path.join(HERE, "output"), exist_ok=True)
    os.makedirs(os.path.join(HERE, "data"), exist_ok=True)

    print("\n[1/3] Running Infinite Engine simulations...")
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

    print("\n[2/3] Running IPL backtest...")
    bt = IPLBacktest(seed=42)
    ipl_results = bt.run()
    s = ipl_results['summary']
    print(f"  Trained on {ipl_results['history']['n_matches']} historical matches ({ipl_results['history']['years'][0]}-{ipl_results['history']['years'][-1]})")
    print(f"  Predicted {s['total_matches']} matches: {s['correct_predictions']}/{s['total_matches']} correct ({s['accuracy']}%)")
    print(f"  MAE Score: {s['mean_abs_error_runs']} runs")
    print(f"  Brier Score: {s['brier_score']}")

    print("\n[3/3] Generating analytics dashboard...")
    from src.generator import generate_dashboard
    out_path = generate_dashboard(results, engine, ipl_results, bt)

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
