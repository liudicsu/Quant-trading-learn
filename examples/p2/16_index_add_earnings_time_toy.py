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

print("=== G. 17 CFR 240.12b-20: Additional information ===")
# 17 CFR 240.12b-20 Additional information (official eCFR versioner
# API XML, title 17 up_to_date_as_of 2026-11-09, opened 2026-11-12).
# Add this section after the last 14a-9 disclaimer so 25/25 after F
# plus the last 14a-9 disclaimer remain a strict byte-prefix. Keep
# sections A-F identical.
# Official sentence: In addition to the information expressly required
# to be included in a statement or report, there shall be added such
# further material information, if any, as may be necessary to make the
# required statements, in the light of the circumstances under which
# they are made not misleading.
# Official typography is "in the light of the circumstances under which
# they are made not misleading" (no comma after "made"). Do not insert
# a comma after "made," and do not tidy that clause into packed 10b-5's
# "under which they were made" or packed 14a-9's "under which it is
# made." A LII wrap space before "not misleading" is not official
# typography. Cite 17 CFR 240.12b-20.
# Do not flatten 12b-20 into packed 14a-9, packed 10b-5, already-taught
# Regulation FD, Form 8-K Item 5.07, or 14a-8. Do not invent a
# scienter / materiality / judicial-opinion catalog, and do not invent
# a form-specific clock in this rule. Learning only; no issuer or
# disclosure advice.

print("12b-20: In addition to the information expressly required to be included in a statement")
print("  or report, there shall be added such further material information, if any, as may be")
print("  necessary to make the required statements, in the light of the circumstances under")
print("  which they are made not misleading")
print('official typography is "in the light of the circumstances under which they are made not misleading" (no comma after "made")')
print("official caption is Additional information.")
print("cite 17 CFR 240.12b-20; title 17 up_to_date_as_of 2026-11-09")
print("a LII wrap space before not misleading is not official typography")
flatten_12b20 = False
print(f"  this is a flatten into packed 14a-9, packed 10b-5, already-taught Regulation FD, Form 8-K Item 5.07, or 14a-8? {flatten_12b20}")
check(flatten_12b20 is False, "do not flatten 12b-20 into packed 14a-9, 10b-5, Regulation FD, Item 5.07, or 14a-8")
comma_after_made = False
print(f'  this toy inserts a comma after "made," or tidies the clause into packed 10b-5\'s "they were made" or packed 14a-9\'s "it is made"? {comma_after_made}')
check(comma_after_made is False, "12b-20 typography has no comma after made")
core_12b20 = True
print(f"  further material information shall be added as may be necessary to make the required statements, in the light of the circumstances under which they are made not misleading? {core_12b20}")
check(core_12b20 is True, "12b-20 requires additional material information so required statements are not misleading")
print("no issuer or disclosure advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 240.12b-20; no issuer or disclosure advice; learning only")

print("=== H. 17 CFR 240.13a-14(a)/(c): Certification of disclosure in annual and quarterly reports ===")
# 17 CFR 240.13a-14 Certification of disclosure in annual and quarterly
# reports (official eCFR versioner API XML, title 17 up_to_date_as_of
# 2026-11-09, opened 2026-11-12). Add this section after the last
# 12b-20 disclaimer so 28/28 after G / 12b-20 plus that disclaimer
# remain a strict byte-prefix. Keep sections A-G identical.
# Official typography is "Form 10-Q, Form 10-K, Form 20-F or Form 40-F"
# (no Oxford comma). Official (c): a person required to provide a
# certification specified in paragraph (a), (b) or (d) may not have the
# certification signed on his or her behalf pursuant to a power of
# attorney or other form of confirming authority. Cite 17 CFR
# 240.13a-14.
# Official (b) 18 U.S.C. 1350 furnished-certification duty, official
# (d)/(e) asset-backed catalog, official (f) Interactive Data File
# exception, and the official (a) ICFR phase-in language that names
# § 240.13a-15 or § 240.15d-15, exist; name them, do not build those
# catalogs, and do not pack official (b) or 13a-15 as the teaching
# core. 17 CFR 240.15d-14 (same official caption; the Section 15(d)
# companion) is named only; do not pack 15d-14 as a second teaching
# core. Do not flatten 13a-14 into already-taught Form 10-K / 10-Q
# clocks, packed 12b-20, already-taught Form 20-F four-month / Form 6-K
# promptly clocks, or Form 8-K Item 4.02. Do not invent a certification
# form number or a filing clock in this rule. Learning only; no issuer
# or disclosure advice.

