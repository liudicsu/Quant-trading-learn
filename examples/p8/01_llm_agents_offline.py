"""P8 lab 01: offline mock of LLM/agent factor mining + LLM sentiment.
NO paid API, NO network at runtime — mocks only.
Sources (read offline for the lesson text): RD-Agent(Q) arXiv:2505.15155;
Chain-of-Alpha arXiv:2508.06312 (WITHDRAWN — caution only); Lopez-Lira & Tang
arXiv:2304.07619; LLM+MCTS arXiv:2505.11122; Quant-Arena arXiv:2610.30113.
Learning only — not investment advice.
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
print("offline mocks only — no LLM API, no network at runtime")
print("eval: purged OOS mean daily CS RankIC + DSR(N) + shared 10bps+impact costs")
print("cite: RD-Agent(Q) arXiv:2505.15155; Lopez-Lira&Tang arXiv:2304.07619")
print("cite: LLM+MCTS arXiv:2505.11122; Quant-Arena arXiv:2610.30113")
print("cite look-ahead/memorization critiques: Glasserman&Lin arXiv:2309.17322; Lopez-Lira/Tang/Zhu arXiv:2504.14765")
print("Chain-of-Alpha arXiv:2508.06312 — EXISTS but WITHDRAWN (arXiv: withdrawn by Lang Cao); drop detailed claims")

rets, slow, meta = make_panel()
y1 = forward_label_wide(rets, h=1)
mom5 = rets.rolling(5).sum()
mom20 = rets.rolling(20).sum()
vol20 = rets.rolling(20).std(ddof=1)
rev5 = -mom5
# "oracle-ish" slow feature known with lag 1 (as of t uses slow[t] which drove ret[t+1] weakly)
feat_bank = {
    "mom5": mom5,
    "mom20": mom20,
    "rev5": rev5,
    "vol20": -vol20,  # low-vol tilt toy
    "slow_lag1": slow.shift(1),  # weak true driver
    "noise_A": pd.DataFrame(np.random.default_rng(1).normal(size=rets.shape), index=rets.index, columns=rets.columns),
    "noise_B": pd.DataFrame(np.random.default_rng(2).normal(size=rets.shape), index=rets.index, columns=rets.columns),
    "mom5_x_vol": mom5 / (vol20 + 1e-6),
}

# ---------- Mock RD-Agent(Q): Research → Development → evaluate loop ----------
print("\n=== mock RD-Agent(Q) loop (Research → Development → Co-STEER-style keep/reject) ===")
print("real paper: Research sets goal-aligned prompts/hypotheses; Development implements;")
print("factor–model co-optimization with iterative feedback (NeurIPS 2025 / arXiv:2505.15155).")
print("here: a formula bank stands in for LLM proposals; bandit keeps top by IS IC (danger!).")

rng = np.random.default_rng(SEED)
dates = rets.index
# IS window vs sealed OOS year-like holdout (last ~120 sessions)
n = len(dates)
is_end = n - 120
is_dates = dates[:is_end]
oos_dates = dates[is_end:]
print(f"IS days={len(is_dates)} sealed_OOS days={len(oos_dates)} (freeze then open once)")


@dataclass
class Proposal:
    name: str
    formula: str
    is_ic: float
    kept: bool
    reason: str


proposals: list[Proposal] = []
# Mock "LLM" proposes in rounds; Development "implements" by looking up formula bank
rounds = [
    [("mom5", "rolling_sum(ret,5)"), ("noise_A", "gaussian_noise()"), ("rev5", "-rolling_sum(ret,5)")],
    [("mom20", "rolling_sum(ret,20)"), ("slow_lag1", "lag(slow,1)"), ("vol20", "-rolling_std(ret,20)")],
    [("mom5_x_vol", "mom5/(vol20+eps)"), ("noise_B", "gaussian_noise()")],
]

kept_names: list[str] = []
N_TRIALS_AGENT = 0  # explicit N for DSR later

for r_i, batch in enumerate(rounds, 1):
    print(f"\n-- Research round {r_i}: mock LLM proposes {len(batch)} hypotheses --")
    for name, formula in batch:
        N_TRIALS_AGENT += 1
        f = feat_bank[name].loc[is_dates]
        y = y1.loc[is_dates]
        # stack to series for IC
        pred = f.stack(); pred.index = pred.index.set_names(["date", "asset"])
        yy = y.stack(); yy.index = yy.index.set_names(["date", "asset"])
        m = mean_daily_cs_ic(pred, yy)
        # Co-STEER-style: keep if mean IC > 0.01 on IS (overfit trap intentionally)
        keep = bool(m["mean_ic"] > 0.01)
        reason = "keep_IS_ic>0.01" if keep else "reject_weak_IS"
        if keep:
            kept_names.append(name)
        proposals.append(Proposal(name, formula, float(m["mean_ic"]), keep, reason))
        print(f"  propose {name:12s} IS_mean_CS_IC={m['mean_ic']:+.4f} t={m['t_stat']:.2f} → {reason}")

print(f"\nkept factors after agent loop: {kept_names}")
print(f"explicit trial count N_TRIALS_AGENT={N_TRIALS_AGENT} (for DSR)")

# Combine kept factors (equal-weight z) on full sample, evaluate purged OOS + sealed
def combine(names: list[str]) -> pd.DataFrame:
    if not names:
        return pd.DataFrame(0.0, index=rets.index, columns=rets.columns)
    zs = []
    for nm in names:
        x = feat_bank[nm]
        mu = x.mean(axis=1)
        sd = x.std(axis=1, ddof=1).replace(0, np.nan)
        zs.append(x.sub(mu, axis=0).div(sd, axis=0))
    return sum(zs) / len(zs)


combo_is_selected = combine(kept_names)
# foil: "honest" factor = only slow_lag1
combo_honest = combine(["slow_lag1"])

print("\n=== purged / sealed OOS evaluation (same framework as P4/P5) ===")


def eval_factor(name: str, pred_wide: pd.DataFrame, n_trials: int) -> dict:
    # purged K-fold OOF on IS only, then sealed OOS once
    folds = purged_kfold_indices(is_dates, N_FOLDS, HORIZON, EMBARGO)
    oof = pd.DataFrame(np.nan, index=is_dates, columns=rets.columns)
    for tr_d, te_d in folds:
        # factor is non-parametric here — just use values on test (no fit); teach purge still
        oof.loc[te_d] = pred_wide.loc[te_d]
    pred_s = oof.stack(); pred_s.index = pred_s.index.set_names(["date", "asset"])
    y_s = y1.loc[is_dates].stack(); y_s.index = y_s.index.set_names(["date", "asset"])
    m_oof = mean_daily_cs_ic(pred_s, y_s)
    net, turn = pred_to_ls_pnl(pred_wide.loc[is_dates], rets.loc[is_dates])
    dsr = dsr_from_pnl(net, n_trials=n_trials)
    # sealed OOS
    pred_oos = pred_wide.loc[oos_dates]
    ps = pred_oos.stack(); ps.index = ps.index.set_names(["date", "asset"])
    ys = y1.loc[oos_dates].stack(); ys.index = ys.index.set_names(["date", "asset"])
    m_oos = mean_daily_cs_ic(ps, ys)
    net_oos, turn_oos = pred_to_ls_pnl(pred_oos, rets.loc[oos_dates])
    dsr_oos = dsr_from_pnl(net_oos, n_trials=n_trials)
    out = {
        "name": name,
        "purged_OOF_mean_CS_IC": m_oof["mean_ic"],
        "purged_OOF_t": m_oof["t_stat"],
        "IS_net_SR": float(net.mean() / (net.std(ddof=1) + 1e-12) * ANN),
        "IS_DSR": dsr["DSR"],
        "IS_SR_star": dsr["SR_star"],
        "n_trials": n_trials,
        "sealed_OOS_mean_CS_IC": m_oos["mean_ic"],
        "sealed_OOS_t": m_oos["t_stat"],
        "sealed_OOS_net_SR": float(net_oos.mean() / (net_oos.std(ddof=1) + 1e-12) * ANN),
        "sealed_OOS_DSR": dsr_oos["DSR"],
        "IS_turn": float(turn.mean()),
        "OOS_turn": float(turn_oos.mean()),
    }
    print(
        f"{name:16s} purged_OOF_IC={out['purged_OOF_mean_CS_IC']:+.4f} "
        f"IS_net_SR={out['IS_net_SR']:.3f} DSR(N={n_trials})={out['IS_DSR']:.3f} "
        f"| sealed_OOS_IC={out['sealed_OOS_mean_CS_IC']:+.4f} "
        f"OOS_net_SR={out['sealed_OOS_net_SR']:.3f} OOS_DSR={out['sealed_OOS_DSR']:.3f}"
    )
    return out


res_agent = eval_factor("agent_kept", combo_is_selected, N_TRIALS_AGENT)
res_honest = eval_factor("honest_slow", combo_honest, 1)

# Quant-Arena spirit: freeze selection, open sealed year once
print("\n=== Quant-Arena spirit (arXiv:2610.30113) ===")
print("freeze factor list AFTER IS loop; evaluate sealed hold-out ONCE; no peeking / re-mining.")
print(f"frozen_kept={kept_names}")
print(f"sealed_OOS_IC agent={res_agent['sealed_OOS_mean_CS_IC']:+.4f} vs honest={res_honest['sealed_OOS_mean_CS_IC']:+.4f}")

# ---------- Mock Lopez-Lira & Tang sentiment ----------
print("\n=== mock Lopez-Lira & Tang (2023) headline sentiment (offline) ===")
print("paper: GPT scores on post-knowledge-cutoff headlines predict reactions/drift (arXiv:2304.07619).")
print("here: synthetic 'headlines' → mock_sentiment in [-1,1]; NO ChatGPT call.")

# Build mock news: each day, each asset gets a score correlated weakly with next ret + noise
# Post-cutoff foil: only use dates after a fake cutoff index
CUTOFF = dates[200]
rng2 = np.random.default_rng(11)
sent = pd.DataFrame(rng2.normal(0, 1, size=rets.shape), index=dates, columns=rets.columns)
# inject weak true signal from next-day residual direction (LOOK-AHEAD if we used y1 unshifted — don't)
# Use lag: sentiment at t correlates with slow_lag1 (available) + noise — tradable foil
sent = 0.3 * slow.shift(1).fillna(0) + 0.7 * sent
sent = sent.clip(-3, 3) / 3.0  # mock GPT score in approx [-1,1]
# Look-ahead FOIL: corrupted sentiment that peeks at next return (training-cutoff / memorization analogue)
sent_leak = sent.copy()
sent_leak.loc[:, :] = (sent_leak.values + 0.5 * np.sign(y1.fillna(0).values))
sent_leak = sent_leak.clip(-1, 1)

post = dates[dates > CUTOFF]
for tag, S in [("mock_sentiment_PIT", sent), ("mock_sentiment_LEAK", sent_leak)]:
    ps = S.loc[post].stack(); ps.index = ps.index.set_names(["date", "asset"])
    ys = y1.loc[post].stack(); ys.index = ys.index.set_names(["date", "asset"])
    m = mean_daily_cs_ic(ps, ys)
    net, turn = pred_to_ls_pnl(S.loc[post], rets.loc[post])
    dsr = dsr_from_pnl(net, n_trials=2)
    print(
        f"{tag:22s} post_cutoff mean_CS_IC={m['mean_ic']:+.4f} t={m['t_stat']:.2f} "
        f"net_SR={float(net.mean()/(net.std(ddof=1)+1e-12)*ANN):.3f} DSR(N=2)={dsr['DSR']:.3f}"
    )

print("teach: LEAK foil inflates IC (cutoff/memorization analogue); PIT mock is the honest path.")

# ---------- Chain-of-Alpha note ----------
print("\n=== Chain-of-Alpha (arXiv:2508.06312) — WITHDRAWN ===")
print("Verified on arXiv: entry exists but is withdrawn (banner: withdrawn by Lang Cao).")
print("DROP detailed dual-chain claims; do not depend on an unstable PDF.")
print("Prefer stable cites: RD-Agent(Q), LLM+MCTS (2505.11122), Quant-Arena (2610.30113).")

# ---------- Plots + exports ----------
fig, ax = plt.subplots(figsize=(8, 4))
names = [p.name for p in proposals]
ics = [p.is_ic for p in proposals]
colors = ["#2ca02c" if p.kept else "#d62728" for p in proposals]
ax.bar(names, ics, color=colors)
ax.axhline(0.01, color="gray", ls="--", lw=1, label="IS keep threshold")
ax.set_ylabel("IS mean daily CS RankIC")
ax.set_title("Mock RD-Agent proposals (green=kept)")
ax.tick_params(axis="x", rotation=45)
ax.legend()
fig.tight_layout()
fig.savefig(PUBLIC / "rdagent_proposals.png", dpi=120)
plt.close()

# NAV foil
net_a, _ = pred_to_ls_pnl(combo_is_selected, rets)
net_h, _ = pred_to_ls_pnl(combo_honest, rets)
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot((1 + net_a.fillna(0)).cumprod(), label="agent_kept (net)")
ax.plot((1 + net_h.fillna(0)).cumprod(), label="honest_slow (net)")
ax.axvline(is_dates[-1], color="k", ls=":", label="sealed OOS start")
ax.set_title("Mock agent vs honest factor NAV (shared costs)")
ax.legend()
fig.tight_layout()
fig.savefig(PUBLIC / "agent_vs_honest_nav.png", dpi=120)
plt.close()

pd.DataFrame([asdict(p) for p in proposals]).to_csv(DATA / "rdagent_proposals.csv", index=False)
pd.DataFrame([res_agent, res_honest]).to_csv(DATA / "agent_eval.csv", index=False)
sent.loc[post].iloc[:5].to_csv(DATA / "mock_sentiment_sample.csv")

report = {
    "N_TRIALS_AGENT": N_TRIALS_AGENT,
    "kept": kept_names,
    "agent_sealed_OOS_IC": res_agent["sealed_OOS_mean_CS_IC"],
    "honest_sealed_OOS_IC": res_honest["sealed_OOS_mean_CS_IC"],
    "chain_of_alpha": "withdrawn_drop_detailed_claims",
}
(DATA / "lab01_report.json").write_text(json.dumps(report, indent=2))

print("\n=== limitations / failure modes (must-read) ===")
print("- LLM training cutoff / memorization: scores on pre-cutoff headlines are not forecasts.")
print("- Agent loops multiply trials → DSR needs explicit N; paper metrics ≠ your OOS edge.")
print("- IS keep rules (IC>threshold) overfit; sealed hold-out must stay sealed.")
print("- Formula banks / CoT traces can look interpretable while mining noise.")
print("- Chain-of-Alpha withdrawn: do not rely on unstable PDFs.")
print("\nwrote", PUBLIC / "rdagent_proposals.png", PUBLIC / "agent_vs_honest_nav.png")
print("DONE lab 01")
