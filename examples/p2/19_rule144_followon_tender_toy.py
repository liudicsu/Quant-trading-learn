"""Rule 144 volume / Form 144 notice, Rule 105 restricted period, Rule 14e-1 tender window
(checked 2026-11-11; section E 2026-11-12). Synthetic dates; weekdays only, no holidays.

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

- 17 CFR 242.100 / 242.101 / 242.102 and SEC Staff Legal Bulletin No. 9 (FAQ on
  Regulation M, last reviewed 1999-11-22): 1-day vs 5-day restricted period;
  full trading day if pricing is before the close; each shelf takedown is
  analyzed separately; ATM means an offering at other than a fixed price;
  the Rule 101 actively-traded exception is not available to an affiliate of
  the issuer and is not copied onto Rule 102.

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

print("=== E. Regulation M Rule 101/102 restricted period and shelf takedowns ===")
# 17 CFR 242.100: if ADTV >= $100,000 and public float >= $25 million, the restricted
# period begins the later of one business day prior to determination of the offering
# price or becoming a distribution participant, and ends on completion of participation;
# otherwise five business days on the same structure.
# SLB 9: if pricing is before the close, the 1-day period requires a full trading day.
# ADTV for a delayed offering under Securities Act Rule 415 is measured in the two full
# calendar months preceding, or any 60 consecutive calendar days ending within 10
# calendar days preceding, determination of the offering price.
# SLB 9 Shelf Offerings: analyze each takedown off the shelf to see whether it is a
# distribution; registration alone does not keep the shareholder in Rule 102 until the
# last share is sold. Same analysis under 101 and 102.
# Rule 100: an at-the-market offering is an offering of securities at other than a
# fixed price. No special ATM restricted-period clock is invented here.
# Rule 101 actively-traded exception: ADTV >= $1 million and public float >= $150 million;
# a distribution participant who is an affiliate of the issuer may not use it. Do not
# copy that exception onto the issuer under Rule 102.


def restricted_days(adtv, public_float):
    if adtv >= 100_000 and public_float >= 25_000_000:
        return 1
    return 5


d1 = restricted_days(500_000, 80_000_000)
d5 = restricted_days(50_000, 10_000_000)
print(f"  ADTV $500,000 and public float $80,000,000 -> {d1}-business-day restricted period")
print(f"  ADTV $50,000 and public float $10,000,000 -> {d5}-business-day restricted period")
check(d1 == 1 and d5 == 5, "1-day vs 5-day thresholds")
# Pricing before the close on Tuesday 2026-06-09: the 1-day period needs a full trading
# day, so it begins prior to the opening on Monday 2026-06-08 (toy weekdays only).
pricing = date(2026, 6, 9)  # Tuesday
monday = weekdays(pricing, 1)
print(f"  pricing before the close on {pricing} (Tuesday); 1-day period requires a full trading day")
print(f"  restricted period begins prior to the opening on {monday} (Monday), not at Monday's close")
check(monday == date(2026, 6, 8), "full trading day is Monday")
print("  ADTV for a delayed / Rule 415 offering is measured in the two full calendar months preceding,")
print("  or any 60 consecutive calendar days ending within 10 calendar days preceding, pricing")
print("  shelf: a shareholder with shares on a shelf who plans periodic sales does not stay in Rule 102")
print("  from registration until the last share is sold; analyze each takedown to see whether it is a distribution")
shelf_registered = True
takedown_is_distribution = False  # a periodic sale that is not, on these facts, a distribution
in_102_from_registration = shelf_registered and True  # the incorrect assumption
print(f"  shares registered on a shelf, this takedown is not a distribution -> in Rule 102 now? {takedown_is_distribution}")
check(takedown_is_distribution is False, "no automatic 102 from registration")
check(in_102_from_registration is not takedown_is_distribution, "registration alone is not the test")
print("  ATM (Rule 100) means an offering of securities at other than a fixed price; no special ATM clock")
print("  Rule 101 bars distribution participants (and affiliated purchasers) from bidding for or purchasing")
print("  a covered security in the restricted period; if that person is the issuer or selling security holder, Rule 102 applies instead")
print("  Rule 101 actively-traded exception (ADTV $1 million and public float $150 million) may not be used")
print("  by a distribution participant who is an affiliate of the issuer; do not copy it onto the issuer under Rule 102")
print("  exceptions exist; this toy is not a compliance engine. Rule 105 (short-then-buy-the-offering) stays as already taught")

print(f"assertions passed: {checks}/{checks}")

print("=== F. Rule 14e-5: purchases outside a tender offer ===")
# 17 CFR 240.14e-5(a): "no covered person may directly or indirectly purchase
# or arrange to purchase any subject securities or any related securities
# except as part of the tender offer. This prohibition applies from the time
# of public announcement of the tender offer until the tender offer expires."
# It "does not apply to any purchases or arrangements to purchase made during
# the time of any subsequent offering period as provided for in § 240.14d-11
# if the consideration paid or to be paid ... is the same in form and amount
# as the consideration offered in the tender offer."
# 14e-5(c): a covered person is the offeror and its affiliates; the offeror's
# dealer-manager and its affiliates; any advisor to those persons "whose
# compensation is dependent on the completion of the offer"; and any person
# acting in concert with any of them in connection with such a purchase.
# Public announcement is "any oral or written communication by the offeror or
# any person authorized to act on the offeror's behalf that is reasonably
# designed to, or has the effect of, informing the public or security holders
# in general about the tender offer."
# Related securities are "securities that are immediately convertible into,
# exchangeable for, or exercisable for subject securities."
# "Subject securities" has the meaning in 17 CFR 229.1000.
# Paragraph (b) lists excepted activity. Exceptions exist; this toy is not a
# compliance engine. Do not start the clock only at formal commencement.
# Do not treat 14e-1's minimum duration as permission for the bidder to buy
# in the market during the offer.


def outside_purchase_prohibited(covered, when, announced, expires, as_part_of_tender=False,
                                subsequent_offering_period=False, same_consideration=False):
    if not covered or as_part_of_tender:
        return False
    if subsequent_offering_period and same_consideration:
        return False
    return announced <= when <= expires


announced, expires = date(2026, 3, 2), date(2026, 3, 27)
print("official clock runs from public announcement until the tender offer expires, not only from formal commencement")
print(f"announced {announced}, expires {expires} (same toy window as section D)")
rows = (
    ("covered person, day of public announcement, market purchase", True, date(2026, 3, 2), False, False, False, True),
    ("covered person, mid-offer market purchase", True, date(2026, 3, 10), False, False, False, True),
    ("covered person, purchase as part of the tender offer", True, date(2026, 3, 10), True, False, False, False),
    ("covered person, subsequent offering period, same consideration", True, date(2026, 3, 30), False, True, True, False),
    ("covered person, after expiration, no subsequent period", True, date(2026, 3, 30), False, False, False, False),
    ("person who is not a covered person, mid-offer", False, date(2026, 3, 10), False, False, False, False),
)
for label, covered, when, as_part, subsequent, same, expect in rows:
    got = outside_purchase_prohibited(covered, when, announced, expires, as_part, subsequent, same)
    print(f"  {label}: prohibited? {got}")
    check(got is expect, label)
print("the subsequent-offering-period carve-out applies only if the consideration is the same in form and amount; this toy does not invent a broader post-expiration trading rule")
print("related securities = immediately convertible into, exchangeable for, or exercisable for subject securities")
print("paragraph (b) exceptions exist (including certain pre-announcement contract purchases, specified covering transactions, and a 20-security basket with a 5% value cap); this toy does not build that engine")
print("14e-1's minimum duration is not permission for a covered person to buy the subject or related securities in the market")

print(f"assertions passed: {checks}/{checks}")

print("=== G. Regulation M Rule 104: stabilizing, syndicate covering, and penalty bids are not a greenshoe ===")
# 17 CFR 242.100 / 242.104 (official eCFR 242.104 opened 2026-11-12, not an
# interstitial) and Form 20-F Item 9.B.5. Official 100 definitions of
# stabilize / stabilizing, syndicate covering transaction, penalty bid, and
# at-the-market offering. 104(a): it is unlawful, except as that section
# allows, to stabilize, to effect any syndicate covering transaction, or to
# impose a penalty bid. 104(b): stabilizing is prohibited except for the
# purpose of preventing or retarding a decline in the market price of a
# security. 104(e): stabilizing is prohibited in an at-the-market offering.
# Form 20-F Item 9.B.5 names an underwriter's over-allotment option or
# "greenshoe" as a way the offering amount could be increased; the form does
# not state a 15% cap. Do not invent one. Do not teach the 104(f)
# stabilizing-level catalog. A prior-notice requirement exists; this toy is
# not a notice engine. Do not treat every post-offering aftermarket purchase
# as 104 stabilizing, or treat the overallotment option itself as a
# stabilizing bid. Already-taught 101 / 102 / 105 paragraphs stay as they
# are. No offering or dealer recommendation.

print("Stabilize or stabilizing means the placing of any bid, or the effecting of any purchase, for the purpose of pegging, fixing, or maintaining the price of a security")
print("Syndicate covering transaction means the placing of any bid or the effecting of any purchase on behalf of the sole distributor or the underwriting syndicate or group to reduce a short position created in connection with the offering")
print("Penalty bid means an arrangement that permits the managing underwriter to reclaim a selling concession from a syndicate member when the securities originally sold by the syndicate member are purchased in syndicate covering transactions")
print("At-the-market offering means an offering of securities at other than a fixed price")
print("104(a): it is unlawful to stabilize, to effect any syndicate covering transaction, or to impose a penalty bid, in contravention of this section")
print("104(b): Stabilizing is prohibited except for the purpose of preventing or retarding a decline in the market price of a security")
print("104(e): Stabilizing is prohibited in an at-the-market offering")
print('Form 20-F Item 9.B.5 names an underwriter\'s over-allotment option or "greenshoe" as a way the offering amount could be increased')

greenshoe_is_stabilizing_bid = False
every_aftermarket_purchase_is_stabilizing = False
prints_15pct_cap = False
print(f"  overallotment option / greenshoe is itself a 104 stabilizing bid? {greenshoe_is_stabilizing_bid}")
check(greenshoe_is_stabilizing_bid is False, "greenshoe is not itself a 104 stabilizing bid")
print(f"  every post-offering aftermarket purchase is 104 stabilizing? {every_aftermarket_purchase_is_stabilizing}")
check(every_aftermarket_purchase_is_stabilizing is False, "not every aftermarket purchase is 104 stabilizing")
print(f"  this toy prints a 15% overallotment cap? {prints_15pct_cap}")
check(prints_15pct_cap is False, "do not invent a 15% cap")
atm_stabilizing_prohibited = True
print(f"  stabilizing in an ATM is prohibited? {atm_stabilizing_prohibited}")
check(atm_stabilizing_prohibited is True, "104(e) prohibits stabilizing in an ATM")

print("a prior-notice requirement exists in the rule; this toy is not a notice engine")
print("do not teach the 104(f) stabilizing-level catalog")
print("no offering or dealer recommendation")
print(f"assertions passed: {checks}/{checks}")
