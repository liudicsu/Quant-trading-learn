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

- enrich11 (2026-11-11): `09_tax_lot_toy.py` — IRS Pub 550 FIFO example (basis 1,380), adequate identification with written confirmation (1,230), no average price per share for stock (3 assertions; not tax advice).

- enrich14 (2026-11-11): `10_section16b_toy.py` — Section 16(b) window of less than six months: 2026-01-15 buy / 2026-06-10 sell inside, 2026-07-20 sell outside; sale-then-repurchase also inside (4 assertions; exact-day edge not decided; not legal advice).

- enrich16 (2026-11-12): `11_tax_1259_1256_roc_toy.py` — IRS Pub 550 return-of-capital Example 1 ($100 / $80 / $30 → basis 100→20→0, $10 long-term gain) and a 1259/1256 classification table (3 assertions; not tax advice).
- enrich17 (2026-11-12): `11_tax_1259_1256_roc_toy.py` new section C — payments in lieu are not QDI (Form 1099-MISC) and preferred-stock QDI 90/181 only when periods total more than 366 days (now 4 assertions; sections A–B output unchanged; not tax advice).

- enrich18 (2026-11-12): `12_form13h_toy.py` — Form 13H identifying-activity level (calendar day 2 million shares or $20 million; calendar month 20 million shares or $200 million), no netting, equity-option underlying counts and exercises do not (9 assertions; not a public PIT filing; not tax or registration advice).

- enrich19 (2026-11-12): `11_tax_1259_1256_roc_toy.py` section D — IRS Pub 550 capital-loss cap (Bob and Shelly $7,000 → $3,000 deductible + $4,000 carryover; $2,000 fully deductible; $1,500 if MFS; carryover remains long-term or short-term) (sections A–C output unchanged, including 4/4 after C; script total 7 assertions; not tax advice).

- enrich20 (2026-11-12): `11_tax_1259_1256_roc_toy.py` sections E–F — Pub 550 Ace Corporation 13-month short sale (buy and immediately deliver → short-term, because the delivered holding period is less than 1 day) and worthless securities treated as sold on the last day of the tax year (calendar-year 2026 → 2026-12-31) (sections A–D still print as before, including the capital-loss cap 7/7; script total 9 assertions; general information, not tax advice).

- enrich21 (2026-11-12): `11_tax_1259_1256_roc_toy.py` sections G–H — Pub 550 investment interest (margin interest to buy taxable securities is investment interest, generally limited to net investment income, with carryover; official mixed-use allocation fraction $8,000 / $10,000) and stock-dividend Example 1 (one share at $45, two new shares for each share held → three shares at $15; holding period of nontaxable new stock begins on the same day as the old stock; fractional-share cash is a sale, not a dividend) (sections A–F still print as before, including the capital-loss cap, Ace short-sale, and worthless last-day-of-year prints, 9/9; script total 12 assertions; general information, not tax advice).
- enrich22 (2026-11-12): `11_tax_1259_1256_roc_toy.py` new section I — Pub 550 gift and inherited basis (inherited FMV basis and always-long-term character; official gift dual-basis $10,000 / $9,000 / $9,500 neither-gain-nor-loss example; official holding-period split) (sections A–H still print as before, including the capital-loss cap, Ace short-sale, worthless last-day-of-year, investment interest, and stock-dividend prints, and 12/12; script total 16 assertions; general information, not tax advice).
- enrich23 (2026-11-12): `11_tax_1259_1256_roc_toy.py` new sections J–K — 1099-DIV box 2a capital-gain distributions (long-term regardless of holding period, even if no shares were sold) and Pub 550 puts and calls (official $4,000 expiration / $6,000 closing-transaction examples; 60/40 only if nonequity section 1256 contracts) (sections A–I still print as before, including box 3, the capital-loss cap, and the gift / inherited official $10,000 / $9,000 / $9,500 example, and 16/16 after I; section J prints 20/20; script total 26 assertions; general information, not tax advice).
- enrich24 (2026-11-12): `11_tax_1259_1256_roc_toy.py` new section L — Pub 550 “Put option as short sale” holding-period rule (buying a put is generally treated as a short sale; exercise, sale, or expiration closes that short sale; official short-term / holding-period-restart sentences; no married-put exception; no §1256 60/40) (sections A–K still print as before, including the official $4,000 / $6,000 examples and the section K “this toy is not that engine” line, and 26/26 after K; script total 32 assertions; general information, not tax advice). `09_tax_lot_toy.py` new section D — 1099-B box 5 / 12 / 1g (noncovered security; official Arlo June 2026 separate-form example; blank basis is not a zero cost; blank 1g is not proof that no wash sale occurred; do not conflate with 1099-DIV box 5) (sections A–C still print as before, including the official Pub 550 FIFO $1,380 example and 3/3 after C; script total 10 assertions; general information, not tax advice).
- enrich25 (2026-11-12): `11_tax_1259_1256_roc_toy.py` new section M — Pub 550 liquidating distributions (1099-DIV box 9 or 10, not box 1a / 1b and not already-taught box 3; not taxable until basis is recovered; after basis is zero, later amounts are capital gain; a capital loss only after the final redeeming or cancelling distribution; official complete-liquidation block allocation named only; synthetic $10,000 / $6,000 / $5,000 fixture, not an official numbered example) (sections A–L still print as before, including the official $4,000 / $6,000 examples, the section K “this toy is not that engine” line, section L, and 32/32 after L; script total 37 assertions; general information, not tax advice).
- enrich31 (2026-11-12): `08_self_trade_pattern_toy.py` new sections D–E — FINRA 2150 no improper use of a customer's securities or funds and no guarantee against loss (official caption typography is “Customers' Securities or Funds”; official (c) written-authorization and direct-proportion sharing conditions, with official family and Advisers Act Rule 205-3 alternatives, named only; official SM .01 / .02 / .03 exist; a member, but not an associated person, may reimburse a customer for transaction losses after the fact and may correct a bona fide error; not a flatten into already-taught 15c3-3 or SIPC, or into packed 2261), and FINRA 3220 current official gift limit of $300 per individual per year (SR-FINRA-2025-003 eff. Mar. 30, 2026, already effective; official SM .09 carves out gifts to the member's own associated persons and to individual retail customers; official (b)–(d) and SM .01–.08 named only; official typography is “SEA Rule 17a-4”; not the pre-amendment $100 cap as current law; not an invented retail-customer gift cap; not a flatten into already-taught 5230 or 5250) (sections A–C still print as before, including **7/7**, `ASSERT_self_trade_pattern_ok`, and the disclaimer, as a strict byte-prefix; section D prints 10/10; script total 13 assertions).
