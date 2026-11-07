"""P6 lab 06: LULD vs MWCB vs Reg SHO Rule 201 — toy state machine (offline synthetic, seed=21).
Learning only — not investment advice. NOT a complete LULD rule engine.

Percentage parameters (LULD Plan Amendment 20, Appendix A; checked_on 2026-11-08):
  Tier 1: ref > $3 -> 5%; $0.75..$3 -> 20%; < $0.75 -> lesser of $0.15 or 75%
  Tier 2: ref > $3 -> 10%; $0.75..$3 -> 20%; < $0.75 -> lesser of $0.15 or 75%
  Last 25 min of regular hours: double for all Tier 1 and Tier 2 priced <= $3 (not Tier 2 > $3).
  No opening doubling since Amendment 18 (2020-02-24).
"""
from __future__ import annotations
import numpy as np


def band_pct(tier: int, ref: float, closing_window: bool) -> tuple[float, str]:
    if ref > 3.0:
        pct = 0.05 if tier == 1 else 0.10
        doubled = closing_window and tier == 1
    elif ref >= 0.75:
        pct, doubled = 0.20, closing_window
    else:
        width = min(0.15, 0.75 * ref)
        return (2 * width if closing_window else width) / ref, "abs"
    return (2 * pct if doubled else pct), "pct"


print("=== 1. band widths (reference price = avg of prior 5 min) ===")
for tier, ref, cw in [(1, 50.0, False), (1, 50.0, True), (2, 50.0, False), (2, 50.0, True), (2, 2.0, True), (1, 0.50, False)]:
    p, _ = band_pct(tier, ref, cw)
    print(f"tier{tier} ref={ref:>6.2f} closing_window={str(cw):5s} -> band +/-{p:.2%} = [{ref*(1-p):.4f}, {ref*(1+p):.4f}]")

print("=== 2. toy single-stock path: limit state -> 5-min halt -> reopen gap ===")
rng = np.random.default_rng(21)
ref, tier = 40.0, 1
lo, hi = ref * (1 - 0.05), ref * (1 + 0.05)
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
