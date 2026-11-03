"""P0 lab: simple vs compound NAV; leverage toy P&L on synthetic returns.
Learning only — not investment advice.
"""
from __future__ import annotations

import pandas as pd

rets = pd.Series([0.01, -0.02, 0.015, 0.01, -0.005], name="r")
# Simple (arithmetic sum) vs compound
simple_nav = 1 + rets.cumsum()
compound_nav = (1 + rets).cumprod()
print("=== simple vs compound NAV ===")
print(pd.DataFrame({"r": rets, "simple_nav": simple_nav, "compound_nav": compound_nav}).round(6).to_string())

# Long vs 2x leverage on same returns (ignores financing — teaching toy)
lev = 2.0
lev_nav = (1 + lev * rets).cumprod()
print("\n=== leverage toy (2x, no financing) ===")
print(pd.DataFrame({"r": rets, "unlev_nav": compound_nav, "lev2_nav": lev_nav}).round(6).to_string())
print("final_unlev", round(float(compound_nav.iloc[-1]), 6))
print("final_lev2", round(float(lev_nav.iloc[-1]), 6))
