"""S&P 500 addition rules as of a date, the announcement timeline, and earnings release times as event
timestamps (checked 2026-11-11).

Sources:
- S&P Dow Jones Indices, "S&P U.S. Indices Methodology" (November 2026 edition), sections Eligibility
  Criteria, Index Maintenance, Index Policy and Appendix A:
  * evaluation date for S&P Composite 1500 eligibility = the open of trading two business days before the
    announcement date;
  * S&P 500: total company market cap >= US$22.7 billion (Appendix A: 18.0 bn after the close of 2024-04-01,
    20.5 bn after the close of 2025-01-02, 22.7 bn after the close of 2025-07-01); security float-adjusted
    market cap (FMC) >= 50% of that threshold; IWF >= 0.10; float-adjusted liquidity ratio >= 0.75; at least
    250,000 shares traded in each of the six months before the evaluation date; GAAP net income from
    continuing operations positive for the most recent quarter AND for the sum of the last four quarters;
    IPOs (and de-SPACs) need 12 months of trading;
  * constituent selection is at the Index Committee's discretion (sector balance is also considered); the
    criteria are for ADDITION, not continued membership; no scheduled reconstitution; additions and
    deletions are announced with at least three business days' notice, at 05:15 PM Eastern Time.
- SEC Form 8-K General Instruction B.1 and Item 2.02: an earnings release triggers an 8-K that states the
  date of the announcement and attaches the release; unless otherwise specified, an 8-K is due within four
  business days. 17 CFR 243.100 (Regulation FD): intentional disclosure to market professionals or holders
  must be made public simultaneously.
Dates in sections B and C are synthetic examples (no real company or real index change). Weekends only:
the example dates avoid US market holidays. Learning only; no claim about price moves around inclusion
and no earnings-trading strategy.
"""
from datetime import date, datetime, time, timedelta

checks = 0


def check(cond, label):
    global checks
    assert cond, label
    checks += 1


def add_bd(d, n):
    step = 1 if n > 0 else -1
    while n:
        d += timedelta(days=step)
        if d.weekday() < 5:
            n -= step
    return d


def bd_between(a, b):
    """Business days strictly after a and strictly before b."""
    n, d = 0, a + timedelta(days=1)
    while d < b:
        n += d.weekday() < 5
        d += timedelta(days=1)
    return n


# (effective after the close of this date, S&P 500 minimum total market cap in USD bn)
SP500_MIN_CAP = [(date(2024, 4, 1), 18.0), (date(2025, 1, 2), 20.5), (date(2025, 7, 1), 22.7)]


def min_cap(d):
    cap = None
    for eff, v in SP500_MIN_CAP:
        if d > eff:  # "after close" of the effective date
            cap = v
    if cap is None:
        raise ValueError(f"{d}: before this toy's table; read Appendix A")
    return cap


def sp500_screen(c, d):
    """Return a list of failed addition criteria as of evaluation date d. Empty list = eligible, not 'added'."""
    t = min_cap(d)
    fails = []
    if not c["us_domicile"]:
        fails.append("domicile")
    if c["cap_bn"] < t:
        fails.append(f"total cap {c['cap_bn']} < {t}")
    if c["fmc_bn"] < 0.5 * t:
        fails.append(f"FMC {c['fmc_bn']} < {0.5 * t:.2f}")
    if c["iwf"] < 0.10:
        fails.append("IWF < 0.10")
    if c["falr"] < 0.75:
        fails.append("FALR < 0.75")
    if min(c["monthly_shares_6m"]) < 250_000:
        fails.append("a month < 250,000 shares")
    if c["ni_q"][-1] <= 0:
        fails.append("latest quarter GAAP NI <= 0")
    if sum(c["ni_q"][-4:]) <= 0:
        fails.append("4-quarter GAAP NI sum <= 0")
    if c["months_trading"] < 12:
        fails.append("traded < 12 months")
    return fails