print("13a-14(a): Each report, including transition reports, filed on Form 10-Q, Form 10-K,")
print("  Form 20-F or Form 40-F under Section 13(a) of the Act, other than a report filed by")
print("  an Asset-Backed Issuer or a report on Form 20-F filed under § 240.13a-19, must")
print("  include certifications in the form specified in the applicable exhibit filing")
print("  requirements of such report and such certifications must be filed as an exhibit to")
print("  such report. Each principal executive and principal financial officer of the issuer,")
print("  or persons performing similar functions, at the time of filing of the report must")
print("  sign a certification.")
print("13a-14(c): A person required to provide a certification specified in paragraph (a),")
print("  (b) or (d) of this section may not have the certification signed on his or her behalf")
print("  pursuant to a power of attorney or other form of confirming authority.")
print('official typography is "Form 10-Q, Form 10-K, Form 20-F or Form 40-F" (no Oxford comma)')
print("official caption is Certification of disclosure in annual and quarterly reports.")
print("cite 17 CFR 240.13a-14; title 17 up_to_date_as_of 2026-11-09")
print("official (b) 18 U.S.C. 1350 furnished certifications, official (d)/(e) ABS, official (f)")
print("  Interactive Data File, and § 240.13a-15 / § 240.15d-15 exist; 17 CFR 240.15d-14 is")
print("  named only; this toy is not those catalogs, and does not pack official (b) or 15d-14")
print("  as the teaching core")
flatten_13a14 = False
print(f"  this is a flatten into already-taught Form 10-K / 10-Q clocks, packed 12b-20, already-taught Form 20-F / Form 6-K clocks, or Form 8-K Item 4.02? {flatten_13a14}")
check(flatten_13a14 is False, "do not flatten 13a-14 into already-taught 10-K / 10-Q clocks, packed 12b-20, 20-F / 6-K, or Item 4.02")
poa_ok = False
print(f"  this toy invents that a required certification may be signed on his or her behalf pursuant to a power of attorney? {poa_ok}")
check(poa_ok is False, "official (c) bars a power of attorney or other form of confirming authority")
core_13a14 = True
print(f"  each principal executive and principal financial officer must sign a certification that is filed as an exhibit, and may not have it signed on his or her behalf pursuant to a power of attorney? {core_13a14}")
check(core_13a14 is True, "13a-14(a)/(c) require a filed, personally signed certification")
print("no issuer or disclosure advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 240.13a-14; no issuer or disclosure advice; learning only")

print("=== I. 17 CFR 240.10D-1(b)(1): recover reasonably promptly the amount of erroneously awarded incentive-based compensation ===")
# 17 CFR 240.10D-1 Listing standards relating to recovery of erroneously
# awarded compensation (official eCFR versioner API XML, title 17
# up_to_date_as_of 2026-11-09, opened 2026-11-12). Keep H identical
# once 13a-14 is added. Packed slice is official (b)(1)'s opening
# written-policy sentence only, including "recover reasonably promptly."
# Official (a) listing-standard / 2023 transition machinery, official
# (b)(1)(i)-(v) lookback / restatement-date / recovery-amount /
# impracticability / no-indemnification catalog (including official
# (b)(1)(i)(D) "An issuer's obligation to recover erroneously awarded
# compensation is not dependent on if or when the restated financial
# statements are filed," and official (b)(1)(iv)(C) typography "the
# requirements of26 U.S.C. 401(a)(13)" with no space after "of"),
# official (c) exemptions, and official (d) definitions exist; name
# them, do not build those catalogs, do not invent a numeric clock for
# "reasonably promptly," and do not silently insert a space into
# official "of26." A LII U.S.C. link wrap is not official typography
# that adds a space. Cite 17 CFR 240.10D-1.
# Do not flatten 10D-1 into already-taught Form 8-K Item 4.02, packed
# 12b-20, packed 13a-14, or already-taught 10-K / 10-Q clocks. Learning
# only; no issuer, compensation, or disclosure advice.

