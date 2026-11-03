"""P5 lab 01: labels, purged CV+embargo, scaler leak demos, overfit trap.
Learning only — not investment advice. Data: P4 WEAK panel subsample.
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import HistGradientBoostingRegressor

from _common import (
    ANN,
    EMBARGO,
    HORIZON,
    N_ASSETS_USE,
    N_FOLDS,
    PUBLIC,
    add_noise_features,
    daily_cs_ic,
    load_weak_subset,
    make_ml_frame,
    purged_kfold_indices,
    spearman_ic_series,
)

print("=== parameters ===")
print(f"P4 WEAK panel subsample n_assets={N_ASSETS_USE}; HORIZON={HORIZON}; N_FOLDS={N_FOLDS}; EMBARGO={EMBARGO}")
print("features: mom_1/5/10/20, vol_5/20, rank_mom20 — built from returns ≤ t; label uses t+1..t+h")
print("labels: forward sum; AFML ch.3 triple-barrier (pt=sl=2%, max_h=5); meta-label vs mom_20 side")
print("cite: López de Prado, Advances in Financial Machine Learning (Wiley) ch.3 labels, ch.7 purged CV")
print("look-ahead: features end at t; TB/meta inspect only future path for y; purge removes label-span overlap")
print("eval: RankIC (NOT accuracy); shared P2/P4 cost model deferred to lab 02 for portfolios")

rets, raw, raw2, log_mcap, meta, mu = load_weak_subset()
print(f"MU_WEAK={mu} panel {rets.shape}")

df = make_ml_frame(rets)
feat_cols = [c for c in df.columns if c.startswith(("mom_", "vol_", "rank_"))]
print(f"rows={len(df)} features={feat_cols}")

# Label look-ahead audit
print("\n=== label construction look-ahead audit ===")
print("fwd_ret[t] = sum(rets[t+1..t+h]) — no feature uses rets after t")
print("TB: walk path from t+1; vertical at h; pt/sl=0.02 — y uses future returns only")
print("meta_y: 1 iff sign(mom_20[t]) agrees with tb_side[t] — primary side from feature at t only")
print(f"tb_side value counts:\n{df['tb_side'].value_counts().to_string()}")
print(f"meta_y mean (hit rate)={df['meta_y'].mean():.3f}")

dates = df.index.get_level_values(0)
uniq_dates = np.array(sorted(dates.unique()))

X = df[feat_cols]
y = df["fwd_ret"]

def fit_predict_ridge(Xtr, ytr, Xte, scale_mode: str):
    if scale_mode == "global":
        # LEAK: scaler fit on train+test jointly (demo only)
        sc = StandardScaler().fit(pd.concat([Xtr, Xte]))
    elif scale_mode == "train":
        sc = StandardScaler().fit(Xtr)
    else:
        raise ValueError(scale_mode)
    model = Ridge(alpha=1.0)
    model.fit(sc.transform(Xtr), ytr)
    return pd.Series(model.predict(sc.transform(Xte)), index=Xte.index)


print("\n=== LEAK demos vs clean handling ===")
# 1) Shuffle split leak
from sklearn.model_selection import train_test_split
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0, shuffle=True)
pred = fit_predict_ridge(Xtr, ytr, Xte, "train")
ic_shuffle = spearman_ic_series(pred, yte)
print(f"LEAK shuffle_split RankIC={ic_shuffle:.4f}  (FORBIDDEN on time series)")

# 2) Time split + global scaler leak
split = int(len(uniq_dates) * 0.7)
train_d, test_d = set(uniq_dates[:split]), set(uniq_dates[split:])
m_tr = dates.isin(train_d)
m_te = dates.isin(test_d)
pred_g = fit_predict_ridge(X.loc[m_tr], y.loc[m_tr], X.loc[m_te], "global")
pred_c = fit_predict_ridge(X.loc[m_tr], y.loc[m_tr], X.loc[m_te], "train")
ic_global = spearman_ic_series(pred_g, y.loc[m_te])
ic_clean_scale = spearman_ic_series(pred_c, y.loc[m_te])
print(f"LEAK global_scaler RankIC={ic_global:.4f}")
print(f"CLEAN train_only_scaler RankIC={ic_clean_scale:.4f}")

# 3) Unpurged KFold vs purged+embargo
def cv_ic(purged: bool) -> float:
    preds = []
    if purged:
        folds = purged_kfold_indices(uniq_dates, N_FOLDS, HORIZON, EMBARGO)
        for tr_d, te_d in folds:
            tr_set, te_set = set(tr_d), set(te_d)
            mtr = dates.isin(tr_set)
            mte = dates.isin(te_set)
            if mtr.sum() < 100 or mte.sum() < 50:
                continue
            p = fit_predict_ridge(X.loc[mtr], y.loc[mtr], X.loc[mte], "train")
            preds.append(pd.concat([p, y.loc[mte]], axis=1))
    else:
        # LEAK: KFold on rows ignoring time / label overlap
        kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=0)
        arr_idx = np.arange(len(X))
        for tr, te in kf.split(arr_idx):
            p = fit_predict_ridge(X.iloc[tr], y.iloc[tr], X.iloc[te], "train")
            preds.append(pd.concat([p, y.iloc[te]], axis=1))
    big = pd.concat(preds)
    return spearman_ic_series(big.iloc[:, 0], big.iloc[:, 1])

ic_unpurged = cv_ic(False)
ic_purged = cv_ic(True)
print(f"LEAK unpurged_shuffled_KFold RankIC={ic_unpurged:.4f}")
print(f"CLEAN purged_KFold+embargo RankIC={ic_purged:.4f}")
print("teach: failures are usually in the pipeline — shuffle / global scale / unpurged CV inflate IC")

# Walk-forward expanding
print("\n=== walk-forward (expanding, train-only scaler) ===")
wf_preds = []
block = max(40, len(uniq_dates) // 8)
for end in range(block, len(uniq_dates) - HORIZON, block // 2):
    tr_set = set(uniq_dates[: end - EMBARGO])
    te_set = set(uniq_dates[end : min(len(uniq_dates), end + block // 2)])
    mtr, mte = dates.isin(tr_set), dates.isin(te_set)
    if mtr.sum() < 200 or mte.sum() < 30:
        continue
    p = fit_predict_ridge(X.loc[mtr], y.loc[mtr], X.loc[mte], "train")
    wf_preds.append(pd.concat([p.rename("p"), y.loc[mte].rename("y")], axis=1))
wf = pd.concat(wf_preds)
ic_wf = spearman_ic_series(wf["p"], wf["y"])
print(f"walk_forward RankIC={ic_wf:.4f}")

# Overfit trap
print("\n=== OVERFIT TRAP: deep GBM + many noise features ===")
X_noisy = add_noise_features(X, n_noise=40, seed=1)
# single time split
mtr, mte = dates.isin(train_d), dates.isin(test_d)
sc = StandardScaler().fit(X_noisy.loc[mtr])
Ztr, Zte = sc.transform(X_noisy.loc[mtr]), sc.transform(X_noisy.loc[mte])
gbm = HistGradientBoostingRegressor(
    max_depth=6, max_iter=200, learning_rate=0.05, random_state=0
)
gbm.fit(Ztr, y.loc[mtr])
pred_tr = pd.Series(gbm.predict(Ztr), index=X_noisy.loc[mtr].index)
pred_te = pd.Series(gbm.predict(Zte), index=X_noisy.loc[mte].index)
ic_tr = spearman_ic_series(pred_tr, y.loc[mtr])
ic_te = spearman_ic_series(pred_te, y.loc[mte])
# also daily CS IC mean
ics_tr = daily_cs_ic(pred_tr, y.loc[mtr])
ics_te = daily_cs_ic(pred_te, y.loc[mte])
print(f"overfit_trap train_RankIC={ic_tr:.4f} OOS_RankIC={ic_te:.4f}")
print(f"overfit_trap train_mean_daily_CS_IC={ics_tr.mean():.4f} OOS_mean_daily_CS_IC={ics_te.mean():.4f}")
print("teach: high train IC + noise features + deep tree ≠ OOS edge; record trial count")

# Chart leak vs clean
fig, ax = plt.subplots(figsize=(8, 4))
labels = ["shuffle", "global\nscaler", "unpurged\nKFold", "train\nscaler", "purged\n+embargo", "walk\nforward"]
vals = [ic_shuffle, ic_global, ic_unpurged, ic_clean_scale, ic_purged, ic_wf]
colors = ["#c45911", "#c45911", "#c45911", "#1f4e79", "#1f4e79", "#1f4e79"]
ax.bar(labels, vals, color=colors)
ax.axhline(0, color="k", lw=0.5)
ax.set_ylabel("RankIC")
ax.set_title("Leak (orange) vs clean (blue) RankIC")
fig.tight_layout(); fig.savefig(PUBLIC / "leak_vs_clean_ic.png", dpi=120); plt.close()
print("chart", PUBLIC / "leak_vs_clean_ic.png")

fig, ax = plt.subplots(figsize=(6, 4))
ax.bar(["train", "OOS"], [ic_tr, ic_te], color=["#9dc3e6", "#c45911"])
ax.set_ylabel("RankIC"); ax.set_title("Overfit trap: deep GBM + 40 noise features")
fig.tight_layout(); fig.savefig(PUBLIC / "overfit_trap_ic.png", dpi=120); plt.close()
print("chart", PUBLIC / "overfit_trap_ic.png")

# Save frame for lab 02
from pathlib import Path as _P
_out = _P(__file__).resolve().parent / "data"
_out.mkdir(exist_ok=True)
df.to_pickle(_out / "ml_frame.pkl")
rets.to_csv(_out / "rets_subset.csv")
print("saved", _out / "ml_frame.pkl")
print("disclaimer: synthetic weak panel — learning only, not investment advice")