base = dict(us_domicile=True, cap_bn=25.0, fmc_bn=20.0, iwf=0.8, falr=1.1,
            monthly_shares_6m=[900_000] * 6, ni_q=[0.2, 0.3, 0.1, 0.4], months_trading=60)
cands = {
    "P (passes all)": dict(base),
    "Q (cap 21.0 bn)": dict(base, cap_bn=21.0, fmc_bn=18.0),
    "R (latest quarter loss)": dict(base, ni_q=[0.5, 0.5, 0.5, -0.1]),
    "S (IPO 10 months ago)": dict(base, months_trading=10),
    "T (IWF 0.08)": dict(base, iwf=0.08, fmc_bn=2.0),
}

print("=== A. S&P 500 addition screen as of an evaluation date (eligible != added) ===")
for d in (date(2025, 6, 2), date(2025, 7, 15)):
    print(f"evaluation {d}: minimum total cap {min_cap(d)} bn, minimum FMC {0.5 * min_cap(d):.2f} bn")
    for name, c in cands.items():
        f = sp500_screen(c, d)
        print(f"  {name:24s} -> {'eligible' if not f else 'fails: ' + '; '.join(f)}")
check(min_cap(date(2025, 7, 1)) == 20.5 and min_cap(date(2025, 7, 2)) == 22.7, "threshold changes after the close of 2025-07-01")
check(sp500_screen(cands["Q (cap 21.0 bn)"], date(2025, 6, 2)) == [], "21.0 bn passes under the 20.5 bn guideline")
check(sp500_screen(cands["Q (cap 21.0 bn)"], date(2025, 7, 15)) != [], "21.0 bn fails under 22.7 bn")
check(sp500_screen(cands["R (latest quarter loss)"], date(2025, 7, 15)) == ["latest quarter GAAP NI <= 0"], "both earnings tests")
check("traded < 12 months" in sp500_screen(cands["S (IPO 10 months ago)"], date(2025, 7, 15)), "12-month rule")
print("  the Index Committee still chooses among eligible names (fixed count 500, sector balance);")
print("  a member that later fails a criterion is not removed automatically.")

print("=== B. announcement timeline (synthetic dates) ===")
ann = datetime(2026, 3, 2, 17, 15)      # Monday, 05:15 PM ET, after the 16:00 close
eff = date(2026, 3, 9)                   # change effective before the open of Monday 2026-03-09
evaluation = add_bd(ann.date(), -2)
print(f"announcement {ann:%Y-%m-%d %a %H:%M} ET; evaluation date = open of {evaluation:%Y-%m-%d %a}")
print(f"business days between announcement and effective date: {bd_between(ann.date(), eff)} (methodology: at least 3)")
first_fill = datetime.combine(add_bd(ann.date(), 1), time(9, 30))
print(f"daily backtest: earliest fill on the news = {first_fill:%Y-%m-%d %H:%M} ET open (the 03-02 close came before the news)")
print(f"decision at the 2026-03-02 16:00 close: is the change known? {datetime(2026, 3, 2, 16, 0) >= ann} (using it = look-ahead)")
check(evaluation == date(2026, 2, 26), "two business days before the announcement")
check(bd_between(ann.date(), eff) >= 3, "at least three business days' notice")
check(first_fill.date() == date(2026, 3, 3), "next session open")

print("=== C. earnings release time -> first session that can react ===")
OPEN, CLOSE = time(9, 30), time(16, 0)


def day0(ts):
    """First regular session (date) that starts after ts, and whether that day's open is usable."""
    d = ts.date()
    if d.weekday() >= 5 or ts.time() >= CLOSE:
        d = add_bd(d if d.weekday() < 5 else d - timedelta(days=1), 1)
        return d, True
    if ts.time() < OPEN:
        return d, True
    return d, False  # released during the session: today's open came before the news


