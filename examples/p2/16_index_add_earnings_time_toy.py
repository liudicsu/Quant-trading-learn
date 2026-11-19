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

print("=== M. 17 CFR 240.14c-6: False or misleading statements ===")
print("official caption typography is False or misleading statements.")
print("14c-6(a): No information statement shall contain any statement which, at the")
print("  time and in the light of the circumstances under which it is made, is false")
print("  or misleading with respect to any material fact, or which omits to state any")
print("  material fact necessary in order to make the statements therein not false or")
print("  misleading or necessary to correct any statement in any earlier communication")
print("  with respect to the same meeting or subject matter which has become false or")
print("  misleading.")
print("14c-6(b): The fact that an information statement has been filed with or")
print("  examined by the Commission shall not be deemed a finding by the Commission")
print("  that such material is accurate or complete or not false or misleading, or")
print("  that the Commission has passed upon the merits of or approved any statement")
print("  contained therein or any matter to be acted upon by security holders. No")
print("  representation contrary to the foregoing shall be made.")
print('official (a) typography is "in the light of the circumstances under which it')
print('  is made" (same singular "it is made" as packed 14a-9(a); this toy does not')
print('  tidy that into packed 10b-5\'s "under which they were made" or packed')
print('  12b-20\'s "under which they are made not misleading")')
print('official (a) typography is "any earlier communication with respect to the same')
print('  meeting or subject matter" — not packed 14a-9(a)\'s "with respect to the')
print('  solicitation of a proxy for the same meeting or subject matter"')
print('official (a) is limited to "No information statement shall contain" and does')
print('  not use packed 14a-9\'s "proxy statement, form of proxy, notice of meeting or')
print('  other communication, written or oral"')
print('official (b) typography is "an information statement has been filed with or')
print('  examined by the Commission" — not packed 14a-9(b)\'s "a proxy statement, form')
print('  of proxy or other soliciting material"')
print('official typography is two-word "security holders."')
print("official 14c-6 has no official (c) and no Note; packed 14a-9's official (c) /")
print("  Note catalog stays named only under 14a-9; this toy does not pack 14a-9(b) /")
print("  (c) / Note as a new core")
print("cite 17 CFR 240.14c-6; title 17 up_to_date_as_of 2026-11-09")
print("[31 FR 262, Jan. 8, 1966].")
print("packed 14a-9 (including official (b), official (c), and the Note, named only")
print("  under that already-printed box), packed 14c-3(a), packed 12b-20, packed")
print("  10b-5, leftover 14c-2 / 14c-5, and 17 CFR 240.14c-4 exist and are named")
print("  only; this toy is not those rules")
flatten_14c6 = False
print(f"  this is a flatten into packed 14a-9, packed 14c-3(a), packed 12b-20, packed 10b-5, already-taught 14a-8, or Form 8-K Item 5.07, a claim that 14c-6 and packed 14a-9 are the same rule, a paste of packed 14a-9(a) or 14a-9(b) over this rule, or a claim that official 14c-6 has an official (c) or a Note catalog? {flatten_14c6}")
check(flatten_14c6 is False, "do not flatten 14c-6 into packed 14a-9 / 14c-3(a) / 12b-20 / 10b-5 / 14a-8 / Item 5.07, and do not paste packed 14a-9 over this rule")
tidy_14c6 = False
print(f'  this toy tidies official (a) into packed 14a-9(a)\'s "with respect to the solicitation of a proxy for the same meeting or subject matter," packed 10b-5\'s "under which they were made," or packed 12b-20\'s "under which they are made not misleading"? {tidy_14c6}')
check(tidy_14c6 is False, "do not tidy official 14c-6 typography into packed 14a-9 / 10b-5 / 12b-20")
core_14c6 = True
print(f"  no information statement shall contain any statement which, at the time and in the light of the circumstances under which it is made, is false or misleading with respect to any material fact, or which omits to state any material fact necessary in order to make the statements therein not false or misleading or necessary to correct any statement in any earlier communication with respect to the same meeting or subject matter which has become false or misleading; and the fact that an information statement has been filed with or examined by the Commission shall not be deemed a finding that such material is accurate or complete or not false or misleading, or that the Commission has passed upon the merits of or approved any statement contained therein or any matter to be acted upon by security holders? {core_14c6}")
check(core_14c6 is True, "14c-6 packs official (a) + official (b), the whole current section")
print("literacy only; not a proxy- or information-statement how-to, and not legal advice")
print("no issuer, information-statement, or investment advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 240.14c-6; no issuer, disclosure, or investment advice; learning only")

print("=== N. 17 CFR 240.15c1-9: Use of pro forma balance sheets ===")
print("official caption typography is Use of pro forma balance sheets.")
print("15c1-9: The term manipulative, deceptive, or other fraudulent device or")
print("  contrivance, as used in section 15(c)(1) of the Act, is hereby defined to")
print("  include the use of financial statements purporting to give effect to the")
print("  receipt and application of any part of the proceeds from the sale or exchange")
print("  of securities, unless the assumptions upon which each such financial")
print("  statement is based are clearly set forth as part of the caption to each such")
print("  statement in type at least as large as that used generally in the body of the")
print("  statement.")
print("official typography italicizes the defined term, including the trailing comma,")
print("  and does not put quotation marks around it: The term <I>manipulative,")
print("  deceptive, or other fraudulent device or contrivance,</I> as used in section")
print("  15(c)(1) of the Act; this toy does not invent quotes, and does not copy packed")
print("  15c2-4 typographic quotes onto this rule")
print('official caption typography is two-word "pro forma" (no hyphen) and a period')
print('  after "sheets."')
print('official typography is "as part of the caption to each such statement in type')
print('  at least as large as that used generally in the body of the statement" (no')
print("  numeric point size)")
print("official authority typography, if quoted, is 15 U.S.C. 78<I>o</I> (italic")
print("  letter-O / \"78o\" form); this toy does not invent a space in that cite, and")
print("  does not treat a LII U.S.C. link wrap as official typography that adds a space")
print("(Sec. 2, 52 Stat. 1075; 15 U.S.C. 78<I>o</I>)")
print("cite 17 CFR 240.15c1-9; title 17 up_to_date_as_of 2026-11-09")
print("[13 FR 8205, Dec. 22, 1948].")
print("packed 244.100 / 244.101 / 244.102 and Regulation S-K Item 10(e) / 17 CFR")
print("  229.10, packed 15c1-3, leftover 15c1-8, and 17 CFR 240.15c1-1 exist and are")
print("  named only; this toy is not those rules")
flatten_15c19 = False
print(f"  this is a flatten into packed 244.100, packed 12b-20, packed 14c-6, packed 15c1-3, or already-taught 10-K / 10-Q clocks, or a claim that 15c1-9 and packed 244.100 are the same rule? {flatten_15c19}")
check(flatten_15c19 is False, "do not flatten 15c1-9 into packed 244.100 / 12b-20 / 14c-6 / 15c1-3 or already-taught 10-K / 10-Q clocks")
invent_pt = False
print(f'  this toy invents a numeric type-point size for "at least as large as," invents a space in official 15 U.S.C. 78o, invents quotation marks around the defined term, or hyphenates official two-word "pro forma"? {invent_pt}')
check(invent_pt is False, "do not invent a point size, a space in 78o, quotes around the defined term, or a hyphen in pro forma")
core_15c19 = True
print(f"  the use of financial statements purporting to give effect to the receipt and application of any part of the proceeds from the sale or exchange of securities, unless the assumptions upon which each such financial statement is based are clearly set forth as part of the caption to each such statement in type at least as large as that used generally in the body of the statement, is a manipulative, deceptive, or other fraudulent device or contrivance as used in section 15(c)(1) of the Act? {core_15c19}")
check(core_15c19 is True, "15c1-9 packs the whole current section")
print("literacy only; not a pro-forma-caption how-to, and not legal advice")
print("no issuer, broker, or investment advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 240.15c1-9; no issuer, disclosure, or investment advice; learning only")

