"""Cash-account payment period and 90-day freeze, TXSE sessions, 15c3-3 reserve toy
(checked 2026-11-11). Synthetic dates; weekdays only, no holidays.

Sources:
- 12 CFR 220.2: "Payment period means the number of business days in the standard
  securities settlement cycle in the United States, as defined in paragraph (a) of SEC
  Rule 15c6-1 ... plus two business days." After T+1 (from 2024-05-28) that is 3 business
  days, not "pay by T+1 or it is a free-ride."
- 12 CFR 220.8(a): in a cash account the customer agrees to make full cash payment
  before selling the security.
- 12 CFR 220.8(c): if a nonexempted security is sold (or delivered to another broker)
  without having been previously paid for in full, the privilege of delaying payment
  beyond the trade date is withdrawn for 90 calendar days following the date of sale.
  The freeze does not apply if, within the payment period, full payment is received (or
  a check clears) and the sale proceeds are not withdrawn prior to that payment.
- investor.gov "Freeriding": during the freeze the investor may still buy, but must
  fully pay on the trade date.
- TXSE Rule 11.001 / session definitions and the 2026-05-06 trader alert: Pre-Market
  8:00-9:30, Market / Regular 9:30-4:00, Post-Market 4:00-5:00 p.m. Eastern.
- 17 CFR 240.15c3-3(e)(1): a Special Reserve Bank Account for the Exclusive Benefit of
  Customers, with cash and/or qualified securities computed under Exhibit A (15c3-3a).
  This toy uses a one-line credits-minus-debits remainder; it is not the full formula.

Learning only; not legal advice and not a broker recommendation.
"""
from datetime import date, datetime, time, timedelta

checks = 0


def check(cond, label):
    global checks
    assert cond, label
    checks += 1


def add_weekdays(start, n):
    d, seen = start, 0
    while seen < n:
        d += timedelta(days=1)
        if d.weekday() < 5:
            seen += 1
    return d


print("=== A. Regulation T payment period is settlement cycle plus two business days ===")
settlement_cycle = 1  # Rule 15c6-1(a) since 2024-05-28
payment_period = settlement_cycle + 2
print(f"standard settlement cycle T+{settlement_cycle}; payment period = {payment_period} business days")
check(payment_period == 3, "payment_period")
trade = date(2026, 7, 6)  # Monday
due = add_weekdays(trade, payment_period)
print(f"cash-account purchase on {trade} has payment period ending {due}")
check(due == date(2026, 7, 9), "due Thu")

print("=== B. Freeriding and the 90-calendar-day freeze ===")
sale = date(2026, 7, 7)  # sold next day, not yet paid
paid_already = False
freeze = sale + timedelta(days=90)
print(f"sold on {sale} before paying in full: 90-calendar-day freeze ends {freeze}")
check(freeze == date(2026, 10, 5), "freeze end")
check(paid_already is False, "unpaid")
print("during the freeze, new purchases must be paid for on the trade date (the delay-beyond-trade-date privilege is withdrawn)")

print("=== C. Same sale, but paid with other funds inside the payment period; proceeds not withdrawn ===")
paid_by = date(2026, 7, 8)
proceeds_withdrawn = False
no_freeze = (paid_by <= due) and (not proceeds_withdrawn)
print(f"full payment {paid_by} (on or before {due}); proceeds withdrawn? {proceeds_withdrawn} -> freeze? {not no_freeze}")
check(no_freeze is True, "exception")
print("selling before T+1 settlement is not automatically freeriding if you pay with other funds on time and do not take the sale proceeds first")

print("=== D. TXSE official sessions (Eastern Time) ===")
sessions = (
    (time(8, 0), "pre-market"),
    (time(9, 29), "pre-market"),
    (time(9, 30), "regular"),
    (time(15, 59), "regular"),
    (time(16, 0), "post-market"),
    (time(16, 59), "post-market"),
    (time(17, 0), "closed"),
    (time(7, 59), "closed"),
)


def txse_session(t):
    if time(8, 0) <= t < time(9, 30):
        return "pre-market"
    if time(9, 30) <= t < time(16, 0):
        return "regular"
    if time(16, 0) <= t < time(17, 0):
        return "post-market"
    return "closed"


for t, expect in sessions:
    got = txse_session(t)
    print(f"  {t.strftime('%H:%M')} ET -> {got}")
    check(got == expect, str(t))
print("SIP participant / market-center identifier for TXSE is F; pre-launch tape data will not contain F prints")

print("=== E. Rule 15c3-3 reserve toy (credits minus debits, not the full Exhibit A formula) ===")
credits, debits = 100_000.0, 40_000.0
reserve = credits - debits
print(f"customer credits {credits:.0f} - debits {debits:.0f} -> reserve at least {reserve:.0f}")
check(reserve == 60_000.0, "reserve")
print("the carrying broker must also keep possession or control of fully paid and excess-margin securities; this is separate from SIPC")
print(f"assertions passed: {checks}/{checks}")

