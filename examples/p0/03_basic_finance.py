"""P0 lab: spot/futures/ETF toys, long/short P&L, margin/liquidation, NAV, tracking error.
Learning only — not investment advice.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

print("=== spot / futures / ETF numeric toys ===")
# Spot: buy 10 shares at 50, sell at 51
spot_shares, spot_entry, spot_exit = 10, 50.0, 51.0
spot_pnl = spot_shares * (spot_exit - spot_entry)
print("spot_long_pnl", spot_pnl)  # +10

# Futures: 1 contract, multiplier 50, entry 4000 → exit 4010 (long)
fut_mult, fut_entry, fut_exit = 50, 4000.0, 4010.0
fut_pnl = fut_mult * (fut_exit - fut_entry)
print("futures_long_pnl", fut_pnl)  # +500

# ETF: buy 20 shares at 100, exit 99 (tracks a basket; ignore NAV premium for toy)
etf_shares, etf_entry, etf_exit = 20, 100.0, 99.0
etf_pnl = etf_shares * (etf_exit - etf_entry)
print("etf_long_pnl", etf_pnl)  # -20

print("\n=== long vs short P&L at ±2% ===")
px0 = 100.0
notional = 100.0  # 1 share teaching unit
for move, label in [(0.02, "+2%"), (-0.02, "-2%")]:
    px1 = px0 * (1 + move)
    long_pnl = notional * (px1 / px0 - 1)
    short_pnl = notional * (px0 / px1 - 1) * (px1 / px0)  # clearer: short earns -(price change)
    short_pnl = -1.0 * (px1 - px0)  # short 1 unit
    print(f"move {label}: long_pnl={long_pnl:.2f} short_pnl={short_pnl:.2f}")

print("\n=== margin & liquidation toy ===")
# Long 1 futures-like position: contract value 100_000, initial margin 10%, maintenance 7%
contract_value = 100_000.0
initial_margin = 0.10 * contract_value  # 10_000
maint_margin = 0.07 * contract_value  # 7_000
# Equity ≈ initial_margin + P&L; liquidation when equity < maint
# P&L = contract_value * (px1/px0 - 1) for a 1x notional toy
# equity = initial_margin + contract_value * (px1/px0 - 1)
# set equity = maint_margin → px1/px0 - 1 = (maint - initial) / contract_value
ret_trigger = (maint_margin - initial_margin) / contract_value
liq_price_ratio = 1 + ret_trigger
print("initial_margin", initial_margin)
print("maintenance_margin", round(maint_margin, 2))
print("liquidation_return_trigger", round(ret_trigger, 6))
print("liquidation_price_ratio_vs_entry", round(liq_price_ratio, 6))
print("if_entry_price_4000_liq_price", round(4000 * liq_price_ratio, 4))

print("\n=== simple vs compound NAV ===")
rets = pd.Series([0.01, -0.02, 0.015, 0.01, -0.005], name="r")
simple_nav = 1 + rets.cumsum()
compound_nav = (1 + rets).cumprod()
print(pd.DataFrame({"r": rets, "simple_nav": simple_nav, "compound_nav": compound_nav}).round(6).to_string())
lev = 2.0
lev_nav = (1 + lev * rets).cumprod()
print("\n=== leverage toy (2x, no financing) ===")
print(pd.DataFrame({"r": rets, "unlev_nav": compound_nav, "lev2_nav": lev_nav}).round(6).to_string())
print("final_unlev", round(float(compound_nav.iloc[-1]), 6))
print("final_lev2", round(float(lev_nav.iloc[-1]), 6))

print("\n=== benchmark & tracking error ===")
rng = np.random.default_rng(7)
n = 63
bench = pd.Series(rng.normal(0.0003, 0.01, n), name="bench")
# portfolio = bench + small residual + tiny bias
port = bench + pd.Series(rng.normal(0.00005, 0.002, n), name="port")
active = port - bench
te_daily = float(active.std(ddof=1))
te_ann = te_daily * np.sqrt(252)
print("active_mean", round(float(active.mean()), 6))
print("tracking_error_daily", round(te_daily, 6))
print("tracking_error_ann", round(te_ann, 6))
print("te_note: annualized TE is std(port - bench)*sqrt(252); lower means tighter benchmark tracking.")