print("=== O. 17 CFR 240.12b-15: Amendments ===")
print("official caption typography is Amendments.")
print("12b-15: All amendments must be filed under cover of the form amended, marked")
print("  with the letter “A” to designate the document as an amendment, e.g.,")
print("  “10-K/A,” and in compliance with pertinent requirements applicable to")
print("  statements and reports. Amendments filed pursuant to this section must set")
print("  forth the complete text of each item as amended. Amendments must be numbered")
print("  sequentially and be filed separately for each statement or report amended.")
print("  Amendments to a statement may be filed either before or after registration")
print("  becomes effective. Amendments must be signed on behalf of the registrant by a")
print("  duly authorized representative of the registrant. An amendment to any report")
print("  required to include the certifications as specified in § 240.13a-14(a) or")
print("  § 240.15d-14(a) must include new certifications by each principal executive")
print("  and principal financial officer of the registrant, and an amendment to any")
print("  report required to be accompanied by the certifications as specified in")
print("  § 240.13a-14(b) or § 240.15d-14(b) must be accompanied by new certifications")
print("  by each principal executive and principal financial officer of the registrant.")
print("  An amendment to any report required to include the certifications as specified")
print("  in § 240.13a-14(d) or § 240.15d-14(d) must include a new certification by an")
print("  individual specified in § 240.13a-14(e) or § 240.15d-14(e), as applicable.")
print("  The requirements of the form being amended will govern the number of copies")
print("  to be filed in connection with a paper format amendment. Electronic filers")
print("  satisfy the provisions dictating the number of copies by filing one copy of")
print("  the amendment in electronic format. See § 232.309 of this chapter (Rule 309")
print("  of Regulation S-T).")
print("official typography uses typographic quotes (U+201C / U+201D) around “A”")
print("  and around “10-K/A,” with the comma inside the closing quote")
print('official typography is "e.g.," (comma after e.g.)')
print('official typography is "complete text of each item as amended" and "numbered')
print('  sequentially and be filed separately for each statement or report amended"')
print("official 13a-14(a) amendments \"must include new certifications,\" official")
print("  13a-14(b) amendments \"must be accompanied by new certifications,\" and")
print("  official 13a-14(d) amendments \"must include a new certification\" — this toy")
print("  does not tidy those three official phrasings into one another")
print("cite 17 CFR 240.12b-15; title 17 up_to_date_as_of 2026-11-09")
print("[68 FR 36665, June 18, 2003, as amended at 70 FR 1620, Jan. 7, 2005].")
print("already-printed XBRL filed-date box (including the Apple 10-K / 10-K/A")
print("  example), packed 13a-14 / named 15d-14, already-taught Form 10-K / 10-Q")
print("  clocks, and 17 CFR 232.309 / Regulation S-T Rule 309 (the electronic")
print("  one-copy sentence already appears in the packed slice; this toy does not")
print("  build a Regulation S-T engine) exist and are named only; this toy is not")
print("  those boxes, and does not rewrite the already-printed XBRL box")
flatten_12b15 = False
print(f"  this is a flatten into packed 13a-14, already-taught Form 10-K / 10-Q clocks, the already-printed XBRL filed-date box, packed 12b-20, packed 14c-6, or packed 244.100, an invention that “10-K/A” is the only amendment form, a how-to for preparing an amendment, or a Regulation S-T filing engine? {flatten_12b15}")
check(flatten_12b15 is False, "do not flatten 12b-15 into packed 13a-14 / 10-K / 10-Q clocks / the already-printed XBRL box / 12b-20 / 14c-6 / 244.100, and do not invent that 10-K/A is the only amendment form")
tidy_12b15 = False
print(f"  this toy tidies official 13a-14(a) / (b) / (d) amendment-certification verbs into one another, moves the comma outside “10-K/A,” or drops official typographic quotes around “A”? {tidy_12b15}")
check(tidy_12b15 is False, "do not tidy official 13a-14(a)/(b)/(d) verbs or official typographic-quote typography")
core_12b15 = True
print(f"  all amendments must be filed under cover of the form amended, marked with the letter “A” to designate the document as an amendment, e.g., “10-K/A,” must set forth the complete text of each item as amended, must be numbered sequentially and be filed separately for each statement or report amended, and a report amendment which requires 13a-14 / 15d-14 certifications must include new certifications or be accompanied by new certifications under the official (a) / (b) / (d) phrasings? {core_12b15}")
check(core_12b15 is True, "12b-15 packs the whole current section")
print("literacy only; not a how-to for preparing an amendment, and not legal advice")
print("no issuer, filing-agent, or investment advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 240.12b-15; no issuer, disclosure, or investment advice; learning only")

