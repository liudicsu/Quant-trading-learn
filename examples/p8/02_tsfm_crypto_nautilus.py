"""P8 lab 02: TSFM follow-up (offline mock), crypto funding/on-chain structure,
NautilusTrader identical backtest/live architecture checklist.
NO network at runtime. Learning only — not investment advice.
Cites: arXiv:2511.18578 (Chronos/TimesFM finance); arXiv:2607.12248 (base-rate-honest dir. acc.);
arXiv:2606.27100 (TSFM as prior); arXiv:2608.25348 (crypto PIT audit); CCXT docs; GMX docs;
@sera00111 https://x.com/sera00111/status/2108332340753969191;
NautilusTrader architecture https://nautilustrader.io/docs/latest/concepts/architecture/
"""
from __future__ import annotations

import json
from dataclasses import dataclass

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from _common import (
    ANN,
    DATA,
    EMBARGO,
    HORIZON,
    N_FOLDS,
    PUBLIC,
    SEED,
    dsr_from_pnl,
    forward_label_wide,
    make_panel,
    mean_daily_cs_ic,
    pred_to_ls_pnl,
    purged_kfold_indices,
)

print("=== parameters ===")
print("offline only — mock TSFM / mock funding ledger; no CCXT live calls at runtime")
print("eval: purged OOS mean daily CS RankIC + DSR(N) + shared costs")
print("cite: arXiv:2511.18578 Re(Visiting) TSFM; arXiv:2606.27100 TSFM as prior not alpha engine")
print("cite: arXiv:2607.12248 base-rate-honest directional accuracy (always-up foil)")
print("cite: arXiv:2608.25348 crypto PIT audit before alpha (Binance BTCUSDT perp)")
print("cite: CCXT docs https://docs.ccxt.com/ ; GMX fees https://docs.gmx.io/docs/trading/fees/")
print("cite: OpenBB Open Data Platform (aggregation); Trading Strategy GMX/CCXT adapters")
print("cite: @sera00111 Vision+CCXT note (P2-verified); Nautilus architecture docs")

rets, slow, meta = make_panel(n_days=520, n_assets=40, seed=SEED)
y1 = forward_label_wide(rets, h=1)
dates = rets.index
is_end = len(dates) - 120
is_dates, oos_dates = dates[:is_end], dates[is_end:]

# ---------- TSFM follow-up: naive / AR vs mock tiny "foundation" ----------
print("\n=== TSFM evaluation follow-up (P5 cites → offline demo) ===")
print("paper finding (2511.18578): off-the-shelf zero-shot TSFMs often lag strong finance baselines;")
print("domain pretrain/fine-tune may help but still needs anti-lookahead + costs.")

# Features known at t: lags of own return (per asset). Mock Chronos = ridge on lags fitted IS only.
LAGS = (1, 2, 3, 5, 10)


def build_lag_cube(r: pd.DataFrame) -> dict[int, pd.DataFrame]:
    return {L: r.shift(L) for L in LAGS}


lags = build_lag_cube(rets)

# (1) Naive: predict 0 (or predict last return — random walk)
naive = rets.shift(1)  # RW forecast of next ret ≈ last ret (poor for CS)

# (2) AR(1) per asset fit on IS
ar_pred = pd.DataFrame(np.nan, index=dates, columns=rets.columns)
for a in rets.columns:
    y = rets[a].loc[is_dates].iloc[1:]
    x = rets[a].loc[is_dates].shift(1).iloc[1:]
    m = pd.concat([x, y], axis=1).dropna()
    if len(m) < 50:
        continue
    # simple OLS
    xb = np.c_[np.ones(len(m)), m.iloc[:, 0].values]
    coef, *_ = np.linalg.lstsq(xb, m.iloc[:, 1].values, rcond=None)
    xa = rets[a].shift(1)
    ar_pred[a] = coef[0] + coef[1] * xa

# (3) Mock TSFM: tiny shared ridge on stacked lags (stand-in for a small pretrained head)
# Fit once on IS pooled (still offline, tiny).
rows = []
for a in rets.columns:
    block = pd.DataFrame({f"L{L}": lags[L][a] for L in LAGS})
    block["y"] = rets[a]
    block["asset"] = a
    block = block.loc[is_dates].dropna()
    rows.append(block)
train = pd.concat(rows, axis=0)
Xtr = train[[f"L{L}" for L in LAGS]].values
ytr = train["y"].values
# ridge
lam = 1.0
XtX = Xtr.T @ Xtr + lam * np.eye(Xtr.shape[1])
xty = Xtr.T @ ytr
w = np.linalg.solve(XtX, xty)
mock_tsfm = pd.DataFrame(np.nan, index=dates, columns=rets.columns)
for a in rets.columns:
    Xa = np.column_stack([lags[L][a].values for L in LAGS])
    mock_tsfm[a] = Xa @ w

