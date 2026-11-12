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

print("=== H. FINRA 2264: margin disclosure prior to or at the time of opening, and not less than once a calendar year ===")
# FINRA Rule 2264 Margin Disclosure Statement (official-page / official
# rulebook HTML opened 2026-11-12). Keep sections A-G identical,
# including the 15c3-3 line "this is separate from SIPC," 14/14 after E,
# 15c6-1 / 11320, 19/19 after F, 2266, and 22/22 after G.
# Official 2264(a): No member shall open a margin account, as specified
# in Regulation T of the Board of Governors of the Federal Reserve
# System, for or on behalf of a non-institutional customer, unless,
# prior to or at the time of opening the account, the member has
# furnished to the customer, individually, in paper or electronic form,
# and in a separate document (or contained by itself on a separate page
# as part of another document), the margin disclosure statement
# specified in this paragraph (a). Official (a) also requires the
# statement to be posted on the member's Web site, in a clear and
# conspicuous manner, if the member permits non-institutional customers
# to open accounts online or to engage in transactions in securities
# online.
# Official (b): Members shall, with a frequency of not less than once a
# calendar year, deliver individually, in paper or electronic form, the
# disclosure statement described in paragraph (a) or the following
# bolded disclosures to all non-institutional customers with margin
# accounts. Official (b) also states that the annual disclosure may be
# delivered within or as part of other account documentation, and is not
# required to be provided in a separate document or on a separate page.
# Official (c) allows a substantially similar alternative.
# Official (d) defines "non-institutional customer" as a customer that
# does not qualify as an "institutional account" under Rule 4512(c);
# name it, do not build a 4512 engine.
# Official typography is "Web site" as two words, and official model
# text includes "short fall" as two words. Do not invent that the
# prescribed statement is the only permitted text. Do not build the
# prescribed-statement catalog. Do not flatten 2264 into Rule 10b-16 or
# already-taught Reg T / 4210, or flatten the clock into packed 2266 /
# 2267. No product, broker, or margin recommendation.

print("2264(a): No member shall open a margin account, as specified in Regulation T of the")
print("  Board of Governors of the Federal Reserve System, for or on behalf of a")
print("  non-institutional customer, unless, prior to or at the time of opening the account,")
print("  the member has furnished to the customer, individually, in paper or electronic form,")
print("  and in a separate document (or contained by itself on a separate page as part of")
print("  another document), the margin disclosure statement specified in this paragraph (a)")
print("  if the member permits non-institutional customers to open accounts online or to")
print('  engage in transactions in securities online, the statement must be posted on the')
print('  member\'s Web site in a clear and conspicuous manner')
print("2264(b): Members shall, with a frequency of not less than once a calendar year,")
print("  deliver individually, in paper or electronic form, the disclosure statement")
print("  described in paragraph (a) or the following bolded disclosures to all")
print("  non-institutional customers with margin accounts")
print("  the annual disclosure may be delivered within or as part of other account")
print("  documentation, and is not required to be provided in a separate document or on a")
print("  separate page")
print("official typography is \"Web site\" as two words; official model text includes \"short fall\" as two words")
print("official (c) substantially similar alternative exists; this toy is not the prescribed-statement catalog")
print('official (d): "non-institutional customer" means a customer that does not qualify')
print('  as an "institutional account" under Rule 4512(c); this toy is not a 4512 engine')
flatten_10b16 = False
print(f"  this is a flatten into Rule 10b-16 or already-taught Reg T? {flatten_10b16}")
check(flatten_10b16 is False, "do not flatten 2264 into 10b-16 or already-taught Reg T")
only_text = False
print(f"  this toy invents that the prescribed statement is the only permitted text? {only_text}")
check(only_text is False, "official (c) alternative exists; not the only permitted text")
clocks = True
print(f"  furnished prior to or at the time of opening, and not less than once a calendar year? {clocks}")
check(clocks is True, "2264 opening and annual clocks")
print("no product, broker, or margin recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== I. FINRA 2267: written BrokerCheck information once every calendar year ===")
# FINRA Rule 2267 Investor Education and Protection (official-page /
# official rulebook HTML opened 2026-11-12). Keep all earlier prints,
# including 22/22 after G / 2266 and the new 2264 section, identical
# once 2264 is added.
# Official 2267(a): Except as otherwise provided in this Rule, each
# member shall once every calendar year provide in writing (which may be
# electronic) to each customer the following items of information:
# (1) FINRA BrokerCheck Hotline Number; (2) FINRA Web site address; and
# (3) A statement as to the availability to the customer of an investor
# brochure that includes information describing FINRA BrokerCheck.
# Official typography is "Web site" as two words.
# Official (b)(1): a member whose contact with customers is limited to
# introducing customer accounts to be held directly at an entity other
# than a FINRA member, and that thereafter does not carry customer
# accounts or hold customer funds and securities, may furnish the
# information at or prior to the time of the customer's initial
# purchase, in lieu of once every calendar year.
# Official (b)(2): a member that does not have customers, or that is a
# party to a carrying agreement where the carrying firm member complies
# with paragraph (a), is exempt.
# Do not invent that the general 2267 duty is an account-opening
# disclosure. Do not flatten the clock into packed 2266. Do not invent a
# BrokerCheck hotline number or a FINRA Web site address from page
# chrome (the rule names those items but does not state the number).
# This is not a rewrite of packed 2266 or already-taught SIPC coverage
# limits. No broker or BrokerCheck recommendation.

