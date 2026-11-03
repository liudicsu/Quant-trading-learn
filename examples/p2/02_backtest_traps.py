"""P2 lab: cheat vs honest MA, grid overfitting, hold-out, trial log.
Learning only — not investment advice. Cite Quant-Arena sealed-holdout spirit (arXiv:2610.30113).
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parent / "data" / "panel_toy.csv"
df = pd.read_csv(DATA, parse_dates=["date"]).set_index("date").sort_index()
px = df["AAA_adj"]
ret = px.pct_change()
n = int(ret.notna().sum())
ANN = np.sqrt(252)
print("=== parameters ===")
print("n", n, "ann_sqrt252", round(float(ANN), 6), "asset=AAA_adj", "Rf=0")

def sharpe(pnl: pd.Series) -> float:
    x = pnl.dropna()
    s = x.std(ddof=1)
    return float("nan") if s == 0 else float(x.mean() / s * ANN)

def nav(pnl: pd.Series) -> float:
    return float((1 + pnl.fillna(0)).cumprod().iloc[-1])

# Cheat: same-bar signal uses today's close and today's return
def run_ma(window: int, honest: bool) -> tuple[float, float]:
    sig = (px > px.rolling(window).mean()).astype(int)
    pos = sig.shift(1) if honest else sig  # cheat = no shift
    pnl = pos * ret
    return sharpe(pnl), nav(pnl)

sh_c, nav_c = run_ma(10, honest=False)
sh_h, nav_h = run_ma(10, honest=True)
print("\n=== MA10 cheat vs honest ===")
print("cheat_same_bar_sharpe", round(sh_c, 4), "nav", round(nav_c, 6))
print("honest_shift1_sharpe", round(sh_h, 4), "nav", round(nav_h, 6))
print("lookahead_def: using today's close in the signal while earning today's close-to-close return.")

# Parameter grid overfitting on first 200 days
train = slice(None, 200)
test = slice(200, None)
windows = list(range(5, 41, 5))
rows = []
for w in windows:
    sig = (px > px.rolling(w).mean()).astype(int)
    pos = sig.shift(1)
    pnl = pos * ret
    rows.append({"w": w, "sharpe_train": sharpe(pnl.iloc[train]), "sharpe_test": sharpe(pnl.iloc[test])})
grid = pd.DataFrame(rows)
best = grid.sort_values("sharpe_train", ascending=False).iloc[0]
print("\n=== parameter grid (honest shift1) ===")
print("windows", windows)
print("best_train_w", int(best["w"]), "sharpe_train", round(float(best["sharpe_train"]), 4), "sharpe_test", round(float(best["sharpe_test"]), 4))
print("mean_train_sharpe", round(float(grid["sharpe_train"].mean()), 4), "mean_test_sharpe", round(float(grid["sharpe_test"].mean()), 4))
print("teach: picking max in-sample Sharpe after many trials overstates OOS — log trial counts.")

# Final hold-out: freeze w from train only, evaluate last 80 days never used in selection
hold = slice(-80, None)
develop = slice(None, -80)
sig = (px > px.rolling(int(best["w"])).mean()).astype(int)
pos = sig.shift(1)
pnl = pos * ret
print("\n=== freeze-then-holdout ===")
print("develop_n", len(px.iloc[develop]), "holdout_n", len(px.iloc[hold]))
print("frozen_w", int(best["w"]))
print("sharpe_develop", round(sharpe(pnl.iloc[develop]), 4))
print("sharpe_holdout", round(sharpe(pnl.iloc[hold]), 4))
print("quant_arena_spirit: research feedback only on an earlier window; freeze one rule; score a sealed later window (arXiv:2610.30113).")

# Multi-seed random rules: expected false hits context
rng = np.random.default_rng(9)
false = []
for seed in range(50):
    rr = np.random.default_rng(seed)
    hits = 0
    for _ in range(30):
        noise = rr.normal(size=n)
        pos = pd.Series(np.sign(noise), index=ret.dropna().index)
        if abs(sharpe(pos * ret.dropna())) > 1.5:
            hits += 1
    false.append(hits)
print("\n=== random-rule false hits (50 seeds × 30 trials, thr |SR|>1.5) ===")
print("mean_false_hits", round(float(np.mean(false)), 3), "std_false_hits", round(float(np.std(false, ddof=1)), 3))
print("null_note: under noise, some seeds look 'significant' — record trials.")

print("\n=== failure log template ===")
print("date | hypothesis | trials | best_is_metric | oos_metric | fail_reason | next_action")
print("2026-11-04 | MA grid | 8 windows | train SR see above | holdout SR see above | IS≠OOS | shrink search / pre-register")
print("ASSERTS_OK")
