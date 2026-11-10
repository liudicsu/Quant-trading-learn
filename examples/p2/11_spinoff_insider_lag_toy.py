"""Spin-offs in price series and insider/ownership filing lags (checked 2026-11-10).

Sources (G1): investor.gov "Spin-Offs" (pro rata distribution of subsidiary shares); FINRA investor
insight "corporate spinoffs" (parent price adjusted lower once the new company trades); CRSP
Calculations & Index Methodologies Guide (spin-offs are "split events" with price factors applied on the
Ex-Distribution Date; shares and volume adjusted only for splits and stock dividends); CRSP CIZ guide
(July 2026; DisPERMNO links a security received in a spin-off or merger); IRS Instructions for Form 8937
(due the 45th day after the action or, if earlier, January 15 of the next year).
Sources (G2): 17 CFR 240.16a-3(g)(1) (Form 4 before the end of the second business day after the trade);
17 CFR 240.13d-1(a) (13D within five business days) and (b)(2) (13G 45 days after quarter-end);
17 CFR 240.0-3 (due date on Saturday, Sunday or holiday -> next business day); SEC HFIA page
(directors/officers of foreign private issuers file Section 16(a) reports from 2026-03-18; exemptive
orders exist for some jurisdictions, list may change); SEC HFIA FAQ (EDGAR by 10:00 p.m. ET).
Synthetic numbers; toy calendar rolls weekends only, US federal holidays are NOT handled (example dates
avoid them). The value-based back-adjustment below is a teaching version, not CRSP's factor for any real
event. Learning only: not investment, tax or legal advice.
"""
from datetime import date, datetime, timedelta

checks = 0


def check(cond, label):
    global checks
    assert cond, label
    checks += 1


def add_bdays(d, n):
    while n > 0:
        d += timedelta(days=1)
        if d.weekday() < 5:
            n -= 1
    return d


def roll_weekend(d):
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d


print("=== A. spin-off: the fake crash on the ex-distribution date ===")
p_prev, p_ex, ratio, child_px = 100.00, 81.00, 0.5, 40.00
raw = p_ex / p_prev - 1
holder = (p_ex + ratio * child_px) / p_prev - 1
adj_prev = p_prev * p_ex / (p_ex + ratio * child_px)
adj_ret = p_ex / adj_prev - 1
print(f"parent close {p_prev:.2f} -> ex-date {p_ex:.2f}; {ratio} child share per parent share, child closes {child_px:.2f}")
print(f"raw parent return      : {raw:.4%}")
print(f"holder total return    : {holder:.4%}")
print(f"adjusted prior close   : {adj_prev:.4f}  adjusted return {adj_ret:.4%}")
check(abs(raw + 0.19) < 1e-12, "raw -19%")
check(abs(holder - 0.01) < 1e-12, "holder +1%")
check(abs(adj_ret - holder) < 1e-12, "adjusted return equals holder return")
vol_prev, vol_ex = 1_000_000, 1_400_000
print(f"volume (not adjusted for spin-offs per CRSP guide): {vol_prev} -> {vol_ex}")
check((vol_prev, vol_ex) == (1_000_000, 1_400_000), "volume left as reported")

print("=== B. linking the new security; when basis information appears ===")
dis_permno = {10001: 20002}   # synthetic PERMNOs: parent -> security received
print(f"DisPERMNO link: parent 10001 -> received 20002")
check(dis_permno[10001] == 20002, "DisPERMNO link")


def f8937_due(action):
    return min(action + timedelta(days=45), date(action.year + 1, 1, 15))


for a in (date(2026, 11, 2), date(2026, 12, 20)):
    print(f"Form 8937 due (earlier of day 45 / Jan 15) for action {a}: {f8937_due(a)}")
check(f8937_due(date(2026, 11, 2)) == date(2026, 12, 17), "8937 day 45")
check(f8937_due(date(2026, 12, 20)) == date(2027, 1, 15), "8937 Jan 15")

print("=== C. Form 4 / 13D / 13G deadlines (weekend roll only) ===")
for tx in (date(2026, 11, 4), date(2026, 11, 6)):
    due = add_bdays(tx, 2)
    print(f"Form 4 trade {tx} ({tx:%a}) -> due by end of {due} ({due:%a})")
check(add_bdays(date(2026, 11, 4), 2) == date(2026, 11, 6), "Form 4 Wed -> Fri")
check(add_bdays(date(2026, 11, 6), 2) == date(2026, 11, 10), "Form 4 Fri -> Tue")
d13 = add_bdays(date(2026, 8, 3), 5)
print(f"13D: crossed 5% on 2026-08-03 (Mon) -> due {d13} ({d13:%a})")
check(d13 == date(2026, 8, 10), "13D five business days")
raw13g = date(2026, 9, 30) + timedelta(days=45)
g = roll_weekend(raw13g)
print(f"13G (45 days after 2026-09-30, Rule 0-3 weekend roll): raw {raw13g} ({raw13g:%a}) -> {g}")
check(g == date(2026, 11, 16), "13G 45 days + weekend roll")

print("=== D. the signal is usable after acceptance, not on the transaction date ===")
accepted = datetime(2026, 11, 6, 21, 40)   # before the 22:00 ET cutoff -> timely
def usable(decision_dt):
    return decision_dt > accepted
print(f"Form 4 for a 2026-11-04 trade accepted {accepted:%Y-%m-%d %H:%M} ET")
print(f"decision 2026-11-05 10:00 ET usable? {usable(datetime(2026, 11, 5, 10, 0))}")
print(f"decision 2026-11-09 09:30 ET (next session open) usable? {usable(datetime(2026, 11, 9, 9, 30))}")
check(not usable(datetime(2026, 11, 5, 10, 0)), "transaction-date leak blocked")
check(usable(datetime(2026, 11, 9, 9, 30)), "next session after acceptance")

HFIA = date(2026, 3, 18)
def fpi_form4_expected(tx):
    """Directors/officers of a foreign private issuer; an exemptive order may still apply."""
    return tx >= HFIA
print(f"FPI director trade 2026-02-10 -> Form 4 expected: {fpi_form4_expected(date(2026, 2, 10))}")
print(f"FPI director trade 2026-04-01 -> Form 4 expected: {fpi_form4_expected(date(2026, 4, 1))} (unless an exemptive order covers the jurisdiction)")
check(not fpi_form4_expected(date(2026, 2, 10)), "no Form 4 before 2026-03-18")
check(fpi_form4_expected(date(2026, 4, 1)), "Form 4 from 2026-03-18")
print(f"assertions passed: {checks}/{checks}")
print("ASSERT_spinoff_insider_lag_ok")
print("disclaimer: synthetic data; holidays not handled; no Form 4 before 2026-03-18 != no insider trades; learning only")
