"""P1 lab: mid, market-buy bps, close vs next-open fill timing, cost sheet.
Learning only — not investment advice.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

CSV = Path(__file__).resolve().parent / "data" / "synthetic_ohlc_ba.csv"
raw = pd.read_csv(CSV, parse_dates=["date"]).set_index("date").sort_index()

# Hand example (fixed quotes)
bid, ask = 99.90, 100.10
mid = (bid + ask) / 2
# Market buy assumed fill at ask
mkt_buy = ask
bps_vs_mid = (mkt_buy / mid - 1) * 10_000
print("=== hand mid & market-buy bps ===")
print("params: bid=99.90 ask=100.10; market buy fill=ask; bps vs mid")
print("mid", mid)
print("market_buy_fill", mkt_buy)
print("buy_cost_bps_vs_mid", round(bps_vs_mid, 4))
half_spread_bps = (ask / mid - 1) * 10_000
print("half_spread_bps", round(half_spread_bps, 4))
print("teach: mid=(bid+ask)/2; market buys lean ask (pay the spread).")

# On CSV: average half-spread
mid_s = (raw["bid"] + raw["ask"]) / 2
half_bps = (raw["ask"] / mid_s - 1) * 10_000
print("\n=== CSV half-spread stats (n=%d) ===" % len(raw))
print("mean_half_spread_bps", round(float(half_bps.mean()), 4))
print("median_half_spread_bps", round(float(half_bps.median()), 4))

# Fill timing: same-bar (LOOK-AHEAD) vs next-open / shift(1) honest
close = raw["close"]
sig = (close > close.rolling(5).mean()).astype(int)
r_cc = close.pct_change()
# Overnight gap then open→close on next day for "next open" narrative
r_next_open_to_close = (close.shift(-1) / raw["open"].shift(-1) - 1)

def nav_of(x: pd.Series) -> float:
    return float((1 + x.fillna(0)).cumprod().iloc[-1])

# LOOK-AHEAD / over-optimistic: use today's close in the signal and earn today's close-to-close
optimistic_same_bar = sig * r_cc
# Honest A: signal at close t, position starts next day (shift 1), earn close-to-close
honest_shift = sig.shift(1) * r_cc
# Honest B: signal at close t, fill next open, earn open[t+1]→close[t+1]
honest_next_open = sig * r_next_open_to_close

print("\n=== fill timing: same-bar vs honest ===")
print("params: signal=close>MA5; optimistic=same-bar (LOOK-AHEAD); honest_shift=signal.shift(1); honest_next_open=fill next open")
print("nav_optimistic_same_bar", round(nav_of(optimistic_same_bar), 6))
print("nav_honest_shift1", round(nav_of(honest_shift), 6))
print("nav_honest_next_open", round(nav_of(honest_next_open), 6))
print("lookahead_warning: same-bar zero-cost fills that reuse today's close in signal AND return are over-optimistic.")

print("\n=== cost assumption one-pager (toy numbers) ===")
print("venue: synthetic equity-like")
print("half_spread_bps_assumed", 10)
print("slippage_bps_per_trade", 5)
print("commission_bps", 1)
print("round_trip_bps", 10 + 5 + 1 + 10 + 5 + 1)  # pay half-spread each side + slip + commission both ways
print("impact_latency: intuition only — larger size → more impact; delay → mid moves against you. No HFT recipe.")
print("ASSERTS_OK")
