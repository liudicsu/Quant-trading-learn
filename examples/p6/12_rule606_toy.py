"""Rule 606-style routing table: net payment for order flow (PFOF) per 100 shares (checked 2026-11-10).

Sources: 17 CFR 242.606(a): quarterly report on non-directed held orders in NMS stocks and
non-directed customer orders in options; venues = the ten with the most orders plus any with
5% or more; net of PFOF, profit-sharing, transaction fees and rebates, total and per share,
for four order types (market, marketable limit, non-marketable limit, other); due within one
month after the quarter. 17 CFR 240.10b-10(d)(8) (definition of payment for order flow).
606(b)(3) reports use "cents per 100 shares, specified to four decimal places"; we reuse that unit.
The public 606(a) venue shares are percentages of order counts, not share counts.
The venues and numbers are synthetic. A 606 table alone says nothing about fill quality:
read it with Rule 605 statistics. Learning only, not a broker evaluation.
"""
checks = 0


def check(cond, label):
    global checks
    assert cond, label
    checks += 1


# venue -> (non-directed orders routed, shares routed, net dollars: + received, - paid)
# 606(a) venue percentages are of order counts; cents-per-100 uses share counts.
venues = {
    "MM_A": (4_800, 1_200_000, 600.0),   # 250 shares/order
    "MM_B": (3_200, 800_000, 240.0),     # 250 shares/order
    "EXCH_C": (2_000, 1_500_000, -150.0),  # 750 shares/order; order share 20%, share share 42.9%
}


def cents_per_100(shares, net_usd):
    return round(net_usd / shares * 100 * 100, 4)


total_orders = sum(o for o, _, _ in venues.values())
total_shares = sum(s for _, s, _ in venues.values())
print("venue   pct_of_orders  pct_of_shares  net_cents_per_100sh")
res = {}
pct_o, pct_s = {}, {}
for v, (orders, shares, usd) in venues.items():
    res[v] = cents_per_100(shares, usd)
    pct_o[v] = orders / total_orders
    pct_s[v] = shares / total_shares
    print(f"{v:<7} {pct_o[v]:>13.1%}  {pct_s[v]:>13.1%}  {res[v]:>19.4f}")
check(res == {"MM_A": 5.0, "MM_B": 3.0, "EXCH_C": -1.0}, "net PFOF per 100 shares")
check(abs(sum(pct_o.values()) - 1) < 1e-12 and abs(sum(pct_s.values()) - 1) < 1e-12, "both columns sum to 100%")
check(round(pct_o["EXCH_C"], 4) == 0.2 and round(pct_s["EXCH_C"], 4) == 0.4286, "order-count vs share-count ranks differ")
check(max(pct_o, key=pct_o.get) == "MM_A" and max(pct_s, key=pct_s.get) == "EXCH_C", "top venue depends on the unit")
print(f"assertions passed: {checks}/{checks}")
print("ASSERT_rule606_ok")
print("reminder: 606 = where orders went and the money; 605 = execution quality; read both. Synthetic; learning only")