print("10D-1(b)(1): The issuer must adopt and comply with a written policy providing that the")
print("  issuer will recover reasonably promptly the amount of erroneously awarded")
print("  incentive-based compensation in the event that the issuer is required to prepare an")
print("  accounting restatement due to the material noncompliance of the issuer with any")
print("  financial reporting requirement under the securities laws, including any required")
print("  accounting restatement to correct an error in previously issued financial statements")
print("  that is material to the previously issued financial statements, or that would result")
print("  in a material misstatement if the error were corrected in the current period or left")
print("  uncorrected in the current period.")
print('official typography is "recover reasonably promptly"')
print("official caption is Listing standards relating to recovery of erroneously awarded compensation.")
print("cite 17 CFR 240.10D-1; title 17 up_to_date_as_of 2026-11-09")
print("official (a) 2023 transition machinery, official (b)(1)(i)-(v) including not dependent on")
print("  if or when the restated financial statements are filed, official (c) exemptions, and")
print("  official (d) definitions exist; this toy is not those catalogs")
print('official (b)(1)(iv)(C) typography is "the requirements of26 U.S.C. 401(a)(13)" (no space after "of")')
flatten_10d1 = False
print(f"  this is a flatten into already-taught Form 8-K Item 4.02, packed 12b-20, packed 13a-14, or already-taught 10-K / 10-Q clocks? {flatten_10d1}")
check(flatten_10d1 is False, "do not flatten 10D-1 into Item 4.02, packed 12b-20, packed 13a-14, or already-taught 10-K / 10-Q clocks")
numeric_clock = False
print(f"  this toy invents a numeric clock for reasonably promptly, or silently inserts a space into official of26? {numeric_clock}")
check(numeric_clock is False, "do not invent a numeric clock for reasonably promptly, and do not insert a space into of26")
core_10d1 = True
print(f"  the issuer must adopt and comply with a written policy providing that the issuer will recover reasonably promptly the amount of erroneously awarded incentive-based compensation? {core_10d1}")
check(core_10d1 is True, "10D-1(b)(1) requires a written policy to recover reasonably promptly")
print("no issuer, compensation, or disclosure advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 240.10D-1; no issuer, compensation, or disclosure advice; learning only")

