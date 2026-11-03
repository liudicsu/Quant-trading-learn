"""P5 shared helpers. Learning only — not investment advice.
Uses the P4 WEAK-signal panel (MU_WEAK) as the ML playground.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

import importlib.util

_P4 = Path(__file__).resolve().parents[1] / "p4" / "_common.py"
_spec = importlib.util.spec_from_file_location("p4_common", _P4)
_p4 = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_p4)
ANN = _p4.ANN
MU_WEAK = _p4.MU_WEAK
apply_costs_ls = _p4.apply_costs_ls
ensure_panel = _p4.ensure_panel
load_strength = _p4.load_strength

DATA = Path(__file__).resolve().parent / "data"
PUBLIC = Path(__file__).resolve().parents[2] / "public" / "p5"
PUBLIC.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)

# Subsample for tractable CV (stated in labs)
N_ASSETS_USE = 50
HORIZON = 5
EMBARGO = 5
N_FOLDS = 5
SEED = 0
EMC = 0.5772156649


def load_weak_subset(n_assets: int = N_ASSETS_USE, seed: int = SEED):
    ensure_panel()
    rets, raw, raw2, log_mcap, meta = load_strength("weak")
    rng = np.random.default_rng(seed)
    cols = list(rets.columns)
    pick = sorted(rng.choice(cols, size=min(n_assets, len(cols)), replace=False))
    return (
        rets[pick],
        raw[pick],
        raw2[pick],
        log_mcap[pick],
        meta.loc[pick],
        MU_WEAK,
    )


def psr(sr_hat: float, sr_star: float, n_obs: int, skew: float, kurt: float) -> float:
    """Bailey & López de Prado (2012) PSR. kurt = Pearson."""
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
    """DSR = PSR(SR̂, SR*=E[max], …) on non-annualized daily SR (Bailey–LdP 2014)."""
    x = pnl.dropna()
    n = len(x)
    if n < 5 or x.std(ddof=1) == 0:
        return {"n_obs": n, "sr_daily": float("nan"), "DSR": float("nan"), "SR_star": float("nan")}
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


def build_features(rets: pd.DataFrame) -> pd.DataFrame:
    """Alpha158-style toy features — ALL lagged (shift 1) so feature[t] uses only info ≤ t-1 close… 
    Actually: using past returns ending at t is OK for predicting t+1..; we use features as of t
    built from rets[t-L:t] inclusive of t's return only if we trade next bar.
    Convention here: feature at date t uses returns up to and including t; label uses t+1..t+h.
    """
    feats = {}
    for w in (1, 5, 10, 20):
        feats[f"mom_{w}"] = rets.rolling(w).sum()
    feats["vol_20"] = rets.rolling(20).std(ddof=1)
    feats["vol_5"] = rets.rolling(5).std(ddof=1)
    # CS ranks of mom_20
    mom20 = feats["mom_20"]
    feats["rank_mom20"] = mom20.rank(axis=1, pct=True)
    # lag everything by 1 so feature[t] has no same-bar future; mom_w at t uses rets[t-w+1..t]
    # then shift(1) → feature known before ret[t] if we wanted; for label fwd from t+1,
    # using unshifted rolling ending at t is standard (info through t, predict t+1+).
    # Lab text: features end at t; labels start t+1 — no look-ahead.
    panel = pd.concat(feats, axis=1)
    panel.columns = [f"{a}_{b}" for a, b in panel.columns] if False else panel.columns
    # flatten MultiIndex if concat on keys
    if isinstance(panel.columns, pd.MultiIndex):
        panel.columns = [f"{a}__{b}" for a, b in panel.columns]
    return panel


def features_long(rets: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return X long (date,asset) and a wide feature dict stack."""
    frames = []
    for w in (1, 5, 10, 20):
        frames.append(rets.rolling(w).sum().stack().rename(f"mom_{w}"))
    frames.append(rets.rolling(20).std(ddof=1).stack().rename("vol_20"))
    frames.append(rets.rolling(5).std(ddof=1).stack().rename("vol_5"))
    frames.append(rets.rolling(20).sum().rank(axis=1, pct=True).stack().rename("rank_mom20"))
    X = pd.concat(frames, axis=1)
    X.index = X.index.set_names(["date", "asset"])
    return X


