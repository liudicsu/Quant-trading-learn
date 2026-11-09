"""P2 lab 07: amended Rule 605 as a public cost-calibration source (offline, synthetic fixture).
Recomputes the SEC staff FAQ Example 27-1 effective spread, then applies a toy version of the covered-order
filters before computing a share-weighted effective spread to compare with this lesson's 5 bps half-spread
assumption. Sources (read by the author on checked_on 2026-11-08): SEC staff FAQ Rule 605 (Apr 1, 2026; Q9,
Q11, Q12, Q14, Q16, Q19, Q20, Q27, Q28, Q30, Q37, Q38) and 17 CFR 242.600(b)(8), (10), (27) (checked 2026-11-09). No real 605 files are downloaded and no 605 field names are used.
Learning only — 605 statistics describe a reporter's aggregate orders, not YOUR fills; not a broker ranking.
"""
from __future__ import annotations

def signed_es(side: str, px: float, mid: float) -> float:
    """17 CFR 242.600(b)(8): buy = 2 x (exec - mid); sell = 2 x (mid - exec). Keep the sign:
    a negative value means the fill was on the customer's favourable side of the mid (not a negative fee)."""
    return 2 * (px - mid) if side == "buy" else 2 * (mid - px)

# sign tests: buy above mid and sell below mid cost money (+); fills across the mid are negative
assert abs(signed_es("buy", 10.02, 10.00) - 0.04) < 1e-12 and abs(signed_es("sell", 9.98, 10.00) - 0.04) < 1e-12
assert signed_es("buy", 9.99, 10.00) < 0 and signed_es("sell", 10.01, 10.00) < 0

print("=== A. SEC FAQ Example 27-1 (market buy 3000 sh; NBBO 25.30 x 25.60 at receipt) ===")
mid = (25.30 + 25.60) / 2
fills = [(400, 25.50), (1000, 25.55), (1600, 25.60)]
es = [signed_es("buy", px, mid) for _, px in fills]
for (q, px), e in zip(fills, es):
    print(f"fill {q:>4} @ {px:.2f}: buy effective spread = 2 x ({px:.2f} - {mid:.2f}) = {e:.2f}")
w = sum(q * e for (q, _), e in zip(fills, es)) / sum(q for q, _ in fills)
print(f"share-weighted effective spread = {w:.4f} USD  (FAQ: 0.10/0.20/0.30 weighted by 400/1000/1600)")
assert [round(x, 2) for x in es] == [0.10, 0.20, 0.30] and abs(w - 0.24) < 1e-12

print("=== B. FAQ Example 38-1 share-weighted average percentage price improvement ===")
trades = [("buy", 300, 20.00, 20.04, 20.03), ("sell", 500, 25.00, 25.04, 25.00),
          ("buy", 400, 23.00, 23.06, 23.08), ("sell", 350, 21.00, 21.08, 21.02)]
net, denom = 0.0, 0.0
for side, q, bid, ask, px in trades:
    quote = ask if side == "buy" else bid
    imp = (quote - px) if side == "buy" else (px - quote)      # >0 improved, <0 outside the quote
    net += q * imp
    denom += q * (bid + ask) / 2
print(f"net price improvement = {net:.2f} USD; sum(mid x shares) = {denom:,.0f}; pct = {net / denom:.6%}")
assert abs(net - 2.0) < 1e-9 and abs(denom - 35092) < 1e-6

print("=== C. toy report coverage, then signed effective spread (synthetic) ===")
# Self-made fixture; field names are NOT Rule 605 / OES field names.
# each order: id, type (mkt = market or marketable limit; nmlo = non-marketable limit), side,
#             shares executed, exec px, nbb, nbo (at the ES benchmark time), flags
orders = [
    ("o1", "mkt", "buy", 200, 50.01, 50.00, 50.04, {}),
    ("o2", "mkt", "sell", 300, 50.03, 50.00, 50.04, {}),
    ("o3", "mkt", "buy", 500, 20.02, 20.00, 20.04, {}),
    ("o4", "mkt", "buy", 100, 50.10, 50.00, 50.04, {"special_handling": "fill-or-kill"}),
    ("o5", "mkt", "buy", 100, 50.02, 50.00, 50.04, {"special_handling": "non-IOC pegged"}),
    ("o6", "mkt", "buy", 100, 50.06, 50.00, 50.04, {"directed_order_at_receiving_broker": True}),
    ("o7", "mkt", "sell", 100, 49.80, 49.70, 50.30, {"nbb_or_nbo_outside_luld_bands": True}),
    ("o8", "mkt", "buy", 100, 50.20, 50.00, 50.04, {"received_outside_regular_hours": True}),
    ("o9", "mkt", "buy", 100, 50.15, 50.00, 50.04, {"nbbo_crossed_30s_or_more": True}),
    ("o10", "mkt", "buy", 100, 50.25, 50.00, 50.04, {"halt": {"received_min_before": 3, "outstanding_at_halt": True}}),
    # R43 exceptions (FAQ Q20, Q28): these NMLOs ARE in report coverage ...
    ("o11", "nmlo", "buy", 100, 50.01, 50.00, 50.04, {"note": "received pre-open, later executable in regular hours"}),
    ("o12", "nmlo", "sell", 100, 50.03, 50.00, 50.04, {"note": "received during a halt, executable after resumption"}),
    # R47 (FAQ Q20 point 3, Examples 20-4 / 20-6): for an NMLO the "<5 min before a halt" test uses FIRST-EXECUTABLE time.
    # first_exec_min_before = None means it first became executable only after trading resumed.
    ("o13", "nmlo", "buy", 100, 50.01, 50.00, 50.04,
     {"note": "received 10 min before halt, first executable 2 min before, outstanding at halt",
      "halt": {"received_min_before": 10, "first_exec_min_before": 2, "outstanding_at_halt": True}}),
    ("o14", "nmlo", "sell", 100, 50.03, 50.00, 50.04,
     {"note": "received 2 min before halt, first executable only after resumption",
      "halt": {"received_min_before": 2, "first_exec_min_before": None, "outstanding_at_halt": True}}),
]
EXCLUDING = {"special_handling", "directed_order_at_receiving_broker", "nbb_or_nbo_outside_luld_bands",
             "received_outside_regular_hours", "nbbo_crossed_30s_or_more"}

