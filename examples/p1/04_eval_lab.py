"""P1 lab: toy signal vs buy&hold; net-of-cost metrics; slippage bump; win-rate trap.
Learning only — not investment advice.
Parameters: n from CSV; cost_bps per one-way trade; Rf=0; ann=√252; MA window=10; seed N/A (deterministic CSV).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

CSV = Path(__file__).resolve().parent / "data" / "synthetic_ohlc_ba.csv"
raw = pd.read_csv(CSV, parse_dates=["date"]).set_index("date").sort_index()
r = raw["close"].pct_change()
# Honest signal: MA cross using prior close only
ma = raw["close"].rolling(10).mean()
sig = (raw["close"] > ma).astype(int)
pos = sig.shift(1)  # no look-ahead
# Turnover: when position changes
turnover = pos.diff().abs().fillna(0)  # 0→1 or 1→0 counts as 1 one-way

ANN = np.sqrt(252)
RF = 0.0


def metrics(pnl: pd.Series, name: str) -> dict:
    x = pnl.dropna()
    nav = (1 + x.fillna(0)).cumprod()
    peak = nav.cummax()
    mdd = float((nav / peak - 1).min())
    mu, sd = float(x.mean()), float(x.std(ddof=1))
    sh = float("nan") if sd == 0 else (mu - RF) / sd * float(ANN)
    # Win rate on days with nonzero pnl contribution when in market — teaching definition:
    active = x[pos.reindex_like(x).fillna(0) != 0] if False else x
    wins = float((x > 0).mean())
    return {
        "name": name,
        "ann_ret": round(mu * 252, 4),
        "ann_vol": round(sd * float(ANN), 4),
        "sharpe_Rf0": round(sh, 4),
        "max_dd": round(mdd, 4),
        "win_rate": round(wins, 4),
        "final_nav": round(float(nav.iloc[-1]), 4),
    }


def apply_costs(pos: pd.Series, r: pd.Series, one_way_bps: float) -> pd.Series:
    turn = pos.diff().abs().fillna(pos.abs())  # first entry counts
    cost = turn * (one_way_bps / 10_000.0)
    gross = pos * r
    return gross - cost


print("=== parameters ===")
print("n", int(r.notna().sum()))
print("MA_window", 10)
print("position = signal.shift(1)  # anti look-ahead")
print("Rf_daily", RF, "ann_sqrt252", round(float(ANN), 6))
print("one_way_cost_bps_levels", [0, 5, 15])

bh = r.copy()
rows = []
rows.append(metrics(bh.dropna(), "buy_hold_gross"))
for bps in [0, 5, 15]:
    net = apply_costs(pos, r, bps)
    rows.append(metrics(net.dropna(), f"toy_MA10_net_{bps}bps"))

print("\n=== metric comparison table ===")
tab = pd.DataFrame(rows).set_index("name")
print(tab.to_string())

# Win rate trap: high win rate bad expectancy toy
rng = np.random.default_rng(3)
# 90% tiny wins, 10% large losses
w = rng.random(1000)
toy = np.where(w < 0.9, 0.01, -0.12)
print("\n=== win-rate trap (seed=3, n=1000) ===")
print("win_rate", round(float((toy > 0).mean()), 4))
print("mean_return", round(float(toy.mean()), 6))
print("note: win_rate=0.9 but mean return negative — win rate ≠ good strategy.")

# Multi-seed noise on costs? Optional: sweep random entry jitter — skip; report turnover instead
print("\n=== turnover ===")
print("mean_daily_turnover", round(float(turnover.mean()), 6))
print("approx_annual_one_way_turns", round(float(turnover.mean() * 252), 2))
print("teach: higher turnover amplifies costs; reporting gross-only is dishonest.")
print("ASSERTS_OK")
