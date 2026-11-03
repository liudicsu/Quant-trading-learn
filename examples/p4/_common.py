"""P4 shared helpers + synthetic panel generator. Learning only — not investment advice."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parent / "data"
PUBLIC = Path(__file__).resolve().parents[2] / "public" / "p4"
PUBLIC.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)
ANN = np.sqrt(252)
ONE_WAY_BPS = 10.0
IMPACT_K = 0.10
ADV = 1e6
CAPITAL = 1e6
VOL_LB = 20

# Planted DGP (teaching-scale premium; exaggerated so FM clears t>3)
N_ASSETS, N_DAYS, N_IND = 200, 750, 10
MU_TRUE = 0.0025
SEED = 42


def lagged_sigma(ret: pd.Series) -> pd.Series:
    roll = ret.rolling(VOL_LB, min_periods=VOL_LB).std(ddof=1)
    expand = ret.expanding(min_periods=2).std(ddof=1)
    return roll.fillna(expand).shift(1).fillna(0.0)


def apply_costs_ls(weights: pd.DataFrame, rets: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """Long-short portfolio: daily pnl = sum_i w_{i,t-1} * r_{i,t}; costs on turnover."""
    w = weights.shift(1).fillna(0.0)
    gross = (w * rets).sum(axis=1)
    turn = w.diff().abs().sum(axis=1).fillna(w.abs().sum(axis=1))
    sigma = lagged_sigma(rets.abs().mean(axis=1))
    c = turn * (ONE_WAY_BPS / 1e4) + IMPACT_K * sigma * np.sqrt((turn * (CAPITAL / 100) / ADV).clip(0))
    return gross - c, turn


def ensure_panel(force: bool = False) -> None:
    """Generate 200×750 multi-asset panel CSVs if missing."""
    marker = DATA / "returns.csv"
    if marker.exists() and not force:
        return
    rng = np.random.default_rng(SEED)
    dates = pd.bdate_range("2020-01-02", periods=N_DAYS)
    assets = [f"A{i:03d}" for i in range(N_ASSETS)]
    ind = rng.integers(0, N_IND, size=N_ASSETS)
    log_mcap0 = 20 + 0.3 * ind + rng.normal(0, 0.8, N_ASSETS)
    f_true = MU_TRUE + rng.normal(0, 0.008, N_DAYS)
    f_mkt = rng.normal(0, 0.012, N_DAYS)
    f_size = rng.normal(0, 0.006, N_DAYS)
    f_ind = rng.normal(0, 0.004, size=(N_DAYS, N_IND))
    beta_true = rng.normal(0, 1.0, N_ASSETS)
    beta_mkt = 0.8 + 0.3 * rng.normal(size=N_ASSETS)
    beta_size = -(log_mcap0 - log_mcap0.mean()) / log_mcap0.std()
    beta_noise = rng.normal(0, 1.0, N_ASSETS)
    rets = np.zeros((N_DAYS, N_ASSETS))
    for t in range(N_DAYS):
        rets[t] = (
            beta_true * f_true[t]
            + beta_mkt * f_mkt[t]
            + beta_size * f_size[t]
            + f_ind[t, ind]
            + rng.normal(0, 0.012, N_ASSETS)
        )
    px = 100 * np.exp(np.cumsum(rets, axis=0))
    raw_factor = (
        np.tile(beta_true, (N_DAYS, 1))
        + 0.4 * ind[None, :]
        + 0.25 * beta_size[None, :]
        + rng.normal(0, 0.35, size=(N_DAYS, N_ASSETS))
    )
    raw_factor2 = (
        np.tile(beta_noise, (N_DAYS, 1))
        + 0.3 * ind[None, :]
        + rng.normal(0, 0.5, size=(N_DAYS, N_ASSETS))
    )
    log_mcap = (
        log_mcap0[None, :]
        + 0.0002 * np.arange(N_DAYS)[:, None]
        + rng.normal(0, 0.01, (N_DAYS, N_ASSETS))
    )
    pd.DataFrame(rets, index=dates, columns=assets).to_csv(DATA / "returns.csv")
    pd.DataFrame(px, index=dates, columns=assets).to_csv(DATA / "prices.csv")
    pd.DataFrame(raw_factor, index=dates, columns=assets).to_csv(DATA / "raw_factor.csv")
    pd.DataFrame(raw_factor2, index=dates, columns=assets).to_csv(DATA / "raw_factor2.csv")
    pd.DataFrame(log_mcap, index=dates, columns=assets).to_csv(DATA / "log_mcap.csv")
    pd.DataFrame(
        {
            "asset": assets,
            "industry": ind,
            "beta_true": beta_true,
            "beta_mkt": beta_mkt,
            "beta_size": beta_size,
            "beta_noise": beta_noise,
        }
    ).to_csv(DATA / "meta.csv", index=False)
    pd.DataFrame({"date": dates, "f_true": f_true, "f_mkt": f_mkt, "f_size": f_size}).to_csv(
        DATA / "factors_truth.csv", index=False
    )
    (DATA / "PANEL_SEED.txt").write_text(f"SEED={SEED} MU_TRUE={MU_TRUE} N={N_ASSETS}x{N_DAYS}\n")


def load_panel():
    ensure_panel()
    rets = pd.read_csv(DATA / "returns.csv", index_col=0, parse_dates=True)
    raw = pd.read_csv(DATA / "raw_factor.csv", index_col=0, parse_dates=True)
    raw2 = pd.read_csv(DATA / "raw_factor2.csv", index_col=0, parse_dates=True)
    log_mcap = pd.read_csv(DATA / "log_mcap.csv", index_col=0, parse_dates=True)
    meta = pd.read_csv(DATA / "meta.csv").set_index("asset")
    return rets, raw, raw2, log_mcap, meta
