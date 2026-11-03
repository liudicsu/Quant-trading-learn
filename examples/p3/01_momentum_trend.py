"""P3 lab: TS vs CS momentum (12-1 spirit on short panel), dual-MA, vol target, costs.
Learning only — not investment advice.

Classic: Jegadeesh & Titman (1993) J/K relative-strength; industry 12-1 skips recent month
to dampen short-term reversal. Stern syllabus: trend-following before counter-trend/pairs.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from _common import (
    ANN,
    PUBLIC,
    apply_costs,
    by_year_sharpe,
    load_panel,
    nav,
    oos_split,
    sharpe,
)

df = load_panel()
names = ["AAA_adj", "BBB_adj", "CCC_adj"]
px = df[names]
rets = px.pct_change()

# Stated parameters (scaled to ~1y panel; spirit of 12-1, not literal months)
LB_FULL = 60          # ~3 months formation stand-in for "12"
SKIP = 5              # skip recent bars (1-month spirit)
MA_FAST, MA_SLOW = 10, 30
VOL_LB = 20
VOL_TARGET = 0.10     # annualized
COST_NOTE = "P2 four-part stack 10 bps one-way + √impact × turnover"

print("=== parameters ===")
print("panel", df.index.min().date(), "→", df.index.max().date(), "n", len(df))
print("LB_FULL", LB_FULL, "SKIP", SKIP, "→ mom window ends at t-1-SKIP, starts t-1-SKIP-LB_FULL")
print("dual_MA", MA_FAST, MA_SLOW, "vol_target", VOL_TARGET, "vol_lb", VOL_LB)
print("costs:", COST_NOTE)
print("look-ahead: all positions use shift(1); mom uses only past returns")
print("cite: Jegadeesh & Titman 1993 JF relative-strength J/K; 12-1 = skip recent month (industry practice)")
print("cite: NYU Stern Dhar Trading Strategies syllabus — trend → counter-trend → pairs")

# --- Dual MA on AAA ---
aaa = px["AAA_adj"]
r_aaa = rets["AAA_adj"]
dual_sig = (aaa.rolling(MA_FAST).mean() > aaa.rolling(MA_SLOW).mean()).astype(float)
dual_pos = dual_sig.shift(1)
dual_net, dual_to, dual_st = apply_costs(dual_pos, r_aaa, aaa)

# --- TS momentum 12-1 spirit on AAA ---
# return from t-(SKIP+LB) to t-SKIP, known at close t → trade next open ≈ shift(1)
past = aaa.shift(SKIP) / aaa.shift(SKIP + LB_FULL) - 1.0
ts_sig = (past > 0).astype(float)
ts_pos = ts_sig.shift(1)
ts_net, ts_to, ts_st = apply_costs(ts_pos, r_aaa, aaa)

# no-skip foil (includes recent bars → short-term reversal contamination)
past_ns = aaa / aaa.shift(LB_FULL) - 1.0
ts_ns_pos = (past_ns > 0).astype(float).shift(1)
ts_ns_net, _, ts_ns_st = apply_costs(ts_ns_pos, r_aaa, aaa)

# --- Vol target 10% on TS mom ---
vol = r_aaa.rolling(VOL_LB).std(ddof=1) * ANN
scale = (VOL_TARGET / vol).clip(upper=2.0).fillna(0.0)
vt_pos = (ts_pos * scale.shift(1)).fillna(0.0)  # scale known prior bar
vt_net, vt_to, vt_st = apply_costs(vt_pos, r_aaa, aaa)

# --- Cross-sectional: long best / short worst of 3 by 12-1 spirit score ---
scores = {}
for c in names:
    scores[c] = px[c].shift(SKIP) / px[c].shift(SKIP + LB_FULL) - 1.0
S = pd.DataFrame(scores)
# equal-weight long top / short bottom; for 3 names: +1/2 on max, -1/2 on min, 0 mid
rank = S.rank(axis=1, method="first")
cs_w = pd.DataFrame(0.0, index=S.index, columns=S.columns)
cs_w = cs_w.mask(rank == 3.0, 0.5).mask(rank == 1.0, -0.5).fillna(0.0)
cs_w = cs_w.shift(1)  # next-bar
# portfolio daily return
cs_gross = (cs_w * rets).sum(axis=1)
# turnover = sum abs weight changes / 2 (one-way notionally) — use sum abs for cost
cs_to = cs_w.diff().abs().sum(axis=1).fillna(cs_w.abs().sum(axis=1))
bps = 10.0 / 1e4
cs_net = cs_gross - cs_to * bps  # simplified stack; no impact for multi-leg toy

# OOS
train_idx, test_idx = oos_split(r_aaa.dropna().index, 0.7)
print("\n=== dual-MA vs TS-mom (AAA, net of costs) ===")
for label, st, net, to in [
    ("dual_MA", dual_st, dual_net, dual_to),
    ("ts_mom_skip", ts_st, ts_net, ts_to),
    ("ts_mom_no_skip", ts_ns_st, ts_ns_net, None),
    ("ts_mom_vol_target", vt_st, vt_net, vt_to),
]:
    tr, te = net.reindex(train_idx), net.reindex(test_idx)
    print(
        f"{label:20s} gross_SR={st['gross_sharpe']:.3f} net_SR={st['net_sharpe']:.3f} "
        f"net_NAV={st['net_nav']:.4f} maxDD={st['net_maxdd']:.3f} "
        f"turn={st['mean_turnover']:.4f} OOS_net_SR={sharpe(te):.3f}"
    )

print("\n=== CS long/short (3-name toy) ===")
print(
    f"cs_net_SR={sharpe(cs_net):.3f} cs_NAV={nav(cs_net):.4f} "
    f"mean_turn={float(cs_to.mean()):.4f} OOS_net_SR={sharpe(cs_net.reindex(test_idx)):.3f}"
)
print("teach: with 3 synthetic names CS is a toy — real CS needs a broad universe")

print("\n=== by-year net Sharpe (TS mom skip) ===")
by = by_year_sharpe(ts_net)
print(by.to_string())
print("mean_by_year", float(by.mean()))

print("\n=== skip vs no-skip (must-teach) ===")
print(
    f"skip_net_SR={ts_st['net_sharpe']:.3f} no_skip_net_SR={ts_ns_st['net_sharpe']:.3f} "
    f"delta={ts_st['net_sharpe']-ts_ns_st['net_sharpe']:.3f}"
)
print("note: on THIS short synthetic panel no-skip can win — that does not refute the JT/industry motive:")
print("  JT 1993 skip-a-week variants avoid bid-ask/short-term reversal; 12-1 skips recent month for the same reason.")
print("  Expected-value framing: skip is a bias-reduction design choice, not a guarantee on every sample.")
print("crowding/turnover: higher turnover erodes edge — compare dual turn vs ts turn above")

# Chart
fig, ax = plt.subplots(figsize=(9, 4.5))
for label, net in [
    ("dual_MA_net", dual_net),
    ("ts_mom_skip_net", ts_net),
    ("ts_mom_vol_target_net", vt_net),
]:
    eq = (1 + net.fillna(0)).cumprod()
    ax.plot(eq.index, eq.values, label=label)
ax.set_title("P3 momentum: dual-MA vs TS mom (±vol target), net of costs")
ax.legend()
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(PUBLIC / "momentum_nav.png", dpi=120)
print("\nchart", PUBLIC / "momentum_nav.png")
print("disclaimer: synthetic panel; learning only — not live performance claims")
