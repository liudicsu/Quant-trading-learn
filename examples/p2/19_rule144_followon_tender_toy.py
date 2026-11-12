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


print("=== H. Rule 14e-2: the subject company must state its position within 10 business days ===")
# 17 CFR 240.14e-2 (official eCFR, current as of 2026-11-09, opened 2026-11-12,
# not an interstitial). Keep sections A-G, including Rule 105, 14e-1, 101/102,
# 14e-5, and Rule 104, identical, including 29/29 after G.
# 14e-2(a): the subject company, no later than 10 business days from the date
# the tender offer is first published or sent or given, shall publish, send or
# give to security holders a statement disclosing that it recommends
# acceptance or rejection, expresses no opinion and is remaining neutral, or
# is unable to take a position, including the reason(s).
# 14e-2(b): a material change shall be published, sent, or given promptly
# (do not invent a fixed number of days for "promptly").
# This is not the 14e-1 20-business-day duration and not a 10-calendar-day
# clock. Schedule 14D-9 / Rule 14d-9 is the recommendation-statement form,
# filed as soon as practicable on the date the recommendation is first
# published; do not invent a second 10-business-day 14D-9 filing clock.
# Quote the operative 10-business-day sentence; do not silently correct the
# official prefatory typo "withing the meaning of section 14(e)".
# No bidder, target, or strategy recommendation.

print("14e-2(a): the subject company, no later than 10 business days from the date the tender offer")
print("  is first published or sent or given, shall publish, send or give to security holders a statement")
print("  disclosing that it recommends acceptance or rejection, remains neutral, or is unable to take a position,")
print("  including the reason(s)")
first_published = date(2026, 3, 2)
due_10bd = add_weekdays(first_published, 10)
print(f"offer first published {first_published}; 10th weekday (counting that date as day 1) = {due_10bd}")
check(due_10bd == date(2026, 3, 13), "14e-2 10-business-day clock from 2026-03-02 is 2026-03-13")
is_20bd_duration = False
is_10_calendar_days = False
print(f"  this is the 14e-1 20-business-day duration? {is_20bd_duration}")
print(f"  this is a 10-calendar-day clock? {is_10_calendar_days}")
check(is_20bd_duration is False, "not the 14e-1 20-business-day duration")
check(is_10_calendar_days is False, "not a 10-calendar-day clock")
print("a material change under 14e-2(b) shall be published, sent, or given promptly; this toy does not invent a fixed number of days for promptly")
print("Schedule 14D-9 is the recommendation-statement form, filed as soon as practicable on the date the recommendation is first published")
second_14d9_10bd_clock = False
print(f"  this toy invents a second 10-business-day Schedule 14D-9 filing clock? {second_14d9_10bd_clock}")
check(second_14d9_10bd_clock is False, "no second 10-business-day 14D-9 filing clock")
print("no bidder, target, or strategy recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== I. Rule 14d-11: a subsequent offering period is an election, not automatic ===")
# 17 CFR 240.14d-11 and 240.14d-7 (official eCFR, current as of 2026-11-09,
# opened 2026-11-12). Keep sections A-H identical once H is added.
# A bidder may elect a subsequent offering period of at least three business
# days only if the official (a)-(f) conditions are met, including: the initial
# offering period of at least 20 business days has expired; the offer is for
# all outstanding securities of the class; the bidder immediately accepts and
# promptly pays; results, including the approximate number and percentage of
# securities deposited to date, are announced no later than 9:00 a.m. Eastern
# time on the next business day after the expiration date of the initial
# offering period and the subsequent period begins immediately; and the same
# form and amount of consideration is offered in both periods.
# Official note: no withdrawal rights during the subsequent offering period
# (14d-7(a)(2)). Withdrawal rights do apply during the initial open period
# (14d-7(a)(1)).
# This 9:00 a.m. results clock is not the already-taught 14e-1(d)
# extension-notice clock. Do not invent a 15-business-day cap or any maximum
# the official text does not state. Cross-link the already-taught 14e-5
# same-consideration carve-out; do not rewrite it.
# No bidder or strategy recommendation.

