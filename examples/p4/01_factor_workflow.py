"""P4 lab 01: factor construction, IC/RankIC/ICIR/decay, quantiles, FM, Harvey zoo, Alphalens-style.
Learning only — not investment advice.

Panel: 200 × 750 with planted beta_true and MU_TRUE premium; raw_factor contaminated by industry/size.
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
ensure_panel()
rets = pd.read_csv(DATA / "returns.csv", index_col=0, parse_dates=True)
raw = pd.read_csv(DATA / "raw_factor.csv", index_col=0, parse_dates=True)
log_mcap = pd.read_csv(DATA / "log_mcap.csv", index_col=0, parse_dates=True)
meta = pd.read_csv(DATA / "meta.csv").set_index("asset")
beta_true = meta["beta_true"]
ind = meta["industry"]

print("=== parameters ===")
print("panel", rets.shape[1], "assets x", rets.shape[0], "days; industries", int(ind.nunique()))
print("DGP: r = beta_true*f_true + beta_mkt*f_mkt + beta_size*f_size + industry + noise")
print("f_true has planted daily premium MU_TRUE=0.0025 (~63% ann per unit beta; exaggerated for teaching clarity)")
print("raw_factor = beta_true + 0.4*industry + 0.25*size_loading + noise  (nuisance contamination)")
print("look-ahead: factor[t] vs forward returns starting t+1; LS weights use shift(1); impact vol lagged")
print("cite: Fama & MacBeth 1973 JPE 81(3) 607-636 — cross-section then time-series mean of slopes")
print("cite: Fama & French 1993 JFE 33(1) 3-56 — Mkt-Rf, SMB, HML (FF3)")
print("cite: Fama & French 2015 JFE 116(1) 1-22 — FF5 = FF3 + RMW + CMA")
print("cite: Harvey, Liu & Zhu 2016 RFS 29(1) 5-68 — '...and the Cross-Section of Expected Returns'; t>3")
print("cite: Alphalens Reloaded docs (alphalens.ml4trading.io) — get_clean_factor_and_forward_returns + tear sheets")
print("cite: Qlib DataHandlerLP processors CSZScoreNorm / CSZFillna / Alpha158 (qlib.readthedocs.io)")
print("niche: quant-wiki factor taxonomy as foil only; frontier LLM formulaic mining deferred to P8 (not re-run)")


def winsorize_cs(df: pd.DataFrame, p: float = 0.01) -> pd.DataFrame:
    lo = df.quantile(p, axis=1)
    hi = df.quantile(1 - p, axis=1)
    return df.clip(lo, hi, axis=0)


def zscore_cs(df: pd.DataFrame) -> pd.DataFrame:
    mu = df.mean(axis=1)
    sd = df.std(axis=1, ddof=1).replace(0, np.nan)
    return df.sub(mu, axis=0).div(sd, axis=0)


def neutralize(df: pd.DataFrame, industry: pd.Series, logcap: pd.DataFrame) -> pd.DataFrame:
    """Cross-sectional residual: factor ~ C(industry) + log_mcap (regression residual)."""
    out = pd.DataFrame(np.nan, index=df.index, columns=df.columns)
    ind_dummies = pd.get_dummies(industry, prefix="ind", dtype=float)
    X_base = ind_dummies  # static across dates; append logcap each day
    for dt in df.index:
        y = df.loc[dt].astype(float)
        x_m = logcap.loc[dt].astype(float)
        X = pd.concat([X_base, x_m.rename("log_mcap")], axis=1).reindex(y.index)
        ok = y.notna() & X.notna().all(axis=1)
        if int(ok.sum()) < X.shape[1] + 5:
            continue
        Yv = y[ok].values
        Xv = np.column_stack([np.ones(int(ok.sum())), X.loc[ok].values])
        coef, *_ = np.linalg.lstsq(Xv, Yv, rcond=None)
        out.loc[dt, y[ok].index] = Yv - Xv @ coef
    return out


def mean_cs_corr(fac: pd.DataFrame, truth: pd.Series) -> float:
    cors = []
    for dt in fac.index[::5]:
        s = fac.loc[dt]
        c = s.corr(truth.reindex(s.index))
        if np.isfinite(c):
            cors.append(float(c))
    return float(np.mean(cors))


def forward_sum(rets: pd.DataFrame, h: int) -> pd.DataFrame:
    """At date t, sum of returns over [t+1, t+h] inclusive. Last h rows NaN."""
    out = pd.DataFrame(np.nan, index=rets.index, columns=rets.columns)
    vals = rets.values
    for i in range(len(rets) - h):
        out.iloc[i] = vals[i + 1 : i + 1 + h].sum(axis=0)
    return out


def spearman_ic(fac: pd.DataFrame, fwd: pd.DataFrame) -> pd.Series:
    ics = []
    idx = []
    for dt in fac.index:
        if dt not in fwd.index:
            continue
        a, b = fac.loc[dt], fwd.loc[dt]
        ok = a.notna() & b.notna()
        if int(ok.sum()) < 30:
            continue
        ics.append(float(stats.spearmanr(a[ok], b[ok]).correlation))
        idx.append(dt)
    return pd.Series(ics, index=idx, name="RankIC")


print("\n=== factor construction ===")
f_w = winsorize_cs(raw, 0.01)
f_z = zscore_cs(f_w)
f_n = neutralize(f_z, ind, log_mcap)
f_nz = zscore_cs(f_n)

print(f"mean_cs_corr(raw, beta_true)={mean_cs_corr(raw, beta_true):.4f}")
print(f"mean_cs_corr(z_only, beta_true)={mean_cs_corr(f_z, beta_true):.4f}")
print(f"mean_cs_corr(neutralized, beta_true)={mean_cs_corr(f_nz, beta_true):.4f}")
print("teach: industry+mcap residualization lifts recovery of the planted loading")

# cache for lab 02
CACHE = DATA / "cache"
CACHE.mkdir(exist_ok=True)
f_nz.to_csv(CACHE / "factor_neutral.csv")
f_z.to_csv(CACHE / "factor_z_only.csv")

print("\n=== RankIC / ICIR / decay ===")
horizons = [1, 5, 10, 20]
ic_table = {}
for h in horizons:
    fwd = forward_sum(rets, h)
    ic = spearman_ic(f_nz, fwd)
    ic_table[h] = ic
    # ICIR annualized roughly: mean/std * sqrt(252/h) for overlapping h-day
    icir = ic.mean() / (ic.std(ddof=1) + 1e-12) * np.sqrt(252 / h)
    print(f"RankIC h={h}: mean={ic.mean():.4f} std={ic.std(ddof=1):.4f} ICIR_ann≈{icir:.3f} n={len(ic)}")

ic1 = ic_table[1]
print(f"ICIR_daily = mean/std * sqrt(252) = {ic1.mean() / ic1.std(ddof=1) * ANN:.3f}")

means = [ic_table[h].mean() for h in horizons]
# Decaying-alpha foil: AR(1) signal that predicts next residual with half-life ~5d, then dies
rng_d = np.random.default_rng(7)
eps = rng_d.normal(0, 1.0, size=f_nz.shape)
theta = 0.87  # ~5 trading-day half-life
sig = np.zeros_like(eps)
sig[0] = eps[0]
for t in range(1, len(eps)):
    sig[t] = theta * sig[t - 1] + eps[t]
# inject into returns already realized? instead: correlate forward 1d residual with sig
# Build a synthetic decaying predictive factor aligned to residual of market
mkt = rets.mean(axis=1)
resid = rets.sub(mkt, axis=0)
# factor_decaying[t] predicts resid[t+1] weakly
fac_dec = pd.DataFrame(sig, index=f_nz.index, columns=f_nz.columns)
fac_dec = zscore_cs(fac_dec)
# make resid depend on lagged sig for teaching (in-place overlay on a copy of rets for IC only)
rets_dec = rets.copy()
# cannot rewrite history; instead measure IC of fac_dec vs forward resid that we construct
fwd_res = resid.shift(-1)  # next-day residual
# Plant: strengthen link by measuring IC of fac_dec shifted against constructed target = 0.05*fac_dec + noise
# Simpler teach: IC of fac_dec[t] vs fac_dec[t+h] * scale as "signal persistence decay"
decay_ic = []
for h in horizons:
    # RankIC between factor today and residual h days ahead (using planted: resid_fwd ≈ 0.02 * fac_dec)
    target = (0.02 * fac_dec).shift(-h) + resid * 0.0  # pure: target is scaled future factor? 
    # Better: IC(fac_dec[t], 0.02*fac_dec[t] + noise) at each horizon via forward resid panel
    # Construct synthetic forward return panel for decay demo only
    noise = pd.DataFrame(rng_d.normal(0, 0.02, size=rets.shape), index=rets.index, columns=rets.columns)
    fwd_h = (0.02 * fac_dec).shift(-h) + noise.shift(-h)
    ic_d = spearman_ic(fac_dec, fwd_h)
    decay_ic.append(float(ic_d.mean()))
    print(f"decaying_alpha_foil RankIC h={h}: mean={ic_d.mean():.4f}")

fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(horizons, means, "o-", color="#1f4e79", label="planted risk-premium loading (cumulative fwd)")
ax.plot(horizons, decay_ic, "s--", color="#c45911", label="decaying-alpha foil")
ax.set_xlabel("horizon (days)"); ax.set_ylabel("mean RankIC")
ax.set_title("IC vs horizon: risk premium vs decaying alpha")
ax.axhline(0, color="k", lw=0.5); ax.legend(); ax.grid(True, alpha=0.3)
fig.tight_layout(); fig.savefig(PUBLIC / "ic_decay.png", dpi=120); plt.close()
print("teach: static risk loading → mean RankIC can RISE with cumulative horizon; decaying alpha FALLS — both are 'IC decay' lessons")
print("chart", PUBLIC / "ic_decay.png")

print("\n=== quintile portfolios (Alphalens-style long-short) ===")
Q = 5
labels = pd.DataFrame(np.nan, index=f_nz.index, columns=f_nz.columns)
for dt in f_nz.index:
    s = f_nz.loc[dt].dropna()
    if len(s) < 50:
        continue
    labels.loc[dt, s.index] = pd.qcut(s, Q, labels=False, duplicates="drop") + 1

w = pd.DataFrame(0.0, index=f_nz.index, columns=f_nz.columns)
for dt in f_nz.index:
    lab = labels.loc[dt]
    for qi, sign in [(1.0, -1.0), (5.0, 1.0)]:
        members = lab[lab == qi].dropna().index
        if len(members) == 0:
            continue
        w.loc[dt, members] = sign / len(members)

net, turn = apply_costs_ls(w, rets)
gross = (w.shift(1).fillna(0) * rets).sum(axis=1)
print(
    f"LS gross_SR={gross.mean() / gross.std(ddof=1) * ANN:.3f} "
    f"net_SR={net.mean() / net.std(ddof=1) * ANN:.3f} "
    f"mean_turn={float(turn.mean()):.4f} NAV_net={float((1 + net.fillna(0)).cumprod().iloc[-1]):.4f}"
)
print("cost model: P2 10 bps one-way + √impact with LAGGEDrolling σ (VOL_LB=20, shift(1), expanding warm-up)")

print("\n=== Fama–MacBeth (single-factor CS slopes) ===")
fwd1 = forward_sum(rets, 1)
gammas = []
for dt in f_nz.index:
    y = fwd1.loc[dt] if dt in fwd1.index else None
    if y is None:
        continue
    x = f_nz.loc[dt]
    ok = y.notna() & x.notna()
    if int(ok.sum()) < 40:
        continue
    slope, *_ = stats.linregress(x[ok], y[ok])
    gammas.append(slope)
g = np.asarray(gammas, dtype=float)


def newey_west_se(x: np.ndarray, lags: int = 5) -> float:
    x = x - x.mean()
    n = len(x)
    s = float(np.dot(x, x) / n)
    for L in range(1, lags + 1):
        wgt = 1.0 - L / (lags + 1)
        s += 2.0 * wgt * float(np.dot(x[L:], x[:-L]) / n)
    return float(np.sqrt(max(s, 0.0) / n))


nw = newey_west_se(g, lags=5)
t_nw = float(g.mean() / nw) if nw > 0 else float("nan")
t_iid = float(g.mean() / (g.std(ddof=1) / np.sqrt(len(g))))
print(f"FM_daily mean_gamma={g.mean():.6f} t_iid={t_iid:.3f} t_NeweyWest_L5={t_nw:.3f} n={len(g)}")
# Monthly FM (classic frequency): sum daily returns within month, use month-end factor
months = f_nz.index.to_period("M")
g_m = []
for m, idx in f_nz.groupby(months).groups.items():
    idx = list(idx)
    if len(idx) < 5:
        continue
    # factor at last day of prior month / first available; use last day factor to predict next-month return
    pass
# cleaner monthly: for each month m, CS-regress month-sum returns on factor as-of prior month-end
uniq = sorted(set(months))
for i in range(1, len(uniq)):
    m_prev, m_cur = uniq[i - 1], uniq[i]
    prev_days = f_nz.index[months == m_prev]
    cur_days = rets.index[rets.index.to_period("M") == m_cur]
    if len(prev_days) == 0 or len(cur_days) == 0:
        continue
    x = f_nz.loc[prev_days[-1]]
    y = rets.loc[cur_days].sum(axis=0)
    ok = x.notna() & y.notna()
    if int(ok.sum()) < 40:
        continue
    slope, *_ = stats.linregress(x[ok], y[ok])
    g_m.append(slope)
g_m = np.asarray(g_m, dtype=float)
t_m = float(g_m.mean() / (g_m.std(ddof=1) / np.sqrt(len(g_m)))) if len(g_m) > 2 else float("nan")
nw_m = newey_west_se(g_m, lags=3) if len(g_m) > 5 else float("nan")
t_m_nw = float(g_m.mean() / nw_m) if nw_m and nw_m > 0 else float("nan")
print(f"FM_monthly mean_gamma={g_m.mean():.6f} t_iid={t_m:.3f} t_NeweyWest_L3={t_m_nw:.3f} n_months={len(g_m)}")
print("FF3 (1993): Mkt-Rf, SMB, HML. FF5 (2015): + RMW, CMA. Lab FM uses the single planted factor.")

print("\n=== factor zoo / Harvey–Liu–Zhu (2016) multiple testing ===")
rng = np.random.default_rng(0)
N_RAND = 200
tstats = []
# subsample dates for speed
dts = list(f_nz.index[::2])
for k in range(N_RAND):
    fake = pd.DataFrame(rng.normal(size=f_nz.shape), index=f_nz.index, columns=f_nz.columns)
    fake = zscore_cs(fake)
    gs = []
    for dt in dts:
        y = fwd1.loc[dt]; x = fake.loc[dt]
        ok = y.notna() & x.notna()
        if int(ok.sum()) < 40:
            continue
        slope, *_ = stats.linregress(x[ok], y[ok])
        gs.append(slope)
    gs = np.asarray(gs)
    if len(gs) < 30:
        continue
    tstats.append(gs.mean() / (gs.std(ddof=1) / np.sqrt(len(gs))))
tstats = np.asarray(tstats)
frac2 = float(np.mean(np.abs(tstats) > 2))
frac3 = float(np.mean(np.abs(tstats) > 3))
print(f"random_factors={len(tstats)} frac_|t|>2={frac2:.3f} frac_|t|>3={frac3:.3f}")
print(f"true_factor_FM_daily_t={t_iid:.3f} FM_monthly_t={t_m:.3f} (monthly should clear t>3 with planted premium)")
print("Harvey et al. 2016: with a zoo of published factors, new claims should clear ~t>3, not t≈2")

print("\n=== crowding / decay foil ===")
rank_ac1 = []
for dt0, dt1 in zip(f_nz.index[:-1], f_nz.index[1:]):
    a, b = f_nz.loc[dt0], f_nz.loc[dt1]
    ok = a.notna() & b.notna()
    if int(ok.sum()) < 30:
        continue
    rank_ac1.append(float(stats.spearmanr(a[ok], b[ok]).correlation))
print(f"factor_rank_autocorr_lag1_mean={float(np.mean(rank_ac1)):.4f}")
print("teach: high rank AC → lower theoretical turnover, but crowding if books converge; IC decay caps horizon")

print("\n=== Alphalens/Qlib-style workflow (pandas) ===")
print("steps: (1) clean factor + forward returns (2) RankIC series (3) quantile returns (4) turnover")
print("optional API map: alphalens.utils.get_clean_factor_and_forward_returns → tears.create_information_tear_sheet / create_returns_tear_sheet")
print("Qlib: DataHandlerLP + CSZScoreNorm / CSZFillna processors ≈ winsorize+z+neutralize here; Alpha158 is a feature set ref")

eq = (1 + net.fillna(0)).cumprod()
fig, axes = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
axes[0].plot(ic1.index, ic1.rolling(20).mean(), label="RankIC MA20", color="#1f4e79")
axes[0].axhline(0, color="k", lw=0.5); axes[0].legend(); axes[0].grid(True, alpha=0.3)
axes[0].set_title("RankIC (h=1) and LS net NAV")
axes[1].plot(eq.index, eq.values, label="LS net NAV", color="#c45911")
axes[1].legend(); axes[1].grid(True, alpha=0.3)
fig.tight_layout(); fig.savefig(PUBLIC / "factor_ic_nav.png", dpi=120); plt.close()
print("chart", PUBLIC / "factor_ic_nav.png")

# quantile mean returns bar
qret = {}
for qi in range(1, Q + 1):
    mask = labels == qi
    # equal-weight within quantile each day
    wr = pd.Series(0.0, index=rets.index)
    for dt in labels.index[:-1]:
        members = labels.loc[dt][labels.loc[dt] == qi].dropna().index
        if len(members) == 0:
            continue
        nxt = rets.index[rets.index.get_loc(dt) + 1] if dt in rets.index and rets.index.get_loc(dt) + 1 < len(rets) else None
        if nxt is None:
            continue
        wr.loc[nxt] = rets.loc[nxt, members].mean()
    qret[qi] = float(wr.mean() * 252)

fig, ax = plt.subplots(figsize=(7, 4))
ax.bar([f"Q{k}" for k in qret], list(qret.values()), color="#2e75b6")
ax.set_ylabel("ann. mean return"); ax.set_title("Quantile mean returns (neutralized factor)")
ax.grid(True, axis="y", alpha=0.3)
fig.tight_layout(); fig.savefig(PUBLIC / "quantile_bars.png", dpi=120); plt.close()
print("quantile_ann_means", {f"Q{k}": round(v, 4) for k, v in qret.items()})
print("chart", PUBLIC / "quantile_bars.png")
print("disclaimer: synthetic panel with planted beta_true + MU_TRUE — learning only, not investment advice")
