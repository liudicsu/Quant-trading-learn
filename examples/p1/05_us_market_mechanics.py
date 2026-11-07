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
