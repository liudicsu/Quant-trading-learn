"""P6 lab 06: LULD vs MWCB vs Reg SHO Rule 201 — toy state machine (offline synthetic, seed=21).
Learning only — not investment advice. NOT a complete LULD rule engine.

Percentage parameters (LULD Plan Amendment 20, Appendix A; checked_on 2026-11-08):
  The day's PRICE TIER comes from the prior trading day's primary-listing close (not the moving reference):
  Tier 1: > $3 -> 5%; $0.75..$3 (inclusive) -> 20%; < $0.75 -> lesser of $0.15 or 75% of reference
  Tier 2: > $3 -> 10%; $0.75..$3 (inclusive) -> 20%; < $0.75 -> lesser of $0.15 or 75% of reference
  The moving reference price (usually mean of eligible trades, prior 5 min) does NOT reselect the tier;
  it sets the centre and, with the fixed tier parameters, the band width and bounds (Plan Sec. V(A)).
  Last 25 min of regular hours (or before an early close): double for all Tier 1 and for Tier 2 whose
  price tier is <= $3 (not Tier 2 > $3). Ordinary non-leveraged toy only.
  No opening doubling since Amendment 18 (2020-02-24).
"""
from __future__ import annotations
import numpy as np


def price_tier(prior_listing_close: float) -> str:
    """Price tier for the WHOLE day, fixed from the prior trading day's primary-listing close."""
    if prior_listing_close > 3.0:
        return "gt3"
    if prior_listing_close >= 0.75:
        return "0.75-3"          # $0.75 to $3, both ends inclusive
    return "lt0.75"


def band(tier: int, prior_listing_close: float, moving_ref: float, closing_window: bool) -> tuple[float, float, float, bool]:
    """Step 1: percentage + doubling eligibility from the day's price tier (prior close).
    Step 2: the moving reference price sets the centre AND enters the width/bounds:
    width = pct * moving_ref (or min(0.15, 0.75 * moving_ref) below $0.75); it never reselects the tier."""
    pt = price_tier(prior_listing_close)
    eligible_double = tier == 1 or pt != "gt3"     # Tier 2 above $3 is not doubled at the close
    doubled = closing_window and eligible_double
    if pt == "gt3":
        width = (0.05 if tier == 1 else 0.10) * moving_ref
    elif pt == "0.75-3":
        width = 0.20 * moving_ref
    else:
        width = min(0.15, 0.75 * moving_ref)
    if doubled:
        width *= 2
    return width / moving_ref, moving_ref - width, moving_ref + width, doubled


print("=== 1. tier from PRIOR CLOSE; centre, width and bounds from MOVING reference price ===")
for tier, pc, ref, cw in [(1, 50.0, 50.0, False), (1, 50.0, 50.0, True), (2, 50.0, 50.0, False), (2, 50.0, 50.0, True), (2, 2.0, 2.0, True), (1, 0.50, 0.50, False)]:
    p, lo_, hi_, d = band(tier, pc, ref, cw)
    print(f"tier{tier} prior_close={pc:>6.2f} ref={ref:>6.2f} closing_window={str(cw):5s} -> band +/-{p:.2%} = [{lo_:.4f}, {hi_:.4f}] doubled={d}")

print("=== 1b. boundary tests (prior close sets the tier, not the moving ref) ===")
TESTS = [
    # name, tier, prior_close, moving_ref, closing_window, expected pct
    ("cross $3 up:   prior 2.90 -> ref 3.10", 2, 2.90, 3.10, False, 0.20),
    ("cross $3 down: prior 3.10 -> ref 2.90", 2, 3.10, 2.90, False, 0.10),
    ("cross $0.75 up:   prior 0.74 -> ref 0.76", 2, 0.74, 0.76, False, 0.15 / 0.76),
    ("cross $0.75 down: prior 0.75 -> ref 0.74", 2, 0.75, 0.74, False, 0.20),
    ("closing: Tier2 prior 3.10 (not eligible)", 2, 3.10, 3.10, True, 0.10),
    ("closing: Tier2 prior 2.90 (eligible)", 2, 2.90, 3.10, True, 0.40),
    ("closing: Tier1 prior 50.00 (eligible)", 1, 50.0, 50.0, True, 0.10),
]
for name, tier, pc, ref, cw, exp in TESTS:
    p, lo_, hi_, d = band(tier, pc, ref, cw)
    assert abs(p - exp) < 1e-12, (name, p, exp)
    print(f"PASS {name}: tier{tier} -> +/-{p:.2%} [{lo_:.4f}, {hi_:.4f}] doubled={d}")
print(f"tests passed: {len(TESTS)}/{len(TESTS)}")

print("=== 2. toy single-stock path: limit state -> 5-min halt -> reopen gap ===")
rng = np.random.default_rng(21)
ref, tier = 40.0, 1
_, lo, hi, _ = band(tier, 40.0, ref, False)
prices = list(40 + np.cumsum(rng.normal(0, 0.05, 80)))
prices[10:14] = [lo, lo, lo, lo]           # offer sits at lower band (limit state)
limit_start, seconds_per_tick = 10, 5       # 4 ticks x 5 s = 20 s > 15 s -> pause
state, halted_until, fills = "normal", None, []
stop_level = 38.5
for t, px in enumerate(prices):
    if state == "halt":
        if t >= halted_until:
            state = "normal"; reopen = 37.20      # synthetic reopening price (gap)
            print(f"t={t}: reopen at {reopen:.2f} (gap from band {lo:.2f})")
            fills.append(("stop_sell", reopen))
        continue
    if px <= lo:
        dur = (t - limit_start + 1) * seconds_per_tick
        if dur > 15:
            state, halted_until = "halt", t + 60      # 60 ticks x 5 s = 5 min
            print(f"t={t}: limit state > 15 s ({dur}s) -> trading pause; no new fills while halted")
print(f"stop-sell trigger {stop_level:.2f} filled at {fills[0][1]:.2f} -> a stop order does not guarantee its price")

print("=== 3. three different mechanisms (do not merge them) ===")
prev_close = 40.0
print("MWCB: market-wide, S&P 500 decline vs prior close, Level 1/2/3 = 7%/13%/20%")
print("LULD: single stock, dynamic band around 5-min reference price, regular hours only")
last = 35.8
print(f"Reg SHO Rule 201: single stock fell {1-last/prev_close:.1%} >= 10% vs prior close -> short-sale PRICE TEST (not a halt) rest of day + next day")
print("disclaimer: synthetic; learning only")