cases = [
    ("before the open", datetime(2026, 2, 3, 7, 0)),
    ("during the session", datetime(2026, 2, 4, 12, 30)),
    ("after the close (Thu)", datetime(2026, 2, 5, 16, 5)),
    ("after the close (Fri)", datetime(2026, 2, 6, 16, 5)),
]
res = {}
for label, ts in cases:
    d, open_ok = day0(ts)
    res[label] = (d, open_ok)
    print(f"release {ts:%Y-%m-%d %a %H:%M} ET ({label}): day 0 = {d:%Y-%m-%d %a}; that day's open usable? {open_ok}")
check(res["before the open"] == (date(2026, 2, 3), True), "pre-open release")
check(res["during the session"] == (date(2026, 2, 4), False), "intraday release: open is look-ahead")
check(res["after the close (Thu)"] == (date(2026, 2, 6), True), "after close -> next day")
check(res["after the close (Fri)"] == (date(2026, 2, 9), True), "Friday after close -> Monday")
rel = datetime(2026, 2, 5, 16, 5)
acc = datetime(2026, 2, 5, 16, 20)
print(f"only the 8-K is stored: accepted {acc:%Y-%m-%d %H:%M} ET -> day 0 {day0(acc)[0]} (same as the release here;")
print("  an 8-K is due within four business days, so its time can be later than the release; using it never looks ahead)")
check(day0(acc)[0] == day0(rel)[0], "8-K acceptance after the release maps to the same day 0 here")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: synthetic candidates and dates; no index-inclusion or earnings strategy; learning only")

print("=== D. Form 8-K items beyond Item 2.02 ===")
# Official Form 8-K (SEC 873 (02-25), opened 2026-11-12). General Instruction
# B.1: unless otherwise specified, a report "is to be filed or furnished
# within four business days after occurrence of the event." "A report
# pursuant to Item 1.05 is to be filed within four business days after the
# registrant determines that it has experienced a material cybersecurity
# incident." B.2: Item 2.02 and Item 7.01 information is furnished, not
# deemed "filed" for Section 18, unless the registrant states otherwise.
# Official item captions (not Instruction G's "Principal Officers" wording
# for 5.02): Item 1.01 Entry into a Material Definitive Agreement; Item 1.05
# Material Cybersecurity Incidents; Item 4.02 Non-Reliance on Previously
# Issued Financial Statements or a Related Audit Report or Completed Interim
# Review; Item 5.02 Departure of Directors or Certain Officers; Election of
# Directors; Appointment of Certain Officers; Compensatory Arrangements of
# Certain Officers. Item 1.05 Instruction 1: the materiality determination
# "must be made without unreasonable delay after discovery of the incident."
# Do not start the 1.05 clock on discovery. The Attorney General delay in
# 1.05(c) is not the usual clock. Do not flatten Item 5.07 or other special
# clocks into the same trigger. Form 12b-25 does not apply to an 8-K. This
# toy is not a complete item-by-item engine. The already-taught Item 2.02
# earnings-timestamp section in backtest-traps stays as written. No filer
# or disclosure advice.

official = {
    "1.01": "Entry into a Material Definitive Agreement",
    "1.05": "Material Cybersecurity Incidents",
    "4.02": "Non-Reliance on Previously Issued Financial Statements or a Related Audit Report or Completed Interim Review",
    "5.02": "Departure of Directors or Certain Officers; Election of Directors; Appointment of Certain Officers; Compensatory Arrangements of Certain Officers",
}
for num, caption in official.items():
    is_earnings = False
    print(f"Item {num} {caption}: Item 2.02 earnings? {is_earnings}")
    check(is_earnings is False, f"Item {num} is not Item 2.02 earnings")

