"""P4 lab 01: factor construction, IC/RankIC/ICIR/decay, quantiles, FM, Harvey zoo, Alphalens-style.
Strong (inflated) vs weak RankIC panels side by side. Learning only — not investment advice.
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
    forward_sum,
    load_strength,
    ls_stats,
    ls_weights,
    spearman_ic,
    zscore_cs,
    DATA as DATA_DIR,
)

DATA = DATA_DIR
ensure_panel(force=True)

print("=== parameters ===")
print("panel 200 assets x 750 days; 10 industries")
print("DGP: r = beta_true*f_true + beta_mkt*f_mkt + beta_size*f_size + industry + noise")
print(f"MU_STRONG={MU_STRONG} (INFLATED teaching setting)  MU_WEAK={MU_WEAK} (realistic-weak foil, target RankIC ~0.02-0.05)")
print("raw_factor = beta_true + 0.4*industry + 0.25*size_loading + noise")
print("look-ahead: factor[t] vs fwd from t+1; LS weights shift(1); impact vol lagged; neutralize uses log_mcap.shift(1)")
print("cite: Fama & MacBeth 1973 JPE 81(3) 607-636")
print("cite: Fama & French 1993 JFE 33(1) 3-56 — FF3; 2015 JFE 116(1) 1-22 — FF5")
print("cite: Harvey, Liu & Zhu 2016 RFS 29(1) 5-68 — t>3 multiple-testing hurdle")
print("cite: Alphalens Reloaded docs (alphalens.ml4trading.io); Qlib CSZScoreNorm / Alpha158")
print("niche: quant-wiki foil; frontier LLM mining deferred to P8")
print("note: overlapping multi-day IC windows mainly inflate IC autocorrelation and ICIR SE (not mean IC);")
print("      fix with non-overlapping sampling or Newey–West on the IC series")


def mean_cs_corr(fac: pd.DataFrame, truth: pd.Series) -> float:
    cors = []
    for dt in fac.index[::5]:
        c = fac.loc[dt].corr(truth.reindex(fac.columns))
        if np.isfinite(c):
            cors.append(float(c))
    return float(np.mean(cors))


# ---- strong panel (main walkthrough) ----
rets_s, raw, raw2, log_mcap, meta = load_strength("strong")
beta_true = meta["beta_true"]
ind = meta["industry"]
f_nz_s = build_factor(raw, ind, log_mcap)

print("\n=== factor construction (strong; log_mcap.shift(1) in neutralize) ===")
f_z = zscore_cs(raw.clip(raw.quantile(0.01, axis=1), raw.quantile(0.99, axis=1), axis=0))
print(f"mean_cs_corr(raw, beta_true)={mean_cs_corr(raw, beta_true):.4f}")
print(f"mean_cs_corr(z_only, beta_true)={mean_cs_corr(f_z, beta_true):.4f}")
print(f"mean_cs_corr(neutralized, beta_true)={mean_cs_corr(f_nz_s, beta_true):.4f}")
print("teach: industry+lagged-mcap residualization lifts recovery of the planted loading")

CACHE = DATA / "cache"
CACHE.mkdir(exist_ok=True)
f_nz_s.to_csv(CACHE / "factor_neutral_strong.csv")

print("\n=== RankIC / ICIR / decay (strong) ===")
horizons = [1, 5, 10, 20]
ic_table = {}
for h in horizons:
    ic = spearman_ic(f_nz_s, forward_sum(rets_s, h))
    ic_table[h] = ic
    icir = ic.mean() / (ic.std(ddof=1) + 1e-12) * np.sqrt(252 / h)
    print(f"RankIC h={h}: mean={ic.mean():.4f} std={ic.std(ddof=1):.4f} ICIR_ann≈{icir:.3f} n={len(ic)}")
print(
    "overlapping-window note: for h>1, overlapping fwd sums inflate IC autocorr and shrink naive ICIR SE;"
    " mean IC is less biased — use non-overlapping IC or Newey–West on the IC series"
)
ic1 = ic_table[1]

# decaying-alpha foil
rng_d = np.random.default_rng(7)
eps = rng_d.normal(0, 1.0, size=f_nz_s.shape)
theta = 0.87
sig = np.zeros_like(eps)
sig[0] = eps[0]
for t in range(1, len(eps)):
    sig[t] = theta * sig[t - 1] + eps[t]
fac_dec = zscore_cs(pd.DataFrame(sig, index=f_nz_s.index, columns=f_nz_s.columns))
decay_ic = []
for h in horizons:
    noise = pd.DataFrame(rng_d.normal(0, 0.02, size=rets_s.shape), index=rets_s.index, columns=rets_s.columns)
    fwd_h = (0.02 * fac_dec).shift(-h) + noise.shift(-h)
    ic_d = spearman_ic(fac_dec, fwd_h)
    decay_ic.append(float(ic_d.mean()))
    print(f"decaying_alpha_foil RankIC h={h}: mean={ic_d.mean():.4f}")

means = [ic_table[h].mean() for h in horizons]
fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(horizons, means, "o-", color="#1f4e79", label="planted risk-premium (cumulative fwd)")
ax.plot(horizons, decay_ic, "s--", color="#c45911", label="decaying-alpha foil")
ax.set_xlabel("horizon (days)"); ax.set_ylabel("mean RankIC")
ax.set_title("IC vs horizon: risk premium vs decaying alpha")
ax.axhline(0, color="k", lw=0.5); ax.legend(); ax.grid(True, alpha=0.3)
fig.tight_layout(); fig.savefig(PUBLIC / "ic_decay.png", dpi=120); plt.close()
print("chart", PUBLIC / "ic_decay.png")

# ---- strong vs weak side-by-side ----
print("\n=== strong vs weak panel (side-by-side) ===")
print("STRONG panel is an INFLATED teaching setting so FM/t>3 recover cleanly;")
print("WEAK panel (MU_WEAK) targets RankIC ~0.02-0.05 — closer to live single-factor magnitudes.")
rets_w, _, _, _, _ = load_strength("weak")
f_nz_w = build_factor(raw, ind, log_mcap)
stats_s = ls_stats(f_nz_s, rets_s)
stats_w = ls_stats(f_nz_w, rets_w)
rows = []
for label, st, mu in [("strong", stats_s, MU_STRONG), ("weak", stats_w, MU_WEAK)]:
    row = {
        "panel": label,
        "MU": mu,
        "RankIC": st["RankIC_mean"],
        "ICIR": st["ICIR"],
        "gross_SR": st["gross_SR"],
        "net_SR": st["net_SR"],
        "mean_turn": st["mean_turn"],
    }
    rows.append(row)
    print(
        f"{label:6s} MU={mu:.4f} RankIC={st['RankIC_mean']:.4f} ICIR={st['ICIR']:.3f} "
        f"gross_SR={st['gross_SR']:.3f} net_SR={st['net_SR']:.3f} turn={st['mean_turn']:.4f}"
    )
print("teach: real single factors are WEAK; costs can wipe net SR even when gross>0; combining many weak signals is why multi-factor exists")
pd.DataFrame(rows).to_csv(DATA / "strong_vs_weak.csv", index=False)

fig, axes = plt.subplots(1, 2, figsize=(10, 4))
for ax, st, title in [(axes[0], stats_s, "strong (inflated)"), (axes[1], stats_w, "weak (realistic foil)")]:
    eq = (1 + st["net"].fillna(0)).cumprod()
    ax.plot(eq.index, eq.values, color="#1f4e79")
    ax.set_title(f"{title}\nnet SR={st['net_SR']:.2f} RankIC={st['RankIC_mean']:.3f}")
    ax.grid(True, alpha=0.3)
fig.suptitle("Strong vs weak: LS net NAV")
fig.tight_layout(); fig.savefig(PUBLIC / "strong_vs_weak.png", dpi=120); plt.close()
print("chart", PUBLIC / "strong_vs_weak.png")

print("\n=== quintile portfolios (strong; Alphalens-style) ===")
w = stats_s["w"]
print(
    f"LS gross_SR={stats_s['gross_SR']:.3f} net_SR={stats_s['net_SR']:.3f} "
    f"mean_turn={stats_s['mean_turn']:.4f} NAV_net={stats_s['NAV_net']:.4f}"
)
print("cost model: P2 10 bps one-way + √impact with LAGGEDrolling σ (VOL_LB=20, shift(1), expanding warm-up)")

print("\n=== Fama–MacBeth (strong panel) ===")
fwd1 = forward_sum(rets_s, 1)
gammas = []
for dt in f_nz_s.index:
    y = fwd1.loc[dt] if dt in fwd1.index else None
    if y is None:
        continue
    x = f_nz_s.loc[dt]
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

months = f_nz_s.index.to_period("M")
uniq = sorted(set(months))
g_m = []
for i in range(1, len(uniq)):
    m_prev, m_cur = uniq[i - 1], uniq[i]
    prev_days = f_nz_s.index[months == m_prev]
    cur_days = rets_s.index[rets_s.index.to_period("M") == m_cur]
    if len(prev_days) == 0 or len(cur_days) == 0:
        continue
    x = f_nz_s.loc[prev_days[-1]]
    y = rets_s.loc[cur_days].sum(axis=0)
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
print("FF3 (1993): Mkt-Rf, SMB, HML. FF5 (2015): + RMW, CMA.")

print("\n=== factor zoo / Harvey–Liu–Zhu (2016) multiple testing ===")
rng = np.random.default_rng(0)
N_RAND = 200
# Two-sided normal null under independent t-tests: P(|Z|>2)≈0.0455, P(|Z|>3)≈0.0027
NULL_GT2 = 2 * (1 - stats.norm.cdf(2))  # ≈0.0455
NULL_GT3 = 2 * (1 - stats.norm.cdf(3))  # ≈0.0027
tstats = []
dts = list(f_nz_s.index[::2])
for k in range(N_RAND):
    fake = zscore_cs(pd.DataFrame(rng.normal(size=f_nz_s.shape), index=f_nz_s.index, columns=f_nz_s.columns))
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
exp2 = NULL_GT2 * len(tstats)
exp3 = NULL_GT3 * len(tstats)
print(f"random_factors={len(tstats)}")
print(
    f"observed frac_|t|>2={frac2:.4f} ({frac2*len(tstats):.1f} of {len(tstats)})  "
    f"null_expectation≈{NULL_GT2:.4f} (≈{exp2:.1f} of {len(tstats)}; N(0,1) two-sided)"
)
print(
    f"observed frac_|t|>3={frac3:.4f} ({frac3*len(tstats):.1f} of {len(tstats)})  "
    f"null_expectation≈{NULL_GT3:.4f} (≈{exp3:.1f} of {len(tstats)}; N(0,1) two-sided)"
)
print(
    f"teach: observed ~{frac2*100:.1f}% at |t|>2 is RIGHT IN LINE with pure noise (~{NULL_GT2*100:.2f}%); "
    f"HLZ 2016 raise the bar to ~t>3 because the published zoo already spent the t≈2 budget"
)
print(f"true_factor_FM_daily_t={t_iid:.3f} FM_monthly_t={t_m:.3f} (strong planted clears t>3; weak often would not)")

print("\n=== crowding / decay foil ===")
rank_ac1 = []
for dt0, dt1 in zip(f_nz_s.index[:-1], f_nz_s.index[1:]):
    a, b = f_nz_s.loc[dt0], f_nz_s.loc[dt1]
    ok = a.notna() & b.notna()
    if int(ok.sum()) < 30:
        continue
    rank_ac1.append(float(stats.spearmanr(a[ok], b[ok]).correlation))
print(f"factor_rank_autocorr_lag1_mean={float(np.mean(rank_ac1)):.4f}")

print("\n=== Alphalens/Qlib-style workflow (pandas) ===")
print("steps: (1) clean factor + forward returns (2) RankIC (3) quantile returns (4) turnover")
print("optional API map: alphalens.utils.get_clean_factor_and_forward_returns → tears.create_*_tear_sheet")
print("Qlib: DataHandlerLP + CSZScoreNorm / CSZFillna ≈ winsorize+z+neutralize(log_mcap.shift(1))")

eq = (1 + stats_s["net"].fillna(0)).cumprod()
fig, axes = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
axes[0].plot(ic1.index, ic1.rolling(20).mean(), label="RankIC MA20", color="#1f4e79")
axes[0].axhline(0, color="k", lw=0.5); axes[0].legend(); axes[0].grid(True, alpha=0.3)
axes[0].set_title("RankIC (h=1) and LS net NAV (strong)")
axes[1].plot(eq.index, eq.values, label="LS net NAV", color="#c45911")
axes[1].legend(); axes[1].grid(True, alpha=0.3)
fig.tight_layout(); fig.savefig(PUBLIC / "factor_ic_nav.png", dpi=120); plt.close()

labels = pd.DataFrame(np.nan, index=f_nz_s.index, columns=f_nz_s.columns)
for dt in f_nz_s.index:
    s = f_nz_s.loc[dt].dropna()
    if len(s) < 50:
        continue
    labels.loc[dt, s.index] = pd.qcut(s, 5, labels=False, duplicates="drop") + 1
qret = {}
for qi in range(1, 6):
    wr = pd.Series(0.0, index=rets_s.index)
    for dt in labels.index[:-1]:
        members = labels.loc[dt][labels.loc[dt] == qi].dropna().index
        if len(members) == 0:
            continue
        loc = rets_s.index.get_loc(dt)
        if not isinstance(loc, int) or loc + 1 >= len(rets_s):
            continue
        nxt = rets_s.index[loc + 1]
        wr.loc[nxt] = rets_s.loc[nxt, members].mean()
    qret[qi] = float(wr.mean() * 252)
fig, ax = plt.subplots(figsize=(7, 4))
ax.bar([f"Q{k}" for k in qret], list(qret.values()), color="#2e75b6")
ax.set_ylabel("ann. mean return"); ax.set_title("Quantile mean returns (strong neutralized)")
ax.grid(True, axis="y", alpha=0.3)
fig.tight_layout(); fig.savefig(PUBLIC / "quantile_bars.png", dpi=120); plt.close()
print("quantile_ann_means", {f"Q{k}": round(v, 4) for k, v in qret.items()})
print("chart", PUBLIC / "quantile_bars.png")
print("disclaimer: strong panel MU is inflated for teaching; weak panel is the realistic foil — learning only")



print("\n=== cost-aware factor / AP-model comparison foil (Detzel–Novy-Marx–Velikov JF 2023) ===")
print("cite: DOI 10.1111/jofi.13225 — ignoring costs biases tests toward high-turnover factors/models")
rng_d = np.random.default_rng(11)
n_d, m_d = 600, 120
# Plant a moderate CS alpha that BOTH factors can see, but fast factor churns more
a = rng_d.normal(0, 1.0, size=(n_d, m_d))
noise = rng_d.normal(0, 0.015, size=(n_d, m_d))
rets_d = 0.0012 * a + noise
fwd = pd.DataFrame(rets_d).shift(-1)
# Slow factor: lagged sticky score (low turnover)
slow = pd.DataFrame(a).shift(1).rolling(40, min_periods=20).mean().rank(axis=1, pct=True)
# Fast factor: re-ranks every day using a noisier short window of the SAME lagged info (no look-ahead)
# Higher gross capture of short-lived noise + true alpha, but huge turnover
fast = (pd.DataFrame(a).shift(1) + 0.8 * pd.DataFrame(noise).shift(1)).rank(axis=1, pct=True)

def ls_pnl(factor, fwd, cost_bps=10.0):
    pnl, turns, prev = [], [], None
    for t_i in range(len(factor) - 1):
        row = factor.iloc[t_i]
        if row.notna().sum() < 30:
            continue
        q_hi, q_lo = row.quantile(0.8), row.quantile(0.2)
        long = row >= q_hi
        short = row <= q_lo
        w = long.astype(float) / max(long.sum(), 1) - short.astype(float) / max(short.sum(), 1)
        r = float((w * fwd.iloc[t_i]).sum())
        turn = float(np.abs(w).sum()) if prev is None else float(np.abs(w - prev).sum())
        prev = w
        pnl.append(r - turn * (cost_bps / 1e4))
        turns.append(turn)
    s = pd.Series(pnl)
    sr = float(s.mean() / s.std(ddof=1) * np.sqrt(252)) if len(s) > 20 and s.std(ddof=1) > 0 else float("nan")
    # also gross SR
    return sr, float(np.mean(turns))

def ls_gross(factor, fwd):
    return ls_pnl(factor, fwd, cost_bps=0.0)

sr_s_g, turn_s = ls_gross(slow, fwd)
sr_s_n, _ = ls_pnl(slow, fwd, cost_bps=10.0)
sr_f_g, turn_f = ls_gross(fast, fwd)
sr_f_n, _ = ls_pnl(fast, fwd, cost_bps=10.0)
print(f"slow_factor  turnover≈{turn_s:.3f}  gross_SR≈{sr_s_g:.3f}  net_SR@10bps≈{sr_s_n:.3f}")
print(f"fast_factor  turnover≈{turn_f:.3f}  gross_SR≈{sr_f_g:.3f}  net_SR@10bps≈{sr_f_n:.3f}")
winner_gross = "fast" if sr_f_g > sr_s_g else "slow"
winner_net = "fast" if sr_f_n > sr_s_n else "slow"
print(f"ranking_by_gross_picks={winner_gross}  ranking_by_net_picks={winner_net}")
print("teach: cost-blind gross rankings bias toward high-turnover factors; net-of-cost rankings can reverse — Detzel spirit.")
print("paper: after costs, FF5 (esp. cash-profitability variants) beat high-cost q/six-factor style comparisons.")

print("\n=== Harvey–Sancetta–Zhao NBER w34898 (2026): t≥3 + local FDR ===")
print("cite: https://www.nber.org/papers/w34898 — What Threshold Should be Applied to Tests of Factor Models?")
print("next to HLZ 2016 + Detzel costs: valid thresholds need dependence, null shape, selection bias")
print("lower bound: researchers should employ a t-statistic cutoff of at least 3.0")
print("local FDR: probability null is true GIVEN the realized test statistic — a p-value cannot supply that")
# toy: 200 simulated factor t-stats under null N(0,1); show p-value vs local-FDR spirit
rng_h = np.random.default_rng(11)
ts = rng_h.normal(0, 1.0, 200)
# plant one strong true t≈4.2
ts[0] = 4.2
from scipy.stats import norm as _norm
pvals = 2 * (1 - _norm.cdf(np.abs(ts)))
# crude local-FDR sketch: compare density at |t| vs null; teaching only
# For |t|~4.2, empirical null density tiny → lfdr low; for |t|~1.2 lfdr high
def lfdr_sketch(t):
    # mixture: 90% null N(0,1) + 10% N(3,1); Bayes posterior null | |T|=t
    # f0 = phi(t); f = 0.9*phi(t)+0.1*phi(t-3) [one-sided sketch on signed]
    f0 = float(_norm.pdf(t))
    f = 0.9 * f0 + 0.1 * float(_norm.pdf(t - 3.0))
    return float(0.9 * f0 / max(f, 1e-12))

for label, t0 in [("noise_t≈1.2", 1.2), ("borderline_t≈2.0", 2.0), ("HLZ_bar_t≈3.0", 3.0), ("planted_t=4.2", 4.2)]:
    pv = 2 * (1 - _norm.cdf(abs(t0)))
    lf = lfdr_sketch(t0)
    print(f"  {label}: two-sided_p≈{pv:.4f}  localFDR_sketch≈{lf:.3f}")
print("quiz_foil: p-value ≠ P(null|data); local FDR targets the latter")
print("costs still matter for economic significance after statistical hurdles (Detzel bridge)")