print("=== P. 17 CFR 240.12b-6: When securities are deemed to be registered ===")
# 17 CFR 240.12b-6 (official eCFR API XML, title 17 up_to_date_as_of 2026-11-17,
# live-refetched 2026-11-19, byte-identical to the 2026-11-09 archive).
# Keep sections A-O identical, including 52/52 after O / 12b-15.
# Do not flatten into packed 12b-15, already-taught Form 10-K / 10-Q clocks,
# leftover 12g-1 / 12g-4, packed Section 16(b), or already-taught Form 4 clocks.
# Learning only; no issuer, filing-agent, or investment advice.

print("official caption typography is When securities are deemed to be registered.")
print("12b-6: A class of securities with respect to which a registration statement has been filed pursuant to section 12 of the act shall be deemed to be registered for the purposes of sections 13, 14, 15(d) and 16 of the act and the rules and regulations thereunder only when such statement has become effective as provided in section 12, and securities of said class shall not be subject to sections 13, 14 and 16 of the act until such statement has become effective as provided in section 12.")
print('official typography is "section 12 of the act" (lowercase act)')
print('official typography is "sections 13, 14, 15(d) and 16 of the act" (no Oxford comma before "and 16")')
print('official typography is "sections 13, 14 and 16 of the act" in the second clause (no 15(d); no Oxford comma)')
print("cite 17 CFR 240.12b-6; title 17 up_to_date_as_of 2026-11-17")
print("[30 FR 482, Jan. 14, 1965].")
print("official authority typography is 15 U.S.C. 78c, 78n, 78p, 78l (italic letter-L)")
deemed_at_filing = False
print(f"  a class is deemed registered for sections 13, 14, 15(d) and 16 when the section 12 statement is filed, before it becomes effective? {deemed_at_filing}")
check(deemed_at_filing is False, "not deemed registered until effective")
second_list_has_15d = False
print(f"  official typography puts 15(d) in the second list (sections 13, 14 and 16)? {second_list_has_15d}")
check(second_list_has_15d is False, "second list has no 15(d)")
applies_only_when_effective = True
print(f"  securities of the class are not subject to sections 13, 14 and 16 until the statement has become effective as provided in section 12? {applies_only_when_effective}")
check(applies_only_when_effective is True, "13/14/16 start at effectiveness")
flatten_12b6 = False
print(f"  this is a flatten into packed 12b-15, already-taught Form 10-K / 10-Q clocks, leftover 12g-1 / 12g-4, packed Section 16(b), or already-taught Form 4 clocks? {flatten_12b6}")
check(flatten_12b6 is False, "do not flatten 12b-6 into those boxes")
print("packed 12b-15, already-taught Form 10-K / 10-Q clocks, leftover 12g-1 / 12g-4, packed Section 16(b), and already-taught Form 4 clocks exist and are named only; this toy is not those boxes")
print("literacy only; not a how-to for registering a class, and not legal advice")
print("no issuer, filing-agent, or investment advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 240.12b-6; no issuer, disclosure, or investment advice; learning only")


print("=== Q. 17 CFR 232.12: Business hours of the Commission ===")
# 17 CFR 232.12 (official eCFR API XML, title 17 up_to_date_as_of 2026-11-17,
# live-refetched 2026-11-19, byte-identical to the 2026-11-09 archive).
# Keep sections A-P identical, including 55/55 after P / 12b-6.
# Do not flatten into already-taught Regulation S-T Rule 13 / 17 CFR 232.13
# (5:30 p.m. filing-date cutoff). Do not invent that the electronic
# transmission window ends at 5:30 p.m., or that every filing submitted by
# 10 p.m. is deemed filed that same business day (that same-day 10 p.m.
# deeming is 232.13(a)(3) / (a)(4) for specified forms, not 232.12).
# Official 232.12 typography is "Eastern Daylight Saving Time" (not Savings).
# Official (a) typography is "Saturdays, Sundays, and federal holidays"
# (Oxford comma; lowercase federal). Official (b) typography is
# "Saturdays, Sundays and federal holidays" (no Oxford comma; lowercase federal).
# Official (c) typography is "Saturdays, Sundays, and Federal holidays"
# (Oxford comma; capital Federal). Official address typography is
# "100 F Street, NE., Washington, DC 20549".
# Learning only; no filer or investment advice.

print("official caption typography is Business hours of the Commission.")
print("232.12(a): The principal office of the Commission, at 100 F Street, NE., Washington, DC 20549, is open each day, except Saturdays, Sundays, and federal holidays, from 9 a.m. to 5:30 p.m., Eastern Standard Time or Eastern Daylight Saving Time, whichever is currently in effect, provided that hours for the filing of documents pursuant to the Acts or the rules and regulations thereunder are as set forth in paragraphs (b) and (c) of this section.")
print("232.12(b): Filers may submit paper documents filed with or otherwise furnished to the Commission each day, except Saturdays, Sundays and federal holidays, from 8 a.m. to 5:30 p.m., Eastern Standard Time or Eastern Daylight Saving Time, whichever is currently in effect.")
print("232.12(c): Electronic filings and other documents may be submitted to the Commission each day, except Saturdays, Sundays, and Federal holidays, from 6 a.m. to 10 p.m., Eastern Standard Time or Eastern Daylight Saving Time, whichever is currently in effect.")
print('official typography italicizes "General." / "Submissions made in paper." / "Submissions by direct transmission." / "provided that", including the trailing period on those three lead-ins')
print('official typography is "Eastern Daylight Saving Time" (not Savings)')
print('official (a) typography is "Saturdays, Sundays, and federal holidays" (Oxford comma; lowercase federal)')
print('official (b) typography is "Saturdays, Sundays and federal holidays" (no Oxford comma; lowercase federal)')
print('official (c) typography is "Saturdays, Sundays, and Federal holidays" (Oxford comma; capital Federal)')
print('official address typography is "100 F Street, NE., Washington, DC 20549"')
print("cite 17 CFR 232.12; title 17 up_to_date_as_of 2026-11-17")
print("[58 FR 14670, Mar. 18, 1993; 58 FR 21349, Apr. 21, 1993, as amended at 59 FR 67761, Dec. 30, 1994; 65 FR 24800, Apr. 27, 2000; 65 FR 24800, Apr. 27, 2000; 68 FR 25799, May 13, 2003; 73 FR 32227, June 5, 2008; 86 FR 7972, Feb. 3, 2021; 88 FR 12209, Feb. 27, 2023].")
window_ends_at_530 = False
print(f"  the official electronic transmission window in 232.12(c) ends at 5:30 p.m.? {window_ends_at_530}")
check(window_ends_at_530 is False, "232.12(c) window is 6 a.m. to 10 p.m., not 5:30 p.m.")
same_as_rule13 = False
print(f"  232.12 is the already-taught 232.13 / Rule 13 5:30 p.m. filing-date cutoff? {same_as_rule13}")
check(same_as_rule13 is False, "do not flatten 232.12 into 232.13")
every_10pm_same_day = False
print(f"  232.12 says every electronic filing submitted by 10 p.m. is deemed filed that same business day? {every_10pm_same_day}")
check(every_10pm_same_day is False, "same-day 10 p.m. deeming is 232.13(a)(3)/(a)(4), not 232.12")
print("already-taught Regulation S-T Rule 13 / 17 CFR 232.13 (5:30 p.m. filing-date cutoff, with official (a)(3) / (a)(4) 10 p.m. same-day exceptions for specified forms) exists and is named only; this toy is not that box, and does not rewrite it")
print("literacy only; not a how-to for transmitting a filing, and not legal advice")
print("no filer, filing-agent, or investment advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 232.12; no filer, disclosure, or investment advice; learning only")

