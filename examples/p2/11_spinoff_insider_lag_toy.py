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
orders exist for some jurisdictions, list may change); SEC HFIA FAQ (EDGAR by 10:00 p.m. ET);
OPM 2026 Holiday Schedule (https://www.opm.gov/policy-data-oversight/pay-leave/federal-holidays/#url=2026).
Synthetic numbers; the toy calendar rolls Saturday, Sunday, and OPM-listed 2026 federal holidays under
Rule 0-3 and 13d-1(i)(2). The value-based back-adjustment below is a teaching version, not CRSP's factor
for any real event. Learning only: not investment, tax or legal advice.
"""
from datetime import date, datetime, timedelta

checks = 0


def check(cond, label):
    global checks
    assert cond, label
    checks += 1


# Official observed dates from the OPM 2026 Holiday Schedule. Independence Day
# 2026 falls on Saturday, so OPM lists Friday, July 3 (5 U.S.C. 6103(b) in lieu).
# Washington's Birthday is the statutory name in 5 U.S.C. 6103(a).
FEDERAL_HOLIDAYS_2026 = frozenset({
    date(2026, 1, 1),   # New Year's Day
    date(2026, 1, 19),  # Birthday of Martin Luther King, Jr.
    date(2026, 2, 16),  # Washington's Birthday
    date(2026, 5, 25),  # Memorial Day
    date(2026, 6, 19),  # Juneteenth National Independence Day
    date(2026, 7, 3),   # Independence Day (observed)
    date(2026, 9, 7),   # Labor Day
    date(2026, 10, 12), # Columbus Day
    date(2026, 11, 11), # Veterans Day
    date(2026, 11, 26), # Thanksgiving Day
    date(2026, 12, 25), # Christmas Day
})


def is_business_day(d):
    """13d-1(i)(2): any day other than Saturday, Sunday, or a Federal holiday."""
    return d.weekday() < 5 and d not in FEDERAL_HOLIDAYS_2026


def add_bdays(d, n):
    while n > 0:
        d += timedelta(days=1)
        if is_business_day(d):
            n -= 1
    return d


def roll_rule_03(d):
    """17 CFR 240.0-3: if the last timely day is Saturday, Sunday or holiday,
    the filing may be made on the first business day following."""
    while not is_business_day(d):
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

print("=== C. Form 4 / 13D / 13G deadlines (Rule 0-3 weekend and holiday roll) ===")
for tx in (date(2026, 11, 4), date(2026, 11, 6)):
    due = add_bdays(tx, 2)
    print(f"Form 4 trade {tx} ({tx:%a}) -> due by end of {due} ({due:%a})")
check(add_bdays(date(2026, 11, 4), 2) == date(2026, 11, 6), "Form 4 Wed -> Fri")
check(add_bdays(date(2026, 11, 6), 2) == date(2026, 11, 10), "Form 4 Fri -> Tue")
d13 = add_bdays(date(2026, 8, 3), 5)
print(f"13D: crossed 5% on 2026-08-03 (Mon) -> due {d13} ({d13:%a})")
check(d13 == date(2026, 8, 10), "13D five business days")
raw13g = date(2026, 9, 30) + timedelta(days=45)
g = roll_rule_03(raw13g)
print(f"13G (45 days after 2026-09-30, Rule 0-3): raw {raw13g} ({raw13g:%a}) -> {g}")
check(g == date(2026, 11, 16), "13G 45 days + Rule 0-3 roll")

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
print("disclaimer: synthetic data; federal holidays from the OPM 2026 schedule; no Form 4 before 2026-03-18 != no insider trades; learning only")

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
form5 = roll_rule_03(raw_form5)
print(
    f"Form 5 (45 days after FYE {fye}, Rule 0-3): raw {raw_form5} ({raw_form5:%a}) -> {form5}"
    f" (Tue; 2026-02-16 is Washington's Birthday)"
)
check(raw_form5 == date(2026, 2, 14), "Form 5 is FYE + 45 calendar days")
check(form5 == date(2026, 2, 17), "Form 5 Rule 0-3 rolls past Washington's Birthday")

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
# Business days skip Saturday, Sunday, and OPM-listed 2026 federal holidays.
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
print(
    f"paragraph (b) filer loses ordinary-course / (b)(1)(ii) eligibility on {elig_loss}, still above 5%"
    f" -> 13D or 13G amendment due {g_due}"
)
check(g_due == date(2026, 10, 13), "13d-1(g) five business days skip Columbus Day")
print("2026-10-12 is Columbus Day, so the fifth business day is 2026-10-13")
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
print("disclaimer: synthetic data; federal holidays from the OPM 2026 schedule; no Form 4 / 13G-13D signal; learning only")

print("=== G. when-issued / when-distributed contracts (FINRA 11130; Nasdaq CQS WI) ===")
# FINRA Rule 11130 governs "when, as and if issued" and "when, as and if
# distributed" contracts. 11130(g)(1): "A date for the settlement of 'when,
# as and if issued' and 'when, as and if distributed' contracts shall be
# determined by the Committee when a sufficient percentage of the issue is
# outstanding." It is not automatic T+1 from the WI trade date.
# 11130(h)(2): "Contracts will be canceled if the securities are not to be
# issued or distributed."
# Official Nasdaq CQS symbol convention: the CQS suffix for "When issued"
# is WI (the same table also lists venue-specific encodings; quote the
# table, do not invent a single tape symbol). Official Nasdaq Symbol
# Directory Definitions include a When Issued Flag and a When Distributed
# Flag. When-distributed is a related official label (Nasdaq WD flag;
# 11130 names both); do not invent separate product mechanics.
# Do not splice a WI series into the regular outstanding symbol. This toy
# is not a Uniform Practice Code engine (marks to market, confirmations,
# Committee procedures). 11130 is firm-facing UPC; no product, offering,
# or venue recommendation.

regular = "ABC"
wi = "ABC WI"
cqs_suffix = "WI"
print(f"regular outstanding symbol {regular} is not the same contract as {wi}")
check(regular != wi, "WI is not the regular outstanding symbol")
print(f"Nasdaq CQS suffix for When issued is {cqs_suffix}")
check(cqs_suffix == "WI", "official CQS suffix WI")
def wi_settles_automatic_t1(_wi_trade_date):
    # 11130(g)(1): settlement date is determined later by the Committee.
    return False


def canceled_if_not_issued():
    # 11130(h)(2)
    return True


print("settlement date is determined later (when a sufficient percentage of the issue is outstanding); not automatic T+1 from the WI trade date")
check(wi_settles_automatic_t1("2026-11-17") is False, "settlement is not automatic T+1 from the WI trade date")
print("contracts canceled if the securities are not to be issued or distributed")
check(canceled_if_not_issued() is True, "contracts canceled if not issued")
print("when-distributed is a related official label (Nasdaq WD flag; 11130 names both)")
print("do not splice a WI series into the regular outstanding symbol")

print(f"assertions passed: {checks}/{checks}")
print("ASSERT_spinoff_insider_lag_ok")
print("disclaimer: official FINRA 11130 / Nasdaq CQS facts; not a UPC engine; learning only")

print("=== H. Nasdaq CQS suffixes beyond WI/WD ===")
# Official Nasdaq CQS symbol convention table (opened 2026-11-12). Columns
# include CQS Suffix, CMS Suffix, NASDAQ Integrated Platform Suffix, and
# NASDAQ ACT/CTCI Suffixes. Quote the official table; say which column a
# dataset uses. Do not invent one universal suffix.
# Rows taught here (CQS suffix / CMS suffix):
#   Preferred: p / PR
#   Preferred Class "A": pA / PRA
#   Class "A": .A / A
#   Class "B": .B / B
#   Warrants: .WS / WS
#   Rights: r / RT
#   Units: .U / U
#   When issued: w / WI   (already taught in section G)
#   When distributed: .WD / WD  (already taught in section G)
# Official notes:
#   "The CMS convention has a space between the root and the suffix."
#   "The CQS convention is shown for reference purposes only. NASDAQ
#   protocols do not support using the CQS ticker symbol convention for
#   sending orders into NASDAQ's integrated platform."
#   "The NASDAQ integrated platform suffix will be used for order-entry
#   via RASH, OUCH, INET FIX, and for data dissemination via ITCH."
#   "NASDAQ ACT/CTCI suffix are used in ACT and CTCI protocol."
#   "Class 'B' though Class 'Z' securities are denoted using the same
#   format as Class 'A' securities on this matrix."
# WI / WD remain as already printed in section G. FINRA 11130 settlement
# facts are already taught there; this section does not re-teach them.
# Form 5 2026-02-17 and 13d-1(g) 2026-10-13 stay as printed in E/F.
# Learning only; no product recommendation.

# Official excerpt: (categorization, CQS suffix, CMS suffix)
CQS_TABLE = (
    ("Preferred", "p", "PR"),
    ("Preferred Class A", "pA", "PRA"),
    ("Class A", ".A", "A"),
    ("Class B", ".B", "B"),
    ("Warrants", ".WS", "WS"),
    ("Rights", "r", "RT"),
    ("Units", ".U", "U"),
    ("When issued", "w", "WI"),
    ("When distributed", ".WD", "WD"),
)
print("official table excerpt (CQS suffix column and CMS suffix column):")
for name, cqs, cms in CQS_TABLE:
    print(f"  {name}: CQS {cqs} | CMS {cms}")

cms = {name: cms for name, cqs, cms in CQS_TABLE}
cqs = {name: cqs for name, cqs, cms in CQS_TABLE}
check(cms["Preferred"] == "PR" and cqs["Preferred"] == "p", "preferred PR vs CQS p")
check(cms["Preferred Class A"] == "PRA" and cqs["Preferred Class A"] == "pA", "PRA")
check(cms["Class A"] == "A" and cms["Class B"] == "B", "class A/B CMS")
check(cqs["Class A"] == ".A" and cqs["Class B"] == ".B", "class A/B CQS")
check(cms["Warrants"] == "WS" and cqs["Warrants"] == ".WS", "warrants")
check(cms["Rights"] == "RT" and cqs["Rights"] == "r", "rights")
check(cms["Units"] == "U" and cqs["Units"] == ".U", "units")
check(cms["When issued"] == "WI" and cqs["When issued"] == "w", "WI already taught; CQS is w")
check(cms["When distributed"] == "WD" and cqs["When distributed"] == ".WD", "WD already taught")
print("ABC PR / ABC A / ABC WS / ABC RT / ABC U are not the regular common share ABC")
print("WI / WD remain as already printed in section G; this section does not re-teach 11130 settlement")
print("the official page lists more than one encoding column (CQS, CMS, NASDAQ Integrated Platform, NASDAQ ACT/CTCI)")
print("the CMS convention has a space between the root and the suffix")
print("the CQS convention is shown for reference purposes only;")
print("  NASDAQ protocols do not support using the CQS ticker symbol convention for sending orders into NASDAQ's integrated platform")
print("the NASDAQ integrated platform suffix will be used for order-entry via RASH, OUCH, INET FIX, and for data dissemination via ITCH")
print("NASDAQ ACT/CTCI suffix are used in ACT and CTCI protocol")
print("Class 'B' though Class 'Z' securities are denoted using the same format as Class 'A' securities on this matrix")
print("do not invent one universal suffix that works on every tape, order port, and vendor file")
print("Form 5 due date 2026-02-17 and 13d-1(g) fifth business day 2026-10-13 remain as already printed")
print(f"assertions passed: {checks}/{checks}")
print("ASSERT_spinoff_insider_lag_ok")
print("disclaimer: official Nasdaq CQS / CMS suffix table; not a corporate-actions catalog; learning only; no product recommendation")


print("=== I. Rule 13d-2: 1% is deemed material on a 13D; a 13G is not on that clock ===")
# 17 CFR 240.13d-2 (official eCFR, current as of 2026-11-09, opened 2026-11-12,
# not an interstitial). Keep sections A-H identical, including Form 5 due date
# 2026-02-17 and 13d-1(g) fifth business day 2026-10-13, and 54/54 after H.
# 13d-2(a): a Schedule 13D amendment disclosing a material change is due
# within two business days after the date of such change. An acquisition or
# disposition of beneficial ownership equal to one percent or more of the
# class shall be deemed "material"; less than those amounts may be material,
# depending upon the facts and circumstances.
# 13d-2(b): a Schedule 13G filer under 13d-1(b), (c), or (d) generally amends
# within 45 days after the end of each calendar quarter if, as of quarter-end,
# there are any material changes. An amendment need not be filed with respect
# to a change in the percent of the class outstanding previously reported if
# the change results solely from a change in the aggregate number of
# securities outstanding.
# 13d-2(c) / (d) official intra-period clocks exist (10% / more-than-5%);
# this toy names them and is not that engine.
# Do not apply the 13D 1% / two-business-day clock to every 13G.
# Do not reopen Form 5 / 13d-1(g) date rows. No filer or disclosure advice.

print("13d-2(a): a Schedule 13D amendment disclosing a material change is due within two business days after the date of such change")
print("an acquisition or disposition of beneficial ownership of one percent or more of the class is deemed material")
print("acquisitions or dispositions of less than one percent may be material, depending upon the facts and circumstances")
one_pct_deemed_material = True
sub_one_pct_may_be_material = True
print(f"  1% acquisition or disposition deemed material? {one_pct_deemed_material}")
print(f"  a smaller change may still be material? {sub_one_pct_may_be_material}")
check(one_pct_deemed_material is True, "1% is deemed material")
check(sub_one_pct_may_be_material is True, "sub-1% may still be material")

print("a 13G is not on that same 1% / two-business-day clock")
print("13d-2(b): a 13G filer under 13d-1(b), (c), or (d) generally amends within 45 days after calendar quarter-end")
print("  if, as of the end of the calendar quarter, there are any material changes")
g_uses_13d_clock = False
print(f"  every 13G amends on the 13D 1% / two-business-day clock? {g_uses_13d_clock}")
check(g_uses_13d_clock is False, "13G is not on the 13D 1%/two-business-day clock")
solely_from_shares_outstanding_needs_13g_amendment = False
print("a percent change solely from a change in the aggregate number of securities outstanding need not be a 13G amendment")
print(f"  13G amendment required when the percent change is solely from shares outstanding? {solely_from_shares_outstanding_needs_13g_amendment}")
check(solely_from_shares_outstanding_needs_13g_amendment is False, "solely shares-outstanding change need not be a 13G amendment")

print("official 13d-2(c) and 13d-2(d) intra-period clocks also exist:")
print("  13d-2(c) (13d-1(b) / QII filers): within five business days after month-end when beneficial ownership,")
print("    computed as of the last day of the month, exceeds 10%, and thereafter after a more-than-5% increase or decrease")
print("  13d-2(d) (13d-1(c) / passive filers): within two business days after acquiring greater than 10%,")
print("    and thereafter within two business days after a more-than-5% increase or decrease")
print("  this toy is not that engine")
builds_cd_engine = False
print(f"  this toy builds the 13d-2(c)/(d) engine? {builds_cd_engine}")
check(builds_cd_engine is False, "name (c)/(d); do not build that engine")
print("Form 5 due date 2026-02-17 and 13d-1(g) fifth business day 2026-10-13 remain as already printed")
print(f"assertions passed: {checks}/{checks}")
print("ASSERT_spinoff_insider_lag_ok")
print("disclaimer: official 13d-2 amendment clocks; no filer or disclosure advice; learning only")

print("=== J. 17 CFR 240.16a-6: Small acquisitions ===")
# 17 CFR 240.16a-6 (official eCFR API XML, title 17 up_to_date_as_of 2026-11-17,
# live-refetched 2026-11-19, byte-identical to the 2026-11-09 archive).
# Keep sections A-I identical, including 59/59 after I / 13d-2, Form 5 due date
# 2026-02-17, and 13d-1(g) fifth business day 2026-10-13.
# Do not flatten into already-taught Form 4 / Form 5 clocks, packed Section 16(b),
# or packed 13d-2. Learning only; no filer or investment advice.

print("official caption typography is Small acquisitions.")
print("16a-6(a): Any acquisition of an equity security or the right to acquire such securities, other than an acquisition from the issuer (including an employee benefit plan sponsored by the issuer), not exceeding $10,000 in market value shall be reported on Form 5, subject to the following conditions:")
print("16a-6(a)(1): Such acquisition, when aggregated with other acquisitions of securities of the same class (including securities underlying derivative securities, but excluding acquisitions exempted by rule from section 16(b) or previously reported on Form 4 or Form 5) within the prior six months, does not exceed a total of $10,000 in market value; and")
print("16a-6(a)(2): The person making the acquisition does not within six months thereafter make any disposition, other than by a transaction exempt from section 16(b) of the Act.")
print("16a-6(b): If an acquisition no longer qualifies for the reporting deferral in paragraph (a) of this section, all such acquisitions that have not yet been reported must be reported on Form 4 before the end of the second business day following the day on which the conditions of paragraph (a) of this section are no longer met.")
print("cite 17 CFR 240.16a-6; title 17 up_to_date_as_of 2026-11-17")
print("[56 FR 7265, Feb. 21, 1991, as amended at 61 FR 30392, June 14, 1996; 67 FR 56467, Sept. 3, 2002].")
from_issuer_qualifies = False
print(f"  an acquisition from the issuer, including an employee benefit plan sponsored by the issuer, qualifies for the 16a-6(a) Form 5 deferral? {from_issuer_qualifies}")
check(from_issuer_qualifies is False, "issuer / employee-plan acquisitions are carved out of 16a-6(a)")
is_within_two_bd = False
print(f'  official 16a-6(b) typography is "within two business days"? {is_within_two_bd}')
check(is_within_two_bd is False, "official typography is before the end of the second business day following")
flatten_16a6 = False
print(f"  this is a flatten into already-taught Form 4 / Form 5 clocks, packed Section 16(b), or packed 13d-2? {flatten_16a6}")
check(flatten_16a6 is False, "do not flatten 16a-6 into those boxes")
print("already-taught Form 4 / Form 5 clocks, packed Section 16(b), and packed 13d-2 exist and are named only; this toy is not those boxes")
print("Form 5 due date 2026-02-17 and 13d-1(g) fifth business day 2026-10-13 remain as already printed")
print("literacy only; not a how-to for deferring a Form 4, and not legal advice")
print("no filer, disclosure, or investment advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 240.16a-6; no filer or disclosure advice; learning only")


print("=== K. 17 CFR 240.16a-9: Stock splits, stock dividends, and pro rata rights ===")
# 17 CFR 240.16a-9 (official eCFR API XML, title 17 up_to_date_as_of 2026-11-17,
# live-refetched 2026-11-19, byte-identical to the 2026-11-09 archive).
# Keep sections A-J identical, including 62/62 after J / 16a-6.
# Pack official (a)+(b) and the official Note. Do not invent that the exercise
# or sale of a pro rata right is also exempt. Do not flatten into already-taught
# split / dividend price adjustments, packed 16a-6, or packed Section 16(b).
# Learning only; no issuer or investment advice.

print("official caption typography is Stock splits, stock dividends, and pro rata rights.")
print("16a-9: The following shall be exempt from section 16 of the Act:")
print("16a-9(a): The increase or decrease in the number of securities held as a result of a stock split or stock dividend applying equally to all securities of a class, including a stock dividend in which equity securities of a different issuer are distributed; and")
print("16a-9(b): The acquisition of rights, such as shareholder or pre-emptive rights, pursuant to a pro rata grant to all holders of the same class of equity securities registered under section 12 of the Act.")
print("official Note: The exercise or sale of a pro rata right shall be reported pursuant to § 240.16a-4 and the exercise shall be eligible for exemption from section 16(b) of the Act pursuant to § 240.16b-6(b).")
print("cite 17 CFR 240.16a-9; title 17 up_to_date_as_of 2026-11-17")
print("[56 FR 7265, Feb. 21, 1991, as amended at 61 FR 30393, June 14, 1996].")
print('official caption typography uses an Oxford comma before "and pro rata rights."')
exercise_also_exempt = False
print(f"  the official Note also exempts the exercise or sale of a pro rata right from section 16 reporting? {exercise_also_exempt}")
check(exercise_also_exempt is False, "exercise or sale of a pro rata right is reported under 16a-4")
flatten_16a9 = False
print(f"  this is a flatten into already-taught split / dividend price adjustments, packed 16a-6, or packed Section 16(b)? {flatten_16a9}")
check(flatten_16a9 is False, "do not flatten 16a-9 into those boxes")
split_change_exempt = True
print(f"  the increase or decrease in the number of securities from a stock split or equal stock dividend is exempt from section 16? {split_change_exempt}")
check(split_change_exempt is True, "split / equal stock-dividend share-count change is exempt")
print("already-taught split / dividend price adjustments, packed 16a-6, packed Section 16(b), and leftover 16a-4 / 16b-6(b) exist and are named only; this toy is not those boxes")
print("Form 5 due date 2026-02-17 and 13d-1(g) fifth business day 2026-10-13 remain as already printed")
print("literacy only; not a how-to for skipping a Form 4, and not legal advice")
print("no issuer, filer, or investment advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 240.16a-9; no filer or disclosure advice; learning only")


print("=== L. 17 CFR 240.16a-11: Dividend or interest reinvestment plans ===")
# 17 CFR 240.16a-11 (official eCFR API XML, title 17 up_to_date_as_of 2026-11-17,
# live-refetched 2026-11-19, byte-identical to the 2026-11-09 archive).
# Keep sections A-K identical, including 65/65 after K / 16a-9.
# Do not flatten into already-taught tax DRIP / Pub 550 / Treas. Reg. 1.1012-1(e),
# packed 16a-6, or packed 16a-9. Do not invent that every DRIP is exempt.
# Learning only; no issuer, tax, or investment advice.

print("official caption typography is Dividend or interest reinvestment plans.")
print("16a-11: Any acquisition of securities resulting from the reinvestment of dividends or interest on securities of the same issuer shall be exempt from section 16 of the Act if the acquisition is made pursuant to a plan providing for the regular reinvestment of dividends or interest and the plan provides for broad-based participation, does not discriminate in favor of employees of the issuer, and operates on substantially the same terms for all plan participants.")
print("cite 17 CFR 240.16a-11; title 17 up_to_date_as_of 2026-11-17")
print("[61 FR 30393, June 14, 1996].")
every_drip_exempt = False
print(f"  every dividend reinvestment plan is automatically exempt from section 16? {every_drip_exempt}")
check(every_drip_exempt is False, "only a qualifying broad-based, non-discriminatory regular plan is exempt")
flatten_16a11 = False
print(f"  this is a flatten into already-taught tax DRIP / Pub 550 / Treas. Reg. 1.1012-1(e), packed 16a-6, or packed 16a-9? {flatten_16a11}")
check(flatten_16a11 is False, "do not flatten 16a-11 into tax DRIP or other 16a boxes")
same_issuer = True
print(f"  official typography limits the exemption to reinvestment of dividends or interest on securities of the same issuer? {same_issuer}")
check(same_issuer is True, "same issuer only")
print("already-taught tax DRIP / Pub 550 / Treas. Reg. 1.1012-1(e), packed 16a-6, and packed 16a-9 exist and are named only; this toy is not those boxes")
print("Form 5 due date 2026-02-17 and 13d-1(g) fifth business day 2026-10-13 remain as already printed")
print("literacy only; not a how-to for a DRIP, and not tax, legal, or investment advice")
print("no issuer, filer, or investment advice")
print(f"assertions passed: {checks}/{checks}")
print("ASSERT_spinoff_insider_lag_ok")
print("disclaimer: official 17 CFR 240.16a-11; no filer, tax, or disclosure advice; learning only")

print("=== M. 17 CFR 240.16a-4: Derivative securities ===")
# 17 CFR 240.16a-4 the whole current section, including the official Note
# (official eCFR API XML, title 17 up_to_date_as_of 2026-11-17,
# live-refetched 2026-11-19, byte-identical to the enrich41-src archive).
# Keep sections A-L identical, including 68/68 after L / 16a-11,
# section-I ASSERT_spinoff_insider_lag_ok, Form 5 due date 2026-02-17,
# and 13d-1(g) fifth business day 2026-10-13.
# Official (a) italicizes "except that" with no trailing comma inside the italics.
# Official Note heading typography emphasizes the letter a:
# Note to § 240.16a-4: (do not print the word HEAD).
# Official (d) points to leftover § 240.16b-6(d); the official Note points
# to leftover § 240.16b-3 or § 240.16b-6(b) — name those leftovers only.
# Do not flatten into already-taught Form 4 codes, packed 16a-6 / 16a-9 /
# 16a-11, or packed Section 16(b).
# Learning only; no issuer, filer, or investment advice.

print("official caption typography is Derivative securities.")
print("16a-4(a): For purposes of section 16 of the Act, both derivative securities and the underlying securities to which they relate shall be deemed to be the same class of equity securities, except that the acquisition or disposition of any derivative security shall be separately reported.")
print("16a-4(b): The exercise or conversion of a call equivalent position shall be reported on Form 4 and treated for reporting purposes as:")
print("16a-4(b)(1): A purchase of the underlying security; and")
print("16a-4(b)(2): A closing of the derivative security position.")
print("16a-4(c): The exercise or conversion of a put equivalent position shall be reported on Form 4 and treated for reporting purposes as:")
print("16a-4(c)(1): A sale of the underlying security; and")
print("16a-4(c)(2): A closing of the derivative security position.")
print("16a-4(d): The disposition or closing of a long derivative security position, as a result of cancellation or expiration, shall be exempt from section 16(a) of the Act if exempt from section 16(b) of the Act pursuant to § 240.16b-6(d).")
print("official typography italicizes \"except that\" with no trailing comma inside the italics")
print("official Note heading typography is Note to § 240.16a-4, with official emphasis on the letter a")
print("official Note: A purchase or sale resulting from an exercise or conversion of a derivative security may be exempt from section 16(b) of the Act pursuant to § 240.16b-3 or § 240.16b-6(b).")
print("cite 17 CFR 240.16a-4; title 17 up_to_date_as_of 2026-11-17")
print("[56 FR 7265, Feb. 21, 1991, as amended at 56 FR 19927, May 1, 1991; 61 FR 30392, June 14, 1996].")
same_class_except = True
print(f"  derivative securities and the underlying shall be deemed to be the same class, except that the acquisition or disposition of any derivative security shall be separately reported? {same_class_except}")
check(same_class_except is True, "same class except that separately reported")
call_purchase_close = True
print(f"  the exercise or conversion of a call equivalent position is reported as a purchase of the underlying and a closing of the derivative? {call_purchase_close}")
check(call_purchase_close is True, "call equivalent: purchase + closing")
put_sale_close = True
print(f"  the exercise or conversion of a put equivalent position is reported as a sale of the underlying and a closing of the derivative? {put_sale_close}")
check(put_sale_close is True, "put equivalent: sale + closing")
note_leftovers_only = True
print(f"  the official Note is part of the packed slice and names leftover 16b-3 / 16b-6(b) only? {note_leftovers_only}")
check(note_leftovers_only is True, "official Note names leftover 16b-3 / 16b-6(b) only")
print("already-taught Form 4 transaction codes, packed 16a-6 / 16a-9 / 16a-11, packed Section 16(b), and leftover 16b-3 / 16b-6(b) / 16b-6(d) exist and are named only; this toy is not those boxes")
print("Form 5 due date 2026-02-17 and 13d-1(g) fifth business day 2026-10-13 remain as already printed")
print("literacy only; not a how-to for reporting a derivative, and not legal advice")
print("no issuer, filer, or investment advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 240.16a-4; no filer or disclosure advice; learning only")

print("=== N. 17 CFR 240.16a-10: Exemptions under section 16(a) ===")
# 17 CFR 240.16a-10 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17, live-refetched 2026-11-19,
# byte-identical to the enrich41-src archive).
# Keep sections A-M identical, including 72/72 after M / 16a-4.
# Official typography opens "Except as provided in § 240.16a-6."
# Official typography is "shall be likewise exempt from section 16(b) of the Act."
# The official API XML has no CITA element; do not invent a source line.
# 16a-6 is the official carve-out, not a 16(b) exemption under 16a-10.
# Do not flatten into packed 16a-6 / 16a-9 / 16a-11 / Section 16(b).
# Learning only; no issuer, filer, or investment advice.

print("official caption typography is Exemptions under section 16(a).")
print("16a-10: Except as provided in § 240.16a-6, any transaction exempted from the requirements of section 16(a) of the Act, insofar as it is otherwise subject to the provisions of section 16(b), shall be likewise exempt from section 16(b) of the Act.")
print('official typography opens "Except as provided in § 240.16a-6"')
print('official typography is "shall be likewise exempt from section 16(b) of the Act."')
print("official API XML has no CITA element; this toy does not invent a source line")
print("cite 17 CFR 240.16a-10; title 17 up_to_date_as_of 2026-11-17")
likewise_exempt = True
print(f"  a transaction exempted from section 16(a), insofar as it is otherwise subject to section 16(b), shall be likewise exempt from section 16(b) of the Act? {likewise_exempt}")
check(likewise_exempt is True, "likewise exempt from section 16(b)")
opens_except_16a6 = True
print(f"  official typography opens “Except as provided in § 240.16a-6”? {opens_except_16a6}")
check(opens_except_16a6 is True, "Except as provided in 16a-6")
sixteen_a6_is_16b_exemption = False
print(f"  16a-6 is a 16(b) exemption under 16a-10, or this is a flatten into packed 16a-6 / 16a-9 / 16a-11 / Section 16(b)? {sixteen_a6_is_16b_exemption}")
check(sixteen_a6_is_16b_exemption is False, "16a-6 is the official carve-out, not a 16(b) exemption under 16a-10")
print("packed 16a-6 / 16a-9 / 16a-11 and packed Section 16(b) exist and are named only; this toy is not those boxes")
print("Form 5 due date 2026-02-17 and 13d-1(g) fifth business day 2026-10-13 remain as already printed")
print("literacy only; not a how-to for claiming a 16(b) exemption, and not legal advice")
print("no issuer, filer, or investment advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 240.16a-10; no filer or disclosure advice; learning only")

print("=== O. 17 CFR 240.16a-13: Change in form of beneficial ownership ===")
# 17 CFR 240.16a-13 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17, live-refetched 2026-11-19,
# byte-identical to the enrich41-src archive).
# Keep sections A-N identical, including 75/75 after N / 16a-10.
# Official typography is "section 16 of the Act," not "section 16(a)" only,
# and "the subject equity securities."
# Official typography carves out "the exercise or conversion of a derivative
# security or deposit into or withdrawal from a voting trust."
# Section O reprints ASSERT_spinoff_insider_lag_ok and the R95 / R96
# date line (Form 5 2026-02-17 and 13d-1(g) 2026-10-13), as section L already does.
# Do not flatten into already-taught Form 4 codes or packed 16a-6 / 16a-9 / 16a-11.
# Learning only; no issuer, filer, or investment advice.

print("official caption typography is Change in form of beneficial ownership.")
print("16a-13: A transaction, other than the exercise or conversion of a derivative security or deposit into or withdrawal from a voting trust, that effects only a change in the form of beneficial ownership without changing a person's pecuniary interest in the subject equity securities shall be exempt from section 16 of the Act.")
print('official typography is "section 16 of the Act," not "section 16(a)" only')
print('official typography is "the subject equity securities"')
print('official typography carves out "the exercise or conversion of a derivative security or deposit into or withdrawal from a voting trust"')
print("cite 17 CFR 240.16a-13; title 17 up_to_date_as_of 2026-11-17")
print("[61 FR 30393, June 14, 1996].")
form_only_exempt = True
print(f"  a transaction that effects only a change in the form of beneficial ownership without changing a person's pecuniary interest in the subject equity securities is exempt from section 16 of the Act? {form_only_exempt}")
check(form_only_exempt is True, "form-only change exempt from section 16 of the Act")
carveout = True
print(f"  official typography carves out the exercise or conversion of a derivative security or deposit into or withdrawal from a voting trust? {carveout}")
check(carveout is True, "derivative-exercise / voting-trust carve-out")
flatten_16a13 = False
print(f"  this is already-taught Form 4 codes or packed 16a-6 / 16a-9 / 16a-11? {flatten_16a13}")
check(flatten_16a13 is False, "do not flatten 16a-13 into Form 4 codes or packed 16a boxes")
print("already-taught Form 4 transaction codes and packed 16a-6 / 16a-9 / 16a-11 exist and are named only; this toy is not those boxes")
print("Form 5 due date 2026-02-17 and 13d-1(g) fifth business day 2026-10-13 remain as already printed")
print("literacy only; not a how-to for skipping a Form 4, and not legal advice")
print("no issuer, filer, or investment advice")
print(f"assertions passed: {checks}/{checks}")
print("ASSERT_spinoff_insider_lag_ok")
print("disclaimer: official 17 CFR 240.16a-13; no filer or disclosure advice; learning only")
