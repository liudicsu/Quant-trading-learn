"""Rule 606-style routing table: net payment for order flow (PFOF) per 100 shares (checked 2026-11-10).

Sources: 17 CFR 242.606(a) (quarterly report on routing of non-directed held orders: top venues,
net PFOF received / fees paid / rebates, total and per share, by order type; due within one month
after the quarter); 17 CFR 240.10b-10(d)(8) (definition of payment for order flow).
606(b)(3) reports use "cents per 100 shares, specified to four decimal places"; we reuse that unit.
The venues and numbers are synthetic. A 606 table alone says nothing about fill quality:
read it with Rule 605 statistics. Learning only, not a broker evaluation.
"""
checks = 0


def check(cond, label):
    global checks
    assert cond, label
    checks += 1


# venue -> (non-directed market-order shares routed, net dollars: + received, - paid)
venues = {"MM_A": (1_200_000, 600.0), "MM_B": (800_000, 240.0), "EXCH_C": (500_000, -50.0)}


def cents_per_100(shares, net_usd):
    return round(net_usd / shares * 100 * 100, 4)


total = sum(s for s, _ in venues.values())
print("venue   share_of_orders  net_cents_per_100sh")
res = {}
for v, (s, usd) in venues.items():
    res[v] = cents_per_100(s, usd)
    print(f"{v:<7} {s / total:>15.1%}  {res[v]:>19.4f}")
check(res == {"MM_A": 5.0, "MM_B": 3.0, "EXCH_C": -1.0}, "net PFOF per 100 shares")
check(abs(sum(s / total for s, _ in venues.values()) - 1) < 1e-12, "routing shares sum to 100%")
check(max(res, key=res.get) == "MM_A", "largest payer identified")
print(f"assertions passed: {checks}/{checks}")
print("ASSERT_rule606_ok")
print("reminder: 606 = where orders went and the money; 605 = execution quality; read both. Synthetic; learning only")
