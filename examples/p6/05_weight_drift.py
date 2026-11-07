"""P6 lab 05: weight drift & constraint consistency (offline synthetic, seed=3).
Learning only — not investment advice.
"""
from __future__ import annotations
import numpy as np

rng = np.random.default_rng(3)
names = ["A", "B", "C", "D"]
w0 = np.array([0.30, 0.30, 0.20, 0.20])     # target weights
cap = 0.33                                   # per-asset cap
print("=== 1. constraint consistency check (before any optimisation) ===")
for c in (cap, 0.20):
    feasible = c * len(names) >= 1.0
    print(f"cap={c:.2f}, n={len(names)}: max total = {c*len(names):.2f} -> {'feasible' if feasible else 'INFEASIBLE (cannot sum to 1)'}")

print("=== 2. drift over 63 days without trading ===")
r = rng.normal([0.004, 0.0, -0.002, 0.0005], 0.01, size=(63, 4))
growth = np.prod(1 + r, axis=0)
w_drift = w0 * growth / (w0 * growth).sum()
for n_, a, b in zip(names, w0, w_drift):
    print(f"{n_}: target={a:.4f} drifted={b:.4f}")
print(f"sum drifted = {w_drift.sum():.4f}; cap breached: {[n for n, v in zip(names, w_drift) if v > cap]}")

print("=== 3. rebalance back to target ===")
turnover = 0.5 * np.abs(w0 - w_drift).sum()
cost_bps = 10
print(f"one-way turnover = {turnover:.4f}; cost @ {cost_bps}bp = {turnover*cost_bps/1e4:.6f} of NAV")
band = 0.02
need = np.abs(w_drift - w0) > band
print(f"assets outside +/-{band:.0%} band: {[n for n, v in zip(names, need) if v]}")
print("-> check constraints on DRIFTED weights, not only on the target you set")
print("disclaimer: synthetic; learning only")
