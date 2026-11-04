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
nav_h=round(float((1 + honest.fillna(0)).cumprod().iloc[-1]), 6)
nav_p=round(float((1 + peek.fillna(0)).cumprod().iloc[-1]), 6)
print("panel_nav_honest_shift1", nav_h)
print("panel_nav_signal_times_next_ret", nav_p)
print(
    "equality_why: honest = shift(1)*ret and peek = signal*ret.shift(-1) are the SAME "
    "PnL stream shifted by one bar (identical non-NA products, different timestamps); "
    "equal NAV is NOT evidence that peek is look-ahead-free — both use next-period returns "
    "aligned to a prior signal; same-bar signal*ret WOULD be look-ahead."
)
print("equal_nav", nav_h == nav_p)

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

# --- Information-driven bars toy (AFML ch.2 spirit; NOT an HFT recipe) ---
print("\n=== information bars toy (AFML ch.2; teaching only, NO HFT recipe) ===")
print("cite: López de Prado AFML ch.2 — tick/volume/dollar bars vs time bars")
print("params: synthetic tick stream seed=0; n_ticks=5000; time_bar=50 ticks wall; tick_bar=50 trades; vol_bar=200 shares; dollar_bar≈200*mid")
import numpy as np
rng = np.random.default_rng(0)
n_ticks = 5000
# Random-walk mid with stochastic size
mid = 100 * np.exp(np.cumsum(rng.normal(0, 0.0008, size=n_ticks)))
size = rng.integers(1, 20, size=n_ticks)
dollar = mid * size
ts = pd.date_range("2024-01-02 09:30", periods=n_ticks, freq="s")
ticks = pd.DataFrame({"mid": mid, "size": size, "dollar": dollar}, index=ts)

def make_bars(rule_values, threshold, price):
    """Accumulate until threshold; emit OHLC on trigger. Teaching sketch."""
    bars = []
    acc = 0.0
    o = h = l = c = None
    t0 = None
    for t, v, px in zip(rule_values.index, rule_values.values, price.values):
        if o is None:
            o = h = l = c = float(px)
            t0 = t
        h = max(h, float(px)); l = min(l, float(px)); c = float(px)
        acc += float(v)
        if acc >= threshold:
            bars.append({"t": t, "open": o, "high": h, "low": l, "close": c, "acc": acc})
            acc = 0.0
            o = h = l = c = None
    return pd.DataFrame(bars).set_index("t") if bars else pd.DataFrame()

# Time bars: every 50 ticks (wall-clock proxy)
time_idx = np.arange(len(ticks))
time_bars = make_bars(pd.Series(1, index=ticks.index), 50, ticks["mid"])
tick_bars = make_bars(pd.Series(1, index=ticks.index), 50, ticks["mid"])  # same threshold unit=trades
# volume / dollar use different clocks
vol_bars = make_bars(ticks["size"], 200, ticks["mid"])
# dollar threshold ≈ 200 * typical mid
dol_thr = 200 * float(ticks["mid"].iloc[0])
dol_bars = make_bars(ticks["dollar"], dol_thr, ticks["mid"])

def bar_stats(name, bars):
    if bars.empty or len(bars) < 3:
        print(name, "too_few")
        return
    ret = bars["close"].pct_change().dropna()
    print(
        f"{name:12s} n_bars={len(bars):4d} mean_|ret|={ret.abs().mean():.6f} "
        f"std_ret={ret.std(ddof=1):.6f} max_gap_s={(bars.index.to_series().diff().dt.total_seconds().max()):.0f}"
    )

print("clock comparison on SAME synthetic tick tape:")
bar_stats("time/tick50", time_bars)
bar_stats("volume200", vol_bars)
bar_stats("dollar~200p", dol_bars)
print(
    "teach: time bars sample the clock; tick/volume/dollar bars sample activity — "
    "busy periods mint more bars, quiet periods fewer. This is a sampling choice for research bars, "
    "NOT a latency or HFT execution recipe."
)
print(
    "intuition: if news hits and 1000 trades arrive in one minute, time bars still emit one 1-min bar, "
    "while tick/volume/dollar bars emit many — returning the series closer to an 'information clock'."
)
# Tiny numeric toy for the lesson table
print("toy_counts", {"time50": len(time_bars), "vol200": len(vol_bars), "dollar": len(dol_bars)})

# --- Mask-first / upstream contamination toy (arXiv:2507.07107 spirit) ---
# Learning only. HARD REJECT paper Sharpe 2.05/1.63, 213-factor engine, AdjMSE as course alpha.
print("\n=== mask-first / upstream contamination (arXiv:2507.07107; Boolean mask contract) ===")
print("cite: https://arxiv.org/abs/2507.07107 — upstream contamination: limit closes enter rolling ops BEFORE row filter")
print("paper_ablation_cite: no-mask apparent IC +18% while realised Sharpe −0.44 vs full mask (author ablation)")
print("REJECT_as_course_alpha: Sharpe 2.05 synthetic / 1.63 real; 213-factor GPU engine; AdjMSE γ system")
print("params: toy seed=11; T=750; N=120; limit_up_p≈0.04; mom_window=10; fantasy vs realisable fill")

