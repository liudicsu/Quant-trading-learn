"""P6 lab 04: market regimes & crisis literacy — causal detectors + stress toys.
Learning only — not investment advice. Offline synthetic data only.
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from _common import PUBLIC, DATA, ANN, max_dd

SEED = 11
rng = np.random.default_rng(SEED)

print("=== parameters ===")
print("seed=11; path: rally→range→crash→recovery; all detectors use shift(1) / data through t-1")
print("cite: Hamilton 1989 Econometrica 57(2) — filtered vs smoothed regime probs")
print("cite: Moreira & Muir 2017 JF; Cederburg et al. 2020 JFE — vol-managed foil literacy")
print("cite: NYSE Rule 7.12 MWCB 7/13/20%; CSRC 2016-01 circuit-breaker suspension literacy")
print("learning only — not investment advice; stress toys are not forecasts")

# ------------------------------------------------------------------
# Lab A: synthetic path with planted regimes
# ------------------------------------------------------------------
n_rally, n_range, n_crash, n_rec = 180, 120, 40, 160
n = n_rally + n_range + n_crash + n_rec
dates = pd.bdate_range("2019-01-02", periods=n)
true = np.array(
    ["rally"] * n_rally + ["range"] * n_range + ["crash"] * n_crash + ["recovery"] * n_rec
)

mu = {"rally": 0.0012, "range": 0.00005, "crash": -0.018, "recovery": 0.0010}
sig = {"rally": 0.008, "range": 0.011, "crash": 0.035, "recovery": 0.014}
ret = np.empty(n)
for i, r in enumerate(true):
    ret[i] = rng.normal(mu[r], sig[r])
# mild AR(1) texture within segments (still causal when lagged)
for i in range(1, n):
    if true[i] == true[i - 1]:
        ret[i] = 0.15 * ret[i - 1] + 0.85 * ret[i]

px = 100 * np.cumprod(1.0 + ret)
s_ret = pd.Series(ret, index=dates, name="ret")
s_px = pd.Series(px, index=dates, name="px")

# Causal detectors (decision at t uses info through t-1 only)
ma_fast = s_px.rolling(20, min_periods=20).mean().shift(1)
ma_slow = s_px.rolling(60, min_periods=60).mean().shift(1)
trend_up = (ma_fast > ma_slow).astype(float)
# price vs N-day high (lagged)
roll_high = s_px.rolling(60, min_periods=60).max().shift(1)
near_high = (s_px.shift(1) / roll_high >= 0.97).astype(float)

vol20 = s_ret.rolling(20, min_periods=20).std(ddof=1).shift(1)
vol60 = s_ret.rolling(60, min_periods=60).std(ddof=1).shift(1)
vol_spike = (vol20 > 1.5 * vol60).astype(float)

# peak-drawdown buckets from lagged equity
eq = (1.0 + s_ret).cumprod()
peak = eq.cummax().shift(1)
dd_lag = eq.shift(1) / peak - 1.0
dd_bucket = pd.Series(0, index=dates, dtype=int)
dd_bucket[dd_lag <= -0.05] = 1
dd_bucket[dd_lag <= -0.10] = 2
dd_bucket[dd_lag <= -0.20] = 3

# Regime label for teaching (causal rule stack — NOT a trading signal)
# crash if vol_spike & dd_bucket>=2; range if not trend and not crash; else rally/recovery by trend
label = pd.Series("warm", index=dates, dtype=object)
label[(trend_up == 1) & (vol_spike == 0) & (dd_bucket < 2)] = "rally_like"
label[(trend_up == 0) & (vol_spike == 0) & (dd_bucket < 2)] = "range_like"
label[(vol_spike == 1) | (dd_bucket >= 2)] = "stress_like"
# recovery-like: after stress, trend turns up with elevated but falling vol — approximate
label[(trend_up == 1) & (dd_bucket >= 1) & (dd_bucket < 3) & (vol_spike == 0)] = "recovery_like"

counts = label.value_counts(dropna=False)
print("\n=== Lab A: causal regime labels (shift(1) stack) ===")
print(f"n_days={n} segments=rally{n_rally}/range{n_range}/crash{n_crash}/recovery{n_rec}")
for k, v in counts.items():
    print(f"label_{k}={int(v)}")
# overlap with planted crash window
crash_idx = np.where(true == "crash")[0]
stress_in_crash = float((label.iloc[crash_idx] == "stress_like").mean())
print(f"stress_hit_rate_in_planted_crash={stress_in_crash:.3f}")
print(f"mean_vol20_rally={float(vol20[true=='rally'].mean()):.4f} mean_vol20_crash={float(vol20[true=='crash'].mean()):.4f}")
print(f"min_dd_lag={float(dd_lag.min()):.4f}")

# chart path + labels
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(s_px.index, s_px.values, lw=1.2, color="#1f4e79", label="price")
# shade planted regimes
colors = {"rally": "#d4edda", "range": "#fff3cd", "crash": "#f8d7da", "recovery": "#cce5ff"}
start = 0
for regime in ["rally", "range", "crash", "recovery"]:
    length = {"rally": n_rally, "range": n_range, "crash": n_crash, "recovery": n_rec}[regime]
    end = start + length
    ax.axvspan(s_px.index[start], s_px.index[end - 1], color=colors[regime], alpha=0.55, label=regime)
    start = end
ax.set_title("Synthetic path: planted regimes (teaching only)")
ax.legend(loc="upper left", fontsize=8, ncol=3)
fig.tight_layout()
fig.savefig(PUBLIC / "regime_path.png", dpi=120)
plt.close()
print(f"wrote {PUBLIC / 'regime_path.png'}")

# ------------------------------------------------------------------
# Lab B: fixed vs vol-target vs DD brake — compare vol & maxDD only
# ------------------------------------------------------------------
print("\n=== Lab B: fixed vs vol-target vs DD brake (vol & maxDD only) ===")
r = s_ret.copy()
# fixed 100% long
pnl_fixed = r
eq_fixed = (1 + pnl_fixed).cumprod()
# vol-target: target daily vol 1%, weight = target/lagged_vol, clip [0, 1.5]
target = 0.01
w_vt = (target / vol20).clip(0, 1.5).fillna(0)
# weight decided at t from vol through t-1 already; apply to ret_t
pnl_vt = w_vt * r
eq_vt = (1 + pnl_vt).cumprod()
# DD brake on controlled book (soft 10% / hard 20%), lagged
kill, soft = 0.20, 0.10
live = np.ones(n)
eq_c = np.ones(n)
peak_c = 1.0
for t in range(1, n):
    ddy = eq_c[t - 1] / peak_c - 1.0
    if ddy <= -kill:
        live[t] = 0.0
    elif ddy <= -soft:
        live[t] = max(0.0, 1.0 - (abs(ddy) - soft) / (kill - soft))
    else:
        live[t] = 1.0
    eq_c[t] = eq_c[t - 1] * (1.0 + live[t] * r.iloc[t])
    peak_c = max(peak_c, eq_c[t])
pnl_dd = r * live
eq_dd = pd.Series(eq_c, index=dates)

def ann_vol(pnl: pd.Series) -> float:
    x = pnl.dropna()
    return float(x.std(ddof=1) * ANN)

rows = [
    ("fixed", ann_vol(pnl_fixed), max_dd(eq_fixed), float(eq_fixed.iloc[-1])),
    ("vol_target", ann_vol(pnl_vt), max_dd(eq_vt), float(eq_vt.iloc[-1])),
    ("dd_brake", ann_vol(pnl_dd), max_dd(eq_dd), float(eq_dd.iloc[-1])),
]
for name, v, dd, nav in rows:
    print(f"{name}: ann_vol={v:.4f} maxDD={dd:.4f} end_nav={nav:.4f}")
print("NOTE: compare ann_vol & maxDD only — end_nav is diagnostic, NOT an edge claim")

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(eq_fixed.index, eq_fixed.values, label="fixed", lw=1.2)
ax.plot(eq_vt.index, eq_vt.values, label="vol_target", lw=1.2)
ax.plot(eq_dd.index, eq_dd.values, label="dd_brake", lw=1.2)
ax.set_title("Risk overlays on one synthetic path (not a strategy bake-off)")
ax.legend()
fig.tight_layout()
fig.savefig(PUBLIC / "regime_overlays.png", dpi=120)
plt.close()
print(f"wrote {PUBLIC / 'regime_overlays.png'}")

# ------------------------------------------------------------------
# Lab C: multi-asset corr→1 stress PnL
# ------------------------------------------------------------------
print("\n=== Lab C: multi-asset corr→1 stress PnL ===")
# 4-asset equal book; calm corr ~0.2; stress corr→1
n_assets = 4
w = np.ones(n_assets) / n_assets
# calm daily shocks
calm = rng.normal(0, 0.01, size=(60, n_assets))
# induce mild correlation
f = rng.normal(0, 0.006, size=60)
calm = calm * 0.8 + f[:, None] * 0.5
# stress day: common -8% shock + tiny idio (corr≈1)
stress = np.full(n_assets, -0.08) + rng.normal(0, 0.002, n_assets)
pnl_calm_mean = float((calm @ w).mean())
pnl_stress = float(w @ stress)
# pairwise corr in calm vs stress window (stress window = repeat stress-like days)
stress_panel = np.column_stack([stress + rng.normal(0, 0.001, n_assets) for _ in range(20)]).T
# better: 20 days of common-factor stress
f_s = rng.normal(-0.04, 0.02, 20)
stress_panel = np.column_stack([f_s + rng.normal(0, 0.003, 20) for _ in range(n_assets)])
corr_calm = np.corrcoef(calm.T)
corr_stress = np.corrcoef(stress_panel.T)
off_calm = corr_calm[np.triu_indices(n_assets, 1)].mean()
off_stress = corr_stress[np.triu_indices(n_assets, 1)].mean()
print(f"equal_w book; mean_daily_pnl_calm={pnl_calm_mean:.5f}")
print(f"one_day_common_shock_pnl={pnl_stress:.4f} (≈-0.08)")
print(f"mean_offdiag_corr_calm={off_calm:.3f} mean_offdiag_corr_stress={off_stress:.3f}")
print("teaching: diversification shrinks when corr→1 — stress PnL ≈ single-name crash")

# ------------------------------------------------------------------
# Lab D: toy HMM filtered vs smoothed (2-state Gaussian)
# ------------------------------------------------------------------
print("\n=== Lab D: HMM filtered vs smoothed (Hamilton filter spirit) ===")
# Plant 2-state mean/vol on a shorter series; estimate with known params (toy)
# State 0 calm: N(0.0005, 0.01^2); State 1 stress: N(-0.01, 0.03^2)
# Transition: sticky
p00, p11 = 0.97, 0.90
m = np.array([0.0005, -0.010])
s = np.array([0.010, 0.030])
T = 400
z = np.zeros(T, dtype=int)
z[0] = 0
# Force a long calm head so the filter-vs-smoother leak is visible before the first stress
force_onset = 80
for t in range(1, T):
    if t < force_onset:
        z[t] = 0
        continue
    if t == force_onset:
        z[t] = 1
        continue
    p_stay = p00 if z[t - 1] == 0 else p11
    z[t] = z[t - 1] if rng.random() < p_stay else 1 - z[t - 1]
y = rng.normal(m[z], s[z])

# Hamilton filter (forward)
# xi_t|t-1 then update with likelihood
xi_pred = np.zeros((T, 2))
xi_filt = np.zeros((T, 2))
xi_filt[0] = np.array([0.5, 0.5])
P = np.array([[p00, 1 - p00], [1 - p11, p11]])
for t in range(T):
    if t == 0:
        pred = xi_filt[0]
    else:
        pred = xi_filt[t - 1] @ P
    xi_pred[t] = pred
    lik = stats.norm.pdf(y[t], m, s)
    unnorm = pred * lik
    xi_filt[t] = unnorm / unnorm.sum()

# Kim smoother (backward) — uses FUTURE information
xi_smooth = np.zeros((T, 2))
xi_smooth[-1] = xi_filt[-1]
for t in range(T - 2, -1, -1):
    # P(S_t | y_1:T) ∝ filter * sum_j P(S_{t+1}=j|S_t) * smooth_{t+1,j} / pred_{t+1,j}
    pred_next = xi_filt[t] @ P
    # avoid div0
    ratio = np.divide(xi_smooth[t + 1], pred_next, out=np.zeros(2), where=pred_next > 1e-12)
    xi_smooth[t] = xi_filt[t] * (P @ ratio)
    xi_smooth[t] /= xi_smooth[t].sum()

# Leakage demo: at a crash onset, compare filter (causal) vs smoother (peek)
onset = int(np.argmax(z == 1))  # first stress
# look at day before onset: smoother often already elevated
day = max(onset - 1, 1)
print(f"first_stress_onset_t={onset}")
print(f"t={day} (day before onset): filt_P(stress)={xi_filt[day,1]:.3f} smooth_P(stress)={xi_smooth[day,1]:.3f}")
print(f"t={onset} (onset):           filt_P(stress)={xi_filt[onset,1]:.3f} smooth_P(stress)={xi_smooth[onset,1]:.3f}")
# count how often smoother exceeds filter before true stress by >0.15 in calm region
calm_before = np.where(z[:onset] == 0)[0]
if len(calm_before) > 5:
    leak_days = int(np.sum((xi_smooth[calm_before, 1] - xi_filt[calm_before, 1]) > 0.15))
    print(f"calm_days_before_onset={len(calm_before)} smoother_leads_filter_by_>0.15_on={leak_days} days")
print("HARD RULE: decision systems may use FILTERED probs only; SMOOTHED = research look-ahead")

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(xi_filt[:, 1], label="filtered P(stress)", lw=1.2)
ax.plot(xi_smooth[:, 1], label="smoothed P(stress)", lw=1.2, alpha=0.85)
ax.plot(z, label="true state", lw=0.8, alpha=0.5)
ax.axvline(onset, color="red", ls="--", lw=0.8, label="first stress onset")
ax.set_title("Hamilton filter vs Kim smoother (smoothed peeks ahead)")
ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig(PUBLIC / "regime_hmm_filter_vs_smooth.png", dpi=120)
plt.close()
print(f"wrote {PUBLIC / 'regime_hmm_filter_vs_smooth.png'}")

# Persist key numbers for lesson sync
out = {
    "n": n,
    "stress_hit_rate_in_planted_crash": stress_in_crash,
    "lab_b": {name: {"ann_vol": v, "maxDD": dd, "end_nav": nav} for name, v, dd, nav in rows},
    "corr_calm": off_calm,
    "corr_stress": off_stress,
    "pnl_stress": pnl_stress,
    "hmm_day_before": {"filt": float(xi_filt[day, 1]), "smooth": float(xi_smooth[day, 1])},
    "hmm_onset": {"filt": float(xi_filt[onset, 1]), "smooth": float(xi_smooth[onset, 1])},
}
pd.Series({k: str(v) for k, v in out.items()}).to_csv(DATA / "04_market_regimes_crisis_summary.csv")
print("\n=== done ===")