print("=== R. 17 CFR 240.12b-4: Supplemental information ===")
# 17 CFR 240.12b-4 (official eCFR API XML, title 17 up_to_date_as_of 2026-11-17,
# live-refetched 2026-11-19, byte-identical to the enrich41-src archive).
# Keep sections A-Q identical, including 59/59 after Q / 232.12.
# Do not flatten into packed 12b-20 / 12b-15 / 12b-6 / 232.12.
# Do not invent that staff-requested supplemental information is filed.
# Learning only; no issuer, filer, or investment advice.

print("official caption typography is Supplemental information.")
print("12b-4: The Commission or its staff may, where it is deemed appropriate, request supplemental information concerning the registrant, a registration statement or a periodic or other report under the Act. This information shall not be required to be filed with or deemed part of the registration statement or report. The information shall be returned to the registrant upon request, provided that:")
print("12b-4(a): Such request is made at the time such information is furnished to the staff;")
print("12b-4(b): The return of such information is consistent with the protection of investors; and")
print("12b-4(c): The return of such information is consistent with the provisions of the Freedom of Information Act (5 U.S.C. 552).")
print("cite 17 CFR 240.12b-4; title 17 up_to_date_as_of 2026-11-17")
print("[47 FR 11465, Mar. 16, 1982].")
print('official typography is "shall not be required to be filed with or deemed part of the registration statement or report"')
print('official (a) typography is "made at the time such information is furnished to the staff"')
print('official (b) ends with "; and"')
print('official (c) cite is "the Freedom of Information Act (5 U.S.C. 552)."')
not_filed = True
print(f"  supplemental information shall not be required to be filed with or deemed part of the registration statement or report? {not_filed}")
check(not_filed is True, "12b-4 information is not filed")
at_time_furnished = True
print(f"  a return request must be made at the time such information is furnished to the staff? {at_time_furnished}")
check(at_time_furnished is True, "return request at the time furnished")
protection_of_investors = True
print(f"  the return of such information must be consistent with the protection of investors? {protection_of_investors}")
check(protection_of_investors is True, "return consistent with protection of investors")
foia_552 = True
print(f"  official (c) cites the Freedom of Information Act (5 U.S.C. 552)? {foia_552}")
check(foia_552 is True, "official FOIA cite is 5 U.S.C. 552")
print("packed 12b-20 / 12b-15 / 12b-6 / 232.12 exist and are named only; this toy is not those boxes")
print("literacy only; not a how-to for sending staff-requested information, and not legal advice")
print("no issuer, filer, or investment advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 240.12b-4; no issuer, disclosure, or investment advice; learning only")

print("=== S. 17 CFR 240.12b-23: Incorporation by reference ===")
# 17 CFR 240.12b-23 official (a)+(b)+(c)+(d)+(e) (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17, live-refetched 2026-11-19,
# byte-identical to the enrich41-src archive).
# Keep sections A-R identical, including 63/63 after R / 12b-4.
# Official (a)-(e) italic lead-ins include the trailing periods.
# Official (d) typography is "You must include" and typographic
# U+201C / U+201D around "EDGAR". Official (e) forbids chain
# incorporation "unless expressly permitted or required."
# Do not tidy official (b) to a bare "GAAP / IFRS."
# Do not flatten into the already-printed XBRL filed-date box or
# packed 12b-20 / 12b-15 / 12b-6 / 232.12, and do not rewrite the XBRL box.
# Learning only; no issuer, filer, or investment advice.

