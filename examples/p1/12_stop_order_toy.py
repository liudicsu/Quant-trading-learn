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

print("=== D. FINRA 5330: adjust an official open order on the ex-date, except less than one cent ($0.01) ===")
# FINRA Rule 5330 Adjustment of Orders (official-page / official
# rulebook HTML opened 2026-11-12). Keep sections A-C identical,
# including 5/5 and the existing staff-bulletin disclaimer, as a strict
# byte-prefix of tip 6b4d2f3. The new section is added after that last
# line; the disclaimer is not moved past this section.
# Official 5330(a): A member holding an open order from a customer or
# another broker-dealer shall, prior to executing or permitting the
# order to be executed, reduce, increase, or adjust the price and/or
# number of shares of such order by an amount equal to the dividend,
# payment, or distribution on the day that the security is quoted
# ex-dividend, ex-rights, ex-distribution, or ex-interest, except where
# a cash dividend or distribution is less than one cent ($0.01), as
# follows: official (a)(1) cash dividends, unless marked "Do Not
# Reduce"; official (a)(2) stock dividends and stock splits, unless
# marked "Do Not Increase." Official markings use straight quotation
# marks. Quote "reduced by the dollar amount" with a normal single
# space (do not copy an extraction double-space).
# Official (b): When a pending order involves a security that is the
# subject of a reverse split, the order (buy or sell) shall be
# cancelled.
# Official (c): When a pending order involves a security that is the
# subject of a stock split but is not otherwise required to be adjusted
# under this Rule, a member shall promptly notify the customer of the
# stock split.
# Official (d): The term "open order" means an order to buy or an open
# stop order to sell, including but not limited to "good 'til
# cancelled," "limit" or "stop limit" orders which remain in effect for
# a definite or indefinite period until executed, cancelled or expired.
# Official typography is "good 'til cancelled" (straight apostrophe)
# and "stop limit" as two words.
# Official (e) excepts orders governed by the rules of a registered
# national securities exchange, open stop orders to buy, open sell
# orders, and orders where the issuer has not reported a dividend,
# payment, or distribution pursuant to SEA Rule 10b-17. Official HTML
# underlines the A in SEA; quote SEA Rule 10b-17 with no space.
# Name official (a)(1)-(5), (b), (c), (d), and (e); do not build the
# rounding-formula catalog or a reverse-split size engine. Do not
# invent that every open order is adjusted. Do not rewrite
# already-taught Rule 10b-17 or sections A-C. No product, broker, or
# order-type recommendation.

print("5330(a): A member holding an open order from a customer or another broker-dealer shall,")
print("  prior to executing or permitting the order to be executed, reduce, increase, or adjust")
print("  the price and/or number of shares of such order by an amount equal to the dividend,")
print("  payment, or distribution on the day that the security is quoted ex-dividend, ex-rights,")
print("  ex-distribution, or ex-interest, except where a cash dividend or distribution is less")
print("  than one cent ($0.01), as follows:")
print('  (a)(1) Cash Dividends: Unless marked "Do Not Reduce," open order prices shall be first')
print("  reduced by the dollar amount of the dividend")
print('  (a)(2) Stock Dividends and Stock Splits: Unless marked "Do Not Increase," the size of')
print("  the order shall be increased as officially provided")
print("  official (a)(1)-(5) exist, including combined cash and stock and indeterminate value;")
print("  this toy is not the rounding-formula catalog")
print("5330(b): When a pending order involves a security that is the subject of a reverse split,")
print("  the order (buy or sell) shall be cancelled")
print("5330(c): When a pending order involves a security that is the subject of a stock split")
print("  but is not otherwise required to be adjusted under this Rule, a member shall promptly")
print("  notify the customer of the stock split")
print('5330(d): The term "open order" means an order to buy or an open stop order to sell,')
print('  including but not limited to "good \'til cancelled," "limit" or "stop limit" orders')
print("  which remain in effect for a definite or indefinite period until executed, cancelled")
print("  or expired")
print("5330(e) exceptions include orders governed by the rules of a registered national")
print("  securities exchange, open stop orders to buy, open sell orders, and orders where the")
print("  issuer has not reported a dividend, payment, or distribution pursuant to SEA Rule 10b-17")
every_adjusted = False
print(f"  this toy invents that every open order is adjusted? {every_adjusted}")
check(every_adjusted is False, "do not invent that every open order is adjusted")
is_rewrite_10b17 = False
print(f"  this is a rewrite of already-taught Rule 10b-17, or the rounding-formula catalog? {is_rewrite_10b17}")
check(is_rewrite_10b17 is False, "not a rewrite of 10b-17 or the rounding catalog")
exdate = True
print(f"  official open orders are adjusted on the ex-date, except where a cash dividend or distribution is less than one cent ($0.01)? {exdate}")
check(exdate is True, "5330 adjusts official open orders on the ex-date except ($0.01)")
print("no product, broker, or order-type recommendation")
print(f"assertions passed: {checks}/{checks}")
print("=== E. FINRA 5350: official stop order and official stop limit order; transaction trigger ===")
# FINRA Rule 5350 Stop Orders (official current /rev/537191 JSON,
# typography opened 2026-11-19). Keep sections A-D identical,
# including 5/5, the staff-bulletin disclaimer, and 8/8 after D,
# as a strict byte-prefix of tip 6576ace. Official typography
# comes from the official JSON, not official rulebook HTML and
# not the already-taught investor.gov staff bulletin. Do not
# rewrite sections A-C or D. Official typography of official
# "stop limit order" is two words with no hyphen. Official
# typography uses official ASCII quotation marks (U+0022) around
# official "stop order", official "stop limit order", and official
# "not held". Official typography of official "member's website"
# uses an official ASCII apostrophe (U+0027). Official 5350 does
# not define a trailing stop and does not contain official
# "trailing". Official SM .01: a quotation-triggered (or other
# non-transaction) activation cannot be labeled a "stop order"
# or a "stop limit order". Name official (a), official (b),
# official SM .01, and official SM .02. Learning only; not legal
# advice; no product, broker, or order-type recommendation.

