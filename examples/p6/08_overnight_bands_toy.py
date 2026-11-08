"""P6 lab 08: LULD Overnight Price Bands, Phase 1 (Amendment No. 27, SEC 34-106042; Consolidated Price time
moved 19:45 -> 19:30 ET by Amendment No. 29, SEC 34-106624, effective on a temporary basis not to exceed 120 days).
Planned start 2026-12-06, dependent on Processor systems changes (checked_on 2026-11-08). Offline toy, synthetic
prices. Not a rule engine; Phase 2 parameters are not known and not modelled. Learning only.
Band rule (34-106042 Sec. III(1)): lower = 20% below the LOWER of the two reference prices, upper = 20% above the
HIGHER; minimum distance from the applicable reference = $3.00 if Closing Price >= $1.00, else $1.00;
leveraged ETP: 20% and the minimum both multiplied by the leverage ratio.
Toy choice (not in the order): the lower band is floored at 0.
"""
from __future__ import annotations


def overnight_bands(closing_price: float, consolidated_price: float, leverage: float = 1.0) -> tuple[float, float]:
    lo_ref, hi_ref = min(closing_price, consolidated_price), max(closing_price, consolidated_price)
    pct = 0.20 * leverage
    min_dist = (3.00 if closing_price >= 1.00 else 1.00) * leverage
    lower = min(lo_ref * (1 - pct), lo_ref - min_dist)
    upper = max(hi_ref * (1 + pct), hi_ref + min_dist)
    return max(lower, 0.0), upper


CASES = [
    ("large cap, quiet evening", 200.00, 201.00, 1.0, (160.00, 241.20)),
    ("after-hours news gap", 50.00, 44.00, 1.0, (35.20, 60.00)),
    ("low price: $3 minimum binds", 8.00, 8.10, 1.0, (5.00, 11.10)),
    ("sub-$1 close: $1 minimum", 0.80, 0.85, 1.0, (0.00, 1.85)),
    ("2x leveraged ETP", 40.00, 40.00, 2.0, (24.00, 56.00)),
]
print("case                         close  consol  lev  -> lower   upper")
for name, c, p, lev, exp in CASES:
    lo, hi = overnight_bands(c, p, lev)
    assert (round(lo, 2), round(hi, 2)) == exp, (name, lo, hi)
    print(f"{name:28s} {c:6.2f} {p:7.2f} {lev:4.1f}  -> {lo:7.2f} {hi:7.2f}")
print(f"tests passed: {len(CASES)}/{len(CASES)}")
print("timeline (ET): consolidated price snapshot 19:30 (Amendment 29; was 19:45) -> bands to Processors by 20:55")
print("-> public before 21:00 -> Overnight Protected Hours 21:00 (Sun-Thu) to 04:00 next calendar day")
print("hitting a band: NO automatic Trading Pause (regular hours: Limit State 15 s -> pause);")
print("the Primary Listing Exchange MAY declare a Regulatory Halt; then orders are rejected and the stock")
print("does not reopen during that night's Overnight Protected Hours. Bands are not a fill guarantee.")
