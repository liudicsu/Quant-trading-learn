"""US holding period: short- vs long-term, and the qualified-dividend 121-day test (checked 2026-11-10).

Sources (rule text only): IRS Topic no. 409: "if you hold the asset for more than one year before you
dispose of it, your capital gain or loss is long-term ... you generally count from the day after the
day you acquired the asset up to and including the day you disposed of the asset."
IRS Publication 550 (2025): "more than 60 days during the 121-day period that begins 60 days before
the ex-dividend date ... include the day you disposed of the stock, but not the day you acquired it."
IRS Publication 519 (2025): nonresident aliens present in the US for less than 183 days: capital gains
generally exempt unless effectively connected; dividends generally 30% or a lower treaty rate.
We do NOT reuse the day counts of the Pub 550 worked examples (they do not reconcile with the rule text).
General information only, not tax advice; this toy does not decide anyone's tax status.
"""
from datetime import date, timedelta

checks = 0


def check(cond, label):
    global checks
    assert cond, label
    checks += 1


def one_year_after(d):
    try:
        return d.replace(year=d.year + 1)
    except ValueError:            # bought on Feb 29: programming fallback only, not an IRS rule
        return d.replace(year=d.year + 1, day=28)


def long_term(buy, sell):
    """'More than one year', counting from the day after purchase through the sale day."""
    return sell > one_year_after(buy)


def qualified_days(buy, sell, ex_date):
    start = ex_date - timedelta(days=60)
    end = start + timedelta(days=120)             # 121 days including both ends
    held = (buy + timedelta(days=k) for k in range(1, (sell - buy).days + 1))   # skip buy day, include sell day
    return sum(1 for d in held if start <= d <= end)


print("=== A. short- vs long-term ===")
b = date(2025, 3, 10)
for s in (date(2026, 3, 10), date(2026, 3, 11)):
    print(f"bought {b}, sold {s}: {'long-term' if long_term(b, s) else 'short-term'}")
check(not long_term(b, date(2026, 3, 10)), "exactly one year is not more than one year")
check(long_term(b, date(2026, 3, 11)), "one day more is long-term")

print("=== B. qualified-dividend holding test (ex-date 2026-03-16) ===")
ex = date(2026, 3, 16)
print(f"121-day window: {ex - timedelta(days=60)} to {ex - timedelta(days=60) + timedelta(days=120)}")
check(ex - timedelta(days=60) == date(2026, 1, 15) and ex + timedelta(days=60) == date(2026, 5, 15), "window ends")
for buy, sell in ((date(2026, 3, 1), date(2026, 4, 30)), (date(2026, 3, 10), date(2026, 5, 10))):
    n = qualified_days(buy, sell, ex)
    print(f"bought {buy}, sold {sell}: {n} days in window -> {'more than 60' if n > 60 else 'not more than 60'}")
check(qualified_days(date(2026, 3, 1), date(2026, 4, 30), ex) == 60, "60 days is not enough")
check(qualified_days(date(2026, 3, 10), date(2026, 5, 10), ex) == 61, "61 days passes the holding test")


def nonresident_note(days_in_us):
    return ("Pub 519: capital gains generally exempt unless effectively connected; dividends generally 30% or treaty rate"
            if days_in_us < 183 else "Pub 519: 183 days or more -> net US-source capital gains taxed at 30% (or treaty rate)")


print(f"nonresident, 120 days in the US: {nonresident_note(120)}")
check(nonresident_note(120).startswith("Pub 519: capital gains generally exempt"), "183-day note (text only, no tax amount)")
print(f"assertions passed: {checks}/{checks}")
print("ASSERT_holding_period_ok")
print("disclaimer: general information, not tax advice; does not decide residency or treaty status")
