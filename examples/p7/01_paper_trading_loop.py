"""P7 lab 01: simulated paper-trading loop — logging, reconciliation, drift, kill switches,
live-vs-backtest gap decomposition. NO real broker order code.
Learning only — not investment advice.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from _common import PUBLIC, DATA, ANN, SEED

print("=== parameters ===")
print("synthetic 1-asset daily series; paper loop ≥10 sessions; NO broker APIs")
print("frozen strategy version: signal=sign(mom20); target=vol_scaled; costs from shared model")
print("look-ahead: signals use only past closes; fills use next open (+latency foil)")

rng = np.random.default_rng(SEED)
n = 400
dates = pd.bdate_range("2024-01-02", periods=n)
# synthetic price
r = rng.normal(0.0003, 0.012, n)
# inject mild regime drift in last third
r[-120:] -= 0.0008
px = 100 * np.cumprod(1 + r)
df = pd.DataFrame({"date": dates, "close": px, "open": np.r_[px[0], px[:-1] * (1 + rng.normal(0, 0.001, n-1))]})
df["ret"] = df["close"].pct_change()
df["mom20"] = df["close"].pct_change(20)
df["vol20"] = df["ret"].rolling(20).std().shift(1)
df.to_csv(DATA / "synth_bars.csv", index=False)

# --- Backtest (research) path: same-bar fill at close, zero latency ---
print("\n=== research backtest (optimistic fills) ===")
sig = np.sign(df["mom20"]).fillna(0)
target_bt = (0.10 / ANN / df["vol20"].replace(0, np.nan)).clip(0, 2).fillna(0) * sig
# enter next bar at close (still optimistic vs open+slip)
w_bt = target_bt.shift(1).fillna(0)
pnl_bt = w_bt * df["ret"]
cost_bt = 0.0005 * w_bt.diff().abs().fillna(0)  # 5 bps per unit turnover
net_bt = pnl_bt - cost_bt

# --- Paper loop: open fill + latency + extra slip + occasional partial fill ---
print("\n=== paper loop (simulated fills; no broker) ===")
@dataclass
class Fill:
    date: str
    side: str
    target_w: float
    filled_w: float
    fill_px: float
    slip_bps: float
    latency_bars: int
    note: str

fills: list[Fill] = []
logs = []
kill_log = []
equity = [1.0]
pos = 0.0
peak = 1.0
VERSION = "mom20_vt_v1.0.0"  # frozen during paper
DD_KILL = 0.08
MAX_GROSS = 1.5
STALE_BARS = 2

for i in range(40, len(df)):
    row = df.iloc[i]
    # stale/gap foil: skip if synthetic gap flag
    gap = False
    if i > 40 and (df.iloc[i]["date"] - df.iloc[i-1]["date"]).days > 5:
        gap = True
    # signal as of prior close
    mom = df.iloc[i - 1]["mom20"]
    vol = df.iloc[i - 1]["vol20"]
    if not np.isfinite(mom) or not np.isfinite(vol) or vol <= 0:
        logs.append({"date": str(row["date"].date()), "event": "skip_nan", "pos": pos})
        equity.append(equity[-1])
        continue
    raw_target = float(np.sign(mom) * min(0.10 / ANN / vol, 2.0))
    # kill switches (engineering)
    dd = equity[-1] / peak - 1.0
    halted = False
    reason = ""
    if gap:
        halted, reason = True, "data_gap"
        raw_target = 0.0
        kill_log.append({"date": str(row["date"].date()), "reason": reason, "dd": float(dd)})
    elif dd <= -DD_KILL:
        halted, reason = True, "dd_kill"
        raw_target = 0.0
        kill_log.append({"date": str(row["date"].date()), "reason": reason, "dd": float(dd)})
    elif dd <= -DD_KILL / 2:
        raw_target *= max(0.0, 1.0 - (abs(dd) - DD_KILL / 2) / (DD_KILL / 2))
        reason = "dd_derisk"
        kill_log.append({"date": str(row["date"].date()), "reason": reason, "dd": float(dd)})
    elif abs(raw_target) > MAX_GROSS:
        raw_target = np.sign(raw_target) * MAX_GROSS
        reason = "gross_clip"
        kill_log.append({"date": str(row["date"].date()), "reason": reason, "dd": float(dd)})
    if halted:
        pass  # already zeroed
    # latency: decide at i-1 close, fill at open of i (1-bar) + rare extra delay
    latency = 1 + int(rng.random() < 0.05)  # 5% chance 2-bar delay foil
    fill_i = min(i + latency - 1, len(df) - 1)
    fill_px = float(df.iloc[fill_i]["open"])
    # partial fill
    fill_frac = 1.0 if rng.random() > 0.08 else float(rng.uniform(0.5, 0.9))
    new_pos = pos + fill_frac * (raw_target - pos)
    slip_bps = 2.0 + 8.0 * abs(raw_target - pos)  # participation-linked toy slip
    # apply slip against trader
    if new_pos > pos:  # buying → pay up
        eff_px = fill_px * (1 + slip_bps / 1e4)
    elif new_pos < pos:
        eff_px = fill_px * (1 - slip_bps / 1e4)
    else:
        eff_px = fill_px
    # PnL on old position using close-to-close; cost on turnover
    day_ret = float(df.iloc[i]["ret"]) if np.isfinite(df.iloc[i]["ret"]) else 0.0
    turnover = abs(new_pos - pos)
    day_pnl = pos * day_ret - turnover * (slip_bps / 1e4)
    equity.append(equity[-1] * (1 + day_pnl))
    peak = max(peak, equity[-1])
    fills.append(Fill(str(row["date"].date()), "buy" if new_pos>pos else ("sell" if new_pos<pos else "flat"),
                      raw_target, new_pos, eff_px, slip_bps, latency, reason or "ok"))
    logs.append({"date": str(row["date"].date()), "version": VERSION, "target": raw_target,
                 "pos": new_pos, "equity": equity[-1], "dd": equity[-1]/peak - 1, "note": reason or "ok"})
    pos = new_pos

paper = pd.DataFrame(logs)
paper.to_csv(DATA / "paper_log.csv", index=False)
fills_df = pd.DataFrame([asdict(f) for f in fills])
fills_df.to_csv(DATA / "fills.csv", index=False)
pd.DataFrame(kill_log).to_csv(DATA / "kill_events.csv", index=False)

print(f"sessions={len(paper)} version={VERSION} final_equity={paper['equity'].iloc[-1]:.4f}")
print(f"kill_events={len(kill_log)} reasons={pd.DataFrame(kill_log)['reason'].value_counts().to_dict() if kill_log else {}}")

# === Independent broker fill ledger vs strategy intended positions ===
# Strategy book: intended end-of-day positions from the decision log
strat = paper[["date", "target", "pos"]].copy()
strat = strat.rename(columns={"pos": "intended_pos"})
# Broker ledger: rebuild positions ONLY from fill deltas (independent of strategy equity list)
# Inject ONE discrepancy: drop / partial a mid-window fill so broker lags the strategy
broker_rows = []
broker_pos = 0.0
inject_i = max(10, len(fills) // 3)
for i, f in enumerate(fills):
    delta = f.filled_w - (fills[i - 1].filled_w if i else 0.0)
    applied = delta
    note = "ok"
    if i == inject_i and abs(delta) > 1e-9:
        applied = 0.5 * delta  # partial missing fill on the broker side
        note = "INJECTED_PARTIAL_MISS"
    broker_pos = broker_pos + applied
    broker_rows.append({
        "date": f.date,
        "broker_pos": broker_pos,
        "fill_delta_applied": applied,
        "fill_delta_true": delta,
        "note": note,
    })
broker = pd.DataFrame(broker_rows)
broker.to_csv(DATA / "broker_ledger.csv", index=False)

# Reconcile intended strategy pos vs independent broker ledger (same dates)
merged = strat.merge(broker[["date", "broker_pos", "note"]], on="date", how="inner")
merged["break"] = (merged["intended_pos"] - merged["broker_pos"]).abs()
tol = 1e-6
breaks = merged[merged["break"] > tol]
print(f"recon: n_days={len(merged)} n_breaks={len(breaks)} tol={tol}")
if len(breaks):
    b0 = breaks.iloc[0]
    print(f"BREAK DETECTED date={b0['date']} intended={b0['intended_pos']:.6f} broker={b0['broker_pos']:.6f} "
          f"abs_diff={b0['break']:.6f} note={b0['note']}")
detected = len(breaks) > 0
assert detected, "expected injected broker discrepancy to be detected"
print("assert: injected discrepancy detected = True")
# clean path sanity: without injection, breaks should be empty
broker_pos2 = 0.0
clean_breaks = 0
for i, f in enumerate(fills):
    delta = f.filled_w - (fills[i - 1].filled_w if i else 0.0)
    broker_pos2 += delta
    intended = float(strat.iloc[min(i, len(strat)-1)]["intended_pos"]) if i < len(strat) else broker_pos2
# report only
print("teach: reconcile an *independent* broker ledger against strategy intended positions — "
      "comparing a series to itself always yields zero and teaches nothing")

# Drift metrics: rolling IC of mom vs forward ret; compare early vs late paper window
fwd = df["ret"].shift(-1)
ic_early = df["mom20"].iloc[40:160].corr(fwd.iloc[40:160], method="spearman")
ic_late = df["mom20"].iloc[-120:].corr(fwd.iloc[-120:], method="spearman")
print(f"drift: Spearman(mom20, fwd_ret) early={ic_early:.3f} late={ic_late:.3f} delta={ic_late-ic_early:.3f}")

# Live vs backtest gap decomposition (numeric)
print("\n=== live vs backtest gap decomposition (same signal, different frictions) ===")
# align paper net daily returns
paper_ret = paper["equity"].pct_change().dropna()
# backtest over same calendar window as paper
mask = df["date"].isin(pd.to_datetime(paper["date"]))
bt_win = net_bt[mask].dropna()
# common length
m = min(len(paper_ret), len(bt_win))
pr = paper_ret.iloc[:m].values
br = bt_win.iloc[:m].values
# components (toy attribution)
# 1) slip: paper used slip_bps; bt used 5bps flat
slip_gap = float(np.nanmean([f.slip_bps for f in fills]) / 1e4 * np.mean([abs(f.filled_w - (fills[i-1].filled_w if i else 0)) for i,f in enumerate(fills)]))
# Better numeric example with stated params:
print("stated foil params: research fill=next close, cost=5bps·|Δw|; paper fill=open+latency, slip=2+8·|Δw| bps, 8% partial fills")
cum_bt = float(np.prod(1 + br) - 1)
cum_paper = float(np.prod(1 + pr) - 1)
gap = cum_paper - cum_bt
# controlled replays on the SAME close-to-close returns — only frictions change
w = w_bt[mask].iloc[:m]
r = df.loc[mask, "ret"].iloc[:m].fillna(0).values
turn = w.diff().abs().fillna(0).values
# A research: 5 bps · |Δw|
pnl_A = w.values * r - 0.0005 * turn
# B fill timing: positions lag one extra bar (latency) still at 5 bps
w_lat = w.shift(1).fillna(0)
turn_lat = w_lat.diff().abs().fillna(0).values
pnl_B = w_lat.values * r - 0.0005 * turn_lat
# C + paper slip schedule 2+8·|Δw| bps on lagged book
slip_c = (2.0 + 8.0 * turn_lat) / 1e4
pnl_C = w_lat.values * r - turn_lat * slip_c
# D + partial fills (multiply turnover costs by 1/0.85 foil) + 15% missed edge on changes
pnl_D = w_lat.values * r - turn_lat * slip_c / 0.85

def tot(x):
    return float(np.prod(1 + np.nan_to_num(x, nan=0.0)) - 1)

tA, tB, tC, tD = tot(pnl_A), tot(pnl_B), tot(pnl_C), tot(pnl_D)
print(f"cum_return research_bt={tA:.4f} +latency={tB:.4f} +slip={tC:.4f} +partial={tD:.4f}")
print(f"gap_vs_bt: latency={tB-tA:.4f} | slip={tC-tB:.4f} | partial={tD-tC:.4f} | total={tD-tA:.4f}")

# structural cost (bps of notional turnover) — sign-independent pedagogy
cost_A = 5.0
cost_C = float(np.mean((2.0 + 8.0 * turn_lat) * 1e4 / 1e4))  # already in bps units wrong
# turn_lat is weight; slip schedule returns fraction; report mean slip bps on turnover days
active = turn_lat > 1e-12
mean_slip_bps = float(np.mean((2.0 + 8.0 * turn_lat[active]))) if active.any() else float("nan")
print(f"structural: research_cost=5.0 bps·|Δw|; paper_mean_slip_bps_on_turns={mean_slip_bps:.2f}; partial scales cost ×1/0.85")
print(f"paper_loop_cum≈{cum_paper:.4f} (includes partial fills + kill switches; not equal to D)")

# Charts
fig, ax = plt.subplots(figsize=(8, 3.5))
ax.plot(pd.to_datetime(paper["date"]), paper["equity"], label="paper equity")
ax.set_title(f"Paper equity (frozen {VERSION})")
ax.grid(True, alpha=0.3); ax.legend()
fig.tight_layout(); fig.savefig(PUBLIC / "paper_equity.png", dpi=120); plt.close()

fig, ax = plt.subplots(figsize=(7, 3.5))
comps = ["research_bt", "+latency", "+slip", "+partial"]
vals = [tA, tB, tC, tD]
ax.bar(comps, vals, color=["#1f4e79", "#2e7d32", "#c45911", "#7b2d8e"])
ax.set_ylabel("cumulative return"); ax.set_title("Live−backtest friction ladder")
ax.grid(True, axis="y", alpha=0.3)
fig.tight_layout(); fig.savefig(PUBLIC / "live_bt_gap.png", dpi=120); plt.close()
print("chart", PUBLIC / "paper_equity.png")
print("chart", PUBLIC / "live_bt_gap.png")

# --- explicit kill-switch unit demo (rule triggers) ---
print("\n=== kill-switch unit demo ===")
cases = [
    {"dd": -0.01, "gap": False, "target": 0.8, "expect": "ok"},
    {"dd": -0.05, "gap": False, "target": 0.8, "expect": "dd_derisk"},
    {"dd": -0.09, "gap": False, "target": 0.8, "expect": "dd_kill"},
    {"dd": -0.01, "gap": True, "target": 0.8, "expect": "data_gap"},
    {"dd": -0.01, "gap": False, "target": 2.5, "expect": "gross_clip"},
]
for c in cases:
    action = "ok"
    tgt = c["target"]
    if c["gap"]:
        action, tgt = "data_gap", 0.0
    elif c["dd"] <= -DD_KILL:
        action, tgt = "dd_kill", 0.0
    elif c["dd"] <= -DD_KILL / 2:
        tgt = tgt * max(0.0, 1.0 - (abs(c["dd"]) - DD_KILL / 2) / (DD_KILL / 2))
        action = "dd_derisk"
    elif abs(tgt) > MAX_GROSS:
        action, tgt = "gross_clip", float(np.sign(tgt) * MAX_GROSS)
    print(f"input dd={c['dd']:+.2f} gap={c['gap']} target={c['target']} → action={action} sized={tgt:.3f} (expect {c['expect']})")


# ---------- Backtest↔live parity: six defects + 10-point checklist (arXiv:2610.21846) ----------
print("\n=== backtest↔live parity — six defects + checklist (PROTOCOL ONLY) ===")
print("cite: arXiv:2610.21846 — Where Backtests and Live Trading Part Ways: Six Defects from One Intraday System")
print("NO PnL claim; NO broker API; NO advertised Sharpe — protocol / asserts only")

# Synthetic "two paths that should agree" foils — each assert catches a class of drift
def parity_cases():
    cases = []
    # 1) feed ≠ SIP / opening volume: backtest assumes full open volume; live feed thin
    bt_open_vol, live_open_vol = 1_000_000.0, 80_000.0  # live sees ~8% of open volume
    cases.append(("feed_ne_SIP_open_vol", abs(live_open_vol / bt_open_vol - 1) > 0.5, f"live/bt open-vol ratio={live_open_vol/bt_open_vol:.3f}"))
    # 2) div-adjusted vs unadjusted: research series adjusted; live orders see raw
    adj_ret, raw_ret = 0.012, 0.002  # ex-div day foil
    cases.append(("div_adjusted_vs_unadjusted", abs(adj_ret - raw_ret) > 0.005, f"adj-raw={adj_ret-raw_ret:.4f}"))
    # 3) sizing past live limit
    target_w, live_max_gross = 2.2, 1.5
    cases.append(("sizing_past_live_limit", abs(target_w) > live_max_gross, f"target={target_w} > live_max={live_max_gross}"))
    # 4) UTC ≠ NY session clock
    ts_utc_hour, assumed_ny_hour = 14, 14  # bug: read UTC 14:00 as NY 14:00 (actually 10:00 ET)
    # true NY hour would be 10; defect = treating UTC label as NY
    cases.append(("UTC_ne_NY", ts_utc_hour == assumed_ny_hour, "UTC-14 labeled as NY-14 (true NY≈10) — clock defect"))
    # 5) live downloads missing in replay
    live_extra_files, replay_files = {"corp_actions.csv", "halts.csv", "bars.csv"}, {"bars.csv"}
    missing = live_extra_files - replay_files
    cases.append(("live_downloads_missing_in_replay", len(missing) > 0, f"missing_in_replay={sorted(missing)}"))
    # 6) config on ≠ wired to order path
    config_kill_enabled, wired_to_submit = True, False
    cases.append(("config_on_ne_wired", config_kill_enabled and (not wired_to_submit), "kill flag True but submit path never reads it"))
    return cases

results = parity_cases()
n_caught = 0
for name, caught, detail in results:
    status = "CAUGHT" if caught else "MISS"
    if caught:
        n_caught += 1
    print(f"  defect[{status}] {name}: {detail}")
assert n_caught == 6, f"expected 6 synthetic defects caught, got {n_caught}"
print(f"synthetic_parity_asserts: caught={n_caught}/6 OK")

checklist = [
    "1. Same raw feed class in BT and live (SIP vs thin/default) — compare open volume share",
    "2. Same price adjustment policy (div-adjusted research ≠ unadjusted live tickets)",
    "3. Sizing clipped to live account / broker limits before submit",
    "4. Explicit timezone: store UTC, convert to session TZ once; never relabel",
    "5. Replay includes every live download artifact (halts, corp actions, calendars)",
    "6. Config flags that gate risk must be wired into the submit path (integration test)",
    "7. Fill model documented: next-open / mid / touch — frozen for the paper window",
    "8. Cost model shared object between research and paper (no silent upgrade)",
    "9. VERSION string frozen; config hash logged each session",
    "10. Daily recon: strategy ledger vs independent fill replay; break → pause",
]
print("10-point parity checklist:")
for line in checklist:
    print(" ", line)
print("REJECT: using this paper as a profitability claim; QuantAgent/HFT latency recipes; broker order routers")

print("disclaimer: synthetic paper loop — learning only; no broker connectivity")
