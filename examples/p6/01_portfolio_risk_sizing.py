"""P6 lab 01: Kelly / half-Kelly, vol target, risk parity, MV vs 1/N, Ledoit–Wolf.
Learning only — not investment advice.
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.covariance import LedoitWolf, empirical_covariance

from _common import ANN, DATA, PUBLIC, lagged_vol, make_asset_panel, max_dd, sharpe

print("=== parameters ===")
print("panel: 10 assets × 1000 days synthetic; look-ahead: all vol/cov use shift(1) / expanding train only")
print("cite: Kelly 1956 Bell System Tech. J. — fortune's formula / growth-optimal bet")
print("cite: Thorp 2006 — The Kelly criterion in blackjack, sports betting, and the stock market (handbook ch.)")
print("cite: Markowitz 1952 JOF — Portfolio Selection")
print("cite: Michaud 1989 — The Markowitz optimization enigma (estimation error / 'error maximization')")
print("cite: DeMiguel, Garlappi & Uppal 2009 RFS 22(5) — Optimal vs naive diversification; 1/N hard to beat OOS")
print("cite: Ledoit & Wolf 2004 JPM — 'Honey, I Shrunk the Sample Covariance Matrix'")
print("cite: Ledoit & Wolf 2004 JMVA 88(2) — well-conditioned shrinkage (sklearn LedoitWolf)")

rets = make_asset_panel()
rets.to_csv(DATA / "asset_returns.csv")
print("panel", rets.shape)

# ----- Kelly simulation -----
print("\n=== Kelly / fractional Kelly simulation ===")
rng = np.random.default_rng(0)
# coin with p=0.55, even money: f* = 2p-1 = 0.10
p, b = 0.55, 1.0
f_star = (p * (b + 1) - 1) / b
print(f"Bernoulli edge: p={p} even-money → f*={f_star:.3f}")
n_paths, n_bets = 500, 500
wealth = {lab: np.ones((n_paths, n_bets + 1)) for lab in ["full", "half", "double"]}
fs = {"full": f_star, "half": 0.5 * f_star, "double": 2.0 * f_star}
for lab, f in fs.items():
    for t in range(n_bets):
        win = rng.random(n_paths) < p
        # wealth update
        wealth[lab][:, t + 1] = wealth[lab][:, t] * (1 + np.where(win, f * b, -f))
        wealth[lab][:, t + 1] = np.maximum(wealth[lab][:, t + 1], 1e-12)

def path_stats(W):
    terminal = W[:, -1]
    ruined = (terminal < 0.01).mean()  # <1% of start ≈ ruin foil
    # median log growth
    g = np.median(np.log(terminal))
    # median max DD along path
    dds = []
    for i in range(min(100, W.shape[0])):
        eq = pd.Series(W[i])
        dds.append(max_dd(eq))
    return float(g), float(ruined), float(np.median(dds))

for lab in ["full", "half", "double"]:
    g, ruin, dd = path_stats(wealth[lab])
    print(f"Kelly_{lab:6s} f={fs[lab]:.3f} median_log_growth={g:.3f} ruin_rate={ruin:.3f} median_maxDD={dd:.3f}")
print("teach: over-betting (2×Kelly) raises ruin / DD; half-Kelly trades growth for smaller drawdowns (Thorp)")

fig, ax = plt.subplots(figsize=(8, 4))
for lab, color in [("full", "#1f4e79"), ("half", "#2e7d32"), ("double", "#c45911")]:
    ax.plot(np.median(wealth[lab], axis=0), label=f"{lab} Kelly", color=color)
ax.set_yscale("log"); ax.set_title("Median wealth path: full / half / 2× Kelly")
ax.legend(); ax.grid(True, alpha=0.3)
fig.tight_layout(); fig.savefig(PUBLIC / "kelly_paths.png", dpi=120); plt.close()

# ----- Vol targeting -----
print("\n=== volatility targeting (lagged vol) ===")
asset = rets["A00"]
vol = lagged_vol(asset, 20)
target = 0.10 / ANN  # 10% ann → daily
w = (target / vol.replace(0, np.nan)).clip(0, 3).fillna(0)
pnl_vt = w.shift(1).fillna(0) * asset  # position from prior close
pnl_raw = asset
print(f"raw_SR={sharpe(pnl_raw):.3f} vol_target_SR={sharpe(pnl_vt):.3f} realized_ann_vol_raw={asset.std()*ANN:.3f} vt={pnl_vt.std()*ANN:.3f}")
print("look-ahead: vol uses shift(1); weights enter next bar")

# ----- Risk parity: inverse-vol and ERC -----
print("\n=== risk parity: inverse-vol and ERC (equal risk contribution) ===")
# expanding cov with lag: use past 120d ending t-1

def erc_weights(cov, n_iter=50, tol=1e-8):
    """Simple cyclical ERC (Maillard–Roncalli–Teiletche style toy)."""
    n = cov.shape[0]
    w = np.ones(n) / n
    for _ in range(n_iter):
        sig_p = float(np.sqrt(w @ cov @ w))
        if sig_p < 1e-12:
            break
        mrc = cov @ w / sig_p          # marginal risk contribution
        rc = w * mrc                   # risk contribution
        # target equal RC = sig_p / n
        w = w * (sig_p / n) / np.maximum(rc, 1e-12)
        w = np.maximum(w, 0)
        w = w / w.sum()
        if np.std(rc) < tol:
            break
    return w

w_iv = pd.DataFrame(index=rets.index, columns=rets.columns, dtype=float)
w_erc = pd.DataFrame(index=rets.index, columns=rets.columns, dtype=float)
w_ew = pd.DataFrame(1.0 / rets.shape[1], index=rets.index, columns=rets.columns)
for i in range(120, len(rets)):
    window = rets.iloc[i - 120 : i]  # excludes day i → no look-ahead
    sig = window.std(ddof=1).replace(0, np.nan)
    inv = 1.0 / sig
    w_iv.iloc[i] = inv / inv.sum()
    cov = window.cov().values
    w_erc.iloc[i] = erc_weights(cov)
pnl_iv = (w_iv.shift(1).fillna(0) * rets).sum(axis=1)
pnl_erc = (w_erc.shift(1).fillna(0) * rets).sum(axis=1)
pnl_ew = (w_ew.shift(1) * rets).sum(axis=1)
print(f"inv_vol_SR={sharpe(pnl_iv):.3f} ERC_SR={sharpe(pnl_erc):.3f} equal_weight_SR={sharpe(pnl_ew):.3f}")
# show one-day RC dispersion for last ERC book
last = w_erc.dropna().iloc[-1].values.astype(float)
cov_last = rets.iloc[-120:].cov().values
sig_p = float(np.sqrt(last @ cov_last @ last))
rc = last * (cov_last @ last) / sig_p
print(f"ERC last-day RC std={rc.std():.6f} (near 0 ⇒ equal risk); inv-vol ignores correlations")

# ----- Mean-variance vs 1/N vs Ledoit-Wolf -----
print("\n=== mean-variance vs 1/N vs Ledoit–Wolf shrinkage (OOS) ===")
# walk-forward: estimate on [t-250,t), hold for 21d
hold = 21
est = 250
rows = []
wealth_mv = wealth_lw = wealth_1n = 1.0
eq_mv, eq_lw, eq_1n = [], [], []
idx = []
for i in range(est, len(rets) - hold, hold):
    train = rets.iloc[i - est : i]
    test = rets.iloc[i : i + hold]
    mu = train.mean().values
    S = empirical_covariance(train.values)
    lw = LedoitWolf().fit(train.values)
    Sigma_lw = lw.covariance_
    # long-only MV: max w'μ - 0.5 w'Σw approx via closed form unconstrained then project
    def mv_weights(Sigma, mu, gamma=5.0):
        try:
            inv = np.linalg.pinv(Sigma)
            w = inv @ mu / gamma
            w = np.maximum(w, 0)
            if w.sum() <= 0:
                w = np.ones_like(w) / len(w)
            else:
                w = w / w.sum()
            return w
        except Exception:
            return np.ones(len(mu)) / len(mu)
    w_mv = mv_weights(S, mu)
    w_l = mv_weights(Sigma_lw, mu)
    w_1 = np.ones(len(mu)) / len(mu)
    # OOS pnl
    r = test.values
    pnl_m = r @ w_mv
    pnl_l = r @ w_l
    pnl_n = r @ w_1
    for t, a, b, c in zip(test.index, pnl_m, pnl_l, pnl_n):
        wealth_mv *= 1 + a
        wealth_lw *= 1 + b
        wealth_1n *= 1 + c
        eq_mv.append(wealth_mv); eq_lw.append(wealth_lw); eq_1n.append(wealth_1n); idx.append(t)
    rows.append({
        "mv": pnl_m.mean(), "lw": pnl_l.mean(), "one_n": pnl_n.mean(),
        "shrinkage": float(lw.shrinkage_),
    })
eq = pd.DataFrame({"mv": eq_mv, "lw": eq_lw, "one_n": eq_1n}, index=idx)
print(f"OOS_SR mv={sharpe(eq['mv'].pct_change()):.3f} LedoitWolf={sharpe(eq['lw'].pct_change()):.3f} 1/N={sharpe(eq['one_n'].pct_change()):.3f}")
print(f"mean_shrinkage_intensity={np.mean([r['shrinkage'] for r in rows]):.3f}")
print("teach: estimation error (Michaud) can make sample-MV lose to 1/N OOS (DeMiguel et al. 2009); shrinkage helps condition Σ")

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(eq.index, eq["mv"], label="sample MV")
ax.plot(eq.index, eq["lw"], label="Ledoit–Wolf MV")
ax.plot(eq.index, eq["one_n"], label="1/N")
ax.legend(); ax.grid(True, alpha=0.3); ax.set_title("OOS equity: MV vs LW vs 1/N")
fig.tight_layout(); fig.savefig(PUBLIC / "mv_vs_1n.png", dpi=120); plt.close()
print("chart", PUBLIC / "kelly_paths.png")
print("chart", PUBLIC / "mv_vs_1n.png")
print("disclaimer: synthetic panel — learning only, not investment advice")
