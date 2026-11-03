"""P2 lab: vectorized fill-timing assumptions; event-loop sketch; isomorphic-engine note.
Learning only — not investment advice.
NautilusTrader docs: Backtest/Sandbox/Live share a common kernel (research↔live parity concept).
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import numpy as np

DATA = Path(__file__).resolve().parent / "data" / "panel_toy.csv"
df = pd.read_csv(DATA, parse_dates=["date"]).set_index("date").sort_index()
# Build open = prior close (same as P1) PLUS a gappy open series for contrast
close = df["AAA_adj"]
open_flat = close.shift(1).fillna(close.iloc[0])
rng = np.random.default_rng(4)
gap = rng.normal(0, 0.002, len(close))
open_gap = open_flat * (1 + gap)

ret_cc = close.pct_change()
ret_oc = close / open_gap - 1
sig = (close > close.rolling(10).mean()).astype(int)
# Vectorized defaults often look like close decision → close-to-close (optimistic if same bar)
pos_opt = sig  # same-bar vectorized default risk
pos_hon = sig.shift(1)
pnl_opt = pos_opt * ret_cc
pnl_next_open = sig * ret_oc.shift(-1)  # signal at t, earn open[t+1]→close[t+1]

def nav(x):
    return float((1 + x.fillna(0)).cumprod().iloc[-1])

print("=== parameters ===")
print("n", len(close), "MA=10", "gap_seed=4", "Rf=0")
print("\n=== same signal, two fill timings (vectorized) ===")
print("nav_vectorized_same_bar_cc", round(nav(pnl_opt), 6))
print("nav_next_open_fill", round(nav(pnl_next_open), 6))
print("nav_honest_shift1_cc", round(nav(pos_hon * ret_cc), 6))
print("vectorized_default_risk: same-bar close fills silently inflate results unless you shift.")

print("\n=== event-loop sketch (initialize / handle_data) ===")
print("initialize: set calendar, commission model, universe, warm-up bars")
print("handle_data(bar): read as-of data only → emit orders → engine fills on next event")
print("teach: engine choice = fill + calendar assumptions, not just 'library brand'.")

print("\n=== assumptions paragraph (machine-printed) ===")
print(
    "ASSUMPTIONS: daily bars; signal from adjusted close; honest research uses shift(1) or next-open fills; "
    "costs applied as bps×turnover; no short locate; timezone=naive dates; freeze params before hold-out."
)
print(
    "isomorphic_note: NautilusTrader documents Backtest/Sandbox/Live sharing one kernel — "
    "same code path reduces research≠live gaps (concept; see nautilustrader.io architecture docs)."
)
print("ASSERTS_OK")
