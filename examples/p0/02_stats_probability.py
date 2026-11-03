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


def count_false_hits(r_values: np.ndarray, seed: int, trials: int = 100, thr: float = 2.0) -> tuple[int, list[float], list[np.ndarray]]:
    rng_mt = np.random.default_rng(seed)
    false_hits = 0
    sharpes: list[float] = []
    pnls: list[np.ndarray] = []
    for _ in range(trials):
        noise = rng_mt.normal(size=len(r_values))
        pos = np.sign(noise)
        pnl = pos * r_values
        sh = sharpe(pd.Series(pnl))
        sharpes.append(sh)
        pnls.append(pnl)
        if abs(sh) > thr:
            false_hits += 1
    return false_hits, sharpes, pnls


# Parameters for the multiple-testing toy (stated in the lesson)
N = n  # 252
ANN = float(np.sqrt(252))
THR = 2.0
SEED_DEMO = 7
TRIALS = 100
# Under H0 with IID-ish noise, SR_ann = mean/std*√252 has sd ≈ 1, so P(|Z|>2) ≈ 4.55%
null_p = float(erfc(THR / sqrt(2.0)))  # two-sided normal
print("\n=== multiple testing parameters ===")
print("n", N)
print("ann_factor_sqrt252", round(ANN, 6))
print("threshold_abs_SR", THR)
print("trials_per_seed", TRIALS)
print("demo_seed", SEED_DEMO)
print("null_P_abs_Z_gt_2", round(null_p, 6))
print("null_expected_false_hits_per_100", round(null_p * TRIALS, 2))

false_hits, sharpes, pnls = count_false_hits(r_a.values, SEED_DEMO, TRIALS, THR)

print("\n=== multiple testing toy (seed 7) ===")
print("trials", TRIALS)
print("false_hits_|Sharpe|>2", false_hits)
print("max_abs_sharpe", round(max(abs(s) for s in sharpes if s == s), 3))
print("mean_abs_sharpe", round(float(np.nanmean(np.abs(sharpes))), 3))

best_i = int(np.nanargmax(np.abs(sharpes)))
best_pnl = pd.Series(pnls[best_i])
best_sh = sharpes[best_i]
t_stat = float(best_pnl.mean() / (best_pnl.std(ddof=1) / np.sqrt(n)))
p_approx = float(erfc(abs(t_stat) / sqrt(2.0)))
print("\n=== p-value misuse walk-through (best of 100 trials, seed 7) ===")
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
print(
    "seed7_note: under the null ~4.55 hits/100 are expected; seed 7 is an extreme draw that produced 10."
)

# Many seeds: average false-hit count and spread
N_SEEDS = 200
hit_counts = np.array(
    [count_false_hits(r_a.values, seed=s, trials=TRIALS, thr=THR)[0] for s in range(N_SEEDS)],
    dtype=float,
)
print("\n=== false-hit sweep over many seeds ===")
print("n_seeds", N_SEEDS)
print("mean_false_hits", round(float(hit_counts.mean()), 3))
print("std_false_hits", round(float(hit_counts.std(ddof=1)), 3))
print("min_false_hits", int(hit_counts.min()))
print("max_false_hits", int(hit_counts.max()))
print("seed7_false_hits", false_hits)