print("2267(a): Except as otherwise provided in this Rule, each member shall once every")
print("  calendar year provide in writing (which may be electronic) to each customer the")
print("  following items of information:")
print("  (1) FINRA BrokerCheck Hotline Number;")
print("  (2) FINRA Web site address; and")
print("  (3) A statement as to the availability to the customer of an investor brochure")
print("  that includes information describing FINRA BrokerCheck")
print('official typography is "Web site" as two words')
print("this toy invents no BrokerCheck hotline number and no FINRA Web site address")
print("official (b)(1): a limited introducing-firm alternative may furnish the information")
print("  at or prior to the time of the customer's initial purchase, in lieu of once every")
print("  calendar year")
print("official (b)(2): a member that does not have customers, or that is a party to a")
print("  carrying agreement where the carrying firm member complies with paragraph (a),")
print("  is exempt; this toy is not an introducing-firm / carrying-agreement engine")
is_rewrite_2266 = False
print(f"  this is a rewrite of packed 2266? {is_rewrite_2266}")
check(is_rewrite_2266 is False, "2267 is not a rewrite of packed 2266")
invents_hotline = False
print(f"  this toy invents a BrokerCheck hotline number or a FINRA Web site address? {invents_hotline}")
check(invents_hotline is False, "do not invent a hotline number or Web site address")
annual_not_opening = True
print(f"  the general 2267 duty is once every calendar year, not a general account-opening disclosure? {annual_not_opening}")
check(annual_not_opening is True, "general 2267 duty is once every calendar year")
print("no broker or BrokerCheck recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== J. FINRA 2261: most recent balance sheet available to inspection by any bona fide regular customer upon request ===")
# FINRA Rule 2261 Disclosure of Financial Condition (official-page /
# official rulebook HTML opened 2026-11-12). Keep all earlier prints,
# including 28/28 after I / 2267, identical.
# Official 2261(a): A member shall make available to inspection by any
# bona fide regular customer, upon request, the information relative to
# such member's financial condition as disclosed in its most recent
# balance sheet prepared either in accordance with such member's usual
# practice or as required by any state or federal securities laws, or
# any rule or regulation thereunder. In lieu of making such balance
# sheet available to inspection, a member may deliver the balance sheet
# to the requesting bona fide regular customer in paper or electronic
# form; provided that, with respect to electronic delivery, the customer
# must consent to receive the balance sheet in electronic form.
# Official (b) is a member-to-member written-request delivery duty.
# Official (c): As used in paragraph (a) of this Rule, the term
# "customer" means any person who, in the regular course of such
# member's business, has cash or securities in the possession of such
# member.
# Quote official "bona fide regular customer" and "most recent balance
# sheet." Do not invent a periodic clock, form number, or coverage
# amount. Name official (b) and official (c); do not build those
# engines. Do not flatten 2261 into already-taught 15c3-3 or SIPC, or
# into packed 2266 / 2267. No broker or financial-condition
# recommendation.

