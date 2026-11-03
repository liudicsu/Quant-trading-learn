"""P0 lab: return stats, rolling corr, multiple-testing false positives.
Synthetic offline data. Learning only — not investment advice.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
n = 252
idx = pd.bdate_range("2023-01-02", periods=n)
# Two synthetic return series
r_a = pd.Series(rng.normal(0.0004, 0.01, n), index=idx, name="a")
r_b = 0.3 * r_a + pd.Series(rng.normal(0, 0.01, n), index=idx, name="b")

print("=== summary stats (a) ===")
print(
    {
        "mean": float(r_a.mean()),
        "var": float(r_a.var(ddof=1)),
        "std": float(r_a.std(ddof=1)),
        "q05": float(r_a.quantile(0.05)),
        "q50": float(r_a.quantile(0.50)),
        "q95": float(r_a.quantile(0.95)),
    }
)

full_corr = float(r_a.corr(r_b))
roll_corr = r_a.rolling(63).corr(r_b)
print("\nfull_sample_corr", round(full_corr, 4))
print("rolling_63_corr_tail")
print(roll_corr.dropna().tail(5).round(4).to_string())

# 100 random "strategies": sign of noise as position; count how often |Sharpe|>2 in-sample
def sharpe(x: pd.Series) -> float:
    s = x.std(ddof=1)
    return float("nan") if s == 0 else float(x.mean() / s * np.sqrt(252))

false_hits = 0
sharpes = []
for i in range(100):
    noise = rng.normal(size=n)
    pos = np.sign(noise)
    pnl = pos * r_a.values
    sh = sharpe(pd.Series(pnl))
    sharpes.append(sh)
    if abs(sh) > 2:
        false_hits += 1

print("\n=== multiple testing toy ===")
print("trials", 100)
print("count_|Sharpe|>2", false_hits)
print("max_abs_sharpe", round(max(abs(s) for s in sharpes if s == s), 3))
print("mean_abs_sharpe", round(float(np.nanmean(np.abs(sharpes))), 3))
