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

- enrich8 (2026-11-10): `09_filing_dates_toy.py` — 10-K/10-Q statutory deadlines by filer type, EDGAR 5:30 p.m. ET deemed-filing rule, 13F 45 days, period-end trap; weekends only, no holidays (9 assertions). `10_delist_index_pit_toy.py` — delisting return vs last three months, CIZ flags G/M must be handled explicitly, survivor-mean bias, ticker reuse vs PERMNO, Russell December 2026 announcement/effective dates (7 assertions; section D used by `backtest-traps`).

- enrich9 (2026-11-10): `11_spinoff_insider_lag_toy.py` — spin-off fake crash (raw −19% vs holder +1%), value-based back-adjustment, volume not adjusted, DisPERMNO link, Form 8937 timing; Form 4 / 13D / 13G deadlines (weekends only, no holidays), acceptance-time usability, FPI insiders from 2026-03-18 (15 assertions). `12_event_time_ipo_toy.py` — FOMC 14:00 EDT statement vs the open, Beijing time, three-week minutes rule (Oct minutes date projected), IPO offering price vs first open, short-history no-signal, lock-up date as an example only (14 assertions).

- enrich11 (2026-11-11): `13_regulatory_fees_toy.py` — SEC Section 31 fee and FINRA TAF looked up by trade date (sells only; $0.00 SEC period, 2026 Q4 TAF pause, TAF cap), 0.206 bps (8 assertions). `14_bid_price_rule_toy.py` — Nasdaq $1 bid-price counts (30 business days), prior-year reverse split, $0.10 rule, 10-day regain, reverse-split fake jump, stayed $5M MVLS rule as status data (8 assertions).
