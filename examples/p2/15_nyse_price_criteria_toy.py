"""NYSE $1.00 price criteria (Listed Company Manual 802.01C) and the $0.25 Minimum Trading Price, as data
flags (checked 2026-11-11).

Sources:
- SEC Release 34-102201 (2025-01-15, SR-NYSE-2024-48), which restates 802.01C: a company is below compliance
  if the AVERAGE closing price over a consecutive 30 trading-day period is less than $1.00. It has six
  months from the notice to cure; it regains compliance if, on the last trading day of any calendar month in
  the cure period, the closing price is at least $1.00 AND the 30 trading-day average closing price ending
  that day is at least $1.00. The 2025 amendment: if the company effected a reverse split over the prior
  one-year period, or reverse splits with a cumulative ratio of 200 shares or more to one over the prior
  two-year period, it gets no compliance period and NYSE immediately starts suspension and delisting.
- SEC Release 34-106133 (2026-08-14, SR-NYSE-2025-43, 91 FR, 2026-08-18): a closing price below $0.25 on any
  trading day -> immediate suspension and delisting proceedings, no cure period; effective 2027-07-01
  (Amendment No. 2 moved it from 2026-10-01). NYSE may also suspend a security whose price has fallen to an
  "abnormally low" level even above $0.25 (802.01D).
Rows are trading days (no calendar). Synthetic prices; no real company. Learning only, not a signal.
"""
from datetime import date

checks = 0


def check(cond, label):
    global checks
    assert cond, label
    checks += 1


def avg30(closes):
    assert len(closes) >= 30
    return sum(closes[-30:]) / 30


def nasdaq_style_run(closes, level=1.00):
    """Consecutive closes below level ending today (Nasdaq counts closing BIDS; closes used here as a stand-in)."""
    n = 0
    for c in closes:
        n = n + 1 if c < level else 0
    return n


def nyse_status(closes, reverse_split_within_1y=False, cumulative_ratio_2y=1.0):
    if avg30(closes) >= 1.00:
        return "no price-criteria flag"
    if reverse_split_within_1y or cumulative_ratio_2y >= 200:
        return "below $1 average; recent reverse split(s) -> no compliance period, suspension/delisting starts"
    return "below $1 average; six-month cure period from NYSE's notice"


def nyse_cured_at_month_end(closes):
    """Checked only on the last trading day of a calendar month (this toy treats the last row as that day)."""
    return closes[-1] >= 1.00 and avg30(closes) >= 1.00


MIN_TRADING_PRICE_EFFECTIVE = date(2027, 7, 1)


def min_trading_price_hit(close, d):
    return d >= MIN_TRADING_PRICE_EFFECTIVE and close < 0.25


print("=== A. NYSE averages 30 trading days; Nasdaq counts consecutive days ===")
zigzag = [0.97, 1.01] * 15                      # 30 rows, average 0.99, never 30 in a row below $1
print(f"zigzag 0.97/1.01 x15: NYSE 30-day average {avg30(zigzag):.4f} -> {nyse_status(zigzag)}")
print(f"  same rows, consecutive closes below $1.00 at the end: {nasdaq_style_run(zigzag)} (a 30-in-a-row count never fires)")
check(abs(avg30(zigzag) - 0.99) < 1e-12 and nyse_status(zigzag).startswith("below"), "average below $1")
check(nasdaq_style_run(zigzag) < 30, "consecutive count never reaches 30")
dip = [1.40] * 20 + [0.40] * 10                 # ten closes at $0.40, average still >= $1
print(f"20 x 1.40 then 10 x 0.40: average {avg30(dip):.4f} -> {nyse_status(dip)}")
check(nyse_status(dip) == "no price-criteria flag", "ten closes below $1 but average 1.0667")

print("=== B. regaining compliance: checked at a month end, needs BOTH tests ===")
jump = [0.70] * 29 + [1.20]                      # one strong close at the month end
print(f"month-end close 1.20 but 30-day average {avg30(jump):.4f} -> cured? {nyse_cured_at_month_end(jump)}")
check(not nyse_cured_at_month_end(jump), "close alone is not enough")
steady = [1.05] * 30
print(f"month-end close 1.05, 30-day average {avg30(steady):.4f} -> cured? {nyse_cured_at_month_end(steady)}")
check(nyse_cured_at_month_end(steady), "both tests pass")

print("=== C. 2025 amendment: recent reverse splits remove the cure period ===")
low = [0.80] * 30
print(f"average 0.80, no recent split -> {nyse_status(low)}")
print(f"average 0.80, 1-for-5 split 7 months ago -> {nyse_status(low, True)}")
print(f"average 0.80, 1-for-10 then 1-for-20 (200:1) over two years, none in prior year -> {nyse_status(low, False, 200)}")
print(f"average 0.80, 1-for-10 then 1-for-15 (150:1) over two years, none in prior year -> {nyse_status(low, False, 150)}")
check("no compliance period" in nyse_status(low, True), "prior-year reverse split")
check("no compliance period" in nyse_status(low, False, 200), "NYSE threshold is 200:1 (Nasdaq: 250:1)")
check("six-month" in nyse_status(low, False, 150), "150:1 outside one year keeps the cure period")

print("=== D. $0.25 Minimum Trading Price: a dated rule (effective 2027-07-01) ===")
for close, d in [(0.24, date(2027, 6, 30)), (0.24, date(2027, 7, 1)), (0.26, date(2027, 7, 1))]:
    print(f"close {close:.2f} on {d}: immediate suspension under the $0.25 rule? {min_trading_price_hit(close, d)}")
check(not min_trading_price_hit(0.24, date(2027, 6, 30)), "not in force before 2027-07-01")
check(min_trading_price_hit(0.24, date(2027, 7, 1)), "one close below $0.25 is enough")
check(not min_trading_price_hit(0.26, date(2027, 7, 1)), "0.26 is above the floor (802.01D may still apply)")
RULES = {
    "nyse_avg30_1usd": ("in force", "802.01C; reverse-split limits from 34-102201 (2025-01-15)"),
    "nyse_min_0.25": ("approved, not yet effective", "34-106133 (2026-08-14), effective 2027-07-01"),
}
for k, (st, note) in RULES.items():
    print(f"{k:16s} {st:27s} {note}")
print("rule: store the exchange, the rule version and the notice/suspension dates; this is listing status, not a signal.")
print(f"assertions passed: {checks}/{checks}")
