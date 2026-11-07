# P2 labs

Offline synthetic labs for Phase P2. Learning only — not investment advice.

```bash
# from repo root
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python examples/p2/01_data_cleaning.py
python examples/p2/02_backtest_traps.py
python examples/p2/03_costs_in_backtest.py
python examples/p2/04_engines_vectorized_event.py
python examples/p2/05_data_versions_calendar.py   # FIZ/CIZ conventions, split adjust, trading calendars (synthetic)
```

Charts land in `public/p2/` (`cost_ladder.png`, `dsr_vs_N.png`, `cost_breakdown.png`, `capacity_sensitivity.png`).
