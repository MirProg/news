#!/usr/bin/env python3
"""
World Sports Pipeline:
1. Build 7-dimensional deep prediction models for all popular sports
2. Generate editorial news takes for each sport
3. Backtest accuracy across all sports
4. Publish news site with HAL's analysis
"""

import os, sys, random
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

from src.world_sports import WorldSportsEngine, SPORTS


def main():
    print("=" * 64)
    print("  HAL 9000 — World Sports Intelligence Engine")
    print("  7-Dimensional Deep Prediction | {} Sports".format(len(SPORTS)))
    print("=" * 64)

    os.makedirs(os.path.join(HERE, "output"), exist_ok=True)

    print("\n[1/3] Building deep prediction models...")
    engine = WorldSportsEngine()
    engine.build_all(seed=42)

    print("\n[2/3] Running backtest validation...")
    bts = engine.run_backtest_all()
    for key in sorted(bts.keys(), key=lambda k: -bts[k]['accuracy']):
        bt = bts[key]
        print(f"  {SPORTS[key]['name']:<28} {bt['accuracy']:>5.1f}%  Brier:{bt.get('brier', '?'):<6}  Pred:{bt.get('predictability', '?'):>4}%  ECE:{bt.get('ece', '?')}")

    print("\n[3/3] Generating news site...")
    takes = engine.generate_all_takes()

    from src.generator import generate_world_news
    out_path = generate_world_news(engine, takes, bts)

    print(f"\n  Published: {out_path}")
    print(f"  {len(takes)} editorial takes across {len(engine.predictors)} sports")
    print("\n" + "=" * 64)
    print("  HAL 9000 — Predictions updated. Stories published.")
    print("=" * 64)


if __name__ == "__main__":
    main()