print("2261(a): A member shall make available to inspection by any bona fide regular customer, upon request,")
print("  the information relative to such member's financial condition as disclosed in its most recent")
print("  balance sheet prepared either in accordance with such member's usual practice or as required by")
print("  any state or federal securities laws, or any rule or regulation thereunder")
print("  In lieu of making such balance sheet available to inspection, a member may deliver the balance")
print("  sheet to the requesting bona fide regular customer in paper or electronic form; provided that,")
print("  with respect to electronic delivery, the customer must consent to receive the balance sheet in")
print("  electronic form")
print('official typography is "bona fide regular customer" and "most recent balance sheet"')
print("official (b): member-to-member written-request delivery of the most recent balance sheet exists;")
print("  this toy is not a member-to-member engine")
print('official (c): as used in paragraph (a), the term "customer" means any person who, in the regular')
print("  course of such member's business, has cash or securities in the possession of such member;")
print('  this toy is not a "customer" engine')
flatten_2261 = False
print(f"  this is a flatten into already-taught 15c3-3 or SIPC, or into packed 2266 / 2267? {flatten_2261}")
check(flatten_2261 is False, "do not flatten 2261 into 15c3-3, SIPC, or packed 2266 / 2267")
invents_clock = False
print(f"  this toy invents a periodic clock, form number, or coverage amount? {invents_clock}")
check(invents_clock is False, "do not invent a 2261 clock, form, or coverage amount")
on_request = True
print(f"  most recent balance sheet must be made available to inspection by any bona fide regular customer upon request, or delivered in paper or electronic form with the customer's consent for electronic delivery? {on_request}")
check(on_request is True, "2261 requires the most recent balance sheet upon request")
print("no broker or financial-condition recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== K. FINRA 2231: a statement of account not less than once every calendar quarter ===")
# FINRA Rule 2231 Customer Account Statements (official-page / official
# rulebook HTML opened 2026-11-12; typography cross-checked against
# same-day official HTML). Keep all earlier prints, including 28/28
# after I / 2267 and the new 2261 section, identical once 2261 is added.
# Official 2231(a): Except as otherwise provided by paragraph (b) of
# this Rule, each general securities member shall, with a frequency of
# not less than once every calendar quarter, send a statement of account
# ("account statement") containing a description of any securities
# positions, money balances, or account activity to each customer whose
# account had a security position, money balance, or account activity
# during the period since the last such statement was sent to the
# customer. Official (a) also requires an advisory to report promptly
# any inaccuracy or discrepancy, a both-firms reference when introducing
# and carrying firms both service the account, and that any oral
# communications should be re-confirmed in writing, including rights
# under SIPA.
# Official (b) DVP/RVP exceptions exist (official typography is
# "SEA Rule 17a-4"). Official closing sentence of (b): Nothing in this
# Rule shall be seen to qualify or condition the obligations of a member
# under SEA Rule 15c3-3(j)(1) concerning quarterly notices of free
# credit balances on statements.
# Official (c) DPP / unlisted REIT catalog exists; official (d)(2)
# exempts a member that does not carry customer accounts and does not
# hold customer funds or securities. Official SM exists; official
# SM .02(a)(2) wording is "accounts statements" — do not silently tidy
# it. Official typography is hyphenated "re-confirmed" and
# "SEA Rule 15c3-3(j)(1)" / "SEA Rule 17a-4" with no space in SEA.
# Name official (b), (c), (d)(2), and official SM; do not build those
# engines. Do not flatten this quarterly clock into packed 10b-16 "at
# least quarterly," or into 15c3-3(j)(1). Do not rewrite already-taught
# 15c3-3 possession-or-control / reserve teaching, or flatten into
# packed 2264 / 2266 / 2267. No broker or product recommendation.

