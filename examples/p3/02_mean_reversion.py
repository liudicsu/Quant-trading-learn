"""P3 lab: z-score mean reversion + stop A/B + trend-regime failure.
Learning only — not investment advice.

Stern syllabus places counter-trend after trend. Chan-style MR: fade extremes, cut losers.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from _common import PUBLIC, apply_costs, load_panel, nav, oos_split, sharpe

df = load_panel()
px = df["AAA_adj"]
r = px.pct_change()

Z_LB = 20
ENTRY_Z = -2.0
EXIT_Z = 0.0          # mean re-touch
STOP_PCT = 0.03       # 3% adverse from entry
TREND_MA = 50

print("=== parameters ===")
print("z_lb", Z_LB, "enter z<", ENTRY_Z, "exit z>=", EXIT_Z, "stop", STOP_PCT)
print("trend filter MA", TREND_MA, "(price>MA = trend regime for failure demo)")
print("look-ahead: z uses rolling past; positions shift(1); stop uses same-bar low proxy = min(open,close) with open=prev close")
print("cite: Stern Dhar syllabus session on counter-trend; Canvas m7 MR template")

mu = px.rolling(Z_LB).mean()
sd = px.rolling(Z_LB).std(ddof=1)
z = (px - mu) / sd

# Vectorized long-only MR without stop: enter when z<ENTRY, flat when z>=EXIT
raw = pd.Series(0.0, index=px.index)
state = 0.0
for t in range(len(px)):
    zt = z.iloc[t]
    if np.isnan(zt):
        raw.iloc[t] = 0.0
        continue
    if state == 0.0 and zt < ENTRY_Z:
        state = 1.0
    elif state == 1.0 and zt >= EXIT_Z:
        state = 0.0
    raw.iloc[t] = state
pos = raw.shift(1)

# With stop: path-dependent using open=prev close, stop if open or close breaches entry*(1-STOP)
pos_stop = pd.Series(0.0, index=px.index)
state = 0.0
entry_px = np.nan
stop_exits = 0
opens = px.shift(1)  # next-open fill proxy
for t in range(len(px)):
    zt = z.iloc[t]
    o = opens.iloc[t]
    c = px.iloc[t]
    if np.isnan(zt) or np.isnan(o):
        pos_stop.iloc[t] = 0.0
        continue
    # manage existing
    if state == 1.0:
        stop_lvl = entry_px * (1 - STOP_PCT)
        # stop can trigger on open or during bar (min)
        if min(o, c) <= stop_lvl:
            state = 0.0
            stop_exits += 1
            pos_stop.iloc[t] = 0.0
            continue
        if zt >= EXIT_Z:
            state = 0.0
            pos_stop.iloc[t] = 0.0
            continue
        pos_stop.iloc[t] = 1.0
    else:
        if zt < ENTRY_Z:
            state = 1.0
            entry_px = o  # fill next open after signal — approximate: signal at t, fill open t+1 handled by storing intent
            # For simplicity aligned with shift: signal today → hold tomorrow. Entry price = tomorrow's open ≈ today's close for flat-open world.
            entry_px = c
            pos_stop.iloc[t] = 0.0  # enter next bar
            # mark next bar: use state so next iteration holds
        else:
            pos_stop.iloc[t] = 0.0

# Fix: after entry signal at t, position should be 1 from t+1 until exit.
# Rebuild stop path cleanly with explicit next-bar entry
pos_stop = pd.Series(0.0, index=px.index)
pending_entry = False
in_pos = False
entry_px = np.nan
stop_exits = 0
for t in range(len(px)):
    zt = z.iloc[t]
    c = px.iloc[t]
    o = opens.iloc[t]
    if pending_entry and not np.isnan(o):
        in_pos = True
        entry_px = o
        pending_entry = False
    if in_pos:
        stop_lvl = entry_px * (1 - STOP_PCT)
        hit_stop = (not np.isnan(o) and min(o, c) <= stop_lvl)
        hit_exit = (not np.isnan(zt) and zt >= EXIT_Z)
        if hit_stop:
            in_pos = False
            stop_exits += 1
            pos_stop.iloc[t] = 0.0
        elif hit_exit:
            in_pos = False
            pos_stop.iloc[t] = 0.0
        else:
            pos_stop.iloc[t] = 1.0
    else:
        pos_stop.iloc[t] = 0.0
        if not np.isnan(zt) and zt < ENTRY_Z:
            pending_entry = True

net_a, to_a, st_a = apply_costs(pos, r, px)
net_b, to_b, st_b = apply_costs(pos_stop, r, px)

# Synthetic strong-trend foil: overlay +0.15%/day drift on a copy and re-run MR+stop
drift = 0.0015
px_tr = px * (1 + drift) ** np.arange(len(px))
# rebuild z on trending series
mu_t = px_tr.rolling(Z_LB).mean()
sd_t = px_tr.rolling(Z_LB).std(ddof=1)
z_t = (px_tr - mu_t) / sd_t
r_tr = px_tr.pct_change()
opens_t = px_tr.shift(1)
pos_tr = pd.Series(0.0, index=px_tr.index)
pending = False
in_pos = False
entry_px = np.nan
stops_tr = 0
for t_i in range(len(px_tr)):
    zt = z_t.iloc[t_i]
    c = px_tr.iloc[t_i]
    o = opens_t.iloc[t_i]
    if pending and not np.isnan(o):
        in_pos = True
        entry_px = o
        pending = False
    if in_pos:
        stop_lvl = entry_px * (1 - STOP_PCT)
        hit_stop = (not np.isnan(o) and min(o, c) <= stop_lvl)
        hit_exit = (not np.isnan(zt) and zt >= EXIT_Z)
        if hit_stop:
            in_pos = False
            stops_tr += 1
            pos_tr.iloc[t_i] = 0.0
        elif hit_exit:
            in_pos = False
            pos_tr.iloc[t_i] = 0.0
        else:
            pos_tr.iloc[t_i] = 1.0
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
print("teach: in a persistent uptrend, long-only fade-the-dip keeps stopping out — stops rise, edge dies")
print("invalidation_list:")
print(" 1) repeated stops in a one-way trend (see drift foil)")
print(" 2) z thresholds estimated on full sample (must re-estimate OOS / rolling)")
print(" 3) gap through stop (open<<stop) — vector close path understates")
print(" 4) cost+turnover after whipsaw")
print(" 5) structural break: window mean no longer mean-reverting")

# Re-estimate demo: thresholds from train only
z_train = z.reindex(train).dropna()
entry_re = float(z_train.quantile(0.05))
exit_re = float(z_train.quantile(0.50))
print("\n=== threshold re-estimate (train quantiles) ===")
print(f"train_entry_q05={entry_re:.3f} train_exit_q50={exit_re:.3f} (vs fixed {ENTRY_Z}/{EXIT_Z})")
print("teach: fixed textbook ±2 is a starting foil — re-estimate on train, freeze for test")

fig, axes = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
axes[0].plot(z.index, z.values, label="z")
axes[0].axhline(ENTRY_Z, color="r", ls="--", alpha=0.6)
axes[0].axhline(EXIT_Z, color="g", ls="--", alpha=0.6)
axes[0].set_title("MR z-score")
axes[0].legend(); axes[0].grid(True, alpha=0.3)
eq_a = (1 + net_a.fillna(0)).cumprod()
eq_b = (1 + net_b.fillna(0)).cumprod()
axes[1].plot(eq_a.index, eq_a.values, label="no_stop_net")
axes[1].plot(eq_b.index, eq_b.values, label="with_stop_net")
axes[1].set_title("MR NAV net of costs")
axes[1].legend(); axes[1].grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(PUBLIC / "mean_reversion_nav.png", dpi=120)
print("\nchart", PUBLIC / "mean_reversion_nav.png")
print("disclaimer: synthetic; learning only")