print("a subsequent offering period under Rule 14d-11 is optional: a bidder may elect at least three business days")
print("  only if the official conditions are met")
every_tender_has_subsequent = False
print(f"  every tender offer has a subsequent offering period? {every_tender_has_subsequent}")
check(every_tender_has_subsequent is False, "subsequent period is an election, not automatic")
print("official conditions include: the initial offering period of at least 20 business days has expired;")
print("  the offer is for all outstanding securities of the class; immediate accept and prompt pay;")
print("  results announced no later than 9:00 a.m. Eastern time on the next business day after initial expiration,")
print("  and the subsequent period begins immediately; same form and amount of consideration")
initial_expires = date(2026, 3, 27)
results_by = add_weekdays(initial_expires + timedelta(days=1), 1)
print(f"initial offering period expires {initial_expires}; results due no later than 9:00 a.m. Eastern on {results_by}")
check(results_by == date(2026, 3, 30), "next business day after Friday 2026-03-27 is Monday 2026-03-30")
is_14e1d_extension_notice = False
print(f"  this 9:00 a.m. results clock is the already-taught 14e-1(d) extension-notice clock? {is_14e1d_extension_notice}")
check(is_14e1d_extension_notice is False, "14d-11 9:00 a.m. is results, not 14e-1(d) extension notice")
print("official note: no withdrawal rights during the subsequent offering period (14d-7(a)(2))")
print("withdrawal rights do apply during the initial open period (14d-7(a)(1))")
withdrawal_in_subsequent = False
withdrawal_in_initial = True
print(f"  withdrawal rights during the subsequent period? {withdrawal_in_subsequent}")
print(f"  withdrawal rights during the initial open period? {withdrawal_in_initial}")
check(withdrawal_in_subsequent is False, "no withdrawal in subsequent period")
check(withdrawal_in_initial is True, "withdrawal during the initial open period")
prints_15bd_cap = False
print(f"  this toy prints a 15-business-day cap or any official maximum the rule text does not state? {prints_15bd_cap}")
check(prints_15bd_cap is False, "do not invent a 14d-11 maximum")
print("the already-taught 14e-5 same-consideration subsequent-period carve-out stays as already printed in section F")
print("no bidder or strategy recommendation")
print(f"assertions passed: {checks}/{checks}")


print("=== J. Rule 14d-10: all-holders / best-price ===")
# 17 CFR 240.14d-10 (official eCFR API, title 17 up to date as of 2026-11-09,
# opened 2026-11-12; not an interstitial). Keep sections A-I identical,
# including Rule 105, 14e-1, 101/102, 14e-5, Rule 104, 14e-2, 14d-11, and
# 39/39 after I.
# 14d-10(a): no bidder shall make a tender offer unless (1) the tender offer
# is open to all security holders of the class of securities subject to the
# tender offer; and (2) the consideration paid to any security holder for
# securities tendered in the tender offer is the highest consideration paid
# to any other security holder for securities tendered in the tender offer.
# This is not the already-taught 14d-11 same-consideration condition or the
# 14e-5 same-consideration subsequent-period carve-out.
# Official (b)-(f) exceptions exist; this toy is not that engine.
# Do not rewrite the already-taught 14e-1(b) 10-business-day
# change-of-consideration window or the 14e-1(d) extension-notice sentence.
# No bidder, target, or strategy recommendation.

