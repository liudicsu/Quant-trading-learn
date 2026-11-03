"""P1 lab: annualized vol, Sharpe (Rf stated), MDD, rolling vol & stress corr plots.
Learning only — not investment advice.
Parameters: n from CSV; ann=√252; Rf_daily=0; rolling windows 21 (vol) and 63 (corr); seed for asset B=21.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CSV = Path(__file__).resolve().parent / "data" / "synthetic_ohlc_ba.csv"
OUT_VOL = ROOT / "public" / "p1" / "rolling_vol.png"
OUT_CORR = ROOT / "public" / "p1" / "rolling_corr_stress.png"

raw = pd.read_csv(CSV, parse_dates=["date"]).set_index("date").sort_index()
r = raw["close"].pct_change().dropna()
n = len(r)
ANN = np.sqrt(252)
RF_D = 0.0
print("=== parameters ===")
print("n", n)
print("ann_factor_sqrt252", round(float(ANN), 6))
print("Rf_daily", RF_D)
print("Rf_note: teaching Sharpe uses Rf=0; always declare frequency and Rf.")

sig_d = float(r.std(ddof=1))
sig_ann = sig_d * float(ANN)
sharpe = float((r.mean() - RF_D) / sig_d * ANN)
print("\n=== vol & Sharpe ===")
print("sigma_daily", round(sig_d, 6))
print("sigma_ann", round(sig_ann, 6))
print("sharpe_ann_Rf0", round(sharpe, 4))


def max_drawdown(nav: pd.Series) -> float:
    peak = nav.cummax()
    dd = nav / peak - 1.0
    return float(dd.min())


nav = (1 + r).cumprod()
mdd = max_drawdown(nav)
print("\n=== max drawdown (path-dependent) ===")
print("final_nav", round(float(nav.iloc[-1]), 6))
print("max_drawdown", round(mdd, 6))
print("mdd_note: same returns in different order → different MDD; path matters.")

# Rolling vol plot
roll_vol = r.rolling(21).std(ddof=1) * ANN
OUT_VOL.parent.mkdir(parents=True, exist_ok=True)
fig, ax = plt.subplots(figsize=(7.5, 3.4), dpi=120)
ax.plot(roll_vol.index, roll_vol.values, color="#2563eb", label="21d vol ann")
ax.axhline(sig_ann, color="#ef4444", ls="--", label=f"full-sample σ_ann={sig_ann:.3f}")
ax.set_title("Rolling 21d annualized volatility (synthetic)")
ax.set_ylabel("σ_ann")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)
fig.autofmt_xdate()
fig.tight_layout()
fig.savefig(OUT_VOL)
plt.close(fig)
print("saved_plot", OUT_VOL.relative_to(ROOT).as_posix())

# Second asset + stress window where corr rises
rng = np.random.default_rng(21)
# Base: mild corr; stress block: shared shock
eps = rng.normal(0, 0.01, n)
b = 0.25 * r.values + eps
# Stress: last 40 days amplify common factor
stress_slice = slice(-40, None)
shock = rng.normal(0, 0.02, 40)
b[stress_slice] = 0.85 * r.values[stress_slice] + 0.15 * eps[stress_slice] + shock
r_b = pd.Series(b, index=r.index, name="b")
full_corr = float(r.corr(r_b))
roll_corr = r.rolling(63).corr(r_b)
print("\n=== correlation ===")
print("params: seed_b=21; stress_last_40_sessions; roll_window=63")
print("full_sample_corr", round(full_corr, 4))
print("rolling_63_corr_tail")
print(roll_corr.dropna().tail(5).round(4).to_string())
print("stress_window_mean_roll_corr", round(float(roll_corr.iloc[stress_slice].mean()), 4))

fig, ax = plt.subplots(figsize=(7.5, 3.4), dpi=120)
ax.plot(roll_corr.index, roll_corr.values, color="#059669", label="63d rolling corr")
ax.axhline(full_corr, color="#6b7280", ls="--", label=f"full corr={full_corr:.3f}")
# Mark stress region
stress_start = r.index[stress_slice][0]
ax.axvspan(stress_start, r.index[-1], color="#fca5a5", alpha=0.35, label="stress window")
ax.set_title("Rolling correlation with stress window marked")
ax.set_ylim(-0.2, 1.05)
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)
fig.autofmt_xdate()
fig.tight_layout()
fig.savefig(OUT_CORR)
plt.close(fig)
print("saved_plot", OUT_CORR.relative_to(ROOT).as_posix())
print("ASSERTS_OK")