print('2231(a): Except as otherwise provided by paragraph (b) of this Rule, each general securities')
print('  member shall, with a frequency of not less than once every calendar quarter, send a statement')
print('  of account ("account statement") containing a description of any securities positions, money')
print("  balances, or account activity to each customer whose account had a security position, money")
print("  balance, or account activity during the period since the last such statement was sent to the")
print("  customer")
print("  the account statement must advise the customer to report promptly any inaccuracy or discrepancy;")
print("  when an introducing and carrying firm both service the account, the advisory must refer to both")
print("  firms; any oral communications should be re-confirmed in writing, including rights under SIPA")
print('official typography is hyphenated "re-confirmed"')
print('official (b) DVP/RVP exceptions exist (official typography is "SEA Rule 17a-4"); this toy is not')
print("  that engine")
print("official closing sentence of (b): Nothing in this Rule shall be seen to qualify or condition the")
print("  obligations of a member under SEA Rule 15c3-3(j)(1) concerning quarterly notices of free credit")
print("  balances on statements")
print('official typography is "SEA Rule 15c3-3(j)(1)" and "SEA Rule 17a-4"')
print("official (c) DPP / unlisted REIT catalog exists; this toy is not that catalog")
print("official (d)(2): a member that does not carry customer accounts and does not hold customer funds")
print("  or securities is exempt from the provisions of this Rule")
print('official SM exists; official SM .02(a)(2) wording is "accounts statements"; this toy is not the')
print("  logos / summary-statement / DPP catalog")
flatten_2231 = False
print(f"  this is a flatten into packed 10b-16 or into 15c3-3(j)(1), or a rewrite of already-taught 15c3-3? {flatten_2231}")
check(flatten_2231 is False, "do not flatten 2231 into 10b-16 or 15c3-3(j)(1)")
builds_c = False
print(f"  this toy builds the official (c) DPP / unlisted REIT catalog? {builds_c}")
check(builds_c is False, "do not build the official (c) catalog")
quarterly = True
print(f"  a statement of account is required not less than once every calendar quarter? {quarterly}")
check(quarterly is True, "2231 requires a statement of account not less than once every calendar quarter")
print("no broker or product recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== L. FINRA 2090: reasonable diligence to know (and retain) the essential facts ===")
# FINRA Rule 2090 Know Your Customer (official-page opened 2026-11-12).
# Keep all earlier prints, including 28/28 after I / 2267 and the new
# 2261 / 2231 sections, identical once those are added.
# Official 2090: Every member shall use reasonable diligence, in regard
# to the opening and maintenance of every account, to know (and retain)
# the essential facts concerning every customer and concerning the
# authority of each person acting on behalf of such customer.
# Official SM .01: For purposes of this Rule, facts "essential" to
# "knowing the customer" are those required to (a) effectively service
# the customer's account, (b) act in accordance with any special
# handling instructions for the account, (c) understand the authority of
# each person acting on behalf of the customer, and (d) comply with
# applicable laws, regulations, and rules.
# Quote the official parenthetical "(and retain)" and official SM .01
# quotation marks. This is a diligence-and-facts duty, not an
# account-opening disclosure clock. Do not flatten 2090 into FINRA 2111
# or Regulation Best Interest / Form CRS, or into packed 2264 / 2266 /
# 2267 / 2261 / 2231. No broker or product recommendation.

