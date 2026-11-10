"""Sell-side regulatory fees in a cost model: SEC Section 31 fee and FINRA TAF (checked 2026-11-11).

Sources:
- SEC Fee Rate Advisory FY2025 (2025-04-08): $0.00 per million from 2025-05-14 (was $27.80).
- SEC Fee Rate Advisory FY2026 (2026-02-27): $20.60 per million for covered sales on charge dates on or
  after 2026-04-04, "until 60 calendar days after legislation is enacted that sets the amount of the
  Commission's fiscal year 2027 appropriation". As of 2026-11-11 the SEC fee-rate page lists no FY2027
  Section 31 advisory.
- FINRA Fee Adjustment Schedule (SR-FINRA-2024-019): TAF on covered equity sales, 2025 $0.000166/share
  (max $8.30/trade), 2026 $0.000195 (max $9.79), 2027 $0.000232 (max $11.61).
- SR-FINRA-2026-021 (SEC Release 34-106409, 91 FR 60435): TAF paused for transactions 2026-10-01 through
  2026-12-31; assessment resumes 2027-01-01.
Both fees are assessed on SALES only. Brokers pass them through in their own way (rounding, small-order
waivers), so this toy prints unrounded amounts. Learning only; not a broker fee schedule.
"""
from datetime import date

checks = 0


def check(cond, label):
    global checks
    assert cond, label
    checks += 1


# (first charge date, USD per million of sale proceeds, note)
SEC31 = [
    (date(2025, 1, 1), 27.80, "toy table starts here; FY2025 advisory: $27.80 through 2025-05-13"),
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
    rate, _ = sec31_rate(d)
    sec = shares * price * rate / 1_000_000
    per_share, cap = taf_rule(d)
    taf = min(shares * per_share, cap)
    flag = " [check for a newer SEC advisory]" if d > CHECKED_ON else ""
    return sec, taf, flag


print("=== A. which rate applies on which trade date (sells only) ===")
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
    print(f"{d} {side:4s} {sh} sh @ {px:.2f} (USD {sh * px:,.0f}): SEC fee {sec:.4f}  TAF {taf:.4f}{flag}")
check(out[("buy", date(2026, 6, 15))] == (0.0, 0.0), "buys pay no Section 31 fee or TAF")
check(out[("sell", date(2025, 8, 1))][0] == 0.0, "SEC rate was $0.00 from 2025-05-14")
check(abs(out[("sell", date(2026, 6, 15))][0] - 1.03) < 1e-9, "50,000 x 20.60 / 1e6 = 1.03")
check(abs(out[("sell", date(2026, 6, 15))][1] - 0.195) < 1e-9, "1000 x 0.000195")
check(out[("sell", date(2026, 11, 11))][1] == 0.0, "TAF paused 2026-10-01..2026-12-31")
check(abs(out[("sell", date(2027, 1, 4))][1] - 0.232) < 1e-9, "2027 TAF 0.000232")

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
