# P1 labs

Offline synthetic examples for Phase P1. Learning only — not investment advice.

| Script | Artifacts |
| --- | --- |
| `01_markets_language.py` | CSV→NAV, Alpha/Beta toy → `01_*.out` |
| `02_microstructure_orders.py` | mid/bps, fill timing → `02_*.out` |
| `03_returns_vol_corr.py` | Sharpe/MDD + `public/p1/rolling_vol.png`, `rolling_corr_stress.png` |
| `04_eval_lab.py` | net-of-cost table, win-rate trap → `04_*.out` |

Data: `data/synthetic_ohlc_ba.csv` (seed 11 when generated).

- US-first pack (2026-11-08): `05_us_market_mechanics.py — US T+1, NYSE sessions in Shanghai time, toy NBBO (offline).`

- enrich7 (2026-11-10): `06_close_auction_roundlot.py` — official close vs last trade, NYSE MOC 15:50 ET cutoff in Shanghai time, tiered round lots, BOLO vs NBBO (17 assertions).

- enrich8 (2026-11-10): `07_etf_nav_letf_toy.py` — Rule 6c-11 premium/discount and the >2%-for-more-than-7-days statement trigger, median spread, SEC 1000→900→990 / 2x 800→960 daily-reset example, choppy-path decay for 1x/2x/3x/−2x (7 assertions; used by `markets-language` and `returns-vol-corr`).

- enrich9 (2026-11-10): `08_tbill_rf_toy.py` — TreasuryDirect bill price formula (999.27 example), 4.00%/91-day price and simple 365-day yield, Sharpe at Rf=0 vs 4%/252, prior-day rate as of each return (7 assertions; synthetic rates, no Treasury download).

- enrich11 (2026-11-11): `09_open_auction_toy.py` — NYSE open may print after 09:30 (DMM), Nasdaq MOO 09:28 ET cutoff in Shanghai time, signal-from-open look-ahead (5 assertions).

- enrich14 (2026-11-11): `10_early_close_nasdaq_moc_toy.py` — NYSE early-close MOC freeze at 12:50 ET (2026-11-27 and 2026-12-24; Beijing 01:50 next day) and Nasdaq regular-day close cutoffs (MOC 15:55 / LOC 15:58) (9 assertions).

- enrich15 (2026-11-11): `11_freeride_txse_15c33_toy.py` — Regulation T cash-account payment period (T+1 plus two business days = 3 BD) and 90-calendar-day freeride freeze, TXSE official session clock, Rule 15c3-3 credits−debits reserve toy (14 assertions).

- enrich17 (2026-11-12): `12_stop_order_toy.py` — stop becomes a market order (fill can deviate from the stop), stop-limit may not fill, trailing-stop $20→$24→trigger $23 example (5 assertions; investor.gov bulletin updated 2026-08-18).

- enrich18 (2026-11-12): `13_sale_condition_toy.py` — SIP sale conditions M / Q / T (CTS matrix: M is not the consolidated last and does not update volume; Q updates the consolidated open; T is not last-sale eligible but counts in volume, including ETH 21:00–09:30 and after 16:00) and 6 vs M (18 assertions).

- enrich21 (2026-11-12): `08_tbill_rf_toy.py` new section D — NY Fed SOFR published at approximately 8:00 a.m. ET one business day after its value date (Monday 2026-11-09 published Tuesday 2026-11-10 ~8:00 can fill at Tuesday’s 09:30 open; Tuesday’s value-date SOFR cannot be used Tuesday morning; official first SOFR 2018-04-03 for 2018-04-02) (sections A–C still print as before, including the 15:30 T-bill prints and 7/7; script total 9 assertions; teaching rate timestamp, not “the” risk-free rate).

- enrich21 (2026-11-12): `11_freeride_txse_15c33_toy.py` new section F — Rule 15c6-1 default T+1 unless otherwise expressly agreed at the time of the transaction, and FINRA 11320 delivery types (cash same day, regular way on but not before the first business day, delayed-delivery on the agreed date; 11320(e) non-business-day roll; 15c6-1(c) after-4:30 p.m. ET firm-commitment offering up to the second business day; current 11320 has no “next day” category) (sections A–E still print as before, including 14/14; script total 19 assertions).
- enrich22 (2026-11-12): `05_us_market_mechanics.py` new section D — Rule 602 firm quote (published offer is generally firm up to the published size; odd-lot orders are excluded; a revision communicated before presentation can change the obligation) (sections A–C still print as before; section D 3/3). `13_sale_condition_toy.py` new section E — current FINRA 6380A 10-second off-exchange TRF reporting (midnight–4:00 a.m. ET due by 4:15 a.m. on trade date, not the 10-second clock; SR-FINRA-2026-015 is not yet implemented) (sections A–D still print as before, including 18/18; script total 25 assertions).
- enrich28 (2026-11-12): `05_us_market_mechanics.py` new section E — FINRA 5220 offers at stated prices / firmness of quotations (a different firmness rule from already-taught Rule 602; a member may not offer at a stated price unless prepared to buy or sell at that price and under the stated conditions; official .01 expects at least a normal unit unless clearly designated as not firm or firm for less than a normal unit; a normal unit of trading for an NMS stock is the official 600(b) round lot, not an invented 100-share unit; official in-process revised-size clause exists; Rule 6420 named only) (sections A–D still print as before, including 3/3 after D / Rule 602; section E 4/4).
- enrich29 (2026-11-12): `13_sale_condition_toy.py` new section F — FINRA 2265 extended hours trading risk disclosure (furnished individually, in paper or electronic form, before a member may permit extended hours trading; official regular trading hours generally 9:30 a.m. to 4:00 p.m. Eastern Standard Time, quoted as written; official model wording includes “upon the opening the next morning”; official typography includes “on-line” and “Web site”; official (b) substantially similar alternative and official (c) additional disclosures named only; not a claim that the model statement is the only permitted text; not a rewrite of already-taught ETH sale-condition T or 6380A) (sections A–E still print as before, including 18/18 after D and 25/25 after E; script total 28 assertions). `11_freeride_txse_15c33_toy.py` new section G — FINRA 2266 written SIPC information at account opening and at least once each year, including the official Web site address and telephone number (official (a)–(b) exceptions named only; official typography is “Web site” as two words; not a rewrite of already-taught SIPC coverage limits; no invented coverage amount, form, or clock) (sections A–F still print as before, including the 15c3-3 line “this is separate from SIPC,” 14/14 after E, and 19/19 after F; script total 22 assertions).
