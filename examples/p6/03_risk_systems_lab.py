"""P6 lab 03: VaR/CVaR, Kupiec, stress, DD rules, concentration/leverage — all lagged.
Learning only — not investment advice. Includes gap + secrets checklist for the lab.
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from _common import PUBLIC, DATA, make_asset_panel, lagged_vol, max_dd

print("=== parameters ===")
print("alpha=0.05 VaR; lookback L=252 for hist/param; MC paths=5000; Kupiec LR on exceptions")
print("all risk estimates use only past returns (shift so day-t VaR uses data through t-1)")
print("cite: Kupiec 1995 J. Derivatives — Techniques for verifying the accuracy of risk measurement models")
print("cite: Artzner et al. 1999 Math. Finance — Coherent measures of risk (CVaR/ES motivation)")
print("cite: lag all estimates — no look-ahead into same-day PnL")

rng = np.random.default_rng(7)
panel = make_asset_panel(n_assets=1, n_days=1500, seed=7)
# single synthetic series with fat tails
ret = panel.iloc[:, 0].values.copy()
# mild negative skew overlay (not catastrophic jumps) so VaR exceptions are informative
ret = ret - 0.0001 + rng.standard_t(6, size=len(ret)) * 0.002
dates = panel.index
L = 252
alpha = 0.05

# Historical / parametric / MC VaR — lagged
hvar = np.full(len(ret), np.nan)
pvar = np.full(len(ret), np.nan)
cvar = np.full(len(ret), np.nan)
for t in range(L + 1, len(ret)):
    window = ret[t - L : t]  # through t-1
    hvar[t] = -np.quantile(window, alpha)
    mu, sig = window.mean(), window.std(ddof=1)
    pvar[t] = -(mu + sig * stats.norm.ppf(alpha))
    # MC: student-t calibrated (df from moments rough)
    z = rng.standard_t(5, size=2000)
    z = (z - z.mean()) / z.std() * sig + mu
    h = -np.quantile(z, alpha)
    # CVaR historical
    thr = np.quantile(window, alpha)
    cvar[t] = -window[window <= thr].mean()
    # store MC var in pvar slot alternate — keep parametric; print MC separately at end

# exceptions: loss > VaR (loss = -ret when ret negative)
loss = -ret
exc_h = (loss > hvar) & np.isfinite(hvar)
exc_p = (loss > pvar) & np.isfinite(pvar)
n_test = int(np.isfinite(hvar).sum())
x_h = int(exc_h.sum()); x_p = int(exc_p.sum())
p_hat_h = x_h / n_test; p_hat_p = x_p / n_test

def kupiec_lr(x, n, p=alpha):
    """Kupiec unconditional coverage LR ~ chi2(1)."""
    if x == 0 or x == n:
        return np.nan, np.nan
    p_hat = x / n
    lr = -2 * (
        (n - x) * np.log(1 - p) + x * np.log(p)
        - ((n - x) * np.log(1 - p_hat) + x * np.log(p_hat))
    )
    pval = 1 - stats.chi2.cdf(lr, 1)
    return lr, pval

lr_h, pv_h = kupiec_lr(x_h, n_test)
lr_p, pv_p = kupiec_lr(x_p, n_test)
print("\n=== VaR backtest (Kupiec) ===")
print(f"n={n_test} hist_exceptions={x_h} rate={p_hat_h:.4f} (target {alpha}) LR={lr_h:.3f} p={pv_h:.3f}")
print(f"n={n_test} para_exceptions={x_p} rate={p_hat_p:.4f} (target {alpha}) LR={lr_p:.3f} p={pv_p:.3f}")
finite = np.isfinite(hvar) & np.isfinite(cvar)
cvar_ge = float(np.mean(cvar[finite] >= hvar[finite])) if finite.any() else float("nan")
print(f"mean_hist_VaR={np.nanmean(hvar):.4f} mean_CVaR={np.nanmean(cvar):.4f} CVaR>=VaR check={cvar_ge:.2f} (finite days only; expect 1.00)")

# MC VaR snapshot at last day
window = ret[-L - 1 : -1]
mu, sig = window.mean(), window.std(ddof=1)
mc = rng.standard_t(5, size=5000)
mc = (mc - mc.mean()) / mc.std() * sig + mu
mc_var = -np.quantile(mc, alpha)
mc_cvar = -mc[mc <= np.quantile(mc, alpha)].mean()
print(f"MC_t5 VaR={mc_var:.4f} CVaR={mc_cvar:.4f}")

# Stress tests
print("\n=== stress tests (scenario PnL) ===")
w = np.array([0.25, 0.25, 0.25, 0.25])  # equal book
scenarios = {
    "equity_-10pct": np.array([-0.10, -0.10, -0.02, 0.01]),
    "rates_+100bp_proxy": np.array([-0.03, -0.04, -0.08, 0.02]),
    "vol_spike_corr1": np.array([-0.08, -0.08, -0.08, -0.08]),
}
for name, shock in scenarios.items():
    pnl = float(w @ shock)
    print(f"stress {name}: book_pnl={pnl:.4f}")

# Drawdown control rule (lagged): scale risk by remaining DD budget on the *controlled* book
print("\n=== drawdown control (lagged) ===")
# cut exposure as trailing DD from peak deepens; decision at t uses controlled equity through t-1
kill = 0.20
soft = 0.10
live = np.ones(len(ret))
eq_c_path = np.ones(len(ret))
peak_c = 1.0
for t in range(1, len(ret)):
    ddy = eq_c_path[t - 1] / peak_c - 1.0
    if ddy <= -kill:
        live[t] = 0.0
    elif ddy <= -soft:
        live[t] = max(0.0, 1.0 - (abs(ddy) - soft) / (kill - soft))
    else:
        live[t] = 1.0
    eq_c_path[t] = eq_c_path[t - 1] * (1.0 + live[t] * ret[t])
    peak_c = max(peak_c, eq_c_path[t])
ret_ctrl = ret * live
eq_u = pd.Series(np.cumprod(1 + ret))
eq_c = pd.Series(eq_c_path)
print(f"uncontrolled maxDD={max_dd(eq_u):.3f} controlled maxDD={max_dd(eq_c):.3f} mean_exposure={live.mean():.3f} days_flat={(live==0).sum()}")

# Concentration & leverage limits
print("\n=== concentration & leverage limits ===")
# random weights then project
raw = rng.dirichlet(np.ones(8), size=5)
w_max, lev_max = 0.30, 1.5
for i, w0 in enumerate(raw):
    # gross leverage
    w = w0 / w0.sum()
    # clip concentration
    for _ in range(20):
        w = np.clip(w, 0, w_max)
        w = w / w.sum()
    gross = np.abs(w).sum()
    if gross > lev_max:
        w = w * (lev_max / gross)
    print(f"book{i}: max_w={w.max():.3f} gross={np.abs(w).sum():.3f} (limits w<={w_max} gross<={lev_max})")

# Chart: VaR band vs losses
fig, ax = plt.subplots(figsize=(8, 3.5))
idx = np.arange(len(ret))
ax.plot(idx, loss, color="#888", lw=0.5, label="loss")
ax.plot(idx, hvar, color="#c0392b", lw=1, label="hist VaR 95% (lagged)")
ax.plot(idx, cvar, color="#8e44ad", lw=1, alpha=0.8, label="hist CVaR")
ax.scatter(idx[exc_h], loss[exc_h], s=8, color="red", label="exceptions", zorder=3)
ax.legend(fontsize=8); ax.set_title("Lagged historical VaR/CVaR vs realized loss")
ax.set_xlabel("day"); ax.grid(True, alpha=0.3)
fig.tight_layout(); fig.savefig(PUBLIC / "var_backtest.png", dpi=120); plt.close()
print("chart", PUBLIC / "var_backtest.png")

print("\n=== lab checklist: gap analysis & secrets hygiene (teach) ===")
print("gap: map each risk limit to an owner, metric, breach action, and lagged data source")
print("secrets: no API keys in notebooks; rotate; least privilege; separate paper vs live credentials")
print("disclaimer: educational simulations — not a production risk system or trading advice")
