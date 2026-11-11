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

- enrich8 (2026-11-10): `07_etf_nav_letf_toy.py` — Rule 6c-11 premium/discount and the >2%-for-more-than-7-days statement trigger, median spread, SEC 1000→900→990 / 2x 800→960 daily-reset example, choppy-path decay for 1x/2x/3x/−2x (7 assertions; used by `markets-language` and `returns-vol-corr`).

- enrich9 (2026-11-10): `08_tbill_rf_toy.py` — TreasuryDirect bill price formula (999.27 example), 4.00%/91-day price and simple 365-day yield, Sharpe at Rf=0 vs 4%/252, prior-day rate as of each return (7 assertions; synthetic rates, no Treasury download).

- enrich11 (2026-11-11): `09_open_auction_toy.py` — NYSE open may print after 09:30 (DMM), Nasdaq MOO 09:28 ET cutoff in Shanghai time, signal-from-open look-ahead (5 assertions).

- enrich14 (2026-11-11): `10_early_close_nasdaq_moc_toy.py` — NYSE early-close MOC freeze at 12:50 ET (2026-11-27 and 2026-12-24; Beijing 01:50 next day) and Nasdaq regular-day close cutoffs (MOC 15:55 / LOC 15:58) (9 assertions).
