"""P0 lab: synthetic OHLC → returns, MA, misalignment demo, asserts.
Learning only — not investment advice. Offline synthetic data.
"""
from __future__ import annotations

import pandas as pd

# Fixed synthetic closes (deterministic)
idx = pd.bdate_range("2024-01-02", periods=8)
close = pd.Series([100.0, 101.0, 100.5, 102.0, 101.5, 103.0, 104.0, 103.5], index=idx, name="close")
ohlc = pd.DataFrame(
    {
        "open": close.shift(1).fillna(close.iloc[0]),
        "high": close + 0.5,
        "low": close - 0.5,
        "close": close,
    }
)

ret = ohlc["close"].pct_change()
ma3 = ohlc["close"].rolling(3).mean()

print("=== OHLC head ===")
print(ohlc.round(4).to_string())
print("\n=== returns & MA3 ===")
print(pd.DataFrame({"ret": ret, "ma3": ma3}).round(6).to_string())

# Deliberate misalignment: use tomorrow's close in today's signal (lookahead toy)
bad_signal = (ohlc["close"].shift(-1) > ma3).astype(int)
good_signal = (ohlc["close"] > ma3).astype(int)
position = good_signal.shift(1)  # decide with info known by prior close

print("\n=== signals (1=above MA3) ===")
print(
    pd.DataFrame(
        {
            "good_signal": good_signal,
            "position_shift1": position,
            "bad_lookahead": bad_signal,
        }
    ).to_string()
)

# Three asserts for a reproducible pipeline
assert isinstance(ohlc.index, pd.DatetimeIndex), "index must be DatetimeIndex"
assert ohlc["close"].dtype.kind in "fi", "close must be numeric"
assert ret.isna().sum() == 1 and pd.isna(ret.iloc[0]), "first pct_change should be NaN"

print("\nASSERTS_OK")
print("misaligned_days", int((bad_signal.fillna(0) != good_signal.fillna(0)).sum()))