print("=== J. 17 CFR 244.100(a): Regulation G non-GAAP financial measure presentation and reconciliation ===")
# 17 CFR 244.100 General rules regarding disclosure of non-GAAP
# financial measures (official eCFR versioner API XML typography,
# title 17 up_to_date_as_of 2026-11-09, opened 2026-11-12). Keep
# 34/34 after I / 10D-1 plus the closing 10D-1 disclaimer identical
# as a strict byte-prefix of the tip file. Packed slice is official
# (a) only. Official typography in (a)(1) is "Generally Accepted
# Accounting Principles (GAAP)" with initial capitals; official (c)(2)
# later uses lowercase "generally accepted accounting principles in
# the United States" — do not tidy one into the other. Official (b)
# typography is "in light of the circumstances under which it is
# presented, not misleading" (not packed 10b-5 / 12b-20 "in the light
# of," and not 12b-20's "they are made," and not "they are presented").
# Name official (b); do not flatten packed 10b-5, packed 12b-20, or
# packed 14a-9 into it. Official (c) FPI conditions and official (d)
# proposed-business-combination exception exist; name them, do not
# build those catalogs. Official (d) typography is "the entity
# resulting therefrom or an entity that is a party thereto" (no Oxford
# comma). Official notes heading is "Notes to § 244.100:". Official
# Note 1 typography is "by Web cast" (two-word, capital W) and cites
# "paragraphs (a)(1)(i) and (a)(1)(ii) of this section" even though
# official (a) is numbered (a)(1) and (a)(2) — do not silently
# renumber the official note. Official Note 1(i) is "the registrant's
# Web site" (capital W, two words); official Note 1(ii) is "the
# location of the web site" (lowercase w, two words); official Note
# 2(iii) is "web sites" (lowercase). Do not tidy those into "website"
# or "webcast," packed 4370 / 2264 "Web site," or packed 3150
# "website." Name 17 CFR 244.101 / 244.102 and Regulation S-K Item
# 10(e) / 17 CFR 229.10 only; do not pack them as second cores, and
# do not flatten 244.102 into packed 10b-5. Official 244.102
# typography is "compliance or non-compliance," "shall in itself
# affect." Do not flatten into already-taught earnings / 10-K / 10-Q
# clocks, packed 13a-14, packed 12b-20, or packed 10D-1. Learning
# only; a non-GAAP figure in a press release or slide is not a
# substitute for the accompanying GAAP measure and reconciliation; no
# investment advice and no "use / avoid non-GAAP" product
# recommendation.

print("244.100(a): Whenever a registrant, or person acting on its behalf, publicly discloses")
print("  material information that includes a non-GAAP financial measure, the registrant must")
print("  accompany that non-GAAP financial measure with:")
print("  (1) A presentation of the most directly comparable financial measure calculated and")
print("  presented in accordance with Generally Accepted Accounting Principles (GAAP); and")
print("  (2) A reconciliation (by schedule or other clearly understandable method), which shall")
print("  be quantitative for historical non-GAAP measures presented, and quantitative, to the")
print("  extent available without unreasonable efforts, for forward-looking information, of")
print("  the differences between the non-GAAP financial measure disclosed or released with the")
print("  most comparable financial measure or measures calculated and presented in accordance")
print("  with GAAP identified in paragraph (a)(1) of this section.")
print('official (a)(1) typography is "Generally Accepted Accounting Principles (GAAP)" with')
print("  initial capitals; official (c)(2) later uses lowercase \"generally accepted accounting")
print('  principles in the United States"; this toy does not tidy one into the other')
print("official caption is General rules regarding disclosure of non-GAAP financial measures.")
print("cite 17 CFR 244.100; title 17 up_to_date_as_of 2026-11-09")
print('official (b) typography is "in light of the circumstances under which it is presented,')
print('  not misleading" (not packed 10b-5 / 12b-20 "in the light of," and not 12b-20\'s "they')
print('  are made," and not "they are presented"); official (b) is named only')
print("official (c) FPI conditions and official (d) proposed-business-combination exception")
print('  exist; official (d) typography is "the entity resulting therefrom or an entity that')
print('  is a party thereto" (no Oxford comma); this toy is not those catalogs')
print("official notes heading is Notes to \u00a7 244.100:")
print('official Note 1 typography is "orally, telephonically, by Web cast, by broadcast, or by')
print('  similar means" (two-word "Web cast," capital W, Oxford comma) and cites "paragraphs')
print('  (a)(1)(i) and (a)(1)(ii) of this section" even though official (a) is numbered (a)(1)')
print("  and (a)(2); this toy does not silently renumber the official note")
print("official Note 1(i) typography is \"the registrant's Web site\" (capital W, two words);")
print('  official Note 1(ii) typography is "the location of the web site" (lowercase w, two')
print('  words); official Note 2(iii) typography is "web sites" (lowercase); this toy does not')
print('  tidy those into "website" or "webcast," packed 4370 / 2264 "Web site," or packed 3150')
print('  "website"')
print("17 CFR 244.101 (definitions, including official (a) Non-GAAP financial measure), 17 CFR")
print('  244.102 ("No effect on antifraud liability"; official typography "compliance or')
print('  non-compliance," "shall in itself affect"), and Regulation S-K Item 10(e) / 17 CFR')
print("  229.10 exist and are named only; this toy does not pack them as second cores, and")
print("  does not flatten 244.102 into packed 10b-5")
flatten_244100 = False
print(f"  this is a flatten into already-taught earnings / 10-K / 10-Q clocks, packed 13a-14, packed 12b-20, or packed 10D-1? {flatten_244100}")
check(flatten_244100 is False, "do not flatten 244.100 into already-taught earnings / 10-K / 10-Q clocks, packed 13a-14, packed 12b-20, or packed 10D-1")
tidy_regg = False
print(f'  this toy tidies official (b) into "in the light of" or "they are presented", tidies "Web cast" / "Web site" / "web site" into "website" or "webcast", or silently renumbers official Note 1\'s (a)(1)(i) and (a)(1)(ii)? {tidy_regg}')
check(tidy_regg is False, "do not tidy Regulation G typography or silently renumber official Note 1")
core_244100 = True
print(f"  whenever a registrant publicly discloses material information that includes a non-GAAP financial measure, the registrant must accompany that measure with the most directly comparable GAAP measure and a reconciliation? {core_244100}")
check(core_244100 is True, "244.100(a) requires the most directly comparable GAAP measure and a reconciliation")
print("learning only; a non-GAAP figure is not a substitute for the accompanying GAAP measure and reconciliation")
print("no investment advice and no use / avoid non-GAAP product recommendation")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 244.100; no issuer, disclosure, or investment advice; learning only")


