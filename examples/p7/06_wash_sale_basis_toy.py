"""Wash sale: the disallowed loss moves into the new shares' basis (checked 2026-11-10).

Source: IRS Publication 550, "Wash Sales" (Example 1: buy 100 shares for
$1,000, sell them for $750, buy 100 again within 30 days for $800 ->
$250 loss disallowed, new basis $1,050). Applies only if US tax rules apply
to you; readers resident in China should not assume US individual tax rules
apply automatically. Equal share quantities only (partial-quantity rules are
not modelled here). Learning only, not tax or investment advice.
"""
from datetime import date, timedelta


def in_window(sale_day, buy_day):
    """30 days before to 30 days after the sale (61 calendar days incl. sale day)."""
    return abs((buy_day - sale_day).days) <= 30


def wash_sale(cost_old, proceeds, cost_new, sale_day, buy_day):
    loss = cost_old - proceeds
    if loss <= 0 or not in_window(sale_day, buy_day):
        return {"wash": False, "disallowed": 0.0, "new_basis": cost_new}
    return {"wash": True, "disallowed": loss, "new_basis": cost_new + loss}


checks = 0
sale = date(2026, 6, 1)
r = wash_sale(1000, 750, 800, sale, sale + timedelta(days=10))
print("IRS Pub 550 Example 1: cost 1,000 -> sold 750 -> rebought 800 on day +10")
print(f"wash sale: {r['wash']}, disallowed loss {r['disallowed']:.0f}, new basis {r['new_basis']:.0f}")
assert r["wash"] and r["disallowed"] == 250 and r["new_basis"] == 1050; checks += 1

later = 1200
print(f"later sale of the new shares at {later}: gain {later - r['new_basis']:.0f} (not {later - 800:.0f}): the 250 loss was postponed, not lost")
assert later - r["new_basis"] == 150; checks += 1

r31 = wash_sale(1000, 750, 800, sale, sale + timedelta(days=31))
print(f"rebought on day +31: wash sale {r31['wash']}, loss 250 allowed")
assert not r31["wash"]; checks += 1

rb = wash_sale(1000, 750, 800, sale, sale - timedelta(days=30))
print(f"bought 30 days BEFORE the sale: wash sale {rb['wash']} (the window runs both ways)")
assert rb["wash"]; checks += 1

print(f"assertions passed: {checks}/4")
assert checks == 4
print("ASSERT_wash_sale_basis_ok")
print("disclaimer: equal quantities only; pre-tax backtests stay the course default; not tax advice")
