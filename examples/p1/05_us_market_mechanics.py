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
