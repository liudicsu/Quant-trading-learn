"""P4 lab 02: neutralization, multi-factor combo, turnover/costs, crowding; strong vs weak.
Learning only — not investment advice.
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from _common import (
    ANN,
    MU_STRONG,
    MU_WEAK,
    PUBLIC,
    apply_costs_ls,
    build_factor,
    ensure_panel,
    load_strength,
    ls_stats,
    ls_weights,
    spearman_ic,
    forward_sum,
    winsorize_cs,
    zscore_cs,
    neutralize,
    DATA as DATA_DIR,
)

DATA = DATA_DIR
ensure_panel()
rets_s, raw, raw2, log_mcap, meta = load_strength("strong")
rets_w, _, _, _, _ = load_strength("weak")
ind = meta["industry"]
beta_true = meta["beta_true"]

print("=== parameters ===")
print("reuse 200x750; true factor + nuisance raw_factor2")
print(f"MU_STRONG={MU_STRONG} (inflated teaching) MU_WEAK={MU_WEAK} (realistic-weak foil)")
print("look-ahead: shift(1) weights; lagged impact vol; neutralize uses log_mcap.shift(1)")
print("cost model: P2 10 bps one-way + √impact")
print("overlapping IC windows inflate IC autocorr / ICIR SE (not mean IC) — use non-overlap or NW")

print("\n=== neutralization before / after (strong; lagged mcap) ===")
logcap_lag = log_mcap.shift(1)
f_z = zscore_cs(winsorize_cs(raw))
f_n = zscore_cs(neutralize(f_z, ind, logcap_lag))
f2_z = zscore_cs(winsorize_cs(raw2))
f2_n = zscore_cs(neutralize(f2_z, ind, logcap_lag))
fwd = forward_sum(rets_s, 1)
ic_before = spearman_ic(f_z, fwd)
ic_after = spearman_ic(f_n, fwd)
ic2_after = spearman_ic(f2_n, fwd)
print(f"true_factor RankIC mean before_neut={ic_before.mean():.4f} after={ic_after.mean():.4f}")
print(f"nuisance_factor RankIC mean after_neut={ic2_after.mean():.4f} (should be ~0)")
print(f"recovery corr after_neut={f_n.mean(axis=0).corr(beta_true):.4f}")
print("neutralize covariates: industry (static) + log_mcap.shift(1) only — no same-day mcap")

print("\n=== strong vs weak (side-by-side portfolio metrics) ===")
f_n_w = build_factor(raw, ind, log_mcap)
st_s = ls_stats(f_n, rets_s)
st_w = ls_stats(f_n_w, rets_w)
for label, st, mu in [("strong", st_s, MU_STRONG), ("weak", st_w, MU_WEAK)]:
    print(
        f"{label:6s} MU={mu:.4f} RankIC={st['RankIC_mean']:.4f} ICIR={st['ICIR']:.3f} "
        f"gross_SR={st['gross_SR']:.3f} net_SR={st['net_SR']:.3f} turn={st['mean_turn']:.4f}"
    )
print("teach: weak RankIC is the live-like case; costs often erase net edge — multi-factor combination exists to stack weak signals")

print("\n=== single vs equal-weight multi-factor (strong) ===")
combo = zscore_cs(0.5 * f_n + 0.5 * f2_n)
specs = {"true_only": f_n, "nuisance_only": f2_n, "ew_true_plus_nuisance": combo}
for name, fac in specs.items():
    st = ls_stats(fac, rets_s)
    print(
        f"{name:24s} gross_SR={st['gross_SR']:.3f} net_SR={st['net_SR']:.3f} "
        f"turn={st['mean_turn']:.4f} NAV={st['NAV_net']:.3f} IC={st['RankIC_mean']:.4f}"
    )
print("teach: blending a null nuisance dilutes IC/net SR — combining ≠ free lunch; combine *informed* weak factors")

# weak: true vs EW with a second weak-ish construct (nuisance still null)
print("\n=== multi-factor honesty on WEAK panel ===")
combo_w = zscore_cs(0.5 * f_n_w + 0.5 * f2_n)
for name, fac in [("weak_true_only", f_n_w), ("weak_ew_true_plus_nuisance", combo_w)]:
    st = ls_stats(fac, rets_w)
    print(
        f"{name:28s} gross_SR={st['gross_SR']:.3f} net_SR={st['net_SR']:.3f} "
        f"turn={st['mean_turn']:.4f} IC={st['RankIC_mean']:.4f}"
    )

print("\n=== turnover–cost table (strong true factor) ===")
base_w = ls_weights(f_n)
for hold in [1, 5, 10, 20]:
    w_h = base_w.copy()
    for i in range(0, len(w_h), hold):
        block = w_h.iloc[i : i + hold]
        if len(block) == 0:
            continue
        w_h.iloc[i : i + hold] = block.iloc[0].values
    net, turn = apply_costs_ls(w_h, rets_s)
    print(
        f"hold={hold:2d}d mean_turn={float(turn.mean()):.4f} "
        f"net_SR={float(net.mean()/net.std(ddof=1)*ANN):.3f} "
        f"NAV={float((1+net.fillna(0)).cumprod().iloc[-1]):.3f}"
    )
print("\n=== turnover–cost table (WEAK true factor) ===")
base_ww = ls_weights(f_n_w)
for hold in [1, 5, 10, 20]:
    w_h = base_ww.copy()
    for i in range(0, len(w_h), hold):
        block = w_h.iloc[i : i + hold]
        if len(block) == 0:
            continue
        w_h.iloc[i : i + hold] = block.iloc[0].values
    net, turn = apply_costs_ls(w_h, rets_w)
    print(
        f"hold={hold:2d}d mean_turn={float(turn.mean()):.4f} "
        f"net_SR={float(net.mean()/net.std(ddof=1)*ANN):.3f} "
        f"NAV={float((1+net.fillna(0)).cumprod().iloc[-1]):.3f}"
    )
print("teach: on weak signals, cutting turnover is often the difference between net>0 and net≈0")

print("\n=== crowding foil ===")
w = ls_weights(f_n)
long = w.clip(lower=0)
hhi = (long ** 2).sum(axis=1)
rank_ac = []
for a, b in zip(f_n.index[:-1], f_n.index[1:]):
    x, y = f_n.loc[a], f_n.loc[b]
    ok = x.notna() & y.notna()
    if int(ok.sum()) < 30:
        continue
    rank_ac.append(float(stats.spearmanr(x[ok], y[ok]).correlation))
print(f"long_leg_HHI_mean={float(hhi.mean()):.5f} rank_AC1={float(np.mean(rank_ac)):.4f}")

fig, axes = plt.subplots(1, 2, figsize=(10, 4))
for ax, st, title in [(axes[0], st_s, "strong (inflated)"), (axes[1], st_w, "weak (realistic)")]:
    ax.plot((1 + st["net"].fillna(0)).cumprod(), color="#1f4e79")
    ax.set_title(f"{title}\nnet SR={st['net_SR']:.2f}")
    ax.grid(True, alpha=0.3)
fig.suptitle("Portfolio lab: strong vs weak net NAV")
fig.tight_layout(); fig.savefig(PUBLIC / "portfolio_strong_vs_weak.png", dpi=120); plt.close()
print("chart", PUBLIC / "portfolio_strong_vs_weak.png")

fig, ax = plt.subplots(figsize=(8, 4))
for name, fac in specs.items():
    st = ls_stats(fac, rets_s)
    ax.plot((1 + st["net"].fillna(0)).cumprod(), label=name)
ax.set_title("Net NAV: true vs nuisance vs EW combo (strong)")
ax.legend(); ax.grid(True, alpha=0.3)
fig.tight_layout(); fig.savefig(PUBLIC / "portfolio_nav_compare.png", dpi=120); plt.close()

fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(["before", "after"], [ic_before.mean(), ic_after.mean()], color=["#9dc3e6", "#1f4e79"])
ax.set_ylabel("mean RankIC"); ax.set_title("True factor RankIC before/after neutralization")
ax.grid(True, axis="y", alpha=0.3)
fig.tight_layout(); fig.savefig(PUBLIC / "ic_before_after.png", dpi=120); plt.close()
print("chart", PUBLIC / "ic_before_after.png")
print("disclaimer: strong MU inflated for teaching; weak panel is the realistic foil — learning only")