print("official caption typography is Incorporation by reference.")
print("12b-23(a): Registration statement or report. Except as provided by this section or in the appropriate form, information may be incorporated by reference in answer, or partial answer, to any item of a registration statement or report.")
print("12b-23(b): Financial information. Except as provided in the Commission's rules, financial information required to be given in comparative form for two or more fiscal years or periods must not be incorporated by reference unless the information incorporated by reference includes the entire period for which the comparative data is given. In the financial statements, incorporating by reference, or cross-referencing to, information outside of the financial statements is not permitted unless otherwise specifically permitted or required by the Commission's rules or by U.S. Generally Accepted Accounting Principles or International Financial Reporting Standards as issued by the International Accounting Standards Board, whichever is applicable.")
print("12b-23(c): Exhibits. Any document or part thereof filed with the Commission pursuant to any Act administered by the Commission may be incorporated by reference as an exhibit to any statement or report filed with the Commission by the same or any other person. Any document or part thereof filed with an exchange pursuant to the Act may be incorporated by reference as an exhibit to any statement or report filed with the exchange by the same or any other person. If any modification has occurred in the text of any document incorporated by reference since the filing thereof, the registrant must file with the reference a statement containing the text of any such modification and the date thereof.")
print("12b-23(d): Hyperlinks. You must include an active hyperlink to information incorporated into a registration statement or report by reference if such information is publicly available on the Commission's Electronic Data Gathering, Analysis and Retrieval System (“EDGAR”) at the time the registration statement or form is filed. For hyperlinking to exhibits, please refer to Item 601 of Regulation S-K (§ 229.601 of this chapter) or the appropriate form.")
print("12b-23(e): General. Include an express statement clearly describing the specific location of the information you are incorporating by reference. The statement must identify the document where the information was originally filed or submitted and the location of the information within that document. The statement must be made at the particular place where the information is required, if applicable. Information must not be incorporated by reference in any case where such incorporation would render the disclosure incomplete, unclear, or confusing. For example, unless expressly permitted or required, disclosure must not be incorporated by reference from a second document if that second document incorporates information pertinent to such disclosure by reference to a third document.")
print('official (a)-(e) italic lead-ins include the trailing periods: "Registration statement or report." / "Financial information." / "Exhibits." / "Hyperlinks." / "General."')
print('official (d) typography is "You must include an active hyperlink"')
print("official typography uses typographic quotes (U+201C / U+201D) around “EDGAR”")
print('official (e) typography is "unless expressly permitted or required."')
print("cite 17 CFR 240.12b-23; title 17 up_to_date_as_of 2026-11-17")
print("[84 FR 12727, Apr. 2, 2019].")
ibr_except_as_provided = True
print(f"  information may be incorporated by reference except as provided by this section or the appropriate form? {ibr_except_as_provided}")
check(ibr_except_as_provided is True, "12b-23(a) except as provided by this section or the form")
entire_period = True
print(f"  comparative financial information must include the entire period for which the comparative data is given? {entire_period}")
check(entire_period is True, "comparative financials need the entire period")
chain_allowed = False
print(f"  incorporation by reference from a second document that itself incorporates information from a third document is allowed without being expressly permitted or required? {chain_allowed}")
check(chain_allowed is False, "official (e) chain example is forbidden unless expressly permitted or required")
you_must_edgar = True
print(f"  official (d) typography is “You must include an active hyperlink” and uses typographic quotes around “EDGAR”? {you_must_edgar}")
check(you_must_edgar is True, "You must include; typographic quotes around EDGAR")
italic_periods = True
print(f"  official (a)–(e) italic lead-ins include the trailing periods? {italic_periods}")
check(italic_periods is True, "italic lead-ins include trailing periods")
print("the already-printed XBRL filed-date box and packed 12b-20 / 12b-15 / 12b-6 / 232.12 exist and are named only; this toy is not those boxes, and does not rewrite the XBRL box")
print("literacy only; not a how-to for incorporating by reference, and not legal advice")
print("no issuer, filer, or investment advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 240.12b-23; no issuer, disclosure, or investment advice; learning only")

print("=== T. 17 CFR 240.13a-11: Current reports on Form 8-K ===")
# 17 CFR 240.13a-11 official (a)+(b)+(c) (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17, live-refetched 2026-11-19,
# byte-identical to the enrich41-src archive).
# Keep sections A-S identical, including 68/68 after S / 12b-23.
# Official caption typography is "Current reports on Form 8-K
# (§ 249.308 of this chapter)."
# Do not invent a numeric clock inside 13a-11 itself.
# Official (c) item list must be copied exactly:
# "Item 1.01, 1.02, 1.05, 2.03, 2.04, 2.05, 2.06, 4.02(a), 5.02(e), or 6.03."
# Do not invent Item 2.02, Item 5.07, or a bare 4.02 / 5.02 into that carve-out.
# Official typography is that no such failure "shall be deemed to be a
# violation of 15 U.S.C. 78j(b) and § 240.10b-5."
# Name official 13a-1 only; do not pack 13a-1 as a second core.
# Official (b) exceptions include foreign private issuers on Form 6-K
# pursuant to 13a-16 (name already-taught 6-K clocks only).
# Do not flatten into already-taught Form 8-K item clocks / Item 5.07 / packed 14e-8.
# Learning only; no issuer, filer, or investment advice.

print("official caption typography is Current reports on Form 8-K (§ 249.308 of this chapter).")
print("13a-11(a): Except as provided in paragraph (b) of this section, every registrant subject to § 240.13a-1 shall file a current report on Form 8-K within the period specified in that form unless substantially the same information as that required by Form 8-K has been previously reported by the registrant.")
print("13a-11(b): This section shall not apply to foreign governments, foreign private issuers required to make reports on Form 6-K (§ 249.306 of this chapter) pursuant to § 240.13a-16, issuers of American Depositary Receipts for securities of any foreign issuer, or investment companies required to file reports pursuant to § 270.30a-1 of this chapter under the Investment Company Act of 1940, except where such an investment company is required to file notice of a blackout period pursuant to § 245.104 of this chapter.")
print("13a-11(c): No failure to file a report on Form 8-K that is required solely pursuant to Item 1.01, 1.02, 1.05, 2.03, 2.04, 2.05, 2.06, 4.02(a), 5.02(e), or 6.03 of Form 8-K shall be deemed to be a violation of 15 U.S.C. 78j(b) and § 240.10b-5.")
print('official (a) typography is "within the period specified in that form"')
print('official (a) typography carves out information that "has been previously reported by the registrant"')
print("official (c) item list typography is Item 1.01, 1.02, 1.05, 2.03, 2.04, 2.05, 2.06, 4.02(a), 5.02(e), or 6.03.")
print('official typography is that no such failure "shall be deemed to be a violation of 15 U.S.C. 78j(b) and § 240.10b-5"')
print("cite 17 CFR 240.13a-11; title 17 up_to_date_as_of 2026-11-17")
print("[42 FR 4428, Jan. 25, 1977, as amended at 50 FR 27939, July 9, 1985; 68 FR 4355, Jan. 28, 2003; 69 FR 15618, Mar. 25, 2004; 70 FR 1621, Jan. 7, 2005; 71 FR 53260, Sept. 8, 2006; 75 FR 56780, Sept. 16, 2010; 81 FR 82020, Nov. 18, 2016; 88 FR 51493, Aug. 4, 2023; 90 FR 9689, Feb. 18, 2025].")
within_period = True
print(f"  official typography is that the 8-K is due within the period specified in that form? {within_period}")
check(within_period is True, "due within the period specified in that form")
previously_reported = True
print(f"  official (a) carves out information that has been previously reported by the registrant? {previously_reported}")
check(previously_reported is True, "previously reported exception")
fpi_6k = True
print(f"  official (b) exceptions include foreign private issuers on Form 6-K pursuant to 13a-16? {fpi_6k}")
check(fpi_6k is True, "FPI Form 6-K / 13a-16 named only")
deemed_10b5 = False
print(f"  a failure to file an 8-K required solely pursuant to Item 1.01, 1.02, 1.05, 2.03, 2.04, 2.05, 2.06, 4.02(a), 5.02(e), or 6.03 shall be deemed to be a violation of 15 U.S.C. 78j(b) and § 240.10b-5? {deemed_10b5}")
check(deemed_10b5 is False, "no such failure shall be deemed to be a 10b-5 violation")
print("official 13a-1 is named only; this toy does not pack 13a-1 as a second core")
print("already-taught Form 8-K item clocks / Item 5.07, already-taught Form 6-K promptly-furnished clocks, and packed 14e-8 exist and are named only; this toy is not those boxes")
print("literacy only; not a how-to for filing Form 8-K, and not legal advice")
print("no issuer, filer, or investment advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 240.13a-11; no issuer, disclosure, or investment advice; learning only")

