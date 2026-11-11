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

- enrich7 (2026-11-10): `09_options_basics_toy.py` — 100-share contract unit, expiry P&L with premium, BSM as a reference, put-call parity, early-assignment flag (9 assertions); `10_mwcb_overnight_resume_toy.py` — Level 3 resumes 04:00 ET or later next trading day under 23/5, Sunday overnight still halted (5 assertions).

- enrich8 (2026-11-10): `11_margin_call_toy.py` — Reg T 50% initial margin, FINRA 4210 25% vs 40% house maintenance on the SEC $16,000/$8,000/$12,000 example, margin-call trigger price (6 assertions). `12_rule606_toy.py` — synthetic Rule 606-style routing table, net PFOF in cents per 100 shares (3 assertions).

- enrich9 (2026-11-10): `11_margin_call_toy.py` new section D — portfolio margin toy under FINRA 4210(g): ten equidistant valuation points read as −15%…+15% incl. both ends, stock-only vs stock + 95 put (intrinsic-only), $.375 per-contract floor (4 more assertions; sections A–C output unchanged).

- enrich15 (2026-11-11): `13_exercise_by_exception_toy.py` — OCC $0.01 in-the-money exercise-by-exception at expiration (calls and puts) and the 100-share stock position created by assignment (7 assertions).
- enrich16 (2026-11-12): `14_clearly_erroneous_toy.py` — clearly erroneous reviewability in regular hours vs the numerical-guideline buckets, and the 2026-12-06 overnight extension (11 assertions; FINRA 11892 as of 2026-11-12 is not treated as already amended). `13_exercise_by_exception_toy.py` adds OCC random assignment to clearing members and a FIFO firm-allocation toy (now 9 assertions).