print("14d-10(a): no bidder shall make a tender offer unless:")
print("  (1) the tender offer is open to all security holders of the class of securities subject to the tender offer; and")
print("  (2) the consideration paid to any security holder for securities tendered in the tender offer")
print("      is the highest consideration paid to any other security holder for securities tendered in the tender offer")
favored_group_ok = False
unequal_price_ok = False
print(f"  offer open only to a favored group? {favored_group_ok}")
print(f"  some holders paid more than others for securities tendered? {unequal_price_ok}")
check(favored_group_ok is False, "all-holders: not open only to a favored group")
check(unequal_price_ok is False, "best-price: not a higher price to some tendering holders")
is_14d11_or_14e5_same_consideration = False
print(f"  this is the already-taught 14d-11 / 14e-5 same-consideration sentence? {is_14d11_or_14e5_same_consideration}")
check(is_14d11_or_14e5_same_consideration is False, "14d-10 is not the already-taught 14d-11 / 14e-5 same-consideration sentence")
print("official (b)-(f) exceptions exist (state-law exclusion after a good-faith effort;")
print("  more than one type of consideration with an equal right to elect;")
print("  employment-compensation safe harbor; alternative consideration when a state prohibits the offered securities;")
print("  Commission exemptive authority); this toy is not that engine")
builds_exceptions = False
print(f"  this toy builds the official (b)-(f) exception engines? {builds_exceptions}")
check(builds_exceptions is False, "do not build 14d-10(b)-(f) engines")
print("do not rewrite the already-taught 14e-1(b) 10-business-day change-of-consideration window or the 14e-1(d) extension-notice sentence")
print("no bidder, target, or strategy recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== K. Rule 14e-4: short tendering / net long in a partial tender ===")
# 17 CFR 240.14e-4 and supporting 240.14d-8 (official eCFR API, title 17
# up to date as of 2026-11-09, opened 2026-11-12). Keep sections A-J
# identical once J is added.
# 14e-4(b): it is unlawful to tender a subject security in a partial
# tender offer for one's own account unless at the time of tender, and at
# the end of the proration period or period during which securities are
# accepted by lot (including any extensions thereof), the person has a
# net long position equal to or greater than the amount tendered.
# 14e-4(a)(5): a "partial tender offer" is an offer for less than all of
# the outstanding securities subject to the offer in which tenders are
# accepted either by lot or on a pro rata basis for a specified period, or
# a tender offer for all of the outstanding shares that offers a choice of
# consideration in which tenders for different forms of consideration may
# be accepted either by lot or on a pro rata basis for a specified period.
# Do not apply the net-long limit to every tender offer.
# Supporting 14d-8: if more securities are deposited than the person is
# bound or willing to take up and pay for, they are taken up as nearly as
# may be pro rata, disregarding fractions.
# Do not invent a 14d-11 maximum, or flatten proration into already-taught
# 14d-11 election language.
# Equivalent securities and options enter the official net-long definition;
# this toy is not that engine. Do not pack 14d-8 as its own MUST.
# No bidder or strategy recommendation.

print("14e-4(b): in a partial tender offer, a person may not tender more than a net long position")
print("  at the time of tender, and at the end of the proration period or period during which")
print("  securities are accepted by lot (including any extensions thereof)")
print("  net long must be equal to or greater than the amount tendered")
applies_to_every_tender = False
print(f"  this net-long limit applies to every tender offer? {applies_to_every_tender}")
check(applies_to_every_tender is False, "14e-4 applies to a partial tender offer as defined, not every tender")
print("14e-4(a)(5): a partial tender offer is an offer for less than all of the outstanding securities")
print("  subject to the offer in which tenders are accepted either by lot or on a pro rata basis for a specified period,")
print("  or a tender offer for all of the outstanding shares that offers a choice of consideration")
print("  in which tenders for different forms of consideration may be accepted either by lot or on a pro rata basis for a specified period")
choice_branch_is_partial = True
print(f"  an all-outstanding offer with a choice of consideration accepted by lot or pro rata is a partial tender offer? {choice_branch_is_partial}")
check(choice_branch_is_partial is True, "official choice-of-consideration branch is a partial tender offer")
print("supporting 14d-8: if a greater number of securities are deposited than the person is bound or willing to take up and pay for,")
print("  the securities taken up shall be taken up and paid for as nearly as may be pro rata, disregarding fractions,")
print("  according to the number of securities deposited by each depositor during the period the offer remains open")
is_14d11_election = False
invents_14d11_max = False
print(f"  this is the already-taught 14d-11 election language? {is_14d11_election}")
print(f"  this toy invents a 14d-11 maximum length? {invents_14d11_max}")
check(is_14d11_election is False, "14d-8 proration is not 14d-11 election language")
check(invents_14d11_max is False, "do not invent a 14d-11 maximum")
print("equivalent securities and options enter the official net-long definition; this toy is not that engine")
builds_net_long_engine = False
print(f"  this toy builds the official net-long options / equivalent-securities engine? {builds_net_long_engine}")
check(builds_net_long_engine is False, "do not build the net-long engine")
print("no bidder or strategy recommendation")
print(f"assertions passed: {checks}/{checks}")


