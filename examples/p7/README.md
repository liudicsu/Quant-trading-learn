# P7 labs

Paper trading & compliance: a simulated paper-trading loop and an official-sources checklist. **No real broker order code.** Learning only — not investment or legal advice.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cd examples/p7
python 01_paper_trading_loop.py   # logging, reconciliation, drift, kill switches, live-vs-backtest gap
python 02_compliance_sources.py   # official regulator sources checklist (rules change; verify current text)
```

Each script has a matching `.out` with its expected stdout; capture **stdout only** when refreshing them.

- US-first pack (2026-11-08): `03_paper_adapter_fixture.py — idempotent adapter, reconciliation, NY vs Shanghai dates; 02 is now a local US-first source ledger (n_sources=33, no fetching).`

- R34 (2026-11-08): `04_finra_migration_fixture.py` + `fixtures/finra_26_10_fixture.json` — FINRA 26-10 four dates, member adoption, broker_checked_on, account category; 8 asserted cases (unknown → needs_broker_verification).

- N1 (2026-11-08): `05_overnight_session_fixture.py` + `fixtures/overnight_sessions_fixture.json` — overnight session classification, next-day trade date, Shanghai time, `overnight_tradable` / limit-only / day-gtc checks, weekly closure Fri 20:00–Sun 20:00 ET as a toy rule (real brokers may queue; R44/R46), DST-switch-week Sunday 20:00 boundary tests, assertion count computed by the script (R48) (Alpaca 24/5 doc as example, not a recommendation).

- enrich7 (2026-11-10): `06_wash_sale_basis_toy.py` — IRS Pub 550 three examples incl. more/less shares matched in purchase order, window before and after the sale (5 assertions; taxable account only).

- enrich8 (2026-11-10): `07_holding_period_toy.py` — IRS Topic 409 more-than-one-year test, Pub 550 qualified-dividend 121-day window from the rule text (not the worked-example day counts), Pub 519 183-day note as text only (6 assertions; not tax advice).

- enrich9 (2026-11-10): `08_self_trade_pattern_toy.py` — same-algo self-trade prevention, layering-style pattern flag for human review (not a legal finding), wash sale vs wash trade glossary (5 assertions; synthetic events). `02_compliance_sources.py` gains 15 U.S.C. 78i, FINRA 5210 and SEC 2026-37 (CAT review) rows: n_sources=36.

- enrich10 (2026-11-10): `02_compliance_sources.py` gains the SEC Innovation Exemption order (Release 34-106402) and the Atkins and Uyeda statements (tokenized NMS stock); the 15 U.S.C. 78i row is now compared with the current US Code through PL 119-138: n_sources=39.