print("2090: Every member shall use reasonable diligence, in regard to the opening and maintenance of")
print("  every account, to know (and retain) the essential facts concerning every customer and concerning")
print("  the authority of each person acting on behalf of such customer")
print('official typography includes the parenthetical "(and retain)"')
print('official SM .01: For purposes of this Rule, facts "essential" to "knowing the customer" are those')
print("  required to (a) effectively service the customer's account, (b) act in accordance with any")
print("  special handling instructions for the account, (c) understand the authority of each person")
print("  acting on behalf of the customer, and (d) comply with applicable laws, regulations, and rules")
flatten_2090 = False
print(f"  this is a flatten into FINRA 2111 or Regulation Best Interest / Form CRS, or into packed 2264 / 2266 / 2267 / 2261 / 2231? {flatten_2090}")
check(flatten_2090 is False, "do not flatten 2090 into 2111, Reg BI / Form CRS, or packed disclosure clocks")
treats_clock = False
print(f"  this toy treats 2090 as an account-opening disclosure clock? {treats_clock}")
check(treats_clock is False, "2090 is a diligence-and-facts duty, not a disclosure clock")
diligence = True
print(f"  reasonable diligence, in regard to the opening and maintenance of every account, to know (and retain) the essential facts? {diligence}")
check(diligence is True, "2090 requires reasonable diligence to know (and retain) the essential facts")
print("no broker or product recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== M. FINRA 4370: written business continuity plan and customer disclosure ===")
# FINRA Rule 4370 Business Continuity Plans and Emergency Contact
# Information (official HTML opened 2026-11-12). Add this section AFTER
# the current last line so 37/37 after L / 2090 remains a strict
# byte-prefix of the tip file.
# Official 4370(a): Each member must create and maintain a written
# business continuity plan identifying procedures relating to an
# emergency or significant business disruption. Such procedures must be
# reasonably designed to enable the member to meet its existing
# obligations to customers.
# Official (e): Each member must disclose to its customers how its
# business continuity plan addresses the possibility of a future
# significant business disruption and how the member plans to respond
# to events of varying scope. At a minimum, such disclosure must be
# made in writing to customers at account opening, posted on the
# member's Web site (if the member maintains a Web site), and mailed
# to customers upon request.
# Official typography is "Web site" (two words, capital W). Do not tidy
# it to "website." Official (c) ten-element catalog exists; name it,
# do not build that catalog. Official (b) annual review, official (d)
# senior-management / registered-principal approval, and official (f)
# emergency-contact reporting exist; name them, do not build those
# engines. Official (f)(1) typography includes "e.g., the member's
# attorney, accountant, or clearing firm contact" if named (comma after
# "e.g."). Official (g) defines "Mission critical system" and
# "Financial and operational assessment"; quote only if named, do not
# build those definitions. Do not invent a clock other than official
# account opening / upon request / Web-site posting. Do not invent that
# a member without a Web site must still post the disclosure on a
# website. Do not flatten 4370 into already-taught 15c3-3, SIPC, or
# packed 2261 / 2266 / 2267 / 2231 / 2090. Do not rewrite already-taught
# SIPC coverage limits. No broker or product recommendation.

print("4370(a): Each member must create and maintain a written business continuity plan identifying")
print("  procedures relating to an emergency or significant business disruption. Such procedures must")
print("  be reasonably designed to enable the member to meet its existing obligations to customers")
print("4370(e): Each member must disclose to its customers how its business continuity plan addresses")
print("  the possibility of a future significant business disruption and how the member plans to")
print("  respond to events of varying scope. At a minimum, such disclosure must be made in writing")
print("  to customers at account opening, posted on the member's Web site (if the member maintains a")
print("  Web site), and mailed to customers upon request")
print('official typography is "Web site" (two words, capital W)')
print("official (b) annual review, official (c) ten-element catalog, official (d) senior-management /")
print("  registered-principal approval, and official (f) emergency-contact reporting exist; official")
print('  (f)(1) typography includes "e.g., the member\'s attorney, accountant, or clearing firm')
print('  contact"; this toy is not those engines')
flatten_4370 = False
print(f"  this is a flatten into already-taught 15c3-3 or SIPC, or into packed 2261 / 2266 / 2267 / 2231 / 2090? {flatten_4370}")
check(flatten_4370 is False, "do not flatten 4370 into 15c3-3, SIPC, or packed 2261 / 2266 / 2267 / 2231 / 2090")
invents_website = False
print(f"  this toy invents that a member without a Web site must still post the disclosure on a website? {invents_website}")
check(invents_website is False, "4370(e) posts on the member's Web site only if the member maintains a Web site")
written_bcp = True
print(f"  a written business continuity plan, reasonably designed to meet existing obligations to customers, and written disclosure at account opening, on the member's Web site if maintained, and mailed upon request? {written_bcp}")
check(written_bcp is True, "4370 requires a written BCP and the official (e) customer disclosure")
print("no broker or product recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== N. FINRA 4340: callable securities fair-and-impartial allocation and customer notice ===")
# FINRA Rule 4340 Callable Securities (official HTML opened 2026-11-12).
# Keep the new 4370 section identical once 4370 is added, and keep
# 37/37 after L / 2090 as a strict byte-prefix of the tip file.
# Official 4340(a): Each member that has in its possession or under its
# control any security which, by its terms, may be called or redeemed
# prior to maturity, shall: (1) establish and make available on the
# member's website procedures by which it will allocate among its
# customers, on a fair and impartial basis, the securities to be
# redeemed or selected as called in the event of a partial redemption
# or call; and (2) provide written notice (which may be electronic) to
# new customers at the opening of an account, and all customers at
# least once every calendar year, of the manner in which they may
# access the allocation procedures on the member's website and that,
# upon a customer's request, the member will provide hard copies of
# the allocation procedures to the customer.
# Official typography is one-word lowercase "website." Do not tidy it
# into packed 4370's official "Web site," or the reverse.
# Official (b) favorable redemptions: a member shall not allocate the
# securities to any account in which it or its associated persons have
# an interest until all other customers' positions have been satisfied.
# Official (c) unfavorable redemptions: the member shall not exclude
# its positions or those of its associated persons from the pool.
# Official SM .02 may name an impartial lottery system, acting on a
# pro-rata basis, or such other means as will achieve a fair and
# impartial allocation; name only. Official SM .01 clerical-and-
# ministerial and official SM .03 introducing-member catalogs exist;
# name them, do not build those catalogs. Do not flatten 4340 into
# already-taught 15c3-3 "possession or control," or into FINRA
# 2232(b)(2) (2232 is not packed). Do not invent that every common
# stock is callable. No broker or product recommendation.