print("=== L. Rule 14e-3: disclose-or-abstain once a substantial step or commencement has occurred ===")
# 17 CFR 240.14e-3 (official eCFR API, title 17 up to date as of 2026-11-09,
# opened 2026-11-12; not an interstitial). Keep sections A-K identical,
# including Rule 105, 14e-1, 101/102, 14e-5, Rule 104, 14e-2, 14d-11,
# 14d-10, 14e-4, and 48/48 after K.
# 14e-3(a): if any person has taken a substantial step or steps to commence,
# or has commenced, a tender offer, it is a fraudulent, deceptive or
# manipulative act or practice for any other person who is in possession of
# material information relating to such tender offer which he knows or has
# reason to know is nonpublic and which he knows or has reason to know has
# been acquired directly or indirectly from the offering person, the issuer,
# or any officer, director, partner or employee or any other person acting
# on behalf of the offering person or such issuer, to purchase or sell or
# cause to be purchased or sold those securities (or convertibles, options,
# or rights) unless within a reasonable time prior to any purchase or sale
# such information and its source are publicly disclosed by press release
# or otherwise.
# This is not already-taught 14e-2 or 10b5-1. Official (b) entity procedures
# / information-barrier defense, (c) offering-person purchase and
# sale-to-offering-person exceptions, and (d) anti-tipping exist; this toy
# is not that engine. Do not invent a fixed number of days for "a reasonable
# time." Official typographical artifact in 14e-3(c): "Notwithstanding
# anything in paragraph (a) of this section to contrary" — quote it; do not
# silently correct "to contrary." No bidder, target, or strategy
# recommendation.

print("14e-3(a): if any person has taken a substantial step or steps to commence, or has commenced, a tender offer,")
print("  it is a fraudulent, deceptive or manipulative act or practice for any other person who is in possession of")
print("  material information relating to such tender offer which he knows or has reason to know is nonpublic")
print("  and which he knows or has reason to know has been acquired directly or indirectly from")
print("  the offering person, the issuer, or any officer, director, partner or employee")
print("  or any other person acting on behalf of the offering person or such issuer,")
print("  to purchase or sell or cause to be purchased or sold those securities (or convertibles, options, or rights)")
print("  unless within a reasonable time prior to any purchase or sale such information and its source")
print("  are publicly disclosed by press release or otherwise")
is_14e2_or_10b51 = False
print(f"  this is already-taught 14e-2 or 10b5-1? {is_14e2_or_10b51}")
check(is_14e2_or_10b51 is False, "14e-3 is not already-taught 14e-2 or 10b5-1")
print("official (b) entity procedures / information-barrier defense, (c) offering-person purchase")
print("  and sale-to-offering-person exceptions, and (d) anti-tipping exist; this toy is not that engine")
builds_14e3_engines = False
print(f"  this toy builds the official (b)-(d) engines? {builds_14e3_engines}")
check(builds_14e3_engines is False, "do not build 14e-3(b)-(d) engines")
invents_reasonable_time_days = False
print(f'  this toy invents a fixed number of days for "a reasonable time"? {invents_reasonable_time_days}')
check(invents_reasonable_time_days is False, "do not invent a fixed number of days for a reasonable time")
print('official typographical artifact in 14e-3(c): "Notwithstanding anything in paragraph (a) of this section to contrary"')
silently_corrects_to_contrary = False
print(f'  this toy silently corrects "to contrary"? {silently_corrects_to_contrary}')
check(silently_corrects_to_contrary is False, "do not silently correct 14e-3(c) to contrary")
print("no bidder, target, or strategy recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== M. Rule 14d-2: commencement at 12:01 a.m. on the date the means to tender is first given ===")
# 17 CFR 240.14d-2 Commencement of a tender offer (official eCFR API,
# title 17 up to date as of 2026-11-09, plus official-page fetch opened
# 2026-11-12; not an interstitial). Keep sections A-L identical,
# including Rule 105, 14e-1, 101/102, 14e-5, Rule 104, 14e-2, 14d-11,
# 14d-10, 14e-4, 14e-3, and 52/52 after L.
# 14d-2(a): A bidder will have commenced its tender offer for purposes
# of section 14(d) of the Act (15 U.S.C. 78n) and the rules under that
# section at 12:01 a.m. on the date when the bidder has first published,
# sent or given the means to tender to security holders. For purposes of
# this section, the means to tender includes the transmittal form or a
# statement regarding how the transmittal form may be obtained.
# Official 14d-2(a) prints "12:01 a.m." with no time zone. Do not invent
# a time zone, and do not copy already-taught Rule 14d-11's "9:00 a.m.
# Eastern" onto 14d-2. A 12:01 a.m. commencement on a given date means
# that day's 09:30 open is after official commencement.
# Official (b): a communication is not commencement if it does not
# include the means to tender and all written communications relating
# to the tender offer, from and including the first public announcement,
# are filed under cover of Schedule TO no later than the date of the
# communication. Official (c): as soon as practicable on the date of
# commencement, a bidder must comply with the filing requirements of
# 14d-3(a), the dissemination requirements of 14d-4(a) or (b), and the
# disclosure requirements of 14d-6(a). This toy is not that engine, and
# is not already-taught 14e-3 or 14e-1. No bidder, target, or strategy
# recommendation.

