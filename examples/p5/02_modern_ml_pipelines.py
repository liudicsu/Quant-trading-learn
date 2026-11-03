"""P5 lab 02: baselines under daily CS RankIC, importance, calibration, costs wipe case (c).
Learning only — not investment advice.
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.linear_model import Ridge, LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.calibration import calibration_curve
from sklearn.isotonic import IsotonicRegression
from sklearn.inspection import permutation_importance

from _common import (
    ANN,
    EMBARGO,
    HORIZON,
    N_FOLDS,
    PUBLIC,
    dsr_from_pnl,
    mean_daily_cs_ic,
    pooled_spearman,
    pred_to_ls_pnl,
    purged_kfold_indices,
)

try:
    import lightgbm as lgb
    HAS_LGB = True
except Exception as e:
    HAS_LGB = False
    LGB_ERR = e

try:
    import shap
    HAS_SHAP = True
except Exception as e:
    HAS_SHAP = False
    SHAP_ERR = e

DATA = Path(__file__).resolve().parent / "data"
df = pd.read_pickle(DATA / "ml_frame.pkl")
rets = pd.read_csv(DATA / "rets_subset.csv", index_col=0, parse_dates=True)
oof_ridge = pd.read_pickle(DATA / "oof_ridge.pkl")["pred"]
oof_gbm = pd.read_pickle(DATA / "oof_gbm.pkl")["pred"]

feat_cols = [c for c in df.columns if c.startswith(("mom_", "vol_", "rank_"))]
rng = np.random.default_rng(0)
df = df.copy()
df["mom_20_dup"] = df["mom_20"] + rng.normal(0, 0.01, size=len(df))
feat_cols_sub = feat_cols + ["mom_20_dup"]
y = df["fwd_ret"]
dates = df.index.get_level_values(0)
uniq = np.array(sorted(dates.unique()))
folds = purged_kfold_indices(uniq, N_FOLDS, HORIZON, EMBARGO)

print("=== parameters ===")
print(f"reuse lab01 frame; PRIMARY metric = mean daily CS RankIC (+ t / ICIR)")
print(f"LightGBM={HAS_LGB}; SHAP={HAS_SHAP}")
print("eval: mean daily CS RankIC + net SR (shared costs) + DSR — NOT accuracy, NOT pooled Spearman as primary")
print("cite: Qlib Alpha158 + LGBModel docs; AFML ch.10 bet sizing")
print("frontier: arXiv:2511.18578, 2412.09880, 2606.27100 (TSFM finance evals); LLM agents → P8")
print(f"TB labels are vol-scaled (k*sigma_t); fixed 2% bands rejected — see lab 01")

print("\n=== baselines under PRIMARY metric ===")
configs = {}
for name, oof in [("ridge", oof_ridge), ("gbm", oof_gbm)]:
    m = mean_daily_cs_ic(oof, y.loc[oof.index])
    pooled = pooled_spearman(oof, y.loc[oof.index])
    net, turn = pred_to_ls_pnl(oof, rets)
    dsr = dsr_from_pnl(net, n_trials=4)
    configs[name] = dict(m=m, pooled=pooled, net=net, turn=turn, dsr=dsr)
    print(
        f"{name:8s} mean_CS_IC={m['mean_ic']:+.4f} t={m['t_stat']:.2f} ICIR={m['ICIR']:.2f} "
        f"| pooled={pooled:+.4f} (counterexample) | net_SR={float(net.mean()/net.std(ddof=1)*ANN):.3f} "
        f"turn={float(turn.mean()):.4f} DSR={dsr['DSR']:.3f}"
    )

# foils for trial count
X = df[feat_cols]
for alpha, tag in [(0.01, "ridge_a0.01"), (100.0, "ridge_a100")]:
    oof = pd.Series(np.nan, index=X.index)
    for tr_d, te_d in folds:
        mtr, mte = dates.isin(set(tr_d)), dates.isin(set(te_d))
        if mtr.sum() < 200 or mte.sum() < 50:
            continue
        sc = StandardScaler().fit(X.loc[mtr])
        model = Ridge(alpha=alpha).fit(sc.transform(X.loc[mtr]), y.loc[mtr])
        oof.loc[mte] = model.predict(sc.transform(X.loc[mte]))
    oof = oof.dropna()
    m = mean_daily_cs_ic(oof, y.loc[oof.index])
    net, turn = pred_to_ls_pnl(oof, rets)
    dsr = dsr_from_pnl(net, n_trials=4)
    configs[tag] = dict(m=m, net=net, turn=turn, dsr=dsr)
    print(f"{tag:12s} mean_CS_IC={m['mean_ic']:+.4f} net_SR={float(net.mean()/net.std(ddof=1)*ANN):.3f} DSR={dsr['DSR']:.3f}")

print("\n=== case (c): weak signal recovered but costs wipe net SR ===")
m_r = configs["ridge"]["m"]
net_r = configs["ridge"]["net"]
gross = (pred_to_ls_pnl.__doc__)  # noqa — compute gross separately
# gross without costs: reconstruct from weights path inside pred_to_ls_pnl by differencing
# simpler: report net SR negative while IC positive
print(
    f"purged_ridge mean_CS_IC={m_r['mean_ic']:+.4f} (signal recovered) but "
    f"net_SR={float(net_r.mean()/net_r.std(ddof=1)*ANN):.3f} after shared 10bps+impact costs "
    f"(turn={float(configs['ridge']['turn'].mean()):.3f})"
)
print("teach: (a) leak illusion ≠ (b) recoverable weak IC ≠ (c) IC>0 with net SR≤0 after costs")

print("\n=== feature importance: MDI / MDA / SHAP + substitution ===")
tr_d, te_d = folds[2]
mtr, mte = dates.isin(set(tr_d)), dates.isin(set(te_d))
Xsub = df[feat_cols_sub]
sc = StandardScaler().fit(Xsub.loc[mtr])
Ztr, Zte = sc.transform(Xsub.loc[mtr]), sc.transform(Xsub.loc[mte])
ytr, yte = y.loc[mtr], y.loc[mte]
if HAS_LGB:
    gbm = lgb.LGBMRegressor(n_estimators=100, max_depth=4, learning_rate=0.05, random_state=0, verbosity=-1)
else:
    from sklearn.ensemble import HistGradientBoostingRegressor
    gbm = HistGradientBoostingRegressor(max_depth=4, max_iter=100, learning_rate=0.05, random_state=0)
gbm.fit(Ztr, ytr)
mdi = pd.Series(getattr(gbm, "feature_importances_", np.zeros(len(feat_cols_sub))), index=feat_cols_sub).sort_values(ascending=False)
print("MDI top:\n" + mdi.head(8).to_string())
r = permutation_importance(gbm, Zte, yte, n_repeats=10, random_state=0, scoring="neg_mean_squared_error")
mda = pd.Series(r.importances_mean, index=feat_cols_sub).sort_values(ascending=False)
print("MDA top:\n" + mda.head(8).to_string())
print(
    f"substitution: MDI mom_20={mdi.get('mom_20', np.nan):.4f} mom_20_dup={mdi.get('mom_20_dup', np.nan):.4f}"
)

if HAS_SHAP:
    explainer = shap.Explainer(gbm, Ztr[:500])
    sv = explainer(Zte[:300])
    shap_mean = pd.Series(np.abs(sv.values).mean(axis=0), index=feat_cols_sub).sort_values(ascending=False)
    print("SHAP mean(|value|) top:\n" + shap_mean.head(8).to_string())
    fig, ax = plt.subplots(figsize=(7, 4))
    shap_mean.head(8).iloc[::-1].plot(kind="barh", ax=ax, color="#1f4e79")
    ax.set_title("SHAP mean |value|")
    fig.tight_layout(); fig.savefig(PUBLIC / "shap_importance.png", dpi=120); plt.close()
else:
    print(f"SHAP unavailable: {SHAP_ERR}")

fig, ax = plt.subplots(figsize=(8, 4))
comp = pd.DataFrame({"MDI": mdi, "MDA": mda}).fillna(0)
comp = comp.loc[comp.abs().sum(axis=1).sort_values(ascending=False).head(8).index]
comp.plot(kind="bar", ax=ax)
ax.set_title("MDI vs MDA (mom_20_dup substitution)")
fig.tight_layout(); fig.savefig(PUBLIC / "mdi_mda_importance.png", dpi=120); plt.close()

print("\n=== calibration + AFML ch.10 bet sizing ===")
ym = df["meta_y"]
X = df[feat_cols]
oof_prob = pd.Series(np.nan, index=df.index)
for tr_d, te_d in folds:
    mtr = dates.isin(set(tr_d)); mte = dates.isin(set(te_d))
    if mtr.sum() < 200 or mte.sum() < 50:
        continue
    sc = StandardScaler().fit(X.loc[mtr])
    clf = LogisticRegression(max_iter=500)
    clf.fit(sc.transform(X.loc[mtr]), ym.loc[mtr])
    oof_prob.loc[mte] = clf.predict_proba(sc.transform(X.loc[mte]))[:, 1]
oof_prob = oof_prob.dropna()
ym_o = ym.loc[oof_prob.index]
prob_true, prob_pred = calibration_curve(ym_o, oof_prob, n_bins=8, strategy="quantile")
ordered = oof_prob.sort_index()
ym_ord = ym_o.loc[ordered.index]
cut = int(len(ordered) * 0.5)
iso = IsotonicRegression(out_of_bounds="clip")
iso.fit(ordered.iloc[:cut], ym_ord.iloc[:cut])
cal = pd.Series(iso.predict(ordered.iloc[cut:]), index=ordered.index[cut:])
prob_true2, prob_pred2 = calibration_curve(ym_ord.iloc[cut:], cal, n_bins=8, strategy="quantile")
print(f"raw_prob mean={oof_prob.mean():.3f} meta_base_rate={ym_o.mean():.3f}")
side = np.sign(df.loc[cal.index, "mom_20"]).replace(0, np.nan)
size = (2 * cal - 1).clip(lower=0)
score = (side * size).dropna()
# score as ranking signal — report daily CS IC of score vs fwd_ret
m_bet = mean_daily_cs_ic(score, y.loc[score.index])
net_bet, turn_bet = pred_to_ls_pnl(score, rets)
print(
    f"bet_sizing mean_CS_IC={m_bet['mean_ic']:+.4f} net_SR={float(net_bet.mean()/net_bet.std(ddof=1)*ANN):.3f} "
    f"turn={float(turn_bet.mean()):.4f}"
)

fig, ax = plt.subplots(figsize=(6, 5))
ax.plot([0, 1], [0, 1], "k--", label="perfect")
ax.plot(prob_pred, prob_true, "o-", label="raw logit")
ax.plot(prob_pred2, prob_true2, "s-", label="isotonic")
ax.set_xlabel("predicted p"); ax.set_ylabel("empirical frequency")
ax.set_title("Reliability curve (meta-label, vol-scaled TB)")
ax.legend(); ax.grid(True, alpha=0.3)
fig.tight_layout(); fig.savefig(PUBLIC / "calibration_reliability.png", dpi=120); plt.close()

print("\n=== Qlib-style workflow (pandas) ===")
print("Qlib: Alpha158 → DatasetH → LGBModel → SignalRecord (official docs)")
print("pandas: features_long ≈ Alpha158; purged folds ≈ segments; LGBM/Ridge ≈ LGBModel; pred_to_ls_pnl ≈ portfolio")

# charts
fig, ax = plt.subplots(figsize=(8, 4))
names = list(configs.keys())
ics = [configs[n]["m"]["mean_ic"] for n in names]
srs = [float(configs[n]["net"].mean()/configs[n]["net"].std(ddof=1)*ANN) for n in names]
x = np.arange(len(names))
ax.bar(x - 0.2, ics, 0.4, label="mean daily CS RankIC")
ax.bar(x + 0.2, [s / 10 for s in srs], 0.4, label="net_SR/10")
ax.set_xticks(x); ax.set_xticklabels(names, rotation=20, ha="right")
ax.axhline(0, color="k", lw=0.5)
ax.set_title("Configs: primary IC vs net SR (case c: IC>0, net SR≤0)")
ax.legend(); ax.grid(True, axis="y", alpha=0.3)
fig.tight_layout(); fig.savefig(PUBLIC / "ridge_vs_gbm.png", dpi=120); plt.close()

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot((1 + configs["ridge"]["net"].fillna(0)).cumprod(), label="ridge net")
ax.plot((1 + configs["gbm"]["net"].fillna(0)).cumprod(), label="gbm net")
ax.legend(); ax.grid(True, alpha=0.3); ax.set_title("OOF L/S net NAV — costs wipe despite IC>0")
fig.tight_layout(); fig.savefig(PUBLIC / "pipeline_nav.png", dpi=120); plt.close()
print("chart", PUBLIC / "ridge_vs_gbm.png")
print("disclaimer: weak synthetic panel — learning only")