def halt_excluded(o) -> bool:
    """Toy of FAQ Q20: excluded if the relevant time is LESS THAN 5 minutes before a halt and the order is still
    outstanding when the halt starts. Relevant time: receipt for market/marketable limit; first-executable for NMLO."""
    h = o[7].get("halt")
    if not h or not h["outstanding_at_halt"]:
        return False
    t = h["received_min_before"] if o[1] == "mkt" else h.get("first_exec_min_before")
    return t is not None and t < 5

def excluded_by(o):
    hits = [kv for kv in o[7].items() if kv[0] in EXCLUDING]
    if o[1] == "nmlo":   # an NMLO received pre-open can still be covered once executable in regular hours (FAQ Q28)
        hits = [kv for kv in hits if kv[0] not in ("received_outside_regular_hours",)]
    if halt_excluded(o):
        hits.append(("halt", "<5 min before halt (" + ("receipt" if o[1] == "mkt" else "first executable") + "), outstanding"))
    return hits
covered = [o for o in orders if not excluded_by(o)]
for o in orders:
    if excluded_by(o):
        print(f"excluded {o[0]:>3}: {excluded_by(o)[0]}")
for o in covered:
    if o[1] == "nmlo":
        print(f"covered  {o[0]:>3} (NMLO): {o[7]['note']}")
# ... but plain NMLOs being in the report does not mean an effective spread is computed for them (FAQ Q30).
es_set = [o for o in covered if o[1] == "mkt"]

def ratio_bps(rows):
    """17 CFR 242.600(b)(10): average effective spread / average midpoint (both share-weighted)."""
    q = sum(o[3] for o in rows)
    avg_es = sum(o[3] * signed_es(o[2], o[4], (o[5] + o[6]) / 2) for o in rows) / q
    avg_mid = sum(o[3] * (o[5] + o[6]) / 2 for o in rows) / q
    return avg_es, avg_mid, avg_es / avg_mid * 1e4

def mean_of_bps(rows):  # toy metric, NOT the official statistic
    q = sum(o[3] for o in rows)
    return sum(o[3] * signed_es(o[2], o[4], (o[5] + o[6]) / 2) / ((o[5] + o[6]) / 2) * 1e4 for o in rows) / q

avg_es, avg_mid, bps = ratio_bps(es_set)
toy = mean_of_bps(es_set)
_, _, bps_all = ratio_bps([o for o in orders if o[1] == "mkt"])
print(f"report coverage: {len(covered)} orders; ES computed for {len(es_set)} market/marketable orders ({sum(o[3] for o in es_set)} sh)")
print(f"avg signed ES = {avg_es:.4f} USD; avg mid = {avg_mid:.2f} USD; avg % effective spread = {bps:.4f} bps")
print(f"(toy mean of per-order bps = {toy:.4f} bps -- a different statistic, do not call it the 605 number)")
print(f"if you (wrongly) ignore the exclusions: {bps_all:.2f} bps")
print("negative here = fills on the customer's side of the mid in THIS toy sample; not a negative fee, not a promise.")
print("lesson assumption: half-spread 5 bps -> compare ORDER OF MAGNITUDE only; 605 = reporter aggregate,")
print("covered orders; it is not your own fill cost and not a broker ranking.")
assert [o[0] for o in es_set] == ["o1", "o2", "o3"] and {"o11", "o12", "o14"} <= {o[0] for o in covered}
ids_excluded = {o[0] for o in orders if excluded_by(o)}
assert "o13" in ids_excluded and "o10" in ids_excluded and "o14" not in ids_excluded
assert abs(avg_es + 0.01) < 1e-9 and abs(avg_mid - 35.02) < 1e-9 and abs(bps - (-0.01 / 35.02 * 1e4)) < 1e-9
assert abs(toy - bps) > 0.5 and bps < bps_all
print("ASSERT_rule605_toy_ok")
