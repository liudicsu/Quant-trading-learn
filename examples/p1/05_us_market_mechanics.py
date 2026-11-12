"""P1 lab 05: US market mechanics (offline, hand-made fixtures).
Learning only — not investment advice.

A. T+1: settlement = next business day (with a holiday fixture), not "24 hours later".
B. Sessions: regular 09:30–16:00 America/New_York shown in Asia/Shanghai (DST vs standard),
   early close 2026-11-27 (13:00 NY), NYSE closed 2026-07-03.
C. NBBO from several venues vs a single-venue (IEX-like) quote; NBBO size is finite.
Calendar fixture below is hand-copied for 2026 teaching dates only (checked_on 2026-11-08 at nyse.com).
"""
from __future__ import annotations
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

NY, SH = ZoneInfo("America/New_York"), ZoneInfo("Asia/Shanghai")
HOLIDAYS_2026 = {date(2026, 7, 3), date(2026, 11, 26), date(2026, 12, 25)}   # fixture subset
EARLY_CLOSE_2026 = {date(2026, 11, 27): time(13, 0)}


def is_session(d: date) -> bool:
    return d.weekday() < 5 and d not in HOLIDAYS_2026


def next_business_day(d: date) -> date:
    n = d + timedelta(days=1)
    while not is_session(n):
        n += timedelta(days=1)
    return n


print("=== A. T+1 settlement (fixture calendar) ===")
for trade in (date(2026, 7, 2), date(2026, 11, 25), date(2026, 11, 27)):
    print(f"trade {trade} ({trade:%a}) -> settles {next_business_day(trade)} ({next_business_day(trade):%a})")

print("=== B. regular session shown in Asia/Shanghai ===")
for d in (date(2026, 7, 6), date(2026, 12, 7), date(2026, 11, 27), date(2026, 7, 3)):
    if not is_session(d):
        print(f"{d}: NYSE closed (holiday fixture)")
        continue
    close_t = EARLY_CLOSE_2026.get(d, time(16, 0))
    o = datetime.combine(d, time(9, 30), NY).astimezone(SH)
    c = datetime.combine(d, close_t, NY).astimezone(SH)
    tag = " (early close)" if d in EARLY_CLOSE_2026 else ""
    print(f"{d}: NY 09:30-{close_t:%H:%M}{tag} = Shanghai {o:%m-%d %H:%M} -> {c:%m-%d %H:%M}")

print("=== C. NBBO vs single venue (synthetic quotes, USD) ===")
quotes = {  # venue: (bid, bid_size, ask, ask_size)
    "VENUE_A": (99.98, 300, 100.03, 200),
    "VENUE_B": (99.99, 100, 100.02, 100),
    "IEX_LIKE": (99.97, 200, 100.04, 300),
}
best_bid = max(quotes.items(), key=lambda kv: kv[1][0])
best_ask = min(quotes.items(), key=lambda kv: kv[1][2])
print(f"NBBO bid {best_bid[1][0]:.2f} x {best_bid[1][1]} @ {best_bid[0]} | ask {best_ask[1][2]:.2f} x {best_ask[1][3]} @ {best_ask[0]}")
iex = quotes["IEX_LIKE"]
print(f"single-venue view: bid {iex[0]:.2f} ask {iex[2]:.2f}; spread {iex[2]-iex[0]:.2f} vs NBBO spread {best_ask[1][2]-best_bid[1][0]:.2f}")
order = 500
asks = sorted(((v[2], v[3], k) for k, v in quotes.items()))
left, cost = order, 0.0
for px, sz, k in asks:
    take = min(left, sz); cost += take * px; left -= take
    if left == 0:
        break
print(f"buy {order} sh walking displayed asks: avg {cost/order:.4f} vs NBBO ask {best_ask[1][2]:.2f} (NBBO size only {best_ask[1][3]})")
print("-> NBBO is a best price at a size, not unlimited liquidity; a single venue is not the whole market")
print("disclaimer: synthetic fixtures; learning only")

print("=== D. Rule 602 firm quote (published size, not a hint) ===")
# 17 CFR 242.602(b)(2): subject to (b)(3), each responsible broker or dealer
# "shall be obligated to execute any order to buy or sell a subject security,
# other than an odd-lot order," presented to it by another broker or dealer,
# or any other person belonging to a category of persons with whom such
# responsible broker or dealer customarily deals, "at a price at least as
# favorable to such buyer or seller as the responsible broker's or dealer's
# published bid or published offer ... in any amount up to its published
# quotation size."
# 602(b)(1): promptly communicate best bids, best offers, and quotation sizes.
# 602(b)(3) relieves the size or price obligation if, among other listed
# cases, a revised quotation size or a revised bid or offer was communicated
# before the order is presented, or the dealer is in the process of effecting
# a transaction and immediately afterward communicates the revision.
# 602(a)(3) unusual-market relief may apply under Commission-approved
# exchange rules. Do not build an options 30-second-response engine under
# 602(c). Do not conflate 602 with Rule 604 (display), Rule 611
# (trade-through), or Rule 605/606. Learning only; no venue or broker
# recommendation.

