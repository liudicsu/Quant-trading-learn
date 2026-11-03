"""P8 shared helpers. Learning only — not investment advice.
Offline only: no LLM/API/network calls at runtime.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

PUBLIC = Path(__file__).resolve().parents[2] / "public" / "p8"
PUBLIC.mkdir(parents=True, exist_ok=True)
DATA = Path(__file__).resolve().parent / "data"
DATA.mkdir(parents=True, exist_ok=True)

ANN = np.sqrt(252)
SEED = 8
HORIZON = 5
EMBARGO = 5
N_FOLDS = 5
EMC = 0.5772156649

# Shared cost model (same spirit as P2/P4): 10 bps one-way + simple impact
ONE_WAY_BPS = 10.0
IMPACT_K = 0.1


def make_panel(n_days: int = 520, n_assets: int = 40, seed: int = SEED):
    """Synthetic cross-section with a weak latent factor + noise."""
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2023-01-02", periods=n_days)
    assets = [f"A{i:02d}" for i in range(n_assets)]
    latent = rng.normal(0, 0.01, size=n_days)
    beta = rng.normal(0.4, 0.6, size=n_assets)
    idio = rng.normal(0, 0.012, size=(n_days, n_assets))
    # mild cross-sectional predictability of next-day residual via slow feature
    slow = np.zeros((n_days, n_assets))
    slow[0] = rng.normal(0, 1, n_assets)
    for t in range(1, n_days):
        slow[t] = 0.95 * slow[t - 1] + rng.normal(0, 0.2, n_assets)
    # true next-day CS alpha proportional to lagged slow (weak)
    alpha = 0.0008 * slow
    rets = latent[:, None] * beta[None, :] + idio + np.r_[alpha[:1] * 0, alpha[:-1]]
    rets = pd.DataFrame(rets, index=dates, columns=assets)
    slow_df = pd.DataFrame(slow, index=dates, columns=assets)
    meta = pd.DataFrame({"beta_true": beta}, index=assets)
    return rets, slow_df, meta


def apply_costs_ls(weights: pd.DataFrame, rets: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    w = weights.shift(1).fillna(0.0)
    gross = (w * rets).sum(axis=1)
    turn = w.diff().abs().sum(axis=1).fillna(w.abs().sum(axis=1))
    sigma = rets.abs().mean(axis=1).rolling(20, min_periods=5).mean().shift(1).fillna(0.01)
    c = turn * (ONE_WAY_BPS / 1e4) + IMPACT_K * sigma * np.sqrt(turn.clip(0))
    return gross - c, turn


def psr(sr_hat: float, sr_star: float, n_obs: int, skew: float, kurt: float) -> float:
    if n_obs < 3 or not np.isfinite(sr_hat):
        return float("nan")
    denom = np.sqrt(max(1e-12, 1.0 - skew * sr_hat + ((kurt - 1.0) / 4.0) * sr_hat**2))
    z = ((sr_hat - sr_star) * np.sqrt(n_obs - 1)) / denom
    return float(norm.cdf(z))


def expected_max_sr(mu: float, sigma: float, n_trials: int) -> float:
    if n_trials < 2:
        return mu
    max_z = (1 - EMC) * norm.ppf(1 - 1.0 / n_trials) + EMC * norm.ppf(1 - 1.0 / (n_trials * np.e))
    return float(mu + sigma * max_z)


def dsr_from_pnl(pnl: pd.Series, n_trials: int) -> dict:
    x = pnl.dropna()
    n = len(x)
    if n < 5 or x.std(ddof=1) == 0:
        return {"n_obs": n, "sr_daily": float("nan"), "DSR": float("nan"), "SR_star": float("nan"), "n_trials": n_trials}
    sr_daily = float(x.mean() / x.std(ddof=1))
    skew = float(x.skew())
    kurt = float(x.kurtosis() + 3.0)
    sr_star = expected_max_sr(0.0, 1.0, n_trials)
    return {
        "n_obs": n,
        "sr_daily": sr_daily,
        "sr_ann": sr_daily * ANN,
        "DSR": psr(sr_daily, sr_star, n, skew, kurt),
        "SR_star": sr_star,
        "n_trials": n_trials,
    }


def purged_kfold_indices(dates, n_folds: int, label_horizon: int, embargo: int):
    dates = np.asarray(sorted(pd.unique(dates)))
    n = len(dates)
    fold_sizes = [n // n_folds] * n_folds
    for i in range(n % n_folds):
        fold_sizes[i] += 1
    bounds = np.cumsum([0] + fold_sizes)
    folds = []
    for i in range(n_folds):
        te_lo, te_hi = int(bounds[i]), int(bounds[i + 1])
        test_dates = dates[te_lo:te_hi]
        purge_lo = max(0, te_lo - label_horizon)
        emb_hi = min(n, te_hi + embargo)
        train_mask = np.ones(n, dtype=bool)
        train_mask[purge_lo:emb_hi] = False
        train_dates = dates[train_mask]
        folds.append((train_dates, test_dates))
    return folds


def daily_cs_ic(pred: pd.Series, y: pd.Series) -> pd.Series:
    df = pd.concat([pred.rename("p"), y.rename("y")], axis=1).dropna()
    ics = df.groupby(level=0).apply(
        lambda g: g["p"].corr(g["y"], method="spearman") if len(g) >= 8 else np.nan
    )
    return ics.dropna()


def mean_daily_cs_ic(pred: pd.Series, y: pd.Series) -> dict:
    ics = daily_cs_ic(pred, y)
    if len(ics) < 5:
        return {"mean_ic": float("nan"), "std_ic": float("nan"), "t_stat": float("nan"), "ICIR": float("nan"), "n_days": len(ics), "ics": ics}
    mu = float(ics.mean())
    sd = float(ics.std(ddof=1))
    t = mu / (sd / np.sqrt(len(ics))) if sd > 0 else float("nan")
    icir = mu / (sd + 1e-12) * ANN
    return {"mean_ic": mu, "std_ic": sd, "t_stat": float(t), "ICIR": float(icir), "n_days": len(ics), "ics": ics}


def pred_to_ls_pnl(pred_wide: pd.DataFrame, rets: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    wide = pred_wide.reindex(index=rets.index, columns=rets.columns)
    w = pd.DataFrame(0.0, index=wide.index, columns=wide.columns)
    for dt in wide.index:
        s = wide.loc[dt].dropna()
        if len(s) < 10:
            continue
        lab = pd.qcut(s, 5, labels=False, duplicates="drop") + 1
        for qi, sign in [(1, -1.0), (5, 1.0)]:
            members = lab[lab == qi].index
            if len(members):
                w.loc[dt, members] = sign / len(members)
    return apply_costs_ls(w, rets)


def forward_label_wide(rets: pd.DataFrame, h: int = 1) -> pd.DataFrame:
    """Label at t = sum of returns over [t+1, t+h]."""
    out = pd.DataFrame(np.nan, index=rets.index, columns=rets.columns)
    vals = rets.values
    for i in range(len(rets) - h):
        out.iloc[i] = vals[i + 1 : i + 1 + h].sum(axis=0)
    return out
