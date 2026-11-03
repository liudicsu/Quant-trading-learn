"""Shared P3 lab helpers. Learning only — not investment advice."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

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
EMC = 0.5772156649  # Euler–Mascheroni


def load_panel() -> pd.DataFrame:
    return pd.read_csv(DATA, parse_dates=["date"]).set_index("date").sort_index()


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


def apply_costs(
    pos: pd.Series,
    ret: pd.Series,
    price: pd.Series,
    *,
    n_legs: int = 1,
) -> tuple[pd.Series, pd.Series, dict]:
    """Next-open style: pos already shifted. Four-part costs; impact × turnover.

    n_legs scales both the bps stack and √impact participation (pairs = 2).
    """
    pos = pos.reindex(ret.index).fillna(0.0)
    turnover = pos.diff().abs().fillna(pos.abs())
    gross = pos * ret
    bps = (n_legs * ONE_WAY_BPS) / 1e4
    c_stack = turnover * bps
    shares = CAPITAL / price.reindex(ret.index).ffill().bfill().clip(lower=1e-6)
    participation = (n_legs * turnover * shares) / ADV_SHARES
    sigma = float(ret.std(ddof=1))
    c_impact = IMPACT_K * sigma * np.sqrt(participation.clip(lower=0.0))
    net = gross - c_stack - c_impact
    stats = {
        "mean_turnover": float(turnover.mean()),
        "one_way_bps": ONE_WAY_BPS,
        "n_legs": n_legs,
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


def psr(sr_hat: float, sr_star: float, n_obs: int, skew: float, kurt: float) -> float:
    """Bailey & López de Prado (2012) Probabilistic Sharpe Ratio. kurt = Pearson."""
    if n_obs < 3 or not np.isfinite(sr_hat):
        return float("nan")
    denom = np.sqrt(max(1e-12, 1.0 - skew * sr_hat + ((kurt - 1.0) / 4.0) * sr_hat**2))
    z = ((sr_hat - sr_star) * np.sqrt(n_obs - 1)) / denom
    return float(norm.cdf(z))


def expected_max_sr(mu: float, sigma: float, n_trials: int) -> float:
    """Bailey & López de Prado (2014) E[max SR] under Normal trials."""
    if n_trials < 2:
        return mu
    max_z = (1 - EMC) * norm.ppf(1 - 1.0 / n_trials) + EMC * norm.ppf(
        1 - 1.0 / (n_trials * np.e)
    )
    return float(mu + sigma * max_z)


def deflated_sharpe(
    pnl: pd.Series, n_trials: int, mu_sr: float = 0.0, sigma_sr: float = 1.0
) -> dict:
    """DSR = PSR(SR̂, SR*=E[max], n, γ3, γ4) on non-annualized daily SR."""
    x = pnl.dropna()
    n = len(x)
    if n < 5 or x.std(ddof=1) == 0:
        return {"n_obs": n, "sr_daily": float("nan"), "DSR": float("nan"), "SR_star": float("nan")}
    sr_daily = float(x.mean() / x.std(ddof=1))
    skew = float(x.skew())
    kurt = float(x.kurtosis() + 3.0)  # Pearson
    sr_star = expected_max_sr(mu_sr, sigma_sr, n_trials)
    return {
        "n_obs": n,
        "sr_daily": sr_daily,
        "sr_ann": sr_daily * ANN,
        "skew": skew,
        "kurt_pearson": kurt,
        "N_trials": n_trials,
        "SR_star": sr_star,
        "DSR": psr(sr_daily, sr_star, n, skew, kurt),
    }
