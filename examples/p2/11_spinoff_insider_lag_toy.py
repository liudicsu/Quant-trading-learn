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

print("=== E. Form 4 transaction codes; Form 3 / Form 5 clocks ===")
# Form 4, General Instruction 8 (SEC 1474 (03-26); OMB expires August 31, 2029):
# "Use the code that most appropriately describes the transaction."
# P — Open market or private purchase of non-derivative or derivative security
# S — Open market or private sale of non-derivative or derivative security
# V in the appropriate column marks a transaction "voluntarily reported earlier
# than required" (otherwise leave that column blank) — not a purchase/sale code.
# A — Grant, award or other acquisition pursuant to Rule 16b-3(d)
# F — Payment of exercise price or tax liability by delivering or withholding
#     securities incident to the receipt, exercise or vesting of a security issued
#     in accordance with Rule 16b-3
# M — Exercise or conversion of derivative security exempted pursuant to Rule 16b-3
# G — Bona fide gift
# Other listed codes include C / E / H / O / X (derivative, except 16b-3-exempt
# exercises/conversions), D, I, L, W, Z, J ("Other acquisition or disposition
# (describe transaction)"), K used in addition for an equity swap or similar
# instrument (e.g. "S/K" or "P/K"), and U (tender in a change-of-control
# transaction). This toy is a classifier, not an insider-trading signal.
# Form 3 / Form 5: 15 U.S.C. 78p(a)(2)(B) requires the initial statement
# "within 10 days after he or she becomes such beneficial owner, director, or
# officer, or within such shorter time as the Commission may establish by rule."
# This lab does not invent a shorter Commission deadline (none was found in
# 16a-3). 17 CFR 240.16a-3(a) assigns the initial statement to Form 3, changes
# to Form 4, and annual statements to Form 5. 16a-3(f): a Form 5 "shall be filed
# within 45 days after the issuer's fiscal year end"; "no Form 5 shall be
# required where all transactions otherwise required to be reported on the
# Form 5 have been reported before the due date." Calendar days as written,
# not rewritten as business days. If that calendar last day falls on a
# Saturday, Sunday or holiday, Rule 0-3 (already taught in section C) lets
# the filing be made on the next business day.
# Do not add Form 13H to this public lag box.


def primary_code(token):
    # K is used in addition (e.g. "S/K" or "P/K"); V is an earlier-reporting flag.
    parts = [p for p in token.replace(" ", "").split("/") if p and p != "V"]
    return parts[0] if parts else ""


def has_v_flag(token):
    return "V" in token.replace(" ", "").split("/")


def is_open_market_or_private_ps(token):
    return primary_code(token) in {"P", "S"}


rows = (
    ("P", True, False, "open market or private purchase"),
    ("S", True, False, "open market or private sale"),
    ("A", False, False, "grant, award or other acquisition under 16b-3(d)"),
    ("M", False, False, "16b-3-exempt exercise or conversion"),
    ("F", False, False, "payment of exercise price or tax by delivering or withholding"),
    ("G", False, False, "bona fide gift"),
    ("P/K", True, False, "open-market/private purchase plus equity-swap code K"),
    ("S/K", True, False, "open-market/private sale plus equity-swap code K"),
    ("J", False, False, "other acquisition or disposition (describe)"),
    ("U", False, False, "tender in a change-of-control transaction"),
)
print("  code  open-market-or-private P/S?  V-flag?  note")
for token, expect_ps, expect_v, note in rows:
    ps, v = is_open_market_or_private_ps(token), has_v_flag(token)
    print(f"  {token:<6} {ps}  {v}  {note}")
    check(ps is expect_ps and v is expect_v, token)
check(has_v_flag("P/V") is True and is_open_market_or_private_ps("P/V") is True, "V is a flag, not a purchase/sale code")
print("  V marks a transaction voluntarily reported earlier than required; it is not a purchase/sale code")
print("  do not treat every Form 4 acquisition as an open-market buy")

became = date(2026, 3, 2)
form3 = became + timedelta(days=10)
print(f"Form 3: became an officer {became} -> initial statement due within 10 days: {form3}")
check(form3 == date(2026, 3, 12), "Form 3 is 10 calendar days as written in 15 U.S.C. 78p(a)(2)(B)")
fye = date(2025, 12, 31)
raw_form5 = fye + timedelta(days=45)
form5 = roll_weekend(raw_form5)
print(f"Form 5 (45 days after FYE {fye}, Rule 0-3 weekend roll): raw {raw_form5} ({raw_form5:%a}) -> {form5}")
check(raw_form5 == date(2026, 2, 14), "Form 5 is FYE + 45 calendar days")
check(form5 == date(2026, 2, 16), "Form 5 Rule 0-3 weekend roll")

def form5_required(already_reported_before_due_date):
    # 16a-3(f): no Form 5 where all transactions otherwise required have been
    # reported before the due date.
    return not already_reported_before_due_date


print(f"Form 5 required if every item was already reported before the due date? {form5_required(True)}")
check(form5_required(True) is False, "16a-3(f): no Form 5 if everything already reported")
check(form5_required(False) is True, "Form 5 is required when unreported items remain")

