"""P1 lab: CSV→returns→NAV; Alpha/Beta toy vs benchmark; friction checklist.
Learning only — not investment advice. Offline synthetic data.
Parameters: seed for beta toy = 11 (data CSV); Rf daily = 0; n from CSV.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

CSV = Path(__file__).resolve().parent / "data" / "synthetic_ohlc_ba.csv"
raw = pd.read_csv(CSV, parse_dates=["date"]).set_index("date").sort_index()
assert isinstance(raw.index, pd.DatetimeIndex)

close = raw["close"]
ret = close.pct_change()
nav = (1 + ret.fillna(0)).cumprod()
print("=== CSV→returns→NAV ===")
print("n_rows", len(raw))
print("params: Rf_daily=0; NAV starts at 1 on first row (ret filled 0 for day-1 only for NAV path)")
print(pd.DataFrame({"close": close, "ret": ret, "nav": nav}).head(5).round(6).to_string())
print("...")
print(pd.DataFrame({"close": close, "ret": ret, "nav": nav}).tail(3).round(6).to_string())
print("final_nav", round(float(nav.iloc[-1]), 6))

# Benchmark: synthetic market with known beta loading (teaching toy)
rng = np.random.default_rng(11)
# burn same length as CSV construction? Use independent market series aligned to index
n = len(ret.dropna())
r = ret.dropna()
# Market returns: independent draw then portfolio = alpha + beta*mkt + eps
mkt = pd.Series(rng.normal(0.0002, 0.01, len(r)), index=r.index, name="mkt")
true_alpha_d = 0.0001
true_beta = 1.2
eps = pd.Series(rng.normal(0, 0.005, len(r)), index=r.index)
# Rebuild a toy strategy return with known alpha/beta (not using price ret — explicit toy)
strat = true_alpha_d + true_beta * mkt + eps
# OLS: beta = cov(s,m)/var(m); alpha = mean(s) - beta*mean(m)
var_m = float(mkt.var(ddof=1))
beta_hat = float(strat.cov(mkt) / var_m)
alpha_hat_d = float(strat.mean() - beta_hat * mkt.mean())
alpha_ann = alpha_hat_d * 252
print("\n=== Alpha/Beta toy (known DGP) ===")
print("params: true_alpha_daily=0.0001 true_beta=1.2 n=", len(r), "seed=11 Rf=0")
print("beta_hat", round(beta_hat, 4))
print("alpha_hat_daily", round(alpha_hat_d, 6))
print("alpha_hat_ann_252x", round(alpha_ann, 4))
print("note: Alpha = residual mean after beta×benchmark; Beta = co-movement with benchmark.")
print("lookahead_flag: none — OLS uses contemporaneous aligned returns only; do not shift(-1) prices into signals.")

frictions = [
    "bid-ask spread",
    "commissions / fees",
    "slippage / market impact",
    "borrow / financing costs",
    "latency / delayed fills",
    "taxes / stamp duties (venue-dependent)",
]
print("\n=== friction checklist (≥5) ===")
for i, f in enumerate(frictions, 1):
    print(f"{i}. {f}")

print("\n=== three-sentence research goal (template filled) ===")
print(
    "GOAL: On synthetic daily equity-like closes (n=252), test whether a pre-registered "
    "rule improves constrained risk-adjusted performance vs a buy-and-hold benchmark after costs."
)
print(
    "CONSTRAINTS: Max 100% gross exposure; declare Rf=0 and √252 annualization; no look-ahead fills."
)
print(
    "SUCCESS: Net Sharpe and max drawdown above the benchmark on a frozen hold-out block — reproducible from seed+CSV."
)
print("ASSERTS_OK")
