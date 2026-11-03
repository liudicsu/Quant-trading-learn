"""P2 lab: versioned panel, survivorship, PIT lag, timezone lookahead, adj vs raw.
Learning only — not investment advice.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parent / "data" / "panel_toy.csv"
HASHF = Path(__file__).resolve().parent / "data" / "panel_toy.sha256"
raw_bytes = DATA.read_bytes()
digest = hashlib.sha256(raw_bytes).hexdigest()
expected = HASHF.read_text().split()[0]
print("=== versioned download / hash ===")
print("file", DATA.name)
print("sha256", digest)
print("hash_match", digest == expected)
print("params: panel seed=17 when generated; n_rows from file")

df = pd.read_csv(DATA, parse_dates=["date"]).set_index("date").sort_index()
print("n_rows", len(df))

today_universe = ["AAA", "BBB"]
hist_members = ["AAA", "BBB", "CCC"]
print("\n=== survivorship toy ===")
print("today_universe", today_universe)
print("historical_members_in_panel", hist_members)
r_aaa = df["AAA_adj"].pct_change()
r_bbb = df["BBB_adj"].pct_change()
r_ccc = df["CCC_adj"].pct_change()
ew_today = pd.concat([r_aaa, r_bbb], axis=1).mean(axis=1)
ew_hist = pd.concat([r_aaa, r_bbb, r_ccc], axis=1).mean(axis=1)
print("mean_ret_survivors_only", round(float(ew_today.mean()), 6))
print("mean_ret_full_hist_universe", round(float(ew_hist.mean()), 6))
print("teach: today's constituents != historical investable universe.")

print("\n=== PIT fundamental lag ===")
print("params: publish_lag_bdays=5; FUND_pit = FUND_true.shift(5)")
corr_cheat = float(df["FUND_true"].corr(df["AAA_adj"].pct_change()))
corr_pit = float(df["FUND_pit"].corr(df["AAA_adj"].pct_change()))
print("corr_fund_true_vs_ret", round(corr_cheat, 4))
print("corr_fund_pit_vs_ret", round(corr_pit, 4))
print("lookahead_flag: aligning fundamentals without as-of/PIT can leak future prints.")

print("\n=== timezone / session label mess ===")
hand = pd.Series(
    [100.0, 101.0, 100.5],
    index=pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"]),
)
bug_index = hand.index - pd.tseries.offsets.BDay(1)
hand_bug = pd.Series(hand.values, index=bug_index)
print("true_closes")
print(hand.to_string())
print("mislabeled_closes_minus_1bd")
print(hand_bug.to_string())
aligned = hand_bug.reindex(hand.index)
print("aligned_bug_on_true_calendar")
print(aligned.to_string())
print("tue_row_price_after_bug", float(aligned.loc["2024-01-03"]))
print("teach: Tue's row now carries Wed's close — one-day timezone/session mislabel embeds look-ahead.")
ret = df["AAA_adj"].pct_change()
sig = (df["AAA_adj"] > df["AAA_adj"].rolling(10).mean()).astype(int)
honest = sig.shift(1) * ret
peek = sig * ret.shift(-1)
print("panel_nav_honest_shift1", round(float((1 + honest.fillna(0)).cumprod().iloc[-1]), 6))
print("panel_nav_signal_times_next_ret", round(float((1 + peek.fillna(0)).cumprod().iloc[-1]), 6))

print("\n=== reindex + missingness assert ===")
cal = pd.bdate_range(df.index.min(), df.index.max())
re = df.reindex(cal)
missing = int(re["AAA_adj"].isna().sum())
print("calendar_rows", len(cal), "panel_rows", len(df), "missing_after_reindex", missing)
assert missing == 0, "unexpected gaps in synthetic panel"
print("ASSERT_missing_ok")

print("\n=== adj vs raw (2:1 split toy at iloc 200) ===")
i = 200
print("raw_before", round(float(df["AAA_raw"].iloc[i - 1]), 4), "raw_after", round(float(df["AAA_raw"].iloc[i]), 4))
print("adj_before", round(float(df["AAA_adj"].iloc[i - 1]), 4), "adj_after", round(float(df["AAA_adj"].iloc[i]), 4))
print("raw_ret_across_split", round(float(df["AAA_raw"].iloc[i] / df["AAA_raw"].iloc[i - 1] - 1), 4))
print("adj_ret_across_split", round(float(df["AAA_adj"].iloc[i] / df["AAA_adj"].iloc[i - 1] - 1), 4))
print("data_sheet_stub: source=synthetic; seed=17; fields=adj/raw/PIT; timezone=naive dates; universe_rule=see survivorship note")
print("ASSERTS_OK")
