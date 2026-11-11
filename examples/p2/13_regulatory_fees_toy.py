"""Sell-side regulatory fees in a cost model: SEC Section 31 fee and FINRA TAF (checked 2026-11-11).

Sources:
- SEC Fee Rate Advisory #2 FY2024 (2024-04-17): $27.80 per million for covered sales on charge dates on or
  after 2024-05-22. SEC Fee Rate Advisory FY2025 (2025-04-08): $0.00 per million from charge date 2025-05-14.
- SEC Fee Rate Advisory FY2026 (2026-02-27): $20.60 per million for covered sales on charge dates on or
  after 2026-04-04, "until 60 calendar days after legislation is enacted that sets the amount of the
  Commission's fiscal year 2027 appropriation". As of 2026-11-11 the SEC fee-rate page lists no FY2027
  Section 31 advisory.
- FINRA Fee Adjustment Schedule (SR-FINRA-2024-019): TAF on covered equity sales, 2025 $0.000166/share
  (max $8.30/trade), 2026 $0.000195 (max $9.79), 2027 $0.000232 (max $11.61).
- SR-FINRA-2026-021 (SEC Release 34-106409, 91 FR 60435): TAF paused for transactions 2026-10-01 through
  2026-12-31; assessment resumes 2027-01-01.
- 17 CFR 240.31(a)(3): the charge date is the settlement date for covered sales an SRO reports from
  designated clearing agency data, and the trade date for all other covered sales. This toy assumes the
  first case and US T+1 settlement on the next business day, skipping weekends and a minimal
  settlement-holiday set. DTCC/NSCC holiday notices are authoritative; e.g. NSCC Important Notice
  a9732 (2026-03-06): markets and NSCC closed Fri 2026-04-03 (Good Friday), CNS settlement next on Mon
  2026-04-06. https://files.dtcc.com/download/assets/a9732/84f27534957911f1b6bb4ec37e043074
The SEC rate is looked up by charge date (= settlement date here); the TAF by trade date.
Both fees are assessed on SALES only. Brokers pass them through in their own way (rounding, small-order
waivers), so this toy prints unrounded amounts. Learning only; not a broker fee schedule.
"""
from datetime import date, timedelta

checks = 0


def check(cond, label):
    global checks
    assert cond, label
    checks += 1


# (first charge date, USD per million of sale proceeds, note)
SEC31 = [
    (date(2024, 5, 22), 27.80, "FY2024 advisory #2: from charge date 2024-05-22"),
    (date(2025, 5, 14), 0.00, "FY2025 advisory: appropriation collected"),
    (date(2026, 4, 4), 20.60, "FY2026 advisory; ends 60 days after FY2027 appropriation is enacted"),
]
# (first date, last date, USD per share, max per trade)
TAF = [
    (date(2025, 1, 1), date(2025, 12, 31), 0.000166, 8.30),
    (date(2026, 1, 1), date(2026, 9, 30), 0.000195, 9.79),
    (date(2026, 10, 1), date(2026, 12, 31), 0.0, 0.0),  # SR-FINRA-2026-021 pause
    (date(2027, 1, 1), date(2027, 12, 31), 0.000232, 11.61),
]
CHECKED_ON = date(2026, 11, 11)


# Minimal settlement-holiday set (toy). Not a full calendar: check DTCC/NSCC holiday notices.
SETTLEMENT_HOLIDAYS = {
    date(2026, 4, 3),  # Good Friday; NSCC Important Notice a9732: NSCC closed, no CNS processing
}


def settle_t1(trade):
    """Next business day: skips weekends and SETTLEMENT_HOLIDAYS (DTCC notices are authoritative)."""
    d = trade + timedelta(days=1)
    while d.weekday() >= 5 or d in SETTLEMENT_HOLIDAYS:
        d += timedelta(days=1)
    return d


def sec31_rate(d):
    rate, note = None, None
    for start, r, n in SEC31:
        if d >= start:
            rate, note = r, n
    return rate, note


def taf_rule(d):
    for a, b, per_share, cap in TAF:
        if a <= d <= b:
            return per_share, cap
    raise ValueError(f"no TAF row for {d}")