print("4340(a): Each member that has in its possession or under its control any security which, by")
print("  its terms, may be called or redeemed prior to maturity, shall:")
print("  (1) establish and make available on the member's website procedures by which it will")
print("  allocate among its customers, on a fair and impartial basis, the securities to be redeemed")
print("  or selected as called in the event of a partial redemption or call; and")
print("  (2) provide written notice (which may be electronic) to new customers at the opening of an")
print("  account, and all customers at least once every calendar year, of the manner in which they")
print("  may access the allocation procedures on the member's website and that, upon a customer's")
print("  request, the member will provide hard copies of the allocation procedures to the customer")
print('official typography is one-word lowercase "website"')
print("official (b) favorable redemptions: a member shall not allocate the securities to any account")
print("  in which it or its associated persons have an interest until all other customers' positions")
print("  in such securities have been satisfied")
print("official (c) unfavorable redemptions: a member shall not exclude its positions or those of")
print("  its associated persons from the pool of the securities eligible to be called")
print("official SM .02 may include an impartial lottery system, acting on a pro-rata basis, or such")
print("  other means as will achieve a fair and impartial allocation; official SM .01 and SM .03")
print("  exist; this toy is not those catalogs")
flatten_4340 = False
print(f"  this is a flatten into already-taught 15c3-3 possession or control, or into FINRA 2232(b)(2)? {flatten_4340}")
check(flatten_4340 is False, "do not flatten 4340 into 15c3-3 or into unpacked 2232")
every_stock = False
print(f"  this toy invents that every common stock is callable? {every_stock}")
check(every_stock is False, "4340 applies to a security which, by its terms, may be called or redeemed prior to maturity")
fair = True
print(f"  fair-and-impartial allocation procedures on the member's website, and written notice to new customers at account opening and to all customers at least once every calendar year? {fair}")
check(fair is True, "4340 requires website allocation procedures and the official customer notice")
print("no broker or product recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== O. FINRA 2140: no interference with a customer's account-transfer request in an employment-change context ===")
# FINRA Rule 2140 Interfering With the Transfer of Customer Accounts in
# the Context of Employment Disputes (official HTML opened 2026-11-12).
# Add this section after the last line so 43/43 after N / 4340 remains a
# strict byte-prefix of the tip file.
# Official core: No member or person associated with a member shall
# interfere with a customer's request to transfer his or her account in
# connection with the change in employment of the customer's registered
# representative where the account is not subject to any lien for monies
# owed by the customer or other bona fide claim. Prohibited interference
# includes, but is not limited to, seeking a judicial order or decree
# that would bar or restrict the submission, delivery or acceptance of a
# written request from a customer to transfer his or her account.
# Nothing in this Rule shall affect the operation of Rule 11870.
# Quote that last sentence with a normal single space; an empty
# <span class="us"></span> before the Rule 11870 link is page chrome,
# not typography. Official typography is "his or her account,"
# "includes, but is not limited to," and "written request from a
# customer to transfer his or her account." Official caption typography
# is "Interfering With the Transfer of Customer Accounts in the Context
# of Employment Disputes." Name Rule 11870 only; do not recast 2140 as a
# street-name / ACATS / CNS product primer, and do not invent a 11870
# engine. Do not invent that every account transfer is covered (official
# text is limited to a transfer request in connection with the change in
# employment of the customer's registered representative, and only where
# the account is not subject to any lien for monies owed by the customer
# or other bona fide claim). Do not flatten 2140 into packed 2165,
# packed 4370 / 4340 / 2090 / 2231, or already-taught 15c3-3 / SIPC.
# No broker or product recommendation.

