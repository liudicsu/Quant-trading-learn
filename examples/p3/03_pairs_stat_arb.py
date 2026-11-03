"""P3 lab: Engle–Granger pairs, rolling cointegration pitfall, costs with impact.
Learning only — not investment advice.

EG two-step: (1) OLS hedge y = α + β x + u; (2) ADF on residual u.
Residual-based critical values differ from a plain unit-root ADF (MacKinnon).
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller, coint

from _common import PUBLIC, apply_costs, load_panel, oos_split, sharpe

df = load_panel()
x = df["BBB_adj"].astype(float)
rng = np.random.default_rng(7)
eps = np.zeros(len(x))
for i in range(1, len(x)):
    eps[i] = 0.85 * eps[i - 1] + rng.normal(0, 0.4)
y_coin = pd.Series(50.0 + 1.2 * x.values + eps, index=x.index, name="Y_coin")
y_drift = pd.Series(50.0 + 1.2 * x.values + eps + 0.05 * np.arange(len(x)), index=x.index, name="Y_drift")
y_aaa = df["AAA_adj"].astype(float)

ROLL = 40
Z_LB = 20
ENTRY, EXIT = 2.0, 0.5

print("=== parameters ===")
print("pairs: (A) Y_coin/BBB cointegrated foil; (B) Y_drift/BBB broken/non-coint foil")
print("also report AAA/BBB as a raw-panel foil")
print("rolling OLS", ROLL, "z_lb", Z_LB, "enter |z|>", ENTRY, "exit |z|<", EXIT)
print("costs: shared P2 model with n_legs=2 (stack + √impact)")
print("cite: Engle–Granger two-step; MacKinnon residual-based critical values")
print("cite: Stern pairs; Canvas m8; quants.md W13/W14 foils")
print("further_reading: Ernest P. Chan, Algorithmic Trading..., Wiley 2013 — no quotes")


def ols_hedge(y: pd.Series, x: pd.Series) -> tuple[float, float, pd.Series]:
    ok = pd.concat([y, x], axis=1).dropna()
    Y, Xv = ok.iloc[:, 0].values, ok.iloc[:, 1].values
    X = np.column_stack([np.ones(len(Xv)), Xv])
    coef, *_ = np.linalg.lstsq(X, Y, rcond=None)
    alpha, beta = float(coef[0]), float(coef[1])
    resid = y - alpha - beta * x
    return alpha, beta, resid


def adf_hand(resid: pd.Series, maxlag: int = 1) -> dict:
    """ADF on residual with constant, lag=1: Δu = a + φ u_{t-1} + γ Δu_{t-1} + e.
    Reports OLS t-stat for φ; p-value via statsmodels' MacKinnon when available —
    here we also print the raw t and compare to adfuller.
    """
    u = resid.dropna()
    du = u.diff()
    u_lag = u.shift(1)
    du_lag = du.shift(1)
    ok = pd.concat([du, u_lag, du_lag], axis=1).dropna()
    yy = ok.iloc[:, 0].values
    XX = np.column_stack([np.ones(len(ok)), ok.iloc[:, 1].values, ok.iloc[:, 2].values])
    coef, *_ = np.linalg.lstsq(XX, yy, rcond=None)
    # residual variance / (X'X)^{-1}
    yhat = XX @ coef
    e = yy - yhat
    s2 = float(e @ e) / (len(yy) - XX.shape[1])
    xtx_inv = np.linalg.inv(XX.T @ XX)
    se_phi = float(np.sqrt(s2 * xtx_inv[1, 1]))
    t_phi = float(coef[1] / se_phi)
    return {"phi": float(coef[1]), "t_phi": t_phi, "se_phi": se_phi, "n": len(yy)}


def eg_report(name: str, y: pd.Series, x: pd.Series) -> dict:
    alpha, beta, resid = ols_hedge(y, x)
    # statsmodels coint: EG with autolag; returns t-stat, pvalue (MacKinnon), crit
    t_coint, p_coint, crit = coint(y.dropna(), x.reindex(y.dropna().index).dropna(), trend="c", autolag="aic")
    # ADF on residual (regression ADF) — note: plain ADF critical values are NOT exact for EG residuals
    adf_res = adfuller(resid.dropna(), maxlag=1, regression="c", autolag=None, result_object=False)
    hand = adf_hand(resid, maxlag=1)
    out = {
        "name": name,
        "alpha": alpha,
        "beta": beta,
        "coint_t": float(t_coint),
        "coint_pvalue": float(p_coint),
        "coint_crit_5pct": float(crit[1]),
        "adf_resid_t": float(adf_res[0]),
        "adf_resid_pvalue_plain": float(adf_res[1]),
        "hand_t_phi": hand["t_phi"],
        "resid_std": float(resid.std(ddof=1)),
    }
    return out, resid


print("\n=== Engle–Granger two-step (full sample) ===")
print("step1: OLS y = alpha + beta x + u")
print("step2: test residual u for unit root; p-values from coint() use MacKinnon EG tables")
print("pitfall: adfuller(p) on residuals uses *plain* ADF null tables — anti-conservative vs EG")

rows = []
for name, y in [("Y_coin/BBB", y_coin), ("Y_drift/BBB", y_drift), ("AAA/BBB", y_aaa)]:
    rep, _ = eg_report(name, y, x)
    rows.append(rep)
    print(
        f"{name}: beta={rep['beta']:.4f} coint_p={rep['coint_pvalue']:.4g} "
        f"coint_t={rep['coint_t']:.3f} crit5={rep['coint_crit_5pct']:.3f} "
        f"adf_plain_p={rep['adf_resid_pvalue_plain']:.4g} hand_t={rep['hand_t_phi']:.3f}"
    )

print("\ncompare: Y_coin should reject unit root in residual (small coint_p); Y_drift / AAA often fail")

# Rolling EG p-values (pitfall: in-sample only vs rolling)
print("\n=== rolling cointegration p-values (window=80) ===")
WIN = 80
roll_p_coin = []
roll_p_drift = []
idx = []
for i in range(WIN, len(x)):
    sl = slice(i - WIN, i)
    _, p1, _ = coint(y_coin.iloc[sl], x.iloc[sl], trend="c", autolag="aic")
    _, p2, _ = coint(y_drift.iloc[sl], x.iloc[sl], trend="c", autolag="aic")
    roll_p_coin.append(p1)
    roll_p_drift.append(p2)
    idx.append(x.index[i - 1])
roll = pd.DataFrame({"p_Y_coin": roll_p_coin, "p_Y_drift": roll_p_drift}, index=idx)
print(f"Y_coin rolling p: median={roll['p_Y_coin'].median():.4g} frac_p<0.05={float((roll['p_Y_coin']<0.05).mean()):.3f}")
print(f"Y_drift rolling p: median={roll['p_Y_drift'].median():.4g} frac_p<0.05={float((roll['p_Y_drift']<0.05).mean()):.3f}")
print("pitfall: a single full-sample coint_p can look fine while rolling windows flip in/out of cointegration")


def rolling_beta(yy, xx, w):
    out = pd.Series(np.nan, index=yy.index)
    for i in range(w, len(yy)):
        a, b, _ = ols_hedge(yy.iloc[i - w : i], xx.iloc[i - w : i])
        out.iloc[i] = b
    return out


def pairs_intent(z: pd.Series) -> pd.Series:
    intent = pd.Series(0.0, index=z.index)
    state = 0.0
    for i in range(len(z)):
        zi = z.iloc[i]
        if np.isnan(zi):
            intent.iloc[i] = 0.0
            continue
        if state == 0.0:
            if zi > ENTRY:
                state = -1.0
            elif zi < -ENTRY:
                state = 1.0
        elif abs(zi) < EXIT:
            state = 0.0
        intent.iloc[i] = state
    return intent.shift(1).fillna(0.0)


# Trade the cointegrated foil with static vs rolling hedge
alpha_s, beta_s, spread_s = ols_hedge(y_coin.iloc[: int(0.4 * len(y_coin))], x.iloc[: int(0.4 * len(x))])
# static beta from first 40%
spread_static = y_coin - alpha_s - beta_s * x
beta_r = rolling_beta(y_coin, x, ROLL)
# reconstruct rolling residual with rolling intercept≈0 for simplicity: y - beta_r * x - mean
spread_roll = y_coin - beta_r * x
spread_roll = spread_roll - spread_roll.rolling(Z_LB).mean()  # center
z_s = (spread_static - spread_static.rolling(Z_LB).mean()) / spread_static.rolling(Z_LB).std(ddof=1)
z_r = (spread_roll) / spread_roll.rolling(Z_LB).std(ddof=1)
pos_s = pairs_intent(z_s)
pos_r = pairs_intent(z_r)
ry = y_coin.pct_change()
rx = x.pct_change()
spread_ret_s = ry - beta_s * rx
spread_ret_r = ry - beta_r.shift(1).bfill() * rx

# price proxy for impact: average of legs
px_ref = (y_coin + x) / 2.0
net_s, _, st_s = apply_costs(pos_s, spread_ret_s, px_ref, n_legs=2)
net_r, _, st_r = apply_costs(pos_r, spread_ret_r, px_ref, n_legs=2)

train, test = oos_split(ry.dropna().index, 0.7)
print("\n=== static vs rolling hedge (Y_coin, net costs n_legs=2) ===")
print(f"static  net_SR={st_s['net_sharpe']:.3f} NAV={st_s['net_nav']:.4f} turn={st_s['mean_turnover']:.4f} OOS={sharpe(net_s.reindex(test)):.3f}")
print(f"rolling net_SR={st_r['net_sharpe']:.3f} NAV={st_r['net_nav']:.4f} turn={st_r['mean_turnover']:.4f} OOS={sharpe(net_r.reindex(test)):.3f}")
print("\n=== shock / broken-leg note ===")
print("After an idiosyncratic gap, static hedge leaves residual beta; rolling adapts with lag=ROLL.")
print(f"|beta_roll-beta_static| mean last 60 = {float((beta_r - beta_s).iloc[-60:].abs().mean()):.4f}")

fig, axes = plt.subplots(3, 1, figsize=(9, 8), sharex=False)
axes[0].plot(roll.index, roll["p_Y_coin"], label="roll p Y_coin")
axes[0].plot(roll.index, roll["p_Y_drift"], label="roll p Y_drift")
axes[0].axhline(0.05, color="r", ls="--", alpha=0.6)
axes[0].set_title("Rolling Engle–Granger p-values")
axes[0].legend(); axes[0].grid(True, alpha=0.3)
axes[1].plot(z_r.index, z_r.values, label="z_roll")
axes[1].axhline(ENTRY, color="r", ls="--", alpha=0.5)
axes[1].axhline(-ENTRY, color="r", ls="--", alpha=0.5)
axes[1].legend(); axes[1].grid(True, alpha=0.3)
eq_s = (1 + net_s.fillna(0)).cumprod()
eq_r = (1 + net_r.fillna(0)).cumprod()
axes[2].plot(eq_s.index, eq_s.values, label="static_net")
axes[2].plot(eq_r.index, eq_r.values, label="rolling_net")
axes[2].set_title("Pairs NAV (2-leg costs + impact)")
axes[2].legend(); axes[2].grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(PUBLIC / "pairs_nav.png", dpi=120)
print("\nchart", PUBLIC / "pairs_nav.png")
print("disclaimer: synthetic; learning only")
