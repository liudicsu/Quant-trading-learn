"""P4 shared helpers + synthetic panel generator. Learning only — not investment advice."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

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

N_ASSETS, N_DAYS, N_IND = 200, 750, 10
MU_STRONG = 0.0025  # inflated teaching setting (RankIC ~0.1)
MU_WEAK = 0.0010  # realistic-weak foil (target RankIC ~0.02–0.05)
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


def winsorize_cs(df: pd.DataFrame, p: float = 0.01) -> pd.DataFrame:
    return df.clip(df.quantile(p, axis=1), df.quantile(1 - p, axis=1), axis=0)


def zscore_cs(df: pd.DataFrame) -> pd.DataFrame:
    mu = df.mean(axis=1)
    sd = df.std(axis=1, ddof=1).replace(0, np.nan)
    return df.sub(mu, axis=0).div(sd, axis=0)


def neutralize(df: pd.DataFrame, industry: pd.Series, logcap: pd.DataFrame) -> pd.DataFrame:
    """CS residual: factor ~ C(industry) + log_mcap. logcap MUST already be shift(1)-lagged by caller."""
    out = pd.DataFrame(np.nan, index=df.index, columns=df.columns)
    ind_dummies = pd.get_dummies(industry, prefix="ind", dtype=float)
    for dt in df.index:
        y = df.loc[dt].astype(float)
        x_m = logcap.loc[dt].astype(float)
        X = pd.concat([ind_dummies, x_m.rename("log_mcap")], axis=1).reindex(y.index)
        ok = y.notna() & X.notna().all(axis=1)
        if int(ok.sum()) < X.shape[1] + 5:
            continue
        Yv = y[ok].values
        Xv = np.column_stack([np.ones(int(ok.sum())), X.loc[ok].values])
        coef, *_ = np.linalg.lstsq(Xv, Yv, rcond=None)
        out.loc[dt, y[ok].index] = Yv - Xv @ coef
    return out


def build_factor(raw: pd.DataFrame, industry: pd.Series, log_mcap: pd.DataFrame) -> pd.DataFrame:
    """Winsorize → z → neutralize with log_mcap.shift(1) → re-z."""
    logcap_lag = log_mcap.shift(1)  # known at t: prior-day mcap only
    f_w = winsorize_cs(raw, 0.01)
    f_z = zscore_cs(f_w)
    f_n = neutralize(f_z, industry, logcap_lag)
    return zscore_cs(f_n)


def forward_sum(rets: pd.DataFrame, h: int) -> pd.DataFrame:
    out = pd.DataFrame(np.nan, index=rets.index, columns=rets.columns)
    vals = rets.values
    for i in range(len(rets) - h):
        out.iloc[i] = vals[i + 1 : i + 1 + h].sum(axis=0)
    return out


def spearman_ic(fac: pd.DataFrame, fwd: pd.DataFrame) -> pd.Series:
    ics, idx = [], []
    for dt in fac.index:
        if dt not in fwd.index:
            continue
        a, b = fac.loc[dt], fwd.loc[dt]
        ok = a.notna() & b.notna()
        if int(ok.sum()) < 30:
            continue
        ics.append(float(stats.spearmanr(a[ok], b[ok]).correlation))
        idx.append(dt)
    return pd.Series(ics, index=idx, name="RankIC")


def ls_weights(fac: pd.DataFrame, q: int = 5) -> pd.DataFrame:
    w = pd.DataFrame(0.0, index=fac.index, columns=fac.columns)
    for dt in fac.index:
        s = fac.loc[dt].dropna()
        if len(s) < 50:
            continue
        lab = pd.qcut(s, q, labels=False, duplicates="drop") + 1
        for qi, sign in [(1, -1.0), (q, 1.0)]:
            members = lab[lab == qi].index
            if len(members):
                w.loc[dt, members] = sign / len(members)
    return w


def ls_stats(fac: pd.DataFrame, rets: pd.DataFrame) -> dict:
    fwd1 = forward_sum(rets, 1)
    ic = spearman_ic(fac, fwd1)
    w = ls_weights(fac)
    net, turn = apply_costs_ls(w, rets)
    gross = (w.shift(1).fillna(0) * rets).sum(axis=1)
    return {
        "RankIC_mean": float(ic.mean()),
        "RankIC_std": float(ic.std(ddof=1)),
        "ICIR": float(ic.mean() / (ic.std(ddof=1) + 1e-12) * ANN),
        "gross_SR": float(gross.mean() / (gross.std(ddof=1) + 1e-12) * ANN),
        "net_SR": float(net.mean() / (net.std(ddof=1) + 1e-12) * ANN),
        "mean_turn": float(turn.mean()),
        "NAV_net": float((1 + net.fillna(0)).cumprod().iloc[-1]),
        "ic": ic,
        "net": net,
        "gross": gross,
        "turn": turn,
        "w": w,
    }


def _write_strength(subdir: Path, mu: float, shared: dict) -> None:
    subdir.mkdir(parents=True, exist_ok=True)
    rng = shared["rng_factory"](mu)  # not used this way
    pass


def ensure_panel(force: bool = False) -> None:
    """Generate shared covariates + strong/weak return panels."""
    marker = DATA / "strong" / "returns.csv"
    if marker.exists() and not force and (DATA / "weak" / "returns.csv").exists():
        return
    rng = np.random.default_rng(SEED)
    dates = pd.bdate_range("2020-01-02", periods=N_DAYS)
    assets = [f"A{i:03d}" for i in range(N_ASSETS)]
    ind = rng.integers(0, N_IND, size=N_ASSETS)
    log_mcap0 = 20 + 0.3 * ind + rng.normal(0, 0.8, N_ASSETS)
    beta_true = rng.normal(0, 1.0, N_ASSETS)
    beta_mkt = 0.8 + 0.3 * rng.normal(size=N_ASSETS)
    beta_size = -(log_mcap0 - log_mcap0.mean()) / log_mcap0.std()
    beta_noise = rng.normal(0, 1.0, N_ASSETS)
    # draw factor shocks once; shift means for strong vs weak
    eps_true = rng.normal(0, 0.008, N_DAYS)
    f_mkt = rng.normal(0, 0.012, N_DAYS)
    f_size = rng.normal(0, 0.006, N_DAYS)
    f_ind = rng.normal(0, 0.004, size=(N_DAYS, N_IND))
    idio = rng.normal(0, 0.012, size=(N_DAYS, N_ASSETS))
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
    # shared files at DATA root
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

    for label, mu in [("strong", MU_STRONG), ("weak", MU_WEAK)]:
        sub = DATA / label
        sub.mkdir(parents=True, exist_ok=True)
        f_true = mu + eps_true
        rets = np.zeros((N_DAYS, N_ASSETS))
        for t in range(N_DAYS):
            rets[t] = (
                beta_true * f_true[t]
                + beta_mkt * f_mkt[t]
                + beta_size * f_size[t]
                + f_ind[t, ind]
                + idio[t]
            )
        px = 100 * np.exp(np.cumsum(rets, axis=0))
        pd.DataFrame(rets, index=dates, columns=assets).to_csv(sub / "returns.csv")
        pd.DataFrame(px, index=dates, columns=assets).to_csv(sub / "prices.csv")
        pd.DataFrame({"date": dates, "f_true": f_true, "f_mkt": f_mkt, "f_size": f_size}).to_csv(
            sub / "factors_truth.csv", index=False
        )
    # legacy flat paths → strong (so old relative reads still work if any)
    for name in ("returns.csv", "prices.csv", "factors_truth.csv"):
        (DATA / name).write_bytes((DATA / "strong" / name).read_bytes())
    (DATA / "PANEL_SEED.txt").write_text(
        f"SEED={SEED} MU_STRONG={MU_STRONG} MU_WEAK={MU_WEAK} N={N_ASSETS}x{N_DAYS}\n"
    )


def load_strength(strength: str = "strong"):
    """Load returns for strong|weak plus shared covariates."""
    ensure_panel()
    assert strength in {"strong", "weak"}
    rets = pd.read_csv(DATA / strength / "returns.csv", index_col=0, parse_dates=True)
    raw = pd.read_csv(DATA / "raw_factor.csv", index_col=0, parse_dates=True)
    raw2 = pd.read_csv(DATA / "raw_factor2.csv", index_col=0, parse_dates=True)
    log_mcap = pd.read_csv(DATA / "log_mcap.csv", index_col=0, parse_dates=True)
    meta = pd.read_csv(DATA / "meta.csv").set_index("asset")
    return rets, raw, raw2, log_mcap, meta