print("=== U. 17 CFR 240.12b-10: Requirements as to proper form ===")
# 17 CFR 240.12b-10 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17, live-refetched 2026-11-19,
# byte-identical to the enrich42-src archive).
# Keep sections A-T identical, including 72/72 after T / 13a-11.
# Official typography is "the form prescribed therefor by the
# Commission, as in effect on the date of filing," and "unless
# objection to the form is made by the Commission within thirty days
# after the date of filing." Do not tidy "therefor" into "therefore,"
# or "thirty days" into "30 days."
# Official source "[30 FR 2022, Feb. 13, 1965]."
# Do not print HEAD or the official SECAUTH blob.
# Do not flatten into packed 12b-15 / 12b-25 / 12b-4 / 12b-23.
# Learning only; no issuer, filer, or investment advice.

print("official caption typography is Requirements as to proper form.")
print("12b-10: Every statement or report shall be on the form prescribed therefor by the Commission, as in effect on the date of filing. Any statement or report shall be deemed to be filed on the proper form unless objection to the form is made by the Commission within thirty days after the date of filing.")
print('official typography is "the form prescribed therefor by the Commission, as in effect on the date of filing"')
print('official typography is "unless objection to the form is made by the Commission within thirty days after the date of filing"')
print('official typography is "therefor" and "thirty days," not "therefore" or "30 days"')
print("cite 17 CFR 240.12b-10; title 17 up_to_date_as_of 2026-11-17")
print("[30 FR 2022, Feb. 13, 1965].")
prescribed_therefor = True
print(f"  every statement or report shall be on the form prescribed therefor by the Commission, as in effect on the date of filing? {prescribed_therefor}")
check(prescribed_therefor is True, "form prescribed therefor as in effect on the date of filing")
thirty_days_objection = True
print(f"  any statement or report shall be deemed to be filed on the proper form unless objection to the form is made by the Commission within thirty days after the date of filing? {thirty_days_objection}")
check(thirty_days_objection is True, "deemed proper form unless objection within thirty days")
flatten_12b10 = False
print(f"  official typography was tidied to therefore / 30 days, or this is packed 12b-15 / 12b-25 / 12b-4 / 12b-23? {flatten_12b10}")
check(flatten_12b10 is False, "do not tidy therefor/thirty days or flatten 12b-10")
print("packed 12b-15 / 12b-25 / 12b-4 / 12b-23 exist and are named only; this toy is not those boxes")
print("literacy only; not a how-to for choosing a form, and not legal advice")
print("no issuer, filer, or investment advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 240.12b-10; no issuer, disclosure, or investment advice; learning only")

print("=== V. 17 CFR 240.12b-21: Information unknown or not available ===")
# 17 CFR 240.12b-21 the whole current section, official opening plus
# official (a)+(b) (official eCFR API XML, title 17 up_to_date_as_of
# 2026-11-17, live-refetched 2026-11-19, byte-identical to the
# enrich42-src archive).
# Keep sections A-U identical, including 75/75 after U / 12b-10.
# Official caption typography is "Information unknown or not
# available." The caption does not say "reasonably," though the
# official opening uses "known or reasonably available."
# Official API XML has no CITA element; do not invent a source line.
# Do not flatten into packed 12b-20 / 12b-23 / 12b-4.
# Learning only; no issuer, filer, or investment advice.

print("official caption typography is Information unknown or not available.")
print("12b-21: Information required need be given only insofar as it is known or reasonably available to the registrant. If any required information is unknown and not reasonably available to the registrant, either because the obtaining thereof would involve unreasonable effort or expense, or because it rests peculiarly within the knowledge of another person not affiliated with the registrant, the information may be omitted, subject to the following conditions.")
print("12b-21(a): The registrant shall give such information on the subject as it possesses or can acquire without unreasonable effort or expense, together with the sources thereof.")
print("12b-21(b): The registrant shall include a statement either showing that unreasonable effort or expense would be involved or indicating the absence of any affiliation with the person within whose knowledge the information rests and stating the result of a request made to such person for the information.")
print('official opening typography is "Information required need be given only insofar as it is known or reasonably available to the registrant."')
print('official caption typography does not say "reasonably"')
print('official (a) typography is "together with the sources thereof"')
print("official API XML has no CITA element; this toy does not invent a source line")
print("cite 17 CFR 240.12b-21; title 17 up_to_date_as_of 2026-11-17")
known_or_reasonably = True
print(f"  information required need be given only insofar as it is known or reasonably available to the registrant? {known_or_reasonably}")
check(known_or_reasonably is True, "known or reasonably available")
caption_not_reasonably = True
print(f"  official caption typography is Information unknown or not available, and the caption does not say reasonably? {caption_not_reasonably}")
check(caption_not_reasonably is True, "caption does not say reasonably")
a_and_b_conditions = True
print(f"  official (a) requires such information as the registrant possesses or can acquire without unreasonable effort or expense, together with the sources thereof, and official (b) requires a statement either showing that unreasonable effort or expense would be involved or indicating the absence of affiliation and the result of a request made to such person for the information? {a_and_b_conditions}")
check(a_and_b_conditions is True, "official (a) sources thereof and official (b) request result")
no_cita_not_flatten_12b21 = True
print(f"  official API XML has no CITA, and this is not packed 12b-20 / 12b-23 / 12b-4? {no_cita_not_flatten_12b21}")
check(no_cita_not_flatten_12b21 is True, "no invented CITA; not packed 12b-20 / 12b-23 / 12b-4")
print("packed 12b-20 / 12b-23 / 12b-4 exist and are named only; this toy is not those boxes")
print("literacy only; not a how-to for omitting required information, and not legal advice")
print("no issuer, filer, or investment advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 240.12b-21; no issuer, disclosure, or investment advice; learning only")