print("14d-2(a): A bidder will have commenced its tender offer for purposes of section 14(d) of the Act")
print("  (15 U.S.C. 78n) and the rules under that section at 12:01 a.m. on the date when the bidder has first")
print("  published, sent or given the means to tender to security holders")
print("  For purposes of this section, the means to tender includes the transmittal form")
print("  or a statement regarding how the transmittal form may be obtained")
print('official 14d-2(a) prints "12:01 a.m." with no time zone')
invents_zone = False
copies_14d11_zone = False
print(f"  this toy invents a time zone? {invents_zone}")
print(f'  this toy copies 14d-11\'s "9:00 a.m. Eastern" onto 14d-2? {copies_14d11_zone}')
check(invents_zone is False, "do not invent a time zone for 14d-2")
check(copies_14d11_zone is False, "do not copy 14d-11 9:00 a.m. Eastern onto 14d-2")
print("a 12:01 a.m. commencement on a given date means that day's 09:30 open is after official commencement")
print("a pre-commencement communication that does not include the means to tender")
print("  and is filed on Schedule TO is not commencement")
print("official (c) 14d-3 / 14d-4 / 14d-6 obligations exist; this toy is not that engine")
builds_14d2_engines = False
is_14e3_or_14e1 = False
print(f"  this toy builds a 14d-3 / 14d-4 / 14d-6 or Schedule TO engine? {builds_14d2_engines}")
print(f"  this is already-taught 14e-3 or 14e-1? {is_14e3_or_14e1}")
check(builds_14d2_engines is False, "do not build 14d-3/14d-4/14d-6 or Schedule TO engines")
check(is_14e3_or_14e1 is False, "14d-2 is not already-taught 14e-3 or 14e-1")
print("no bidder, target, or strategy recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== N. Rule 10b-9: all-or-none / contingency-offering representations ===")
# 17 CFR 240.10b-9 Prohibited representations in connection with certain
# offerings (official eCFR API, title 17 up to date as of 2026-11-09;
# official-page fetch opened 2026-11-12; [27 FR 9943, Oct. 10, 1962]).
# Keep sections A-M identical, including Rule 105, 14e-1, 101/102, 14e-5,
# Rule 104, 14e-2, 14d-11, 14d-10, 14e-4, 14e-3, 14d-2, and 56/56 after M.
# 10b-9(a): It shall constitute a "manipulative or deception device or
# contrivance," as used in section 10(b) of the Act, for any person,
# directly or indirectly, in connection with the offer or sale of any
# security, to make any representation: (1) to the effect that the
# security is being offered or sold on an "all-or-none" basis, unless the
# official refund conditions in (a)(1) are met; or (2) to the effect that
# the security is being offered or sold on any other basis whereby all or
# part of the consideration paid will be refunded if all or some of the
# securities are not sold, unless the official refund conditions in
# (a)(2) are met.
# Official typographical artifact in (a): "manipulative or deception
# device or contrivance" — quote it; do not silently correct it.
# Official (b): This rule shall not apply to any offer or sale of
# securities as to which the seller has a firm commitment from
# underwriters or others (subject only to customary conditions precedent,
# including "market outs") for the purchase of all the securities being
# offered. This toy is not that engine. Do not invent a clock, a form, or
# a percentage. This is not already-taught Rule 144, Regulation M, or
# Rule 14e-1. No offering, underwriter, or strategy recommendation.

