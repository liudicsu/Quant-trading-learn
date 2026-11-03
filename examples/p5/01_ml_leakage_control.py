"""P5 lab 01: vol-scaled TB labels, purged CV, daily CS RankIC primary, side-by-side table.
Learning only — not investment advice. Data: P4 WEAK panel subsample.
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import HistGradientBoostingRegressor

from _common import (
    ANN,
    EMBARGO,
    HORIZON,
    N_ASSETS_USE,
    N_FOLDS,
    PUBLIC,
    TB_K,
    VOL_SPAN,
    add_noise_features,
    load_weak_subset,
    make_ml_frame,
    mean_daily_cs_ic,
    pooled_spearman,
    purged_kfold_indices,
)

print("=== parameters ===")
print(f"P4 WEAK panel subsample n_assets={N_ASSETS_USE}; HORIZON={HORIZON}; N_FOLDS={N_FOLDS}; EMBARGO={EMBARGO}")
print(f"TB: AFML ch.3 vol-scaled bands pt=sl=k*sigma_t with k={TB_K}, sigma=lagged EWMA span={VOL_SPAN}")
print("PRIMARY metric: mean daily cross-sectional RankIC (+ t-stat / ICIR)")
print("pooled Spearman is a COUNTEREXAMPLE (mixes time-series + cross-sectional variation)")
print("cite: López de Prado AFML ch.3 (vol-scaled barriers), ch.7 (purged CV)")
print("look-ahead: features ≤ t; sigma_t = EWMA.shift(1); labels walk t+1..; purge on label-span overlap")

rets, raw, raw2, log_mcap, meta, mu = load_weak_subset()
print(f"MU_WEAK={mu} panel {rets.shape}")

df = make_ml_frame(rets, meta=meta, raw=raw)
feat_cols = [c for c in df.columns if c.startswith(("mom_", "vol_", "rank_"))]
print(f"rows={len(df)} features={feat_cols}")

print("\n=== label construction look-ahead audit ===")
print("fwd_ret[t] = sum(rets[t+1..t+h])")
print(f"TB: pt=sl={TB_K}*sigma_t per asset/time; sigma from lagged EWMA — NOT fixed 2%")
print("why fixed 2% is wrong: high-vol names hit barriers by noise; low-vol almost never touch → labels become vol-driven")
print(f"tb_pt (vol-scaled) describe:\n{df['tb_pt'].describe().to_string()}")
print(f"tb_side value counts:\n{df['tb_side'].value_counts().to_string()}")
print(f"meta_y mean (hit rate)={df['meta_y'].mean():.3f}")

dates = df.index.get_level_values(0)
uniq_dates = np.array(sorted(dates.unique()))
X = df[feat_cols]
y = df["fwd_ret"]


def fit_predict(model_factory, Xtr, ytr, Xte, scale_mode: str):
    if scale_mode == "global":
        sc = StandardScaler().fit(pd.concat([Xtr, Xte]))
    else:
        sc = StandardScaler().fit(Xtr)
    model = model_factory()
    model.fit(sc.transform(Xtr), ytr)
    return pd.Series(model.predict(sc.transform(Xte)), index=Xte.index)


def ridge_factory():
    return Ridge(alpha=1.0)


def summarize(name, pred, y):
    m = mean_daily_cs_ic(pred, y)
    pooled = pooled_spearman(pred, y)
    print(
        f"{name:28s} mean_daily_CS_RankIC={m['mean_ic']:+.4f} t={m['t_stat']:.2f} "
        f"ICIR={m['ICIR']:.2f} n_days={m['n_days']}  | pooled_Spearman={pooled:+.4f} (counterexample)"
    )
    return m


print("\n=== PRIMARY metric note ===")
print("mean daily CS RankIC = average over dates of Spearman(pred, y) within that day's cross-section")
print("pooled Spearman stacks all (date,asset) rows — confounds TS persistence with CS ranking")

# --- Oracle upper bound ---
print("\n=== oracle upper bound (beta_true as score) ===")
oracle_pred = df["oracle_beta"]
m_oracle = summarize("oracle_beta_true", oracle_pred, y)

# --- Leaks ---
print("\n=== LEAK demos (inflated) vs CLEAN purged ===")
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0, shuffle=True)
pred_sh = fit_predict(ridge_factory, Xtr, ytr, Xte, "train")
m_shuffle = summarize("LEAK shuffle_split", pred_sh, yte)

# unpurged shuffled KFold OOF
oof_unp = pd.Series(np.nan, index=X.index)
kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=0)
for tr, te in kf.split(np.arange(len(X))):
    oof_unp.iloc[te] = fit_predict(ridge_factory, X.iloc[tr], y.iloc[tr], X.iloc[te], "train").values
oof_unp = oof_unp.dropna()
m_unp = summarize("LEAK unpurged_KFold", oof_unp, y.loc[oof_unp.index])

# purged ridge OOF
folds = purged_kfold_indices(uniq_dates, N_FOLDS, HORIZON, EMBARGO)
oof_ridge = pd.Series(np.nan, index=X.index)
for tr_d, te_d in folds:
    mtr, mte = dates.isin(set(tr_d)), dates.isin(set(te_d))
    if mtr.sum() < 200 or mte.sum() < 50:
        continue
    oof_ridge.loc[mte] = fit_predict(ridge_factory, X.loc[mtr], y.loc[mtr], X.loc[mte], "train")
oof_ridge = oof_ridge.dropna()
m_ridge = summarize("CLEAN purged_ridge", oof_ridge, y.loc[oof_ridge.index])

# purged GBM
try:
    import lightgbm as lgb
    def gbm_factory():
        return lgb.LGBMRegressor(
            n_estimators=80, learning_rate=0.05, max_depth=4, subsample=0.8,
            colsample_bytree=0.8, random_state=0, verbosity=-1,
        )
    gbm_name = "lightgbm"
except Exception:
    def gbm_factory():
        return HistGradientBoostingRegressor(max_depth=4, max_iter=80, learning_rate=0.05, random_state=0)
    gbm_name = "HistGBM"

oof_gbm = pd.Series(np.nan, index=X.index)
for tr_d, te_d in folds:
    mtr, mte = dates.isin(set(tr_d)), dates.isin(set(te_d))
    if mtr.sum() < 200 or mte.sum() < 50:
        continue
    oof_gbm.loc[mte] = fit_predict(gbm_factory, X.loc[mtr], y.loc[mtr], X.loc[mte], "train")
oof_gbm = oof_gbm.dropna()
m_gbm = summarize(f"CLEAN purged_GBM({gbm_name})", oof_gbm, y.loc[oof_gbm.index])

# overfit GBM: deep + noise, report train vs OOS daily CS IC
print("\n=== OVERFIT trap (deep GBM + 40 noise features) ===")
X_noisy = add_noise_features(X, n_noise=40, seed=1)
split = int(len(uniq_dates) * 0.7)
train_d, test_d = set(uniq_dates[:split]), set(uniq_dates[split:])
mtr, mte = dates.isin(train_d), dates.isin(test_d)
sc = StandardScaler().fit(X_noisy.loc[mtr])
gbm_over = HistGradientBoostingRegressor(max_depth=6, max_iter=200, learning_rate=0.05, random_state=0)
gbm_over.fit(sc.transform(X_noisy.loc[mtr]), y.loc[mtr])
pred_tr = pd.Series(gbm_over.predict(sc.transform(X_noisy.loc[mtr])), index=X_noisy.loc[mtr].index)
pred_te = pd.Series(gbm_over.predict(sc.transform(X_noisy.loc[mte])), index=X_noisy.loc[mte].index)
m_over_tr = summarize("overfit_GBM train", pred_tr, y.loc[mtr])
m_over_te = summarize("overfit_GBM OOS", pred_te, y.loc[mte])

# Side-by-side table
print("\n=== SIDE-BY-SIDE TABLE (primary = mean daily CS RankIC) ===")
rows = [
    ("oracle_beta_true", m_oracle["mean_ic"], m_oracle["t_stat"], m_oracle["ICIR"], "upper bound"),
    ("LEAK unpurged_KFold", m_unp["mean_ic"], m_unp["t_stat"], m_unp["ICIR"], "pipeline illusion"),
    ("LEAK shuffle_split", m_shuffle["mean_ic"], m_shuffle["t_stat"], m_shuffle["ICIR"], "pipeline illusion"),
    ("purged_ridge", m_ridge["mean_ic"], m_ridge["t_stat"], m_ridge["ICIR"], "weak signal recovered"),
    ("purged_GBM", m_gbm["mean_ic"], m_gbm["t_stat"], m_gbm["ICIR"], "weak signal recovered"),
    ("overfit_GBM_OOS", m_over_te["mean_ic"], m_over_te["t_stat"], m_over_te["ICIR"], "train high / OOS collapse"),
]
print(f"{'model':22s} {'mean_CS_IC':>10} {'t':>8} {'ICIR':>8}  note")
for name, ic, tstat, icir, note in rows:
    print(f"{name:22s} {ic:+10.4f} {tstat:8.2f} {icir:8.2f}  {note}")
print("teach three cases:")
print("  (a) ILLUSION: leak protocols inflate IC (unpurged/shuffle) without a real OOS edge")
print("  (b) WEAK RECOVERABLE: purged ridge/GBM still recover mean CS IC ~ +0.04 on this planted weak panel")
print("  (c) REAL BUT COST-WIPED: see lab 02 — positive IC can still yield net SR≤0 after shared costs")
print(f"verify: purged_ridge mean daily CS IC = {m_ridge['mean_ic']:.4f} (reviewer ~+0.040)")

# Charts
fig, ax = plt.subplots(figsize=(9, 4))
names = [r[0] for r in rows]
ics = [r[1] for r in rows]
colors = ["#2e7d32", "#c45911", "#c45911", "#1f4e79", "#1f4e79", "#7b2d8e"]
ax.bar(names, ics, color=colors)
ax.axhline(0, color="k", lw=0.5)
ax.set_ylabel("mean daily CS RankIC")
ax.set_title("Oracle / leaked / purged / overfit (primary metric)")
plt.xticks(rotation=25, ha="right")
fig.tight_layout(); fig.savefig(PUBLIC / "side_by_side_ic.png", dpi=120); plt.close()
print("chart", PUBLIC / "side_by_side_ic.png")

fig, ax = plt.subplots(figsize=(6, 4))
ax.bar(["train", "OOS"], [m_over_tr["mean_ic"], m_over_te["mean_ic"]], color=["#9dc3e6", "#c45911"])
ax.set_ylabel("mean daily CS RankIC")
ax.set_title("Overfit trap: deep GBM + noise features")
fig.tight_layout(); fig.savefig(PUBLIC / "overfit_trap_ic.png", dpi=120); plt.close()

fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(
    ["shuffle", "unpurged KF", "purged ridge"],
    [m_shuffle["mean_ic"], m_unp["mean_ic"], m_ridge["mean_ic"]],
    color=["#c45911", "#c45911", "#1f4e79"],
)
ax.set_ylabel("mean daily CS RankIC")
ax.set_title("Leak (orange) vs purged (blue)")
fig.tight_layout(); fig.savefig(PUBLIC / "leak_vs_clean_ic.png", dpi=120); plt.close()
print("chart", PUBLIC / "leak_vs_clean_ic.png")

# save artifacts for lab 02
out = Path(__file__).resolve().parent / "data"
out.mkdir(exist_ok=True)
df.to_pickle(out / "ml_frame.pkl")
rets.to_csv(out / "rets_subset.csv")
meta.to_csv(out / "meta_subset.csv")
pd.Series({"purged_ridge_mean_cs_ic": m_ridge["mean_ic"], "oracle_mean_cs_ic": m_oracle["mean_ic"]}).to_json(
    out / "lab01_metrics.json"
)
# save OOF preds
oof_ridge.to_frame("pred").to_pickle(out / "oof_ridge.pkl")
oof_gbm.to_frame("pred").to_pickle(out / "oof_gbm.pkl")
print("saved artifacts for lab 02")
print("disclaimer: synthetic weak panel — learning only")
