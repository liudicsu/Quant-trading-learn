"""Section 16(b) short-swing profit window (checked 2026-11-11).

Source:
- 15 U.S.C. 78p(b): for the purpose of preventing the unfair use of information which may have
  been obtained by a beneficial owner, director, or officer by reason of his relationship to
  the issuer, any profit realized by him from any purchase and sale, or any sale and purchase,
  of any equity security of such issuer (other than an exempted security) within any period of
  less than six months ... shall inure to and be recoverable by the issuer, irrespective of
  any intention on the part of such beneficial owner, director, or officer in entering into
  such transaction of holding the security purchased or of not repurchasing the security sold
  for a period exceeding six months.

The people in scope are the same directors, officers and >10% beneficial owners who file
Form 4 (see data-cleaning). This script only tests the "less than six months" window.
Learning only; not legal advice and not an insider-trading signal.
"""
from datetime import date

checks = 0


def check(cond, label):
    global checks
    assert cond, label
    checks += 1


def add_months(d, months):
    year = d.year + (d.month - 1 + months) // 12
    month = (d.month - 1 + months) % 12 + 1
    day = d.day
    # Clamp to the last day of the target month (e.g. 31 Jan + 1 month -> 28/29 Feb).
    for last in (31, 30, 29, 28):
        try:
            return date(year, month, min(day, last))
        except ValueError:
            continue
    raise ValueError(d)


def less_than_six_months(first, second):
    a, b = (first, second) if first <= second else (second, first)
    return b < add_months(a, 6)


print("=== Section 16(b): purchase and sale (or sale and purchase) in less than six months ===")
buy = date(2026, 1, 15)
for sell, expect in (
    (date(2026, 6, 10), True),
    (date(2026, 7, 20), False),
):
    got = less_than_six_months(buy, sell)
    print(f"  buy {buy} / sell {sell}: less than six months? {got}")
    check(got is expect, f"{sell}")
print("the statute says 'less than six months'; this toy uses calendar months and only tests dates that are clearly inside or outside. It does not decide the exact-day edge.")

print("the same window applies to a sale first and a repurchase later")
sale = date(2026, 2, 2)
repurchase = date(2026, 7, 1)
print(f"  sale {sale} / repurchase {repurchase}: less than six months? {less_than_six_months(sale, repurchase)}")
check(less_than_six_months(sale, repurchase), "sale then repurchase")
check(not less_than_six_months(sale, date(2026, 8, 3)), "six months later is outside")
print("if the window is open, any profit inures to the issuer irrespective of the insider's intention")
print("this is not a Form 4 trading signal")

print(f"OK {checks} assertions")
