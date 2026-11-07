"""P3 lab 06: short-sale constraints are not "just a negative weight" (offline synthetic, seed=9).
Learning only — not investment advice. Borrow fees / recall below are ASSUMPTIONS, not broker facts.
"""
from __future__ import annotations
import numpy as np

rng = np.random.default_rng(9)
T = 60
r_long = rng.normal(0.0004, 0.01, T)          # leg we hold long (SYN_US_A)
r_short = rng.normal(0.0001, 0.012, T)        # leg we would short (SYN_US_B)
borrow_avail = np.ones(T, dtype=int); borrow_avail[20:30] = 0     # synthetic: no borrow for 10 days
recall_day = 45                                                    # synthetic recall -> forced cover
borrow_fee_annual = 0.08                                           # ASSUMPTION
div_day, div_ps, px = 35, 0.40, 50.0                               # dividend owed to lender

print("=== 1. long-only baseline vs naive pair vs constrained pair ===")
long_only = r_long
naive = 0.5 * r_long - 0.5 * r_short
short_on = borrow_avail.copy(); short_on[recall_day:] = 0
fee = borrow_fee_annual / 252 * 0.5 * short_on
div_cost = np.zeros(T); div_cost[div_day] = 0.5 * div_ps / px * short_on[div_day]
constrained = 0.5 * r_long - 0.5 * r_short * short_on - fee - div_cost
for name, x in (("long_only", long_only), ("naive_pair", naive), ("constrained_pair", constrained)):
    print(f"{name:17s} cum={np.prod(1 + x) - 1:+.4f}")
print(f"days short leg rejected/forced flat: {int((short_on == 0).sum())}/{T} (no-borrow 10 + after recall {T-recall_day})")
print(f"borrow fee paid (sum)={fee.sum():.5f}; dividend owed on day {div_day}={div_cost.sum():.5f} of NAV")

print("=== 2. unlimited-loss shape of a short ===")
for move in (0.5, 1.0, 3.0):
    print(f"stock +{move:.0%}: long loses at most 100% if it goes to 0; short of 1 share @50 loses {50*move:.0f} (no cap)")

print("=== 3. Reg SHO layers (different duties) ===")
for k, v in [("Rule 200", "mark order long / short / short exempt"),
             ("Rule 203(b)", "broker locate before short sale (reasonable grounds to borrow)"),
             ("Rule 201", "price test after >=10% one-day drop (rest of day + next day), not a halt"),
             ("Rule 204", "clearing participants close out fails to deliver")]:
    print(f"{k:12s}: {v}")
print("-> a local mask is a teaching constraint, NOT legal compliance; a locate is not a guaranteed borrow")
print("disclaimer: synthetic; learning only")
