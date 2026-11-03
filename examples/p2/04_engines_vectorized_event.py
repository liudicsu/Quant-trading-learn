"""P2 lab: vectorized vs minimal event-driven engine (next-open fills).
Learning only — not investment advice.

Compares libraries by official docs (read this batch):
- VectorBT: vectorized research at scale (vectorbt.dev)
- Backtrader: Cerebro + Strategy ease-of-use (backtrader.com/docu)
- Zipline Reloaded: initialize/handle_data event API (zipline.ml4trading.io)
- NautilusTrader: shared kernel Backtest/Sandbox/Live (nautilustrader.io architecture)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parent / "data" / "panel_toy.csv"
OUT = Path(__file__).resolve().parents[2] / "public" / "p2"
OUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA, parse_dates=["date"]).set_index("date").sort_index()
close = df["AAA_adj"].astype(float)
# synthetic open = prior close (honest next-open path aligns with shift(1) cc when gaps=0)
open_ = close.shift(1)
open_.iloc[0] = close.iloc[0]
rng = np.random.default_rng(4)
open_gap = open_ * (1 + rng.normal(0, 0.002, len(close)))

MA = 10
sig = (close > close.rolling(MA).mean()).astype(int)

print("=== parameters ===")
print("n", len(close), "MA", MA, "gap_seed=4", "Rf=0", "fill=next_open")


def nav_from_pnl(pnl: pd.Series) -> float:
    return float((1 + pnl.fillna(0)).cumprod().iloc[-1])


# --- vectorized baselines ---
ret_cc = close.pct_change()
ret_oc_flat = close / open_ - 1.0  # open=prev close → equals next-bar cc under shift
pnl_same = sig * ret_cc
pnl_shift = sig.shift(1) * ret_cc
# signal at t → fill open[t+1] → earn open[t+1]→close[t+1]
pnl_next_open_vec = sig * (close / open_).shift(-1).sub(1.0)

print("\n=== same signal, fill timings (vectorized) ===")
print("nav_vectorized_same_bar_cc", round(nav_from_pnl(pnl_same), 6))
print("nav_honest_shift1_cc", round(nav_from_pnl(pnl_shift), 6))
print("nav_next_open_vec_flat_open", round(nav_from_pnl(pnl_next_open_vec), 6))
print("vectorized_default_risk: same-bar close fills silently inflate results unless you shift.")


# --- minimal event-driven engine ---
class Side(Enum):
    BUY = 1
    SELL = -1


@dataclass
class Order:
    side: Side
    qty: float
    order_type: str = "market"  # market | stop
    stop_price: float | None = None
    created_i: int = 0


@dataclass
class Fill:
    i: int
    price: float
    qty: float
    side: Side


@dataclass
class Portfolio:
    cash: float = 1.0
    position: float = 0.0
    equity_curve: list[float] = field(default_factory=list)


@dataclass
class EventEngine:
    """Bar event loop: decisions on close[t]; market orders fill at next open."""

    opens: np.ndarray
    closes: np.ndarray
    pending: list[Order] = field(default_factory=list)
    fills: list[Fill] = field(default_factory=list)
    port: Portfolio = field(default_factory=Portfolio)
    positions: list[float] = field(default_factory=list)

    def submit(self, order: Order) -> None:
        self.pending.append(order)

    def _fill_markets_at_open(self, i: int) -> None:
        still = []
        for od in self.pending:
            if od.order_type == "market":
                px = float(self.opens[i])
                signed = od.qty if od.side == Side.BUY else -od.qty
                # target-style: set position toward signed absolute for long-only 0/1
                self.port.position = 1.0 if od.side == Side.BUY else 0.0
                self.fills.append(Fill(i=i, price=px, qty=od.qty, side=od.side))
            else:
                still.append(od)
        self.pending = still

    def _check_stops_intrabar(self, i: int) -> None:
        """Stop: if low-proxy (min(open,close)) breaches stop, fill at stop (toy)."""
        still = []
        lo = min(float(self.opens[i]), float(self.closes[i]))
        hi = max(float(self.opens[i]), float(self.closes[i]))
        for od in self.pending:
            if od.order_type != "stop" or od.stop_price is None:
                still.append(od)
                continue
            hit = lo <= od.stop_price <= hi or lo < od.stop_price
            if hit and self.port.position > 0 and od.side == Side.SELL:
                self.port.position = 0.0
                self.fills.append(Fill(i=i, price=float(od.stop_price), qty=od.qty, side=Side.SELL))
            else:
                still.append(od)
        self.pending = still

    def run_ma_next_open(self, signal: pd.Series) -> pd.Series:
        """Long-only: on close signal flip, queue market order filled next open."""
        n = len(self.closes)
        equity = np.ones(n)
        pos_hist = np.zeros(n)
        prev_sig = 0
        for i in range(n):
            # 1) fill market orders resting from prior close at today's open
            self._fill_markets_at_open(i)
            # 2) mark-to-market on close for equity path using current position
            if i == 0:
                equity[i] = 1.0
            else:
                # overnight: held position earns open→close; position already set at open
                r_oc = float(self.closes[i] / self.opens[i] - 1.0)
                equity[i] = equity[i - 1] * (1.0 + self.port.position * r_oc)
            pos_hist[i] = self.port.position
            # 3) decide on close; queue order for next open
            s = int(signal.iloc[i]) if i < len(signal) else 0
            if np.isnan(signal.iloc[i]):
                s = prev_sig
            if s != prev_sig:
                if s == 1 and self.port.position < 1:
                    self.submit(Order(Side.BUY, qty=1.0, order_type="market", created_i=i))
                elif s == 0 and self.port.position > 0:
                    self.submit(Order(Side.SELL, qty=1.0, order_type="market", created_i=i))
            prev_sig = s
        self.positions = list(pos_hist)
        return pd.Series(equity, index=signal.index)


# Use flat open (=prev close) so event NAV should match vectorized next-open / shift narrative
eng = EventEngine(opens=open_.to_numpy(), closes=close.to_numpy())
eq_event = eng.run_ma_next_open(sig.astype(float))
# Convert equity to pnl for comparison with vectorized next-open NAV
nav_event = float(eq_event.iloc[-1])

# Vectorized next-open with flat open: signal[t] earns ret from open[t+1] to close[t+1]
# Equivalent construction: position after fill at open[t] equals signal[t-1]
pos_event_equiv = sig.shift(1).fillna(0)
pnl_vec_match = pos_event_equiv * (close / open_ - 1.0)
nav_vec_match = nav_from_pnl(pnl_vec_match)

print("\n=== minimal event engine (next-open fills) ===")
print("nav_event_next_open", round(nav_event, 6))
print("nav_vectorized_equiv_shift1_oc", round(nav_vec_match, 6))
max_diff = float(np.nanmax(np.abs(eq_event.to_numpy() - (1 + pnl_vec_match.fillna(0)).cumprod().to_numpy())))
print("max_abs_equity_diff_event_vs_vectorized", round(max_diff, 12))
assert max_diff < 1e-9, max_diff
print("ASSERT_event_matches_vectorized")

# --- stop-loss demo: vectorized struggles; event handles path-dependent exit ---
print("\n=== when an event engine is required (stop-loss demo) ===")
print(
    "need_event_for: stop-loss / limit fills inside the bar, path-dependent exits, "
    "multi-asset partial fills, capital/margin constraints checked before send."
)

# Build a simple long-when-MA strategy with a 3% stop from entry (event)
stop_pct = 0.03


@dataclass
class StopEngine(EventEngine):
    entry_price: float | None = None

    def run_ma_with_stop(self, signal: pd.Series, stop_pct: float) -> pd.Series:
        n = len(self.closes)
        equity = np.ones(n)
        prev_sig = 0
        for i in range(n):
            self._fill_markets_at_open(i)
            # stop check after open fill, using open/close range proxy
            if self.port.position > 0 and self.entry_price is not None:
                stop_px = self.entry_price * (1 - stop_pct)
                lo = min(float(self.opens[i]), float(self.closes[i]))
                if lo <= stop_px:
                    # fill at stop
                    self.port.position = 0.0
                    self.fills.append(Fill(i=i, price=stop_px, qty=1.0, side=Side.SELL))
                    self.entry_price = None
                    # cancel pending
                    self.pending = [od for od in self.pending if od.order_type != "market"]
            if i == 0:
                equity[i] = 1.0
            else:
                # approximate: if stopped, use stop return from prior close via open path — toy
                r_oc = float(self.closes[i] / self.opens[i] - 1.0)
                equity[i] = equity[i - 1] * (1.0 + self.port.position * r_oc)
            s = int(signal.iloc[i]) if not np.isnan(signal.iloc[i]) else prev_sig
            if s == 1 and self.port.position < 1 and prev_sig != 1:
                self.submit(Order(Side.BUY, 1.0, "market", created_i=i))
            elif s == 0 and self.port.position > 0:
                self.submit(Order(Side.SELL, 1.0, "market", created_i=i))
            # track entry on next fill — set when we just bought at open this bar
            if any(f.i == i and f.side == Side.BUY for f in self.fills):
                self.entry_price = float(self.opens[i])
            if self.port.position == 0:
                self.entry_price = None if not any(f.i == i and f.side == Side.BUY for f in self.fills) else self.entry_price
            prev_sig = s if self.port.position > 0 or s == 0 else prev_sig
        return pd.Series(equity, index=signal.index)


# cleaner stop engine loop
def run_stop_demo(opens, closes, signal, stop_pct):
    n = len(closes)
    equity = np.ones(n)
    position = 0.0
    entry = None
    pending_target = None  # 0 or 1 for next open
    stop_exits = 0
    for i in range(n):
        # fill at open
        if pending_target is not None:
            position = float(pending_target)
            if position > 0:
                entry = float(opens[i])
            else:
                entry = None
            pending_target = None
        # stop during bar
        if position > 0 and entry is not None:
            stop_px = entry * (1 - stop_pct)
            lo = min(float(opens[i]), float(closes[i]))
            if lo <= stop_px:
                # exit at stop; remaining close return not earned
                # equity update: from open to stop
                r_stop = stop_px / float(opens[i]) - 1.0
                equity[i] = equity[i - 1] * (1 + r_stop) if i else 1.0
                position = 0.0
                entry = None
                stop_exits += 1
                pending_target = None
                continue
        if i == 0:
            equity[i] = 1.0
        else:
            equity[i] = equity[i - 1] * (1 + position * (float(closes[i]) / float(opens[i]) - 1))
        s = int(signal.iloc[i]) if not np.isnan(signal.iloc[i]) else 0
        desired = 1.0 if s == 1 else 0.0
        if desired != position:
            pending_target = desired
    return pd.Series(equity, index=signal.index), stop_exits


eq_stop, n_stops = run_stop_demo(open_.to_numpy(), close.to_numpy(), sig.astype(float), stop_pct)
# naive vectorized cannot express stop cleanly: compare to no-stop next-open
print("stop_pct", stop_pct, "stop_exits", n_stops)
print("nav_event_with_stop", round(float(eq_stop.iloc[-1]), 6))
print("nav_event_no_stop", round(nav_event, 6))
print(
    "teach: stop exits are path-dependent inside the bar; a single close-to-close vector "
    "cannot place the fill at the stop without an intrabar rule — use an event engine."
)

# chart
fig, ax = plt.subplots(figsize=(7.5, 4.2))
ax.plot((1 + pnl_same.fillna(0)).cumprod(), label="vectorized same-bar (optimistic)", alpha=0.8)
ax.plot(eq_event, label="event next-open (= vec equiv)", lw=2)
ax.plot(eq_stop, label=f"event + {stop_pct:.0%} stop", lw=2)
ax.set_title("Vectorized vs event engine (toy MA10)")
ax.legend()
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(OUT / "engines_event_vs_vectorized.png", dpi=120)
plt.close(fig)
print("saved_plot public/p2/engines_event_vs_vectorized.png")

print("\n=== library comparison (docs read this batch) ===")
print(
    "vectorbt: research-scale vectorized backtests on pandas/NumPy (Numba/Rust); "
    "sweep many params/assets fast — https://vectorbt.dev/ | https://github.com/polakowo/vectorbt"
)
print(
    "backtrader: Cerebro engine; write a Strategy with indicators + entry/exit logic, add data, run/plot — "
    "https://www.backtrader.com/docu/ | https://github.com/mementum/backtrader"
)
print(
    "zipline_reloaded: Pythonic event-driven initialize/handle_data API (Quantopian lineage); "
    "maintained for bugs/compat; new features → ML4T Backtest — "
    "https://zipline.ml4trading.io/ | https://github.com/stefan-jansen/zipline-reloaded"
)
print(
    "nautilustrader: Rust-native event-driven; Backtest/Sandbox/Live share NautilusKernel — "
    "https://nautilustrader.io/docs/latest/concepts/architecture/ | "
    "https://github.com/nautechsystems/nautilus_trader"
)
print(
    "ASSUMPTIONS: daily bars; MA signal; event market orders fill next open; "
    "stop demo uses min(open,close) as range proxy; Rf=0; learning only."
)
print("ASSERTS_OK")
