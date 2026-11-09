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

- US-first pack (2026-11-08): `06_us_short_constraints.py — Reg SHO layers, locate/borrow fee/dividend owed on a synthetic pair.`

- enrich7 (2026-11-10): `07_short_data_pit.py` — FINRA short interest by publish date (real 2026 calendar), short volume vs short interest (FINRA 10.7% example), FTD as a balance, SR-FINRA-2026-012 withdrawn (8 assertions).
