"""P6 shared helpers. Learning only — not investment advice."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PUBLIC = Path(__file__).resolve().parents[2] / "public" / "p6"
PUBLIC.mkdir(parents=True, exist_ok=True)
DATA = Path(__file__).resolve().parent / "data"
DATA.mkdir(parents=True, exist_ok=True)
ANN = np.sqrt(252)
SEED = 42


def make_asset_panel(n_assets: int = 10, n_days: int = 1000, seed: int = SEED) -> pd.DataFrame:
    """Synthetic multi-asset daily returns with a common factor + idio."""
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2018-01-02", periods=n_days)
    assets = [f"A{i:02d}" for i in range(n_assets)]
    f = rng.normal(0.0002, 0.01, n_days)
    betas = 0.5 + rng.random(n_assets)
    rets = np.column_stack([betas[i] * f + rng.normal(0, 0.012, n_days) for i in range(n_assets)])
    return pd.DataFrame(rets, index=dates, columns=assets)


def lagged_vol(r: pd.Series, lb: int = 20) -> pd.Series:
    return r.rolling(lb, min_periods=lb).std(ddof=1).shift(1)


def sharpe(pnl: pd.Series) -> float:
    x = pnl.dropna()
    if len(x) < 5 or x.std(ddof=1) == 0:
        return float("nan")
    return float(x.mean() / x.std(ddof=1) * ANN)


def max_dd(equity: pd.Series) -> float:
    peak = equity.cummax()
    return float((equity / peak - 1.0).min())
