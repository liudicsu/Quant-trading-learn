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
```

Each script has a matching `.out` with its expected stdout; capture **stdout only** when refreshing them.
`04_market_regimes_crisis.py` uses offline synthetic data only (seed=11).
