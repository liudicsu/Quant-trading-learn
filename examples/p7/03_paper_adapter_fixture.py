"""P7 lab 03: MockBroker adapter on a HAND-MADE event fixture + US-session vs Shanghai-date reconciliation.
Learning only — not investment advice. No real broker, no API key, no network, no order is ever sent.
"""
from __future__ import annotations
from datetime import datetime
from zoneinfo import ZoneInfo

NY, SH = ZoneInfo("America/New_York"), ZoneInfo("Asia/Shanghai")


class MockBroker:
    """Document-shaped toy: idempotent client_order_id, reject, partial fill, disconnect, halt."""
    def __init__(self, script):
        self.script, self.orders, self.fills, self.sent = script, {}, [], 0

    def submit(self, coid, sym, qty):
        if coid in self.orders:                      # retry with same id -> no duplicate intent
            return self.orders[coid]["status"] + " (dup ignored)"
        self.sent += 1
        ev = self.script.get(coid, "fill")
        st = {"reject": "rejected", "halt": "held_halted", "partial": "partially_filled",
              "disconnect": "unknown"}.get(ev, "filled")
        self.orders[coid] = {"sym": sym, "qty": qty, "status": st}
        if st == "filled": self.fills.append((coid, qty))
        if st == "partially_filled": self.fills.append((coid, qty // 2))
        if ev == "disconnect": self.fills.append((coid, qty))   # broker filled; we never saw ack
        return st


print("=== 1. adapter fixture ===")
b = MockBroker({"o2": "reject", "o3": "partial", "o4": "disconnect", "o5": "halt"})
intents = [("o1", "SYN_US_01", 100), ("o2", "SYN_US_02", 50), ("o3", "SYN_US_03", 80),
           ("o4", "SYN_US_04", 40), ("o4", "SYN_US_04", 40), ("o5", "SYN_US_05", 30)]
for coid, s, q in intents:
    print(f"{coid} {s} {q:>4} -> {b.submit(coid, s, q)}")
print(f"intents={len(intents)} unique_orders_sent={b.sent}")
local_pos = {"o1": 100, "o3": 40}                    # what our loop recorded
broker_pos = {c: q for c, q in b.fills}
gaps = {k: (local_pos.get(k, 0), v) for k, v in broker_pos.items() if local_pos.get(k, 0) != v}
print(f"reconcile after reconnect: gaps={gaps} -> trust broker ledger, log, re-derive position")

print("=== 2. paper != live (document-level notes, not tested on an account) ===")
print("Alpaca paper: fills simulated vs NBBO; qty NOT checked vs NBBO size; no dividends simulated")
print("IBKR paper: fills from top of book; some order types unsupported (e.g. VWAP, Auction)")

print("=== 3. S-D: US session date vs Shanghai calendar date ===")
fills_utc = ["2026-07-06T13:31:00+00:00", "2026-07-06T19:59:00+00:00", "2026-12-07T20:59:00+00:00", "2026-11-27T17:59:00+00:00"]
for f in fills_utc:
    t = datetime.fromisoformat(f)
    print(f"fill {f}: NY session date {t.astimezone(NY):%Y-%m-%d %H:%M} | Shanghai {t.astimezone(SH):%Y-%m-%d %H:%M}")
print("-> book by NY session date; a Shanghai 'next morning' fill belongs to the previous US session")
print("tzdata: zoneinfo (pin your tzdata version in requirements for reproducibility)")
print("disclaimer: hand-made fixture; learning only")
