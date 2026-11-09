"""Wash sale: the disallowed loss moves into the new shares' basis (checked 2026-11-10).

Source: IRS Publication 550 (2025), "Wash Sales", incl. "More or less stock
bought than sold": replacement shares bought within 30 days BEFORE or AFTER
the sale are matched to the shares sold in the order they were bought,
beginning with the first shares bought. All three cases below are the IRS's
own examples.
Not modelled (read Pub 550): repurchase inside an IRA/Roth IRA (the
disallowed loss is NOT added to the new basis there), purchases by a spouse
or a corporation you control (also a wash sale), options/contracts.
Applies only if US tax rules apply to you; readers resident in China should
not assume US individual tax rules apply automatically.
Learning only, not tax or investment advice.
"""
from datetime import date


def in_window(sale_day, buy_day):
    """30 days before to 30 days after the sale (61 calendar days incl. sale day)."""
    return abs((buy_day - sale_day).days) <= 30


def wash_sale(sale_day, shares_sold, loss, buys):
    """buys: list of (day, shares, cost) of replacement lots (not the lot sold).

    Returns (disallowed, deductible, per-lot basis adjustments)."""
    per_share = loss / shares_sold
    left = shares_sold
    adj = []
    for day, sh, cost in sorted(buys, key=lambda b: b[0]):
        m = min(sh, left) if in_window(sale_day, day) else 0
        left -= m
        adj.append((day, sh, cost, m * per_share))
    disallowed = sum(a[3] for a in adj)
    return disallowed, loss - disallowed, adj


checks = 0
print("A. IRS main example: 100 sh bought 1,000, sold 750, 100 sh rebought 800 within 30 days")
dis, ded, adj = wash_sale(date(2026, 6, 1), 100, 250, [(date(2026, 6, 11), 100, 800)])
print(f"   disallowed {dis:.0f}, deductible {ded:.0f}, new basis {adj[0][2] + adj[0][3]:.0f}")
assert dis == 250 and ded == 0 and adj[0][2] + adj[0][3] == 1050; checks += 1
dis31, _, _ = wash_sale(date(2026, 6, 1), 100, 250, [(date(2026, 7, 2), 100, 800)])
print(f"   rebought on day +31 instead: disallowed {dis31:.0f}")
assert dis31 == 0; checks += 1

print("B. IRS 'less bought than sold' example: lots bought BEFORE the sale count too")
buys = [(date(2024, 12, 13), 50, 2750), (date(2024, 12, 20), 25, 1125)]
dis, ded, adj = wash_sale(date(2025, 1, 3), 100, 1000, buys)
for d, sh, c, a in adj:
    print(f"   lot {d} {sh} sh cost {c}: +{a:.0f} -> basis {c + a:.0f}")
print(f"   disallowed {dis:.0f}, deductible {ded:.0f}")
assert dis == 750 and ded == 250; checks += 1
assert [c + a for _, _, c, a in adj] == [3250, 1375]; checks += 1

print("C. IRS 'more bought than sold' example: match in purchase order")
buys = [(date(2025, 2, d), 50, 0) for d in (3, 4, 5, 6)]   # costs not given; adjustments only
dis, ded, adj = wash_sale(date(2025, 1, 29), 100, 1000, buys)
for d, sh, c, a in adj:
    print(f"   lot {d} {sh} sh: basis adjustment +{a:.0f}")
assert dis == 1000 and [a for *_, a in adj] == [500, 500, 0, 0]; checks += 1

print(f"assertions passed: {checks}/5")
assert checks == 5
print("ASSERT_wash_sale_basis_ok")
print("disclaimer: taxable-account toy; IRA/Roth, spouse and controlled-corporation cases not modelled; not tax advice")
