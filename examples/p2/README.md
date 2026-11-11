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

- enrich13 (2026-11-11): `13_regulatory_fees_toy.py` section D — CAT fees billed to both executing brokers per executed share by trade date (2025-1 / 2025-2 / none invoiced 2025-12..2026-04 / 2026-1), and the 2027 SEC row flagged as an FY2026-rate placeholder (14 assertions). `15_nyse_price_criteria_toy.py` — NYSE 30-trading-day average vs Nasdaq consecutive count, month-end cure test, 200:1 reverse-split limit, $0.25 floor from 2027-07-01 (11 assertions). `16_index_add_earnings_time_toy.py` — S&P 500 addition screen with dated cap thresholds, evaluation/announcement/effective timeline, earnings release time → day 0 (13 assertions). `17_xbrl_pit_10b51_toy.py` — SEC XBRL records chosen by `filed` (real Apple FY2009 values copied from data.sec.gov; no network), Rule 10b5-1 cooling-off and the Form 4 plan check box from 2023-04-01 (10 assertions).

- enrich14 (2026-11-11): `18_buyback_10b18_disclosure_toy.py` — Rule 10b-18 25% ADTV cap and weekly block exception, 10- vs 30-minute close windows, Item 703 known only after the 10-Q is filed (9 assertions).

- enrich15 (2026-11-11): `19_rule144_followon_tender_toy.py` — Rule 144 affiliate three-month volume cap and Form 144 notice threshold, Rule 105 five-business-day restricted window, Rule 14e-1 20- and 10-business-day tender windows (weekday-only toy; 15 assertions).

- enrich18 (2026-11-12): `18_buyback_10b18_disclosure_toy.py` section E — Rule 10b-18 after-hours prong (opening-print ban; price cap = lower of the primary close and any later lower bid or sale; volume still counts; no official 23/5 mapping) (now 11 assertions; sections A–D output unchanged). `19_rule144_followon_tender_toy.py` section E — Regulation M Rule 101/102 1-day vs 5-day restricted period, full trading day if pricing is before the close, each shelf takedown analyzed separately, 101 actively-traded exception not copied onto the issuer (sections A–D still print 15/15; script total 19 assertions).
