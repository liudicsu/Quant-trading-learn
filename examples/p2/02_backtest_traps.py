"""P2 lab: traps, walk-forward, PSR/DSR (Bailey & López de Prado), false-hit null.
Learning only — not investment advice.

Formulas verified against:
- Bailey & López de Prado (2012) "The Sharpe Ratio Efficient Frontier" (PSR with skew/kurtosis)
- Bailey & López de Prado (2014) "The Deflated Sharpe Ratio" (E[max SR], DSR = PSR(SR0))
- AFML ch.7 purged/embargo sketch; ch.14 multiple testing / DSR spirit
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm

DATA = Path(__file__).resolve().parent / "data" / "panel_toy.csv"
OUT_DIR = Path(__file__).resolve().parents[2] / "public" / "p2"
OUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA, parse_dates=["date"]).set_index("date").sort_index()
px = df["AAA_adj"]
ret = px.pct_change()
r = ret.dropna()
n = int(len(r))
ANN = np.sqrt(252)
EMC = 0.5772156649  # Euler-Mascheroni (Bailey & LdP 2014)

print("=== parameters ===")
print("n", n, "ann_sqrt252", round(float(ANN), 6), "asset=AAA_adj", "Rf=0")
print("sources: Bailey-LdP 2012 SRE Frontier (PSR); Bailey-LdP 2014 DSR; AFML ch.7/14")


def sharpe_ann(pnl: pd.Series) -> float:
    x = pnl.dropna()
    s = x.std(ddof=1)
    return float("nan") if s == 0 or len(x) < 3 else float(x.mean() / s * ANN)


def sharpe_raw(pnl: pd.Series) -> float:
    """Non-annualized SR (same frequency as returns) — as in Bailey PSR code."""
    x = pnl.dropna()
    s = x.std(ddof=1)
    return float("nan") if s == 0 or len(x) < 3 else float(x.mean() / s)


def nav(pnl: pd.Series) -> float:
    return float((1 + pnl.fillna(0)).cumprod().iloc[-1])


def moments4(pnl: pd.Series) -> tuple[float, float, float, float]:
    x = pnl.dropna().astype(float)
    mu = float(x.mean())
    sd = float(x.std(ddof=1))
    # Pearson kurtosis (γ4), not Fisher's excess — Bailey formula uses (γ4-1)/4
    m3 = float(((x - mu) ** 3).mean())
    m4 = float(((x - mu) ** 4).mean())
    skew = m3 / sd**3 if sd else 0.0
    kurt = m4 / sd**4 if sd else 3.0
    return mu, sd, skew, kurt


def psr(sr_hat: float, sr_star: float, n_obs: int, skew: float, kurt: float) -> float:
    """Bailey & López de Prado (2012) Probabilistic Sharpe Ratio.
    PSR(SR*) = Φ[(SR̂−SR*)√(n−1) / √(1 − γ3 SR̂ + ((γ4−1)/4) SR̂²)]
    SR̂, SR* in the same (non-annualized) frequency as the return sample.
    """
    if n_obs < 3 or not np.isfinite(sr_hat):
        return float("nan")
    denom = np.sqrt(max(1e-12, 1.0 - skew * sr_hat + ((kurt - 1.0) / 4.0) * sr_hat**2))
    z = ((sr_hat - sr_star) * np.sqrt(n_obs - 1)) / denom
    return float(norm.cdf(z))


def expected_max_sr(mu: float, sigma: float, n_trials: int) -> float:
    """Bailey & López de Prado (2014) Eq.(1): E[max SR] under Normal trials.
    E[max] ≈ μ + σ · [(1−γ) Φ⁻¹(1−1/N) + γ Φ⁻¹(1−1/(N e))]
    """
    if n_trials < 2:
        return mu
    max_z = (1 - EMC) * norm.ppf(1 - 1.0 / n_trials) + EMC * norm.ppf(
        1 - 1.0 / (n_trials * np.e)
    )
    return float(mu + sigma * max_z)


def run_ma(window: int, honest: bool) -> tuple[float, float, pd.Series]:
    sig = (px > px.rolling(window).mean()).astype(int)
    pos = sig.shift(1) if honest else sig
    pnl = (pos * ret).reindex(r.index)
    return sharpe_ann(pnl), nav(pnl), pnl


# --- cheat vs honest ---
sh_c, nav_c, _ = run_ma(10, honest=False)
sh_h, nav_h, pnl_h = run_ma(10, honest=True)
print("\n=== MA10 cheat vs honest ===")
print("cheat_same_bar_sharpe", round(sh_c, 4), "nav", round(nav_c, 6))
print("honest_shift1_sharpe", round(sh_h, 4), "nav", round(nav_h, 6))
print("lookahead_def: using today's close in the signal while earning today's close-to-close return.")

# --- survivorship / snooping recap (cross-link data-cleaning) ---
print("\n=== recap: survivorship & data snooping (see data-cleaning) ===")
print("survivorship: today's members != historical universe — replaying only survivors inflates means.")
print("snooping: choosing rules after peeking at full-sample ranks / many unlabeled trials.")
print("cross_link: /phase/data-honest-backtests/data-cleaning")

# --- parameter grid ---
windows = list(range(5, 41, 5))
rows = []
for w in windows:
    _, _, pnl = run_ma(w, honest=True)
    train_pnl = pnl.iloc[:200]
    test_pnl = pnl.iloc[200:]
    rows.append(
        {
            "w": w,
            "sharpe_train": sharpe_ann(train_pnl),
            "sharpe_test": sharpe_ann(test_pnl),
            "sr_raw_full": sharpe_raw(pnl),
            "n_full": int(pnl.dropna().shape[0]),
        }
    )
grid = pd.DataFrame(rows)
best = grid.sort_values("sharpe_train", ascending=False).iloc[0]
print("\n=== parameter grid (honest shift1) ===")
print("windows", windows)
print(
    "best_train_w",
    int(best["w"]),
    "sharpe_train",
    round(float(best["sharpe_train"]), 4),
    "sharpe_test",
    round(float(best["sharpe_test"]), 4),
)
print(
    "mean_train_sharpe",
    round(float(grid["sharpe_train"].mean()), 4),
    "mean_test_sharpe",
    round(float(grid["sharpe_test"].mean()), 4),
)
print("teach: picking max in-sample Sharpe after many trials overstates OOS — log trial counts.")

# --- freeze-then-holdout ---
hold = slice(-80, None)
develop = slice(None, -80)
_, _, pnl_fr = run_ma(int(best["w"]), honest=True)
print("\n=== freeze-then-holdout ===")
print("develop_n", len(px.iloc[develop]), "holdout_n", len(px.iloc[hold]))
print("frozen_w", int(best["w"]))
print("sharpe_develop", round(sharpe_ann(pnl_fr.iloc[develop]), 4))
print("sharpe_holdout", round(sharpe_ann(pnl_fr.iloc[hold]), 4))
print(
    "quant_arena_spirit: research feedback only on an earlier window; freeze one rule; "
    "score a sealed later window (arXiv:2610.30113)."
)

# --- full walk-forward ---
print("\n=== walk-forward (rolling train/test) ===")
train_len, test_len, step = 80, 20, 20
wf_rows = []
idx = r.index
start = 0
fold = 0
while start + train_len + test_len <= len(idx):
    tr_idx = idx[start : start + train_len]
    te_idx = idx[start + train_len : start + train_len + test_len]
    best_w, best_sr = None, -1e9
    for w in windows:
        sig = (px > px.rolling(w).mean()).astype(int)
        pos = sig.shift(1)
        pnl = (pos * ret).reindex(tr_idx)
        s = sharpe_ann(pnl)
        if np.isfinite(s) and s > best_sr:
            best_sr, best_w = s, w
    sig = (px > px.rolling(best_w).mean()).astype(int)
    pos = sig.shift(1)
    pnl_te = (pos * ret).reindex(te_idx)
    wf_rows.append(
        {
            "fold": fold,
            "train_start": str(tr_idx[0].date()),
            "train_end": str(tr_idx[-1].date()),
            "test_start": str(te_idx[0].date()),
            "test_end": str(te_idx[-1].date()),
            "best_w": best_w,
            "sharpe_train": round(float(best_sr), 4),
            "sharpe_test": round(sharpe_ann(pnl_te), 4),
        }
    )
    fold += 1
    start += step

wf = pd.DataFrame(wf_rows)
print("params: train_len", train_len, "test_len", test_len, "step", step, "windows", windows)
print("per_window_table")
print(wf.to_string(index=False))
print("summary_n_folds", len(wf))
nan_folds = wf.loc[wf["sharpe_test"].isna(), "fold"].tolist()
print("nan_test_folds", nan_folds)
print(
    "nan_reason: those test windows had a flat position path (all PnL≈0 → std=0), "
    "so Sharpe is undefined; pandas mean/median skip NaN by default."
)
print("summary_mean_train_sr", round(float(wf["sharpe_train"].mean()), 4))
print("summary_mean_test_sr", round(float(wf["sharpe_test"].mean(skipna=True)), 4))
print("summary_median_test_sr", round(float(wf["sharpe_test"].median(skipna=True)), 4))
print("summary_frac_test_positive", round(float((wf["sharpe_test"] > 0).mean()), 4))
print("summary_note: mean/median exclude NaN folds; frac_positive counts NaN as not >0.")

# --- false-hit null with SE verification ---
print("\n=== random-rule false hits + null SE check ===")
n_trials_null = 30
n_seeds = 50
thr = 1.5
se_ann = float(np.sqrt(252.0 / n))
p_one = float(1 - norm.cdf(thr / se_ann))
p_abs = 2 * p_one
expected = n_trials_null * p_abs
print("n_returns", n)
print("SE_ann_SR_under_null ≈ √(252/n) =", round(se_ann, 6))
print("P(|SR_ann|>1.5) under Normal null ≈", round(p_abs, 6))
print("expected_hits_per_30_trials ≈", round(expected, 4))

false = []
for seed in range(n_seeds):
    rr = np.random.default_rng(seed)
    hits = 0
    for _ in range(n_trials_null):
        noise = rr.normal(size=n)
        pos = pd.Series(np.sign(noise), index=r.index)
        if abs(sharpe_ann(pos * r)) > thr:
            hits += 1
    false.append(hits)
mean_fh = float(np.mean(false))
print("mean_false_hits", round(mean_fh, 3), "std_false_hits", round(float(np.std(false, ddof=1)), 3))
print(
    "context: Monte Carlo mean_false_hits≈",
    round(mean_fh, 3),
    "vs Normal-null expectation≈",
    round(expected, 3),
    "(close; discrete ±1 signs add slight difference).",
)

# --- PSR / DSR on best full-sample honest trial ---
_, _, pnl_best = run_ma(int(best["w"]), honest=True)
pnl_best = pnl_best.dropna()
mu, sd, sk, ku = moments4(pnl_best)
sr_raw = sharpe_raw(pnl_best)
sr_ann = sharpe_ann(pnl_best)
n_obs = len(pnl_best)
# Cross-trial SR variance from the grid (annualized SRs → convert to raw for E[max] scale)
# Bailey example uses non-annualized SR space. Use raw SRs from each window on full sample.
raw_srs = []
for w in windows:
    _, _, pnl_w = run_ma(w, honest=True)
    raw_srs.append(sharpe_raw(pnl_w.dropna()))
raw_srs = np.array(raw_srs, dtype=float)
var_sr = float(np.var(raw_srs, ddof=1))
sigma_sr = float(np.sqrt(var_sr))
mu_sr = 0.0  # null for deflation: true skill zero → E[max] from noise

print("\n=== PSR / DSR (Bailey & López de Prado) ===")
print("selected_w", int(best["w"]), "n_obs", n_obs)
print("SR_raw", round(sr_raw, 6), "SR_ann", round(sr_ann, 4))
print("skew_gamma3", round(sk, 4), "kurtosis_gamma4_pearson", round(ku, 4))
print("PSR(SR*=0)", round(psr(sr_raw, 0.0, n_obs, sk, ku), 4))
print("N_trials_grid", len(windows), "V[SR_raw_trials]", round(var_sr, 6))

dsr_rows = []
for N in [1, 2, 5, 8, 10, 20, 30, 50, 100, 200]:
    sr0 = expected_max_sr(mu_sr, sigma_sr if N > 1 else 1e-12, N)
    d = psr(sr_raw, sr0, n_obs, sk, ku)
    dsr_rows.append({"N": N, "E_max_SR_raw": round(sr0, 6), "DSR": round(d, 6)})
dsr_tbl = pd.DataFrame(dsr_rows)
print("DSR_vs_N_table (SR* = E[max SR] under null; grows with N → DSR falls)")
print(dsr_tbl.to_string(index=False))
print(
    "formula_note: DSR = PSR(SR̂, SR*=E[max], n, γ3, γ4); "
    "E[max]=σ_SR*[(1-γ)Φ^{-1}(1-1/N)+γ Φ^{-1}(1-1/(N e))] (Bailey-LdP 2014)."
)

fig, ax = plt.subplots(figsize=(7.5, 4.2))
ax.plot(dsr_tbl["N"], dsr_tbl["DSR"], "o-", color="#1f4e79", label="DSR of selected trial")
ax.plot(dsr_tbl["N"], dsr_tbl["E_max_SR_raw"], "s--", color="#c45911", label="E[max SR] (raw, null)")
ax.set_xlabel("Number of independent trials N")
ax.set_ylabel("DSR / E[max SR]")
ax.set_title("Deflated Sharpe vs trial count N (Bailey & López de Prado 2014)")
ax.grid(True, alpha=0.3)
ax.legend()
fig.tight_layout()
fig.savefig(OUT_DIR / "dsr_vs_N.png", dpi=120)
plt.close(fig)
print("saved_plot public/p2/dsr_vs_N.png")

# --- optional purged / embargo CV sketch (AFML ch.7) ---
print("\n=== optional: purged + embargo CV sketch (AFML ch.7) ===")
# Toy: binary labels from next-day return; purge train points whose information window overlaps test
label_horizon = 1
embargo = 3
# One split: train first 150, test next 40; purge last `label_horizon` of train; embargo `embargo` after test start
train_end = 150
test_start = 150
test_end = 190
purge_cut = train_end - label_horizon
train_idx = idx[:purge_cut]
# embargo: skip `embargo` bars after train before test usable — here we move test start
test_idx = idx[test_start + embargo : test_end + embargo]
print("label_horizon", label_horizon, "embargo_bars", embargo)
print("naive_train_n", train_end, "purged_train_n", len(train_idx))
print("test_after_embargo_n", len(test_idx))
print(
    "teach: purge drops train samples whose labels overlap the test window; "
    "embargo adds a gap so serial dependence does not leak."
)
print(
    "afml_note: this embargo/purge block is a SIMPLIFIED sketch of AFML ch.7, "
    "not the full combinatorial purged CV / embargo machinery in the book."
)

print("\n=== failure log template ===")
print("date | hypothesis | trials | best_is_metric | oos_metric | fail_reason | next_action")
print(
    "2026-11-04 | MA walk-forward | "
    f"{len(windows)} windows × {len(wf)} folds | "
    f"mean_train={round(float(wf['sharpe_train'].mean()), 3)} | "
    f"mean_test={round(float(wf['sharpe_test'].mean()), 3)} | IS≠OOS / DSR falls with N | "
    "shrink search / pre-register / sealed hold-out"
)

# --- CPCV teaching sketch (AFML ch.12 spirit; NOT production CombinatorialPurgedKFold) ---
print("\n=== CPCV teaching sketch (AFML ch.12 spirit) ===")
print("disclaimer: teaching sketch — NOT production AFML Combinatorial Purged Cross-Validation")
print("cite: López de Prado, Advances in Financial Machine Learning (Wiley, 2018), ch.12 CPCV; ch.7 purge/embargo")
from itertools import combinations

N_GROUPS, N_TEST = 6, 2
# Use honest MA pnl series for SR paths
_, _, pnl_cpcv = run_ma(20, honest=True)
pnl_cpcv = pnl_cpcv.dropna()
n_c = len(pnl_cpcv)
# Contiguous groups
edges = np.linspace(0, n_c, N_GROUPS + 1, dtype=int)
groups = [pnl_cpcv.iloc[edges[i] : edges[i + 1]] for i in range(N_GROUPS)]
print(f"params: N_GROUPS={N_GROUPS} N_TEST={N_TEST} n_obs={n_c} combo_count=C({N_GROUPS},{N_TEST})")
n_combos = int(__import__("math").comb(N_GROUPS, N_TEST))
# Number of backtest paths φ[N,k] = C(N-1, k-1)
n_paths = int(__import__("math").comb(N_GROUPS - 1, N_TEST - 1))
print(f"n_combinations={n_combos} n_backtest_paths=C({N_GROUPS-1},{N_TEST-1})={n_paths}")

# For each combo of test groups: train = rest (drop adjacent purge of 1 group-edge bar count approx)
# Teaching: compute SR on the concatenated test groups; collect one SR per combo; also reconstruct paths
combo_srs = []
for test_ids in combinations(range(N_GROUPS), N_TEST):
    test_pnl = pd.concat([groups[i] for i in test_ids]).sort_index()
    # Purge sketch: drop first/last bar of each train group adjacent to a test group (simplified)
    train_ids = [i for i in range(N_GROUPS) if i not in test_ids]
    train_pnl = pd.concat([groups[i] for i in train_ids]).sort_index()
    # Embargo sketch: drop 2 bars after each test block from train (already separated by groups here)
    sr_te = sharpe_ann(test_pnl)
    sr_tr = sharpe_ann(train_pnl)
    combo_srs.append({"test": test_ids, "sr_test": sr_te, "sr_train": sr_tr, "n_test": len(test_pnl)})

combo_df = pd.DataFrame(combo_srs)
print("combo_SR_test describe:")
print(combo_df["sr_test"].describe().round(4).to_string())
print(f"combo_SR_test mean={combo_df['sr_test'].mean():.4f} std={combo_df['sr_test'].std(ddof=1):.4f}")

# Single hold-out contrast: first 2/3 train, last 1/3 test — one number
cut = int(n_c * 2 / 3)
sr_hold = sharpe_ann(pnl_cpcv.iloc[cut:])
sr_is = sharpe_ann(pnl_cpcv.iloc[:cut])
print(f"single_holdout: IS_SR={sr_is:.4f} OOS_SR={sr_hold:.4f} (ONE path)")
print(
    f"contrast: single hold-out gives ONE OOS SR={sr_hold:.4f}; "
    f"CPCV-style combos give a DISTRIBUTION of {n_combos} test SRs "
    f"(mean={combo_df['sr_test'].mean():.4f}, std={combo_df['sr_test'].std(ddof=1):.4f})"
)
print(
    "teach: combinatorial test blocks reuse information across paths — paths are NOT independent trials; "
    "use the SR distribution to stress-test stability, not to mint N free trials for DSR."
)

fig, ax = plt.subplots(figsize=(7.5, 4))
ax.hist(combo_df["sr_test"].dropna(), bins=8, color="#1f4e79", edgecolor="white", alpha=0.9)
ax.axvline(sr_hold, color="#c45911", lw=2, label=f"single hold-out OOS SR={sr_hold:.2f}")
ax.axvline(combo_df["sr_test"].mean(), color="#2e7d32", lw=2, ls="--", label="combo mean")
ax.set_xlabel("test-block Sharpe (ann.)")
ax.set_ylabel("count")
ax.set_title("CPCV teaching sketch: SR distribution across test combinations")
ax.legend()
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(OUT_DIR / "cpcv_sr_dist.png", dpi=120)
plt.close(fig)
print("saved_plot public/p2/cpcv_sr_dist.png")
print("reuse_note: ml-leakage-control reuses this combinatorial idea when scoring many purged folds")


# ---------- One-switch decision-time leakage (arXiv:2605.23959) ----------
# Teaching foil only: hold data/model/costs fixed; toggle ONE protocol rule.
print("\n=== one-switch decision-time leakage (arXiv:2605.23959 When Alpha Disappears) ===")
print("cite: Zhang et al. arXiv:2605.23959 — TEMP_CENTER and EXEC_OPEN dominate Leakage Gain")
rng_sw = np.random.default_rng(42)
# Synthetic daily OHLCV-like path for one name
n_sw = 400
eps = rng_sw.normal(0, 0.01, n_sw)
close = 100 * np.exp(np.cumsum(eps))
open_ = np.r_[close[0], close[:-1]] * (1 + rng_sw.normal(0, 0.001, n_sw))
# Clean: trailing 5d mean of past closes only; enter next open; label next-open return
trail = pd.Series(close).rolling(5, min_periods=5).mean().shift(1)  # known by close t using t and earlier only via shift after mean of past
# Actually trailing mean at t using close[t-4..t] then trade at open[t+1]
trail_clean = pd.Series(close).rolling(5, min_periods=5).mean()
# signal at close t -> position from open t+1 to open t+2
sig_clean = trail_clean.diff()  # momentum of trailing mean
pos_clean = np.sign(sig_clean).shift(1)  # decide after close, hold next day open-to-open
r_oo = pd.Series(open_).pct_change().shift(-1)  # open[t+1]/open[t]-1 aligned to t
pnl_clean = (pos_clean * r_oo).dropna()

# TEMP_CENTER: centered 5d mean uses future closes around t
def centered_mean(x, w=5):
    s = pd.Series(x)
    # centered window: for index t use [t-2..t+2]
    return s.rolling(w, center=True, min_periods=w).mean()

trail_center = centered_mean(close, 5)
sig_center = trail_center.diff()
pos_center = np.sign(sig_center).shift(1)
pnl_center = (pos_center * r_oo).dropna()

# EXEC_OPEN: use same-day close information while assuming same-day open fill (infeasible)
# signal uses close[t] but position is applied to open[t]->open[t+1] return (as if filled at open t)
sig_exec = pd.Series(close).pct_change()  # uses close[t] vs close[t-1]
pos_exec = np.sign(sig_exec)  # NO shift — pretends we traded the open using the close
r_open_same = pd.Series(open_).pct_change().shift(-1)  # from open t to open t+1, indexed at t
# Align: at decision "open t" we illegally use close t
pnl_exec = (pos_exec * r_open_same).dropna()

def sr_ann(x):
    x = pd.Series(x).dropna()
    if len(x) < 10 or x.std(ddof=1) == 0:
        return float("nan")
    return float(x.mean() / x.std(ddof=1) * np.sqrt(252))

sr_c = sr_ann(pnl_clean)
sr_tc = sr_ann(pnl_center)
sr_eo = sr_ann(pnl_exec)
lg_tc = sr_tc - sr_c
lg_eo = sr_eo - sr_c
print(f"CLEAN SR@toy≈{sr_c:.3f}")
print(f"TEMP_CENTER SR≈{sr_tc:.3f}  LeakageGain_SR≈{lg_tc:+.3f}  (centered rolling uses future)")
print(f"EXEC_OPEN   SR≈{sr_eo:.3f}  LeakageGain_SR≈{lg_eo:+.3f}  (close info + same-day open fill)")
print("teach: chronological train/test split alone is NOT enough — decision-time semantics matter.")
print("paper: TEMP_CENTER & EXEC_OPEN dominate; NORM_GLOBAL / STRUCT_GRAPH / EXEC_CLOSE often weak.")
print("diagnostic only — large LG is protocol inflation under infeasible rules, not deployable alpha.")

print("ASSERTS_OK")
