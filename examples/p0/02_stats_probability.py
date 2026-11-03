"""P0 lab: distributions, IID caveat, p-value misuse, histogram, multiple-testing loop.
Synthetic offline data. Learning only — not investment advice.
Cite: López de Prado, Advances in Financial Machine Learning (Wiley, 2018) —
multiple testing / backtest overfitting spirit.
"""
from __future__ import annotations

from math import erfc, sqrt
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT_PNG = ROOT / "public" / "p0" / "returns_hist.png"

# Hand-calc toy — var≈0.000358, std≈0.0189
hand = pd.Series([0.01, -0.02, 0.015])
print("=== hand_calc three returns ===")
print({"mean": float(hand.mean()), "var": float(hand.var(ddof=1)), "std": float(hand.std(ddof=1))})

rng = np.random.default_rng(42)
n = 252
idx = pd.bdate_range("2023-01-02", periods=n)
r_a = pd.Series(rng.normal(0.0004, 0.01, n), index=idx, name="a")
r_b = 0.3 * r_a + pd.Series(rng.normal(0, 0.01, n), index=idx, name="b")

print("\n=== summary stats (a) ===")
stats = {
    "mean": float(r_a.mean()),
    "var": float(r_a.var(ddof=1)),
    "std": float(r_a.std(ddof=1)),
    "q05": float(r_a.quantile(0.05)),
    "q50": float(r_a.quantile(0.50)),
    "q95": float(r_a.quantile(0.95)),
}
print(stats)

full_corr = float(r_a.corr(r_b))
roll_corr = r_a.rolling(63).corr(r_b)
print("\nfull_sample_corr", round(full_corr, 4))
print("rolling_63_corr_tail")
print(roll_corr.dropna().tail(5).round(4).to_string())

OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
fig, ax = plt.subplots(figsize=(7.2, 3.6), dpi=120)
ax.hist(r_a.values, bins=30, color="#3b82f6", edgecolor="white", alpha=0.9)
ax.axvline(stats["mean"], color="#ef4444", linestyle="--", label=f"mean={stats['mean']:.5f}")
ax.axvline(stats["q05"], color="#f59e0b", linestyle=":", label=f"q05={stats['q05']:.4f}")
ax.axvline(stats["q95"], color="#10b981", linestyle=":", label=f"q95={stats['q95']:.4f}")
ax.set_title("Synthetic daily returns histogram (seed=42)")
ax.set_xlabel("return")
ax.set_ylabel("count")
ax.legend(loc="best", fontsize=8)
ax.grid(True, alpha=0.25)
fig.tight_layout()
fig.savefig(OUT_PNG)
plt.close(fig)
print("saved_plot", OUT_PNG.relative_to(ROOT).as_posix())


def sharpe(x: pd.Series) -> float:
    s = x.std(ddof=1)
    return float("nan") if s == 0 else float(x.mean() / s * np.sqrt(252))


# Dedicated RNG for the multiple-testing loop (reproducible, independent of r_a draws)
rng_mt = np.random.default_rng(7)
false_hits = 0
sharpes = []
pnls = []
for i in range(100):
    noise = rng_mt.normal(size=n)
    pos = np.sign(noise)
    pnl = pos * r_a.values
    sh = sharpe(pd.Series(pnl))
    sharpes.append(sh)
    pnls.append(pnl)
    if abs(sh) > 2:
        false_hits += 1

print("\n=== multiple testing toy ===")
print("trials", 100)
print("false_hits_|Sharpe|>2", false_hits)
print("max_abs_sharpe", round(max(abs(s) for s in sharpes if s == s), 3))
print("mean_abs_sharpe", round(float(np.nanmean(np.abs(sharpes))), 3))

best_i = int(np.nanargmax(np.abs(sharpes)))
best_pnl = pd.Series(pnls[best_i])
best_sh = sharpes[best_i]
t_stat = float(best_pnl.mean() / (best_pnl.std(ddof=1) / np.sqrt(n)))
p_approx = float(erfc(abs(t_stat) / sqrt(2.0)))
print("\n=== p-value misuse walk-through (best of 100 trials) ===")
print("H0: mean daily pnl of this random-sign rule is 0")
print("best_trial_index", best_i)
print("best_sharpe", round(float(best_sh), 4))
print("t_stat_mean0", round(t_stat, 4))
print("two_sided_normal_p_approx", round(p_approx, 6))
print(
    "misuse_note: a small p on the *selected* best trial is not evidence of a real edge; "
    "you already searched 100 rules (multiple testing / backtest overfitting — see AFML, López de Prado 2018)."
)
print(
    "iid_note: financial returns often violate IID (volatility clustering); "
    "IID-based p-values then overstate significance."
)
