# P1 labs

Offline synthetic examples for Phase P1. Learning only — not investment advice.

| Script | Artifacts |
| --- | --- |
| `01_markets_language.py` | CSV→NAV, Alpha/Beta toy → `01_*.out` |
| `02_microstructure_orders.py` | mid/bps, fill timing → `02_*.out` |
| `03_returns_vol_corr.py` | Sharpe/MDD + `public/p1/rolling_vol.png`, `rolling_corr_stress.png` |
| `04_eval_lab.py` | net-of-cost table, win-rate trap → `04_*.out` |

Data: `data/synthetic_ohlc_ba.csv` (seed 11 when generated).

- US-first pack (2026-11-08): `05_us_market_mechanics.py — US T+1, NYSE sessions in Shanghai time, toy NBBO (offline).`

- enrich7 (2026-11-10): `06_close_auction_roundlot.py` — official close vs last trade, NYSE MOC 15:50 ET cutoff in Shanghai time, tiered round lots, BOLO vs NBBO (17 assertions).
