"""P3 lab: controlled comparison of three families vs simple baseline.
Learning only — not investment advice.

Same universe, costs, next-open convention. Complexity must beat dual-MA baseline OOS.
Critique open dumps (quants.md) as hypothesis sources only.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from _common import (
    ONE_WAY_BPS,
    PUBLIC,
    apply_costs,
    load_panel,
    nav,
    oos_split,
    sharpe,
)

df = load_panel()
aaa = df["AAA_adj"]
bbb = df["BBB_adj"].astype(float)
# pairs leg: cointegrated foil (same construction as 03)
rng = np.random.default_rng(7)
eps = np.zeros(len(bbb))
for i in range(1, len(bbb)):
    eps[i] = 0.85 * eps[i - 1] + rng.normal(0, 0.4)
yc = pd.Series(50.0 + 1.2 * bbb.values + eps, index=bbb.index)
r = aaa.pct_change()
rx = bbb.pct_change()
ryc = yc.pct_change()

MA_F, MA_S = 10, 30
LB, SKIP = 60, 5
Z_LB, ENTRY_Z, EXIT_Z = 20, -2.0, 0.0
ROLL, P_ENTRY, P_EXIT = 40, 2.0, 0.5

print("=== controlled comparison parameters ===")
print("universe: AAA for single-name; Y_coin/BBB for pairs; fill=next-open via shift(1); Rf=0")
print("costs: one-way stack", ONE_WAY_BPS, "bps (+ √impact for single-name); pairs 2× stack")
print("OOS: last 30% bars")
print("baseline: dual_MA", MA_F, MA_S)
print("cite: JoinQuant research ethos — same interrogation for every strategy")
print("cite: quants.md open library (read 2026-11-04) — many cards print Sharpe≤0; use as foils not proof")

# 1 baseline dual MA
dual = (aaa.rolling(MA_F).mean() > aaa.rolling(MA_S).mean()).astype(float).shift(1)
net_dual, _, st_dual = apply_costs(dual, r, aaa)

# 2 TS mom skip
past = aaa.shift(SKIP) / aaa.shift(SKIP + LB) - 1.0
mom = (past > 0).astype(float).shift(1)
net_mom, _, st_mom = apply_costs(mom, r, aaa)

# 3 MR z
mu = aaa.rolling(Z_LB).mean()
sd = aaa.rolling(Z_LB).std(ddof=1)
z = (aaa - mu) / sd
raw = pd.Series(0.0, index=aaa.index)
state = 0.0
for i in range(len(aaa)):
    zi = z.iloc[i]
    if np.isnan(zi):
        continue
    if state == 0 and zi < ENTRY_Z:
        state = 1.0
    elif state == 1 and zi >= EXIT_Z:
        state = 0.0
    raw.iloc[i] = state
mr = raw.shift(1)
net_mr, _, st_mr = apply_costs(mr, r, aaa)

# 4 pairs rolling (optional fourth — report three main + baseline)
def roll_beta(yy, xx, w):
    out = pd.Series(np.nan, index=yy.index)
    for i in range(w, len(yy)):
        ys = yy.iloc[i - w : i].values
        xs = xx.iloc[i - w : i].values
        X = np.column_stack([np.ones(w), xs])
        coef, *_ = np.linalg.lstsq(X, ys, rcond=None)
        out.iloc[i] = coef[1]
    return out

beta = roll_beta(yc, bbb, ROLL)
spread = yc - beta * bbb
zs = (spread - spread.rolling(Z_LB).mean()) / spread.rolling(Z_LB).std(ddof=1)
pos = pd.Series(0.0, index=yc.index)
state = 0.0
for i in range(len(aaa)):
    zi = zs.iloc[i]
    if np.isnan(zi):
        continue
    if state == 0:
        if zi > P_ENTRY:
            state = -1.0
        elif zi < -P_ENTRY:
            state = 1.0
    elif abs(zi) < P_EXIT:
        state = 0.0
    pos.iloc[i] = state
pos = pos.shift(1)
spread_ret = ryc - beta.shift(1).bfill() * rx
turn = pos.diff().abs().fillna(pos.abs())
net_pairs = pos * spread_ret - turn * (2 * ONE_WAY_BPS / 1e4)

train, test = oos_split(r.dropna().index, 0.7)

rows = []
for name, net, st in [
    ("baseline_dual_MA", net_dual, st_dual),
    ("ts_momentum_skip", net_mom, st_mom),
    ("mean_reversion_z", net_mr, st_mr),
    ("pairs_rolling", net_pairs, {
        "gross_sharpe": sharpe(pos * spread_ret),
        "net_sharpe": sharpe(net_pairs),
        "net_nav": nav(net_pairs),
        "mean_turnover": float(turn.mean()),
        "net_maxdd": float(((1+net_pairs.fillna(0)).cumprod() / (1+net_pairs.fillna(0)).cumprod().cummax() - 1).min()),
    }),
]:
    oos = sharpe(net.reindex(test))
    rows.append({
        "strategy": name,
        "IS_net_SR": sharpe(net.reindex(train)),
        "OOS_net_SR": oos,
        "net_NAV": st["net_nav"] if "net_nav" in st else nav(net),
        "turnover": st.get("mean_turnover", float("nan")),
        "maxDD": st.get("net_maxdd", float("nan")),
        "beats_baseline_OOS": oos > sharpe(net_dual.reindex(test)),
    })

tab = pd.DataFrame(rows)
print("\n=== comparison table (net of costs) ===")
print(tab.to_string(index=False, float_format=lambda v: f"{v:.4f}"))

base_oos = float(tab.loc[tab.strategy == "baseline_dual_MA", "OOS_net_SR"].iloc[0])
print("\n=== judgment ===")
print(f"baseline_OOS_net_SR={base_oos:.4f}")
winners = tab.loc[tab.strategy != "baseline_dual_MA"]
any_beat = bool(winners["beats_baseline_OOS"].any())
print(f"any_complex_beats_baseline_OOS={any_beat}")
print("rule: if no — keep the simple baseline; complexity needs OOS proof under identical assumptions")
print("hidden_assumptions_controlled: universe, costs, shift(1), Rf, OOS cut")
print("quants.md foil: open dashboards can show +CAGR with Sharpe≈0 or negative — headline Return ≠ edge")

fig, ax = plt.subplots(figsize=(9, 4.5))
for name, net in [
    ("baseline_dual_MA", net_dual),
    ("ts_momentum_skip", net_mom),
    ("mean_reversion_z", net_mr),
    ("pairs_rolling", net_pairs),
]:
    eq = (1 + net.fillna(0)).cumprod()
    ax.plot(eq.index, eq.values, label=name)
ax.axvline(test[0], color="k", ls=":", alpha=0.5, label="OOS start")
ax.set_title("P3 strategy compare (net of costs)")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(PUBLIC / "strategy_compare_nav.png", dpi=120)
print("\nchart", PUBLIC / "strategy_compare_nav.png")
print("disclaimer: synthetic panel; learning only — not a claim any strategy works live")
