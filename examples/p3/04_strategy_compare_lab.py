"""P3 lab: controlled comparison + trial count N + DSR (link to P2 traps).
Learning only — not investment advice.

One cost model for ALL strategies (bps stack + √impact; pairs n_legs=2).
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
    deflated_sharpe,
    load_panel,
    nav,
    oos_split,
    sharpe,
)

df = load_panel()
aaa = df["AAA_adj"].astype(float)
bbb = df["BBB_adj"].astype(float)
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

# Explicit trial count: the strategies we actually ran in this horse race
STRATEGIES = ["baseline_dual_MA", "ts_momentum_skip", "mean_reversion_z", "pairs_rolling"]
N_TRIALS = len(STRATEGIES)

print("=== controlled comparison parameters ===")
print("universe: AAA single-name; Y_coin/BBB pairs foil; fill=shift(1); Rf=0")
print("ONE cost model: one_way_bps", ONE_WAY_BPS, "+ √impact×turnover; pairs n_legs=2")
print("OOS: last 30%; baseline dual_MA", MA_F, MA_S)
print(f"trial_count N={N_TRIALS} strategies in this lab (explicit — feeds DSR)")
print("cite: P2 backtest-traps Bailey–LdP DSR; same-protocol backtest interrogation discipline")
print("cite: quants.md as hypothesis foil only")
print("further_reading: Ernest P. Chan, Algorithmic Trading..., Wiley 2013 — no quotes")

dual = (aaa.rolling(MA_F).mean() > aaa.rolling(MA_S).mean()).astype(float).shift(1)
net_dual, _, st_dual = apply_costs(dual, r, aaa, n_legs=1)

past = aaa.shift(SKIP) / aaa.shift(SKIP + LB) - 1.0
mom = (past > 0).astype(float).shift(1)
net_mom, _, st_mom = apply_costs(mom, r, aaa, n_legs=1)

mu = aaa.rolling(Z_LB).mean()
sd = aaa.rolling(Z_LB).std(ddof=1)
z = (aaa - mu) / sd
intent = pd.Series(0.0, index=aaa.index)
state = 0.0
for i in range(len(aaa)):
    zi = z.iloc[i]
    if np.isnan(zi):
        continue
    if state == 0 and zi < ENTRY_Z:
        state = 1.0
    elif state == 1 and zi >= EXIT_Z:
        state = 0.0
    intent.iloc[i] = state
mr = intent.shift(1).fillna(0.0)
net_mr, _, st_mr = apply_costs(mr, r, aaa, n_legs=1)


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
intent_p = pd.Series(0.0, index=yc.index)
state = 0.0
for i in range(len(yc)):
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
    intent_p.iloc[i] = state
pos = intent_p.shift(1).fillna(0.0)
spread_ret = ryc - beta.shift(1).bfill() * rx
px_ref = (yc + bbb) / 2.0
net_pairs, _, st_pairs = apply_costs(pos, spread_ret, px_ref, n_legs=2)

train, test = oos_split(r.dropna().index, 0.7)

bundle = [
    ("baseline_dual_MA", net_dual, st_dual),
    ("ts_momentum_skip", net_mom, st_mom),
    ("mean_reversion_z", net_mr, st_mr),
    ("pairs_rolling", net_pairs, st_pairs),
]

rows = []
for name, net, st in bundle:
    oos = sharpe(net.reindex(test))
    rows.append({
        "strategy": name,
        "IS_net_SR": sharpe(net.reindex(train)),
        "OOS_net_SR": oos,
        "net_NAV": st["net_nav"],
        "turnover": st["mean_turnover"],
        "maxDD": st["net_maxdd"],
        "n_legs": st["n_legs"],
        "beats_baseline_OOS": oos > sharpe(net_dual.reindex(test)),
    })
tab = pd.DataFrame(rows)
print("\n=== comparison table (ONE cost model; net of costs) ===")
print(tab.to_string(index=False, float_format=lambda v: f"{v:.4f}"))

# Best by OOS net SR among all N trials — DSR MUST use the SAME OOS series that made the choice
best_idx = int(tab["OOS_net_SR"].astype(float).fillna(-999).idxmax())
best_name = tab.loc[best_idx, "strategy"]
best_oos_sr_ann = float(tab.loc[best_idx, "OOS_net_SR"])
nets = {n: net for n, net, _ in bundle}
best_oos = nets[best_name].reindex(test).dropna()

# Cross-trial σ_SR from the N raw daily Sharpes on the SAME OOS window (not full sample)
raw_srs = []
for name, net, _ in bundle:
    x = net.reindex(test).dropna()
    s = x.std(ddof=1)
    raw_srs.append(float(x.mean() / s) if len(x) > 2 and s > 0 else float("nan"))
raw_srs = np.array(raw_srs, dtype=float)
sigma_sr = float(np.nanstd(raw_srs, ddof=1))
mu_sr = 0.0
dsr = deflated_sharpe(best_oos, n_trials=N_TRIALS, mu_sr=mu_sr, sigma_sr=max(sigma_sr, 1e-8))

# Assert: daily SR * sqrt(252) matches the table OOS annualized SR used for selection
from _common import ANN
sr_ann_from_daily = dsr["sr_daily"] * ANN
assert abs(sr_ann_from_daily - best_oos_sr_ann) < 1e-9, (
    f"DSR series mismatch: sr_daily*sqrt(252)={sr_ann_from_daily} vs table OOS_net_SR={best_oos_sr_ann}"
)
print("\n=== DSR on best OOS strategy (link P2 backtest-traps) ===")
print("rule: DSR uses the SAME OOS net-return series that produced OOS_net_SR / the choice — never mix full-sample PnL with an OOS ranking")
print(f"best_strategy={best_name}")
print(f"N_trials={N_TRIALS}")
print(f"OOS_raw_SR_trials={np.round(raw_srs, 6).tolist()} sigma_SR_OOS={sigma_sr:.6f}")
print(f"sr_daily={dsr['sr_daily']:.6f} sr_ann={dsr['sr_ann']:.4f} table_OOS_net_SR={best_oos_sr_ann:.4f}")
print(f"ASSERT_sr_daily_times_sqrt252_matches_table_OOS_SR: OK (diff={abs(sr_ann_from_daily-best_oos_sr_ann):.2e})")
print(f"SR_star_Emax={dsr['SR_star']:.6f} DSR={dsr['DSR']:.6f} n_obs_OOS={dsr['n_obs']}")
print("formula: DSR = PSR(SR̂, SR*=E[max SR under N trials], n, skew, kurt_Pearson) on OOS bars only")
print("teach: even the horse-race winner must clear a multiple-testing bar — see P2 DSR vs N")

base_oos = float(tab.loc[tab.strategy == "baseline_dual_MA", "OOS_net_SR"].iloc[0])
print("\n=== judgment ===")
print(f"baseline_OOS_net_SR={base_oos:.4f}")
print(f"any_complex_beats_baseline_OOS={bool(tab.loc[tab.strategy!='baseline_dual_MA','beats_baseline_OOS'].any())}")
print("rule: complexity needs OOS proof under identical cost/fill assumptions + survive DSR(N)")

fig, ax = plt.subplots(figsize=(9, 4.5))
for name, net, _ in bundle:
    eq = (1 + net.fillna(0)).cumprod()
    ax.plot(eq.index, eq.values, label=name)
ax.axvline(test[0], color="k", ls=":", alpha=0.5, label="OOS start")
ax.set_title(f"P3 compare (shared costs); best={best_name}; N={N_TRIALS}; DSR={dsr['DSR']:.3f}")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(PUBLIC / "strategy_compare_nav.png", dpi=120)
print("\nchart", PUBLIC / "strategy_compare_nav.png")
print("disclaimer: synthetic; learning only — not live claims")
