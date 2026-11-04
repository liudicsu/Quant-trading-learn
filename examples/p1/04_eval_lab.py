"""P1 lab: toy signal vs buy&hold; net-of-cost metrics; slippage bump; win-rate trap.
Learning only — not investment advice.
Parameters: n from CSV; cost_bps per one-way trade; Rf=0; ann=√252; MA window=10; seed N/A (deterministic CSV).
Win rate definition: fraction of ALL days in the pnl series with pnl > 0 (includes flat days as non-wins).
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
    # Win rate = share of ALL days with pnl > 0 (flat/zero days count as non-wins)
    wins = float((x > 0).mean())
    return {
        "name": name,
        "ann_ret": round(mu * 252, 4),
        "ann_vol": round(sd * float(ANN), 4),
        "sharpe_Rf0": round(sh, 4),
        "max_dd": round(mdd, 4),
        "win_rate_all_days": round(wins, 4),
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
print("win_rate_def: fraction of ALL days with pnl>0 (flat days are non-wins)")

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
w = rng.random(1000)
toy = np.where(w < 0.9, 0.01, -0.12)
print("\n=== win-rate trap (seed=3, n=1000) ===")
print("win_rate_all_days", round(float((toy > 0).mean()), 4))
print("mean_return", round(float(toy.mean()), 6))
print("note: win_rate≈0.9 but mean return negative — win rate ≠ good strategy.")

print("\n=== turnover ===")
print("mean_daily_turnover", round(float(turnover.mean()), 6))
print("approx_annual_one_way_turns", round(float(turnover.mean() * 252), 2))
print("teach: higher turnover amplifies costs; reporting gross-only is dishonest.")
print("ASSERTS_OK")

# --- PyFolio tear-sheet meaning (map to metrics you already compute) ---
print("\n=== PyFolio tear-sheet meaning (reuse existing metrics) ===")
print("cite: Quantopian pyfolio / pyfolio-reloaded — create_returns_tear_sheet(returns, benchmark_rets=...)")
print("params: same toy pnl at 5 bps; Rf=0; ann=√252")
pnl5 = apply_costs(pos, r, 5.0).dropna()
nav = (1 + pnl5.fillna(0)).cumprod()
peak = nav.cummax()
dd = nav / peak - 1
m = metrics(pnl5, "signal_5bps")
# Tear-sheet panel → already-known metric
mapping = [
    ("Annual return", m["ann_ret"], "mean(daily)×252"),
    ("Annual volatility", m["ann_vol"], "std(daily)×√252"),
    ("Sharpe ratio", m["sharpe_Rf0"], "(mean-Rf)/std×√252"),
    ("Max drawdown", m["max_dd"], "min(nav/peak-1)"),
    ("Cumulative return", round(float(nav.iloc[-1] - 1), 4), "final NAV - 1"),
    ("Daily VaR (5%)", round(float(pnl5.quantile(0.05)), 6), "empirical 5th pct of daily pnl"),
    ("Stability (R^2)", round(float(np.corrcoef(np.arange(len(nav)), np.log(nav.clip(lower=1e-12)))[0, 1] ** 2), 4), "R² of log-NAV vs time"),
]
print("tear_sheet_map (PyFolio-style label → value → how we already compute it)")
for lab, val, how in mapping:
    print(f"  {lab:20s} {val:+.6f}  via {how}")
print(
    "teach: a returns tear sheet is a dashboard of metrics you already met in returns-vol-corr / this lab — "
    "it does not create a new edge; read full sample vs OOS carefully and still apply cost honesty."
)
print("benchmark note: tear sheets often take benchmark_rets; compare excess return / beta only when the benchmark is investable and aligned.")
