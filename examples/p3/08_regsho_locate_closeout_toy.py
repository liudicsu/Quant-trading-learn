"""Reg SHO locate vs borrow, Rule 204 close-out under T+1, Rule 201 price test,
and the threshold-security definition (checked 2026-11-11).

Sources:
- 17 CFR 242.203(b)(1): a broker-dealer may not accept or effect a short sale unless it has
  borrowed the security, entered into a bona-fide arrangement to borrow it, or has reasonable
  grounds to believe the security can be borrowed so that it can be delivered on the date
  delivery is due, and has documented compliance. A locate is not the same as a completed borrow.
- 17 CFR 242.204(a): close out a fail by no later than the beginning of regular trading hours
  on the settlement day following the settlement date (default, including short-sale fails).
  Long-sale fails the participant can demonstrate, and bona-fide market-making fails: the
  beginning of regular trading hours on the third consecutive settlement day following the
  settlement date. Settlement date is the clearing-agency delivery date (under T+1, usually
  the next business day). 89 FR 26608 (2024-04-15) amended the rule for T+1. This script does
  not use stale "T+4" / "T+6" labels that some older FAQ pages still print.
- 17 CFR 242.201(b)(1)(i): after a 10% drop from the listing market's prior-day close, a
  trading center's policies must prevent execution or display of a short sale at a price that
  is less than or equal to the current national best bid, for the rest of that day and the next.
- 17 CFR 242.203(c)(6): a threshold security has an aggregate fail of 10,000 shares or more
  that is also at least 0.5% of total shares outstanding, for five consecutive settlement days,
  and is on an SRO-disseminated list.

Weekends and the 2026 Thanksgiving week only, as dated. Learning only; not a short-sale recipe.
"""
from datetime import date, timedelta

checks = 0


def check(cond, label):
    global checks
    assert cond, label
    checks += 1


print("=== A. locate (Rule 203(b)(1)) is not a completed borrow ===")


def locate_ok(borrowed=False, arrangement=False, reasonable_grounds=False, documented=False):
    return documented and (borrowed or arrangement or reasonable_grounds)


cases = [
    ("borrowed and documented", dict(borrowed=True, documented=True), True),
    ("arrangement and documented", dict(arrangement=True, documented=True), True),
    ("reasonable grounds and documented", dict(reasonable_grounds=True, documented=True), True),
    ("reasonable grounds but not documented", dict(reasonable_grounds=True, documented=False), False),
    ("nothing in place", dict(), False),
]
for label, kwargs, expect in cases:
    got = locate_ok(**kwargs)
    print(f"  {label}: locate_ok={got}")
    check(got is expect, label)
print("a locate can be reasonable grounds that the shares can be borrowed by settlement; it is not already borrowing them")

print("=== B. Rule 204 close-out under T+1 (skip Thanksgiving 2026-11-26) ===")
HOLIDAYS = {date(2026, 11, 26)}


def is_settlement_day(d):
    return d.weekday() < 5 and d not in HOLIDAYS


def add_settlement_days(d, n):
    while n:
        d += timedelta(days=1)
        if is_settlement_day(d):
            n -= 1
    return d


def settlement_date(trade):
    return add_settlement_days(trade, 1)


def short_fail_closeout_morning(trade):
    """Beginning of regular hours on the settlement day following the settlement date."""
    return add_settlement_days(settlement_date(trade), 1)


def long_fail_closeout_morning(trade):
    """Beginning of regular hours on the third consecutive settlement day following settlement."""
    return add_settlement_days(settlement_date(trade), 3)


trade = date(2026, 11, 23)  # Monday
sd = settlement_date(trade)
short_co = short_fail_closeout_morning(trade)
long_co = long_fail_closeout_morning(trade)
print(f"trade {trade} (Mon) -> settlement {sd} (Tue) -> short-fail close-out by regular open {short_co} (Wed)")
print(f"same trade, demonstrated long-sale fail -> close-out by regular open {long_co}")
check(sd == date(2026, 11, 24), "T+1 settlement")
check(short_co == date(2026, 11, 25), "short fail: morning of T+2")
check(long_co == date(2026, 11, 30), "long fail: settlement + 3 settlement days, skipping Thanksgiving")

trade2 = date(2026, 11, 25)  # Wednesday before Thanksgiving
sd2 = settlement_date(trade2)
short_co2 = short_fail_closeout_morning(trade2)
print(f"trade {trade2} (Wed) -> settlement {sd2} (Fri, skips Thanksgiving) -> short-fail close-out by regular open {short_co2}")
check(sd2 == date(2026, 11, 27) and short_co2 == date(2026, 11, 30), "Thanksgiving week roll")

print("=== C. Rule 201: after a 10% drop, a short sale may not be at or below the NBB ===")
prior_close = 20.00
nbb = 17.90
print(f"prior listing-market close {prior_close:.2f}; last sale 17.90 is a {100 * (prior_close - 17.90) / prior_close:.1f}% decline -> Rule 201 on")
check((prior_close - 17.90) / prior_close >= 0.10, "10% trigger")


def short_allowed_at(price, nbb_now, rule201_on):
    if not rule201_on:
        return True
    return price > nbb_now


for px in (17.90, 17.91):
    print(f"  short at {px:.2f} vs NBB {nbb:.2f}: allowed={short_allowed_at(px, nbb, True)}")
check(not short_allowed_at(17.90, nbb, True), "at the NBB is not allowed")
check(short_allowed_at(17.91, nbb, True), "above the NBB is allowed")

print("=== D. threshold security (Rule 203(c)(6)): 10,000 shares AND 0.5% of shares outstanding, five settlement days, on an SRO list ===")
shares_outstanding = 2_000_000
fail = 12_000
pct = fail / shares_outstanding
print(f"fail {fail:,} shares vs 0.5% of {shares_outstanding:,} = {0.005 * shares_outstanding:,.0f}; fail is {pct:.2%} of outstanding")
meets_size = fail >= 10_000 and pct >= 0.005
print(f"size test met? {meets_size}; still needs five consecutive settlement days and an SRO list to be a threshold security")
check(meets_size, "this example meets the size test")
check(not (9_000 >= 10_000 and 9_000 / shares_outstanding >= 0.005), "9,000 shares fails the 10,000-share prong")
# 0.5% of 2,000,000 is 10,000, so both prongs bind together here.
# A 12,000 fail on a 10,000,000-share issuer is 0.12% and would fail the 0.5% prong.
check(not (12_000 / 10_000_000 >= 0.005), "12,000 on a larger issuer can miss 0.5%")

print(f"OK {checks} assertions")