print('10b-9(a): It shall constitute a "manipulative or deception device or contrivance," as used in section 10(b) of the Act,')
print("  for any person, directly or indirectly, in connection with the offer or sale of any security, to make any representation:")
print('  (1) that the security is being offered or sold on an "all-or-none" basis, unless the official refund conditions in (a)(1) are met; or')
print("  (2) that the security is being offered or sold on any other refund-if-not-sold basis, unless the official refund conditions in (a)(2) are met")
print('official typographical artifact: "manipulative or deception device or contrivance"')
silently_corrects_deception = False
print(f'  this toy silently corrects "deception device"? {silently_corrects_deception}')
check(silently_corrects_deception is False, "do not silently correct 10b-9 typographical artifact")
print('10b-9(b): This rule shall not apply to any offer or sale of securities as to which the seller has a firm commitment')
print('  from underwriters or others (subject only to customary conditions precedent, including "market outs")')
print("  for the purchase of all the securities being offered")
print("  official (b) firm-commitment exception exists; this toy is not that engine")
builds_10b9b = False
print(f"  this toy builds a market-out or firm-commitment engine? {builds_10b9b}")
check(builds_10b9b is False, "do not build a 10b-9(b) engine")
invents_clock_form_pct = False
print(f"  this toy invents a clock, a form, or a percentage? {invents_clock_form_pct}")
check(invents_clock_form_pct is False, "do not invent a clock, form, or percentage")
is_144_or_regm = False
print(f"  this is already-taught Rule 144 or Regulation M? {is_144_or_regm}")
check(is_144_or_regm is False, "10b-9 is not already-taught Rule 144 or Regulation M")
print("no offering, underwriter, or strategy recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== O. Rule 14d-3: Schedule TO filing and transmittal on the date of commencement ===")
# 17 CFR 240.14d-3 Filing and transmission of tender offer statement
# (official eCFR API, title 17 up_to_date_as_of 2026-11-09;
# official-page fetch and matching LII opened 2026-11-12).
# Keep sections A-N identical, including 14d-2, 56/56 after M, 10b-9,
# and 60/60 after N.
# 14d-3(a): No bidder shall make a tender offer if, after consummation
# thereof, such bidder would be the beneficial owner of more than 5 percent
# of the class of the subject company's securities for which the tender
# offer is made, unless as soon as practicable on the date of the
# commencement of the tender offer such bidder: official (a)(1) files
# Schedule TO, official (a)(2) delivers a copy as officially provided,
# and official (a)(3) gives telephonic notice and mails Schedule TO,
# "which telephonic notice shall be made when practicable before the
# opening of each such exchange," and the still-printed NASD / NASDAQ
# clause quoted as written. Official typography in the eCFR API uses
# typographic quotation marks around NASD.
# Official (b) requires an amendment reporting promptly any material
# changes and a final amendment reporting promptly the results. Official
# (c) certain-announcements paragraph exists. Name them; do not build
# the amendment / 14d-6(d)(2) engine, and do not pack 14d-4 or 14d-6 as
# this item. This is not a substitute for already-taught 14d-2. Do not
# invent a clock or a time zone beyond "as soon as practicable on the
# date of the commencement" and "when practicable before the opening."
# Do not silently modernize the still-printed NASD / NASDAQ names.
# No bidder, offer, or strategy recommendation.

