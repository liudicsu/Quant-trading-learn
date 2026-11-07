# P3 labs

Offline synthetic labs for Phase P3 (classic strategy families). Learning only — not investment advice.

Reuse P2 cost conventions (10 bps one-way stack + √impact × turnover where noted).

```bash
# from repo root
source .venv/bin/activate  # or: python3 -m venv .venv && pip install -r requirements.txt
cd examples/p3
python 01_momentum_trend.py
python 02_mean_reversion.py
python 03_pairs_stat_arb.py
python 04_strategy_compare_lab.py
python 05_kalman_hedge.py          # optional: Kalman hedge ratio, filter vs smoother leak (synthetic)
```

Charts land in `public/p3/`.
