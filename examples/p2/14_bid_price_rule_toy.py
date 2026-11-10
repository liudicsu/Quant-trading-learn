"""Nasdaq $1 bid-price rule, reverse splits and a stayed rule, as data flags (checked 2026-11-11).

Sources:
- SEC Release 34-102245 (2025-01-17, SR-NASDAQ-2024-045): closing bid below $1.00 for 30 consecutive
  business days = failure (Rule 5810(c)(3)(A)); 180-calendar-day compliance period; compliance = at
  least $1.00 for 10 consecutive business days; no compliance period if the company effected a reverse
  stock split over the prior one-year period.
- SEC Release 34-104318 (2025-12-05, SR-NASDAQ-2025-065; 90 FR, 2025-12-10): closing bid of $0.10 or
  less for ten consecutive business days -> Staff Delisting Determination, trading suspended on Nasdaq,
  no compliance period; operative 45 days after approval.
- SEC Release 34-105971 (2026-07-22, SR-NASDAQ-2026-004): new $5 million Market Value of Listed
  Securities requirement; stayed by the Commission (34-106594, 2026-10-05, describes the stay).
Rows are business days (no calendar). Synthetic prices; no real company. Learning only.
"""
from datetime import date, timedelta

checks = 0


def check(cond, label):
    global checks
    assert cond, label
    checks += 1


def run_below(bids, level, strict=True):
    """Longest current run (ending at the last row) of bids below (or at) a level."""
    n = 0
    for b in bids:
        hit = b < level if strict else b <= level
        n = n + 1 if hit else 0
    return n


def status(bids, reverse_split_within_1y=False):
    if run_below(bids, 0.10, strict=False) >= 10:
        return "delisting determination + suspended on Nasdaq (<= $0.10 for 10 business days)"
    if run_below(bids, 1.00) >= 30:
        if reverse_split_within_1y:
            return "deficient; reverse split in prior year -> no compliance period, delisting determination"
        return "deficient; 180-calendar-day compliance period starts at Nasdaq's notice"
    return "no bid-price flag"


print("=== A. counting consecutive business days ===")
a = [1.20] * 5 + [0.80] * 29
b = a + [0.80]
print(f"29 closes below $1.00 -> {status(a)}")
print(f"30 closes below $1.00 -> {status(b)}")
print(f"30 closes below $1.00, reverse split 8 months ago -> {status(b, True)}")
check(status(a) == "no bid-price flag", "29 is not 30")
check(status(b).startswith("deficient; 180"), "30 consecutive")
check("no compliance period" in status(b, True), "prior-year reverse split")
c = [0.80] * 20 + [0.09] * 10
print(f"10 closes at or below $0.10 -> {status(c)}")
check(status(c).startswith("delisting determination"), "$0.10 rule")
notice = date(2026, 3, 2)
print(f"notice on {notice} -> 180 calendar days end {notice + timedelta(days=180)}")
check(notice + timedelta(days=180) == date(2026, 8, 29), "180 calendar days")

print("=== B. a 1-for-10 reverse split in the raw series ===")
raw = [0.62, 0.60, 6.10, 6.05]  # 10 old shares became 1 new share before row 3
naive = raw[2] / raw[1] - 1
holder = raw[2] / (raw[1] * 10) - 1
print(f"raw close-to-close on the split day {naive:+.1%} (fake); holder return {holder:+.2%}")
check(abs(holder - (6.10 / 6.00 - 1)) < 1e-12, "adjusted return")
regain = [1.05] * 9
print(f"after the split: 9 closes >= $1.00 -> regained? {len(regain) >= 10}; needs 10")
check(len(regain) < 10, "10 consecutive business days to regain")

print("=== C. rule status is data too ===")
RULES = {
    "bid_price_30d": ("in force", "34-102245 amendments approved 2025-01-17"),
    "low_price_0.10": ("in force", "34-104318 approved 2025-12-05, operative 45 days later"),
    "mvls_5m": ("stayed", "34-105971 approved 2026-07-22, then stayed; check sec.gov before use"),
}
for k, (st, note) in RULES.items():
    print(f"{k:15s} {st:9s} {note}")
check(RULES["mvls_5m"][0] == "stayed", "do not apply a stayed rule")
print("rule: a reverse split near $1 is a listing-status event; keep the delisting flag and the split ratio.")
print(f"assertions passed: {checks}/{checks}")
