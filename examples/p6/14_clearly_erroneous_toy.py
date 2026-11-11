"""Clearly erroneous print reviewability and numerical guidelines (checked 2026-11-12).

Sources:
- FINRA Rule 11892: during Normal Market Hours (09:30–16:00 ET), a transaction is
  generally not reviewable as clearly erroneous unless a listed exception applies
  (NMS stock not subject to the LULD Plan; bands unavailable, or a systems issue
  puts the trade outside the bands, or the trade is after a primary-listing-market
  regulatory halt / suspension / pause; certain corporate-action / new-issue or
  LULD-pause-then-resume-without-auction cases). FINRA 11892 covers over-the-counter
  transactions in exchange-listed securities. On-exchange prints follow the executing
  exchange's parallel rule (e.g. NYSE Rule 7.10, Nasdaq Equity 11 Rule 11890).
- Numerical guidelines vs the consolidated last sale, when a review is allowed
  outside those hours or for non-LULD stocks under 11892(b)(2):
  FINRA wording: Greater than $0.00 up to and including $25.00: 10% (normal-hours-
  eligible) / 20% (outside normal hours); Greater than $25.00 up to and including
  $50.00: 5% / 10%; Greater than $50.00: 3% / 6%. Multi-stock and leveraged-ETP
  rows stay with the cited rule and are not blended here.
  NYSE Rule 7.10 Exhibit 5 uses different bucket labels for the first two rows
  ("Between $0.00 and $25.00" / "Between $25.01 and $50.00") with the same
  percentages. This toy does not invent a blended table; it prints both wordings
  and applies only the FINRA labels when it classifies a reference price.
- 2026 overnight extension: several exchanges filed immediately effective changes
  to extend the "not reviewable while bands are in place" logic to Overnight
  Protected Hours, operative at the commencement of 23/5 trading, scheduled
  industry-wide 2026-12-06 (SEC 34-106407, 34-106631, 34-106604, 34-106727,
  34-106649). Those notices say they understand other exchanges and FINRA will
  file identical substance. The FINRA 11892 text retrieved 2026-11-12 still has
  no Overnight Protected Hours clause — this toy does not treat FINRA 11892 as
  already amended, and does not invent a single market-wide overnight CE rule.

Learning only; not a recommendation of any venue or a complete rule engine.
"""
from datetime import date
from decimal import Decimal

checks = 0


def check(cond, label):
    global checks
    assert cond, label
    checks += 1


OPERATIVE = date(2026, 12, 6)


def finra_bucket(reference):
    """FINRA 11892 labels only; not a blended FINRA/NYSE table."""
    p = Decimal(str(reference))
    if p <= 0:
        raise ValueError(reference)
    if p <= Decimal("25.00"):
        return ("Greater than $0.00 up to and including $25.00", Decimal("0.10"), Decimal("0.20"))
    if p <= Decimal("50.00"):
        return ("Greater than $25.00 up to and including $50.00", Decimal("0.05"), Decimal("0.10"))
    return ("Greater than $50.00", Decimal("0.03"), Decimal("0.06"))


def pct_away(price, reference):
    price = Decimal(str(price))
    reference = Decimal(str(reference))
    return abs(price - reference) / reference


print("=== A. FINRA 11892 numerical-guideline buckets (not a blended table) ===")
print("FINRA 11892: Greater than $0.00 up to and including $25.00 -> 10% / 20%;")
print("  Greater than $25.00 up to and including $50.00 -> 5% / 10%; Greater than $50.00 -> 3% / 6%")
print("NYSE Rule 7.10 Exhibit 5 labels the first two rows: Between $0.00 and $25.00 / Between $25.01 and $50.00")
print("  (same percentages). $25.00 is in the first bucket under both wordings; $25.01 is in the second under both.")
for ref, expect_normal, expect_outside in (
    (Decimal("25.00"), Decimal("0.10"), Decimal("0.20")),
    (Decimal("25.01"), Decimal("0.05"), Decimal("0.10")),
    (Decimal("50.00"), Decimal("0.05"), Decimal("0.10")),
    (Decimal("50.01"), Decimal("0.03"), Decimal("0.06")),
):
    label, normal, outside = finra_bucket(ref)
    print(f"  FINRA bucket for ${ref}: {label} -> {normal:.0%} / {outside:.0%}")
    check(normal == expect_normal and outside == expect_outside, f"bucket {ref}")

print("=== B. Regular hours: an ordinary LULD-covered print is generally not reviewable ===")


def regular_hours_reviewable(luld_covered, listed_exception):
    """True only if a listed 11892(b)(1) exception applies, or the stock is not LULD-covered."""
    if not luld_covered:
        return True
    return bool(listed_exception)


cases = (
    ("LULD-covered, 15% from last sale, no listed exception", True, False, False),
    ("not subject to the LULD Plan", False, False, True),
    ("LULD-covered, bands unavailable (listed exception)", True, True, True),
)
for label, covered, exc, expect in cases:
    got = regular_hours_reviewable(covered, exc)
    print(f"  {label}: reviewable={got}")
    check(got is expect, label)
print("the old percentage table is not the regular-hours test for ordinary LULD stocks")

print("=== C. Outside hours, and the 2026-12-06 overnight extension ===")
print("until 23/5 starts (scheduled 2026-12-06), outside-hours reviews still use the outside-hours numerical guidelines")
print("FINRA 11892 retrieved 2026-11-12 has no Overnight Protected Hours clause;")
print("do not write that FINRA has already amended 11892, or that the whole market has one overnight CE rule")


def overnight_generally_stands(as_of, venue_rule_extended):
    """Once 23/5 has started and the executing venue's rule is operative, a print
    inside overnight bands is generally expected to stand. FINRA 11892 as of
    2026-11-12 is not that rule."""
    return as_of >= OPERATIVE and venue_rule_extended


for label, as_of, extended, expect in (
    ("2026-11-12, FINRA 11892 as retrieved", date(2026, 11, 12), False, False),
    ("2026-12-06, NYSE Rule 7.10 as amended (34-106407)", date(2026, 12, 6), True, True),
    ("2026-12-05, even on a venue that has filed", date(2026, 12, 5), True, False),
):
    got = overnight_generally_stands(as_of, extended)
    print(f"  {label}: print inside overnight bands generally expected to stand? {got}")
    check(got is expect, label)

print("=== D. Toy: is this away from the reference by at least the outside-hours guideline? ===")
# $20 last sale, print at $24 = 20% away, equals the 20% outside-hours guideline for the <=$25 bucket.
ref, px = Decimal("20.00"), Decimal("24.00")
_, _, outside = finra_bucket(ref)
away = pct_away(px, ref)
meets = away >= outside
print(f"  reference ${ref} print ${px}: {away:.0%} away; outside-hours guideline {outside:.0%}; meets guideline? {meets}")
check(meets is True, "20% away at $20")
print(f"assertions passed: {checks}/{checks}")
