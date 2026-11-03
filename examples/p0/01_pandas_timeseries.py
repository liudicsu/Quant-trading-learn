"""P0 lab: CSV→DatetimeIndex, align, missing values, rolling, plot, lookahead asserts.
Learning only — not investment advice. Offline synthetic data.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CSV = Path(__file__).resolve().parent / "data" / "synthetic_ohlc.csv"
OUT_PNG = ROOT / "public" / "p0" / "returns_ma.png"

# --- 1) read_csv → DatetimeIndex ---
raw = pd.read_csv(CSV)
ohlc = raw.copy()
ohlc["date"] = pd.to_datetime(ohlc["date"])
ohlc = ohlc.set_index("date").sort_index()
print("=== OHLC from CSV (DatetimeIndex) ===")
print(ohlc.round(4).to_string())
print("index_type", type(ohlc.index).__name__)

# --- 2) reindex / align worked example ---
# Series A: all business days in the CSV calendar
a = ohlc["close"].rename("a")
# Series B: drop two mid dates to simulate a different venue calendar
b = a.drop(a.index[[2, 5]]).rename("b")
inner = pd.concat([a, b], axis=1, join="inner")
outer = pd.concat([a, b], axis=1, join="outer")
print("\n=== align calendars ===")
print("a_len", len(a), "b_len", len(b))
print("inner_rows", len(inner), "inner_nonnull_b", int(inner["b"].notna().sum()))
print("outer_rows", len(outer), "outer_null_b", int(outer["b"].isna().sum()))
print("inner_table")
print(inner.round(4).to_string())
print("outer_table")
print(outer.round(4).to_string())

# --- 3) missing-value handling trade-offs ---
planted = ohlc["close"].copy()
planted.iloc[[3, 7]] = float("nan")  # plant NaNs on two closes
methods = {
    "dropna": planted.dropna(),
    "ffill": planted.ffill(),
    "interpolate": planted.interpolate(method="time"),
}
print("\n=== missing-value handling (planted NaN at iloc 3,7) ===")
print("planted_close")
print(planted.round(4).to_string())
for name, s in methods.items():
    r = s.pct_change()
    print(f"{name}: n={len(s)} mean_ret={float(r.mean()):.6f} n_ret_nonnull={int(r.notna().sum())}")

# Trade-off notes (also printed for the lesson paste)
print(
    "tradeoffs: dropna shortens the sample and changes overlapping windows; "
    "ffill invents flat prices on missing days (fake prints); "
    "time-interpolate invents a smooth path between known prints — neither is 'true' volume."
)

# --- 4) returns, rolling, plot ---
ret = ohlc["close"].pct_change()
ma3 = ohlc["close"].rolling(3).mean()
print("\n=== returns & MA3 ===")
print(pd.DataFrame({"ret": ret, "ma3": ma3}).round(6).to_string())

OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
fig, ax = plt.subplots(figsize=(7.5, 3.6), dpi=120)
ax.plot(ohlc.index, ohlc["close"], marker="o", label="close")
ax.plot(ma3.index, ma3, marker="o", label="MA3")
ax.set_title("Synthetic close and 3-day MA (teaching data)")
ax.set_xlabel("date")
ax.set_ylabel("price")
ax.legend(loc="best")
ax.grid(True, alpha=0.3)
fig.autofmt_xdate()
fig.tight_layout()
fig.savefig(OUT_PNG)
plt.close(fig)
print("saved_plot", OUT_PNG.relative_to(ROOT).as_posix())

# --- 5) lookahead vs shift(1) ---
good_signal = (ohlc["close"] > ma3).astype(int)
position = good_signal.shift(1)
bad_signal = (ohlc["close"].shift(-1) > ma3).astype(int)
print("\n=== signals ===")
print(
    pd.DataFrame(
        {"good_signal": good_signal, "position_shift1": position, "bad_lookahead": bad_signal}
    ).to_string()
)
misaligned_days = int((bad_signal.fillna(0) != good_signal.fillna(0)).sum())
print("misaligned_days", misaligned_days)

# --- 6) asserts ---
assert isinstance(ohlc.index, pd.DatetimeIndex), "index must be DatetimeIndex"
assert ohlc["close"].dtype.kind in "fi", "close must be numeric"
assert ret.isna().sum() >= 1 and pd.isna(ret.iloc[0]), "first pct_change should be NaN"
print("\nASSERTS_OK")
