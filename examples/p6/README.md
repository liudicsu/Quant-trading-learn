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
- enrich17 (2026-11-12): `15_soq_occ_adj_toy.py` — AM vs PM last-trading-day clock (GTH change still Effective TBD), SOQ / SET ≠ prior close / official index open / later spot, and OCC IM 54262 cash-dividend examples ($0.10 / 100-share and 150-share; $0.15 / 50-share) (8 assertions).
- enrich17 (2026-11-12): `11_margin_call_toy.py` new section E — Reg T 150% short initial (100% convertible exception) and FINRA 4210(c)(2)–(3) maintenance at $50 / $4 / $2 / $10 (4 more assertions; sections A–D output unchanged).

- enrich20 (2026-11-12): `06_luld_halt_toy.py` section 4 — LULD Plan Section VII reopen clocks (five-minute attempt; pause ends at a Reopening Price; ten-minute all-centers branch; last ten minutes of Regular Trading Hours go to a closing transaction, not a mid-session reopen) (earlier printed output unchanged, including 7/7 boundary tests; section 4/4).

- enrich21 (2026-11-12): `15_soq_occ_adj_toy.py` new section D — Cboe Rule 5.1(e)(3) early-close Curb for Curb-eligible options starts at the end of shortened Regular Trading Hours and lasts 15 minutes (official example 1:00 p.m. to 1:15 p.m.); not the stock 12:50 p.m. ET MOC cutoff; AM-settled last-trading-day change remains Effective TBD (sections A–C still print as before, including 8/8; script total 9 assertions).
- enrich22 (2026-11-12): `06_luld_halt_toy.py` new section 5 — official Nasdaq halt codes T1 / H10 / LUDP / LUDS / MWC1–3 as a map onto already-taught halt types; the official table’s T5 “10% in five minutes” sentence is not current LULD (sections 1–4 still print as before, including 7/7 boundary tests and section 4/4; section 5 6/6).
- enrich25 (2026-11-12): `12_rule606_toy.py` new sections B–C — FINRA 5250 payments for market making (issuer / affiliate / promoter payment for quoting or market making prohibited; official (b) bona fide-services / registration-and-listing-fee / exchange-rule exceptions named only; not already-taught PFOF / 606) and FINRA 5270 front running of block transactions (different from already-taught 5320; an equity block is generally 10,000 shares or more, but fewer can be a block; public availability only after the entire block is completed and publicly reported; official SM .04 exceptions named only) (the current 606 table, 4/4, `ASSERT_rule606_ok`, and the reminder line still print as before; section B prints 8/8; script total 12 assertions).
- enrich26 (2026-11-12): `12_rule606_toy.py` new sections D–E — FINRA 5230 payments involving publications that influence the market price (a member may not give anything of value to influence or reward such a publication; official (b) paid-advertising / Securities Act 17(b) disclosure / Rule 2241 research-report exceptions named only; not already-taught 5250 or PFOF / 606) and FINRA 5280 trading ahead of research reports (a different prohibition from already-taught 5270 and 5320; a member may not change an inventory position in a security or a derivative of that security based on non-public advance knowledge of the content or timing of a research report; official 5280(b) information-flow procedures named only) (the current 606 table, 4/4, `ASSERT_rule606_ok`, the reminder line, the 5250 section, the 5270 section, and 12/12 after 5270 still print as before; section D prints 15/15; script total 18 assertions).