def reg_fees(side, shares, price, d):
    """Return (sec_fee, taf, flag). Buys pay neither fee."""
    if side == "buy":
        return 0.0, 0.0, ""
    rate, _ = sec31_rate(settle_t1(d))  # charge date = settlement date
    sec = shares * price * rate / 1_000_000
    per_share, cap = taf_rule(d)  # TAF: trade date
    taf = min(shares * per_share, cap)
    flag = " [check for a newer SEC advisory]" if d > CHECKED_ON else ""
    return sec, taf, flag


print("=== A. SEC rate by charge date (settlement, T+1), TAF by trade date (sells only) ===")
cases = [
    ("buy", 1000, 50.0, date(2026, 6, 15)),
    ("sell", 1000, 50.0, date(2025, 8, 1)),
    ("sell", 1000, 50.0, date(2026, 6, 15)),
    ("sell", 1000, 50.0, date(2026, 11, 11)),
    ("sell", 1000, 50.0, date(2027, 1, 4)),
]
out = {}
for side, sh, px, d in cases:
    sec, taf, flag = reg_fees(side, sh, px, d)
    out[(side, d)] = (sec, taf)
    print(f"trade {d} (settle {settle_t1(d)}) {side:4s} {sh} sh @ {px:.2f} (USD {sh * px:,.0f}): SEC fee {sec:.4f}  TAF {taf:.4f}{flag}")
check(out[("buy", date(2026, 6, 15))] == (0.0, 0.0), "buys pay no Section 31 fee or TAF")
check(out[("sell", date(2025, 8, 1))][0] == 0.0, "SEC rate was $0.00 from 2025-05-14")
check(abs(out[("sell", date(2026, 6, 15))][0] - 1.03) < 1e-9, "50,000 x 20.60 / 1e6 = 1.03")
check(abs(out[("sell", date(2026, 6, 15))][1] - 0.195) < 1e-9, "1000 x 0.000195")
check(out[("sell", date(2026, 11, 11))][1] == 0.0, "TAF paused 2026-10-01..2026-12-31")
check(abs(out[("sell", date(2027, 1, 4))][1] - 0.232) < 1e-9, "2027 TAF 0.000232")

print("=== A2. boundary: trade date vs charge date ===")
b_sec, b_taf, _ = reg_fees("sell", 1000, 50.0, date(2025, 5, 13))
print(f"trade 2025-05-13 (Tue) settles {settle_t1(date(2025, 5, 13))} -> SEC rate {sec31_rate(settle_t1(date(2025, 5, 13)))[0]:.2f}/M, SEC fee {b_sec:.4f} (by trade date it would be 27.80/M = 1.3900)")
check(settle_t1(date(2025, 5, 13)) == date(2025, 5, 14) and b_sec == 0.0, "05-13 sale settles 05-14 -> $0.00")
g_trade = date(2026, 4, 2)
g_settle = settle_t1(g_trade)
print(f"trade 2026-04-02 (Thu) -> 04-03 Good Friday, no settlement -> settles {g_settle} (Mon) -> "
      f"SEC rate {sec31_rate(g_settle)[0]:.2f}/M; by trade date it would wrongly be {sec31_rate(g_trade)[0]:.2f}/M")
check(g_settle == date(2026, 4, 6) and sec31_rate(g_settle)[0] == 20.60 and sec31_rate(g_trade)[0] == 0.00,
      "Good Friday: 04-02 trade settles 04-06 at 20.60, not trade-date 0.00")

print("=== B. the TAF cap binds on large share counts ===")
sec, taf, _ = reg_fees("sell", 100_000, 5.0, date(2026, 6, 15))
print(f"2026-06-15 sell 100,000 sh @ 5.00: raw TAF {100_000 * 0.000195:.2f} -> capped {taf:.2f}; SEC fee {sec:.2f}")
check(taf == 9.79, "2026 cap 9.79")

print("=== C. size versus this lesson's toy commission ===")
bps = 20.60 / 1_000_000 * 10_000
print(f"SEC fee at $20.60 per million = {bps:.3f} bps of sale proceeds (sells only); toy commission = 2 bps each way")
check(abs(bps - 0.206) < 1e-12, "0.206 bps")
print("round trip at 2026-06-15 on USD 50,000: buy 0 + sell SEC 1.03 + TAF 0.195 = 1.225 USD")
print("rule: store fee schedules with effective dates; never hard-code one rate for the whole backtest.")
print(f"assertions passed: {checks}/{checks}")
