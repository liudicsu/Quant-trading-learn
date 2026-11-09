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

- US-first pack (2026-11-08): `06_us_data_sources_pit.py — EDGAR/ALFRED-shaped self-made fixtures (data/us_fixtures), PIT vs naive latest; no real FRED/yfinance downloads (R16). 05 adds section D: ledger vs split-adjusted vs total return, delisting flag.`

- N2 (2026-11-08): `07_rule605_effective_spread.py` — amended Rule 605 (SEC staff FAQ): Example 27-1 effective spread (0.24), Example 38-1 price improvement (0.005699%), toy covered-order filters on a synthetic fixture; signed ES + ratio-of-averages % (R42); NMLO pre-open/halt exceptions incl. first-executable halt test (R43/R47). No 605 field names.

- enrich7 (2026-11-10): `08_dividend_dates_yf_shapes.py` — ex-date = record date under T+1, total vs price-only return, yfinance `auto_adjust` return shapes (11 assertions).