print("usual clock: filed or furnished within four business days after occurrence of the event, unless otherwise specified")
print("Item 1.05 is due within four business days after the registrant determines that it has experienced a material cybersecurity incident")
clock_starts_on_discovery = False
print(f"  Item 1.05 clock starts on discovery? {clock_starts_on_discovery}")
check(clock_starts_on_discovery is False, "1.05 clock does not start on discovery")
print("  Instruction 1: the materiality determination must be made without unreasonable delay after discovery of the incident")
print("Item 2.02 / 7.01 are furnished, not deemed filed for Section 18 in the usual case")
print("Form 12b-25 does not apply to an 8-K")
print("the Attorney General delay in 1.05(c) is not the usual clock")
print("do not flatten Item 5.07 or other special clocks into the same trigger")
print("use the official Item 5.02 caption 'Certain Officers', not Instruction G 'Principal Officers'")
print("this toy is not a complete item-by-item engine; no filer or disclosure advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official Form 8-K item map; no filer or disclosure advice; learning only")

print("=== E. Form 8-K Item 5.07 special clock ===")
# Official Form 8-K Item 5.07 (SEC 873 (02-25); OMB Number 3235-0060,
# Expires November 30, 2027; official PDF opened 2026-11-12). Keep
# sections A-D identical, including 13/13 after C and 18/18 after D,
# and the existing line "do not flatten Item 5.07 or other special
# clocks into the same trigger."
# Instruction 1 to Item 5.07: The four business day period for reporting
# the event under this Item 5.07, other than with respect to Item
# 5.07(d), shall begin to run on the day on which the meeting ended.
# The registrant shall disclose on Form 8-K under this Item 5.07 the
# preliminary voting results. The registrant shall file an amended
# report on Form 8-K under this Item 5.07 to disclose the final voting
# results within four business days after the final voting results are
# known. However, no preliminary voting results need be disclosed under
# this Item 5.07 if the registrant has disclosed final voting results
# on Form 8-K under this Item.
# Official 5.07(d) uses a different 150-calendar-day / 60-calendar-day-
# before-14a-8 clock; this toy is not a 14a-8 engine and does not invent
# a four-business-day clock for 5.07(d). This is not a rewrite of
# already-taught Instruction B.1 or Item 1.05. No issuer or voting
# advice.

print("Instruction 1 to Item 5.07: The four business day period for reporting the event under this Item 5.07,")
print("  other than with respect to Item 5.07(d), shall begin to run on the day on which the meeting ended")
print("The registrant shall disclose on Form 8-K under this Item 5.07 the preliminary voting results")
print("The registrant shall file an amended report on Form 8-K under this Item 5.07")
print("  to disclose the final voting results within four business days after the final voting results are known")
print("However, no preliminary voting results need be disclosed under this Item 5.07")
print("  if the registrant has disclosed final voting results on Form 8-K under this Item")
print("the 5.07 four-business-day period, other than 5.07(d), begins on the day the meeting ended")
print("preliminary results are disclosed, and finals are amended within four business days after they are known")
print("no preliminary is required if finals have already been disclosed")
starts_on_occurrence = False
print(f"  the 5.07 four-business-day clock, other than (d), starts on a generic occurrence date rather than the day the meeting ended? {starts_on_occurrence}")
check(starts_on_occurrence is False, "5.07 clock other than (d) begins on the day the meeting ended")
print("official 5.07(d) uses a different 150-calendar-day / 60-calendar-day-before-14a-8 clock and this toy is not a 14a-8 engine")
invents_d_four_bd = False
is_b1_or_105 = False
builds_14a8 = False
print(f"  this toy invents a four-business-day clock for 5.07(d)? {invents_d_four_bd}")
print(f"  this is a rewrite of already-taught Instruction B.1 or Item 1.05? {is_b1_or_105}")
print(f"  this toy builds a Rule 14a-8 engine? {builds_14a8}")
check(invents_d_four_bd is False, "do not invent a four-business-day clock for 5.07(d)")
check(is_b1_or_105 is False, "5.07 is not a rewrite of Instruction B.1 or Item 1.05")
check(builds_14a8 is False, "do not build a Rule 14a-8 engine")
print("no issuer or voting advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official Form 8-K Item 5.07 special clock; no issuer or voting advice; learning only")

