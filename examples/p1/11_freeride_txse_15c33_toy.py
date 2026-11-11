"""Cash-account payment period and 90-day freeze, TXSE sessions, 15c3-3 reserve toy
(checked 2026-11-11). Synthetic dates; weekdays only, no holidays.

Sources:
- 12 CFR 220.2: "Payment period means the number of business days in the standard
  securities settlement cycle in the United States, as defined in paragraph (a) of SEC
  Rule 15c6-1 ... plus two business days." After T+1 (from 2024-05-28) that is 3 business
  days, not "pay by T+1 or it is a free-ride."
- 12 CFR 220.8(a): in a cash account the customer agrees to make full cash payment
  before selling the security.
- 12 CFR 220.8(c): if a nonexempted security is sold (or delivered to another broker)
  without having been previously paid for in full, the privilege of delaying payment
  beyond the trade date is withdrawn for 90 calendar days following the date of sale.
  The freeze does not apply if, within the payment period, full payment is received (or
  a check clears) and the sale proceeds are not withdrawn prior to that payment.
- investor.gov "Freeriding": during the freeze the investor may still buy, but must
  fully pay on the trade date.
- TXSE Rule 11.001 / session definitions and the 2026-05-06 trader alert: Pre-Market
  8:00-9:30, Market / Regular 9:30-4:00, Post-Market 4:00-5:00 p.m. Eastern.
- 17 CFR 240.15c3-3(e)(1): a Special Reserve Bank Account for the Exclusive Benefit of
  Customers, with cash and/or qualified securities computed under Exhibit A (15c3-3a).
  This toy uses a one-line credits-minus-debits remainder; it is not the full formula.

Learning only; not legal advice and not a broker recommendation.
"""
from datetime import date, datetime, time, timedelta

checks = 0


def check(cond, label):
    global checks
    assert cond, label
    checks += 1


def add_weekdays(start, n):
    d, seen = start, 0
    while seen < n:
        d += timedelta(days=1)
        if d.weekday() < 5:
            seen += 1
    return d


print("=== A. Regulation T payment period is settlement cycle plus two business days ===")
settlement_cycle = 1  # Rule 15c6-1(a) since 2024-05-28
payment_period = settlement_cycle + 2
print(f"standard settlement cycle T+{settlement_cycle}; payment period = {payment_period} business days")
check(payment_period == 3, "payment_period")
trade = date(2026, 7, 6)  # Monday
due = add_weekdays(trade, payment_period)
print(f"cash-account purchase on {trade} has payment period ending {due}")
check(due == date(2026, 7, 9), "due Thu")

print("=== B. Freeriding and the 90-calendar-day freeze ===")
sale = date(2026, 7, 7)  # sold next day, not yet paid
paid_already = False
freeze = sale + timedelta(days=90)
print(f"sold on {sale} before paying in full: 90-calendar-day freeze ends {freeze}")
check(freeze == date(2026, 10, 5), "freeze end")
check(paid_already is False, "unpaid")
print("during the freeze, new purchases must be paid for on the trade date (the delay-beyond-trade-date privilege is withdrawn)")

print("=== C. Same sale, but paid with other funds inside the payment period; proceeds not withdrawn ===")
paid_by = date(2026, 7, 8)
proceeds_withdrawn = False
no_freeze = (paid_by <= due) and (not proceeds_withdrawn)
print(f"full payment {paid_by} (on or before {due}); proceeds withdrawn? {proceeds_withdrawn} -> freeze? {not no_freeze}")
check(no_freeze is True, "exception")
print("selling before T+1 settlement is not automatically freeriding if you pay with other funds on time and do not take the sale proceeds first")

print("=== D. TXSE official sessions (Eastern Time) ===")
sessions = (
    (time(8, 0), "pre-market"),
    (time(9, 29), "pre-market"),
    (time(9, 30), "regular"),
    (time(15, 59), "regular"),
    (time(16, 0), "post-market"),
    (time(16, 59), "post-market"),
    (time(17, 0), "closed"),
    (time(7, 59), "closed"),
)


def txse_session(t):
    if time(8, 0) <= t < time(9, 30):
        return "pre-market"
    if time(9, 30) <= t < time(16, 0):
        return "regular"
    if time(16, 0) <= t < time(17, 0):
        return "post-market"
    return "closed"


for t, expect in sessions:
    got = txse_session(t)
    print(f"  {t.strftime('%H:%M')} ET -> {got}")
    check(got == expect, str(t))
print("SIP participant / market-center identifier for TXSE is F; pre-launch tape data will not contain F prints")

print("=== E. Rule 15c3-3 reserve toy (credits minus debits, not the full Exhibit A formula) ===")
credits, debits = 100_000.0, 40_000.0
reserve = credits - debits
print(f"customer credits {credits:.0f} - debits {debits:.0f} -> reserve at least {reserve:.0f}")
check(reserve == 60_000.0, "reserve")
print("the carrying broker must also keep possession or control of fully paid and excess-margin securities; this is separate from SIPC")
print(f"assertions passed: {checks}/{checks}")