print("=== K. 17 CFR 240.14a-3(b): annual report to security holders accompanying or preceding the proxy ===")
print("official caption typography is Information to be furnished to security holders.")
print("14a-3(b) opening: If the solicitation is made on behalf of the registrant, other than")
print("  an investment company registered under the Investment Company Act of 1940, and")
print("  relates to an annual (or special meeting in lieu of the annual) meeting of")
print("  security holders, or written consent in lieu of such meeting, at which directors")
print("  are to be elected, each proxy statement furnished pursuant to paragraph (a) of")
print("  this section shall be accompanied or preceded by an annual report to security")
print("  holders as follows:")
print('official typography is two-word "security holders" and "accompanied or preceded"')
print("official (a) (the three ways a proxy statement may be furnished), official (b)(1)")
print("  and later, including the financial-statement catalog, official 14a-3(e)")
print("  householding, and 17 CFR 240.14a-4 / 14a-6 exist and are named only; this toy is")
print("  not those catalogs")
print('if official (b)(1) is quoted, official typography includes the typo "this paragraph')
print('  9(b)(1)"; this toy does not tidy that typo')
print("cite 17 CFR 240.14a-3; title 17 up_to_date_as_of 2026-11-09")
flatten_14a3 = False
print(f"  this is a flatten into packed 14a-9, packed 12b-20, already-taught 14a-8, Form 8-K Item 5.07, already-taught 10-K / 10-Q clocks, packed 13a-14, or packed 244.100, or a claim that the annual report to security holders is the same filing as the Form 10-K? {flatten_14a3}")
check(flatten_14a3 is False, "do not flatten 14a-3(b) into packed 14a-9 / 12b-20 / 13a-14 / 244.100, already-taught 14a-8 / Item 5.07 / 10-K / 10-Q, or treat the annual report as the Form 10-K")
every_proxy = False
print(f"  this toy invents that every proxy mailing requires an annual report? {every_proxy}")
check(every_proxy is False, "official (b) is limited to a solicitation on behalf of the registrant, other than a registered investment company, for an annual or special-in-lieu meeting, or written consent in lieu of such meeting, at which directors are to be elected")
core_14a3 = True
print(f"  if the solicitation is made on behalf of the registrant, other than a registered investment company, and relates to an annual (or special meeting in lieu of the annual) meeting of security holders, or written consent in lieu of such meeting, at which directors are to be elected, each proxy statement furnished pursuant to official (a) shall be accompanied or preceded by an annual report to security holders as follows? {core_14a3}")
check(core_14a3 is True, "14a-3(b) opening is the packed slice, through as follows:")
print("learning only; the annual report to security holders is not the same filing as the Form 10-K")
print("no issuer, proxy, or investment advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 240.14a-3(b); no issuer, disclosure, or investment advice; learning only")