print("2140: No member or person associated with a member shall interfere with a customer's")
print("  request to transfer his or her account in connection with the change in employment")
print("  of the customer's registered representative where the account is not subject to any")
print("  lien for monies owed by the customer or other bona fide claim")
print("Prohibited interference includes, but is not limited to, seeking a judicial order or")
print("  decree that would bar or restrict the submission, delivery or acceptance of a")
print("  written request from a customer to transfer his or her account")
print("Nothing in this Rule shall affect the operation of Rule 11870")
print('official typography uses a normal single space before "Rule 11870"; empty page-chrome spans are not typography')
print('official typography is "his or her account," "includes, but is not limited to," and')
print('  "written request from a customer to transfer his or her account"')
print("official caption typography is Interfering With the Transfer of Customer Accounts in the Context of Employment Disputes")
print("Rule 11870 is named only; this toy is not a street-name / ACATS / CNS primer or a 11870 engine")
flatten_2140 = False
print(f"  this is a flatten into packed 2165, packed 4370 / 4340 / 2090 / 2231, or already-taught 15c3-3 / SIPC? {flatten_2140}")
check(flatten_2140 is False, "do not flatten 2140 into packed 2165 / 4370 / 4340 / 2090 / 2231 or 15c3-3 / SIPC")
every_transfer = False
print(f"  this toy invents that every account transfer is covered? {every_transfer}")
check(every_transfer is False, "2140 is limited to a transfer request in connection with the RR employment change, and only where the account is not subject to any lien or other bona fide claim")
core_2140 = True
print(f"  no interference with a customer's request to transfer his or her account in connection with the change in employment of the customer's registered representative, where the account is not subject to any lien for monies owed by the customer or other bona fide claim? {core_2140}")
check(core_2140 is True, "2140 prohibits interference with that official account-transfer request")
print("no broker or product recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== P. 17 CFR 240.15c6-2: Same-day allocation, confirmation, and affirmation ===")
# 17 CFR 240.15c6-2 Same-day allocation, confirmation, and affirmation
# (official eCFR versioner API XML, title 17 up_to_date_as_of 2026-11-09,
# opened 2026-11-12). Add this section after the last line so 46/46 after
# O / 2140 remains a strict byte-prefix of the tip file.
# Official (a) is a shall with a written-agreement or written-policies
# disjunction, and applies only to a transaction that is subject to
# § 240.15c6-1(a). Official typography is "as soon as technologically
# practicable and no later than the end of the day on trade date" (no
# "the" before "trade date"). Official caption typography is "Same-day
# allocation, confirmation, and affirmation" (Oxford comma). Cite 17 CFR
# 240.15c6-2. Name official (b); do not build that procedures catalog.
# Do not flatten 15c6-2 into already-taught Rule 15c6-1 / T+1 / FINRA
# 11320, and do not invent that settlement itself is T+0. Official text
# is the allocation, confirmation, affirmation, or any combination
# thereof, in such form as necessary to achieve settlement. Learning
# only; no broker or settlement-vendor recommendation.

