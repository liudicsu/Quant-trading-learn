"""P5 depth labs: fracdiff, sample uniqueness, meta-label filter, CPCV reuse note.
Learning only — not investment advice. Offline/synthetic.
cite: López de Prado AFML ch.3 meta-labeling; ch.4 uniqueness/seq bootstrap; ch.5 fracdiff; ch.12 CPCV spirit.
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
from statsmodels.tsa.stattools import adfuller
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.preprocessing import StandardScaler

from _common import (
    ANN,
    EMBARGO,
    HORIZON,
    N_FOLDS,
    PUBLIC,
    mean_daily_cs_ic,
    pred_to_ls_pnl,
    purged_kfold_indices,
)

print("=== parameters / sources ===")
print("cite: AFML ch.3 meta-labeling; ch.4 average uniqueness + sequential bootstrap; ch.5 fracdiff")
print("cite: AFML ch.12 CPCV — reuse note only (full toy lives in P2 backtest-traps)")
print("disclaimer: teaching sketches on synthetic series — not production AFML code")

DATA = Path(__file__).resolve().parent / "data"
df = pd.read_pickle(DATA / "ml_frame.pkl")
rets = pd.read_csv(DATA / "rets_subset.csv", index_col=0, parse_dates=True)
PUBLIC.mkdir(parents=True, exist_ok=True)

# -------------------- Fracdiff --------------------
print("\n=== fractional differentiation (AFML ch.5) ===")
print("intuition: integer d=1 (pct_change) kills memory; fractional d keeps long memory while aiming at stationarity")
rng = np.random.default_rng(0)
# Mildly non-stationary log-price: integrated noise + slow drift
n = 800
eps = rng.normal(0, 0.01, size=n)
logp = np.cumsum(eps) + 0.0002 * np.arange(n)
px = pd.Series(np.exp(logp), name="px")


def frac_weights(d: float, size: int, threshold: float = 1e-4):
    """AFML weight formula ω0=1, ωk=−ω_{k-1}(d−k+1)/k; cutoff when |ω|<threshold."""
    w = [1.0]
    for k in range(1, size):
        w_k = -w[-1] * (d - k + 1) / k
        if abs(w_k) < threshold:
            break
        w.append(w_k)
    return np.asarray(w, dtype=float)


def fracdiff_series(x: pd.Series, d: float, threshold: float = 1e-4) -> pd.Series:
    w = frac_weights(d, len(x), threshold=threshold)
    width = len(w)
    vals = x.values.astype(float)
    out = np.full(len(x), np.nan)
    for t in range(width - 1, len(x)):
        out[t] = np.dot(w[::-1], vals[t - width + 1 : t + 1])
    return pd.Series(out, index=x.index, name=f"fd_{d}")


d_star = 0.4
w_demo = frac_weights(d_star, 200, threshold=1e-4)
print(f"d={d_star} weight_cutoff_len={len(w_demo)} first5={np.round(w_demo[:5], 6)} last={w_demo[-1]:.6g}")
print("integer note: when d is a positive integer, weights beyond lag d are exactly 0 → memory cancelled")

fd = fracdiff_series(px, d_star, threshold=1e-4)
fd1 = px.diff()  # integer d=1
# ADF on levels / fd / diff — dropna
adf_level = adfuller(px.dropna(), maxlag=10, autolag="AIC")
adf_fd = adfuller(fd.dropna(), maxlag=10, autolag="AIC")
adf_d1 = adfuller(fd1.dropna(), maxlag=10, autolag="AIC")
print(f"ADF px level: stat={adf_level[0]:.3f} p={adf_level[1]:.4f} (usually fail to reject unit root)")
print(f"ADF fracdiff d={d_star}: stat={adf_fd[0]:.3f} p={adf_fd[1]:.4f}")
print(f"ADF integer diff d=1: stat={adf_d1[0]:.3f} p={adf_d1[1]:.4f}")
# Memory proxy: corr(transformed_t, px_{t-20})
lag = 20
# Memory proxy: autocorrelation at lag 20 (how much of the series still "remembers" itself)
acf_fd = float(fd.dropna().autocorr(lag=lag))
acf_d1 = float(fd1.dropna().autocorr(lag=lag))
# Also corr with lagged price level (integer diff ≈ orthogonal to level path)
corr_lvl_fd = float(fd.corr(px.shift(lag)))
corr_lvl_d1 = float(fd1.corr(px.shift(lag)))
print(f"memory_proxy autocorr(lag={lag}): fracdiff={acf_fd:.4f} integer_diff={acf_d1:.4f}")
print(f"memory_proxy corr(series, px.shift({lag})): fracdiff={corr_lvl_fd:.4f} integer_diff={corr_lvl_d1:.4f}")
print("teach: fracdiff aims for the smallest d that passes a stationarity test while preserving more serial dependence than d=1")

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(w_demo, color="#1f4e79")
ax.set_title(f"Fracdiff weights d={d_star} (cutoff |w|<{1e-4})")
ax.set_xlabel("lag k"); ax.set_ylabel("ω_k")
ax.grid(True, alpha=0.3)
fig.tight_layout(); fig.savefig(PUBLIC / "fracdiff_weights.png", dpi=120); plt.close()
print("chart", PUBLIC / "fracdiff_weights.png")

# -------------------- Sample uniqueness --------------------
print("\n=== sample uniqueness / average uniqueness (AFML ch.4) ===")
print("intuition: overlapping label spans are not independent samples — down-weight concurrent events")
# Tiny panel: 12 events with horizons overlapping
events = pd.DataFrame({
    "t0": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
    "t1": [3, 4, 5, 4, 7, 8, 9, 10, 11, 12, 13, 14],
    "y": [0.02, -0.01, 0.03, 0.00, -0.02, 0.01, 0.04, -0.03, 0.02, 0.01, -0.01, 0.03],
})
T = int(events["t1"].max()) + 1
conc = np.zeros(T)
for _, row in events.iterrows():
    conc[int(row.t0) : int(row.t1) + 1] += 1
avg_u = []
for _, row in events.iterrows():
    span = conc[int(row.t0) : int(row.t1) + 1]
    avg_u.append(float(np.mean(1.0 / span)))
events["avg_uniqueness"] = avg_u
print("concurrent_count_by_t:", conc.astype(int).tolist())
print(events.round(4).to_string(index=False))
w = events["avg_uniqueness"].values
y = events["y"].values
mean_eq = float(y.mean())
mean_w = float(np.average(y, weights=w))
print(f"equal_weight_mean_y={mean_eq:.4f} uniqueness_weighted_mean_y={mean_w:.4f}")
print(
    "sequential bootstrap (1 paragraph): instead of drawing IDs with equal probability, "
    "draw the next bootstrap sample with probability proportional to remaining uniqueness "
    "given already drawn overlapping events — AFML ch.4 — so bags are less redundant than IID bagging."
)
print("reweight_effect: uniqueness weights shrink the influence of highly concurrent (redundant) labels")

# -------------------- Meta-labeling --------------------
print("\n=== meta-labeling full filter (AFML ch.3) ===")
print("primary side = sign(mom_20); meta learns whether to TRADE or SKIP that side")
print("link: bet sizing after the meta filter → modern-ml-pipelines (P5-02) / AFML ch.10")
feat_cols = [c for c in df.columns if c.startswith(("mom_", "vol_", "rank_"))]
dates = df.index.get_level_values(0)
uniq = np.array(sorted(dates.unique()))
folds = purged_kfold_indices(uniq, N_FOLDS, HORIZON, EMBARGO)
side = np.sign(df["mom_20"]).replace(0, np.nan)
meta_y = df["meta_y"]
X = df[feat_cols]
# Primary-only: always trade the side
primary_score = side
# Meta OOF probability of "trade"
oof_p = pd.Series(np.nan, index=df.index)
for tr_d, te_d in folds:
    mtr, mte = dates.isin(set(tr_d)), dates.isin(set(te_d))
    if mtr.sum() < 200 or mte.sum() < 50:
        continue
    sc = StandardScaler().fit(X.loc[mtr])
    clf = LogisticRegression(max_iter=400)
    clf.fit(sc.transform(X.loc[mtr]), meta_y.loc[mtr])
    oof_p.loc[mte] = clf.predict_proba(sc.transform(X.loc[mte]))[:, 1]
oof_p = oof_p.dropna()

# Filter A: trade if p>=0.55; Filter B: trade if p>=0.50 (base-rate-ish)
thr_a, thr_b = 0.52, 0.48


def filtered_score(prob, thr):
    """Return primary side where meta says trade; NaN where skip (so CS IC uses active names)."""
    trade = prob >= thr
    s = side.loc[prob.index].where(trade)
    return s.dropna()


meta_table = []
for name, score, raw_prob, thr in [
    ("A_primary_always", primary_score.dropna(), None, None),
    ("B_meta_filter_0.52", filtered_score(oof_p, thr_a), oof_p, thr_a),
    ("C_meta_filter_0.48", filtered_score(oof_p, thr_b), oof_p, thr_b),
]:
    y = df["fwd_ret"].reindex(score.index)
    m = mean_daily_cs_ic(score, y)
    net, turn = pred_to_ls_pnl(score.fillna(0), rets)
    sr = float(net.mean() / net.std(ddof=1) * ANN) if net.std(ddof=1) > 0 else float("nan")
    if raw_prob is None:
        tfrac = 1.0
    else:
        tfrac = float((raw_prob >= thr).mean())
    meta_table.append({
        "config": name,
        "mean_CS_IC": round(m["mean_ic"], 4),
        "turnover": round(float(turn.mean()), 4),
        "net_SR": round(sr, 3),
        "trade_frac": round(tfrac, 4),
    })
meta_df = pd.DataFrame(meta_table)
print(meta_df.to_string(index=False))
print("teach: meta-labeling does not invent the side — it filters when to size the primary bet (→ P5-02 sizing)")

# -------------------- CPCV reuse note --------------------
print("\n=== CPCV reuse note (see P2 backtest-traps for the numeric toy) ===")
print(
    "When you score many purged fold combinations, you get a DISTRIBUTION of OOS metrics — "
    "same spirit as AFML ch.12 CPCV. Paths reuse test blocks and are NOT independent DSR trials. "
    "Teaching sketch lives in examples/p2/02_backtest_traps.py (cpcv_sr_dist.png)."
)

print("disclaimer: synthetic weak panel — learning only, not investment advice")