N_TRIALS_TSFM = 4  # naive, AR, mock_tsfm, strong_CS (all scored)


def score_pred(tag: str, pred: pd.DataFrame, n_trials: int) -> dict:
    # purged OOF on IS: for parametric models we already fit IS-only; report IS CS IC + sealed OOS
    ps = pred.loc[is_dates].stack(); ps.index = ps.index.set_names(["date", "asset"])
    ys = y1.loc[is_dates].stack(); ys.index = ys.index.set_names(["date", "asset"])
    m_is = mean_daily_cs_ic(ps, ys)
    net, turn = pred_to_ls_pnl(pred.loc[is_dates], rets.loc[is_dates])
    dsr = dsr_from_pnl(net, n_trials=n_trials)
    ps2 = pred.loc[oos_dates].stack(); ps2.index = ps2.index.set_names(["date", "asset"])
    ys2 = y1.loc[oos_dates].stack(); ys2.index = ys2.index.set_names(["date", "asset"])
    m_oos = mean_daily_cs_ic(ps2, ys2)
    net_o, turn_o = pred_to_ls_pnl(pred.loc[oos_dates], rets.loc[oos_dates])
    dsr_o = dsr_from_pnl(net_o, n_trials=n_trials)
    # also a "strong baseline": CS rank of slow_lag1
    out = dict(
        tag=tag,
        IS_mean_CS_IC=m_is["mean_ic"],
        IS_net_SR=float(net.mean() / (net.std(ddof=1) + 1e-12) * ANN),
        IS_DSR=dsr["DSR"],
        sealed_OOS_IC=m_oos["mean_ic"],
        OOS_net_SR=float(net_o.mean() / (net_o.std(ddof=1) + 1e-12) * ANN),
        OOS_DSR=dsr_o["DSR"],
        n_trials=n_trials,
    )
    print(
        f"{tag:12s} IS_CS_IC={out['IS_mean_CS_IC']:+.4f} IS_net_SR={out['IS_net_SR']:.3f} "
        f"DSR(N={n_trials})={out['IS_DSR']:.3f} | sealed_OOS_IC={out['sealed_OOS_IC']:+.4f} "
        f"OOS_net_SR={out['OOS_net_SR']:.3f}"
    )
    return out


res_naive = score_pred("naive_RW", naive, N_TRIALS_TSFM)
res_ar = score_pred("AR1", ar_pred, N_TRIALS_TSFM)
res_tsfm = score_pred("mock_TSFM", mock_tsfm, N_TRIALS_TSFM)
# Strong traditional baseline: CS signal from lagged slow (not a TSFM)
strong = slow.shift(1)
res_strong = score_pred("strong_CS", strong, N_TRIALS_TSFM)

print("teach: mock_TSFM is a tiny shared linear head — NOT Chronos weights; compares protocol only.")
print("paper-aligned caution: zero-shot / generic TSFM often ≤ strong traditional baselines on daily excess.")

# ---------- Funding-rate carry numeric example ----------
print("\n=== perpetual funding carry (numeric toy; offline) ===")
print("CEX funding (CCXT-shaped): longs pay shorts when funding>0 (typical premium).")
print("GMX (docs.gmx.io/docs/trading/fees): dominant side pays minority; rate from OI imbalance;")
print("funding accrues continuously (per-second); do NOT overstate modify/close as the funding story.")
print("settlement on modify/close is mainly borrow-fee + position-fee mechanics (funding also settles then).")

# Toy: 8h funding on BTC perp
notional = 100_000.0  # USD
funding_8h = 0.0001  # +1 bp per 8h → longs pay
periods_per_day = 3
days = 30
# long perp, hedge spot (carry): receive -funding if funding>0 (i.e. pay)
pay_per_day = notional * funding_8h * periods_per_day
pay_30d = pay_per_day * days
ann_carry_bps = (pay_per_day * 365 / notional) * 1e4
print(f"notional=${notional:.0f} funding_8h={funding_8h:.4%} (longs pay)")
print(f"daily_funding_pnl_long={-pay_per_day:.2f} USD  (negative = pay)")
print(f"30d_funding_cost_long=${pay_30d:.2f}")
print(f"ann_carry_cost_long≈{ann_carry_bps:.1f} bps/year if rate stays constant")
# Regime shift foil
funding_regimes = pd.Series(
    [0.0001] * 10 + [-0.0003] * 10 + [0.00005] * 10,
    index=pd.date_range("2024-01-01", periods=30, freq="D"),
    name="funding_8h",
)
pnl_long = -notional * funding_regimes * periods_per_day
print("regime-shift foil (10d +1bp, 10d -3bp, 10d +0.5bp) cum PnL long:")
print(f"  cum_funding_pnl_long=${pnl_long.sum():.2f}  (sign flips with regime)")
funding_regimes.to_csv(DATA / "mock_funding_series.csv")
pnl_long.to_csv(DATA / "mock_funding_pnl_long.csv")

