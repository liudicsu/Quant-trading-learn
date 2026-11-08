"""P2 lab 07: amended Rule 605 as a public cost-calibration source (offline, synthetic fixture).
Recomputes the SEC staff FAQ Example 27-1 effective spread, then applies a toy version of the covered-order
filters before computing a share-weighted effective spread to compare with this lesson's 5 bps half-spread
assumption. Sources (read by the author on checked_on 2026-11-08): SEC staff FAQ Rule 605 (Apr 1, 2026; Q11,
Q12, Q14, Q16, Q19, Q20, Q27, Q37, Q38). No real 605 files are downloaded and no 605 field names are used.
Learning only — 605 statistics describe a reporter's aggregate orders, not YOUR fills; not a broker ranking.
"""
from __future__ import annotations

print("=== A. SEC FAQ Example 27-1 (market buy 3000 sh; NBBO 25.30 x 25.60 at receipt) ===")
mid = (25.30 + 25.60) / 2
fills = [(400, 25.50), (1000, 25.55), (1600, 25.60)]
es = [2 * abs(px - mid) for _, px in fills]
for (q, px), e in zip(fills, es):
    print(f"fill {q:>4} @ {px:.2f}: effective spread = 2 x |{px:.2f} - {mid:.2f}| = {e:.2f}")
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

print("=== C. toy covered-order filter, then share-weighted effective spread (synthetic) ===")
# each order: id, shares executed, exec px, nbb, nbo, side, flags
orders = [
    ("o1", 200, 50.01, 50.00, 50.04, "buy", {}),
    ("o2", 300, 50.03, 50.00, 50.04, "sell", {}),
    ("o3", 500, 20.02, 20.00, 20.04, "buy", {}),
    ("o4", 100, 50.10, 50.00, 50.04, "buy", {"special_handling": "fill-or-kill"}),
    ("o5", 100, 50.02, 50.00, 50.04, "buy", {"special_handling": "non-IOC pegged"}),
    ("o6", 100, 50.06, 50.00, 50.04, "buy", {"directed_order_at_receiving_broker": True}),
    ("o7", 100, 49.80, 49.70, 50.30, "sell", {"nbb_or_nbo_outside_luld_bands": True}),
    ("o8", 100, 50.20, 50.00, 50.04, "buy", {"outside_regular_hours": True}),
    ("o9", 100, 50.15, 50.00, 50.04, "buy", {"nbbo_crossed_30s_or_more": True}),
    ("o10", 100, 50.25, 50.00, 50.04, "buy", {"received_within_5min_before_halt_and_outstanding": True}),
]
covered, excluded = [], []
for o in orders:
    (excluded if o[6] else covered).append(o)
for o in excluded:
    print(f"excluded {o[0]:>3}: {list(o[6].items())[0]}")
def es_bps(o):
    _, q, px, b, a, _, _ = o
    m = (b + a) / 2
    return 2 * abs(px - m) / m * 1e4
tot = sum(o[1] for o in covered)
es_cov = sum(o[1] * es_bps(o) for o in covered) / tot
es_all = sum(o[1] * es_bps(o) for o in orders) / sum(o[1] for o in orders)
print(f"covered orders: {len(covered)} ({tot} sh) -> share-weighted effective spread {es_cov:.2f} bps, implied half {es_cov / 2:.2f} bps")
print(f"if you (wrongly) ignore the exclusions: {es_all:.2f} bps")
print("lesson assumption: half-spread 5 bps -> compare ORDER OF MAGNITUDE only; 605 = reporter aggregate,")
print("covered orders, regular hours only; it is not your own fill cost and not a broker ranking.")
assert len(covered) == 3 and es_cov < es_all
print("ASSERT_rule605_toy_ok")
