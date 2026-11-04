"""P6 lab 02: TWAP/VWAP, Almgren–Chriss, implementation shortfall, limit vs market, TCA.
Learning only — not investment advice.
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from _common import PUBLIC, DATA

print("=== parameters ===")
print("liquidation: X0=1e6 shares over T=1 day, N=10 slices; σ daily=0.02; temp impact η; perm γ")
print("cite: Almgren & Chriss 2000/2001 Journal of Risk 3(2) pp.5–39 — Optimal execution of portfolio transactions")
print("cite: Perold 1988 JPM 14(3) — The implementation shortfall: paper vs reality")
print("cite: TWAP/VWAP as schedule benchmarks (industry TCA); arrival-price IS decomposition")
print("look-ahead: schedules use only ex-ante volume/price forecasts; post-trade report uses realized path")

rng = np.random.default_rng(1)
N, T, X0 = 10, 1.0, 1_000_000.0
tau = T / N
sigma = 0.02  # daily vol on price
eta = 1e-6  # temporary impact
gamma = 1e-7  # permanent
S0 = 100.0

def ac_trajectory(lam: float):
    """Closed-form Almgren–Chriss remaining shares x_j = X0 * sinh(κ(T-t_j))/sinh(κT)."""
    kappa = np.sqrt(lam * sigma**2 / eta) if lam > 0 else 1e-12
    t = np.linspace(0, T, N + 1)
    if abs(np.sinh(kappa * T)) < 1e-12:
        x = X0 * (1 - t / T)
    else:
        x = X0 * np.sinh(kappa * (T - t)) / np.sinh(kappa * T)
    x[-1] = 0.0
    trades = -np.diff(x)  # positive sells
    return t, x, trades, kappa

# Risk-aversion sweep → efficient frontier E[cost] vs risk
print("\n=== Almgren–Chriss efficient frontier (λ sweep) ===")
lams = np.logspace(-8, -3, 12)
frontier = []
for lam in lams:
    t, x, trades, kappa = ac_trajectory(lam)
    # Expected cost & variance under linear impact (AC formulas)
    # E ≈ 0.5*gamma*X0^2 + eta/tau * sum(n_j^2); V ≈ sigma^2 * sum(x_j^2)*tau
    n = trades
    E = 0.5 * gamma * X0**2 + (eta / tau) * np.sum(n**2)
    V = (sigma**2) * tau * np.sum(x[:-1] ** 2)
    frontier.append({"lam": lam, "E": E, "std": np.sqrt(V), "kappa": kappa})
    print(f"lambda={lam:.1e} kappa={kappa:.4f} E_cost={E:.2f} risk_std={np.sqrt(V):.2f}")
fr = pd.DataFrame(frontier)

fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(fr["std"], fr["E"], "o-", color="#1f4e79")
ax.set_xlabel("risk std (AC)"); ax.set_ylabel("expected cost E")
ax.set_title("Almgren–Chriss efficient frontier (cost vs risk)")
ax.grid(True, alpha=0.3)
fig.tight_layout(); fig.savefig(PUBLIC / "ac_frontier.png", dpi=120); plt.close()

# Trajectories for three λ
fig, ax = plt.subplots(figsize=(7, 4))
for lam, lab in [(1e-7, "patient"), (1e-5, "balanced"), (1e-3, "urgent")]:
    t, x, trades, kappa = ac_trajectory(lam)
    ax.plot(t, x, label=f"{lab} λ={lam:.0e}")
ax.set_ylabel("shares remaining"); ax.set_xlabel("time")
ax.legend(); ax.grid(True, alpha=0.3); ax.set_title("AC liquidation trajectories")
fig.tight_layout(); fig.savefig(PUBLIC / "ac_trajectories.png", dpi=120); plt.close()
print("chart", PUBLIC / "ac_frontier.png")

# TWAP vs VWAP schedules
print("\n=== TWAP vs VWAP schedules ===")
# synthetic intraday volume U-shape
minutes = np.arange(N)
vol_profile = 1.2 - 0.8 * np.sin(np.pi * minutes / (N - 1))  # higher at open/close
vol_profile = vol_profile / vol_profile.sum()
twap_trades = np.full(N, X0 / N)
vwap_trades = X0 * vol_profile
print("TWAP slice:", np.round(twap_trades[:3], 1), "...")
print("VWAP slice:", np.round(vwap_trades, 1))
print("teach: TWAP ignores volume; VWAP matches expected volume profile")

# Implementation shortfall (Perold)
print("\n=== implementation shortfall (Perold 1988) ===")
# arrival price S0; decision to sell X0; simulate mid path + temporary impact on AC balanced traj
_, x, trades, _ = ac_trajectory(1e-5)
# Brownian mid — permanent impact is INCREMENTAL: each slice moves the mid by γ·n_j once
# (do NOT subtract the running sum of permanent impact every step — that double-counts)
dW = rng.normal(0, sigma * np.sqrt(tau), N)
mid = np.zeros(N + 1); mid[0] = S0
exec_px = np.zeros(N)
for j in range(N):
    # temporary impact on this fill (seller gets worse than prevailing mid)
    exec_px[j] = mid[j] - eta * (trades[j] / tau)
    # mid evolves: diffusion + incremental permanent impact from this slice
    mid[j + 1] = mid[j] + dW[j] - gamma * trades[j]
arrival = S0
paper = arrival * X0  # paper liquidation at arrival
realized = np.sum(exec_px * trades)
IS = paper - realized  # positive = shortfall for a sell program vs arrival
IS_bps = 1e4 * IS / (arrival * X0)
# volume-weighted arrival slip ≡ Perold IS/arrival (same dollars / same notional)
vw_arrival_slip_bps = 1e4 * np.sum((arrival - exec_px) * trades) / (arrival * X0)
print(f"arrival={arrival:.2f} paper_value={paper:.0f} realized={realized:.0f} IS={IS:.0f} IS_bps={IS_bps:.1f}")
print(f"volume_weighted_arrival_slip_bps={vw_arrival_slip_bps:.1f}  (== IS_bps; identical to Perold IS, not a second metric)")
print("post-trade: decompose IS ≈ delay + trading (impact) components under arrival-price benchmark")

# Limit vs market toy
print("\n=== limit vs market: fill probability vs adverse selection ===")
# Fair value ~ mid; limit improves price but fill_prob < 1 and adverse selection when filled
n_sim = 2000
edge_wanted = 0.05  # cents better than mid
fill_p = 0.55
mid_moves = rng.normal(0, 0.1, n_sim)  # adverse if filled when mid moves against
# market: always fill at mid - half_spread
half_spread = 0.02
mkt_pnl = -half_spread * np.ones(n_sim)  # cost of immediacy (sell)
# limit: with p fill at mid+edge (better), else miss and chase at mid-half_spread after move
filled = rng.random(n_sim) < fill_p
# adverse: fills more likely when mid already moved against (correlation)
# simplify: when filled, mid_move tends negative for seller
limit_pnl = np.where(
    filled,
    edge_wanted + 0.5 * np.minimum(mid_moves, 0),  # partial adverse
    -half_spread - np.abs(mid_moves),  # chase after miss
)
print(f"market mean_cost={-mkt_pnl.mean():.4f} limit mean_pnl={limit_pnl.mean():.4f} fill_rate={filled.mean():.2f}")
print("teach: limits improve price conditional on fill but add non-fill + adverse-selection risk")

# Slippage monitoring report — arrival (= Perold) vs interval VWAP vs close
print("\n=== slippage / TCA mini report (multiple benchmarks) ===")
# Interval VWAP foil: volume-weighted mid over the window (ex-post interval benchmark)
# Interval VWAP here uses the *planned* VWAP schedule weights (vol_profile), not realized tape volume
interval_vwap = float(np.sum(mid[:-1] * vol_profile))
close_px = float(mid[-1])
report = pd.DataFrame({
    "slice": np.arange(1, N + 1),
    "shares": trades,
    "exec_px": exec_px,
    "mid": mid[:-1],
    "arrival_slip_bps": 1e4 * (arrival - exec_px) / arrival,
    "vwap_slip_bps": 1e4 * (interval_vwap - exec_px) / interval_vwap,
    "close_slip_bps": 1e4 * (close_px - exec_px) / close_px,
})
print(report.round(4).to_string(index=False))
# Volume-weighted arrival slip == Perold IS_bps (do NOT treat unweighted mean as a second IS)
vw_arr = 1e4 * np.sum((arrival - exec_px) * trades) / (arrival * np.sum(trades))
vw_vwap = 1e4 * np.sum((interval_vwap - exec_px) * trades) / (interval_vwap * np.sum(trades))
vw_close = 1e4 * np.sum((close_px - exec_px) * trades) / (close_px * np.sum(trades))
print(f"benchmarks (volume-weighted): arrival/Perold={vw_arr:.2f} bps | interval_VWAP={vw_vwap:.2f} bps | close={vw_close:.2f} bps")
uw = float(report['arrival_slip_bps'].mean())
print(f"note: on nearly equal slice sizes, unweighted mean arrival_slip={uw:.2f} bps ≈ volume-weighted Perold={vw_arr:.2f}; "
      f"they diverge only when slice sizes differ — always prefer volume-weighted (=IS)")
print(f"interval_VWAP(planned weights)={interval_vwap:.4f} close={close_px:.4f} participation_max={(trades/X0).max():.2f}")
report.to_csv(DATA / "tca_report.csv", index=False)
print("disclaimer: toy paths — learning only, not a broker TCA")


# ---------- Thin pointer: alpha-decay no-trade (arXiv:2502.04284) ----------
print("\n=== Pointer — alpha decay + costs → no-trade (arXiv:2502.04284) ===")
print("host detail in portfolio-risk-sizing: widen no-trade band with costs; 不交易也是决策")
print("here: TCA / Almgren paths still assume you decided TO trade — size the band first")



# ---------- Square-root / double-√ impact literacy (arXiv:2502.16246 + 2411.13965) ----------
print("\n=== square-root / double-√ impact literacy (NOT edge) ===")
print("cite: arXiv:2502.16246 — double square-root: child √q + time decay → metaorder √Q; scramble → mechanical")
print("cite: arXiv:2411.13965 — TSE complete survey: δ≈1/2 universal within errors")
print("cite: Gatheral 2010 Quant. Finance 10(7) DOI 10.1080/14697680903373692 — no-dynamic-arbitrage: exp decay ↔ only linear impact")
print("formula: I ≈ Y · σ · √(Q/V)  — cost RULER, not alpha; reject optimize-Y→alpha")
print("tension: Almgren–Chriss linear temporary η vs empirical √; AC remains a desk utility frontier")

Y, sig_d, V_d = 1.0, 0.02, 1_000_000.0
ladder_rows = []
print("Q/V | I_sqrt(bps) | I_lin(bps) | sqrt/lin")
for Q in [1e3, 1e4, 5e4, 1e5, 2e5]:
    I_sqrt = Y * sig_d * np.sqrt(Q / V_d)
    I_lin = Y * sig_d * (Q / V_d)  # Kyle-style linear foil, same Yσ scale
    ladder_rows.append((Q / V_d, 1e4 * I_sqrt, 1e4 * I_lin, I_sqrt / I_lin))
    print(f"{Q/V_d:.4f} | {1e4*I_sqrt:8.2f} | {1e4*I_lin:8.2f} | {I_sqrt/I_lin:6.3f}")

# Double-√ toy: J(q,i) ∝ σ√(q/V)·(√(i+i0)−√i0); when i=N and Q=qN → ~√Q
i0, q_child = 4.0, 10_000.0
print("double-√ child cumulative (q=1e4, i0=4):")
for i in (1, 4, 9, 16, 25):
    J = sig_d * np.sqrt(q_child / V_d) * (np.sqrt(i + i0) - np.sqrt(i0))
    print(f"  i={i:2d} J_bps={1e4*J:.2f}")
Q_meta = q_child * 25
I_meta = Y * sig_d * np.sqrt(Q_meta / V_d)
J25 = sig_d * np.sqrt(q_child / V_d) * (np.sqrt(25 + i0) - np.sqrt(i0))
print(f"metaorder √Q at Q=q*25 → I_bps={1e4*I_meta:.2f}; child-cumul J(i=25)_bps={1e4*J25:.2f}")
print("schedule caveat: empirics often find I(Q) ≈ independent of T for moderate participation — not a free speed dial")
print("scramble literacy: synthetic metaorders (ID reshuffle) follow the same √Q law → mechanical origin foil")
print("REJECT: fitting Y on the evaluation path as 'alpha'; Obizhaeva–Wang N-trader games; RL execution papers")

# √ vs linear cost on equal slice programme (same Q total)
Q_tot = 100_000.0
I_sqrt_tot = Y * sig_d * np.sqrt(Q_tot / V_d)
I_lin_tot = Y * sig_d * (Q_tot / V_d)
print(f"equal-programme foil Q/V=0.10: √-ruler={1e4*I_sqrt_tot:.2f}bps vs linear={1e4*I_lin_tot:.2f}bps")
print("bridge from costs-in-backtest: same √(Q/ADV) capacity ruler — deepen mechanics here, not a second alpha")
print("disclaimer: TSE ID-resolved empirics cited for literacy; toy Y=1 — learning only, not a broker impact model")