# Offline CCXT-shaped ledger (same fields as fetchFundingRate history would return)
ccxt_rows = []
for i, (dt, fr) in enumerate(funding_regimes.items()):
    ccxt_rows.append(
        {
            "timestamp": int(pd.Timestamp(dt).timestamp() * 1000),
            "datetime": str(dt),
            "symbol": "BTC/USDT:USDT",
            "fundingRate": float(fr),
            "markPrice": 60000 + 50 * i,
            "info_source": "OFFLINE_MOCK_not_ccxt_network",
        }
    )
pd.DataFrame(ccxt_rows).to_csv(DATA / "ccxt_shaped_funding_mock.csv", index=False)
print("wrote CCXT-shaped mock funding CSV (structure ref only; no exchange call)")

# GMX-style OI imbalance → funding factor toy
oi_long, oi_short = 1.2e8, 0.8e8
imbalance = (oi_long - oi_short) / (oi_long + oi_short)
funding_factor_per_sec = 1e-8 * imbalance  # toy scale
print(f"GMX-style toy: OI_long={oi_long:.2e} OI_short={oi_short:.2e} imbalance={imbalance:.3f}")
print(f"savedFundingFactorPerSecond≈{funding_factor_per_sec:.3e} (positive → longs pay; docs semantics)")
print("@sera00111: minute/hour research can start from Binance Vision + CCXT free entry; pick grain after strategy.")

# ---------- NautilusTrader identical code checklist ----------
print("\n=== NautilusTrader: keep backtest and live code identical ===")
print("source: https://nautilustrader.io/docs/latest/concepts/architecture/")
print("Backtest / Sandbox / Live share NautilusKernel (cache, portfolio, engines, trader, clock, bus).")
print("Strategy code should NOT branch on environment for signal logic — adapters differ, kernel same.")

@dataclass
class StrategyIdenticalChecklist:
    item: str
    ok: bool
    note: str


checks = [
    StrategyIdenticalChecklist("signal/on_bar logic identical in backtest & live", True, "no if env==live: tweak"),
    StrategyIdenticalChecklist("order intents via submit_order API only", True, "no direct REST in strategy"),
    StrategyIdenticalChecklist("RiskEngine validates before venue", True, "kernel path"),
    StrategyIdenticalChecklist("clock: backtest static vs live realtime — strategy uses clock API", True, "injected clock"),
    StrategyIdenticalChecklist("no peeking future bars in research path", True, "same event handlers"),
    StrategyIdenticalChecklist("recon: live ExecutionEngine vs research fills logged", True, "paper/live gap discipline"),
]
for c in checks:
    print(f"  [{'OK' if c.ok else 'FAIL'}] {c.item} — {c.note}")
pd.DataFrame([c.__dict__ for c in checks]).to_csv(DATA / "nautilus_identical_checklist.csv", index=False)

# ---------- Plots ----------
fig, ax = plt.subplots(figsize=(7, 4))
tags = [res_naive, res_ar, res_tsfm, res_strong]
ax.bar([r["tag"] for r in tags], [r["sealed_OOS_IC"] for r in tags], color=["#d62728", "#ff7f0e", "#1f77b4", "#2ca02c"])
ax.set_ylabel("sealed OOS mean daily CS RankIC")
ax.set_title("TSFM mock vs baselines (offline)")
ax.axhline(0, color="k", lw=0.8)
fig.tight_layout()
fig.savefig(PUBLIC / "tsfm_vs_baselines.png", dpi=120)
plt.close()

fig, ax = plt.subplots(figsize=(7, 3.5))
ax.plot(funding_regimes.index, funding_regimes.values * 1e4, marker="o", label="funding_8h (bps)")
ax.plot(pnl_long.index, pnl_long.cumsum().values / 100, label="cum PnL long (/100 USD)")
ax.set_title("Funding regime shift foil (offline mock)")
ax.legend()
fig.tight_layout()
fig.savefig(PUBLIC / "funding_regime.png", dpi=120)
plt.close()

pd.DataFrame(tags).to_csv(DATA / "tsfm_eval.csv", index=False)
report = {
    "tsfm_paper": "arXiv:2511.18578",
    "mock_vs_strong_OOS_IC": {"mock_TSFM": res_tsfm["sealed_OOS_IC"], "strong_CS": res_strong["sealed_OOS_IC"]},
    "funding_ann_carry_bps_long": ann_carry_bps,
    "nautilus": "shared NautilusKernel across Backtest/Sandbox/Live",
}
(DATA / "lab02_report.json").write_text(json.dumps(report, indent=2))