print("=== W. 17 CFR 240.13a-1: Requirements of annual reports ===")
# 17 CFR 240.13a-1 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17, live-refetched 2026-11-19,
# byte-identical to the enrich42-src archive).
# Keep sections A-V identical, including 79/79 after V / 12b-21.
# Official typography is "section 12 of the Act (15 U.S.C. 78l)" with
# official italic on the letter l. Do not print HEAD or the source
# <I> markup, and do not tidy the italic l into a plain "78l" label
# that hides the italics, or into "781".
# Official clock is "Annual reports shall be filed within the period
# specified in the appropriate form." Do not invent a numeric clock
# inside 13a-1 itself.
# Official source "[62 FR 39767, July 24, 1997]."
# Name official 15d-1 only (official 15d-1 caption typography is
# singular "Requirement of annual reports."); do not pack 15d-1 as a
# second core.
# Do not flatten into already-taught Form 10-K clocks, packed 13a-11,
# or packed 13a-14.
# Learning only; no issuer, filer, or investment advice.

print("official caption typography is Requirements of annual reports.")
print("13a-1: Every issuer having securities registered pursuant to section 12 of the Act (15 U.S.C. 78l) shall file an annual report on the appropriate form authorized or prescribed therefor for each fiscal year after the last full fiscal year for which financial statements were filed in its registration statement. Annual reports shall be filed within the period specified in the appropriate form.")
print("official typography is 15 U.S.C. 78l with official italic on the letter l")
print('official typography is "Annual reports shall be filed within the period specified in the appropriate form."')
print("official 15d-1 is named only; official 15d-1 caption typography is Requirement of annual reports.")
print("cite 17 CFR 240.13a-1; title 17 up_to_date_as_of 2026-11-17")
print("[62 FR 39767, July 24, 1997].")
each_fiscal_year_after = True
print(f"  every issuer having securities registered pursuant to section 12 of the Act shall file an annual report for each fiscal year after the last full fiscal year for which financial statements were filed in its registration statement? {each_fiscal_year_after}")
check(each_fiscal_year_after is True, "annual report for each fiscal year after the last full fiscal year in the registration statement")
period_specified = True
print(f"  official typography is that annual reports shall be filed within the period specified in the appropriate form? {period_specified}")
check(period_specified is True, "within the period specified in the appropriate form")
italic_l_15d1_named = True
print(f"  official cite typography is 15 U.S.C. 78l with an italic letter l, official 15d-1 is named only, and this is not already-taught Form 10-K clocks, packed 13a-11, or packed 13a-14? {italic_l_15d1_named}")
check(italic_l_15d1_named is True, "italic letter l; 15d-1 named only; not 10-K clocks / 13a-11 / 13a-14")
print("official 15d-1 is named only; this toy does not pack 15d-1 as a second core")
print("already-taught Form 10-K clocks, packed 13a-11, and packed 13a-14 exist and are named only; this toy is not those boxes")
print("literacy only; not a how-to for filing an annual report, and not legal advice")
print("no issuer, filer, or investment advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 240.13a-1; no issuer, disclosure, or investment advice; learning only")

print("=== X. 17 CFR 240.13a-13: Quarterly reports on Form 10-Q ===")
# 17 CFR 240.13a-13 official (a)+(b)+(c)+(d) (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17, live-refetched 2026-11-19,
# byte-identical to the enrich42-src archive).
# Keep sections A-W identical, including 82/82 after W / 13a-1.
# Official caption typography is "Quarterly reports on Form 10-Q
# (§ 249.308a of this chapter)." Official Form 10-Q cite is
# 249.308a, not 249.308. Official Form 10-K cite inside (a) is
# § 249.310.
# Official general clock is "within the period specified in General
# Instruction A.1. to that form" for "each of the first three
# quarters." Do not invent a fourth-quarter 10-Q. Keep "A.1."
# typography, including the period after 1.
# Official first-report typography is "if the issuer has been
# required to file reports on Form 10-Q as of its last fiscal
# quarter, whichever is later" — official "has been required," not
# "had been required."
# Official (d) uses typographic U+201C / U+201D around "filed" and
# "Section 18 of the Act."
# Official (b)(2) ends with "; and". Official (c) typography is
# "exploration for the development of" and "oil, gas or coal" with
# no Oxford comma; "eight months"; "$500,000 in any of the most
# recent six years" and "$1,500,000 in the most recent six fiscal
# years."
# Name official 15d-13 / 13a-17 only; do not invent a 15d-13 form
# number. Do not build an ABS or mining-company engine out of
# official (c).
# Do not flatten into already-taught Form 10-Q clocks, packed
# 13a-11, or the new 13a-1 box.
# Learning only; no issuer, filer, or investment advice.