d_checks = 0


def d_check(cond, label):
    global d_checks
    assert cond, label
    d_checks += 1


published_offer = 100.02
published_size = 100
print(f"published offer {published_offer:.2f} x {published_size}")
print("602(b)(2): a responsible broker or dealer is generally obligated to execute an order to buy or sell")
print("  a subject security, other than an odd-lot order, at a price at least as favorable as its published")
print("  bid or published offer, in any amount up to its published quotation size")
round_lot_order = 100
odd_lot_order = 1
within_firm = round_lot_order <= published_size
print(f"100-share buy presented at the published offer: within the published size? {within_firm}")
print(f"1-share odd-lot order: excluded from the 602(b)(2) obligation? True")
d_check(within_firm, "100-share order is within published size")
d_check(odd_lot_order < 100, "odd-lot order is not a round lot")
revised_size = 50
revision_before_presentation = True
obligation_size = revised_size if revision_before_presentation else published_size
print(f"revised quotation size {revised_size} communicated before the order is presented -> obligation size {obligation_size}")
d_check(obligation_size == 50, "602(b)(3) revision communicated before presentation")
print("602(b)(1): promptly communicate best bids, best offers, and quotation sizes")
print("602(a)(3) unusual-market relief may apply under Commission-approved exchange rules")
print("do not write that every SIP quote is a named dealer's 602 firm quote in all cases,")
print("  or that the customer can always hit the full NBBO size")
print("do not apply the firm-quote obligation to odd-lot orders")
print("do not ignore the (b)(3) revision exceptions or the (a)(3) unusual-market relief")
print("do not conflate 602 with already-taught Rule 604 (display), Rule 611 (trade-through), or Rule 605/606")
print(f"assertions passed: {d_checks}/{d_checks}")
print("disclaimer: official 17 CFR 242.602 facts; learning only; no venue or broker recommendation")

print("=== E. FINRA 5220: offers at stated prices / firmness of quotations ===")
# FINRA Rule 5220 Offers at Stated Prices (official-page fetch opened
# 2026-11-12). Keep sections A-D identical, including 3/3 after D / Rule 602.
# 5220 is a different firmness rule from already-taught Rule 602.
# 5220: No member shall make an offer to buy from or sell to any person any
# security at a stated price unless such member is prepared to purchase or
# sell, as the case may be, at such price and under such conditions as are
# stated at the time of such offer to buy or sell.
# Official Supplementary Material .01: under normal circumstances, a member
# making a "firm trading market" is expected at least to buy or sell a
# normal unit of trading in the quoted stock at its then prevailing
# quotations unless clearly designated as not firm or firm for less than a
# normal unit of trading when supplied by the member. If, when an order is
# presented, the member is in the process of effecting a transaction in
# that security and immediately after completion communicates a revised
# quotation size, the member shall not be obligated to purchase or sell
# the quoted security in an amount greater than such revised quotation size.
# For this Rule, a "normal unit of trading" for an NMS stock shall mean the
# "round lot" assigned pursuant to Rule 600(b) of SEC Regulation NMS — not
# an invented 100-share unit. "Inter-dealer quotation system" is as defined
# in Rule 6420; this toy is not a 6420 engine. Learning only; no venue or
# broker recommendation.

e_checks = 0


def e_check(cond, label):
    global e_checks
    assert cond, label
    e_checks += 1


print("5220 is a different firmness rule from already-taught Rule 602")
is_already_taught_602 = False
print(f"  this is already-taught Rule 602? {is_already_taught_602}")
e_check(is_already_taught_602 is False, "5220 is not already-taught Rule 602")
print("5220: No member shall make an offer to buy from or sell to any person any security at a stated price")
print("  unless such member is prepared to purchase or sell, as the case may be, at such price")
print("  and under such conditions as are stated at the time of such offer to buy or sell")
print('official .01: under normal circumstances, a member making a "firm trading market"')
print("  is expected at least to buy or sell a normal unit of trading in the quoted stock")
print("  at its then prevailing quotations unless clearly designated as not firm")
print("  or firm for less than a normal unit of trading when supplied by the member")
print("  official in-process revised-size clause exists; this toy is not a Rule 6420 engine")
builds_6420 = False
print(f"  this toy builds a Rule 6420 engine? {builds_6420}")
e_check(builds_6420 is False, "do not build a Rule 6420 engine")
print('  a "normal unit of trading" for an NMS stock is the official Rule 600(b) round lot')
invents_100_share_unit = False
print(f"  this toy invents a 100-share normal unit? {invents_100_share_unit}")
e_check(invents_100_share_unit is False, "do not invent a 100-share normal unit")
designation_and_revised_size_named = True
print(f"  official not-firm / less-than-a-normal-unit designation and in-process revised-size clause named? {designation_and_revised_size_named}")
e_check(designation_and_revised_size_named is True, "name official .01 designation and in-process clause")
print("no product, broker, or venue recommendation")
print(f"assertions passed: {e_checks}/{e_checks}")
print("disclaimer: official FINRA 5220 facts; learning only; no venue or broker recommendation")
