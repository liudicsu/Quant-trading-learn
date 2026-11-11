"""Stop, stop-limit, and trailing-stop mechanics (checked 2026-11-12).

Sources: investor.gov Investor Bulletin "Stop, Stop-Limit, and Trailing Stop
Orders" (updated 2026-08-18). Staff bulletin, not a Commission rule.

- A stop order becomes a market order when the stop price is reached.
  "The stop price is not the guaranteed execution price for a stop order."
  The fill can deviate significantly from the stop; a short-term intraday
  move can produce a fill substantially worse than that day's close.
- A stop-limit becomes a limit order and "may not be executed if the
  stock's price moves away from the specified limit price." The stop and
  the limit need not be the same price.
- A trailing stop trails in the favorable direction and holds still in
  the unfavorable direction. Bulletin example: buy at $20, peak $24,
  $1 trail, trigger $23; "the execution price may deviate from $23."
- Trigger convention (last-sale vs quotation) differs by firm; check
  with the broker. Availability of these order types is firm-specific.

Learning only; not a recommendation of any order type, broker, or venue.
Synthetic prints; not a broker rule engine.
"""
from decimal import Decimal

checks = 0


def check(cond, label):
    global checks
    assert cond, label
    checks += 1


def triggered(stop, path, side="sell"):
    """First print that reaches the stop. Sell: price <= stop; buy: price >= stop."""
    stop = Decimal(str(stop))
    for px in path:
        px = Decimal(str(px))
        if (side == "sell" and px <= stop) or (side == "buy" and px >= stop):
            return True, px
    return False, None


print("=== A. A stop becomes a market order; the stop is not a guaranteed fill ===")
# Sell stop at 23; the tape trades 24, 23.50, then gaps to 22.
path = (Decimal("24"), Decimal("23.50"), Decimal("22"), Decimal("21.80"))
hit, trigger_print = triggered(23, path, "sell")
fill = Decimal("22")  # first available print after the trigger; not 23
print(f"  sell stop 23; tape {', '.join(str(p) for p in path)}")
print(f"  triggered? {hit} at print {trigger_print}; market-order fill {fill} (not the stop 23)")
check(hit and trigger_print == Decimal("22") and fill == Decimal("22"), "gap fill != stop")
print("  the stop price is a trigger, not a guaranteed execution price")

print("=== B. A stop-limit may not be executed ===")
# Same tape, stop 23, limit 22.50: the trigger print is 22, which is through
# the limit, so the limit order does not fill.
stop, limit = Decimal("23"), Decimal("22.50")
hit, trigger_print = triggered(stop, path, "sell")
limit_fillable = trigger_print is not None and trigger_print >= limit
print(f"  sell stop-limit stop {stop} / limit {limit}; same tape")
print(f"  triggered? {hit} at print {trigger_print}; limit fillable at or above {limit}? {limit_fillable}")
check(hit and trigger_print == Decimal("22") and not limit_fillable, "stop-limit no fill")
print("  a stop-limit becomes a limit order and may not be executed if the price moves away")

print("=== C. Trailing-stop bulletin example: $20 -> $24 -> trigger $23 ===")
bought = Decimal("20")
peak = Decimal("24")
trail = Decimal("1")
trailing_stop = peak - trail
print(f"  bought at {bought}; price peaks at {peak}; $1 sell trailing stop holds at {trailing_stop}")
check(trailing_stop == Decimal("23"), "trail holds at 23")
# Favorable move first: 20 -> 22 -> 24 trails 19 -> 21 -> 23; then drops.
favor = (Decimal("20"), Decimal("22"), Decimal("24"))
trail_px = None
last = None
for px in favor:
    if last is None or px > last:
        trail_px = px - trail
    last = px
print(f"  as the price rises {', '.join(str(p) for p in favor)}, the stop trails to {trail_px}")
check(trail_px == Decimal("23"), "trails to 23")
# Unfavorable drop: stop stays at 23; first print at or below 23 triggers;
# execution may deviate (here 22.90, not 23).
drop = (Decimal("23.40"), Decimal("22.90"), Decimal("22.50"))
hit, trigger_print = triggered(trail_px, drop, "sell")
fill = Decimal("22.90")
print(f"  price then drops {', '.join(str(p) for p in drop)}")
print(f"  triggered? {hit} at print {trigger_print}; fill {fill} (may deviate from 23)")
check(hit and trigger_print == Decimal("22.90") and fill != Decimal("23"), "trail fill may deviate")

print("trigger convention (last-sale vs quotation) differs by firm; check with the broker")
print("availability of stop, stop-limit and trailing-stop orders is firm-specific")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: staff bulletin, not a Commission rule; learning only; no order-type recommendation")