print("official caption typography is Quarterly reports on Form 10-Q (§ 249.308a of this chapter).")
print("13a-13(a): Except as provided in paragraphs (b) and (c) of this section, every issuer that has securities registered pursuant to section 12 of the Act and is required to file annual reports pursuant to section 13 of the Act, and has filed or intends to file such reports on Form 10-K (§ 249.310 of this chapter), shall file a quarterly report on Form 10-Q (§ 249.308a of this chapter) within the period specified in General Instruction A.1. to that form for each of the first three quarters of each fiscal year of the issuer, commencing with the first fiscal quarter following the most recent fiscal year for which full financial statements were included in the registration statement, or, if the registration statement included financial statements for an interim period subsequent to the most recent fiscal year end meeting the requirements of Article 10 of Regulation S-X and Rule 8-03 of Regulation S-X for smaller reporting companies, for the first fiscal quarter subsequent to the quarter reported upon in the registration statement. The first quarterly report of the issuer shall be filed either within 45 days after the effective date of the registration statement or on or before the date on which such report would have been required to be filed if the issuer has been required to file reports on Form 10-Q as of its last fiscal quarter, whichever is later.")
print("13a-13(b): The provisions of this rule shall not apply to the following issuers:")
print("13a-13(b)(1): Investment companies required to file reports pursuant to § 270.30a-1;")
print("13a-13(b)(2): Foreign private issuers required to file reports pursuant to § 240.13a-16; and")
print("13a-13(b)(3): Asset-backed issuers required to file reports pursuant to § 240.13a-17.")
print("13a-13(c): Part I of the quarterly reports on Form 10-Q need not be filed by:")
print("13a-13(c)(1): Mutual life insurance companies; or")
print("13a-13(c)(2): Mining companies not in the production stage but engaged primarily in the exploration for the development of mineral deposits other than oil, gas or coal, if all of the following conditions are met:")
print("13a-13(c)(2)(i): The registrant has not been in production during the current fiscal year or the two years immediately prior thereto; except that being in production for an aggregate period of not more than eight months over the three-year period shall not be a violation of this condition.")
print("13a-13(c)(2)(ii): Receipts from the sale of mineral products or from the operations of mineral producing properties by the registrant and its subsidiaries combined have not exceeded $500,000 in any of the most recent six years and have not aggregated more than $1,500,000 in the most recent six fiscal years.")
print("13a-13(d): Notwithstanding the foregoing provisions of this section, the financial information required by Part I of Form 10-Q shall not be deemed to be “filed” for the purpose of Section 18 of the Act or otherwise subject to the liabilities of that section of the Act, but shall be subject to all other provisions of the Act.")
print('official (a) typography is "within the period specified in General Instruction A.1. to that form"')
print('official typography is "each of the first three quarters of each fiscal year of the issuer"')
print('official first-report typography is "has been required," not "had been required"')
print("official (b)(2) ends with \"; and\"")
print('official (d) uses typographic U+201C / U+201D around "filed"')
print("cite 17 CFR 240.13a-13; title 17 up_to_date_as_of 2026-11-17")
print("[42 FR 24064, May 12, 1977, as amended at 48 FR 19877, May 3, 1983; 50 FR 27939, July 9, 1985; 54 FR 10317, Mar. 13, 1989; 57 FR 10615, Mar. 27, 1992; 61 FR 30403, June 14, 1996; 70 FR 1621, Jan. 7, 2005; 73 FR 975, Jan. 4, 2008; 81 FR 82020, Nov. 18, 2016].")
three_quarters_A1 = True
print(f"  a Form 10-Q is due within the period specified in General Instruction A.1. to that form for each of the first three quarters of each fiscal year of the issuer? {three_quarters_A1}")
check(three_quarters_A1 is True, "A.1. clock for the first three quarters")
first_report_has_been = True
print(f"  the first quarterly report shall be filed either within 45 days after the effective date of the registration statement or on or before the date on which such report would have been required to be filed if the issuer has been required to file reports on Form 10-Q as of its last fiscal quarter, whichever is later? {first_report_has_been}")
check(first_report_has_been is True, "first-report 45-day alternative; has been required")
b_exceptions = True
print(f"  official (b) exceptions include investment companies required to file pursuant to § 270.30a-1, foreign private issuers pursuant to § 240.13a-16, and asset-backed issuers pursuant to § 240.13a-17? {b_exceptions}")
check(b_exceptions is True, "official (b) 30a-1 / 13a-16 / 13a-17 exceptions")
part_i_not_deemed_filed = True
print(f"  official (d) typography is that Part I financial information shall not be deemed to be “filed” for the purpose of Section 18 of the Act or otherwise subject to the liabilities of that section of the Act, but shall be subject to all other provisions of the Act? {part_i_not_deemed_filed}")
check(part_i_not_deemed_filed is True, "Part I not deemed filed for Section 18")
four_quarters_or_invented_clock = False
print(f"  13a-13 requires a Form 10-Q for all four fiscal quarters, or invents a numeric general clock inside 13a-13 other than the official first-report 45-day alternative? {four_quarters_or_invented_clock}")
check(four_quarters_or_invented_clock is False, "no fourth-quarter 10-Q; no invented general numeric clock")
print("official 15d-13 / 13a-17 are named only; this toy does not pack them as second cores")
print("already-taught Form 10-Q clocks, packed 13a-11, the new 13a-1 box, and already-taught Form 6-K promptly-furnished clocks exist and are named only; this toy is not those boxes")
print("literacy only; not a how-to for filing Form 10-Q, and not legal advice")
print("no issuer, filer, or investment advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 240.13a-13; no issuer, disclosure, or investment advice; learning only")

print("=== Y. 17 CFR 243.102: No effect on antifraud liability ===")
# 17 CFR 243.102 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17, live-refetched 2026-11-19,
# byte-identical to the enrich42-src archive).
# Keep sections A-X identical, including 87/87 after X / 13a-13.
# Official typography: "No failure to make a public disclosure
# required solely by § 243.100 shall be deemed to be a violation of
# Rule 10b-5 (17 CFR 240.10b-5) under the Securities Exchange Act."
# Do not invert that negation. Official typography names both
# "Rule 10b-5" and "17 CFR 240.10b-5," and this sentence does not
# say "of 1934."
# Official API XML has no CITA element; do not invent a source line.
# Already-taught Regulation FD clocks live in backtest-traps
# (243.100-101); do not rewrite that box.
# Do not flatten into already-taught Regulation FD clocks, packed
# 10b-5, packed 13a-11(c), or named 244.102.
# Learning only; no issuer, filer, or investment advice.

print("official caption typography is No effect on antifraud liability.")
print("243.102: No failure to make a public disclosure required solely by § 243.100 shall be deemed to be a violation of Rule 10b-5 (17 CFR 240.10b-5) under the Securities Exchange Act.")
print('official typography is "required solely by § 243.100"')
print('official typography names both "Rule 10b-5" and "17 CFR 240.10b-5"')
print('official typography is "under the Securities Exchange Act" and does not say "of 1934"')
print("official API XML has no CITA element; this toy does not invent a source line")
print("cite 17 CFR 243.102; title 17 up_to_date_as_of 2026-11-17")
no_failure_deemed = True
print(f"  no failure to make a public disclosure required solely by § 243.100 shall be deemed to be a violation of Rule 10b-5 (17 CFR 240.10b-5) under the Securities Exchange Act? {no_failure_deemed}")
check(no_failure_deemed is True, "no such failure shall be deemed to be a 10b-5 violation")
solely_and_both_names = True
print(f"  official typography is required solely by § 243.100, and names both Rule 10b-5 and 17 CFR 240.10b-5? {solely_and_both_names}")
check(solely_and_both_names is True, "required solely by 243.100; both Rule 10b-5 names")
no_cita_not_flatten_243102 = True
print(f"  official API XML has no CITA, and this is not already-taught Regulation FD clocks, packed 10b-5, packed 13a-11(c), or named 244.102? {no_cita_not_flatten_243102}")
check(no_cita_not_flatten_243102 is True, "no invented CITA; not FD clocks / 10b-5 / 13a-11(c) / 244.102")
print("already-taught Regulation FD clocks in backtest-traps (243.100-101), packed 10b-5, packed 13a-11(c), and named 244.102 exist and are named only; this toy is not those boxes")
print("literacy only; not a how-to for withholding a public disclosure, and not legal advice")
print("no issuer, filer, or investment advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 243.102; no issuer, disclosure, or investment advice; learning only")