print("14d-3(a): No bidder shall make a tender offer if, after consummation thereof, such bidder would be")
print("  the beneficial owner of more than 5 percent of the class of the subject company's securities")
print("  for which the tender offer is made, unless as soon as practicable on the date of the commencement")
print("  of the tender offer such bidder:")
print("  (1) Files with the Commission a Tender Offer Statement on Schedule TO (§ 240.14d-100), including all exhibits thereto")
print("  (2) Delivers a copy of such Schedule TO as officially provided")
print('  (3) Gives telephonic notice, "which telephonic notice shall be made when practicable before the opening of each such exchange"')
print(f"  (ii) To the National Association of Securities Dealers, Inc. (“NASD”) if such class of the subject company's securities is authorized for quotation in the NASDAQ interdealer quotation system.")
print("official (b) requires an amendment reporting promptly any material changes and a final amendment")
print("  reporting promptly the results; this toy is not that engine")
print("official (c) certain-announcements paragraph exists; this toy is not that engine")
is_sub_14d2 = False
print(f"  this is a substitute for already-taught 14d-2? {is_sub_14d2}")
check(is_sub_14d2 is False, "14d-3 is not a substitute for already-taught 14d-2")
invents_clock = False
print(f'  this toy invents a clock or a time zone beyond "as soon as practicable on the date of the commencement" and "when practicable before the opening"? {invents_clock}')
check(invents_clock is False, "do not invent a clock or zone beyond the official phrases")
modernizes_nasd = False
print(f"  this toy silently modernizes the still-printed NASD / NASDAQ names? {modernizes_nasd}")
check(modernizes_nasd is False, "quote the still-printed NASD / NASDAQ clause as written")
print("no bidder, offer, or strategy recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== P. Rule 13e-1: issuer purchases of its equity during a third-party tender offer ===")
# 17 CFR 240.13e-1 Purchase of securities by the issuer during a
# third-party tender offer (official eCFR API, title 17
# up_to_date_as_of 2026-11-09; official-page fetch and matching LII
# opened 2026-11-12). Keep all earlier prints, including 60/60 after N
# and the new 14d-3 section, identical once 14d-3 is added.
# Official core: An issuer that has received notice that it is the
# subject of a tender offer made under Section 14(d)(1) of the Act
# (15 U.S.C. 78n), that has commenced under § 240.14d-2 must not
# purchase any of its equity securities during the tender offer unless
# the issuer first: (a) files a statement containing the official
# (a)(1)-(7) information, (b) pays the fee required by § 240.0-11,
# and (c) submits the official (a)(7) exhibit.
# The official core text requires "a statement," not a named form; do
# not invent a form number, and do not flatten this into Schedule 13E-3
# or Rule 13e-3. Official citation is § 240.13e-1 (a WebFetch
# "§ 240.13 e-1" space is not official typography).
# Official (d): This section does not apply to periodic repurchases in
# connection with an employee benefit plan or other similar plan of the
# issuer so long as the purchases are made in the ordinary course and
# not in response to the tender offer.
# Name official (a)(7) fee tables / (b) / (c); do not build the
# fee-table or Rule 0-11 engine. Do not flatten 13e-1 into
# already-taught 14e-5 or 14d-2. No issuer, offer, or strategy
# recommendation.

print("13e-1: An issuer that has received notice that it is the subject of a tender offer made under Section 14(d)(1)")
print("  of the Act (15 U.S.C. 78n), that has commenced under § 240.14d-2 must not purchase any of its equity")
print("  securities during the tender offer unless the issuer first:")
print("  (a) Files a statement with the Commission containing the official (a)(1)-(7) information")
print("  (b) Pays the fee required by § 240.0-11")
print("  (c) Submits the official (a)(7) exhibit")
print("official citation is § 240.13e-1")
print("official (d): This section does not apply to periodic repurchases in connection with an employee benefit plan")
print("  or other similar plan of the issuer so long as the purchases are made in the ordinary course")
print("  and not in response to the tender offer")
print('the official core text requires "a statement," not a named form; this toy invents no form number')
print("official (a)(7) fee tables / (b) / (c) exist; this toy is not the fee-table or Rule 0-11 engine")
is_14e5_or_14d2 = False
print(f"  this is already-taught 14e-5 or 14d-2? {is_14e5_or_14d2}")
check(is_14e5_or_14d2 is False, "13e-1 is not already-taught 14e-5 or 14d-2")
is_13e3 = False
print(f"  this is Schedule 13E-3 or Rule 13e-3? {is_13e3}")
check(is_13e3 is False, "do not flatten 13e-1 into Schedule 13E-3 or Rule 13e-3")
invents_form = False
print(f"  this toy invents a form number? {invents_form}")
check(invents_form is False, "do not invent a form number for 13e-1")
print("no issuer, offer, or strategy recommendation")
print(f"assertions passed: {checks}/{checks}")