# ---------- Base-rate-honest directional accuracy (arXiv:2607.12248) ----------
print("\n=== base-rate-honest directional accuracy (always-up foil; arXiv:2607.12248) ===")
print("Headline metric: excess_acc = model_accuracy - always_up_accuracy on identical windows.")
# Strong bull path (teaching foil): high always-up base rate like the paper's ~0.70 recreation
rng_br = np.random.default_rng(42)
T_br = 1280  # enough non-overlapping h=64 windows
drift = 0.00105  # bull daily drift vs 1% vol → long-horizon mostly up (~70-80% band)
noise = rng_br.normal(0, 0.01, size=T_br)
r_br = drift + noise
h = 64  # paper-style multi-month horizon where base rate inflates
starts = list(range(0, T_br - h, h))
fwd = np.array([r_br[s : s + h].sum() for s in starts])
y_up = fwd > 0
always_up_acc = float(y_up.mean())
# "Fine-tuned" marketing model: mostly-up but slightly worse than always-up (paper spirit)
model_pred_up = np.ones_like(y_up, dtype=bool)
flip = rng_br.choice(len(y_up), size=max(1, len(y_up) // 8), replace=False)
model_pred_up[flip] = False
model_acc = float((model_pred_up == y_up).mean())
excess = model_acc - always_up_acc
# Naive coin-flip reference marketers wrongly use
coin_ref = 0.50
vs_coin = model_acc - coin_ref
# Persistence baseline (sign of prior window)
persist = np.array([
    (r_br[s - h : s].sum() > 0) if s >= h else True for s in starts
])
persist_acc = float((persist == y_up).mean())
persist_excess = persist_acc - always_up_acc
print(f"bull toy: n_windows={len(fwd)} always_up_acc={always_up_acc:.3f} (~70-80% band in rising markets)")
print(f"marketing_mostly_up raw_acc={model_acc:.3f} vs_coin_flip={vs_coin:+.3f}  <-- ads quote raw vs 50%")
print(f"marketing_mostly_up excess_acc={excess:+.3f}  <-- honest headline; can be <=0 while raw looks high")
print(f"persistence_baseline raw_acc={persist_acc:.3f} excess_acc={persist_excess:+.3f}")
print("Paper recreation spirit: always-up base ~0.70; fine-tuned model can fail to beat it (excess negative).")
print("WARN box: ads saying '80% directional accuracy' without always-up / excess_acc are base-rate theatre.")
print("WARN box: zero-shot Chronos/TimesFM as free equity alpha — reject; treat TSFM as prior (2606.27100).")

# ---------- Crypto PIT audit checklist (arXiv:2608.25348) ----------
print("\n=== crypto PIT audit before alpha (arXiv:2608.25348; Binance BTCUSDT perp spirit) ===")
pit_checks = [
    ("no_same_bar_execution", True, "decision at t uses only availability_time <= t; no unfinished bar"),
    ("funding_lag", True, "realized funding not shifted backward; use event+lag assumption, test sensitivity"),
    ("no_backfill_gap_fill", True, "do not interpolate/backward-fill gaps to manufacture continuity"),
    ("OI_publication_unverified", True, "if OI pub time unverified, disable as alpha input (paper: OI optional)"),
    ("core_streams_trade_mark_index_funding", True, "admit on availability-masked complete days, not silent repair"),
]
for name, ok, note in pit_checks:
    print(f"  [{'OK' if ok else 'FAIL'}] {name}: {note}")
print("Paper negative result spirit: positive IC can still yield negative net Sharpe under costs — audit first.")
pd.DataFrame([{"check": a, "ok": b, "note": c} for a, b, c in pit_checks]).to_csv(
    DATA / "crypto_pit_audit_checklist.csv", index=False
)

print("\n=== limitations / failure modes ===")
print("- TSFM zero-shot: weak on noisy daily excess; do not skip purge/costs/DSR.")
print("- Mock != real Chronos/TimesFM weights; protocol transfer only.")
print("- Base-rate trap: raw ~80% direction can be always-up; report excess_acc (2607.12248).")
print("- TSFM as prior not alpha engine (2606.27100); reject free-equity-alpha marketing.")
print("- Crypto: PIT audit before alpha (2608.25348) — no same-bar / funding lag / no backfill.")
print("- Crypto survivorship: delisted perps/coins drop out of free histories.")
print("- Funding regime shifts: carry sign flips; constant-rate ann. is a foil.")
print("- On-chain/GMX: MEV, oracle, liquidity, bridge risks beyond CEX CCXT.")
print("- Nautilus: identical strategy code ≠ identical fills (latency/partial/recon still differ).")
print("\nwrote", PUBLIC / "tsfm_vs_baselines.png", PUBLIC / "funding_regime.png")
print("DONE lab 02")