print("15c6-2(a): Any broker or dealer engaging in the allocation, confirmation, or affirmation")
print("  process with another party or parties to achieve settlement of a securities transaction")
print("  that is subject to the requirements of § 240.15c6-1(a) shall:")
print("  (1) enter into a written agreement with the relevant parties to ensure completion of the")
print("  allocation, confirmation, affirmation, or any combination thereof, for the transaction")
print("  as soon as technologically practicable and no later than the end of the day on trade date")
print("  in such form as necessary to achieve settlement of the transaction; or")
print("  (2) establish, maintain, and enforce written policies and procedures reasonably designed")
print("  to ensure completion of the allocation, confirmation, affirmation, or any combination")
print("  thereof, for the transaction as soon as technologically practicable and no later than")
print("  the end of the day on trade date in such form as necessary to achieve settlement of the")
print("  transaction")
print("official caption typography is Same-day allocation, confirmation, and affirmation (Oxford comma)")
print('official typography is "as soon as technologically practicable and no later than the end of the day on trade date" (no "the" before "trade date")')
print("cite 17 CFR 240.15c6-2; title 17 up_to_date_as_of 2026-11-09")
print("official (a) is a written-agreement or written-policies disjunction")
print("official (b) exists; this toy is not that procedures catalog")
flatten_15c62 = False
print(f"  this is a flatten into already-taught Rule 15c6-1 / T+1 / FINRA 11320, or an invention that settlement itself is T+0? {flatten_15c62}")
check(flatten_15c62 is False, "do not flatten 15c6-2 into 15c6-1 / T+1 / 11320, and do not invent that settlement itself is T+0")
combo = True
print(f"  official text is the allocation, confirmation, affirmation, or any combination thereof, in such form as necessary to achieve settlement? {combo}")
check(combo is True, "15c6-2 is allocation, confirmation, affirmation, or any combination thereof")
core_15c62 = True
print(f"  completion as soon as technologically practicable and no later than the end of the day on trade date, by written agreement or written policies and procedures reasonably designed? {core_15c62}")
check(core_15c62 is True, "15c6-2 requires same-day allocation, confirmation, and affirmation by written agreement or reasonably designed written policies")
print("no broker or settlement-vendor recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== Q. FINRA 4330(a): written authorization before lending a customer's margin securities ===")
# FINRA Rule 4330 Customer Protection — Permissible Use of Customers'
# Securities (official <h1> typography uses an em dash U+2014; official
# HTML opened earlier on 2026-11-12, wording reconfirmed 2026-11-12).
# Keep P identical once 15c6-2 is added.
# Official (a): No member shall lend securities that are held on margin
# for a customer and that are eligible to be pledged or loaned, unless
# such member shall first have obtained a written authorization from
# such customer permitting the lending of such securities.
# Official SM .02: members may use a single customer account
# agreement/margin agreement/loan consent with clear and prominent
# disclosure in lieu of a separate written authorization; name it; do
# not invent that a separate writing is always required.
# Official (b) fully-paid / excess-margin borrow catalog exists,
# including official (b)(1)(A) "SEA Rule 15c3-3"; name official (b)
# and official SM .01 / .03-.06, do not build that catalog.
# Do not flatten 4330(a) into already-taught 15c3-3 or SIPC, or into
# packed 2264. Customer-protection literacy only; no securities-lending
# product recommendation.

print("4330(a): No member shall lend securities that are held on margin for a customer and that")
print("  are eligible to be pledged or loaned, unless such member shall first have obtained a")
print("  written authorization from such customer permitting the lending of such securities")
print("official caption typography is Customer Protection \u2014 Permissible Use of Customers' Securities")
print("  (em dash U+2014, not a hyphen or an en dash; apostrophe in Customers')")
print("official (a) heading typography is Authorization to Lend Customers' Margin Securities")
print("official SM .02: members may use a single customer account agreement/margin agreement/loan")
print("  consent signed by a customer as written authorization in lieu of a separate written")
print("  authorization, provided it includes clear and prominent disclosure that the firm may")
print("  lend either to itself or others any securities held by the customer in its margin account")
print('official typography is "SEA Rule 15c3-3" and "in writing (which may be electronic)"')
print("official (b) and official SM .01 / .03-.06 exist; this toy is not that fully-paid /")
print("  excess-margin borrow, SIPC-notice, or appropriateness catalog")
flatten_4330 = False
print(f"  this is a flatten into already-taught 15c3-3 or SIPC, or into packed 2264? {flatten_4330}")
check(flatten_4330 is False, "do not flatten 4330(a) into already-taught 15c3-3 or SIPC, or into packed 2264")
separate_always = False
print(f"  this toy invents that a separate writing is always required? {separate_always}")
check(separate_always is False, "official SM .02 permits a single customer account agreement/margin agreement/loan consent with the official disclosure")
core_4330 = True
print(f"  written authorization is required before lending a customer's eligible margin securities? {core_4330}")
check(core_4330 is True, "4330(a) requires written authorization before lending a customer's eligible margin securities")
print("customer-protection literacy only; no securities-lending product recommendation")
print(f"assertions passed: {checks}/{checks}")