rng_m = np.random.default_rng(11)
T_m, N_m = 750, 120
rets_m = rng_m.normal(0.00015, 0.016, size=(T_m, N_m))
lu = rng_m.random((T_m, N_m)) < 0.04
rets_m = np.where(lu, 0.098, rets_m)
ld = (~lu) & (rng_m.random((T_m, N_m)) < 0.02)
rets_m = np.where(ld, -0.098, rets_m)
for t in range(T_m - 1):
    rets_m[t + 1] = np.where(lu[t], rets_m[t + 1] + 0.012, rets_m[t + 1])
prices_m = 100 * np.cumprod(1 + rets_m, axis=0)
M_m = ~(lu | ld)
fwd_m = np.full((T_m, N_m), np.nan)
fwd_m[:-1] = rets_m[1:]
M_next = np.vstack([M_m[1:], np.zeros((1, N_m), dtype=bool)])

px_df = pd.DataFrame(prices_m)
feat_c = (px_df / px_df.shift(10) - 1).to_numpy()
px_masked = prices_m.astype(float).copy()
px_masked[~M_m] = np.nan
px_ff = pd.DataFrame(px_masked).ffill()
feat_m = (px_ff / px_ff.shift(10) - 1).to_numpy()
n_bad = np.zeros((T_m, N_m))
for k in range(10):
    pad = np.zeros((k, N_m))
    n_bad += np.vstack([pad, (~M_m)[: T_m - k].astype(float)])
feat_m = feat_m.copy()
feat_m[n_bad >= 1] = np.nan
feat_m[~M_m] = np.nan

def _rank_ic(sig, realisable: bool) -> float:
    ics = []
    for t in range(10, T_m - 1):
        s, y = sig[t], fwd_m[t]
        m = np.isfinite(s) & np.isfinite(y)
        if realisable:
            m &= M_m[t] & M_next[t]
        if m.sum() < 30:
            continue
        ics.append(float(pd.Series(s[m]).rank().corr(pd.Series(y[m]).rank())))
    return float(np.mean(ics)) if ics else float("nan")

def _ls_sr(sig, fantasy: bool) -> float:
    pnls = []
    for t in range(10, T_m - 1):
        s = sig[t].copy()
        if not fantasy:
            s[~M_m[t]] = np.nan
        m = np.isfinite(s)
        if m.sum() < 50:
            continue
        r = pd.Series(s).rank(pct=True)
        w = np.zeros(N_m)
        top = (r >= 0.8).to_numpy() & m
        bot = (r <= 0.2).to_numpy() & m
        if top.sum() < 5 or bot.sum() < 5:
            continue
        w[top] = 1.0 / top.sum()
        w[bot] = -1.0 / bot.sum()
        y = fwd_m[t].copy()
        if not fantasy:
            y[~(M_m[t] & M_next[t])] = 0.0
        pnls.append(float(w @ y))
    p = np.asarray(pnls, dtype=float)
    return float(p.mean() / p.std(ddof=1) * np.sqrt(252))

ic_app = _rank_ic(feat_c, False)
ic_real_c = _rank_ic(feat_c, True)
ic_mask = _rank_ic(feat_m, True)
sr_fant = _ls_sr(feat_c, True)
sr_real_c = _ls_sr(feat_c, False)
sr_mask = _ls_sr(feat_m, False)
print("toy_IC_apparent_contam", round(ic_app, 4))
print("toy_IC_realisable_contam", round(ic_real_c, 4))
print("toy_IC_mask_first", round(ic_mask, 4))
print(
    "toy_IC_inflate_apparent_vs_realisable_pct",
    round((ic_app / ic_real_c - 1) * 100, 1) if ic_real_c else None,
)
print("toy_SR_fantasy_contam", round(sr_fant, 3))
print("toy_SR_realisable_contam", round(sr_real_c, 3))
print("toy_SR_mask_first", round(sr_mask, 3))
print("toy_SR_gap_fantasy_minus_realisable", round(sr_fant - sr_real_c, 3))
print(
    "teach: contaminated rolling features make limit-chasing look predictive (high apparent IC / fantasy SR); "
    "realisable fill on the same features collapses — mask-first Boolean contract refuses non-executable closes in the window."
)
print(
    "boolean_mask_contract: M[t,i]=tradable; every rolling op must ignore cells with M=0; "
    "post-hoc row drop CANNOT un-poison aggregates already computed."
)

print("\n=== rolling MA contamination sketch (5 closes) ===")
closes = np.array([10.0, 10.1, 10.2, 11.2, 10.3])
mask5 = np.array([True, True, True, False, True])
ma_naive = pd.Series(closes).rolling(3).mean()
closes_m5 = closes.astype(float).copy()
closes_m5[~mask5] = np.nan
ma_mask = [float("nan")] * 2 + [float(np.nanmean(closes_m5[i - 2 : i + 1])) for i in range(2, 5)]
print("closes", closes.tolist())
print("tradable_mask", mask5.astype(int).tolist())
print("MA3_naive", [None if pd.isna(x) else round(float(x), 4) for x in ma_naive])
print("MA3_mask_first", [None if (isinstance(x, float) and np.isnan(x)) else round(x, 4) for x in ma_mask])
print("teach: day-index-3 limit print 11.2 enters naive MA for indices 3–4; mask-first never reads it.")
print("ASSERT_mask_first_demo_ok")
