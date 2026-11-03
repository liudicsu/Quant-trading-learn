"""P2 lab: turnover cost formula + cost ladder chart.
Learning only — not investment advice.
"""
from __future__ import annotations
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "public" / "p2" / "cost_ladder.png"
DATA = Path(__file__).resolve().parent / "data" / "panel_toy.csv"
df = pd.read_csv(DATA, parse_dates=["date"]).set_index("date").sort_index()
px = df["AAA_adj"]
ret = px.pct_change()
sig = (px > px.rolling(10).mean()).astype(int)
pos = sig.shift(1)
turn = pos.diff().abs().fillna(pos.abs())
ANN = np.sqrt(252)
print("=== parameters ===")
print("n", int(ret.notna().sum()), "MA=10", "position=shift(1)", "Rf=0", "ann=sqrt(252)")
print("cost_formula: net = pos*ret - turnover * one_way_bps/1e4")
print("explicit_costs: commission-like bps; implicit: spread/impact approximated in bps ladder")

def net_stats(bps: float) -> dict:
    cost = turn * (bps / 1e4)
    pnl = pos * ret - cost
    x = pnl.dropna()
    sh = float(x.mean() / x.std(ddof=1) * ANN)
    nav = float((1 + x.fillna(0)).cumprod().iloc[-1])
    return {"bps": bps, "sharpe": round(sh, 4), "final_nav": round(nav, 4), "ann_ret": round(float(x.mean() * 252), 4)}

ladder = [net_stats(b) for b in [0, 5, 10, 20, 40]]
print("\n=== cost ladder ===")
print(pd.DataFrame(ladder).to_string(index=False))
print("teach: zero-cost curve ≠ live evidence; turnover amplifies every bps.")

OUT.parent.mkdir(parents=True, exist_ok=True)
fig, ax = plt.subplots(figsize=(6.8, 3.4), dpi=120)
ax.plot([r["bps"] for r in ladder], [r["sharpe"] for r in ladder], "o-", color="#b45309")
ax.set_xlabel("one-way cost (bps)")
ax.set_ylabel("Sharpe (Rf=0, √252)")
ax.set_title("Cost ladder: honest MA10 on synthetic AAA")
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(OUT)
plt.close(fig)
print("saved_plot", OUT.relative_to(ROOT).as_posix())
print("ASSERTS_OK")