print("=== F. 13G to 13D switch and 13d-3 beneficial ownership ===")
# 17 CFR 240.13d-1(e): a person that has reported more than 5% on Schedule 13G
# under paragraph (b) or (c), or is required to report the acquisition but has
# not yet filed, shall file a Schedule 13D "within five business days" if the
# person has acquired or holds the securities with a purpose or effect of
# changing or influencing control of the issuer and is still above 5%.
# From that time "until the expiration of the tenth day from the date of the
# filing of the Schedule 13D," the person shall not vote or direct the voting
# of those securities, or acquire an additional beneficial ownership interest
# in any equity securities of the issuer, nor of any person controlling the
# issuer.
# 13d-1(f): persons reporting on 13G pursuant to paragraph (c) shall file a
# 13D "within five business days after the date on which the person's
# beneficial ownership equals or exceeds 20 percent of the class," with the
# same standstill from the 20% acquisition until the tenth day from the 13D
# filing. Do not copy the 20% cap onto every 13G filer.
# 13d-1(g): a paragraph (b) 13G filer who ceases to be a person specified in
# (b)(1)(ii) or determines it no longer holds the securities in the ordinary
# course of business shall file a 13D or a 13G amendment, as applicable,
# "within five business days thereafter," if still above 5%.
# 13d-1(i)(2): "business day means any day, other than Saturday, Sunday, or a
# Federal holiday, from 12 a.m. to 11:59 p.m., Eastern Time."
# This toy rolls weekends only; the example dates avoid federal holidays.
# Do not revive the pre-2023 "10 calendar days" filing clock. "Tenth day" is
# the standstill after the 13D is filed.
# 17 CFR 240.13d-3(a): beneficial owner includes any person who, directly or
# indirectly, through any contract, arrangement, understanding, relationship,
# or otherwise has or shares voting power and/or investment power — not merely
# shares of record. 13d-3(c): aggregate the class. 13d-3(d)(1)(i): a person
# is deemed the beneficial owner if the person has the right to acquire
# beneficial ownership within sixty days (option, warrant, right, or
# conversion); if that right is acquired with a purpose or effect of changing
# or influencing control, the person is deemed the owner immediately upon
# such acquisition. Securities not outstanding which are subject to such
# options, warrants, rights or conversion privileges are deemed outstanding
# for that person's percentage only.
# This toy is not a full beneficial-ownership compliance engine.


def add_bdays_from(d, n):
    return add_bdays(d, n)


def tenth_day_from(filing):
    """Calendar 'tenth day from the date of the filing' (not a filing clock)."""
    return filing + timedelta(days=10)


intent = date(2026, 8, 3)  # Monday, still above 5%
d13 = add_bdays_from(intent, 5)
print(f"intent-change path (13d-1(e)), still above 5%: purpose on {intent} ({intent:%a}) -> 13D due {d13} ({d13:%a})")
check(d13 == date(2026, 8, 10), "switch filing clock is five business days")
filed = d13
standstill_end = tenth_day_from(filed)
print(f"13D filed {filed}: standstill until the expiration of the tenth day from the filing date = {standstill_end}")
check(standstill_end == date(2026, 8, 20), "tenth day is the standstill, not a 10-calendar-day filing clock")
print("pre-2023 10-calendar-day filing clock is not used for the switch")

cross20 = date(2026, 9, 8)  # Tuesday
d20 = add_bdays_from(cross20, 5)


def path_f_20pct_applies(paragraph):
    return paragraph == "c"


print(f"paragraph (c) filer reaches 20% on {cross20} -> 13D due {d20} ({d20:%a})")
check(d20 == date(2026, 9, 15), "20% path: five business days")
check(path_f_20pct_applies("c") is True and path_f_20pct_applies("b") is False, "20% path is the paragraph (c) path in 13d-1(f)")
print("do not copy the 20% cap onto a paragraph (b) 13G filer")
elig_loss = date(2026, 10, 5)  # Monday
g_due = add_bdays_from(elig_loss, 5)
print(f"paragraph (b) filer loses ordinary-course / (b)(1)(ii) eligibility on {elig_loss}, still above 5% -> 13D or 13G amendment due {g_due}")
check(g_due == date(2026, 10, 12), "13d-1(g) is also five business days if still above 5%")
print("business day (13d-1(i)(2)) = any day other than Saturday, Sunday, or a Federal holiday, 12 a.m. to 11:59 p.m. ET")

outstanding = 10_000_000
record_sh = 490_000
warrant = 600_000
deemed = record_sh + warrant
denom = outstanding + warrant
pct = deemed / denom
other_pct = 500_000 / outstanding
print(f"4.9% of record ({record_sh}) plus a 60-day exercisable warrant for {warrant}")
print(f"  deemed shares {deemed}; percentage uses warrant in the denominator only for this person: {pct:.4%}")
print(f"  another holder of 500,000 shares of record: {other_pct:.4%} (warrant not outstanding for that person)")
check(abs(pct - 1_090_000 / 10_600_000) < 1e-15, "60-day warrant is deemed ownership; underlying outstanding only for this person")
check(abs(other_pct - 0.05) < 1e-15, "do not treat shares of record as the whole 13(d)/13(g) position")

def deemed_owner_now(days_to_exercise, control_purpose):
    # 13d-3(d)(1)(i): 60-day right-to-acquire is deemed ownership; a
    # control-purpose right is counted immediately upon acquisition.
    if control_purpose:
        return True
    return days_to_exercise <= 60


print(f"60-day warrant, no control purpose: deemed now? {deemed_owner_now(60, False)}")
print(f"90-day warrant, no control purpose: deemed now? {deemed_owner_now(90, False)}")
print(f"90-day warrant, control purpose: deemed now? {deemed_owner_now(90, True)} (counted immediately)")
check(deemed_owner_now(60, False) is True, "60-day branch")
check(deemed_owner_now(90, False) is False, "outside 60 days, no control purpose")
check(deemed_owner_now(90, True) is True, "control-purpose right counted immediately")

print(f"assertions passed: {checks}/{checks}")
print("ASSERT_spinoff_insider_lag_ok")
print("disclaimer: synthetic data; holidays not handled; no Form 4 / 13G-13D signal; learning only")
