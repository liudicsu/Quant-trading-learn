"""P5 lab 02: ridge vs GBM baselines, importance/SHAP, calibration, bet sizing, Qlib-style.
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
    daily_cs_ic,
    dsr_from_pnl,
    load_weak_subset,
    pred_to_ls_pnl,
    purged_kfold_indices,
    spearman_ic_series,
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

feat_cols = [c for c in df.columns if c.startswith(("mom_", "vol_", "rank_"))]
# Substitution effect: duplicate mom_20 with noise
rng = np.random.default_rng(0)
df = df.copy()
df["mom_20_dup"] = df["mom_20"] + rng.normal(0, 0.01, size=len(df))
feat_cols_sub = feat_cols + ["mom_20_dup"]

print("=== parameters ===")
print(f"reuse lab01 frame rows={len(df)} HORIZON={HORIZON} purged folds={N_FOLDS} embargo={EMBARGO}")
print(f"LightGBM available={HAS_LGB}; SHAP available={HAS_SHAP}")
print("eval: RankIC + net SR (shared cost) + DSR over configs — NOT accuracy")
print("cite: Qlib docs — Alpha158 handler + LGBModel (qlib.contrib.model.gbdt) workflow")
print("cite: AFML ch.10 bet sizing from predicted probabilities")
print("frontier: arXiv:2511.18578 Re(Visiting) TSFMs in Finance — zero-shot Chronos/TimesFM underperform LightGBM/CatBoost on excess returns")
print("frontier: arXiv:2412.09880 — baseline TimesFM unsatisfactory on price prediction before finance fine-tune")
print("frontier: arXiv:2606.27100 — TSFM gains vs random walk small/sparse on equity returns")
print("LLM agents deferred to P8")

dates = df.index.get_level_values(0)
uniq = np.array(sorted(dates.unique()))
folds = purged_kfold_indices(uniq, N_FOLDS, HORIZON, EMBARGO)
y = df["fwd_ret"]
X = df[feat_cols]


def purged_oof_predict(model_factory, X, y, feat=feat_cols):
    oof = pd.Series(np.nan, index=X.index)
    for tr_d, te_d in folds:
        mtr = dates.isin(set(tr_d))
        mte = dates.isin(set(te_d))
        if mtr.sum() < 200 or mte.sum() < 50:
            continue
        sc = StandardScaler().fit(X.loc[mtr, feat])
        model = model_factory()
        model.fit(sc.transform(X.loc[mtr, feat]), y.loc[mtr])
        oof.loc[mte] = model.predict(sc.transform(X.loc[mte, feat]))
    return oof.dropna()


configs = {}
print("\n=== baselines: Ridge vs LightGBM (purged OOF) ===")

def ridge_factory():
    return Ridge(alpha=1.0)

oof_ridge = purged_oof_predict(ridge_factory, X, y)
ic_ridge = spearman_ic_series(oof_ridge, y.loc[oof_ridge.index])
net_r, turn_r = pred_to_ls_pnl(oof_ridge, rets)
dsr_r = dsr_from_pnl(net_r, n_trials=4)
configs["ridge"] = dict(ic=ic_ridge, net_sr=float(net_r.mean()/net_r.std(ddof=1)*ANN), turn=float(turn_r.mean()), dsr=dsr_r["DSR"], oof=oof_ridge)
print(f"ridge  RankIC={ic_ridge:.4f} net_SR={configs['ridge']['net_sr']:.3f} turn={configs['ridge']['turn']:.4f} DSR={dsr_r['DSR']:.3f}")

if HAS_LGB:
    def lgb_factory():
        return lgb.LGBMRegressor(
            n_estimators=80, learning_rate=0.05, max_depth=4, subsample=0.8,
            colsample_bytree=0.8, random_state=0, verbosity=-1,
        )
    oof_lgb = purged_oof_predict(lgb_factory, X, y)
else:
    from sklearn.ensemble import HistGradientBoostingRegressor
    def lgb_factory():
        return HistGradientBoostingRegressor(max_depth=4, max_iter=80, learning_rate=0.05, random_state=0)
    oof_lgb = purged_oof_predict(lgb_factory, X, y)
    print("note: LightGBM import failed — using sklearn HistGradientBoostingRegressor")

ic_lgb = spearman_ic_series(oof_lgb, y.loc[oof_lgb.index])
net_l, turn_l = pred_to_ls_pnl(oof_lgb, rets)
dsr_l = dsr_from_pnl(net_l, n_trials=4)
configs["gbm"] = dict(ic=ic_lgb, net_sr=float(net_l.mean()/net_l.std(ddof=1)*ANN), turn=float(turn_l.mean()), dsr=dsr_l["DSR"], oof=oof_lgb)
print(f"gbm    RankIC={ic_lgb:.4f} net_SR={configs['gbm']['net_sr']:.3f} turn={configs['gbm']['turn']:.4f} DSR={dsr_l['DSR']:.3f} backend={'lightgbm' if HAS_LGB else 'HistGBM'}")
print(f"DSR uses n_trials={4} (= configs tried: ridge, gbm, +2 foils below)")

# Two foils for DSR trial count honesty
oof_ridge_hi = purged_oof_predict(lambda: Ridge(alpha=0.01), X, y)
oof_ridge_lo = purged_oof_predict(lambda: Ridge(alpha=100.0), X, y)
for name, oof in [("ridge_alpha0.01", oof_ridge_hi), ("ridge_alpha100", oof_ridge_lo)]:
    ic = spearman_ic_series(oof, y.loc[oof.index])
    net, turn = pred_to_ls_pnl(oof, rets)
    dsr = dsr_from_pnl(net, n_trials=4)
    configs[name] = dict(ic=ic, net_sr=float(net.mean()/net.std(ddof=1)*ANN), turn=float(turn.mean()), dsr=dsr["DSR"])
    print(f"{name:16s} RankIC={ic:.4f} net_SR={configs[name]['net_sr']:.3f} DSR={dsr['DSR']:.3f}")

print("\n=== feature importance: MDI / MDA / SHAP + substitution ===")
# Fit one purged train fold for importances
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

# MDI
if hasattr(gbm, "feature_importances_"):
    mdi = pd.Series(gbm.feature_importances_, index=feat_cols_sub).sort_values(ascending=False)
else:
    mdi = pd.Series(0.0, index=feat_cols_sub)
print("MDI top:")
print(mdi.head(8).to_string())

# MDA on purged test fold
r = permutation_importance(gbm, Zte, yte, n_repeats=10, random_state=0, scoring="neg_mean_squared_error")
mda = pd.Series(r.importances_mean, index=feat_cols_sub).sort_values(ascending=False)
print("MDA (purged test fold) top:")
print(mda.head(8).to_string())
print(
    f"substitution: MDI mom_20={mdi.get('mom_20', float('nan')):.4f} mom_20_dup={mdi.get('mom_20_dup', float('nan')):.4f} "
    f"— correlated duplicates SPLIT importance (substitution effect)"
)

if HAS_SHAP:
    explainer = shap.Explainer(gbm, Ztr[:500])
    sv = explainer(Zte[:300])
    shap_mean = pd.Series(np.abs(sv.values).mean(axis=0), index=feat_cols_sub).sort_values(ascending=False)
    print("SHAP mean(|value|) top:")
    print(shap_mean.head(8).to_string())
    fig, ax = plt.subplots(figsize=(7, 4))
    shap_mean.head(8).iloc[::-1].plot(kind="barh", ax=ax, color="#1f4e79")
    ax.set_title("SHAP mean |value| (sample)")
    fig.tight_layout(); fig.savefig(PUBLIC / "shap_importance.png", dpi=120); plt.close()
    print("chart", PUBLIC / "shap_importance.png")
else:
    print(f"SHAP not available ({SHAP_ERR if not HAS_SHAP else 'n/a'}) — reporting MDI/MDA only")

fig, ax = plt.subplots(figsize=(8, 4))
comp = pd.DataFrame({"MDI": mdi, "MDA": mda}).fillna(0)
comp = comp.loc[comp.abs().sum(axis=1).sort_values(ascending=False).head(8).index]
comp.plot(kind="bar", ax=ax)
ax.set_title("MDI vs MDA (with mom_20_dup substitution)")
fig.tight_layout(); fig.savefig(PUBLIC / "mdi_mda_importance.png", dpi=120); plt.close()
print("chart", PUBLIC / "mdi_mda_importance.png")

print("\n=== probability calibration + AFML ch.10 bet sizing ===")
# Binary meta-label model
ym = df["meta_y"]
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
# reliability
prob_true, prob_pred = calibration_curve(ym_o, oof_prob, n_bins=8, strategy="quantile")
# isotonic calibration on first half of OOF
mid = oof_prob.index[len(oof_prob)//2]
# use time order
ordered = oof_prob.sort_index()
ym_ord = ym_o.loc[ordered.index]
cut = int(len(ordered) * 0.5)
iso = IsotonicRegression(out_of_bounds="clip")
iso.fit(ordered.iloc[:cut], ym_ord.iloc[:cut])
cal = pd.Series(iso.predict(ordered.iloc[cut:]), index=ordered.index[cut:])
prob_true2, prob_pred2 = calibration_curve(ym_ord.iloc[cut:], cal, n_bins=8, strategy="quantile")
print(f"raw_prob mean={oof_prob.mean():.3f} meta_base_rate={ym_o.mean():.3f}")
print("calibration: reliability curve raw vs isotonic (Platt/logit also common; we show isotonic)")

# Bet sizing: AFML-style monotone size from probability — here size ∝ (2p-1)+
side = np.sign(df.loc[cal.index, "mom_20"]).replace(0, np.nan)
size = (2 * cal - 1).clip(lower=0)  # long-only confidence when p>0.5
# Build weights: CS rank of size * side
score = (side * size).dropna()
net_bet, turn_bet = pred_to_ls_pnl(score, rets)
print(f"bet_sizing net_SR={float(net_bet.mean()/net_bet.std(ddof=1)*ANN):.3f} turn={float(turn_bet.mean()):.4f}")
print("teach: size from calibrated probs, not raw scores; bad calibration → bad Kelly-like bets")

fig, ax = plt.subplots(figsize=(6, 5))
ax.plot([0, 1], [0, 1], "k--", label="perfect")
ax.plot(prob_pred, prob_true, "o-", label="raw logit")
ax.plot(prob_pred2, prob_true2, "s-", label="isotonic")
ax.set_xlabel("predicted p"); ax.set_ylabel("empirical frequency")
ax.set_title("Reliability curve (meta-label)")
ax.legend(); ax.grid(True, alpha=0.3)
fig.tight_layout(); fig.savefig(PUBLIC / "calibration_reliability.png", dpi=120); plt.close()
print("chart", PUBLIC / "calibration_reliability.png")

print("\n=== Qlib-style workflow (plain pandas equivalent) ===")
print("Qlib pattern (from official docs): Alpha158 DataHandler → DatasetH segments → LGBModel.fit → SignalRecord")
print("pandas equivalent here:")
print("  1) features_long ≈ Alpha158 processors (mom/vol/rank; CSZScoreNorm ↔ StandardScaler on train fold)")
print("  2) purged segments ≈ DatasetH train/valid/test without label overlap")
print("  3) LGBMRegressor/Ridge ≈ LGBModel")
print("  4) pred_to_ls_pnl ≈ portfolio analysis from scores")
print("We do NOT claim Qlib install in this lab; cite docs and mirror the stages.")

# Baseline comparison chart
fig, ax = plt.subplots(figsize=(8, 4))
names = list(configs.keys())
ics = [configs[n]["ic"] for n in names]
srs = [configs[n]["net_sr"] for n in names]
x = np.arange(len(names))
ax.bar(x - 0.2, ics, 0.4, label="RankIC")
ax.bar(x + 0.2, [s / 10 for s in srs], 0.4, label="net_SR/10")
ax.set_xticks(x); ax.set_xticklabels(names, rotation=20, ha="right")
ax.set_title("Configs: RankIC and net SR (scaled)")
ax.legend(); ax.grid(True, axis="y", alpha=0.3)
fig.tight_layout(); fig.savefig(PUBLIC / "ridge_vs_gbm.png", dpi=120); plt.close()
print("chart", PUBLIC / "ridge_vs_gbm.png")

eq = (1 + net_l.fillna(0)).cumprod()
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot((1 + net_r.fillna(0)).cumprod(), label="ridge net")
ax.plot(eq, label="gbm net")
ax.legend(); ax.grid(True, alpha=0.3); ax.set_title("OOF L/S net NAV (purged)")
fig.tight_layout(); fig.savefig(PUBLIC / "pipeline_nav.png", dpi=120); plt.close()
print("chart", PUBLIC / "pipeline_nav.png")
print("disclaimer: weak synthetic panel — learning only; TSFM papers cited, not re-run here")
