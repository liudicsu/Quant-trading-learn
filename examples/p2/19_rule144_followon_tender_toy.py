"""Rule 144 volume / Form 144 notice, Rule 105 restricted period, Rule 14e-1 tender window
(checked 2026-11-11). Synthetic dates; weekdays only, no holidays.

Sources:
- 17 CFR 230.144(e)(1): affiliate three-month sales shall not exceed the greatest of
  1% of the class outstanding, the four-calendar-week average weekly exchange / NASD
  reported volume, or the four-week average weekly volume reported under an effective
  transaction reporting / NMS plan.
- 17 CFR 230.144(h): Form 144 is required if the amount to be sold under the rule in
  three months exceeds 5,000 shares or has an aggregate sale price in excess of $50,000;
  it is transmitted concurrently with placing the broker order or executing with a market
  maker. It is a notice of proposed sale, not proof a sale occurred.
- 17 CFR 242.105(a): unlawful to short the offered equity during the Rule 105 restricted
  period and then buy the offered securities from an underwriter or participating broker
  or dealer. The restricted period is the shorter of (1) beginning five business days
  before pricing and ending with pricing, or (2) beginning with the initial registration
  filing (or Form 1-A / 1-E) and ending with pricing. 242.105(c): does not apply to
  offerings that are not firm-commitment.
- 17 CFR 240.14e-1(a),(b): a tender offer must stay open at least 20 business days from
  the date it is first published or sent; if the percentage sought, the consideration, or
  the dealer's soliciting fee changes, it must stay open at least 10 business days from
  that notice. The 2026-04-16 equity exemptive order is not applied automatically here.

Learning only; not legal advice and not a trading signal.
"""
from datetime import date, timedelta

checks = 0


def check(cond, label):
    global checks
    assert cond, label
    checks += 1


def weekdays(start, n):
    """n weekdays strictly before start (n=1 is the previous Mon-Fri)."""
    d, seen = start, 0
    while seen < n:
        d -= timedelta(days=1)
        if d.weekday() < 5:
            seen += 1
    return d


def add_weekdays(start, n):
    """Count start as day 1; return the nth weekday on or after start."""
    d, seen = start - timedelta(days=1), 0
    while seen < n:
        d += timedelta(days=1)
        if d.weekday() < 5:
            seen += 1
    return d


print("=== A. Rule 144 affiliate three-month volume cap ===")
outstanding = 100_000_000
one_pct = outstanding * 0.01
weeks = [800_000, 900_000, 1_100_000, 1_200_000]
avg = sum(weeks) / 4
cap = max(one_pct, avg)
print(f"1% of {outstanding} outstanding = {one_pct:.0f}")
print(f"four-week average weekly volume = {avg:.0f}")
print(f"listed-stock cap (greater of 1% and four-week average) = {cap:.0f}")
check(one_pct == 1_000_000, "one_pct")
check(avg == 1_000_000, "avg")
check(cap == 1_000_000, "cap equal")
weeks_hi = [1_200_000, 1_400_000, 1_600_000, 1_800_000]
avg_hi = sum(weeks_hi) / 4
cap_hi = max(one_pct, avg_hi)
print(f"if four-week average is {avg_hi:.0f}, listed-stock cap = {cap_hi:.0f}")
check(avg_hi == 1_500_000 and cap_hi == 1_500_000, "cap follows the average when it is larger")
print("OTC / non-listed: the SEC Rule 144 investor publication says only the 1% measure applies")
otc_cap = one_pct
print(f"OTC cap in this toy = {otc_cap:.0f} (1% only)")
check(otc_cap == 1_000_000, "otc")

print("=== B. Form 144 notice threshold ===")


def form144_required(shares, price):
    return shares > 5_000 or shares * price > 50_000


for shares, price, expect in (
    (4_000, 10.0, False),   # $40,000 and 4,000 shares: neither threshold
    (4_000, 20.0, True),    # $80,000
    (6_000, 5.0, True),     # 6,000 shares
    (5_000, 10.0, False),   # the rule says "exceeds" 5,000 shares or $50,000
):
    got = form144_required(shares, price)
    print(f"  {shares} shares at ${price:.2f} (gross ${shares * price:.0f}): Form 144 required? {got}")
    check(got is expect, f"{shares}@{price}")
print("Form 144 is a notice of proposed sale, filed with the order; it is not executed volume")

print("=== C. Rule 105 restricted period (five business days before pricing) ===")
pricing = date(2026, 6, 12)  # Friday
start = weekdays(pricing, 5)
print(f"pricing {pricing}; five business days before = {start} (toy weekdays only)")
check(start == date(2026, 6, 5), "start Jun 5")
for d, expect in (
    (date(2026, 6, 4), False),  # Thursday before the start
    (date(2026, 6, 5), True),
    (date(2026, 6, 12), True),  # the period ends with pricing
):
    inside = start <= d <= pricing
    print(f"  short on {d}: inside restricted period? {inside}")
    check(inside is expect, str(d))
print("a short inside this window plus a purchase of the offered shares from an underwriter is the Rule 105 prohibition (firm-commitment equity offerings); exceptions exist but are not modelled here")

print("=== D. Rule 14e-1 minimum tender window (toy weekday count) ===")
print("official 'business day' is defined in Rules 14d-1(g)(3) and 13e-4(a)(3); this toy counts Mon-Fri and ignores holidays")
commenced = date(2026, 3, 2)  # Monday
day20 = add_weekdays(commenced, 20)
print(f"offer first published {commenced}; 20th weekday (counting that date as day 1) = {day20}")
check(day20 == date(2026, 3, 27), "day20")
change = date(2026, 3, 20)
day10 = add_weekdays(change, 10)
print(f"if consideration is increased on {change}, 10 weekdays from that notice (counting that date as day 1) = {day10}")
check(day10 == date(2026, 4, 2), "day10")
print("the April 16, 2026 exemptive order can shorten some equity offers to 10 business days only when every stated condition is met; this toy does not apply that order")
print(f"assertions passed: {checks}/{checks}")
