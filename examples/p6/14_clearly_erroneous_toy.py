"""Clearly erroneous print reviewability and numerical guidelines (checked 2026-11-26).

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
- 2026 overnight extension: FINRA filed SR-FINRA-2026-027 on November 18, 2026
  (official SEC PDF caption typography "[Release No. 34-106946; File No.
  SR-FINRA-2026-027]", official "November 20, 2026."). Official Exhibit 5 is
  official proposed rule-body typography. Official Commission typography contains
  both "become operative on December 6, 2026, when exchanges will commence 23/5
  Trading" and "the Commission waives the 30-day operative delay and designates
  the proposed rule change to be operative upon filing." The official live FINRA
  11892 rulebook HTML opened 2026-11-26 still has official visible typography
  "If the execution time of the transaction(s) under review is during Normal
  Market Hours, the transaction will not be reviewable as clearly erroneous
  unless the transaction:" and does not contain official "Overnight Protected
  Hours" or official "LULD Protected Hours" in the official rule body. Official
  amendment-line typography still ends at official "Amended by SR-FINRA-2022-027
  eff. Oct. 1, 2022." This toy does not write that the live rulebook has already
  printed the new rule text, and does not write that FINRA has not filed. Several
  exchanges also filed immediately effective changes (SEC 34-106407, 34-106631,
  34-106604, 34-106727, 34-106649). Official IEX "Release No. 34–106920" /
  official "Rule 11.270" and official TXSE "Release No. 34–106938" / official
  "Rule 11.014" may be named as same-kind companions. This toy does not invent a
  single market-wide overnight CE rule, and does not fold this item into leftover
  official N7 / official FINRA 6121.02 typography. Official "will stand and not
  be broken" is official purpose / official Commission 2022 quotation typography,
  not official Exhibit 5 rule-body typography, and is not rewritten into the
  official Exhibit 5 (b)(1) sentence.

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

# Official typography from official file bytes (checked 2026-11-26).
SEC_CAPTION = "[Release No. 34-106946; File No. SR-FINRA-2026-027]"
SEC_NOTICE_DATE = "November 20, 2026."
SEC_FILED = (
    "notice is hereby given that on November 18, 2026, the Financial Industry "
    "Regulatory Authority, Inc. (\u201cFINRA\u201d) filed with the Securities and Exchange Commission"
)
FR_HEADER = "75956 Federal Register / Vol. 91, No. 225 / Tuesday, November 24, 2026 / Notices"
FR_DOC = "[FR Doc. 2026\u201323915 Filed 11\u201323\u201326; 8:45 am]"
FR_RELEASE = "34\u2013106946"
FR_FILE = "SR\u2013FINRA\u20132026\u2013027"
EXHIBIT_5_DEF = (
    "For the purposes of this Rule, \u201cLULD Protected Hours\u201d includes Normal Market Hours "
    "(9:30 a.m. Eastern Time to 4:00 p.m. Eastern Time) and Overnight Protected Hours as defined "
    "in Section VIII of the Plan to Address Extraordinary Market Volatility Pursuant to Rule 608 "
    "of SEC Regulation NMS under the Exchange Act (\u201cLULD Plan\u201d)."
)
EXHIBIT_5_B1 = (
    "If the execution time of the transaction(s) under review is during LULD Protected "
    "Hours[Normal Market Hours], the transaction will not be reviewable as clearly erroneous "
    "unless the transaction:"
)
PURPOSE_HOURS = "9:30 a.m. Eastern Time (\u201cE.T.\u201d) to 4:00 p.m. E.T."
OPERATIVE_DEC6 = "become operative on December 6, 2026, when exchanges will commence 23/5 Trading"
OPERATIVE_UPON_FILING = (
    "the Commission waives the 30-day operative delay and designates the proposed rule change "
    "to be operative upon filing."
)
LIVE_B1 = (
    "If the execution time of the transaction(s) under review is during Normal Market Hours, "
    "the transaction will not be reviewable as clearly erroneous unless the transaction:"
)
AMENDMENT_LINE = "Amended by SR-FINRA-2022-027 eff. Oct. 1, 2022."
STAND_PHRASE = "will stand and not be broken"


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

print("=== C. Outside hours, and the filed 2026-12-06 overnight extension ===")
print("until 23/5 starts (scheduled 2026-12-06), outside-hours reviews still use the outside-hours numerical guidelines")
print("FINRA filed SR-FINRA-2026-027 on November 18, 2026")
print(f"official SEC PDF caption typography is {SEC_CAPTION}")
print(f"official SEC notice-date typography is {SEC_NOTICE_DATE}")
print(f"official body typography is {SEC_FILED}")
print(f"official Federal Register header typography is {FR_HEADER}")
print(f"official FR Doc typography is {FR_DOC}")
print(f"official FR release typography uses official {FR_RELEASE} and official {FR_FILE}")
print(f"official Commission typography contains both {OPERATIVE_DEC6}")
print(f"and {OPERATIVE_UPON_FILING}")
print(f"official live FINRA 11892 rulebook opened 2026-11-26 still has: {LIVE_B1}")
print(f"official amendment-line typography still ends at {AMENDMENT_LINE}")
print("do not write that the live rulebook has already printed the new rule text, and do not write that FINRA has not filed")


def overnight_generally_stands(as_of, venue_rule_extended):
    """Once 23/5 has started and the executing venue's rule is operative, a print
    inside overnight bands is generally expected to stand. The live FINRA 11892
    rulebook opened 2026-11-26 is not that printed rule body."""
    return as_of >= OPERATIVE and venue_rule_extended


for label, as_of, extended, expect in (
    ("2026-11-26, live FINRA 11892 rulebook as opened", date(2026, 11, 26), False, False),
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

print("=== E. Official typography checks (Exhibit 5 vs live rulebook; both operative phrases) ===")
check("-" in SEC_CAPTION and "\u2013" not in SEC_CAPTION, "SEC caption uses hyphens, not en dashes")
check(SEC_CAPTION == "[Release No. 34-106946; File No. SR-FINRA-2026-027]", "SEC caption typography")
check(SEC_NOTICE_DATE == "November 20, 2026.", "SEC notice date typography")
check("November 18, 2026" in SEC_FILED and "(\u201cFINRA\u201d)" in SEC_FILED, "SEC filing-date typography")
check("\u2013" in FR_DOC and FR_DOC == "[FR Doc. 2026\u201323915 Filed 11\u201323\u201326; 8:45 am]", "FR Doc en-dash typography")
check(FR_RELEASE == "34\u2013106946" and FR_FILE == "SR\u2013FINRA\u20132026\u2013027", "FR release en-dash typography")
check("Eastern Time to 4:00 p.m. Eastern Time" in EXHIBIT_5_DEF, "Exhibit 5 Eastern Time written out")
check(PURPOSE_HOURS not in EXHIBIT_5_DEF, "do not tidy Exhibit 5 hours to purpose E.T. typography")
check(EXHIBIT_5_B1.endswith("unless the transaction:"), "Exhibit 5 (b)(1) ends at unless the transaction:")
check(STAND_PHRASE not in EXHIBIT_5_B1, "do not rewrite will stand and not be broken into Exhibit 5 (b)(1)")
check(OPERATIVE_DEC6 != OPERATIVE_UPON_FILING, "keep both official Commission operative phrases")
check("LULD Protected Hours" not in LIVE_B1 and "Overnight Protected Hours" not in LIVE_B1, "live rule body still Normal Market Hours")
check("SR-FINRA-2026-027" not in AMENDMENT_LINE, "live amendment line has no SR-FINRA-2026-027")
print(f"official Exhibit 5 definition typography is {EXHIBIT_5_DEF}")
print(f"official Exhibit 5 (b)(1) typography is {EXHIBIT_5_B1}")
print("official will stand and not be broken is official purpose / official Commission 2022 quotation typography, not official Exhibit 5 (b)(1)")
print("do not tidy official Exhibit 5 Eastern Time to official purpose E.T. typography")
print("do not tidy official SEC hyphen typography to official FR en-dash typography")
print("same-kind companions may be named: official IEX Release No. 34\u2013106920 / official Rule 11.270 and official TXSE Release No. 34\u2013106938 / official Rule 11.014")
print("do not claim the whole market is already uniform; do not fold this item into leftover official N7 / official FINRA 6121.02")
print(f"assertions passed: {checks}/{checks}")