def forward_label(rets: pd.DataFrame, h: int = HORIZON) -> pd.Series:
    """Sum of returns over [t+1, t+h] — label at t. Look-ahead check: uses only future path."""
    vals = rets.values
    out = pd.DataFrame(np.nan, index=rets.index, columns=rets.columns)
    for i in range(len(rets) - h):
        out.iloc[i] = vals[i + 1 : i + 1 + h].sum(axis=0)
    s = out.stack(); s.index = s.index.set_names(["date", "asset"]); return s.rename("fwd_ret")


TB_K = 1.0  # pt = sl = TB_K * sigma_t (AFML ch.3 vol-scaled)
VOL_SPAN = 20  # EWMA / rolling window for daily vol


def lagged_ewma_vol(rets: pd.DataFrame, span: int = VOL_SPAN) -> pd.DataFrame:
    """Per-asset daily vol from EWMA of squared returns, then shift(1) — known at t."""
    var = rets.pow(2).ewm(span=span, min_periods=max(5, span // 2), adjust=False).mean()
    return np.sqrt(var).shift(1)


def triple_barrier_labels(
    rets: pd.DataFrame,
    k: float = TB_K,
    max_h: int = HORIZON,
    vol: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """AFML ch.3 triple-barrier with volatility-scaled horizontal bands.

    For each asset/time t: pt = sl = k * sigma_t, where sigma_t is lagged EWMA vol.
    Fixed 2% bands are wrong: high-vol names hit barriers by noise, low-vol names
    almost never touch — labels become vol-driven rather than information-driven.
    Look-ahead: sigma_t uses only past returns (shift 1); path walk uses t+1.. only.
    """
    if vol is None:
        vol = lagged_ewma_vol(rets)
    n_t, n_a = rets.shape
    side = np.zeros((n_t, n_a))
    touch = np.full((n_t, n_a), np.nan)
    pt_used = np.full((n_t, n_a), np.nan)
    R = rets.values
    S = vol.values
    for i in range(n_t - max_h):
        for j in range(n_a):
            sig = S[i, j]
            if not np.isfinite(sig) or sig <= 0:
                continue
            pt = sl = float(k * sig)
            pt_used[i, j] = pt
            cum = 0.0
            hit = 0
            for step in range(1, max_h + 1):
                cum += R[i + step, j]
                if cum >= pt:
                    hit = 1
                    touch[i, j] = step
                    break
                if cum <= -sl:
                    hit = -1
                    touch[i, j] = step
                    break
            if hit == 0:
                hit = 1 if cum > 0 else (-1 if cum < 0 else 0)
                touch[i, j] = max_h
            side[i, j] = hit
    side_df = pd.DataFrame(side, index=rets.index, columns=rets.columns)
    touch_df = pd.DataFrame(touch, index=rets.index, columns=rets.columns)
    pt_df = pd.DataFrame(pt_used, index=rets.index, columns=rets.columns)
    side_s = side_df.stack(); touch_s = touch_df.stack(); pt_s = pt_df.stack()
    for s in (side_s, touch_s, pt_s):
        s.index = s.index.set_names(["date", "asset"])
    return pd.DataFrame({"tb_side": side_s, "tb_touch": touch_s, "tb_pt": pt_s})


def meta_labels(primary_side: pd.Series, tb: pd.DataFrame) -> pd.Series:
    """AFML meta-label: y=1 if primary side agrees with barrier outcome (trade), else 0."""
    side = tb["tb_side"]
    y = ((primary_side.reindex(side.index).fillna(0) * side) > 0).astype(float)
    y.name = "meta_y"
    return y


def make_ml_frame(rets: pd.DataFrame, meta: pd.DataFrame | None = None, raw: pd.DataFrame | None = None) -> pd.DataFrame:
    X = features_long(rets)
    y_fwd = forward_label(rets, HORIZON)
    vol = lagged_ewma_vol(rets)
    tb = triple_barrier_labels(rets, vol=vol)
    primary = np.sign(X["mom_20"]).replace(0, np.nan)
    meta_y = meta_labels(primary, tb)
    df = X.join(y_fwd, how="inner").join(tb, how="left").join(meta_y, how="left")
    # oracle columns (upper bound): beta_true and raw_factor (as-of t, CS)
    if meta is not None and "beta_true" in meta.columns:
        beta = meta["beta_true"]
        df["oracle_beta"] = df.index.get_level_values("asset").map(beta)
    if raw is not None:
        raw_s = raw.stack()
        raw_s.index = raw_s.index.set_names(["date", "asset"])
        df["oracle_raw"] = raw_s.reindex(df.index)
    df = df.dropna(subset=["mom_5", "vol_20", "fwd_ret", "tb_side"])
    return df


def purged_kfold_indices(dates, n_folds: int, label_horizon: int, embargo: int):
    """AFML ch.7: purged K-fold + embargo on the DATE axis.

    Label at date t spans returns (t+1 .. t+h). For a test block [te_lo, te_hi),
    purge any train t with label span overlapping the test block, and embargo
    `embargo` bars immediately after the test block (also removed from train).
    """
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
        # earliest train index that would still overlap test via label horizon
        purge_lo = max(0, te_lo - label_horizon)
        emb_hi = min(n, te_hi + embargo)
        train_mask = np.ones(n, dtype=bool)
        train_mask[purge_lo:emb_hi] = False  # drop purge+test+embargo
        train_dates = dates[train_mask]
        folds.append((train_dates, test_dates))
    return folds


def pooled_spearman(pred: pd.Series, y: pd.Series) -> float:
    """COUNTEREXAMPLE metric: pools all (date,asset) pairs — mixes TS + CS variation."""
    df = pd.concat([pred, y], axis=1).dropna()
    if len(df) < 30:
        return float("nan")
    return float(df.iloc[:, 0].corr(df.iloc[:, 1], method="spearman"))


# backward-compatible alias (labs should prefer mean_daily_cs_ic)
spearman_ic_series = pooled_spearman


def daily_cs_ic(pred: pd.Series, y: pd.Series) -> pd.Series:
    """PRIMARY: Spearman RankIC within each date (cross-section), then series over time."""
    df = pd.concat([pred.rename("p"), y.rename("y")], axis=1).dropna()
    ics = df.groupby(level=0).apply(
        lambda g: g["p"].corr(g["y"], method="spearman") if len(g) >= 10 else np.nan
    )
    return ics.dropna()


def mean_daily_cs_ic(pred: pd.Series, y: pd.Series) -> dict:
    """Primary scorecard: mean daily CS RankIC, t-stat, ICIR."""
    ics = daily_cs_ic(pred, y)
    if len(ics) < 5:
        return {"mean_ic": float("nan"), "std_ic": float("nan"), "t_stat": float("nan"), "ICIR": float("nan"), "n_days": len(ics), "ics": ics}
    mu = float(ics.mean())
    sd = float(ics.std(ddof=1))
    t = mu / (sd / np.sqrt(len(ics))) if sd > 0 else float("nan")
    icir = mu / (sd + 1e-12) * ANN
    return {"mean_ic": mu, "std_ic": sd, "t_stat": float(t), "ICIR": float(icir), "n_days": len(ics), "ics": ics}


def pred_to_ls_pnl(pred: pd.Series, rets: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """Daily CS quintile L/S from predictions; costs via shared model."""
    wide = pred.unstack()
    wide = wide.reindex(index=rets.index, columns=rets.columns)
    w = pd.DataFrame(0.0, index=wide.index, columns=wide.columns)
    for dt in wide.index:
        s = wide.loc[dt].dropna()
        if len(s) < 20:
            continue
        lab = pd.qcut(s, 5, labels=False, duplicates="drop") + 1
        for qi, sign in [(1, -1.0), (5, 1.0)]:
            members = lab[lab == qi].index
            if len(members):
                w.loc[dt, members] = sign / len(members)
    return apply_costs_ls(w, rets)


def add_noise_features(X: pd.DataFrame, n_noise: int = 30, seed: int = 1) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    noise = pd.DataFrame(
        rng.normal(size=(len(X), n_noise)),
        index=X.index,
        columns=[f"noise_{i}" for i in range(n_noise)],
    )
    return pd.concat([X, noise], axis=1)
