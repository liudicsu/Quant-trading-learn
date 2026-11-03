"""P4 lab 02: neutralization before/after, multi-factor combo, turnover/costs, crowding.
Learning only — not investment advice.
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from _common import ANN, PUBLIC, apply_costs_ls, ensure_panel, DATA as DATA_DIR

DATA = DATA_DIR
CACHE = DATA / "cache"
ensure_panel()
rets = pd.read_csv(DATA / "returns.csv", index_col=0, parse_dates=True)
raw = pd.read_csv(DATA / "raw_factor.csv", index_col=0, parse_dates=True)
raw2 = pd.read_csv(DATA / "raw_factor2.csv", index_col=0, parse_dates=True)
log_mcap = pd.read_csv(DATA / "log_mcap.csv", index_col=0, parse_dates=True)
meta = pd.read_csv(DATA / "meta.csv").set_index("asset")
ind = meta["industry"]
beta_true = meta["beta_true"]

print("=== parameters ===")
print("reuse panel 200x750; true factor + nuisance raw_factor2 (noise loading)")
print("look-ahead: shift(1) weights; lagged impact vol; factor[t] → fwd from t+1")
print("cost model shared with P2/P3/P4-01: 10 bps one-way + √impact")


def winsorize_cs(df, p=0.01):
    return df.clip(df.quantile(p, axis=1), df.quantile(1 - p, axis=1), axis=0)


def zscore_cs(df):
    return df.sub(df.mean(axis=1), axis=0).div(df.std(axis=1, ddof=1).replace(0, np.nan), axis=0)


def neutralize(df, industry, logcap):
    out = pd.DataFrame(np.nan, index=df.index, columns=df.columns)
    ind_dummies = pd.get_dummies(industry, prefix="ind", dtype=float)
    for dt in df.index:
        y = df.loc[dt].astype(float)
        X = pd.concat([ind_dummies, logcap.loc[dt].astype(float).rename("log_mcap")], axis=1).reindex(y.index)
        ok = y.notna() & X.notna().all(axis=1)
        if int(ok.sum()) < X.shape[1] + 5:
            continue
        Yv, Xv = y[ok].values, np.column_stack([np.ones(int(ok.sum())), X.loc[ok].values])
        coef, *_ = np.linalg.lstsq(Xv, Yv, rcond=None)
        out.loc[dt, y[ok].index] = Yv - Xv @ coef
    return out


def forward1(rets):
    out = pd.DataFrame(np.nan, index=rets.index, columns=rets.columns)
    out.iloc[:-1] = rets.values[1:]
    return out


def spearman_ic(fac, fwd):
    ics = []
    idx = []
    for dt in fac.index:
        a, b = fac.loc[dt], fwd.loc[dt]
        ok = a.notna() & b.notna()
        if int(ok.sum()) < 30:
            continue
        ics.append(float(stats.spearmanr(a[ok], b[ok]).correlation))
        idx.append(dt)
    return pd.Series(ics, index=idx)


def ls_weights(fac, q=5):
    w = pd.DataFrame(0.0, index=fac.index, columns=fac.columns)
    for dt in fac.index:
        s = fac.loc[dt].dropna()
        if len(s) < 50:
            continue
        lab = pd.qcut(s, q, labels=False, duplicates="drop") + 1
        for qi, sign in [(1, -1.0), (q, 1.0)]:
            members = lab[lab == qi].index
            if len(members):
                w.loc[dt, members] = sign / len(members)
    return w


print("\n=== neutralization before / after ===")
f_z = zscore_cs(winsorize_cs(raw))
f_n = zscore_cs(neutralize(f_z, ind, log_mcap))
f2_z = zscore_cs(winsorize_cs(raw2))
f2_n = zscore_cs(neutralize(f2_z, ind, log_mcap))
fwd = forward1(rets)
ic_before = spearman_ic(f_z, fwd)
ic_after = spearman_ic(f_n, fwd)
ic2_after = spearman_ic(f2_n, fwd)
print(f"true_factor RankIC mean before_neut={ic_before.mean():.4f} after={ic_after.mean():.4f}")
print(f"nuisance_factor RankIC mean after_neut={ic2_after.mean():.4f} (should be ~0)")
print(f"recovery corr after_neut={f_n.mean(axis=0).corr(beta_true):.4f}")

print("\n=== single vs equal-weight multi-factor ===")
# EW combo of true + nuisance (bad idea) vs true alone
combo = zscore_cs(0.5 * f_n + 0.5 * f2_n)
specs = {
    "true_only": f_n,
    "nuisance_only": f2_n,
    "ew_true_plus_nuisance": combo,
}
rows = []
for name, fac in specs.items():
    w = ls_weights(fac)
    net, turn = apply_costs_ls(w, rets)
    gross = (w.shift(1).fillna(0) * rets).sum(axis=1)
    rows.append({
        "spec": name,
        "gross_SR": float(gross.mean() / gross.std(ddof=1) * ANN),
        "net_SR": float(net.mean() / net.std(ddof=1) * ANN),
        "mean_turn": float(turn.mean()),
        "NAV_net": float((1 + net.fillna(0)).cumprod().iloc[-1]),
        "RankIC_mean": float(spearman_ic(fac, fwd).mean()),
    })
    print(
        f"{name:24s} gross_SR={rows[-1]['gross_SR']:.3f} net_SR={rows[-1]['net_SR']:.3f} "
        f"turn={rows[-1]['mean_turn']:.4f} NAV={rows[-1]['NAV_net']:.3f} IC={rows[-1]['RankIC_mean']:.4f}"
    )
print("teach: blending a null nuisance factor dilutes IC and net SR — combining ≠ free lunch")

print("\n=== turnover–cost table (rebalance cadence) ===")
# hold weights for H days (reduce turnover)
base_w = ls_weights(f_n)
for hold in [1, 5, 10, 20]:
    w_h = base_w.copy()
    # freeze weights within each hold block
    for i in range(0, len(w_h), hold):
        block = w_h.iloc[i : i + hold]
        if len(block) == 0:
            continue
        w_h.iloc[i : i + hold] = block.iloc[0].values
    net, turn = apply_costs_ls(w_h, rets)
    print(
        f"hold={hold:2d}d mean_turn={float(turn.mean()):.4f} "
        f"net_SR={float(net.mean()/net.std(ddof=1)*ANN):.3f} "
        f"NAV={float((1+net.fillna(0)).cumprod().iloc[-1]):.3f}"
    )
print("teach: lower turnover cuts cost drag; expected-value tradeoff vs signal freshness")

print("\n=== crowding foil ===")
# Herfindahl of long-leg weights + rank AC
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
print("teach: high AC + concentrated books → crowding risk if many funds hold the same names")

# charts
fig, ax = plt.subplots(figsize=(8, 4))
for name, fac in specs.items():
    w = ls_weights(fac)
    net, _ = apply_costs_ls(w, rets)
    ax.plot((1 + net.fillna(0)).cumprod(), label=name)
ax.set_title("Net NAV: true vs nuisance vs EW combo")
ax.legend(); ax.grid(True, alpha=0.3)
fig.tight_layout(); fig.savefig(PUBLIC / "portfolio_nav_compare.png", dpi=120); plt.close()
print("chart", PUBLIC / "portfolio_nav_compare.png")

fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(["before", "after"], [ic_before.mean(), ic_after.mean()], color=["#9dc3e6", "#1f4e79"])
ax.set_ylabel("mean RankIC"); ax.set_title("True factor RankIC before/after neutralization")
ax.grid(True, axis="y", alpha=0.3)
fig.tight_layout(); fig.savefig(PUBLIC / "ic_before_after.png", dpi=120); plt.close()
print("chart", PUBLIC / "ic_before_after.png")
print("disclaimer: synthetic planted panel — learning only, not investment advice")
