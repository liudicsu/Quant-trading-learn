"""P3 lab: pairs spread, rolling hedge, corr≠tradeable, costs.
Learning only — not investment advice.

Stern syllabus: spreads/pairs after counter-trend. High correlation alone is not a trade.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from _common import PUBLIC, apply_costs, load_panel, nav, oos_split, sharpe

df = load_panel()
x = df["BBB_adj"].astype(float)
# Construct a cointegrated-like y = 50 + 1.2*x + AR(1) residual (lab foil)
rng = np.random.default_rng(7)
eps = np.zeros(len(x))
for i in range(1, len(x)):
    eps[i] = 0.85 * eps[i - 1] + rng.normal(0, 0.4)
y = pd.Series(50.0 + 1.2 * x.values + eps, index=x.index, name="Y_coin")
# Non-cointegrated high-corr foil: same shocks but with drifting intercept
t_idx = np.arange(len(x))
y_drift = pd.Series(50.0 + 1.2 * x.values + eps + 0.05 * t_idx, index=x.index)
ry = y.pct_change()
rx = x.pct_change()

ROLL = 40
Z_LB = 20
ENTRY = 2.0
EXIT = 0.5

print("=== parameters ===")
print("pair synthetic Y_coin vs BBB (cointegrated foil); rolling OLS window", ROLL, "z_lb", Z_LB)
print("enter |z|>", ENTRY, "exit |z|<", EXIT, "; dollar-neutral ≈ long y short beta*x")
print("look-ahead: beta/z use past windows only; positions shift(1)")
print("cite: Stern Dhar pairs session; Canvas m8; quants.md W13/W14 pairs as open foils (metrics often near 0)")


def rolling_beta(yy: pd.Series, xx: pd.Series, w: int) -> pd.Series:
    out = pd.Series(np.nan, index=yy.index)
    for i in range(w, len(yy)):
        ys = yy.iloc[i - w : i].values
        xs = xx.iloc[i - w : i].values
        if np.any(~np.isfinite(ys)) or np.any(~np.isfinite(xs)):
            continue
        xs_ = np.column_stack([np.ones(w), xs])
        try:
            coef, *_ = np.linalg.lstsq(xs_, ys, rcond=None)
            out.iloc[i] = coef[1]
        except np.linalg.LinAlgError:
            pass
    return out


# static beta on first 40% train
cut = int(len(y) * 0.4)
beta_static = float(np.polyfit(x.iloc[:cut], y.iloc[:cut], 1)[0])
beta_roll = rolling_beta(y, x, ROLL)

spread_static = y - beta_static * x
spread_roll = y - beta_roll * x

corr_coin = float(ry.corr(rx))
corr_drift = float(y_drift.pct_change().corr(rx))
# residual variance growth under drift foil (levels diverge)
resid_coin = (y - 1.2 * x)
resid_drift = (y_drift - 1.2 * x)
print("\n=== corr vs cointegration intuition ===")
print(f"corr_returns_coint_pair={corr_coin:.3f}")
print(f"corr_returns_drift_foil={corr_drift:.3f} (can stay high while levels walk apart)")
print(f"resid_std_coint={float(resid_coin.std()):.3f} resid_std_drift={float(resid_drift.std()):.3f}")
print(f"beta_static={beta_static:.4f} beta_roll_mean={float(beta_roll.mean()):.4f}")
print("teach: high return correlation ≠ tradeable; need (approx) stationary residual / cointegration intuition")


def zscore(s: pd.Series, w: int) -> pd.Series:
    m = s.rolling(w).mean()
    sd = s.rolling(w).std(ddof=1)
    return (s - m) / sd


def pairs_pos(z: pd.Series) -> pd.Series:
    """+1 = long spread (long y short beta x); -1 = short spread."""
    pos = pd.Series(0.0, index=z.index)
    state = 0.0
    for i in range(len(z)):
        zi = z.iloc[i]
        if np.isnan(zi):
            pos.iloc[i] = 0.0
            continue
        if state == 0.0:
            if zi > ENTRY:
                state = -1.0
            elif zi < -ENTRY:
                state = 1.0
        else:
            if abs(zi) < EXIT:
                state = 0.0
        pos.iloc[i] = state
    return pos.shift(1)


z_s = zscore(spread_static, Z_LB)
z_r = zscore(spread_roll, Z_LB)
pos_s = pairs_pos(z_s)
pos_r = pairs_pos(z_r)

# PnL ≈ pos * (ry - beta * rx); use contemporaneous beta_roll.shift(1)
beta_lag = beta_roll.shift(1).fillna(beta_static)
spread_ret_s = ry - beta_static * rx
spread_ret_r = ry - beta_lag * rx

# apply costs on |pos| notional (both legs → ~2x turnover notionally)
# approximate: treat as single series with 2x one-way bps
from _common import ONE_WAY_BPS

def net_from(pos, spread_ret, px_ref):
    turnover = pos.diff().abs().fillna(pos.abs())
    gross = pos * spread_ret
    # two legs
    c = turnover * (2 * ONE_WAY_BPS / 1e4)
    net = gross - c
    return net, turnover, {
        "gross_sr": sharpe(gross),
        "net_sr": sharpe(net),
        "nav": nav(net),
        "turn": float(turnover.mean()),
    }

net_s, to_s, st_s = net_from(pos_s, spread_ret_s, y)
net_r, to_r, st_r = net_from(pos_r, spread_ret_r, y)

train, test = oos_split(ry.dropna().index, 0.7)
print("\n=== static vs rolling hedge ===")
print(f"static  gross={st_s['gross_sr']:.3f} net={st_s['net_sr']:.3f} NAV={st_s['nav']:.4f} turn={st_s['turn']:.4f} OOS={sharpe(net_s.reindex(test)):.3f}")
print(f"rolling gross={st_r['gross_sr']:.3f} net={st_r['net_sr']:.3f} NAV={st_r['nav']:.4f} turn={st_r['turn']:.4f} OOS={sharpe(net_r.reindex(test)):.3f}")

# Shock scenario: jump beta at last 20% 
print("\n=== shock scenario (broken leg) ===")
print("If one leg gaps on idiosyncratic news, static hedge leaves residual beta; rolling adapts with lag=ROLL.")
print("scenario_note: after a structural break, expect a burst of stop-outs / widener before beta re-learns.")
print(f"demo: |beta_roll - beta_static| mean last 60 bars = {float((beta_roll - beta_static).iloc[-60:].abs().mean()):.4f}")

fig, axes = plt.subplots(3, 1, figsize=(9, 8), sharex=True)
axes[0].plot(spread_roll.index, spread_roll.values, label="rolling spread")
axes[0].set_title("Rolling residual spread")
axes[0].legend(); axes[0].grid(True, alpha=0.3)
axes[1].plot(z_r.index, z_r.values, label="z_roll")
axes[1].axhline(ENTRY, color="r", ls="--", alpha=0.5)
axes[1].axhline(-ENTRY, color="r", ls="--", alpha=0.5)
axes[1].legend(); axes[1].grid(True, alpha=0.3)
eq_s = (1 + net_s.fillna(0)).cumprod()
eq_r = (1 + net_r.fillna(0)).cumprod()
axes[2].plot(eq_s.index, eq_s.values, label="static_net")
axes[2].plot(eq_r.index, eq_r.values, label="rolling_net")
axes[2].set_title("Pairs NAV net of 2-leg costs")
axes[2].legend(); axes[2].grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(PUBLIC / "pairs_nav.png", dpi=120)
print("\nchart", PUBLIC / "pairs_nav.png")
print("disclaimer: synthetic pair; learning only — quants.md W13/W14 show real open examples can print near-zero Sharpe")
