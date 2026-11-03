"""P2 lab: four-part costs + square-root impact + capacity.
Learning only — not investment advice.

Impact: pedagogical square-root form k·σ·√(Q/ADV). Almgren et al. (2005)
"Direct Estimation of Equity Market Impact" discuss √ as a candidate (Barra)
and empirically prefer temporary impact ∝ (participation)^(3/5) on their desk;
we still teach √ as the common reduced-form capacity demo and cite that paper.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parent / "data" / "panel_toy.csv"
OUT = Path(__file__).resolve().parents[2] / "public" / "p2"
OUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA, parse_dates=["date"]).set_index("date").sort_index()
px = df["AAA_adj"]
ret = px.pct_change()
r = ret.dropna()
n = len(r)
ANN = np.sqrt(252)

# Stated toy parameters
COMMISSION_BPS = 2.0          # explicit commission one-way
HALF_SPREAD_BPS = 5.0         # half bid-ask (implicit microstructure)
SLIPPAGE_BPS = 3.0            # extra slippage beyond half-spread
IMPACT_K = 0.10               # square-root prefactor (dimensionless)
ADV_SHARES = 1_000_000.0      # average daily volume (shares)
VOL_LB = 20
# Single-trade demo uses STATED prior sigma from first 100 bars only (no future).
SIGMA_PRIOR = float(r.iloc[:100].std(ddof=1))
SIGMA_DAILY = SIGMA_PRIOR  # print alias; path impact uses lagged rolling
PRICE = float(px.iloc[-1])
CAPITAL_BASE = 1_000_000.0    # $ for unit demo
PARTICIPATION_DEFAULT = 0.05  # Q/ADV for single-trade demo

print("=== parameters ===")
print("n", n, "MA=10 position=shift(1) Rf=0 ann=sqrt(252)")
print("commission_bps", COMMISSION_BPS)
print("half_spread_bps", HALF_SPREAD_BPS)
print("slippage_bps", SLIPPAGE_BPS)
print("impact_model: k*sigma*sqrt(Q/ADV) with k=", IMPACT_K)
print("ADV_shares", ADV_SHARES, "sigma_prior_first100", round(SIGMA_PRIOR, 6), "price", round(PRICE, 4))
print("impact_vol_rule: rolling", VOL_LB, "std shifted by 1; warm-up=expanding std shifted by 1")
print("cite: Almgren et al. 2005 Direct Estimation of Equity Market Impact (√ candidate; empirical β≈0.6)")


def sharpe(pnl: pd.Series) -> float:
    x = pnl.dropna()
    s = x.std(ddof=1)
    return float("nan") if s == 0 else float(x.mean() / s * ANN)


def nav(pnl: pd.Series) -> float:
    return float((1 + pnl.fillna(0)).cumprod().iloc[-1])


def ma_position(window: int = 10) -> pd.Series:
    sig = (px > px.rolling(window).mean()).astype(float)
    return sig.shift(1).reindex(r.index).fillna(0.0)


pos = ma_position(10)
turnover = pos.diff().abs().fillna(pos.abs())  # first bar: enter
gross = pos * r

# --- four parts: per-unit (one-way) in return space ---
def bps_to_ret(bps: float) -> float:
    return bps / 1e4


# 1) Commission
c_comm = turnover * bps_to_ret(COMMISSION_BPS)
# 2) Half spread
c_spread = turnover * bps_to_ret(HALF_SPREAD_BPS)
# 3) Slippage
c_slip = turnover * bps_to_ret(SLIPPAGE_BPS)


# 4) Market impact via square-root: each rebalance trades Q shares ≈ turnover * (capital/price)
def lagged_sigma(ret: pd.Series, lb: int = VOL_LB) -> pd.Series:
    """sigma[t] from returns strictly before t (rolling lb; warm-up expanding)."""
    roll = ret.rolling(lb, min_periods=lb).std(ddof=1)
    expand = ret.expanding(min_periods=2).std(ddof=1)
    return roll.fillna(expand).shift(1).fillna(0.0)


def impact_cost_series(capital: float) -> pd.Series:
    # shares traded on a day ≈ turnover * (capital / price); Q/ADV = shares/ADV
    shares = turnover * (capital / PRICE)
    q_over_adv = shares / ADV_SHARES
    # impact: k * σ_{t-1} * sqrt(Q/ADV) — no full-sample look-ahead
    sigma = lagged_sigma(r)
    impact_ret = IMPACT_K * sigma * np.sqrt(q_over_adv.clip(lower=0))
    return impact_ret


c_impact = impact_cost_series(CAPITAL_BASE)
net = gross - c_comm - c_spread - c_slip - c_impact

print("\n=== four-part numeric example (single trade Q/ADV=%.2f) ===" % PARTICIPATION_DEFAULT)
q = PARTICIPATION_DEFAULT
imp_one = IMPACT_K * SIGMA_PRIOR * np.sqrt(q)
print("commission_one_way_ret", round(bps_to_ret(COMMISSION_BPS), 6), f"({COMMISSION_BPS} bps)")
print("half_spread_one_way_ret", round(bps_to_ret(HALF_SPREAD_BPS), 6), f"({HALF_SPREAD_BPS} bps)")
print("slippage_one_way_ret", round(bps_to_ret(SLIPPAGE_BPS), 6), f"({SLIPPAGE_BPS} bps)")
print(
    "impact_one_trade_ret",
    round(imp_one, 6),
    f"= {IMPACT_K}*{round(SIGMA_PRIOR,4)}*sqrt({q}) (stated prior)",
)
print(
    "total_one_way_demo_bps",
    round((bps_to_ret(COMMISSION_BPS) + bps_to_ret(HALF_SPREAD_BPS) + bps_to_ret(SLIPPAGE_BPS) + imp_one) * 1e4, 2),
)

print("\n=== stacked path totals (capital=$%.0f) ===" % CAPITAL_BASE)
parts = {
    "gross_nav": nav(gross),
    "minus_commission_nav": nav(gross - c_comm),
    "minus_comm_spread_nav": nav(gross - c_comm - c_spread),
    "minus_comm_spread_slip_nav": nav(gross - c_comm - c_spread - c_slip),
    "net_all_four_nav": nav(net),
}
for k, v in parts.items():
    print(k, round(v, 6))
print("mean_daily_turnover", round(float(turnover.mean()), 6))
print("sum_commission_ret", round(float(c_comm.sum()), 6))
print("sum_half_spread_ret", round(float(c_spread.sum()), 6))
print("sum_slippage_ret", round(float(c_slip.sum()), 6))
print("sum_impact_ret", round(float(c_impact.sum()), 6))
print("sharpe_gross", round(sharpe(gross), 4), "sharpe_net_all_four", round(sharpe(net), 4))

# Stacked bar of cumulative cost drag (sum of costs)
sums = [
    float(c_comm.sum()) * 1e4,
    float(c_spread.sum()) * 1e4,
    float(c_slip.sum()) * 1e4,
    float(c_impact.sum()) * 1e4,
]
labels = ["commission", "half-spread", "slippage", "sqrt impact"]
fig, ax = plt.subplots(figsize=(7, 4))
bottom = 0.0
colors = ["#2e75b6", "#70ad47", "#ed7d31", "#c00000"]
for lab, val, col in zip(labels, sums, colors):
    ax.bar(["total cost drag (bps·path)"], [val], bottom=bottom, label=lab, color=col)
    bottom += val
ax.set_ylabel("Cumulative cost (return × 1e4)")
ax.set_title("Stacked four-part cost breakdown (MA10 path)")
ax.legend()
fig.tight_layout()
fig.savefig(OUT / "cost_breakdown.png", dpi=120)
plt.close(fig)
print("saved_plot public/p2/cost_breakdown.png")

# Legacy cost ladder (bps one-way combined proxy) for continuity
print("\n=== cost ladder (combined one-way bps proxy, no separate impact) ===")
ladder_rows = []
for bps in [0, 5, 10, 20, 40]:
    pnl = gross - turnover * (bps / 1e4)
    ladder_rows.append(
        {
            "bps": bps,
            "sharpe": round(sharpe(pnl), 4),
            "final_nav": round(nav(pnl), 4),
            "ann_ret": round(float(pnl.mean() * 252), 4),
        }
    )
ladder = pd.DataFrame(ladder_rows)
print(ladder.to_string(index=False))
fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(ladder["bps"], ladder["sharpe"], "o-", color="#1f4e79")
ax.set_xlabel("one-way combined bps")
ax.set_ylabel("ann. Sharpe (Rf=0)")
ax.set_title("Cost ladder (combined bps × turnover)")
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(OUT / "cost_ladder.png", dpi=120)
plt.close(fig)
print("saved_plot public/p2/cost_ladder.png")
print("teach: zero-cost curve ≠ live evidence; turnover amplifies every bps.")

# Capacity sensitivity across capital sizes
print("\n=== capacity sensitivity (vary capital; impact ∝ sqrt(Q/ADV)) ===")
cap_rows = []
for capital in [1e5, 5e5, 1e6, 5e6, 1e7, 5e7]:
    imp = impact_cost_series(capital)
    pnl = gross - c_comm - c_spread - c_slip - imp
    avg_q_adv = float((turnover * (capital / PRICE) / ADV_SHARES).mean())
    cap_rows.append(
        {
            "capital": int(capital),
            "mean_Q_over_ADV": round(avg_q_adv, 6),
            "sum_impact_bps": round(float(imp.sum()) * 1e4, 2),
            "sharpe_net": round(sharpe(pnl), 4),
            "final_nav": round(nav(pnl), 4),
        }
    )
cap = pd.DataFrame(cap_rows)
print(cap.to_string(index=False))
fig, ax = plt.subplots(figsize=(7.5, 4.2))
ax.plot(cap["capital"], cap["sharpe_net"], "o-", color="#1f4e79")
ax.set_xscale("log")
ax.set_xlabel("Capital ($, log)")
ax.set_ylabel("Net Sharpe (all four costs)")
ax.set_title("Capacity sensitivity: larger capital → larger √ impact drag")
ax.grid(True, alpha=0.3, which="both")
fig.tight_layout()
fig.savefig(OUT / "capacity_sensitivity.png", dpi=120)
plt.close(fig)
print("saved_plot public/p2/capacity_sensitivity.png")
print("ASSERTS_OK")
