"""Shared P3 lab helpers. Learning only — not investment advice."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parent / "data" / "panel_toy.csv"
PUBLIC = Path(__file__).resolve().parents[2] / "public" / "p3"
PUBLIC.mkdir(parents=True, exist_ok=True)

ANN = np.sqrt(252)
COMMISSION_BPS = 2.0
HALF_SPREAD_BPS = 5.0
SLIPPAGE_BPS = 3.0
ONE_WAY_BPS = COMMISSION_BPS + HALF_SPREAD_BPS + SLIPPAGE_BPS  # 10 bps one-way stack
IMPACT_K = 0.10
ADV_SHARES = 1_000_000.0
CAPITAL = 1_000_000.0


def load_panel() -> pd.DataFrame:
    df = pd.read_csv(DATA, parse_dates=["date"]).set_index("date").sort_index()
    return df


def sharpe(pnl: pd.Series) -> float:
    x = pnl.dropna()
    s = x.std(ddof=1)
    return float("nan") if len(x) < 2 or s == 0 else float(x.mean() / s * ANN)


def max_dd(equity: pd.Series) -> float:
    peak = equity.cummax()
    dd = equity / peak - 1.0
    return float(dd.min())


def nav(pnl: pd.Series) -> float:
    return float((1 + pnl.fillna(0)).cumprod().iloc[-1])


def apply_costs(pos: pd.Series, ret: pd.Series, price: pd.Series) -> tuple[pd.Series, pd.Series, dict]:
    """Next-open style: pos already shifted. Four-part costs; impact × turnover."""
    pos = pos.reindex(ret.index).fillna(0.0)
    turnover = pos.diff().abs().fillna(pos.abs())
    gross = pos * ret
    bps = ONE_WAY_BPS / 1e4
    c_stack = turnover * bps
    # pedagogical √ impact scaled by turnover * (shares/ADV)
    shares = CAPITAL / price.reindex(ret.index).ffill().bfill().clip(lower=1e-6)
    participation = (turnover * shares) / ADV_SHARES
    sigma = float(ret.std(ddof=1))
    c_impact = IMPACT_K * sigma * np.sqrt(participation.clip(lower=0.0))
    net = gross - c_stack - c_impact
    stats = {
        "mean_turnover": float(turnover.mean()),
        "one_way_bps": ONE_WAY_BPS,
        "gross_sharpe": sharpe(gross),
        "net_sharpe": sharpe(net),
        "gross_nav": nav(gross),
        "net_nav": nav(net),
        "net_maxdd": max_dd((1 + net.fillna(0)).cumprod()),
    }
    return net, turnover, stats


def oos_split(index: pd.DatetimeIndex, frac: float = 0.7) -> tuple[pd.DatetimeIndex, pd.DatetimeIndex]:
    cut = int(len(index) * frac)
    return index[:cut], index[cut:]


def by_year_sharpe(pnl: pd.Series) -> pd.Series:
    return pnl.groupby(pnl.index.year).apply(sharpe)