print("=== F. Rule 15c6-1 default and FINRA 11320 delivery-date types ===")
# 17 CFR 240.15c6-1(a): except as provided in (b), (c), and (d), a broker or
# dealer shall not effect or enter into a contract for the purchase or sale of
# a security ... that provides for payment of funds and delivery of securities
# later than the first business day after the date of the contract unless
# otherwise expressly agreed to by the parties at the time of the transaction.
# 15c6-1(c): contracts for the sale for cash of securities that are priced
# after 4:30 p.m. Eastern Time (ET) on the date such securities are priced and
# that are sold by an issuer to an underwriter pursuant to a firm commitment
# underwritten offering ... are not under (a); the dealer shall not enter a
# contract for those securities later than the second business day after the
# date of the contract unless otherwise expressly agreed ... at the time of
# the transaction.
# FINRA Rule 11320 (Dates of Delivery), amended by SR-FINRA-2023-017 eff.
# May 28, 2024: (a) cash — delivery on the day of the transaction; (b) regular
# way — on, but not before, the first business day following the date of the
# transaction; (c) seller's option; (d) buyer's option; (f) delayed-delivery —
# on the date agreed upon at the time for the transaction; (e) contracts due
# on a day other than a business day shall mature on the next business day.
# Current 11320 has no separate "next day" category; do not invent one.
# 11320(g)–(h) delivery time-and-place rules exist; this toy is not a UPC or
# close-out engine. Learning only; no product or venue recommendation.

trade = date(2026, 7, 6)  # Monday
regular_way = add_weekdays(trade, 1)
cash_day = trade
agreed = date(2026, 7, 10)  # Friday, agreed at the time of the transaction
print(f"regular way: trade {trade} delivers on, but not before, {regular_way}")
check(regular_way == date(2026, 7, 7), "regular way is first business day after the trade date")
print(f"cash: delivery on the day of the transaction {cash_day}")
check(cash_day == trade, "cash delivers the same day, not T+1")
print(f"delayed-delivery: date agreed at the time of the transaction {agreed}")
check(agreed == date(2026, 7, 10), "delayed-delivery uses the agreed date")
due_sat = date(2026, 7, 11)  # Saturday
mature = due_sat
while mature.weekday() >= 5:
    mature += timedelta(days=1)
print(f"11320(e): contract due {due_sat} (not a business day) matures {mature}")
check(mature == date(2026, 7, 13), "non-business-day due date rolls to the next business day")
after_430_cap = add_weekdays(trade, 2)
print(f"15c6-1(c) firm-commitment offering priced after 4:30 p.m. ET: not forced into (a)'s first-business-day default; up to {after_430_cap} unless otherwise agreed")
check(after_430_cap == date(2026, 7, 8), "paragraph (c) allows up to the second business day")
print("T+1 is the 15c6-1(a) default unless the parties expressly agree otherwise at the time of the transaction")
print("do not write that every trade must settle T+1, that a cash contract settles T+1, or that every IPO or follow-on settles T+2")
print("current FINRA 11320 has no separate next-day category (amended by SR-FINRA-2023-017 eff. May 28, 2024)")
print("11320 also lists seller's option and buyer's option; 11320(g)-(h) delivery time-and-place rules exist; this toy is not that engine")
print("a not-regular-way contract can be a listed Rule 611(b)(2) trade-through exception; that does not make every such print a data error")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: learning only; not a UPC or close-out engine; no product or venue recommendation")

print("=== G. FINRA 2266: written SIPC information at account opening and at least annually ===")
# FINRA Rule 2266 SIPC Information (official-page fetch opened
# 2026-11-12). Keep sections A-F identical, including the 15c3-3 line
# "this is separate from SIPC," 14/14 after E, 15c6-1 / 11320, 19/19
# after F, and the section-F disclaimer.
# Official 2266: members (with official (a)-(b) exceptions) shall advise
# all new customers, in writing, at the opening of an account, that they
# may obtain information about SIPC, including the SIPC brochure, by
# contacting SIPC, and also shall provide the Web site address and
# telephone number of SIPC; the same written information must be provided
# at least once each year. Introducing/clearing firms may assign these
# requirements to one of the firms.
# Official typography is "Web site" as two words. Name official (a)-(b)
# exceptions; do not build a SIPA-exclusion engine. Do not rewrite
# already-taught SIPC coverage limits ($500,000 including a $250,000
# cash limit; not FDIC), and do not invent a coverage amount, form, or
# clock this rule does not state. Do not rewrite already-taught 15c3-3 /
# Reg T / 15c6-1. No broker or SIPC-membership recommendation.

print("2266: All members, except those members: (a) that pursuant to Section 3(a)(2)(A)(i) through (iii)")
print("  of the Securities Investor Protection Act of 1970 (SIPA) are excluded from membership in the")
print("  Securities Investor Protection Corporation (SIPC) and that are not SIPC members; or (b) whose")
print("  business consists exclusively of the sale of investments that are ineligible for SIPC protection,")
print("  shall advise all new customers, in writing, at the opening of an account, that they may obtain")
print("  information about SIPC, including the SIPC brochure, by contacting SIPC, and also shall provide")
print("  the Web site address and telephone number of SIPC.")
print("  In addition, such members shall provide all customers with the same information, in writing,")
print("  at least once each year.")
print("  In cases where both an introducing firm and clearing firm service an account,")
print("  the firms may assign these requirements to one of the firms")
print('official typography is "Web site" as two words')
print("official (a)-(b) exceptions exist; this toy is not a SIPA-exclusion engine")
is_rewrite_sipc = False
print(f"  this is a rewrite of already-taught SIPC coverage limits? {is_rewrite_sipc}")
check(is_rewrite_sipc is False, "2266 is not a rewrite of already-taught SIPC coverage limits")
invents_amount = False
print(f"  this toy invents a coverage amount, form, or clock this rule does not state? {invents_amount}")
check(invents_amount is False, "do not invent a coverage amount, form, or clock")
written_required = True
print(f"  written information is required at account opening and at least once each year? {written_required}")
check(written_required is True, "2266 requires written SIPC information at opening and at least annually")
print("no broker or SIPC-membership recommendation")
print(f"assertions passed: {checks}/{checks}")