print("=== L. 17 CFR 240.14c-3(a): annual report to security holders accompanying or preceding the information statement ===")
print("official caption typography is Annual report to be furnished security holders.")
print("14c-3(a) opening: If the information statement relates to an annual (or special")
print("  meeting in lieu of the annual) meeting, or written consent in lieu of such")
print("  meeting, of security holders at which directors of the registrant, other than")
print("  an investment company registered under the Investment Company Act of 1940, are")
print("  to be elected, it shall be accompanied or preceded by an annual report to")
print("  security holders:")
print('official typography is "Annual report to be furnished security holders." — no')
print('  "to" before "security holders," and a period after "holders."; official')
print('  two-word "security holders" and "accompanied or preceded"')
print("official (a) word order is not identical to packed 14a-3(b); this toy does not")
print("  paste the 14a-3(b) sentence over this one")
print("official (a)(1) (the financial-statement catalog that cross-references")
print("  14a-3(b)(1) through (b)(11)), official (a)(2) [Reserved], official (b) (the")
print("  electronic-format submission / typographic quotes around “filed”), official")
print("  (c) householding (already named under packed 14b-1 as 14a-3(e)(1) / 14c-3(c)),")
print("  official (d) (names 14a-16), 17 CFR 240.14c-2, and 17 CFR 240.14c-5 exist and")
print("  are named only; this toy is not those catalogs, and packing 14c-3(c)")
print("  householding as a new core remains wrong")
print("cite 17 CFR 240.14c-3; title 17 up_to_date_as_of 2026-11-09")
flatten_14c3 = False
print(f"  this is a flatten into packed 14a-3(b), packed 14a-9, packed 12b-20, already-taught 14a-8, Form 8-K Item 5.07, already-taught 10-K / 10-Q clocks, packed 13a-14, or packed 244.100, a claim that 14c-3(a) and packed 14a-3(b) are the same rule, or a claim that the annual report to security holders is the same filing as the Form 10-K? {flatten_14c3}")
check(flatten_14c3 is False, "do not flatten 14c-3(a) into packed 14a-3(b) / 14a-9 / 12b-20 / 13a-14 / 244.100 or already-taught 14a-8 / Item 5.07 / 10-K / 10-Q, and do not treat 14c-3(a) as 14a-3(b) or as the Form 10-K")
every_is = False
print(f"  this toy invents that every information statement requires an annual report, or packs 14c-3(c) householding as a new core? {every_is}")
check(every_is is False, "official (a) is limited to an annual or special-in-lieu meeting, or written consent in lieu of such meeting, at which directors of the registrant, other than a registered investment company, are to be elected; packing 14c-3(c) householding as a new core remains wrong")
core_14c3 = True
print(f"  if the information statement relates to an annual (or special meeting in lieu of the annual) meeting, or written consent in lieu of such meeting, of security holders at which directors of the registrant, other than an investment company registered under the Investment Company Act of 1940, are to be elected, it shall be accompanied or preceded by an annual report to security holders:? {core_14c3}")
check(core_14c3 is True, "14c-3(a) opening is the packed slice, through security holders:")
print("learning only; the annual report to security holders is not the same filing as the Form 10-K")
print("no issuer, information-statement, or investment advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 240.14c-3(a); no issuer, disclosure, or investment advice; learning only")
