# P6 labs

Risk & execution: position sizing, execution slippage, risk systems, and market regimes / crisis literacy. All rules are lagged (no look-ahead). Learning only — not investment advice.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cd examples/p6
python 01_portfolio_risk_sizing.py   # Kelly / half-Kelly, vol target, risk parity, Ledoit–Wolf
python 02_execution_slippage.py      # TWAP/VWAP, Almgren–Chriss, implementation shortfall, TCA
python 03_risk_systems_lab.py        # VaR/CVaR, Kupiec/Christoffersen, stress, drawdown rules
python 04_market_regimes_crisis.py   # causal regime detectors, stress toys, HMM filtered vs smoothed
python 05_weight_drift.py            # weight drift & constraint consistency (synthetic)
```

Each script has a matching `.out` with its expected stdout; capture **stdout only** when refreshing them.
`04_market_regimes_crisis.py` uses offline synthetic data only (seed=11).

- US-first pack (2026-11-08): `06_luld_halt_toy.py — LULD tiers (R12) + halt toy (not a rule engine); 07_feed_tca_toy.py — IEX vs SIP arrival, stale NBBO, capacity.`

- N1 (2026-11-08): `08_overnight_bands_toy.py` — LULD overnight price bands Phase 1 (SEC 34-106042 / 34-106624; planned 2026-12-06, dependent on systems changes), 5 synthetic cases; not a rule engine.
