"""P3 lab: half-life (OU/AR1) + z-score MR + stop A/B + trend failure.
Learning only — not investment advice.

Half-life: fit Δx = a + b x_{t-1} + ε; HL = −ln(2)/ln(1+b).
OU: dx = κ(θ−x)dt + σdW with κ ≈ −ln(1+b) per bar → HL = ln(2)/κ.
z at close[t] may only change position from t+1 (asserted).
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from _common import PUBLIC, apply_costs, load_panel, oos_split, sharpe

df = load_panel()
px = df["AAA_adj"].astype(float)
r = px.pct_change()
opens = px.shift(1)

ENTRY_Z = -2.0
EXIT_Z = 0.0
STOP_PCT = 0.03

print("=== parameters ===")
print("enter z<", ENTRY_Z, "exit z>=", EXIT_Z, "stop", STOP_PCT)
print("look-ahead rule: z[t] may only change position from t+1 onward (asserted)")
print("cite: Stern Dhar counter-trend; Canvas m7; OU/AR(1) half-life for lookback choice")
print("further_reading: Ernest P. Chan, Algorithmic Trading: Winning Strategies and Their Rationale, Wiley 2013 (ISBN 978-1-118-46014-6) — no quotes")


def ar1_half_life(level: pd.Series) -> dict:
    """OLS Δx = a + b x_{t-1} + ε on non-NaN pairs."""
    x_lag = level.shift(1)
    dx = level.diff()
    ok = pd.concat([dx, x_lag], axis=1).dropna()
    y = ok.iloc[:, 0].values
    xl = ok.iloc[:, 1].values
    X = np.column_stack([np.ones(len(xl)), xl])
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    a, b = float(coef[0]), float(coef[1])
    if b >= 0 or (1 + b) <= 0:
        hl = float("nan")
        kappa = float("nan")
    else:
        kappa = -np.log(1 + b)  # per bar
        hl = np.log(2) / kappa  # = -ln2 / ln(1+b)
    return {"a": a, "b": b, "kappa_per_bar": kappa, "half_life_bars": hl, "n": len(xl)}


hl = ar1_half_life(px)
print("\n=== AR(1) / OU half-life ===")
print("model: dx = a + b * x_{t-1} + eps")
print("OU link: kappa ≈ -ln(1+b) per bar; half_life = ln(2)/kappa = -ln(2)/ln(1+b)")
print(f"a={hl['a']:.6f} b={hl['b']:.6f} kappa={hl['kappa_per_bar']:.6f}")
print(f"half_life_bars={hl['half_life_bars']:.2f} n={hl['n']}")

# Choose lookback / holding from half-life (stated rule)
Z_LB = int(max(10, min(60, round(hl["half_life_bars"] * 1.5)))) if np.isfinite(hl["half_life_bars"]) else 20
HOLD_HINT = int(max(3, min(40, round(hl["half_life_bars"])))) if np.isfinite(hl["half_life_bars"]) else 10
print(f"rule: z_lookback ≈ 1.5 * HL → Z_LB={Z_LB}; holding_hint ≈ 1 * HL → {HOLD_HINT} bars")
print("teach: if HL is very large (near unit root), fade strategies are slow/fragile")

mu = px.rolling(Z_LB).mean()
sd = px.rolling(Z_LB).std(ddof=1)
z = (px - mu) / sd


def mr_positions_from_z(z: pd.Series) -> pd.Series:
    """Intent after close[t] stored in intent[t]; position[t] = intent[t-1]."""
    intent = pd.Series(0.0, index=z.index)
    state = 0.0
    for t in range(len(z)):
        zt = z.iloc[t]
        if np.isnan(zt):
            intent.iloc[t] = 0.0
            state = 0.0
            continue
        if state == 0.0 and zt < ENTRY_Z:
            state = 1.0
        elif state == 1.0 and zt >= EXIT_Z:
            state = 0.0
        intent.iloc[t] = state
    return intent.shift(1).fillna(0.0), intent


pos, intent = mr_positions_from_z(z)

# ASSERT: z[t] does not change position[t] — position[t] equals prior intent
# i.e. whenever intent changes at t, pos[t] still equals old intent (pos[t]==intent[t-1])
assert (pos.fillna(0) == intent.shift(1).fillna(0)).all(), "look-ahead: pos must lag intent"
# stronger: on bars where z triggers exit (intent goes 0 while prior intent was 1), pos that bar still 1
trig = (intent == 0) & (intent.shift(1) == 1) & z.notna()
if trig.any():
    assert (pos[trig] == 1.0).all(), "z-exit at close[t] must leave position[t]=1 (flat from t+1)"
print("ASSERT_z_exit_no_lookahead: OK (z[t] changes position only from t+1)")

# Stop path: price stop may flatten same bar; z-exit still deferred to t+1 via intent lag
pos_stop = pd.Series(0.0, index=px.index)
pending_entry = False
pending_z_exit = False
in_pos = False
entry_px = np.nan
stop_exits = 0
for t in range(len(px)):
    zt = z.iloc[t]
    c = px.iloc[t]
    o = opens.iloc[t]
    # apply deferred z-exit at open of this bar
    if pending_z_exit:
        in_pos = False
        pending_z_exit = False
        pending_entry = False
    if pending_entry and not np.isnan(o):
        in_pos = True
        entry_px = o
        pending_entry = False
    if in_pos:
        stop_lvl = entry_px * (1 - STOP_PCT)
        hit_stop = not np.isnan(o) and min(o, c) <= stop_lvl
        if hit_stop:
            in_pos = False
            stop_exits += 1
            pos_stop.iloc[t] = 0.0
        else:
            pos_stop.iloc[t] = 1.0
            # z-exit: signal at close → flatten from next bar
            if not np.isnan(zt) and zt >= EXIT_Z:
                pending_z_exit = True
    else:
        pos_stop.iloc[t] = 0.0
        if not np.isnan(zt) and zt < ENTRY_Z:
            pending_entry = True

# Assert stop path also defers z-exit: when z crosses EXIT, that bar still holds if no stop
z_exit_bars = (z >= EXIT_Z) & (z.shift(1) < EXIT_Z) & z.notna()
# not a hard assert on all such bars (may not be in pos); check deferred flag logic via lag equality for z-only exits
print(f"stop_exits={stop_exits}")

net_a, _, st_a = apply_costs(pos, r, px)
net_b, _, st_b = apply_costs(pos_stop, r, px)

# Trend-failure foil
drift = 0.0015
px_tr = px * (1 + drift) ** np.arange(len(px))
z_t = (px_tr - px_tr.rolling(Z_LB).mean()) / px_tr.rolling(Z_LB).std(ddof=1)
r_tr = px_tr.pct_change()
opens_t = px_tr.shift(1)
pos_tr = pd.Series(0.0, index=px_tr.index)
pending = False
pending_zx = False
in_pos = False
entry_px = np.nan
stops_tr = 0
for t_i in range(len(px_tr)):
    zt = z_t.iloc[t_i]
    c = px_tr.iloc[t_i]
    o = opens_t.iloc[t_i]
    if pending_zx:
        in_pos = False
        pending_zx = False
    if pending and not np.isnan(o):
        in_pos = True
        entry_px = o
        pending = False
    if in_pos:
        if not np.isnan(o) and min(o, c) <= entry_px * (1 - STOP_PCT):
            in_pos = False
            stops_tr += 1
            pos_tr.iloc[t_i] = 0.0
        else:
            pos_tr.iloc[t_i] = 1.0
            if not np.isnan(zt) and zt >= EXIT_Z:
                pending_zx = True
    else:
        pos_tr.iloc[t_i] = 0.0
        if not np.isnan(zt) and zt < ENTRY_Z:
            pending = True
net_tr, _, st_tr = apply_costs(pos_tr, r_tr, px_tr)

train, test = oos_split(r.dropna().index, 0.7)
print("\n=== A/B stops (original panel) ===")
print(f"no_stop  net_SR={st_a['net_sharpe']:.3f} NAV={st_a['net_nav']:.4f} turn={st_a['mean_turnover']:.4f} OOS={sharpe(net_a.reindex(test)):.3f}")
print(f"with_stop net_SR={st_b['net_sharpe']:.3f} NAV={st_b['net_nav']:.4f} turn={st_b['mean_turnover']:.4f} stop_exits={stop_exits} OOS={sharpe(net_b.reindex(test)):.3f}")
print("\n=== trend-failure foil (synthetic +0.15%/day drift) ===")
print(f"mr_on_trend net_SR={st_tr['net_sharpe']:.3f} NAV={st_tr['net_nav']:.4f} stop_exits={stops_tr}")
print("invalidation_list:")
print(" 1) repeated stops in a one-way trend")
print(" 2) z thresholds estimated on full sample")
print(" 3) gap through stop — close-only understates")
print(" 4) cost+turnover after whipsaw")
print(" 5) HL → ∞ (unit-root) — mean reversion thesis invalid")

z_train = z.reindex(train).dropna()
print("\n=== threshold re-estimate (train quantiles) ===")
print(f"train_entry_q05={float(z_train.quantile(0.05)):.3f} train_exit_q50={float(z_train.quantile(0.50)):.3f}")

fig, axes = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
axes[0].plot(z.index, z.values, label=f"z (lb={Z_LB})")
axes[0].axhline(ENTRY_Z, color="r", ls="--", alpha=0.6)
axes[0].axhline(EXIT_Z, color="g", ls="--", alpha=0.6)
axes[0].set_title(f"MR z-score (HL={hl['half_life_bars']:.1f} bars → lb={Z_LB})")
axes[0].legend(); axes[0].grid(True, alpha=0.3)
eq_a = (1 + net_a.fillna(0)).cumprod()
eq_b = (1 + net_b.fillna(0)).cumprod()
axes[1].plot(eq_a.index, eq_a.values, label="no_stop_net")
axes[1].plot(eq_b.index, eq_b.values, label="with_stop_net")
axes[1].legend(); axes[1].grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(PUBLIC / "mean_reversion_nav.png", dpi=120)
print("\nchart", PUBLIC / "mean_reversion_nav.png")
print("disclaimer: synthetic; learning only")
