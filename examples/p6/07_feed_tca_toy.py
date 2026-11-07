"""Feed-aware TCA toy (S-C). Offline synthetic quotes. IEX-only top of book vs consolidated (SIP-like) NBBO:
arrival price depends on which feed you saw; a stale quote overstates/understates slippage; size caps capacity.
Alpaca Basic real-time = IEX only (checked 2026-11-08). Not a fill model of any venue. Learning only."""
sip = [(0, 100.00, 100.02), (1, 100.01, 100.03), (2, 100.03, 100.05), (3, 100.05, 100.07)]
iex = [(0, 99.99, 100.04), (1, 99.99, 100.04), (2, 100.02, 100.06), (3, 100.04, 100.08)]
def mid(q): return (q[1] + q[2]) / 2
t_arr, fill_px, side = 1, 100.05, +1
a_sip, a_iex = mid(sip[t_arr]), mid(iex[t_arr])
bps = lambda a: side * (fill_px - a) / a * 1e4
print(f"A) arrival mid SIP={a_sip:.3f} IEX={a_iex:.3f}")
print(f"B) slippage vs SIP={bps(a_sip):.2f} bps vs IEX={bps(a_iex):.2f} bps (same fill, different benchmark)")
stale = mid(sip[0])
print(f"C) stale NBBO (1 tick old) arrival={stale:.3f} -> slippage {bps(stale):.2f} bps (overstated)")
print("D) report must record: feed, quote_ts, decision_ts, fill_ts")
depth, adv, part = 300, 200_000, 0.05
for q in (200, 1_000, 20_000):
    flag = "OK" if q <= depth else ("walks book" if q <= part * adv else "exceeds 5% ADV")
    print(f"E) order {q:>6} shares vs top-of-book {depth}: {flag}")
