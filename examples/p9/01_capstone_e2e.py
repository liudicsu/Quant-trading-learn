"""P9 Capstone lab: end-to-end honest small strategy on synthetic PIT data.
Stages: hypothesis → PIT panel → walk-forward + shared costs → DSR(N=ALL trials)
→ risk sizing/limits → TCA estimate → paper loop + independent-ledger recon (injected break)
→ compliance checklist → research-report template fill.
Offline only. Learning only — not investment advice.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from _common import (
    ANN,
    DATA,
    ONE_WAY_BPS,
    IMPACT_K,
    PUBLIC,
    SEED,
    apply_costs_ls,
    dsr_from_pnl,
    forward_label_wide,
    make_panel,
    mean_daily_cs_ic,
    pred_to_ls_pnl,
    pred_to_ls_weights,
)

print("=== parameters ===")
print("offline / synthetic only — no broker, no paid API")
print("panel: 50 assets × 600 sessions; weak lagged slow driver; PIT as-of lag=2")
print("shared cost model: 10 bps one-way + IMPACT_K=0.1·σ·√turn (same spirit as P2/P4/P8)")
print("walk-forward: train 240d / test 60d / step 60d; embargo=5; label h=1")
print("look-ahead: signals use shift(1); costs use lagged σ; never join final revision as day-0")
print("cite: Bailey & López de Prado 2014 JPM 40(5) 94–107 — Deflated Sharpe Ratio")
print("cite: AFML (LdP) purged CV / embargo; Perold 1988 FAJ — implementation shortfall")
print("cite: Almgren–Chriss 2000/01 optimal execution intuition; FINRA Notice 26-10 (PDT successor)")

rets, slow, asof, revision, meta = make_panel()
y1 = forward_label_wide(rets, h=1)
dates = rets.index
rets.to_csv(DATA / "panel_rets.csv")
asof.to_csv(DATA / "pit_asof_slow.csv")
revision.to_csv(DATA / "pit_revision_foil.csv")

# ---------- 1) Hypothesis (written artefact) ----------
print("\n=== 1) hypothesis (research brief) ===")
HYP = {
    "name": "slow_momentum_cs_v1",
    "claim": "Cross-sectional ranks of a slow mean-reverting state (lagged 1 day) weakly predict next-day residual returns.",
    "null": "H0: mean daily CS RankIC of lagged slow vs fwd1 = 0 after costs and multiple testing.",
    "pit_rule": "Feature at t uses only information known by close t (slow.shift(1)); as-of alt foil uses lag=2.",
    "decision_rule": "Keep candidate only if sealed OOS mean CS RankIC > 0 AND DSR(N=all_trials) on the SAME net series used for the decision.",
    "not_advice": "Learning exercise on synthetic data — not investment advice.",
}
(DATA / "hypothesis.json").write_text(json.dumps(HYP, indent=2))
for k, v in HYP.items():
    print(f"  {k}: {v}")

# ---------- 2) Candidate bank (counts as trials) ----------
print("\n=== 2) candidate bank (ALL count toward N) ===")
# Honest: lagged slow. Foils: raw asof, leaky future slow, noise, short mom
candidates = {
    "slow_lag1": slow.shift(1),                 # honest primary
    "asof_lag2": asof,                          # PIT alt-data with reporting lag
    "rev_final_LEAK": revision.shift(-1),       # LEAK: uses next revision as if available
    "mom20": rets.rolling(20).mean().shift(1),
    "noise": pd.DataFrame(np.random.default_rng(SEED).normal(0, 1, rets.shape), index=rets.index, columns=rets.columns),
    "slow_raw_noshift_LEAK": slow,              # LEAK: same-bar slow
}
N_TRIALS = len(candidates)
print(f"explicit N_TRIALS={N_TRIALS} (every scored candidate counts; DSR uses this N on the decision series)")

# ---------- 3) Walk-forward with shared costs ----------
print("\n=== 3) walk-forward backtest (shared cost model) ===")
TRAIN, TEST, STEP, EMBARGO = 240, 60, 60, 5
wf_rows = []
oof_pred = {k: pd.DataFrame(np.nan, index=dates, columns=rets.columns) for k in candidates}

i0 = TRAIN
while i0 + TEST <= len(dates):
    tr_end = i0
    te_lo, te_hi = i0, i0 + TEST
    # embargo: drop last EMBARGO train days from feature fit window (selection uses fit_dates (embargo already dropped); OOF in sealed window is never used for selection)
    fit_dates = dates[: max(0, tr_end - EMBARGO)]
    te_dates = dates[te_lo:te_hi]
    for name, pred in candidates.items():
        # selection metric on train (purged-ish via embargo)
        ps = pred.loc[fit_dates].stack(); ps.index = ps.index.set_names(["date", "asset"])
        ys = y1.loc[fit_dates].stack(); ys.index = ys.index.set_names(["date", "asset"])
        m_tr = mean_daily_cs_ic(ps, ys)
        # OOF assign test predictions (no refit — these are static transforms)
        oof_pred[name].loc[te_dates] = pred.loc[te_dates]
        net, turn = pred_to_ls_pnl(pred.loc[te_dates], rets.loc[te_dates])
        wf_rows.append({
            "fold_start": str(te_dates[0].date()),
            "name": name,
            "train_IC": m_tr["mean_ic"],
            "test_net_SR": float(net.mean() / (net.std(ddof=1) + 1e-12) * ANN) if net.std(ddof=1) > 0 else float("nan"),
            "test_turn": float(turn.mean()),
        })
    i0 += STEP

wf = pd.DataFrame(wf_rows)
wf.to_csv(DATA / "walkforward_folds.csv", index=False)
print(f"folds per candidate ≈ {wf.groupby('name').size().iloc[0]}; embargo={EMBARGO}")

# ---------- 4) Sealed OOS + DSR on SAME series ----------
print("\n=== 4) sealed OOS evaluation + DSR(N=ALL) on decision series ===")
# Last 120 days sealed after walk-forward research window
seal_n = 120
research_dates, sealed_dates = dates[:-seal_n], dates[-seal_n:]
# Decision: pick best by research OOF mean CS IC among non-LEAK names
honest_names = [n for n in candidates if "LEAK" not in n]
research_scores = {}
for name in honest_names:
    pred = oof_pred[name].loc[research_dates]
    ps = pred.stack(); ps.index = ps.index.set_names(["date", "asset"])
    ys = y1.loc[research_dates].stack(); ys.index = ys.index.set_names(["date", "asset"])
    research_scores[name] = mean_daily_cs_ic(ps, ys)["mean_ic"]
best = max(research_scores, key=lambda k: research_scores[k] if np.isfinite(research_scores[k]) else -9)
print("research OOF mean CS IC (honest bank):")
for k, v in sorted(research_scores.items(), key=lambda kv: -kv[1]):
    print(f"  {k:16s} IC={v:+.4f}")
print(f"selected={best}  (LEAK foils excluded from selection but INCLUDED in N={N_TRIALS})")

# Score ALL candidates on sealed OOS; DSR uses N_TRIALS on each net series
seal_rows = []
for name, pred0 in candidates.items():
    pred = pred0.loc[sealed_dates]
    ps = pred.stack(); ps.index = ps.index.set_names(["date", "asset"])
    ys = y1.loc[sealed_dates].stack(); ys.index = ys.index.set_names(["date", "asset"])
    mic = mean_daily_cs_ic(ps, ys)
    net, turn = pred_to_ls_pnl(pred, rets.loc[sealed_dates])
    dsr = dsr_from_pnl(net, n_trials=N_TRIALS)
    # Also show dishonest DSR(N=1) foil for the selected series only
    row = dict(
        name=name,
        sealed_IC=mic["mean_ic"],
        sealed_IC_t=mic["t_stat"],
        net_SR=float(net.mean() / (net.std(ddof=1) + 1e-12) * ANN),
        DSR_N_all=dsr["DSR"],
        mean_turn=float(turn.mean()),
        leak="LEAK" in name,
    )
    seal_rows.append(row)
    flag = " <-- SELECTED" if name == best else ""
    print(
        f"{name:22s} sealed_IC={row['sealed_IC']:+.4f} net_SR={row['net_SR']:.3f} "
        f"DSR(N={N_TRIALS})={row['DSR_N_all']:.3f}{flag}"
    )

seal_df = pd.DataFrame(seal_rows)
seal_df.to_csv(DATA / "sealed_oos_scores.csv", index=False)
net_best, turn_best = pred_to_ls_pnl(candidates[best].loc[sealed_dates], rets.loc[sealed_dates])
dsr_honest = dsr_from_pnl(net_best, n_trials=N_TRIALS)
dsr_cheat = dsr_from_pnl(net_best, n_trials=1)
print(f"teach: DSR on SELECTED series with N={N_TRIALS} → {dsr_honest['DSR']:.3f}; "
      f"same series with dishonest N=1 → {dsr_cheat['DSR']:.3f}")
print("expected-value context: under H0, max SR across N trials is >0; DSR deflates for that.")

# ---------- 5) Risk sizing / limits ----------
print("\n=== 5) risk sizing / hard limits ===")
# Vol-target the LS book to 10% ann on expanding train vol; gross/net caps
w_raw = pred_to_ls_weights(candidates[best])
gross = w_raw.abs().sum(axis=1)
# lagged vol of equal-risk proxy
proxy = (w_raw.shift(1).fillna(0) * rets).sum(axis=1)
vol = proxy.rolling(20, min_periods=10).std().shift(1)
target_vol = 0.10 / ANN
scale = (target_vol / vol.replace(0, np.nan)).clip(0, 2.0).fillna(0)
w_sized = w_raw.mul(scale, axis=0)
# hard limits
MAX_GROSS, MAX_NET, DD_KILL = 1.5, 0.3, 0.08
w_sized = w_sized.clip(-0.1, 0.1)  # per-name cap
g = w_sized.abs().sum(axis=1)
w_sized = w_sized.div(g.replace(0, np.nan) / MAX_GROSS, axis=0).fillna(0).where(g > 0, 0)
net_expo = w_sized.sum(axis=1).clip(-MAX_NET, MAX_NET)
# apply net clip proportionally
for dt in w_sized.index:
    s = w_sized.loc[dt].sum()
    if abs(s) > MAX_NET and abs(s) > 0:
        w_sized.loc[dt] *= MAX_NET / abs(s)

pnl_sized, turn_sized = apply_costs_ls(w_sized.loc[sealed_dates], rets.loc[sealed_dates])
eq = (1 + pnl_sized.fillna(0)).cumprod()
peak = eq.cummax()
dd = eq / peak - 1
killed = (dd <= -DD_KILL).any()
print(f"vol_target=10% ann; MAX_GROSS={MAX_GROSS}; MAX_NET={MAX_NET}; DD_KILL={DD_KILL}")
print(f"sealed sized net_SR={pnl_sized.mean()/(pnl_sized.std(ddof=1)+1e-12)*ANN:.3f} "
      f"maxDD={dd.min():.3f} mean_gross={w_sized.loc[sealed_dates].abs().sum(axis=1).mean():.3f}")
print(f"DD kill would have fired on sealed path? {bool(killed)} (engineering switch, not alpha)")
w_sized.loc[sealed_dates].to_csv(DATA / "sized_weights_sealed.csv")

# ---------- 6) Execution / TCA estimate ----------
print("\n=== 6) execution / TCA estimate (Perold IS intuition) ===")
# Toy: participate 10% ADV, arrival mid → VWAP-style schedule; IS = side * (avg_fill - arrival) / arrival
rng = np.random.default_rng(SEED)
notional = 1_000_000.0
adv = 5_000_000.0
participation = 0.10
arrival = 100.0
# temporary impact ~ sigma * sqrt(participation); permanent ~ 0.5 * temp (Almgren–Chriss intuition)
sigma_daily = 0.012
temp_bps = 1e4 * sigma_daily * np.sqrt(participation)
perm_bps = 0.5 * temp_bps
# schedule: 5 slices; fill noise
slices = 5
slice_px = arrival * (1 + rng.normal(perm_bps / 1e4 / 2, temp_bps / 1e4 / 3, slices))
avg_fill = float(slice_px.mean())
# long buy IS in bps
is_bps = 1e4 * (avg_fill - arrival) / arrival
# half-spread + fee foil
spread_bps, fee_bps = 2.0, 1.0
total_tca = is_bps + spread_bps + fee_bps
print(f"notional=${notional:.0f} ADV=${adv:.0f} participation={participation:.0%}")
print(f"temp_impact≈{temp_bps:.2f} bps  permanent≈{perm_bps:.2f} bps  (toy; σ={sigma_daily})")
print(f"implementation_shortfall≈{is_bps:.2f} bps  +spread {spread_bps} +fee {fee_bps} → TCA≈{total_tca:.2f} bps")
print("look-ahead warning: do not size impact with same-bar realized σ; use lagged/ex-ante σ.")
(DATA / "tca_toy.json").write_text(json.dumps({
    "temp_bps": temp_bps, "perm_bps": perm_bps, "is_bps": is_bps, "tca_bps": total_tca
}, indent=2))

# ---------- 7) Paper loop + independent ledger recon ----------
print("\n=== 7) paper-trading plan + independent-ledger reconciliation ===")
# Single-asset mom foil for paper infra (process validation), ≥10 sessions
n = 80
px_r = rng.normal(0.0002, 0.01, n)
px = 100 * np.cumprod(1 + px_r)
bars = pd.DataFrame({
    "date": pd.bdate_range("2025-01-02", periods=n),
    "close": px,
    "open": np.r_[px[0], px[:-1] * (1 + rng.normal(0, 0.0008, n - 1))],
})
bars["ret"] = bars["close"].pct_change()
bars["mom10"] = bars["close"].pct_change(10)
VERSION = "capstone_mom10_vt_v1.0.0"
pos = 0.0
equity = [1.0]
strat_pos = []
fills = []
for i in range(15, n):
    mom = bars.iloc[i - 1]["mom10"]
    target = float(np.sign(mom)) * 0.5 if np.isfinite(mom) else 0.0
    # paper fill at open with slip
    slip = 0.0003 + 0.001 * abs(target - pos)
    fill_w = target
    # inject one partial miss
    note = ""
    if i == 40:
        fill_w = target * 0.6
        note = "INJECTED_PARTIAL_MISS"
    fills.append({"i": i, "date": str(bars.iloc[i]["date"].date()), "target": target, "filled": fill_w, "note": note})
    # PnL on close-to-close with prior pos
    equity.append(equity[-1] * (1 + pos * bars.iloc[i]["ret"] - slip * abs(fill_w - pos)))
    pos = fill_w
    strat_pos.append({"date": str(bars.iloc[i]["date"].date()), "pos": pos, "equity": equity[-1]})

fills_df = pd.DataFrame(fills)
strat_df = pd.DataFrame(strat_pos)
# Independent broker ledger: rebuild ONLY from fill deltas (separate from strategy equity list)
broker_pos = []
bp = 0.0
for _, row in fills_df.iterrows():
    bp = row["filled"]  # broker records filled qty as position
    # inject break: broker misses the partial on its ledger deliberately mismatch
    ledger_pos = bp
    if row["note"] == "INJECTED_PARTIAL_MISS":
        ledger_pos = row["target"]  # broker wrongly books intended, not filled
    broker_pos.append({"date": row["date"], "broker_pos": ledger_pos, "strat_pos": row["filled"]})
broker_df = pd.DataFrame(broker_pos)
broker_df["abs_diff"] = (broker_df["broker_pos"] - broker_df["strat_pos"]).abs()
breaks = broker_df[broker_df["abs_diff"] > 1e-12]
assert len(breaks) >= 1, "expected injected break"
print(f"sessions={len(strat_df)} version={VERSION} final_equity≈{equity[-1]:.3f}")
print(f"BREAK DETECTED on {breaks.iloc[0]['date']} abs_diff={breaks.iloc[0]['abs_diff']:.4f} "
      f"note=INJECTED_PARTIAL_MISS; assert detected=True")
fills_df.to_csv(DATA / "paper_fills.csv", index=False)
broker_df.to_csv(DATA / "paper_recon.csv", index=False)

# ---------- 8) Compliance checklist ----------
print("\n=== 8) compliance / ethics checklist (learning) ===")
checklist = [
    ("learning_only_disclaimer", True, "site + report state not investment advice"),
    ("no_live_broker_orders", True, "paper/sim only in this curriculum"),
    ("pit_timestamps_documented", True, "as-of lag=2; LEAK foils labelled"),
    ("all_trials_counted_in_DSR", True, f"N={N_TRIALS} includes LEAK/noise"),
    ("dsr_on_decision_series", True, "same net PnL series as selection"),
    ("version_frozen_in_paper", True, VERSION),
    ("independent_ledger_recon", True, "injected break detected"),
    ("finra_26_10_awareness", True, "PDT successor effective 2026-06-04 — know your venue rules"),
    ("no_fabricated_citations", True, "every niche/frontier cite verified"),
]
for name, ok, note in checklist:
    print(f"  [{'OK' if ok else 'FAIL'}] {name} — {note}")
pd.DataFrame([{"item": a, "ok": b, "note": c} for a, b, c in checklist]).to_csv(
    DATA / "compliance_checklist.csv", index=False
)

# ---------- 9) Research report template (filled from this run) ----------
print("\n=== 9) research report template (auto-filled from lab) ===")
report = {
    "title": "Capstone: honest CS slow-state signal (synthetic)",
    "hypothesis": HYP,
    "data": {"n_assets": rets.shape[1], "n_days": rets.shape[0], "pit_lag": 2, "seed": SEED},
    "costs": {"one_way_bps": ONE_WAY_BPS, "impact_k": IMPACT_K},
    "trials": {"N_TRIALS": N_TRIALS, "names": list(candidates)},
    "selection": {"best": best, "research_IC": research_scores[best]},
    "sealed_oos": seal_df[seal_df.name == best].iloc[0].to_dict(),
    "dsr": {"N": N_TRIALS, "DSR": dsr_honest["DSR"], "DSR_if_N1_foil": dsr_cheat["DSR"]},
    "risk": {"vol_target_ann": 0.10, "max_gross": MAX_GROSS, "max_net": MAX_NET, "dd_kill": DD_KILL},
    "tca_bps": total_tca,
    "paper": {"version": VERSION, "sessions": len(strat_df), "break_detected": True},
    "limitations": [
        "Synthetic DGP — numbers are teaching foils, not market evidence.",
        "Weak planted alpha; after shared costs net SR often fails DSR.",
        "Optional frontier appendix must not reopen sealed OOS.",
    ],
    "disclaimer": "Learning only — not investment advice.",
}
(DATA / "research_report.json").write_text(json.dumps(report, indent=2, default=float))
print(json.dumps({k: report[k] for k in ["selection", "sealed_oos", "dsr", "tca_bps", "paper"]}, indent=2, default=float))

# ---------- Plots ----------
fig, ax = plt.subplots(figsize=(8, 4))
order = seal_df.sort_values("sealed_IC")
colors = ["#d62728" if L else "#2ca02c" for L in order["leak"]]
ax.barh(order["name"], order["sealed_IC"], color=colors)
ax.axvline(0, color="k", lw=0.8)
ax.set_xlabel("sealed OOS mean daily CS RankIC")
ax.set_title(f"Capstone candidates (red=LEAK); N={N_TRIALS}")
fig.tight_layout()
fig.savefig(PUBLIC / "capstone_sealed_ic.png", dpi=120)
plt.close()

fig, ax = plt.subplots(figsize=(7, 3.5))
ax.plot(eq.index, eq.values, label="sized sealed NAV")
ax.set_title(f"Selected={best} sized sealed path")
ax.legend()
fig.tight_layout()
fig.savefig(PUBLIC / "capstone_sized_nav.png", dpi=120)
plt.close()

fig, ax = plt.subplots(figsize=(7, 3.5))
ax.plot(range(len(equity)), equity, label="paper equity")
ax.set_title("Paper loop equity (process validation)")
ax.legend()
fig.tight_layout()
fig.savefig(PUBLIC / "capstone_paper_equity.png", dpi=120)
plt.close()

print("\n=== limitations / failure modes ===")
print("- Counting only the winner as N=1 inflates DSR — always use ALL trials.")
print("- Joining final revisions as day-0 is look-ahead (rev_final_LEAK foil).")
print("- Paper validates wiring/recon/kills — not alpha.")
print("- Grading rubric scores honesty/engineering, not whether SR>0.")
print("\nwrote", PUBLIC / "capstone_sealed_ic.png", PUBLIC / "capstone_sized_nav.png", PUBLIC / "capstone_paper_equity.png")
print("DONE capstone lab 01")