print("=== F. 17 CFR 240.14a-9: False or misleading statements ===")
# 17 CFR 240.14a-9 False or misleading statements (official eCFR
# versioner API XML, title 17 up_to_date_as_of 2026-11-09, opened
# 2026-11-12; API XML byte-identical to the enrich32 copy). Add this
# section after the current last Item 5.07 disclaimer so the tip file
# remains a strict byte-prefix. Keep sections A-E, including 13/13
# after C, 18/18 after D, the existing line "do not flatten Item 5.07
# or other special clocks into the same trigger," and 22/22 after E
# plus the last disclaimer, identical.
# Official (a): No solicitation subject to this regulation shall be
# made by means of any proxy statement, form of proxy, notice of
# meeting or other communication, written or oral, containing any
# statement which, at the time and in the light of the circumstances
# under which it is made, is false or misleading with respect to any
# material fact, or which omits to state any material fact necessary in
# order to make the statements therein not false or misleading or
# necessary to correct any statement in any earlier communication with
# respect to the solicitation of a proxy for the same meeting or subject
# matter which has become false or misleading.
# Official typography is "in the light of the circumstances under which
# it is made" (singular "it is made"). Do not tidy that into packed
# 10b-5's "in the light of the circumstances under which they were
# made." Official (a) is "notice of meeting or other communication,
# written or oral." Official caption is "False or misleading
# statements." Cite 17 CFR 240.14a-9.
# Official (b) (filing with or examination by the Commission is not a
# finding of accuracy or a merits approval) and official (c) (false or
# misleading statements in a registrant's proxy materials, a Schedule
# 14N notice, or a related communication by a nominee, nominating
# shareholder, or nominating shareholder group) exist; official Note
# examples a-d exist. Name official (b), official (c), and the Note;
# do not build official (c) or the Note catalog. Do not flatten 14a-9
# into already-taught Rule 14a-8 or Form 8-K Item 5.07, and do not
# rewrite those already-shipped boxes. Learning only; no issuer or
# voting advice.

print("14a-9(a): No solicitation subject to this regulation shall be made by means of any proxy")
print("  statement, form of proxy, notice of meeting or other communication, written or oral,")
print("  containing any statement which, at the time and in the light of the circumstances")
print("  under which it is made, is false or misleading with respect to any material fact, or")
print("  which omits to state any material fact necessary in order to make the statements")
print("  therein not false or misleading or necessary to correct any statement in any earlier")
print("  communication with respect to the solicitation of a proxy for the same meeting or")
print("  subject matter which has become false or misleading")
print('official typography is "in the light of the circumstances under which it is made" (singular "it is made")')
print("official (a) is notice of meeting or other communication, written or oral")
print("official caption is False or misleading statements")
print("cite 17 CFR 240.14a-9; title 17 up_to_date_as_of 2026-11-09")
print("official (b), official (c), and the Note exist; this toy is not official (c) or the Note catalog")
flatten_14a9 = False
print(f"  this is a flatten into already-taught Rule 14a-8 or Form 8-K Item 5.07? {flatten_14a9}")
check(flatten_14a9 is False, "do not flatten 14a-9 into already-taught 14a-8 or Item 5.07")
tidies_10b5 = False
print(f"  this toy tidies official typography into packed 10b-5's under which they were made? {tidies_10b5}")
check(tidies_10b5 is False, "14a-9 typography is under which it is made, not they were made")
core_14a9 = True
print(f"  a solicitation may not be made by a proxy statement, form of proxy, notice of meeting or other communication, written or oral, that is false or misleading in the light of the circumstances under which it is made? {core_14a9}")
check(core_14a9 is True, "14a-9 bars false or misleading proxy statements under which it is made")
print("no issuer or voting advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 240.14a-9; no issuer or voting advice; learning only")
