"""P2 lab 05: data versions, corporate actions, trading calendars (offline synthetic, seed=7).
Learning only — not investment advice.

A. Two monthly-return conventions on the SAME synthetic daily prices + one dividend:
   - month-end reinvest (like the legacy CRSP FIZ convention described on Ken French's site)
   - compound daily returns, dividend reinvested on the ex-date (like CIZ)
B. A 2-for-1 split: raw close vs split-adjusted close.
C. Trading calendar: joining two markets with different holidays.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

rng = np.random.default_rng(7)
days = pd.bdate_range("2025-01-01", "2025-02-28")
r = rng.normal(0.0004, 0.012, len(days))
price = pd.Series(100 * np.cumprod(1 + r), index=days)
ex_date = days[10]          # ex-dividend date in January
div = 2.0
price[price.index >= ex_date] -= div   # price drops by the dividend on the ex-date

print("=== A. monthly return conventions (same data) ===")
jan = price[price.index.month == 1]
prev_close = 100.0
# convention 1: price return over month + dividend added at month end (reinvested at month-end)
r_month_end = (jan.iloc[-1] + div) / prev_close - 1
# convention 2: daily total returns (dividend counted on ex-date) compounded
p = pd.concat([pd.Series([prev_close], index=[days[0] - pd.Timedelta(days=1)]), jan])
d = np.zeros(len(p)); d[list(p.index).index(ex_date)] = div
daily_tr = (p.values[1:] + d[1:]) / p.values[:-1] - 1
r_ex_date = np.prod(1 + daily_tr) - 1
print(f"Jan month-end reinvest  : {r_month_end:.6f}")
print(f"Jan ex-date reinvest    : {r_ex_date:.6f}")
print(f"difference (bp)         : {(r_ex_date - r_month_end) * 1e4:.2f}")
print("-> same prices, different conventions => record which data VERSION you used")

print("=== B. 2-for-1 split ===")
raw = pd.Series([50.0, 51.0, 25.6, 25.9], index=pd.bdate_range("2025-03-03", periods=4))
factor = pd.Series([0.5, 0.5, 1.0, 1.0], index=raw.index)   # split effective on day 3
adj = raw * factor
print("raw daily ret     :", np.round(raw.pct_change().dropna().values, 4).tolist())
print("adjusted daily ret:", np.round(adj.pct_change().dropna().values, 4).tolist())
print("-> raw shows a fake -49.8% 'crash'; adjusted shows the economic move")

print("=== C. trading calendars ===")
a_days = pd.bdate_range("2025-04-01", "2025-04-10")
b_days = a_days.drop(pd.Timestamp("2025-04-04"))           # market B closed on 04-04
a = pd.Series(rng.normal(0, 0.01, len(a_days)), index=a_days)
b = pd.Series(rng.normal(0, 0.01, len(b_days)), index=b_days)
outer_ffill = pd.concat([a, b], axis=1).ffill()
inner = pd.concat([a, b], axis=1, join="inner")
print(f"A days={len(a)} B days={len(b)} inner-join days={len(inner)}")
print(f"ffill rows where B return is a stale copy: {int((outer_ffill.index == '2025-04-04').sum())}")
print("-> forward-filling a RETURN invents a trade on a closed day; use the right calendar")
print("=== D. raw vs split-adjusted vs total return; share ledger; delisting ===")
# hand-made: 100 shares at 60.00; 2-for-1 split; then 0.50/share cash dividend (post-split); then delisted
shares, cash = 100, 0.0
raw = [60.00, 61.00, 30.40, 30.10, 30.30]            # day3 = split day; day4 = ex-dividend
events = {2: ("split", 2.0), 3: ("div", 0.50)}
wealth = []
for i, px in enumerate(raw):
    ev = events.get(i)
    if ev and ev[0] == "split":
        shares = int(shares * ev[1])
    if ev and ev[0] == "div":
        cash += shares * ev[1]
    wealth.append(shares * px + cash)
print("shares/cash ledger wealth:", [round(w, 2) for w in wealth])
split_adj = [p / 2.0 if i < 2 else p for i, p in enumerate(raw)]
pr = [split_adj[i] / split_adj[i - 1] - 1 for i in range(1, len(raw))]
tr = [(split_adj[i] + (0.50 if i == 3 else 0.0)) / split_adj[i - 1] - 1 for i in range(1, len(raw))]
print("split-adj price ret:", [round(x, 4) for x in pr])
print("total ret (div once):", [round(x, 4) for x in tr])
wrong = (split_adj[3] + 0.50 + 0.50) / split_adj[2] - 1
print(f"double-counted dividend on ex-day: {wrong:.4f} vs correct {tr[2]:.4f}")
print(f"split day: ledger wealth {wealth[1]:.2f} -> {wealth[2]:.2f} (shares doubled, no free wealth)")
delist_ret_known, delist_ret_missing = -0.30, None
print(f"delisting: final ret known={delist_ret_known:+.2f}; missing ret -> flag 'delist_ret_missing', do NOT drop or set 0")
print("disclaimer: synthetic; learning only")
