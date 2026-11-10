"""When does a filing become usable? Statutory deadlines and the EDGAR 17:30 rule (checked 2026-11-10).

Sources: Form 10-K General Instruction A(2) (60 / 75 / 90 days); Form 10-Q General Instruction A.1
(40 / 45 days); 17 CFR 232.13(a)(2) (filings whose transmission starts after 5:30 p.m. Eastern
are deemed filed the next business day); investor.gov "Form 8-K" (generally four business days);
SEC Form 13F FAQ Q25 (45 days after quarter-end; 3Q 2026 due 2026-11-16).
SEC semiannual reporting (Form 10-S): proposed 2026-05-05, not adopted as of 2026-11-10; not modelled.
Toy calendar: weekends roll forward, US federal holidays are NOT handled. Learning only.
"""
from datetime import date, datetime, time, timedelta

checks = 0


def check(cond, label):
    global checks
    assert cond, label
    checks += 1


def next_bday(d):
    d += timedelta(days=1)
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d


def roll_weekend(d):
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d


def deemed_filing_date(transmission_start_et):
    """Reg S-T Rule 13(a)(2): on or before 17:30 ET -> same business day; after -> next business day."""
    d = transmission_start_et.date()
    if d.weekday() >= 5 or transmission_start_et.time() > time(17, 30):
        return next_bday(d)
    return d


DAYS = {"10-K": {"large": 60, "accelerated": 75, "other": 90},
        "10-Q": {"large": 40, "accelerated": 40, "other": 45}}


def statutory_deadline(period_end, form, filer):
    return roll_weekend(period_end + timedelta(days=DAYS[form][filer]))


def usable_value(decision_day, period_end, value, filed_on=None, filer="other", form="10-Q"):
    """Use the real filing date if known; otherwise assume the latest legal date (conservative)."""
    known_on = filed_on or statutory_deadline(period_end, form, filer)
    return value if decision_day > known_on else None   # act the next day at the earliest


print("=== A. EDGAR filing date vs transmission time (Reg S-T Rule 13) ===")
for ts in (datetime(2026, 2, 26, 17, 30), datetime(2026, 2, 26, 18, 5)):
    print(f"transmission starts {ts:%Y-%m-%d %a %H:%M} ET -> filing date {deemed_filing_date(ts):%Y-%m-%d %a}")
check(deemed_filing_date(datetime(2026, 2, 26, 17, 30)) == date(2026, 2, 26), "17:30 sharp counts as same day")
check(deemed_filing_date(datetime(2026, 2, 26, 18, 5)) == date(2026, 2, 27), "18:05 -> next business day")

print("=== B. statutory deadlines (weekend roll only) ===")
cases = [(date(2025, 12, 31), "10-K", "large", date(2026, 3, 2)),
         (date(2025, 12, 31), "10-K", "other", date(2026, 3, 31)),
         (date(2026, 9, 30), "10-Q", "large", date(2026, 11, 9)),
         (date(2026, 9, 30), "10-Q", "other", date(2026, 11, 16))]
for pe, form, filer, want in cases:
    got = statutory_deadline(pe, form, filer)
    print(f"{form} period end {pe} ({filer} filer): due {got:%Y-%m-%d %a}")
    check(got == want, f"{form} {filer} deadline")

print("=== C. 13F: holdings as of quarter-end, public up to 45 days later ===")
q3_13f = roll_weekend(date(2026, 9, 30) + timedelta(days=45))
print(f"3Q 2026 Form 13F due {q3_13f} (SEC FAQ table: November 16, 2026)")
check(q3_13f == date(2026, 11, 16), "13F 3Q 2026 deadline")

print("=== D. the period-end trap ===")
pe = date(2026, 9, 30)
print(f"decision on period end {pe}: value = {usable_value(pe, pe, 123.0)}")
print(f"decision 2026-11-17, no filing timestamp (assume latest legal date): value = {usable_value(date(2026, 11, 17), pe, 123.0)}")
print(f"decision 2026-11-03, filed 2026-10-29: value = {usable_value(date(2026, 11, 3), pe, 123.0, filed_on=date(2026, 10, 29))}")
check(usable_value(pe, pe, 123.0) is None, "period-end value is not known on period end")
check(usable_value(date(2026, 11, 17), pe, 123.0) == 123.0, "conservative lag after the deadline")
print(f"assertions passed: {checks}/{checks}")
print("ASSERT_filing_dates_ok")
print("disclaimer: deadlines are upper bounds, many firms file earlier; holidays not handled; learning only")
