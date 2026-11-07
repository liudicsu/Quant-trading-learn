"""US factor benchmark parsing toy (S-B). Offline: a hand-made Ken French-SHAPED CSV string, not real data.
Teaches: percent -> decimal, -99.99 / -999 missing markers, excess return = R - RF, daily -> monthly compounding,
and that Mkt-RF already has RF subtracted. Source format: Ken French Data Library (checked 2026-11-08). Learning only."""
import io
import numpy as np
import pandas as pd

RAW = """This file was created by a SYNTHETIC generator (shape mimics the library's daily file)
,Mkt-RF,SMB,HML,RF
20260601,0.50,-0.10,0.20,0.02
20260602,-1.20,0.30,-99.99,0.02
20260603,0.80,0.05,0.10,0.02
20260630,0.40,-0.20,0.15,0.02
20260701,-0.30,0.10,-999,0.02
20260702,1.00,0.00,0.05,0.02
"""
df = pd.read_csv(io.StringIO(RAW), skiprows=1, index_col=0)
df.index = pd.to_datetime(df.index.astype(str), format="%Y%m%d")
df = df.replace([-99.99, -999], np.nan)
print("A) missing markers -> NaN:", int(df.isna().sum().sum()), "cells")
dec = df / 100.0
print("B) percent -> decimal, first row:", dec.iloc[0].round(4).to_dict())
mkt = dec["Mkt-RF"] + dec["RF"]
print("C) total market return = (Mkt-RF) + RF, day 1:", round(float(mkt.iloc[0]), 4))
strat = pd.Series([0.006, -0.010, 0.009, 0.004, -0.002, 0.011], index=dec.index)
excess = strat - dec["RF"]
print("D) strategy excess (R - RF) day 1:", round(float(excess.iloc[0]), 4))
monthly = (1 + mkt).groupby(mkt.index.to_period("M")).prod() - 1
wrong = mkt.groupby(mkt.index.to_period("M")).sum()
for p in monthly.index:
    print(f"E) {p}: compounded={monthly[p]:.5f} simple_sum={wrong[p]:.5f}")
hml_m = (1 + dec["HML"]).groupby(dec.index.to_period("M")).prod(min_count=1) - 1
print("F) HML month with a NaN day is NOT silently zero-filled; NaN days:", int(dec['HML'].isna().sum()))
print("G) double subtraction trap: (Mkt-RF) - RF day 1 =", round(float(dec['Mkt-RF'].iloc[0] - dec['RF'].iloc[0]), 4), "(wrong)")