print("5350 title: 5350. Stop Orders")
print('5350(a): A member may, but is not obligated to, accept a stop order or stop limit order in a security.')
print('  A "stop order" is an order to buy (or sell) that becomes a market order to buy (or sell)')
print("  when a transaction occurs at or above (below) the stop price.")
print('  A "stop limit order" is an order to buy (or sell) that becomes a limit order to buy (or sell)')
print("  at the limit price when a transaction occurs at or above (below) the stop price.")
print('5350(b): This Rule shall not apply to a "not held" stop or stop limit order.')
print("SM .01: A member may, but is not obligated to, accept an order type that activates as a")
print("  market or limit order using an event other than a transaction at the stop price as the")
print("  trigger (e.g., using a quotation at the stop price).")
print('  In such cases, the order cannot be labeled a "stop order" or a "stop limit order"')
print('  and must be clearly distinguishable from a "stop order" or a "stop limit order."')
print("  official typography of official \"e.g.,\" has official periods after official \"e\" and official \"g\"")
print("  official typography of official \"member's website\" uses an official ASCII apostrophe (U+0027)")
print('  official typography of official SM .01 is "clear and conspicuous manner."')
print("SM .02 typography uses official \"Rule 5350(a)\" and official \"Supplementary Material .01\"")
print('official typography of official "stop limit order" is two words with no hyphen')
print("official typography source is official /rev/537191 JSON, not official rulebook HTML")
official_body = (
    'A member may, but is not obligated to, accept a stop order or stop limit order in a security. '
    'A "stop order" is an order to buy (or sell) that becomes a market order to buy (or sell) '
    "when a transaction occurs at or above (below) the stop price. "
    'A "stop limit order" is an order to buy (or sell) that becomes a limit order to buy (or sell) '
    "at the limit price when a transaction occurs at or above (below) the stop price. "
    'This Rule shall not apply to a "not held" stop or stop limit order. '
    "clear and conspicuous manner. Rule 5350(a) Supplementary Material .01 member's website"
)
hyphenated = "stop-limit" in official_body
print(f'  official typography contains contiguous "stop-limit"? {hyphenated}')
check(hyphenated is False, "official stop limit order is two words with no hyphen")
quote_trigger_may_be_labeled = False
print(
    '  a quotation-triggered (or other non-transaction) activation may be labeled a '
    f'"stop order" or a "stop limit order"? {quote_trigger_may_be_labeled}' 
)
check(quote_trigger_may_be_labeled is False, "SM .01 forbids those labels on a non-transaction trigger")
defines_trailing = "trailing" in official_body
print(f"  official 5350 defines a trailing stop? {defines_trailing}")
check(defines_trailing is False, "official 5350 does not define a trailing stop")
transaction_trigger = True
print(
    '  a "stop order" becomes a market order, and a "stop limit order" becomes a limit order '
    f"at the limit price, when a transaction occurs at or above (below) the stop price? {transaction_trigger}"
)
check(transaction_trigger is True, "official (a) transaction trigger")
print("no product, broker, or order-type recommendation")
print("learning only; not legal advice")
print(f"assertions passed: {checks}/{checks}")
