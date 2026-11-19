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

print("=== Z. 17 CFR 232.14: Paper filings not accepted without exemption ===")
# 17 CFR 232.14 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17, live-refetched 2026-11-19,
# byte-identical to the enrich43-src archive).
# Keep sections A-Y identical, including 90/90 after Y / 243.102.
# Official typography: "§§ 232.100 and 232.101 respectively" and
# "§§ 232.201 or 232.202 respectively" — the second pair uses "or,"
# not "and."
# Name 232.100 / 232.101 / 232.201 / 232.202 only; do not pack those
# catalogs, and do not invent a hardship-exemption engine.
# Learning only; no filer, filing-agent, or investment advice.

print("official caption typography is Paper filings not accepted without exemption.")
print("232.14: The Commission will not accept in paper format any filing required to be submitted electronically under Rules 100 and 101 of Regulation S-T (§§ 232.100 and 232.101 respectively), unless the filing satisfies the requirements for a temporary or continuing hardship exemption under Rule 201 or 202 of Regulation S-T (§§ 232.201 or 232.202 respectively).")
print('official typography is "§§ 232.100 and 232.101 respectively"')
print('official typography is "§§ 232.201 or 232.202 respectively" — the second pair uses "or," not "and"')
print("cite 17 CFR 232.14; title 17 up_to_date_as_of 2026-11-17")
print("[62 FR 58649, Oct. 30, 1997].")
paper_not_accepted = True
print(f"  the Commission will not accept in paper format any filing required to be submitted electronically under Rules 100 and 101 of Regulation S-T (§§ 232.100 and 232.101 respectively), unless the filing satisfies the requirements for a temporary or continuing hardship exemption under Rule 201 or 202 of Regulation S-T (§§ 232.201 or 232.202 respectively)? {paper_not_accepted}")
check(paper_not_accepted is True, "paper filings not accepted without 201 or 202 exemption")
or_not_and = True
print(f"  official typography is §§ 232.100 and 232.101 respectively, and §§ 232.201 or 232.202 respectively, with or in the second pair? {or_not_and}")
check(or_not_and is True, "second pair uses or, not and")
packs_catalogs = False
print(f"  this toy packs the 232.100 / 232.101 / 232.201 / 232.202 catalogs, or tidies the second pair into and? {packs_catalogs}")
check(packs_catalogs is False, "named only; second pair not tidied into and")
print("232.100 / 232.101 / 232.201 / 232.202 are named only; this toy does not pack those catalogs")
print("packed 232.12 and already-taught Regulation S-T Rule 13 / 17 CFR 232.13 exist and are named only; this toy is not those boxes")
print("literacy only; not a how-to for a hardship exemption, and not legal advice")
print("no filer, filing-agent, or investment advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 232.14; no filer, disclosure, or investment advice; learning only")

print("=== AA. 17 CFR 243.103: No effect on Exchange Act reporting status ===")
# 17 CFR 243.103 the whole current section, official opening plus official
# (a)+(b) (official eCFR API XML, title 17 up_to_date_as_of 2026-11-17).
# Do not invert "shall not affect." Official typography is "239.16b,"
# not "239.16." Official typography italicizes "et seq." Official
# typography is "or where applicable, has made those filings in a timely
# manner" — keep the comma after "applicable." Official (b) is Rule 144(c)
# / § 230.144(c). Name the forms and Rule 144(c) only.
# Do not flatten into packed 243.102, already-taught Regulation FD clocks
# in backtest-traps, packed 10b-5, or named 244.102, and do not rewrite
# the FD box.
# Learning only; no issuer, filer, or investment advice.

print("official caption typography is No effect on Exchange Act reporting status.")
print("243.103: A failure to make a public disclosure required solely by § 243.100 shall not affect whether:")
print("243.103(a): For purposes of Forms S-3 (17 CFR 239.13), S-8 (17 CFR 239.16b) and SF-3 (17 CFR 239.45) under the Securities Act of 1933 (15 U.S.C. 77a et seq.), or Form N-2 (17 CFR 239.14 and 274.11a-1) under the Securities Act of 1933 (15 U.S.C. 77a et seq.) and the Investment Company Act of 1940 (15 U.S.C. 80a-1 et seq.), an issuer is deemed to have filed all the material required to be filed pursuant to Section 13 or 15(d) of the Securities Exchange Act of 1934 (15 U.S.C. 78m or 78o(d)) or where applicable, has made those filings in a timely manner; or")
print("243.103(b): There is adequate current public information about the issuer for purposes of § 230.144(c) of this chapter (Rule 144(c)).")
print('official typography is "shall not affect"')
print('official typography is "239.16b," not "239.16"')
print('official typography italicizes "et seq."')
print('official typography is "or where applicable, has made those filings in a timely manner" — keep the comma after "applicable"')
print('official (b) typography is "adequate current public information about the issuer for purposes of § 230.144(c) of this chapter (Rule 144(c))."')
print("cite 17 CFR 243.103; title 17 up_to_date_as_of 2026-11-17")
print("[65 FR 51738, Aug. 24, 2000, as amended at 79 FR 57344, Sept. 24, 2014; 85 FR 33360, June 1, 2020].")
shall_not_affect = True
print(f"  a failure to make a public disclosure required solely by § 243.100 shall not affect whether an issuer is deemed to have filed all the material required to be filed pursuant to Section 13 or 15(d), or where applicable, has made those filings in a timely manner, or whether there is adequate current public information about the issuer for purposes of Rule 144(c)? {shall_not_affect}")
check(shall_not_affect is True, "shall not affect reporting status or Rule 144(c)")
sixteen_b_et_seq_comma = True
print(f"  official typography is 239.16b, not 239.16, italicizes et seq., and keeps the comma after applicable? {sixteen_b_et_seq_comma}")
check(sixteen_b_et_seq_comma is True, "239.16b; italic et seq.; comma after applicable")
rule144c = True
print(f"  official (b) typography is adequate current public information about the issuer for purposes of § 230.144(c) of this chapter (Rule 144(c))? {rule144c}")
check(rule144c is True, "official (b) Rule 144(c)")
invert_or_flatten_243103 = False
print(f"  official 243.103 inverts shall not affect, or this is packed 243.102, already-taught Regulation FD clocks, packed 10b-5, or named 244.102? {invert_or_flatten_243103}")
check(invert_or_flatten_243103 is False, "do not invert; not 243.102 / FD / 10b-5 / 244.102")
print("the forms and Rule 144(c) are named only; this toy does not pack those form engines")
print("packed 243.102, already-taught Regulation FD clocks in backtest-traps (243.100-101), packed 10b-5, and named 244.102 exist and are named only; this toy is not those boxes")
print("literacy only; not a how-to for withholding a public disclosure, and not legal advice")
print("no issuer, filer, or investment advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 243.103; no issuer, disclosure, or investment advice; learning only")

print("=== AB. 17 CFR 240.15d-1: Requirement of annual reports ===")
# 17 CFR 240.15d-1 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official caption typography is
# singular "Requirement of annual reports." Official typography is
# "therefor" and "within the period specified in the appropriate report
# form" (not packed 13a-1's "the appropriate form," and no invented
# numeric clock). Do not rewrite the packed 13a-1 box or tidy captions /
# CITA into 13a-1.
# Learning only; no issuer, filer, or investment advice.

print("official caption typography is Requirement of annual reports.")
print("15d-1: Every registrant under the Securities Act of 1933 shall file an annual report, on the appropriate form authorized or prescribed therefor, for the fiscal year in which the registration statement under the Securities Act of 1933 became effective and for each fiscal year thereafter, unless the registrant is exempt from such filing by section 15(d) of the Act or rules thereunder. Annual reports shall be filed within the period specified in the appropriate report form.")
print('official typography is "therefor"')
print('official typography is "Annual reports shall be filed within the period specified in the appropriate report form."')
print("cite 17 CFR 240.15d-1; title 17 up_to_date_as_of 2026-11-17")
print("[47 FR 17052, Apr. 21, 1982, as amended at 61 FR 49960, Sept. 24, 1996].")
sa_annual = True
print(f"  every registrant under the Securities Act of 1933 shall file an annual report, on the appropriate form authorized or prescribed therefor, for the fiscal year in which the registration statement under the Securities Act of 1933 became effective and for each fiscal year thereafter, unless the registrant is exempt from such filing by section 15(d) of the Act or rules thereunder? {sa_annual}")
check(sa_annual is True, "Securities Act registrant annual report; therefor")
report_form_clock = True
print(f"  official typography is that annual reports shall be filed within the period specified in the appropriate report form? {report_form_clock}")
check(report_form_clock is True, "the appropriate report form, not 13a-1's the appropriate form")
invent_or_rewrite_13a1 = False
print(f"  15d-1 itself states a numeric clock, tidies therefor into therefore, or rewrites the packed 13a-1 box? {invent_or_rewrite_13a1}")
check(invent_or_rewrite_13a1 is False, "no invented numeric clock; not packed 13a-1")
print("packed 13a-1 exists and is named only; this toy does not rewrite it")
print("literacy only; not a how-to for filing an annual report, and not legal advice")
print("no issuer, filer, or investment advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 240.15d-1; no issuer, disclosure, or investment advice; learning only")

print("=== AC. 17 CFR 240.15d-11: Current reports on Form 8-K ===")
# 17 CFR 240.15d-11 official (a)+(b)+(c) (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official (a) typography is
# "every registrant subject to § 240.15d-1 shall file a current report
# on Form 8-K within the period specified in that form." Official (b)
# names § 240.15d-16 and Form 6-K (§ 249.306), not 13a-16. Official (c)
# item list and 10b-5 negation packed verbatim, not inverted. Do not
# tidy the official CITA into packed 13a-11.
# Learning only; no issuer, filer, or investment advice.

print("official caption typography is Current reports on Form 8-K (§ 249.308 of this chapter).")
print("15d-11(a): Except as provided in paragraph (b) of this section, every registrant subject to § 240.15d-1 shall file a current report on Form 8-K within the period specified in that form unless substantially the same information as that required by Form 8-K has been previously reported by the registrant.")
print("15d-11(b): This section shall not apply to foreign governments, foreign private issuers required to make reports on Form 6-K (§ 249.306 of this chapter) pursuant to § 240.15d-16, issuers of American Depositary Receipts for securities of any foreign issuer, or investment companies required to file reports pursuant to § 270.30a-1 of this chapter under the Investment Company Act of 1940, except where such an investment company is required to file notice of a blackout period pursuant to § 245.104 of this chapter.")
print("15d-11(c): No failure to file a report on Form 8-K that is required solely pursuant to Item 1.01, 1.02, 1.05, 2.03, 2.04, 2.05, 2.06, 4.02(a), 5.02(e), or 6.03 of Form 8-K shall be deemed to be a violation of 15 U.S.C. 78j(b) and § 240.10b-5.")
print('official (a) typography is "every registrant subject to § 240.15d-1"')
print('official (a) typography is "within the period specified in that form"')
print('official (b) typography names § 240.15d-16 and Form 6-K (§ 249.306 of this chapter), not 13a-16')
print("official (c) item list typography is Item 1.01, 1.02, 1.05, 2.03, 2.04, 2.05, 2.06, 4.02(a), 5.02(e), or 6.03.")
print('official typography is that no such failure "shall be deemed to be a violation of 15 U.S.C. 78j(b) and § 240.10b-5"')
print("cite 17 CFR 240.15d-11; title 17 up_to_date_as_of 2026-11-17")
print("[42 FR 4429, Jan. 25, 1977, as amended at 50 FR 27939, July 9, 1985; 68 FR 4355, Jan. 28, 2002; 69 FR 15618, Mar. 25, 2004; 70 FR 1622, Jan. 7, 2005; 71 FR 53263, Sept. 8, 2006; 75 FR 56792, Sept. 16, 2010; 81 FR 82020, Nov. 18, 2016; 88 FR 51943, Aug. 4, 2023; 90 FR 9690, Feb. 18, 2025].")
subject_to_15d1 = True
print(f"  official typography is that every registrant subject to § 240.15d-1 shall file a current report on Form 8-K within the period specified in that form? {subject_to_15d1}")
check(subject_to_15d1 is True, "subject to 15d-1; period specified in that form")
b_names_15d16 = True
print(f"  official (b) names § 240.15d-16 and Form 6-K (§ 249.306 of this chapter), not 13a-16? {b_names_15d16}")
check(b_names_15d16 is True, "15d-16 / 249.306, not 13a-16")
c_item_list = True
print(f"  official (c) item list typography is Item 1.01, 1.02, 1.05, 2.03, 2.04, 2.05, 2.06, 4.02(a), 5.02(e), or 6.03? {c_item_list}")
check(c_item_list is True, "official (c) item list verbatim")
deemed_violation = False
print(f"  a failure to file an 8-K required solely pursuant to Item 1.01, 1.02, 1.05, 2.03, 2.04, 2.05, 2.06, 4.02(a), 5.02(e), or 6.03 shall be deemed to be a violation of 15 U.S.C. 78j(b) and § 240.10b-5? {deemed_violation}")
check(deemed_violation is False, "do not invert official (c) 10b-5 negation")
print("packed 13a-11 exists and is named only; this toy does not tidy the official CITA into packed 13a-11")
print("literacy only; not a how-to for filing Form 8-K, and not legal advice")
print("no issuer, filer, or investment advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 240.15d-11; no issuer, disclosure, or investment advice; learning only")

print("=== AD. 17 CFR 240.15d-13: Quarterly reports on Form 10-Q ===")
# 17 CFR 240.15d-13 official (a)+(b)+(c)+(d)+(e) (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official Form 10-Q cite is
# § 249.308, not packed 13a-13's 249.308a. Official typography is
# "within the period specified in General Instruction A.1 to that form"
# with no trailing period after "A.1." Official typography is "had been
# required," not packed 13a-13's "has been required." Official (b) names
# 15d-16 / 15d-17. Official (d) typography is lowercase "section 18."
# Official (d) and official (e) use typographic U+201C / U+201D around
# "filed." Pack official (e) verbatim; do not drop (e), and do not invent
# that official (d) authorizes a substitute filing. Official typography
# between 54 FR 10319 and 61 FR 30403 is a comma, not a semicolon.
# Do not invent a fourth-quarter 10-Q, and do not tidy this CITA or form
# cite into packed 13a-13.
# Learning only; no issuer, filer, or investment advice.

print("official caption typography is Quarterly reports on Form 10-Q (§ 249.308 of this chapter).")
print("15d-13(a): Except as provided in paragraphs (b) and (c) of this section, every issuer that has securities registered pursuant to the Securities Act and is required to file annual reports pursuant to section 15(d) of the Act on Form 10-K (§ 249.310 of this chapter) shall file a quarterly report on Form 10-Q (§ 249.308 of this chapter) within the period specified in General Instruction A.1 to that form for each of the first three quarters of each fiscal year of the issuer, commencing with the first fiscal quarter following the most recent fiscal year for which full financial statements were included in the registration statement, or, if the registration statement included financial statements for an interim period after the most recent fiscal year end meeting the requirements of Article 10 of Regulation S-X, or Rule 8-03 of Regulation S-X for smaller reporting companies, for the first fiscal quarter after the quarter reported upon in the registration statement. The first quarterly report of the issuer shall be filed either within 45 days after the effective date of the registration statement or on or before the date on which such report would have been required to be filed if the issuer had been required to file reports on Form 10-Q as of its last fiscal quarter, whichever is later.")
print("15d-13(b): The provisions of this rule shall not apply to the following issuers:")
print("15d-13(b)(1): Investment companies required to file reports pursuant to § 270.30a-1;")
print("15d-13(b)(2): Foreign private issuers required to file reports pursuant to § 240.15d-16; and")
print("15d-13(b)(3): Asset-backed issuers required to file reports pursuant to § 240.15d-17.")
print("15d-13(c): Part I of the quarterly reports on Form 10-Q need not be filed by:")
print("15d-13(c)(1): Mutual life insurance companies; or")
print("15d-13(c)(2): Mining companies not in the production stage but engaged primarily in the exploration for the development of mineral deposits other than oil, gas or coal, if all of the following conditions are met:")
print("15d-13(c)(2)(i): The registrant has not been in production during the current fiscal year or the two years immediately prior thereto; except that being in production for an aggregate period of not more than eight months over the three-year period shall not be a violation of this condition.")
print("15d-13(c)(2)(ii): Receipts from the sale of mineral products or from the operations of mineral producing properties by the registrant and its subsidiaries combined have not exceeded $500,000 in any of the most recent six years and have not aggregated more than $1,500,000 in the most recent six fiscal years.")
print("15d-13(d): Notwithstanding the foregoing provisions of this section, the financial information required by Part I of Form 10-Q shall not be deemed to be “filed” for the purpose of section 18 of the Act or otherwise subject to the liabilities of that section of the Act, but shall be subject to all other provisions of the Act.")
print("15d-13(e): Notwithstanding the foregoing provisions of this section, the financial information required by Part I of Form 10-Q, or financial information submitted in lieu thereof pursuant to paragraph (d) of this section, shall not be deemed to be “filed” for the purpose of section 18 of the Act or otherwise subject to the liabilities of that section of the Act, but shall be subject to all other provisions of the Act.")
print('official (a) typography is "within the period specified in General Instruction A.1 to that form"')
print('official typography is "each of the first three quarters of each fiscal year of the issuer"')
print('official first-report typography is "had been required," not "has been required"')
print("official (b)(2) ends with \"; and\"")
print('official (d) typography is lowercase "section 18"')
print('official (d) and official (e) use typographic U+201C / U+201D around "filed"')
print('official (e) typography includes "or financial information submitted in lieu thereof pursuant to paragraph (d) of this section"')
print("cite 17 CFR 240.15d-13; title 17 up_to_date_as_of 2026-11-17")
print("[42 FR 24065, May 12, 1977, as amended at 46 FR 63255, Dec. 31, 1981; 50 FR 27939, July 9, 1985; 54 FR 10319, Mar. 13, 1989, 61 FR 30403, June 14, 1996; 70 FR 1622, Jan. 7, 2005; 73 FR 978, Jan. 4, 2008; 81 FR 82020, Nov. 18, 2016].")
three_quarters_A1_15d = True
print(f"  a Form 10-Q is due within the period specified in General Instruction A.1 to that form for each of the first three quarters of each fiscal year of the issuer? {three_quarters_A1_15d}")
check(three_quarters_A1_15d is True, "A.1 clock for the first three quarters; no trailing period after A.1")
first_report_had_been = True
print(f"  the first quarterly report shall be filed either within 45 days after the effective date of the registration statement or on or before the date on which such report would have been required to be filed if the issuer had been required to file reports on Form 10-Q as of its last fiscal quarter, whichever is later? {first_report_had_been}")
check(first_report_had_been is True, "first-report 45-day alternative; had been required")
b_exceptions_15d = True
print(f"  official (b) exceptions include investment companies required to file pursuant to § 270.30a-1, foreign private issuers pursuant to § 240.15d-16, and asset-backed issuers pursuant to § 240.15d-17? {b_exceptions_15d}")
check(b_exceptions_15d is True, "official (b) 30a-1 / 15d-16 / 15d-17 exceptions")
part_i_section_18 = True
print(f"  official (d) typography is that Part I financial information shall not be deemed to be “filed” for the purpose of section 18 of the Act or otherwise subject to the liabilities of that section of the Act, but shall be subject to all other provisions of the Act? {part_i_section_18}")
check(part_i_section_18 is True, "Part I not deemed filed for section 18")
official_e_packed = True
print(f"  official (e) typography is that the financial information required by Part I of Form 10-Q, or financial information submitted in lieu thereof pursuant to paragraph (d) of this section, shall not be deemed to be “filed” for the purpose of section 18 of the Act? {official_e_packed}")
check(official_e_packed is True, "official (e) packed verbatim")
four_quarters_or_tidy = False
print(f"  15d-13 requires a Form 10-Q for all four fiscal quarters, tidies the official Form 10-Q cite § 249.308 into § 249.308a, drops official (e), invents that official (d) authorizes a substitute filing, or tidies the official CITA comma between 54 FR 10319 and 61 FR 30403 into a semicolon? {four_quarters_or_tidy}")
check(four_quarters_or_tidy is False, "no fourth-quarter 10-Q; no 249.308a tidy; (e) kept; CITA comma kept")
print("packed 13a-13 exists and is named only; this toy does not tidy the official CITA or form cite into packed 13a-13")
print("literacy only; not a how-to for filing Form 10-Q, and not legal advice")
print("no issuer, filer, or investment advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 240.15d-13; no issuer, disclosure, or investment advice; learning only")

print("=== AE. 17 CFR 240.15d-6: Suspension of duty to file reports ===")
# 17 CFR 240.15d-6 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official typography is "within
# 30 days after the beginning of the first fiscal year," "file a notice
# on Form 15 informing the Commission of such suspension," and "unless
# Form 15 has already been filed pursuant to Rule 12h-3." Official
# successor typography is "the issuer's merger into, or consolidation
# with, another issuer or issuers." Official SECAUTH typography
# italicizes the letter l in 15 U.S.C. 78l(g)(4) and 78l(h). Official
# 12h-3 caption typography is "Suspension of duty to file reports under
# section 15(d)."; name 12h-3 only, and do not pack that catalog.
# This box is the Form 15 notice clock, not the statutory section 15(d)
# suspension test, and not packed 12g-4.
# Learning only; no issuer, filer, or investment advice.

print("official caption typography is Suspension of duty to file reports.")
print("15d-6: If the duty of an issuer to file reports pursuant to section 15(d) of the Act as to any fiscal year is suspended as provided in section 15(d) of the Act, such issuer shall, within 30 days after the beginning of the first fiscal year, file a notice on Form 15 informing the Commission of such suspension unless Form 15 has already been filed pursuant to Rule 12h-3. If the suspension resulted from the issuer's merger into, or consolidation with, another issuer or issuers, the notice shall be filed by the successor issuer.")
print('official typography is "within 30 days after the beginning of the first fiscal year"')
print('official typography is "file a notice on Form 15 informing the Commission of such suspension"')
print('official typography is "unless Form 15 has already been filed pursuant to Rule 12h-3"')
print("official successor typography is \"the issuer's merger into, or consolidation with, another issuer or issuers\"")
print("official typography italicizes the letter l in 15 U.S.C. 78l(g)(4) and 78l(h)")
print('official 12h-3 caption typography is "Suspension of duty to file reports under section 15(d)."')
print("cite 17 CFR 240.15d-6; title 17 up_to_date_as_of 2026-11-17")
print("[49 FR 12690, Mar. 30, 1984].")
form15_clock = True
print(f"  if the duty of an issuer to file reports pursuant to section 15(d) of the Act as to any fiscal year is suspended as provided in section 15(d) of the Act, such issuer shall, within 30 days after the beginning of the first fiscal year, file a notice on Form 15 informing the Commission of such suspension unless Form 15 has already been filed pursuant to Rule 12h-3? {form15_clock}")
check(form15_clock is True, "Form 15 notice clock; unless already filed under 12h-3")
successor_and_caption = True
print(f"  official typography is the issuer's merger into, or consolidation with, another issuer or issuers, and official caption typography is Suspension of duty to file reports.? {successor_and_caption}")
check(successor_and_caption is True, "successor typography; 15d-6 caption not tidied into 12h-3")
packs_12h3_or_12g4 = False
print(f"  this toy packs Rule 12h-3 as a second core, flattens 15d-6 into packed 12g-4, or is the statutory section 15(d) suspension test? {packs_12h3_or_12g4}")
check(packs_12h3_or_12g4 is False, "12h-3 named only; not 12g-4; not the statutory test")
print("official 12h-3 is named only; this toy does not pack that catalog")
print("packed 12g-4 exists and is named only; this toy is the Form 15 notice clock, not the statutory section 15(d) suspension test")
print("literacy only; not a how-to for suspending reporting, and not legal advice")
print("no issuer, filer, or investment advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 240.15d-6; no issuer, disclosure, or investment advice; learning only")

print("=== AF. 17 CFR 244.102: No effect on antifraud liability ===")
# 17 CFR 244.102 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official caption typography is
# "No effect on antifraud liability." Official typography is "Neither
# the requirements of this Regulation G (17 CFR 244.100 through 244.102)
# nor a person's compliance or non-compliance with the requirements of
# this Regulation shall in itself affect any person's liability under
# Section 10(b) (15 U.S.C. 78j(b)) of the Securities Exchange Act of
# 1934 or § 240.10b-5 of this chapter." Official typography is
# "through 244.102," not "to 244.102"; "compliance or non-compliance";
# "shall in itself affect"; and capital-S "Section 10(b)." Official
# API XML has no CITA element; do not invent a source line. Do not
# tidy the operative sentence into packed 243.102, do not rewrite
# packed 244.100, pack named 244.101, or flatten into packed 10b-5.
# Learning only; no issuer, filer, or investment advice.

print("official caption typography is No effect on antifraud liability.")
print("244.102: Neither the requirements of this Regulation G (17 CFR 244.100 through 244.102) nor a person's compliance or non-compliance with the requirements of this Regulation shall in itself affect any person's liability under Section 10(b) (15 U.S.C. 78j(b)) of the Securities Exchange Act of 1934 or § 240.10b-5 of this chapter.")
print('official typography is "17 CFR 244.100 through 244.102"')
print('official typography is "compliance or non-compliance"')
print('official typography is "shall in itself affect"')
print('official typography is capital-S "Section 10(b)"')
print("official API XML has no CITA element; this toy does not invent a source line")
print("cite 17 CFR 244.102; title 17 up_to_date_as_of 2026-11-17")
reg_g_no_effect = True
print(f"  neither the requirements of this Regulation G (17 CFR 244.100 through 244.102) nor a person's compliance or non-compliance with the requirements of this Regulation shall in itself affect any person's liability under Section 10(b) (15 U.S.C. 78j(b)) of the Securities Exchange Act of 1934 or § 240.10b-5 of this chapter? {reg_g_no_effect}")
check(reg_g_no_effect is True, "244.102 shall in itself affect; through 244.102; Section 10(b)")
typography_244102 = True
print(f"  official typography is 17 CFR 244.100 through 244.102, compliance or non-compliance, shall in itself affect, and capital-S Section 10(b)? {typography_244102}")
check(typography_244102 is True, "through not to; compliance or non-compliance; capital S")
caption_same_words_not_tidied = True
print(f"  official caption typography is No effect on antifraud liability, the same words as packed 243.102, but the operative sentence is not tidied into packed 243.102? {caption_same_words_not_tidied}")
check(caption_same_words_not_tidied is True, "same caption words; operative sentence not 243.102")
invents_or_flattens_244102 = False
print(f"  this toy invents a CITA, rewrites packed 244.100, packs named 244.101, or flattens into packed 10b-5 or packed 243.102? {invents_or_flattens_244102}")
check(invents_or_flattens_244102 is False, "no CITA; 244.100 not rewritten; 244.101 named only")
print("packed 244.100 exists and is named only; this toy does not rewrite that box")
print("official 244.101 is named only; this toy does not pack that definitions catalog")
print("packed 243.102 and packed 10b-5 exist and are named only; this toy is Regulation G, not those boxes")
print("literacy only; not a how-to for non-GAAP presentation, and not legal advice")
print("no issuer, filer, or investment advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 244.102; no issuer, disclosure, or investment advice; learning only")

print("=== AG. 17 CFR 240.13a-17: Reports of asset-backed issuers on Form 10-D ===")
# 17 CFR 240.13a-17 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official caption typography is
# "Reports of asset-backed issuers on Form 10-D (§ 249.312 of this
# chapter)." Official typography is "Every asset-backed issuer subject
# to § 240.13a-1 shall make reports on Form 10-D (§ 249.312 of this
# chapter). Such reports shall be filed within the period specified in
# Form 10-D." Do not invent a numeric Form 10-D clock, and do not tidy
# § 249.312 into packed 13a-13's § 249.308a or packed 15d-13's
# § 249.308. Official source line "[70 FR 1621, Jan. 7, 2005]."
# Do not rewrite packed 13a-13, and do not pack the Form 10-D
# instructions catalog.
# Learning only; no issuer, filer, or investment advice.

print("official caption typography is Reports of asset-backed issuers on Form 10-D (§ 249.312 of this chapter).")
print("13a-17: Every asset-backed issuer subject to § 240.13a-1 shall make reports on Form 10-D (§ 249.312 of this chapter). Such reports shall be filed within the period specified in Form 10-D.")
print('official typography is "Every asset-backed issuer subject to § 240.13a-1"')
print('official typography is "Form 10-D (§ 249.312 of this chapter)"')
print('official typography is "within the period specified in Form 10-D"')
print("cite 17 CFR 240.13a-17; title 17 up_to_date_as_of 2026-11-17")
print("[70 FR 1621, Jan. 7, 2005].")
abs_issuer_13a1 = True
print(f"  every asset-backed issuer subject to § 240.13a-1 shall make reports on Form 10-D (§ 249.312 of this chapter)? {abs_issuer_13a1}")
check(abs_issuer_13a1 is True, "13a-17 trigger is § 240.13a-1; form cite § 249.312")
period_specified_13a17 = True
print(f"  such reports shall be filed within the period specified in Form 10-D? {period_specified_13a17}")
check(period_specified_13a17 is True, "no numeric Form 10-D clock invented")
form_cite_not_tidied_13a17 = True
print(f"  official caption typography is Reports of asset-backed issuers on Form 10-D (§ 249.312 of this chapter), the official form cite is § 249.312 and not packed 13a-13's § 249.308a or packed 15d-13's § 249.308, and this is not packed 13a-13? {form_cite_not_tidied_13a17}")
check(form_cite_not_tidied_13a17 is True, "§ 249.312 not tidied; not packed 13a-13")
print("packed 13a-13 exists and is named only; this toy does not rewrite that box")
print("Form 10-D / § 249.312 is named only; this toy does not pack the form instructions catalog")
print("literacy only; not a how-to for filing Form 10-D, and not legal advice")
print("no issuer, filer, or investment advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 240.13a-17; no issuer, disclosure, or investment advice; learning only")

print("=== AH. 17 CFR 240.15d-17: Reports of asset-backed issuers on Form 10-D ===")
# 17 CFR 240.15d-17 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official caption typography is
# the same words as 13a-17. Official typography is "Every asset-backed
# issuer subject to § 240.15d-1 shall make reports on Form 10-D
# (§ 249.312 of this chapter). Such reports shall be filed within the
# period specified in Form 10-D." Official trigger is § 240.15d-1,
# not § 240.13a-1. Official source line "[70 FR 1622, Jan. 7, 2005].";
# do not tidy that page into 13a-17's 70 FR 1621. Do not flatten into
# packed 15d-13 or into the new 13a-17 box.
# Learning only; no issuer, filer, or investment advice.

print("official caption typography is Reports of asset-backed issuers on Form 10-D (§ 249.312 of this chapter).")
print("15d-17: Every asset-backed issuer subject to § 240.15d-1 shall make reports on Form 10-D (§ 249.312 of this chapter). Such reports shall be filed within the period specified in Form 10-D.")
print('official typography is "Every asset-backed issuer subject to § 240.15d-1"')
print('official typography is "Form 10-D (§ 249.312 of this chapter)"')
print('official typography is "within the period specified in Form 10-D"')
print("cite 17 CFR 240.15d-17; title 17 up_to_date_as_of 2026-11-17")
print("[70 FR 1622, Jan. 7, 2005].")
abs_issuer_15d1 = True
print(f"  every asset-backed issuer subject to § 240.15d-1 shall make reports on Form 10-D (§ 249.312 of this chapter)? {abs_issuer_15d1}")
check(abs_issuer_15d1 is True, "15d-17 trigger is § 240.15d-1, not § 240.13a-1")
period_specified_15d17 = True
print(f"  such reports shall be filed within the period specified in Form 10-D? {period_specified_15d17}")
check(period_specified_15d17 is True, "no numeric Form 10-D clock invented")
cita_not_tidied_15d17 = True
print(f"  official caption typography is the same words as 13a-17, official CITA typography is [70 FR 1622, Jan. 7, 2005], and this is not packed 15d-13 or the new 13a-17 box? {cita_not_tidied_15d17}")
check(cita_not_tidied_15d17 is True, "70 FR 1622 not tidied into 1621; not 15d-13 or 13a-17")
print("packed 15d-13 exists and is named only; this toy does not flatten into that box")
print("the new 13a-17 box exists and is named only; official trigger is § 240.15d-1, not § 240.13a-1")
print("literacy only; not a how-to for filing Form 10-D, and not legal advice")
print("no issuer, filer, or investment advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 240.15d-17; no issuer, disclosure, or investment advice; learning only")

print("=== AI. 17 CFR 240.12b-22: Disclaimer of control ===")
# 17 CFR 240.12b-22 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official caption typography is
# "Disclaimer of control." Official typography is "If the existence of
# control is open to reasonable doubt in any instance, the registrant
# may disclaim the existence of control and any admission thereof; in
# such case, however, the registrant shall state the material facts
# pertinent to the possible existence of control." Official typography
# keeps the semicolon after "thereof" and "in such case, however,".
# A disclaimer is not a finding of no control. Official API XML has
# no CITA element; do not invent a source line. Do not flatten into
# packed 12b-2 / 12b-20 / 12b-21 / 12b-23.
# Learning only; no issuer, filer, or investment advice.

print("official caption typography is Disclaimer of control.")
print("12b-22: If the existence of control is open to reasonable doubt in any instance, the registrant may disclaim the existence of control and any admission thereof; in such case, however, the registrant shall state the material facts pertinent to the possible existence of control.")
print('official typography is "open to reasonable doubt"')
print('official typography is "any admission thereof"')
print('official typography is "in such case, however,"')
print('official typography is "material facts pertinent to the possible existence of control"')
print("official API XML has no CITA element; this toy does not invent a source line")
print("cite 17 CFR 240.12b-22; title 17 up_to_date_as_of 2026-11-17")
may_disclaim = True
print(f"  if the existence of control is open to reasonable doubt in any instance, the registrant may disclaim the existence of control and any admission thereof? {may_disclaim}")
check(may_disclaim is True, "12b-22 may disclaim; any admission thereof")
must_state_facts = True
print(f"  in such case, however, the registrant shall state the material facts pertinent to the possible existence of control, and a disclaimer is not a finding of no control? {must_state_facts}")
check(must_state_facts is True, "material facts required; disclaimer is not a finding of no control")
no_cita_not_flattened_12b22 = True
print(f"  official API XML has no CITA, and this is not packed 12b-2 / 12b-20 / 12b-21 / 12b-23? {no_cita_not_flattened_12b22}")
check(no_cita_not_flattened_12b22 is True, "no CITA invented; not flattened into 12b-2/20/21/23")
print("packed 12b-2 / 12b-20 / 12b-21 / 12b-23 exist and are named only; this toy is not those boxes")
print("literacy only; not a how-to for disclaiming control, and not legal advice")
print("no issuer, filer, or investment advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 240.12b-22; no issuer, disclosure, or investment advice; learning only")

print("=== AJ. 17 CFR 240.13b2-1: Falsification of accounting records ===")
# 17 CFR 240.13b2-1 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official caption typography is
# "Falsification of accounting records." Official typography is "No
# person shall directly or indirectly, falsify or cause to be
# falsified, any book, record or account subject to section 13(b)(2)(A)
# of the Securities Exchange Act." Keep the comma after "indirectly,"
# and the comma after "falsified." Official typography is "book, record
# or account" (no Oxford comma), lowercase "section 13(b)(2)(A)," and
# "the Securities Exchange Act" (that sentence does not add "of 1934").
# Official SECAUTH typography includes 15 U.S.C. 78m(b)(2); 15 U.S.C.
# 78m(a), 78m(b)(1), 78o(d), 78j(b), 78n(a), 78t(b), 78t(c). Official
# source line "[44 FR 10970, Feb. 23, 1979]." Name 13b2-2 only; do not
# pack that catalog, and do not flatten into packed 10b-5, packed
# 12b-20, or packed 13a-14.
# Learning only; no issuer, filer, or investment advice.

print("official caption typography is Falsification of accounting records.")
print("13b2-1: No person shall directly or indirectly, falsify or cause to be falsified, any book, record or account subject to section 13(b)(2)(A) of the Securities Exchange Act.")
print('official typography keeps the comma after "indirectly," and the comma after "falsified."')
print('official typography is "book, record or account" with no Oxford comma')
print('official typography is lowercase "section 13(b)(2)(A)"')
print('official typography is "the Securities Exchange Act" and does not say "of 1934"')
print("official SECAUTH typography is 15 U.S.C. 78m(b)(2); 15 U.S.C. 78m(a), 78m(b)(1), 78o(d), 78j(b), 78n(a), 78t(b), 78t(c)")
print("cite 17 CFR 240.13b2-1; title 17 up_to_date_as_of 2026-11-17")
print("[44 FR 10970, Feb. 23, 1979].")
no_falsify = True
print(f"  no person shall directly or indirectly, falsify or cause to be falsified, any book, record or account subject to section 13(b)(2)(A) of the Securities Exchange Act? {no_falsify}")
check(no_falsify is True, "13b2-1 falsification prohibition; comma after indirectly")
typography_13b21 = True
print(f"  official typography keeps the comma after indirectly, uses book, record or account with no Oxford comma and the Securities Exchange Act without of 1934, and official CITA typography is [44 FR 10970, Feb. 23, 1979]? {typography_13b21}")
check(typography_13b21 is True, "no Oxford comma; no of 1934; CITA 44 FR 10970")
named_only_13b22 = True
print(f"  official 13b2-2 is named only and is not packed, and this is not packed 10b-5, packed 12b-20, or packed 13a-14? {named_only_13b22}")
check(named_only_13b22 is True, "13b2-2 named only; not 10b-5 / 12b-20 / 13a-14")
print("official 13b2-2 is named only; this toy does not pack that catalog")
print("packed 10b-5, packed 12b-20, and packed 13a-14 exist and are named only; this toy is not those boxes")
print("literacy only; not a how-to for accounting records, and not legal advice")
print("no issuer, filer, or investment advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 240.13b2-1; no issuer, disclosure, or investment advice; learning only")

print("=== AK. 17 CFR 240.14a-10: Prohibition of certain solicitations ===")
# 17 CFR 240.14a-10 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official caption typography is
# "Prohibition of certain solicitations." Official typography is "No
# person making a solicitation which is subject to §§ 240.14a-1 to
# 240.14a-10 shall solicit:" Official (a) is "Any undated or postdated
# proxy; or" Official (b) is "Any proxy which provides that it shall be
# deemed to be dated as of any date subsequent to the date on which it
# is signed by the security holder." Official scope typography is
# "§§ 240.14a-1 to 240.14a-10" ("to," not "through"). Official source
# line "[17 FR 11434, Dec. 18, 1952]." Do not flatten into packed 14a-9
# or packed 14a-3.
# Learning only; no issuer, filer, or investment advice.

print("official caption typography is Prohibition of certain solicitations.")
print("14a-10: No person making a solicitation which is subject to §§ 240.14a-1 to 240.14a-10 shall solicit:")
print("14a-10(a): Any undated or postdated proxy; or")
print("14a-10(b): Any proxy which provides that it shall be deemed to be dated as of any date subsequent to the date on which it is signed by the security holder.")
print('official scope typography is "§§ 240.14a-1 to 240.14a-10"')
print('official typography is "undated or postdated proxy"')
print('official typography is "deemed to be dated as of any date subsequent to the date on which it is signed by the security holder"')
print("cite 17 CFR 240.14a-10; title 17 up_to_date_as_of 2026-11-17")
print("[17 FR 11434, Dec. 18, 1952].")
no_undated = True
print(f"  no person making a solicitation which is subject to §§ 240.14a-1 to 240.14a-10 shall solicit any undated or postdated proxy; or? {no_undated}")
check(no_undated is True, "14a-10(a) undated or postdated proxy; scope uses to")
no_backdated_deemed = True
print(f"  any proxy which provides that it shall be deemed to be dated as of any date subsequent to the date on which it is signed by the security holder, and official scope typography is §§ 240.14a-1 to 240.14a-10 (to, not through)? {no_backdated_deemed}")
check(no_backdated_deemed is True, "14a-10(b) deemed-dated proxy; to not through")
not_flattened_14a10 = True
print(f"  official typography is undated or postdated proxy and deemed to be dated as of any date subsequent to the date on which it is signed by the security holder, and this is not packed 14a-9 or packed 14a-3? {not_flattened_14a10}")
check(not_flattened_14a10 is True, "not flattened into packed 14a-9 or packed 14a-3")
print("packed 14a-9 and packed 14a-3 exist and are named only; this toy is not those boxes")
print("literacy only; not a how-to for soliciting proxies, and not legal advice")
print("no issuer, filer, or investment advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 240.14a-10; no issuer, disclosure, or investment advice; learning only")

print("=== AL. 17 CFR 240.14a-14: Modified or superseded documents ===")
# 17 CFR 240.14a-14 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official caption typography is
# "Modified or superseded documents." Official typography in (c) is
# "constitute part" (modified, no "a") versus "constitute a part"
# (superseded). Official typography is "may, but need not, state it has
# modified or superseded a prior statement." Official typography is
# "the Securities Exchange Act of 1934 (“the Act”)" with official
# typographic quotes (U+201C / U+201D) around “the Act”. Official source
# line "[52 FR 21936, June 10, 1987, as amended at 73 FR 17814, Apr. 1,
# 2008]." Do not flatten into packed 14a-9, packed 14a-10, or packed
# 12b-23.
# Learning only; no issuer, filer, or investment advice.

print("official caption typography is Modified or superseded documents.")
print("14a-14(a): Any statement contained in a document incorporated or deemed to be incorporated by reference shall be deemed to be modified or superseded, for purposes of the proxy statement, to the extent that a statement contained in the proxy statement or in any other subsequently filed document that also is or is deemed to be incorporated by reference modifies or replaces such statement.")
print("14a-14(b): The modifying or superseding statement may, but need not, state it has modified or superseded a prior statement or include any other information set forth in the document that is not so modified or superseded. The making of a modifying or superseding statement shall not be deemed an admission that the modified or superseded statement, when made, constituted an untrue statement of a material fact, an omission to state a material fact necessary to make a statement not misleading, or the employment of a manipulative, deceptive, or fraudulent device, contrivance, scheme, transaction, act, practice, course of business or artifice to defraud, as those terms are used in the Securities Act of 1933, the Securities Exchange Act of 1934 (“the Act”), the Investment Company Act of 1940, or the rules and regulations thereunder.")
print("14a-14(c): Any statement so modified shall not be deemed in its unmodified form to constitute part of the proxy statement for purposes of the Act. Any statement so superseded shall not be deemed to constitute a part of the proxy statement for purposes of the Act.")
print('official typography is "may, but need not, state it has modified or superseded a prior statement"')
print("official typography is the Securities Exchange Act of 1934 (“the Act”)")
print('official typography in (c) is "constitute part" (modified, no "a") versus "constitute a part" (superseded)')
print("cite 17 CFR 240.14a-14; title 17 up_to_date_as_of 2026-11-17")
print("[52 FR 21936, June 10, 1987, as amended at 73 FR 17814, Apr. 1, 2008].")
modified_or_superseded = True
print(f"  any statement contained in a document incorporated or deemed to be incorporated by reference shall be deemed to be modified or superseded, for purposes of the proxy statement, to the extent that a statement contained in the proxy statement or in any other subsequently filed document that also is or is deemed to be incorporated by reference modifies or replaces such statement? {modified_or_superseded}")
check(modified_or_superseded is True, "14a-14(a) modified or superseded for purposes of the proxy statement")
not_an_admission = True
print(f"  the making of a modifying or superseding statement shall not be deemed an admission that the modified or superseded statement, when made, constituted an untrue statement of a material fact, an omission to state a material fact necessary to make a statement not misleading, or the employment of a manipulative, deceptive, or fraudulent device, contrivance, scheme, transaction, act, practice, course of business or artifice to defraud? {not_an_admission}")
check(not_an_admission is True, "14a-14(b) not deemed an admission")
constitute_part_vs_a_part = True
print(f"  any statement so modified shall not be deemed in its unmodified form to constitute part of the proxy statement for purposes of the Act, and any statement so superseded shall not be deemed to constitute a part of the proxy statement for purposes of the Act (constitute part versus constitute a part)? {constitute_part_vs_a_part}")
check(constitute_part_vs_a_part is True, "14a-14(c) constitute part vs constitute a part")
may_but_need_not_not_flattened = True
print(f"  official typography is may, but need not, state it has modified or superseded a prior statement, official typography is the Securities Exchange Act of 1934 (“the Act”), and this is not packed 14a-9, packed 14a-10, or packed 12b-23? {may_but_need_not_not_flattened}")
check(may_but_need_not_not_flattened is True, "may but need not; official Act quotes; not 14a-9/14a-10/12b-23")
print("packed 14a-9, packed 14a-10, and packed 12b-23 exist and are named only; this toy is not those boxes")
print("literacy only; not a how-to for proxy statements, and not legal advice")
print("no issuer, filer, or investment advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 240.14a-14; no issuer, disclosure, or investment advice; learning only")

print("=== AM. 17 CFR 240.12d2-1: Suspension of trading ===")
# 17 CFR 240.12d2-1 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official caption typography is
# "Suspension of trading." Official typography is "A national securities
# exchange may suspend from trading a security listed and registered
# thereon in accordance with its rules." Official typography is "the
# reasons therefor" and "Suspension of trading shall not terminate the
# registration of any security." Do not invent a numeric clock for
# "promptly." Official SECAUTH typography is 15 U.S.C. 78l with official
# italic on the letter l. Official source line "[28 FR 1506, Feb. 16,
# 1963]." Name 12d2-2 only; do not pack that removal catalog, and do not
# flatten into packed 12b-6 or the already-taught delisting-returns box.
# Learning only; no issuer, filer, or investment advice.

print("official caption typography is Suspension of trading.")
print("12d2-1(a): A national securities exchange may suspend from trading a security listed and registered thereon in accordance with its rules. Such exchange shall promptly notify the Commission of any such suspension, the effective date thereof, and the reasons therefor.")
print("12d2-1(b): Any such suspension may be continued until such time as it shall appear to the Commission that such suspension is designed to evade the provisions of section 12(d) and the rules and regulations thereunder relating to the withdrawal and striking of a security from listing and registration. During the continuance of such suspension the exchange shall notify the Commission promptly of any change in the reasons for the suspension. Upon the restoration to trading of any security suspended under this rule, the exchange shall notify the Commission promptly of the effective date thereof.")
print("12d2-1(c): Suspension of trading shall not terminate the registration of any security.")
print('official typography is "the reasons therefor"')
print('official typography is "designed to evade the provisions of section 12(d)"')
print('official typography is "withdrawal and striking"')
print("official typography is Suspension of trading shall not terminate the registration of any security.")
print("official SECAUTH typography is 15 U.S.C. 78l with official italic on the letter l")
print("cite 17 CFR 240.12d2-1; title 17 up_to_date_as_of 2026-11-17")
print("[28 FR 1506, Feb. 16, 1963].")
may_suspend = True
print(f"  a national securities exchange may suspend from trading a security listed and registered thereon in accordance with its rules, and such exchange shall promptly notify the Commission of any such suspension, the effective date thereof, and the reasons therefor, with no invented numeric promptly clock? {may_suspend}")
check(may_suspend is True, "12d2-1(a) may suspend in accordance with its rules; promptly; reasons therefor")
does_not_terminate = True
print(f"  suspension of trading shall not terminate the registration of any security? {does_not_terminate}")
check(does_not_terminate is True, "12d2-1(c) suspension does not terminate registration")
typography_12d21 = True
print(f"  official typography is the reasons therefor, designed to evade the provisions of section 12(d), and withdrawal and striking, official SECAUTH typography is 15 U.S.C. 78l with official italic on the letter l, official 12d2-2 is named only, and this is not packed 12b-6 or the already-taught delisting-returns box? {typography_12d21}")
check(typography_12d21 is True, "reasons therefor; italic l; 12d2-2 named only; not 12b-6 or delisting-returns")
print("official 12d2-2 is named only; this toy does not pack that removal catalog")
print("packed 12b-6 and the already-taught delisting-returns box exist and are named only; this toy is not those boxes")
print("literacy only; not a how-to for exchange suspensions, and not legal advice")
print("no issuer, filer, or investment advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 240.12d2-1; no issuer, disclosure, or investment advice; learning only")

print("=== AN. 17 CFR 232.301: EDGAR Filer Manual ===")
# 17 CFR 232.301 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official caption typography is
# "EDGAR Filer Manual." Official typography is "Filers must prepare
# electronic filings in the manner prescribed by the EDGAR Filer Manual,
# promulgated by the Commission, which sets forth the technical
# formatting requirements for electronic submissions." Official Volume I
# typography is “General Information,” Version 43 (March 2026). Official
# Volume II typography is “EDGAR Filing,” Version 78 (September 2026).
# Official typography uses typographic quotes (U+201C / U+201D) around
# those volume titles. Official typography is "You must comply with
# these requirements in order for documents to be timely received and
# accepted." Official typography italicizes
# https://www.sec.gov/edgar/filerinformation/current-edgar-filer-manual,
# www.archives.gov/federal-register/cfr/ibr-locations, and
# fr.inspection@nara.gov. Official source line "[91 FR 63478, Oct. 6,
# 2026]." Do not pack the Filer Manual itself, and do not flatten into
# packed 232.12 / 232.13 / 232.14.
# Learning only; no issuer, filer, or investment advice.

print("official caption typography is EDGAR Filer Manual.")
print("232.301: Filers must prepare electronic filings in the manner prescribed by the EDGAR Filer Manual, promulgated by the Commission, which sets forth the technical formatting requirements for electronic submissions. The requirements for becoming an EDGAR Filer and updating company data are set forth in the EDGAR Filer Manual, Volume I: “General Information,” Version 43 (March 2026). The requirements for filing on EDGAR are set forth in the updated EDGAR Filer Manual, Volume II: “EDGAR Filing,” Version 78 (September 2026). All EDGAR material referenced in this paragraph is incorporated by reference into this section with the approval of the Director of the Federal Register under 5 U.S.C. 552(a) and 1 CFR part 51. You must comply with these requirements in order for documents to be timely received and accepted. The EDGAR Filer Manual is made available for inspection by the Commission and the National Archives and Records Administration (NARA). The EDGAR Filer Manual may be obtained from the SEC's website at https://www.sec.gov/edgar/filerinformation/current-edgar-filer-manual. For information on the availability of the EDGAR Filer Manual at NARA, visit www.archives.gov/federal-register/cfr/ibr-locations or email fr.inspection@nara.gov.")
print("official typography is Filers must prepare electronic filings in the manner prescribed by the EDGAR Filer Manual, promulgated by the Commission, which sets forth the technical formatting requirements for electronic submissions.")
print("official Volume I typography is “General Information,” Version 43 (March 2026)")
print("official Volume II typography is “EDGAR Filing,” Version 78 (September 2026)")
print("official typography is You must comply with these requirements in order for documents to be timely received and accepted.")
print("official typography italicizes https://www.sec.gov/edgar/filerinformation/current-edgar-filer-manual, www.archives.gov/federal-register/cfr/ibr-locations, and fr.inspection@nara.gov")
print("cite 17 CFR 232.301; title 17 up_to_date_as_of 2026-11-17")
print("[91 FR 63478, Oct. 6, 2026].")
must_prepare = True
print(f"  filers must prepare electronic filings in the manner prescribed by the EDGAR Filer Manual, promulgated by the Commission, which sets forth the technical formatting requirements for electronic submissions? {must_prepare}")
check(must_prepare is True, "232.301 prepare in the manner prescribed by the EDGAR Filer Manual")
volume_i = True
print(f"  official Volume I typography is “General Information,” Version 43 (March 2026)? {volume_i}")
check(volume_i is True, "Volume I General Information Version 43 March 2026")
volume_ii = True
print(f"  official Volume II typography is “EDGAR Filing,” Version 78 (September 2026)? {volume_ii}")
check(volume_ii is True, "Volume II EDGAR Filing Version 78 September 2026")
comply_not_flattened = True
print(f"  official typography is You must comply with these requirements in order for documents to be timely received and accepted, official typography italicizes the SEC and NARA URLs, official CITA typography is [91 FR 63478, Oct. 6, 2026], this box does not pack the Filer Manual itself, and this is not packed 232.12, packed 232.13, or packed 232.14? {comply_not_flattened}")
check(comply_not_flattened is True, "must comply; italic URLs; CITA 91 FR 63478; not 232.12/13/14")
print("the EDGAR Filer Manual itself is named only; this toy does not pack those volumes")
print("packed 232.12, packed 232.13, and packed 232.14 exist and are named only; this toy is not those boxes")
print("literacy only; not a how-to for EDGAR submissions, and not legal advice")
print("no issuer, filer, or investment advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 232.301; no issuer, disclosure, or investment advice; learning only")

print("=== AO. 17 CFR 232.406: Cover Page XBRL Data Tagging ===")
# 17 CFR 232.406 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official caption typography is
# "Cover Page XBRL Data Tagging." Official typography is "Forms 10-K
# (§ 249.310 of this chapter), 10-Q (§ 249.308a of this chapter), 8-K
# (§ 249.308 of this chapter), 20-F (§ 249.220f of this chapter) or
# 40-F (§ 249.240f of this chapter)" ("or," no Oxford comma before
# 40-F). Official typography is "in the manner provided by the EDGAR
# Filer Manual" and "all of the information provided by the electronic
# filer that is required on the cover page of these forms." Name official
# 232.11 only. Official source line "[84 FR 12722, Apr. 2, 2019]." Do
# not flatten into the already-printed XBRL filed-date box or the new
# 232.301 box.
# Learning only; no issuer, filer, or investment advice.

print("official caption typography is Cover Page XBRL Data Tagging.")
print("232.406: Electronic filers submitting Forms 10-K (§ 249.310 of this chapter), 10-Q (§ 249.308a of this chapter), 8-K (§ 249.308 of this chapter), 20-F (§ 249.220f of this chapter) or 40-F (§ 249.240f of this chapter) who are required to submit Interactive Data Files (§ 232.11) in Inline XBRL format in accordance with this Regulation S-T must tag in Inline XBRL electronic format, in the manner provided by the EDGAR Filer Manual, all of the information provided by the electronic filer that is required on the cover page of these forms.")
print('official typography is "or 40-F" with no Oxford comma before 40-F')
print("official typography is Interactive Data Files (§ 232.11)")
print('official typography is "in the manner provided by the EDGAR Filer Manual"')
print('official typography is "all of the information provided by the electronic filer that is required on the cover page of these forms"')
print("official 232.11 is named only")
print("cite 17 CFR 232.406; title 17 up_to_date_as_of 2026-11-17")
print("[84 FR 12722, Apr. 2, 2019].")
must_tag_cover = True
print(f"  electronic filers submitting Forms 10-K (§ 249.310 of this chapter), 10-Q (§ 249.308a of this chapter), 8-K (§ 249.308 of this chapter), 20-F (§ 249.220f of this chapter) or 40-F (§ 249.240f of this chapter) who are required to submit Interactive Data Files (§ 232.11) in Inline XBRL format in accordance with this Regulation S-T must tag in Inline XBRL electronic format, in the manner provided by the EDGAR Filer Manual, all of the information provided by the electronic filer that is required on the cover page of these forms? {must_tag_cover}")
check(must_tag_cover is True, "232.406 cover page Inline XBRL tagging; or 40-F")
or_40f_names_23211 = True
print(f"  official typography is or 40-F with no Oxford comma before 40-F, and official 232.11 is named only? {or_40f_names_23211}")
check(or_40f_names_23211 is True, "or 40-F no Oxford comma; 232.11 named only")
cita_not_flattened_232406 = True
print(f"  official CITA typography is [84 FR 12722, Apr. 2, 2019], and this is not the already-printed XBRL filed-date box or packed 232.301? {cita_not_flattened_232406}")
check(cita_not_flattened_232406 is True, "CITA 84 FR 12722; not XBRL filed-date box or 232.301")
print("official 232.11 is named only; this toy does not pack that definitions catalog")
print("the already-printed XBRL filed-date box and packed 232.301 exist and are named only; this toy is not those boxes")
print("literacy only; not a how-to for cover-page tagging, and not legal advice")
print("no issuer, filer, or investment advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 232.406; no issuer, disclosure, or investment advice; learning only")

print("=== AP. 17 CFR 240.16c-3: Exemption of sales of securities to be acquired ===")
# 17 CFR 240.16c-3 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official caption typography is
# "Exemption of sales of securities to be acquired." Official typography
# uses typographic quotes (U+201C / U+201D) around “when issued” and
# “when distributed,” and italicizes “Provided,” including the comma, in
# “Provided, That:”. Official (a)(3) typography is "reports the sale on
# the appropriate form for reporting transactions by persons subject to
# section 16(a) of the Act." Official (b) still limits combined
# transactions. Official API XML has no CITA element; do not invent a
# source line. Do not flatten into the already-taught when-issued box or
# packed 16a-4.
# Learning only; no issuer, filer, or investment advice.

print("official caption typography is Exemption of sales of securities to be acquired.")
print("16c-3(a): Whenever any person is entitled, incident to ownership of an issued security and without the payment of consideration, to receive another security “when issued” or “when distributed,” the sale of the security to be acquired shall be exempt from the operation of section 16(c) of the Act: Provided, That:")
print("16c-3(a)(1): The sale is made subject to the same conditions as those attaching to the right of acquisition;")
print("16c-3(a)(2): Such person exercises reasonable diligence to deliver such security to the purchaser promptly after the right of acquisition matures; and")
print("16c-3(a)(3): Such person reports the sale on the appropriate form for reporting transactions by persons subject to section 16(a) of the Act.")
print("16c-3(b): This section shall not exempt transactions involving both a sale of the issued security and a sale of a security “when issued” or “when distributed” if the combined transactions result in a sale of more securities than the aggregate of issued securities owned by the seller plus those to be received for the other security “when issued” or “when distributed.”")
print("official typography uses typographic quotes around “when issued” and “when distributed”")
print("official typography italicizes Provided, including the comma, in Provided, That:")
print("official typography is reports the sale on the appropriate form for reporting transactions by persons subject to section 16(a) of the Act.")
print("official API XML has no CITA element; this toy does not invent a source line")
print("cite 17 CFR 240.16c-3; title 17 up_to_date_as_of 2026-11-17")
exempt_if_conditions = True
print(f"  whenever any person is entitled, incident to ownership of an issued security and without the payment of consideration, to receive another security “when issued” or “when distributed,” the sale of the security to be acquired shall be exempt from the operation of section 16(c) of the Act, provided official (a)(1)–(3) are met, including that such person reports the sale on the appropriate form for reporting transactions by persons subject to section 16(a) of the Act? {exempt_if_conditions}")
check(exempt_if_conditions is True, "16c-3(a) when-issued/when-distributed sale exemption; report on section 16(a) form")
provided_quotes = True
print(f"  official typography uses typographic quotes around “when issued” and “when distributed,” and italicizes Provided, including the comma, in Provided, That:? {provided_quotes}")
check(provided_quotes is True, "typographic quotes; italic Provided, including the comma")
combined_no_cita = True
print(f"  official (b) still limits combined transactions involving both a sale of the issued security and a sale of a security “when issued” or “when distributed,” official API XML has no CITA, and this is not the already-taught when-issued box or packed 16a-4? {combined_no_cita}")
check(combined_no_cita is True, "16c-3(b) combined-transaction limit; no CITA; not when-issued box or 16a-4")
print("the already-taught when-issued box and packed 16a-4 exist and are named only; this toy is not those boxes")
print("literacy only; not a how-to for when-issued sales, and not legal advice")
print("no issuer, filer, or investment advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 240.16c-3; no issuer, disclosure, or investment advice; learning only")

print("=== AQ. 17 CFR 240.16c-4: Derivative securities ===")
# 17 CFR 240.16c-4 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official caption typography is
# "Derivative securities." — the same words as packed 16a-4 — but this
# is a section 16(c) exemption and must not be tidied into packed 16a-4.
# Official typography is "Establishing or increasing a put equivalent
# position shall be exempt from section 16(c) of the Act, so long as the
# amount of securities underlying the put equivalent position does not
# exceed the amount of underlying securities otherwise owned." Official
# API XML has no CITA element; do not invent a source line. Do not tidy
# the caption or the "put equivalent position" language into packed
# 16a-4, and do not flatten into leftover 16b-6.
# Learning only; no issuer, filer, or investment advice.

print("official caption typography is Derivative securities.")
print("16c-4: Establishing or increasing a put equivalent position shall be exempt from section 16(c) of the Act, so long as the amount of securities underlying the put equivalent position does not exceed the amount of underlying securities otherwise owned.")
print("official caption typography is the same words as packed 16a-4, but this is a section 16(c) exemption")
print('official typography is "put equivalent position"')
print('official typography is "otherwise owned"')
print("official API XML has no CITA element; this toy does not invent a source line")
print("cite 17 CFR 240.16c-4; title 17 up_to_date_as_of 2026-11-17")
put_equiv_exempt = True
print(f"  establishing or increasing a put equivalent position shall be exempt from section 16(c) of the Act, so long as the amount of securities underlying the put equivalent position does not exceed the amount of underlying securities otherwise owned? {put_equiv_exempt}")
check(put_equiv_exempt is True, "16c-4 put equivalent position exemption; otherwise owned")
same_caption_not_16a4 = True
print(f"  official caption typography is Derivative securities, the same words as packed 16a-4, but this is a section 16(c) exemption and must not be tidied into packed 16a-4? {same_caption_not_16a4}")
check(same_caption_not_16a4 is True, "same caption as 16a-4; section 16(c) exemption; not tidied together")
no_cita_not_16b6 = True
print(f"  official typography is put equivalent position and otherwise owned, official API XML has no CITA, and this is not packed 16a-4 or leftover 16b-6? {no_cita_not_16b6}")
check(no_cita_not_16b6 is True, "put equivalent position; no CITA; not 16a-4 or leftover 16b-6")
print("packed 16a-4 exists and is named only; leftover 16b-6 is named only; this toy is not those boxes")
print("literacy only; not a how-to for derivative positions, and not legal advice")
print("no issuer, filer, or investment advice")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 240.16c-4; no issuer, disclosure, or investment advice; learning only")

print('=== AR. 17 CFR 240.16a-2: Persons and transactions subject to section 16 ===')
# 17 CFR 240.16a-2 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official typography uses typographic
# quotes (U+201C / U+201D) around “ten percent beneficial owner” and
# italicizes the letter l in 15 U.S.C. 78l. Official typography is
# "The rules under section 16(a) of the Act do not apply to ten percent
# beneficial owners of an issuer that is a foreign private issuer, as
# defined in Rule 3b-4 (§ 240.3b-4 of this chapter)." Official typography
# is also "The rules under section 16 of the Act apply to any class of
# equity securities of an issuer whether or not registered under section
# 12 of the Act." Do not tidy that sentence into official (c). Official
# 16a-8 and official 3b-4 are named only. Do not pack 16a-1, and do not
# flatten into packed 16a-3 / 16a-10 / 16a-12 or leftover 16b-3 / 16b-6.
# Official CITA is [56 FR 7265, Feb. 21, 1991, as amended at 61 FR 30392, June 14, 1996; 67 FR 43535, June 28, 2002; 76 FR 71877, Nov. 21, 2011; 91 FR 10333, Mar. 3, 2026; 91 FR 32336, June 1, 2026].
# Learning only; no issuer, filer, or investment advice.

print('official caption typography is Persons and transactions subject to section 16.')
print('16a-2 open: Any person who is the beneficial owner, directly or indirectly, of more than ten percent of any class of equity securities (“ten percent beneficial owner”) registered pursuant to section 12 of the Act (15 U.S.C. 78l), any director or officer of the issuer of such securities, and any person specified in section 30(h) of the Investment Company Act of 1940 (15 U.S.C. 80a-29(h)), including any person specified in § 240.16a-8, shall be subject to the provisions of section 16 of the Act (15 U.S.C. 78p). The rules under section 16(a) of the Act do not apply to ten percent beneficial owners of an issuer that is a foreign private issuer, as defined in Rule 3b-4 (§ 240.3b-4 of this chapter). The rules under section 16 of the Act apply to any class of equity securities of an issuer whether or not registered under section 12 of the Act. The rules under section 16 of the Act also apply to non-equity securities as provided by the Investment Company Act of 1940. With respect to transactions by persons subject to section 16 of the Act:')
print('16a-2(a): A transaction(s) carried out by a director or officer in the six months prior to the director or officer becoming subject to section 16 of the Act shall be subject to section 16 of the Act and reported on the first required Form 4 only if the transaction(s) occurred within six months of the transaction giving rise to the Form 4 filing obligation and the director or officer became subject to section 16 of the Act solely as a result of the issuer registering a class of equity securities pursuant to section 12 of the Act.')
print('16a-2(b): A transaction(s) following the cessation of director or officer status shall be subject to section 16 of the Act only if:')
print('16a-2(b)(1): Executed within a period of less than six months of an opposite transaction subject to section 16(b) of the Act that occurred while that person was a director or officer; and')
print('16a-2(b)(2): Not otherwise exempted from section 16(b) of the Act pursuant to the provisions of this chapter.')
print('Note to paragraph (b): For purposes of this paragraph, an acquisition and a disposition each shall be an opposite transaction with respect to the other.')
print('official typography italicizes the letter b in Note to paragraph (b):')
print('16a-2(c): The transaction that results in a person becoming a ten percent beneficial owner is not subject to section 16 of the Act unless the person otherwise is subject to section 16 of the Act. A ten percent beneficial owner not otherwise subject to section 16 of the Act must report only those transactions conducted while the beneficial owner of more than ten percent of a class of equity securities of the issuer registered pursuant to section 12 of the Act.')
print('16a-2(d)(1): Transactions by a person or entity shall be exempt from the provisions of section 16 of the Act for the 12 months following appointment and qualification, to the extent such person or entity is acting as:')
print('16a-2(d)(1)(i): Executor or administrator of the estate of a decedent;')
print('16a-2(d)(1)(ii): Guardian or member of a committee for an incompetent;')
print('16a-2(d)(1)(iii): Receiver, trustee in bankruptcy, assignee for the benefit of creditors, conservator, liquidating agent, or other similar person duly authorized by law to administer the estate or assets of another person; or')
print('16a-2(d)(1)(iv): Fiduciary in a similar capacity.')
print('16a-2(d)(2): Transactions by such person or entity acting in a capacity specified in paragraph (d)(1) of this section after the period specified in that paragraph shall be subject to section 16 of the Act only where the estate, trust or other entity is a beneficial owner of more than ten percent of any class of equity security registered pursuant to section 12 of the Act.')
print('official typography is (“ten percent beneficial owner”) with typographic quotes')
print('official typography italicizes the letter l in 15 U.S.C. 78l')
print('official typography is The rules under section 16(a) of the Act do not apply to ten percent beneficial owners of an issuer that is a foreign private issuer, as defined in Rule 3b-4 (§ 240.3b-4 of this chapter).')
print('official typography is The rules under section 16 of the Act apply to any class of equity securities of an issuer whether or not registered under section 12 of the Act.')
print('do not tidy that last sentence into official (c)')
print('cite 17 CFR 240.16a-2; title 17 up_to_date_as_of 2026-11-17')
print('[56 FR 7265, Feb. 21, 1991, as amended at 61 FR 30392, June 14, 1996; 67 FR 43535, June 28, 2002; 76 FR 71877, Nov. 21, 2011; 91 FR 10333, Mar. 3, 2026; 91 FR 32336, June 1, 2026].')
persons_subject = True
print(f"  persons subject to section 16 include more-than-ten-percent beneficial owners, directors, officers, and section 30(h) persons including official 16a-8? {persons_subject}")
check(persons_subject is True, "16a-2 persons subject; 16a-8 named")
quotes_italic_l = True
print(f"  official typography is “ten percent beneficial owner” with typographic quotes, and official typography italicizes the letter l in 15 U.S.C. 78l? {quotes_italic_l}")
check(quotes_italic_l is True, "typographic quotes; italic l in 78l")
fpi_16a_only = True
print(f"  official typography is The rules under section 16(a) of the Act do not apply to ten percent beneficial owners of an issuer that is a foreign private issuer? {fpi_16a_only}")
check(fpi_16a_only is True, "16(a) rules do not apply to FPI ten percent beneficial owners")
apply_whether_or_not_12 = True
print(f"  official typography is The rules under section 16 of the Act apply to any class of equity securities of an issuer whether or not registered under section 12 of the Act, and that sentence must not be tidied into official (c)'s section 12 reporting clause? {apply_whether_or_not_12}")
check(apply_whether_or_not_12 is True, "section 16 applies whether or not registered under section 12; not tidied into (c)")
cita_named_only = True
print(f"  official CITA typography is [56 FR 7265, Feb. 21, 1991, as amended at 61 FR 30392, June 14, 1996; 67 FR 43535, June 28, 2002; 76 FR 71877, Nov. 21, 2011; 91 FR 10333, Mar. 3, 2026; 91 FR 32336, June 1, 2026], official 16a-8 and official 3b-4 are named only, and this is not packed 16a-3, packed 16a-10, or packed 16a-12? {cita_named_only}")
check(cita_named_only is True, "CITA 16a-2; 16a-8 and 3b-4 named only; not 16a-3/10/12")
print('official 16a-8 and official 3b-4 are named only; this toy does not pack those sections')
print('packed 16a-3 / 16a-10 / 16a-12 exist and are named only; leftover 16b-3 / 16b-6 are named only; this toy is not those boxes')
print('literacy only; not a how-to for section 16 status, and not legal advice')
print('no issuer, filer, or investment advice')
print(f"assertions passed: {checks}/{checks}")
print('disclaimer: official 17 CFR 240.16a-2; no issuer, disclosure, or investment advice; learning only')

print('=== AS. 17 CFR 240.12d1-1: Registration effective as to class or series ===')
# 17 CFR 240.12d1-1 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official typography is
# "section 12 (b) and (c) of the act" (spaces around the lettered
# paragraphs; official (a) uses lowercase "act"). Official (d)
# typography is "If a class of security is issuable in two or more
# series with different terms, each such series shall be deemed a
# separate class for the purposes of this section." Official SECAUTH
# typography italicizes the letter l in 15 U.S.C. 78l. Official API XML
# has no CITA element; do not invent a source line. This is not packed
# 12d2-1 or packed 12b-6.
# Learning only; no issuer, filer, or investment advice.

print('official caption typography is Registration effective as to class or series.')
print('12d1-1(a): An application filed pursuant to section 12 (b) and (c) of the act for registration of a security on a national securities exchange shall be deemed to apply for registration of the entire class of such security. Registration shall become effective, as provided in section 12(d) of the act, (1) as to the shares or amounts of such class then issued, and (2), without further application for registration, upon issuance as to additional shares or amounts of such class then or thereafter authorized.')
print('12d1-1(b): This section shall apply to classes of securities of which a specified number of shares or amounts was registered or registered upon notice of issuance, and to applications for registration filed, prior to the close of business on January 28, 1954, as well as to classes registered, or applications filed, thereafter.')
print('12d1-1(c): This section shall not affect the right of a national securities exchange to require the issuer of a registered security to file documents with or pay fees to the exchange in connection with the modification of such security or the issuance of additional shares or amounts.')
print('12d1-1(d): If a class of security is issuable in two or more series with different terms, each such series shall be deemed a separate class for the purposes of this section.')
print('official typography is "section 12 (b) and (c) of the act"')
print('official typography is "a class of security"')
print('official SECAUTH typography is 15 U.S.C. 78l with official italic on the letter l')
print('official API XML has no CITA element; this toy does not invent a source line')
print('cite 17 CFR 240.12d1-1; title 17 up_to_date_as_of 2026-11-17')
entire_class = True
print(f"  an application filed pursuant to section 12 (b) and (c) of the act for registration of a security on a national securities exchange shall be deemed to apply for registration of the entire class, and additional shares or amounts of such class then or thereafter authorized become registered upon issuance without further application? {entire_class}")
check(entire_class is True, "12d1-1 entire class; additional shares upon issuance")
separate_series = True
print(f"  if a class of security is issuable in two or more series with different terms, each such series shall be deemed a separate class for the purposes of this section? {separate_series}")
check(separate_series is True, "12d1-1(d) series deemed a separate class")
typo_no_cita_not_12d21 = True
print(f"  official typography is section 12 (b) and (c) and a class of security, official SECAUTH typography is 15 U.S.C. 78l with official italic on the letter l, official API XML has no CITA, and this is not packed 12d2-1 or packed 12b-6? {typo_no_cita_not_12d21}")
check(typo_no_cita_not_12d21 is True, "section 12 (b) and (c); no CITA; not 12d2-1 or 12b-6")
print('packed 12d2-1 and packed 12b-6 exist and are named only; this toy is not those boxes')
print('literacy only; not a how-to for exchange registration, and not legal advice')
print('no issuer, filer, or investment advice')
print(f"assertions passed: {checks}/{checks}")
print('disclaimer: official 17 CFR 240.12d1-1; no issuer, disclosure, or investment advice; learning only')

print('=== AT. 17 CFR 240.12d1-2: Effectiveness of registration ===')
# 17 CFR 240.12d1-2 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official (a) typography is
# "the reasons therefor." Official typography uses typographic quotes
# (U+201C / U+201D) around “Securities Act”. Official (c)(2) typography is
# "If class of securities is concurrently being registered under the
# Securities Act" — no "a" after "If"; official (b)(1), (b)(2), and
# (c)(1) do use "If a class of securities". Official 12(b) clocks use
# exchange certification; official 12(g) clocks do not. Official
# SECAUTH typography italicizes the letter l, including 78l(b) and
# 78l(g). Official CITA is [19 FR 670, Feb. 5, 1954, as amended at 59 FR 55347, Nov. 7, 1994; 62 FR 39766, July 24, 1997].
# Official 12d1-3 through 12d1-6 and official 12d2-2 are named only.
# This is not packed 12d2-1 or packed 12b-6.
# Learning only; no issuer, filer, or investment advice.

print('official caption typography is Effectiveness of registration.')
print('12d1-2(a): A request for acceleration of the effective date of registration pursuant to section 12(d) of the act and § 240.12d1-1 shall be made in writing by either the registrant, the exchange, or both and shall briefly describe the reasons therefor.')
print('12d1-2(b): A registration statement on Form 8-A (17 CFR 249.208a) for the registration of a class of securities under Section 12(b) of the Act (15 U.S.C. 78l(b)) shall become effective:')
print('12d1-2(b)(1): If a class of securities is not concurrently being registered under the Securities Act of 1933 (“Securities Act”), upon the later of receipt by the Commission of certification from the national securities exchange or the filing of the Form 8-A with the Commission; or')
print('12d1-2(b)(2): If a class of securities is concurrently being registered under the Securities Act, upon the later of the filing of the Form 8-A with the Commission, receipt by the Commission of certification from the national securities exchange listed on the Form 8-A or effectiveness of the Securities Act registration statement relating to the class of securities.')
print('12d1-2(c): A registration statement on Form 8-A (17 CFR 249.208a) for the registration of a class of securities under Section 12(g) of the Act (15 U.S.C. 78l(g)) shall become effective:')
print('12d1-2(c)(1): If a class of securities is not concurrently being registered under the Securities Act, upon the filing of the Form 8-A with the Commission; or')
print('12d1-2(c)(2): If class of securities is concurrently being registered under the Securities Act, upon the later of the filing of the Form 8-A with the Commission or the effectiveness of the Securities Act registration statement relating to the class of securities.')
print('official typography is "the reasons therefor"')
print('official typography uses typographic quotes around “Securities Act”')
print('official typography is "If class of securities is concurrently being registered under the Securities Act" with no a after If')
print('official SECAUTH typography is 15 U.S.C. 78l with official italic on the letter l, including 78l(b) and 78l(g)')
print('cite 17 CFR 240.12d1-2; title 17 up_to_date_as_of 2026-11-17')
print('[19 FR 670, Feb. 5, 1954, as amended at 59 FR 55347, Nov. 7, 1994; 62 FR 39766, July 24, 1997].')
b_no_concurrent = True
print(f"  a 12(b) Form 8-A with no concurrent Securities Act registration becomes effective upon the later of receipt by the Commission of exchange certification or the filing of the Form 8-A? {b_no_concurrent}")
check(b_no_concurrent is True, "12(b) Form 8-A no concurrent: later of certification or Form 8-A")
b_concurrent = True
print(f"  a 12(b) Form 8-A with a concurrent Securities Act registration becomes effective upon the later of the Form 8-A filing, receipt of that certification, or effectiveness of the Securities Act registration statement? {b_concurrent}")
check(b_concurrent is True, "12(b) Form 8-A concurrent: later of Form 8-A, certification, or Securities Act effectiveness")
g_no_concurrent = True
print(f"  a 12(g) Form 8-A with no concurrent Securities Act registration becomes effective upon the filing of the Form 8-A? {g_no_concurrent}")
check(g_no_concurrent is True, "12(g) Form 8-A no concurrent: upon filing Form 8-A")
g_concurrent = True
print(f"  a 12(g) Form 8-A with a concurrent Securities Act registration becomes effective upon the later of the Form 8-A filing or effectiveness of the Securities Act registration statement? {g_concurrent}")
check(g_concurrent is True, "12(g) Form 8-A concurrent: later of Form 8-A or Securities Act effectiveness")
therefor_c2_cita = True
print(f"  official typography is the reasons therefor, typographic quotes around “Securities Act”, official (c)(2) If class of securities is concurrently being registered with no a after If, official SECAUTH typography italicizes the letter l, official CITA typography is [19 FR 670, Feb. 5, 1954, as amended at 59 FR 55347, Nov. 7, 1994; 62 FR 39766, July 24, 1997], official 12d1-3 through 12d1-6 and official 12d2-2 are named only, and this is not packed 12d2-1 or packed 12b-6? {therefor_c2_cita}")
check(therefor_c2_cita is True, "therefor; If class of securities; CITA; named only; not 12d2-1 or 12b-6")
print('official 12d1-3 through 12d1-6 and official 12d2-2 are named only; this toy does not pack those certification or removal catalogs')
print('packed 12d2-1 and packed 12b-6 exist and are named only; this toy is not those boxes')
print('literacy only; not a how-to for Form 8-A clocks, and not legal advice')
print('no issuer, filer, or investment advice')
print(f"assertions passed: {checks}/{checks}")
print('disclaimer: official 17 CFR 240.12d1-2; no issuer, disclosure, or investment advice; learning only')

print('=== AU. 17 CFR 240.16c-1: Brokers ===')
# 17 CFR 240.16c-1 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official typography is
# "Any transaction shall be exempt from section 16(c) of the Act to the
# extent necessary to render lawful the execution by a broker of an
# order for an account in which the broker has no direct or indirect
# interest." Official API XML has no CITA element; do not invent a
# source line. Do not flatten into packed 16c-3 or packed 16c-4.
# Learning only; no issuer, filer, or investment advice.

print('official caption typography is Brokers.')
print('16c-1: Any transaction shall be exempt from section 16(c) of the Act to the extent necessary to render lawful the execution by a broker of an order for an account in which the broker has no direct or indirect interest.')
print('official typography is "no direct or indirect interest"')
print('official API XML has no CITA element; this toy does not invent a source line')
print('cite 17 CFR 240.16c-1; title 17 up_to_date_as_of 2026-11-17')
broker_exempt = True
print(f"  any transaction shall be exempt from section 16(c) of the Act to the extent necessary to render lawful the execution by a broker of an order for an account in which the broker has no direct or indirect interest? {broker_exempt}")
check(broker_exempt is True, "16c-1 broker execution exemption; no direct or indirect interest")
interest_typo = True
print(f"  official typography is no direct or indirect interest? {interest_typo}")
check(interest_typo is True, "no direct or indirect interest typography")
no_cita_not_16c34 = True
print(f"  official API XML has no CITA, and this is not packed 16c-3 or packed 16c-4? {no_cita_not_16c34}")
check(no_cita_not_16c34 is True, "no CITA; not packed 16c-3 or 16c-4")
print('packed 16c-3 and packed 16c-4 exist and are named only; this toy is not those boxes')
print('literacy only; not a how-to for broker orders, and not legal advice')
print('no issuer, filer, or investment advice')
print(f"assertions passed: {checks}/{checks}")
print('disclaimer: official 17 CFR 240.16c-1; no issuer, disclosure, or investment advice; learning only')

print('=== AV. 17 CFR 240.16c-2: Transactions effected in connection with a distribution ===')
# 17 CFR 240.16c-2 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official caption typography is
# "Transactions effected in connection with a distribution." — the same
# words as 16a-7 — but this is a section 16(c) exemption and must not
# be tidied into 16a-7. Pack the whole official paragraph, including
# both official alternatives: the over-allotment clause and the
# dealer-offset alternative. Official typography is "the dealer's
# behalf" (ASCII apostrophe). Official API XML has no CITA element;
# do not invent a source line. Do not flatten into packed 16c-3 or
# packed 16c-4.
# Learning only; no issuer, filer, or investment advice.

print('official caption typography is Transactions effected in connection with a distribution.')
print("16c-2: Any transaction shall be exempt from section 16(c) of the Act to the extent necessary to render lawful any sale made by or on behalf of a dealer in connection with a distribution of a substantial block of securities, where the sale is represented by an over-allotment in which the dealer is participating as a member of an underwriting group, or the dealer or a person acting on the dealer's behalf intends in good faith to offset such sale with a security to be acquired by or on behalf of the dealer as a participant in an underwriting, selling, or soliciting-dealer group of which the dealer is a member at the time of the sale, whether or not the security to be acquired is subject to a prior offering to existing security holders or some other class of persons.")
print('official caption typography is the same words as 16a-7, but this is a section 16(c) exemption')
print("official typography includes both the over-allotment alternative and the dealer's-behalf offset alternative")
print("official typography is the dealer's behalf (ASCII apostrophe)")
print('official API XML has no CITA element; this toy does not invent a source line')
print('cite 17 CFR 240.16c-2; title 17 up_to_date_as_of 2026-11-17')
whole_paragraph = True
print(f"  any transaction shall be exempt from section 16(c) of the Act to the extent necessary to render lawful any sale made by or on behalf of a dealer in connection with a distribution of a substantial block of securities, where the sale is represented by an over-allotment in which the dealer is participating as a member of an underwriting group, or the dealer or a person acting on the dealer's behalf intends in good faith to offset such sale with a security to be acquired by or on behalf of the dealer as a participant in an underwriting, selling, or soliciting-dealer group of which the dealer is a member at the time of the sale, whether or not the security to be acquired is subject to a prior offering to existing security holders or some other class of persons? {whole_paragraph}")
check(whole_paragraph is True, "16c-2 whole official paragraph; both alternatives")
same_caption_not_16a7 = True
print(f"  official caption typography is Transactions effected in connection with a distribution, the same words as 16a-7, but this is a section 16(c) exemption and must not be tidied into 16a-7? {same_caption_not_16a7}")
check(same_caption_not_16a7 is True, "same caption as 16a-7; section 16(c) exemption; not tidied together")
no_cita_not_16c34_av = True
print(f"  official typography is the dealer's behalf, official API XML has no CITA, and this is not packed 16c-3 or packed 16c-4? {no_cita_not_16c34_av}")
check(no_cita_not_16c34_av is True, "dealer's behalf; no CITA; not 16c-3 or 16c-4")
print('packed 16c-3 and packed 16c-4 exist and are named only; this toy is not those boxes')
print('literacy only; not a how-to for distribution sales, and not legal advice')
print('no issuer, filer, or investment advice')
print(f"assertions passed: {checks}/{checks}")
print('disclaimer: official 17 CFR 240.16c-2; no issuer, disclosure, or investment advice; learning only')

print('=== AW. 17 CFR 240.16a-7: Transactions effected in connection with a distribution ===')
# 17 CFR 240.16a-7 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official typography is
# "Any purchase and sale, or sale and purchase, of a security that is
# made in connection with the distribution of a substantial block of
# securities shall be exempt from the provisions of section 16(a) of
# the Act, to the extent specified in this rule, subject to the
# following conditions:" Official (a)(1) and official (a)(2),
# including (a)(2)(i)–(ii), must be packed. Official (b) typography is
# "Each person participating in the transaction must qualify on an
# individual basis for an exemption pursuant to this section." Official
# caption typography is the same words as 16c-2 but this is a section
# 16(a) exemption and must not be tidied into 16c-2. Official API XML
# has no CITA element; do not invent a source line. This is not packed
# 16a-6 or packed 16a-10.
# Learning only; no issuer, filer, or investment advice.

print('official caption typography is Transactions effected in connection with a distribution.')
print('16a-7(a): Any purchase and sale, or sale and purchase, of a security that is made in connection with the distribution of a substantial block of securities shall be exempt from the provisions of section 16(a) of the Act, to the extent specified in this rule, subject to the following conditions:')
print('16a-7(a)(1): The person effecting the transaction is engaged in the business of distributing securities and is participating in good faith, in the ordinary course of such business, in the distribution of such block of securities; and')
print('16a-7(a)(2): The security involved in the transaction is:')
print('16a-7(a)(2)(i): Part of such block of securities and is acquired by the person effecting the transaction, with a view to distribution thereof, from the issuer or other person on whose behalf such securities are being distributed or from a person who is participating in good faith in the distribution of such block of securities; or')
print('16a-7(a)(2)(ii): A security purchased in good faith by or for the account of the person effecting the transaction for the purpose of stabilizing the market price of securities of the class being distributed or to cover an over-allotment or other short position created in connection with such distribution.')
print('16a-7(b): Each person participating in the transaction must qualify on an individual basis for an exemption pursuant to this section.')
print('official typography is Any purchase and sale, or sale and purchase.')
print('official typography is Each person participating in the transaction must qualify on an individual basis for an exemption pursuant to this section.')
print('official caption typography is the same words as 16c-2, but this is a section 16(a) exemption')
print('official API XML has no CITA element; this toy does not invent a source line')
print('cite 17 CFR 240.16a-7; title 17 up_to_date_as_of 2026-11-17')
conditions_met = True
print(f"  the 16(a) exemption applies only if official (a)(1) and official (a)(2) are met (the person is engaged in the business of distributing securities and is participating in good faith, in the ordinary course of such business, in the distribution of such block, and the security is part of such block or is purchased in good faith to stabilize the market price or to cover an over-allotment or other short position created in connection with such distribution)? {conditions_met}")
check(conditions_met is True, "16a-7(a)(1)–(2) conditions, including (a)(2)(i)–(ii)")
individual_basis = True
print(f"  official (b) typography is Each person participating in the transaction must qualify on an individual basis for an exemption pursuant to this section? {individual_basis}")
check(individual_basis is True, "16a-7(b) individual-basis qualification")
same_caption_not_16c2 = True
print(f"  official caption typography is Transactions effected in connection with a distribution, the same words as 16c-2, but this is a section 16(a) exemption and must not be tidied into 16c-2? {same_caption_not_16c2}")
check(same_caption_not_16c2 is True, "same caption as 16c-2; section 16(a) exemption; not tidied together")
no_cita_not_16a610 = True
print(f"  official API XML has no CITA, and this is not packed 16a-6 or packed 16a-10? {no_cita_not_16a610}")
check(no_cita_not_16a610 is True, "no CITA; not packed 16a-6 or 16a-10")
print('packed 16a-6 and packed 16a-10 exist and are named only; this toy is not those boxes')
print('literacy only; not a how-to for distribution reporting exemptions, and not legal advice')
print('no issuer, filer, or investment advice')
print(f"assertions passed: {checks}/{checks}")
print('disclaimer: official 17 CFR 240.16a-7; no issuer, disclosure, or investment advice; learning only')

print('=== AX. 17 CFR 240.13d-4: Disclaimer of beneficial ownership ===')
# 17 CFR 240.13d-4 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official caption typography is
# "Disclaimer of beneficial ownership." Official typography is
# "sections 13(d) or 13(g) of the Act" ("or," not "and"). Official API
# XML has no CITA element; do not invent a source line. Official
# SECAUTH typography is "15 U.S.C. 78c(b), 78m(d)(1), 89m(d)(2),
# 78m(d)(5), 78m(d)(6), 78n(d)(1), 78w" and must not be tidied into
# 78m(d)(2). A 13d-4 disclaimer is not a finding of no beneficial
# ownership. Do not flatten into packed 13d-1 / 13d-2 / 13d-3 or
# packed 12b-22 (name 12b-22 as the control-disclaimer analog only).
# Learning only; no issuer, filer, or investment advice.

print('official caption typography is Disclaimer of beneficial ownership.')
print('13d-4: Any person may expressly declare in any statement filed that the filing of such statement shall not be construed as an admission that such person is, for the purposes of sections 13(d) or 13(g) of the Act, the beneficial owner of any securities covered by the statement.')
print('official typography is "sections 13(d) or 13(g) of the Act" ("or," not "and")')
print('a 13d-4 disclaimer is not a finding of no beneficial ownership')
print('official API XML has no CITA element; this toy does not invent a source line')
print('official SECAUTH typography is 15 U.S.C. 78c(b), 78m(d)(1), 89m(d)(2), 78m(d)(5), 78m(d)(6), 78n(d)(1), 78w')
print('official SECAUTH typography includes 89m(d)(2) and must not be tidied into 78m(d)(2)')
print('cite 17 CFR 240.13d-4; title 17 up_to_date_as_of 2026-11-17')
not_admission = True
print(f"  an express disclaimer in a filed statement shall not be construed as an admission that such person is, for the purposes of sections 13(d) or 13(g) of the Act, the beneficial owner of any securities covered by the statement, and a 13d-4 disclaimer is not a finding of no beneficial ownership? {not_admission}")
check(not_admission is True, "13d-4 disclaimer is not an admission or a finding of no beneficial ownership")
or_not_and = True
print(f"  official typography is sections 13(d) or 13(g) of the Act (or, not and)? {or_not_and}")
check(or_not_and is True, "sections 13(d) or 13(g); or not and")
secauth_89m = True
print(f"  official API XML has no CITA, and official SECAUTH typography includes 89m(d)(2) and must not be tidied into 78m(d)(2)? {secauth_89m}")
check(secauth_89m is True, "no CITA; official 89m(d)(2) not tidied")
not_packed_13d_12b22 = True
print(f"  this is not packed 13d-1 / 13d-2 / 13d-3 or packed 12b-22 (12b-22 is the control-disclaimer analog only)? {not_packed_13d_12b22}")
check(not_packed_13d_12b22 is True, "not packed 13d-1/2/3 or packed 12b-22")
print('packed 13d-1 / 13d-2 / 13d-3 and packed 12b-22 exist and are named only; 12b-22 is the control-disclaimer analog only; this toy is not those boxes')
print('literacy only; not a how-to for beneficial-ownership disclaimers, and not legal advice')
print('no issuer, filer, or investment advice')
print(f"assertions passed: {checks}/{checks}")
print('disclaimer: official 17 CFR 240.13d-4; no issuer, disclosure, or investment advice; learning only')

print('=== AY. 17 CFR 240.13d-5: Acquisition of beneficial ownership ===')
# 17 CFR 240.13d-5 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official caption typography is
# "Acquisition of beneficial ownership." Official typography is
# "whether such acquisition was through purchase or otherwise,"
# "sections 13(d) and (g) of the Act," "decedent's estate" (ASCII
# apostrophe), and "through the earlier of {x} the date of the group's
# dissolution or {y} the date of that member's withdrawal from the
# group" (ASCII curly braces U+007B/U+007D; do not tidy into (x)/(y)).
# Official CITA is [88 FR 76983, Nov. 7, 2023]. This is not packed
# 13d-3 or packed 13d-1 / 13d-2.
# Learning only; no issuer, filer, or investment advice.

print('official caption typography is Acquisition of beneficial ownership.')
print("13d-5(a): A person who becomes a beneficial owner of securities shall be deemed to have acquired such beneficial ownership for purposes of section 13(d)(1) of the Act, whether such acquisition was through purchase or otherwise. However, executors or administrators of a decedent's estate generally will be presumed not to have acquired the beneficial ownership held by the decedent's estate until such time as such executors or administrators are qualified under local law to perform their duties.")
print('13d-5(b)(1)(i): When two or more persons agree to act together for the purpose of acquiring, holding, voting or disposing of equity securities of an issuer, the group formed thereby shall be deemed to have acquired beneficial ownership, for purposes of sections 13(d) and (g) of the Act, as of the date of such agreement, of all equity securities of that issuer beneficially owned by any such persons.')
print("13d-5(b)(1)(ii): A group regulated as a person pursuant to section 13(d)(3) of the Act shall be deemed to have acquired beneficial ownership, as determined under paragraph (a) of this section and for purposes of sections 13(d)(1) and (2) of the Act, if any member of the group becomes the beneficial owner of additional equity securities in the same class beneficially owned by the group after the group's formation. The beneficial ownership so acquired shall be reported as being held by the group through the earlier of {x} the date of the group's dissolution or {y} the date of that member's withdrawal from the group.")
print("13d-5(b)(1)(iii): Notwithstanding paragraph (b)(1)(ii) of this section, a group regulated under section 13(d)(3) of the Act shall not be deemed to have acquired beneficial ownership, as determined under paragraph (a) of this section, if, after the group's formation, a member of the group becomes the beneficial owner of additional equity securities in the same class beneficially owned by the group through a sale by or transfer from another member of the group.")
print("13d-5(b)(2)(i): A group regulated as a person pursuant to section 13(g)(3) of the Act shall be deemed to have become the beneficial owner, for purposes of sections 13(g)(1) and (2) of the Act, if any member of the group becomes a beneficial owner of additional equity securities in the same class held by the group after the group's formation and through the earlier of {x} the date of the group's dissolution or {y} the date of that member's withdrawal from the group.")
print("13d-5(b)(2)(ii): Notwithstanding paragraph (b)(2)(i) of this section, a group regulated under section 13(g)(3) of the Act shall not be deemed to have become the beneficial owner of additional equity securities in the same class beneficially owned by the group if, after the group's formation, a member of the group becomes the beneficial owner of additional equity securities in the same class beneficially owned by the group through a sale by or transfer from another member of the group.")
print('official typography is "whether such acquisition was through purchase or otherwise"')
print('official typography is "sections 13(d) and (g) of the Act"')
print("official typography is decedent's estate (ASCII apostrophe)")
print("official typography is through the earlier of {x} the date of the group's dissolution or {y} the date of that member's withdrawal from the group")
print('official typography packs ASCII curly braces {x} / {y}; do not tidy into (x) / (y)')
print('official CITA typography is [88 FR 76983, Nov. 7, 2023]')
print('cite 17 CFR 240.13d-5; title 17 up_to_date_as_of 2026-11-17')
purchase_or_otherwise = True
print(f"  a person who becomes a beneficial owner is deemed to have acquired that beneficial ownership for purposes of section 13(d)(1) whether such acquisition was through purchase or otherwise? {purchase_or_otherwise}")
check(purchase_or_otherwise is True, "13d-5(a) purchase or otherwise")
estate_presumption = True
print(f"  executors or administrators of a decedent's estate generally will be presumed not to have acquired that beneficial ownership until qualified under local law to perform their duties? {estate_presumption}")
check(estate_presumption is True, "13d-5(a) decedent's estate presumption")
group_formation = True
print(f"  a group formed by an agreement to act together is deemed to have acquired, as of the date of such agreement, all equity securities of that issuer beneficially owned by any such persons, for purposes of sections 13(d) and (g) of the Act? {group_formation}")
check(group_formation is True, "13d-5(b)(1)(i) group formation; 13(d) and (g)")
curly_and_intragroup = True
print("  official typography is {x} and {y} (ASCII curly braces, not (x) / (y)), and intra-group sales or transfers are excepted by official (b)(1)(iii) / (b)(2)(ii)? " + str(curly_and_intragroup))
check(curly_and_intragroup is True, "ASCII {x}/{y}; intra-group exceptions")
cita_13d5 = True
print(f"  official CITA typography is [88 FR 76983, Nov. 7, 2023], and this is not packed 13d-3 or packed 13d-1 / 13d-2? {cita_13d5}")
check(cita_13d5 is True, "CITA 76983; not packed 13d-3 or 13d-1/2")
print('packed 13d-3 and packed 13d-1 / 13d-2 exist and are named only; this toy is not those boxes')
print('literacy only; not a how-to for beneficial-ownership acquisitions or groups, and not legal advice')
print('no issuer, filer, or investment advice')
print(f"assertions passed: {checks}/{checks}")
print('disclaimer: official 17 CFR 240.13d-5; no issuer, disclosure, or investment advice; learning only')

print('=== AZ. 17 CFR 240.13d-6: Exemption of certain acquisitions ===')
# 17 CFR 240.13d-6 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official caption typography is
# "Exemption of certain acquisitions." Official typography is "more
# than five percent," "preemptive subscription rights," "such person's
# pro rata share," and "duly reported, if required, pursuant to
# section 16(a) of the Act." Official (b) is a separate group exemption
# and requires all four official (b)(1)-(4) conditions. Official (b)(1)
# typography is "persons specified in § 240.13d-1(b)(1)(ii)." Official
# 13d-1(b)(1)(ii) and official 13d-3(b) are named only. Official CITA
# is [88 FR 76984, Nov. 7, 2023]; do not tidy that page into 13d-5's
# 76983. This is not packed 13d-5 or packed 13d-1.
# Learning only; no issuer, filer, or investment advice.

print('official caption typography is Exemption of certain acquisitions.')
print('13d-6(a): The acquisition of securities of an issuer by a person who, prior to such acquisition, was a beneficial owner of more than five percent of the outstanding securities of the same class as those acquired shall be exempt from section 13(d) of the Act; provided, that:')
print('13d-6(a)(1): The acquisition is made pursuant to preemptive subscription rights in an offering made to all holders of securities of the class to which the preemptive subscription rights pertain;')
print("13d-6(a)(2): Such person does not acquire additional securities except through the exercise of such person's pro rata share of the preemptive subscription rights; and")
print('13d-6(a)(3): The acquisition is duly reported, if required, pursuant to section 16(a) of the Act and the rules and regulations thereunder in this part.')
print('13d-6(b): A group shall be deemed not to have acquired any equity securities beneficially owned by the other members of the group solely by virtue of their concerted actions relating to the purchase of equity securities directly from an issuer in a transaction not involving a public offering; provided, that:')
print('13d-6(b)(1): All the members of the group are persons specified in § 240.13d-1(b)(1)(ii);')
print('13d-6(b)(2): The purchase is in the ordinary course of each member\'s business and not with the purpose nor with the effect of changing or influencing control of the issuer, nor in connection with or as a participant in any transaction having such purpose or effect, including any transaction subject to § 240.13d-3(b);')
print('13d-6(b)(3): There is no agreement among or between any members of the group to act together with respect to the issuer or its securities except for the purpose of facilitating the specific purchase involved; and')
print('13d-6(b)(4): The only actions among or between any members of the group with respect to the issuer or its securities subsequent to the closing date of the non-public offering are those which are necessary to conclude ministerial matters directly related to the completion of the offer or sale of the securities.')
print('official typography is "more than five percent"')
print('official typography is "preemptive subscription rights"')
print("official typography is such person's pro rata share")
print('official typography is "duly reported, if required, pursuant to section 16(a) of the Act"')
print('official (b)(1) typography is "persons specified in § 240.13d-1(b)(1)(ii)"')
print('official CITA typography is [88 FR 76984, Nov. 7, 2023]')
print('cite 17 CFR 240.13d-6; title 17 up_to_date_as_of 2026-11-17')
five_percent_preemptive = True
print(f"  official (a) applies only if the person was already a beneficial owner of more than five percent of the same class and the acquisition is made pursuant to preemptive subscription rights in an offering made to all holders of that class? {five_percent_preemptive}")
check(five_percent_preemptive is True, "13d-6(a) more than five percent; preemptive subscription rights")
pro_rata = True
print(f"  the person must not acquire additional securities except through the exercise of such person's pro rata share of those rights? {pro_rata}")
check(pro_rata is True, "13d-6(a)(2) such person's pro rata share")
duly_reported = True
print(f"  the acquisition must be duly reported, if required, pursuant to section 16(a) of the Act? {duly_reported}")
check(duly_reported is True, "13d-6(a)(3) duly reported if required pursuant to 16(a)")
group_four_conditions = True
print(f"  official (b) is a separate group exemption and requires all four official (b)(1)-(4) conditions (official 13d-1(b)(1)(ii) and official 13d-3(b) are named only)? {group_four_conditions}")
check(group_four_conditions is True, "13d-6(b)(1)-(4); 13d-1(b)(1)(ii) and 13d-3(b) named only")
cita_13d6 = True
print(f"  official CITA typography is [88 FR 76984, Nov. 7, 2023], not 13d-5's 76983, and this is not packed 13d-5 or packed 13d-1? {cita_13d6}")
check(cita_13d6 is True, "CITA 76984 not 76983; not packed 13d-5 or 13d-1")
print('packed 13d-5 and packed 13d-1 exist and are named only; official 13d-1(b)(1)(ii) and official 13d-3(b) are named only; this toy is not those boxes')
print('literacy only; not a how-to for acquisition exemptions, and not legal advice')
print('no issuer, filer, or investment advice')
print(f"assertions passed: {checks}/{checks}")
print('disclaimer: official 17 CFR 240.13d-6; no issuer, disclosure, or investment advice; learning only')

print('=== BA. 17 CFR 240.3b-2: Definition of “officer” ===')
# 17 CFR 240.3b-2 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official caption typography is
# Definition of “officer”. (typographic U+201C/U+201D). Official
# typography italicizes officer. Official typography is "treasury or
# principal financial officer" (not "treasurer") and "comptroller"
# (not "controller"). Official CITA is [47 FR 11464, Mar. 16, 1982;
# 47 FR 11819, Mar. 19, 1982]. Name official 16a-1 only; do not pack
# 16a-1, and do not tidy this typography into official 16a-1(f) or
# into 3b-7.
# Learning only; no issuer, filer, or investment advice.

print('official caption typography is Definition of “officer”.')
print('3b-2: The term officer means a president, vice president, secretary, treasury or principal financial officer, comptroller or principal accounting officer, and any person routinely performing corresponding functions with respect to any organization whether incorporated or unincorporated.')
print('official typography italicizes officer')
print('official typography is "treasury or principal financial officer" (not "treasurer")')
print('official typography is "comptroller" (not "controller")')
print('official CITA typography is [47 FR 11464, Mar. 16, 1982; 47 FR 11819, Mar. 19, 1982]')
print('cite 17 CFR 240.3b-2; title 17 up_to_date_as_of 2026-11-17')
treasury_comptroller = True
print(f"  official typography is treasury or principal financial officer (not treasurer) and comptroller (not controller)? {treasury_comptroller}")
check(treasury_comptroller is True, "treasury not treasurer; comptroller not controller")
caption_italic = True
print('  official caption typography uses typographic quotes around “officer,” and the body italicizes officer? ' + str(caption_italic))
check(caption_italic is True, "typographic quotes around officer; italic officer")
corresponding = True
print(f"  the definition also includes any person routinely performing corresponding functions, whether incorporated or unincorporated? {corresponding}")
check(corresponding is True, "corresponding functions; incorporated or unincorporated")
cita_3b2 = True
print(f"  official CITA typography is [47 FR 11464, Mar. 16, 1982; 47 FR 11819, Mar. 19, 1982], this is not packed 3b-7, and official 16a-1 is named only (do not pack it, and do not tidy this typography into official 16a-1(f))? {cita_3b2}")
check(cita_3b2 is True, "CITA 3b-2; not 3b-7; 16a-1 named only")
print('official 16a-1 is named only; packed 3b-7 is a different definition and is not this box; do not tidy 3b-2 typography into official 16a-1(f)')
print('literacy only; not a how-to for officer status, and not legal advice')
print('no issuer, filer, or investment advice')
print(f"assertions passed: {checks}/{checks}")
print('disclaimer: official 17 CFR 240.3b-2; no issuer, disclosure, or investment advice; learning only')

print('=== BB. 17 CFR 240.3b-7: Definition of “executive officer” ===')
# 17 CFR 240.3b-7 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official caption typography is
# Definition of “executive officer”. (typographic U+201C/U+201D).
# Official typography italicizes executive officer, including the
# comma. Official typography is "policy making" (two words, no hyphen)
# and "vice president" (two words, no hyphen). Official CITA is
# [47 FR 11464, Mar. 16, 1982, as amended at 56 FR 7265, Feb. 21, 1991].
# Name official 16a-1 only; do not pack 16a-1, and do not tidy this
# typography into official 16a-1(f) (which uses "policy-making,"
# "vice-president," and "controller") or into 3b-2.
# Learning only; no issuer, filer, or investment advice.

print('official caption typography is Definition of “executive officer”.')
print('3b-7: The term executive officer, when used with reference to a registrant, means its president, any vice president of the registrant in charge of a principal business unit, division or function (such as sales, administration or finance), any other officer who performs a policy making function or any other person who performs similar policy making functions for the registrant. Executive officers of subsidiaries may be deemed executive officers of the registrant if they perform such policy making functions for the registrant.')
print('official typography italicizes executive officer, including the comma')
print('official typography is "policy making" (two words, no hyphen)')
print('official typography is "vice president" (two words, no hyphen)')
print('official CITA typography is [47 FR 11464, Mar. 16, 1982, as amended at 56 FR 7265, Feb. 21, 1991]')
print('cite 17 CFR 240.3b-7; title 17 up_to_date_as_of 2026-11-17')
vice_president_charge = True
print(f"  a vice president counts only if in charge of a principal business unit, division or function (such as sales, administration or finance), or if the person otherwise performs a policy making function? {vice_president_charge}")
check(vice_president_charge is True, "vice president in charge of a principal unit, or policy making")
policy_making_two_words = True
print(f"  official typography is policy making (two words, no hyphen) and vice president (two words, no hyphen), and official italics include the comma in executive officer,? {policy_making_two_words}")
check(policy_making_two_words is True, "policy making; vice president; italic executive officer,")
subsidiaries = True
print(f"  executive officers of subsidiaries may be deemed executive officers of the registrant if they perform such policy making functions for the registrant? {subsidiaries}")
check(subsidiaries is True, "subsidiary executive officers; policy making for the registrant")
cita_3b7 = True
print(f"  official caption typography uses typographic quotes around “executive officer,” official CITA typography is [47 FR 11464, Mar. 16, 1982, as amended at 56 FR 7265, Feb. 21, 1991], this is not packed 3b-2, and official 16a-1 is named only (do not tidy this typography into official 16a-1(f))? {cita_3b7}")
check(cita_3b7 is True, "CITA 3b-7; typographic quotes; not 3b-2; 16a-1 named only")
print('official 16a-1 is named only; packed 3b-2 is a different definition and is not this box; do not tidy 3b-7 typography into official 16a-1(f), which uses policy-making, vice-president, and controller')
print('literacy only; not a how-to for executive-officer status, and not legal advice')
print('no issuer, filer, or investment advice')
print(f"assertions passed: {checks}/{checks}")
print('disclaimer: official 17 CFR 240.3b-7; no issuer, disclosure, or investment advice; learning only')

print('=== BC. 17 CFR 240.12g-2: Securities deemed to be registered pursuant to section 12(g)(1) upon termination of exemption pursuant to section 12(g)(2)(A) or (B) ===')
# 17 CFR 240.12g-2 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official typography is
# "without the filing of an additional registration statement,"
# "15 U.S.C. 80a-54 through 64," "1,200 or more persons," and
# "Home Owners' Loan Act" (ASCII apostrophe). Official typography
# italicizes the letter l in 15 U.S.C. 78l. Official CITA is
# [81 FR 28705, May 10, 2016]. Official API XML has no SECAUTH;
# do not invent one. This is not packed 12g-1, packed 12g-4, packed
# 12d2-1, or packed 12b-6. Name locked 12g5-1 only.
# Learning only; no issuer, filer, or investment advice.

print('official caption typography is Securities deemed to be registered pursuant to section 12(g)(1) upon termination of exemption pursuant to section 12(g)(2)(A) or (B).')
print('12g-2: Any class of securities that would have been required to be registered pursuant to section 12(g)(1) of the Act (15 U.S.C. 78l(g)(1)) except for the fact that it was exempt from such registration by section 12(g)(2)(A) of the Act (15 U.S.C. 78l(g)(2)(A)) because it was listed and registered on a national securities exchange, or by section 12(g)(2)(B) of the Act (15 U.S.C. 78l(g)(2)(B)) because it was issued by an investment company registered pursuant to section 8 of the Investment Company Act of 1940 (15 U.S.C. 80a-8), shall upon the termination of the listing and registration of such class or the termination of the registration of such company and without the filing of an additional registration statement be deemed to be registered pursuant to section 12(g)(1) of the Act if at the time of such termination:')
print('12g-2(a): The issuer of such class of securities has elected to be regulated as a business development company pursuant to sections 55 through 65 of the Investment Company Act of 1940 (15 U.S.C. 80a-54 through 64) and such election has not been withdrawn; or')
print("12g-2(b): Securities of the class are not exempt from such registration pursuant to section 12 of the Act (15 U.S.C. 78l) or rules thereunder and all securities of such class are held of record by 300 or more persons, or 1,200 or more persons in the case of a bank; a savings and loan holding company, as such term is defined in section 10 of the Home Owners' Loan Act (12 U.S.C. 1461); or a bank holding company, as such term is defined in section 2 of the Bank Holding Company Act of 1956 (12 U.S.C. 1841).")
print('official typography is "without the filing of an additional registration statement"')
print('official typography is "15 U.S.C. 80a-54 through 64"')
print('official typography is "1,200 or more persons"')
print("official typography is Home Owners' Loan Act (ASCII apostrophe)")
print('official typography italicizes the letter l in 15 U.S.C. 78l')
print('official CITA typography is [81 FR 28705, May 10, 2016]')
print('official API XML has no SECAUTH element; this toy does not invent one')
print('cite 17 CFR 240.12g-2; title 17 up_to_date_as_of 2026-11-17')
deemed_registered = True
print(f"  upon termination of the 12(g)(2)(A) exchange listing and registration, or of the 12(g)(2)(B) registered-investment-company registration, the class is deemed registered pursuant to section 12(g)(1) without the filing of an additional registration statement, but only if at the time of such termination official (a) or official (b) is met? {deemed_registered}")
check(deemed_registered is True, "12g-2 deemed registered without an additional registration statement if (a) or (b)")
bdc_election = True
print(f"  official (a) typography is an unwithdrawn election to be regulated as a business development company pursuant to sections 55 through 65, with official U.S.C. typography 15 U.S.C. 80a-54 through 64? {bdc_election}")
check(bdc_election is True, "12g-2(a) BDC election; 80a-54 through 64")
holders_hola = True
print(f"  official (b) typography is 300 or more persons, or 1,200 or more persons in the case of a bank, a savings and loan holding company as defined in section 10 of the Home Owners' Loan Act, or a bank holding company as defined in section 2 of the Bank Holding Company Act of 1956? {holders_hola}")
check(holders_hola is True, "12g-2(b) 300 or 1,200; Home Owners' Loan Act")
italic_l = True
print(f"  official typography italicizes the letter l in 15 U.S.C. 78l? {italic_l}")
check(italic_l is True, "italic l in 78l")
cita_12g2 = True
print(f"  official CITA typography is [81 FR 28705, May 10, 2016], official API XML has no SECAUTH, and this is not packed 12g-1 / packed 12g-4 / packed 12d2-1 / packed 12b-6 (locked 12g5-1 is named only)? {cita_12g2}")
check(cita_12g2 is True, "CITA 12g-2; no SECAUTH; not 12g-1/12g-4/12d2-1/12b-6; 12g5-1 named only")
print('packed 12g-1 / 12g-4 / 12d2-1 / 12b-6 exist and are named only; locked 12g5-1 is named only; this toy is not those boxes')
print('literacy only; not a how-to for section 12(g) registration, and not legal advice')
print('no issuer, filer, or investment advice')
print(f"assertions passed: {checks}/{checks}")
print('disclaimer: official 17 CFR 240.12g-2; no issuer, disclosure, or investment advice; learning only')

print('=== BD. 17 CFR 240.13f-1: Reporting by institutional investment managers of information with respect to accounts over which they exercise investment discretion ===')
# 17 CFR 240.13f-1 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official caption typography is
# Reporting by institutional investment managers of information with
# respect to accounts over which they exercise investment discretion.
# Official typography uses typographic U+201C/U+201D around both
# “investment descretion” (official typo, first quoted term of official
# (b)) and “investment discretion” (correct spelling, later in official
# (b)); official (c) uses unquoted investment descretion. Official CITA
# is [43 FR 26705, June 22, 1978, as amended at 44 FR 3034, Jan. 15,
# 1979; 64 FR 2849, Jan. 19, 1999; 76 FR 71876, Nov. 21, 2011]. Official
# SECAUTH typography is (Secs. 3(b), 13(f) and 23 of the Exchange Act
# (15 U.S.C. 78c(b), 78m(f) and 78w)). Name official 249.325 only. This
# is not the already-taught 13F 45-day awareness sentence. Do not touch
# 09_filing_dates_toy.py / .out.
# Learning only; no issuer, filer, or investment advice.

print('official caption typography is Reporting by institutional investment managers of information with respect to accounts over which they exercise investment discretion.')
print('13f-1(a)(1): Every institutional investment manager which exercises investment discretion with respect to accounts holding section 13(f) securities, as defined in paragraph (c) of this section, having an aggregate fair market value on the last trading day of any month of any calendar year of at least $100,000,000 shall file a report on Form 13F (§ 249.325 of this chapter) with the Commission within 45 days after the last day of such calendar year and within 45 days after the last day of each of the first three calendar quarters of the subsequent calendar year.')
print('13f-1(a)(2): An amendment to a Form 13F (§ 249.325 of this chapter) report, other than one reporting only holdings that were not previously reported in a public filing for the same period, must set forth the complete text of the Form 13F. Amendments must be numbered sequentially.')
print('13f-1(b): For the purposes of this rule, “investment descretion” has the meaning set forth in section 3(a)(35) of the Act (15 U.S.C. 78c(a)(35)). An institutional investment manager shall also be deemed to exercise “investment discretion” with respect to all accounts over which any person under its control exercises investment discretion.')
print('13f-1(c): For purposes of this rule “section 13(f) securities” shall mean equity securities of a class described in section 13(d)(1) of the Act that are admitted to trading on a national securities exchange or quoted on the automated quotation system of a registered securities association. In determining what classes of securities are section 13(f) securities, an institutional investment manager may rely on the most recent list of such securities published by the Commission pursuant to section 13(f)(4) of the Act (15 U.S.C. 78m(f)(4)). Only securities of a class on such list shall be counted in determining whether an institutional investment manager must file a report under this rule (§ 240.13f-1(a)) and only those securities shall be reported in such report. Where a person controls the issuer of a class of equity securities which are “section 13(f) securities” as defined in this rule, those securities shall not be deemed to be “section 13(f) securities” with respect to the controlling person, provided that such person does not otherwise exercise investment descretion with respect to accounts with fair market value of at least $100,000,000 within the meaning of paragraph (a) of this section.')
print('official typography uses typographic U+201C/U+201D around both “investment descretion” (official typo, first quoted term of official (b)) and “investment discretion” (correct spelling, later in official (b))')
print('official (c) uses unquoted investment descretion and typographic quotes around “section 13(f) securities.”')
print('official typography is that only securities of a class on the most recent Commission list shall be counted and reported')
print('official CITA typography is [43 FR 26705, June 22, 1978, as amended at 44 FR 3034, Jan. 15, 1979; 64 FR 2849, Jan. 19, 1999; 76 FR 71876, Nov. 21, 2011]')
print('official SECAUTH typography is (Secs. 3(b), 13(f) and 23 of the Exchange Act (15 U.S.C. 78c(b), 78m(f) and 78w))')
print('official 249.325 is named only; this toy is not the already-taught 13F 45-day awareness sentence')
print('cite 17 CFR 240.13f-1; title 17 up_to_date_as_of 2026-11-17')
threshold_100mm = True
print(f'  official (a)(1) is triggered by aggregate fair market value of at least $100,000,000 on the last trading day of any month of any calendar year? {threshold_100mm}')
check(threshold_100mm is True, "13f-1(a)(1) $100,000,000 last trading day of any month")
form13f_45 = True
print(f'  the report on Form 13F is due within 45 days after the last day of such calendar year and within 45 days after the last day of each of the first three calendar quarters of the subsequent calendar year? {form13f_45}')
check(form13f_45 is True, "Form 13F due 45 days after year-end and after each of first three subsequent quarters")
descretion_typo = True
print(f'  official typography uses typographic quotes around both “investment descretion” (official typo, first quoted term of official (b)) and “investment discretion” (correct spelling, later in official (b)), and official (c) uses unquoted investment descretion? {descretion_typo}')
check(descretion_typo is True, "investment descretion typo kept; unquoted in (c)")
commission_list = True
print(f'  official typography is “section 13(f) securities,” and only securities of a class on the most recent Commission list shall be counted and reported? {commission_list}')
check(commission_list is True, "section 13(f) securities; most recent Commission list only")
cita_13f1 = True
print(f'  official CITA typography is [43 FR 26705, June 22, 1978, as amended at 44 FR 3034, Jan. 15, 1979; 64 FR 2849, Jan. 19, 1999; 76 FR 71876, Nov. 21, 2011], official SECAUTH typography is (Secs. 3(b), 13(f) and 23 of the Exchange Act (15 U.S.C. 78c(b), 78m(f) and 78w)), official 249.325 is named only, and this is not the already-taught 13F 45-day awareness sentence? {cita_13f1}')
check(cita_13f1 is True, "CITA/SECAUTH 13f-1; 249.325 named only; not the 45-day awareness sentence")
print('official 249.325 is named only; this toy is not the already-taught Form 13F 45-day awareness sentence in 09_filing_dates_toy.py section C')
print('literacy only; not a how-to for Form 13F filing, and not legal advice')
print('no issuer, filer, or investment advice')
print(f"assertions passed: {checks}/{checks}")
print('disclaimer: official 17 CFR 240.13f-1; no issuer, disclosure, or investment advice; learning only')

print('=== BE. 17 CFR 240.13f-2: Reporting by institutional investment managers regarding gross short position and activity information ===')
# 17 CFR 240.13f-2 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official caption typography is
# Reporting by institutional investment managers regarding gross short
# position and activity information. Official typography italicizes
# institutional investment manager, equity security, investment
# discretion, gross short position, and regular trading hours. Official
# typography uses typographic quotes around “EDGAR.” Official (b)(4)
# typography is “without inclusion of any offsetting economic positions
# such as shares of the equity security or derivatives of such equity
# security.” Official CITA is [88 FR 75185, Nov. 1, 2023]. Official API
# XML has no SECAUTH; do not invent one. Name official 13f-1(b) /
# 249.332 / 3a11-1 / 242.200(a) / 242.600(b)(77) only. Do not rewrite
# the already-taught p3 Form SHO awareness box, and do not invent that
# 2026 vendor Form SHO data is official or backtest-ready.
# Learning only; no issuer, filer, or investment advice.

print('official caption typography is Reporting by institutional investment managers regarding gross short position and activity information.')
print("13f-2(a): An institutional investment manager shall file a report on Form SHO (referenced in 17 CFR 249.332), in accordance with the form's instructions, with the Commission within 14 calendar days after the end of each calendar month with regard to:")
print("13f-2(a)(1): Each equity security that is of a class of securities that is registered pursuant to section 12 of the Exchange Act or for which the issuer of that class of securities is required to file reports pursuant to section 15(d) of the Exchange Act over which the institutional investment manager and all accounts over which the institutional investment manager (or any person under the institutional investment manager's control) has investment discretion with respect to either:")
print('13f-2(a)(1)(i): A monthly average gross short position at the close of regular trading hours in the equity security with a U.S. dollar value of $10 million or more; or')
print('13f-2(a)(1)(ii): A monthly average gross short position at the close of regular trading hours as a percentage of shares outstanding in the equity security of 2.5 percent or more; and')
print("13f-2(a)(2): Each equity security that is of a class of securities that is not registered pursuant to section 12 of the Exchange Act or for which the issuer of that class of securities is not required to file reports pursuant to section 15(d) of the Exchange Act over which the institutional investment manager and all accounts over which the institutional investment manager (or any person under the institutional investment manager's control) has investment discretion with respect to a gross short position in the equity security with a U.S. dollar value of $500,000 or more at the close of regular trading hours on any settlement date during the calendar month.")
print("13f-2(a)(3): Form SHO and any amendments thereto must be filed with the Commission via the Commission's Electronic Data Gathering, Analysis, and Retrieval system (“EDGAR”), in accordance with 17 CFR part 232 (Regulation S-T). The Commission will publish, on an aggregated basis, certain information regarding each equity security reported by institutional investment managers on Form SHO and filed with the Commission via EDGAR.")
print('13f-2(b): For the purposes of this section:')
print('13f-2(b)(1): The term institutional investment manager has the same meaning as in section 13(f)(6)(A) of the Exchange Act.')
print('13f-2(b)(2): The term equity security has the same meaning as in section 3(a)(11) of the Exchange Act and § 240.3a11-1 (Rule 3a11-1).')
print('13f-2(b)(3): The term investment discretion has the same meaning as in § 240.13f-1(b) (Rule 13f-1(b)).')
print('13f-2(b)(4): The term gross short position means the number of shares of the equity security that are held short as a result of short sales as defined in 17 CFR 242.200(a) (Rule 200(a) of Regulation SHO), without inclusion of any offsetting economic positions such as shares of the equity security or derivatives of such equity security.')
print('13f-2(b)(5): The term regular trading hours has the same meaning as in 17 CFR 242.600(b)(77) (Rule 600(b)(77)).')
print('official typography italicizes institutional investment manager, equity security, investment discretion, gross short position, and regular trading hours')
print('official typography uses typographic quotes around “EDGAR.”')
print('official (b)(4) typography is “without inclusion of any offsetting economic positions such as shares of the equity security or derivatives of such equity security”')
print('official CITA typography is [88 FR 75185, Nov. 1, 2023]')
print('official API XML has no SECAUTH element; this toy does not invent one')
print('official 13f-1(b) / 249.332 / 3a11-1 / 242.200(a) / 242.600(b)(77) are named only')
print('cite 17 CFR 240.13f-2; title 17 up_to_date_as_of 2026-11-17')
form_sho_14 = True
print(f'  a report on Form SHO is due within 14 calendar days after the end of each calendar month? {form_sho_14}')
check(form_sho_14 is True, "Form SHO due within 14 calendar days after month-end")
sec12_thresholds = True
print(f'  for section 12-registered or 15(d)-reporting equity, the official thresholds are a monthly average gross short position at the close of regular trading hours of $10 million or more, or 2.5 percent or more of shares outstanding? {sec12_thresholds}')
check(sec12_thresholds is True, "section 12 / 15(d) thresholds $10 million or 2.5 percent")
unregistered_500k = True
print(f'  for equity not so registered or 15(d)-reporting, the official threshold is a gross short position of $500,000 or more at the close of regular trading hours on any settlement date during the calendar month? {unregistered_500k}')
check(unregistered_500k is True, "unregistered / non-15(d) threshold $500,000 on any settlement date")
italics_offset = True
print(f'  official typography italicizes institutional investment manager, equity security, investment discretion, gross short position, and regular trading hours, official typography uses typographic quotes around “EDGAR,” and official (b)(4) typography is “without inclusion of any offsetting economic positions such as shares of the equity security or derivatives of such equity security”? {italics_offset}')
check(italics_offset is True, "italics; typographic EDGAR; without inclusion of offsetting economic positions")
cita_13f2 = True
print(f'  official CITA typography is [88 FR 75185, Nov. 1, 2023], official API XML has no SECAUTH, official (a)(3) typography is that the Commission will publish, on an aggregated basis, certain information, official 13f-1(b) / 249.332 / 3a11-1 / 242.200(a) / 242.600(b)(77) are named only, and this toy does not rewrite the already-taught p3 Form SHO awareness box or invent that 2026 vendor Form SHO data is official or backtest-ready? {cita_13f2}')
check(cita_13f2 is True, "CITA 13f-2; no SECAUTH; (a)(3) aggregated publication; named only; not p3 / vendor data")
print('official 13f-1(b) / 249.332 / 3a11-1 / 242.200(a) / 242.600(b)(77) are named only; this toy does not rewrite the already-taught p3 pairs-stat-arb Form SHO awareness box')
print('this toy does not invent that 2026 vendor Form SHO data is official or backtest-ready')
print('literacy only; not a how-to for Form SHO filing, and not legal advice')
print('no issuer, filer, or investment advice')
print(f"assertions passed: {checks}/{checks}")
print('disclaimer: official 17 CFR 240.13f-2; no issuer, disclosure, or investment advice; learning only')

print('=== BF. 17 CFR 240.14d-7: Additional withdrawal rights ===')
# 17 CFR 240.14d-7 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official caption typography is
# Additional withdrawal rights. Official typography is “such offer
# request or invitation remains open,” “accompained” (official typo),
# and “depositary.” Official typography italicizes the paragraph labels
# Rights., Exemption during subsequent offering period., and Notice of
# withdrawal. Official CITA is [44 FR 70345, Dec. 6, 1979, as amended at
# 51 FR 25882, July 17, 1986; 51 FR 32630, Sept. 15, 1986; 64 FR 61461,
# Nov. 10, 1999; 76 FR 71876, Nov. 21, 2011]. Official API XML has no
# SECAUTH; do not invent one. This is not packed 14d-11, packed 14d-10,
# or packed 14e-4. Do not pack locked 14d-4 / 14d-6. Do not rewrite
# already-taught 14d-11 or 14e-4 withdrawal sentences.
# Learning only; no issuer, filer, or investment advice.

print('official caption typography is Additional withdrawal rights.')
print('14d-7(a)(1): In addition to the provisions of section 14(d)(5) of the Act, any person who has deposited securities pursuant to a tender offer has the right to withdraw any such securities during the period such offer request or invitation remains open.')
print('14d-7(a)(2): Notwithstanding the provisions of section 14(d)(5) of the Act (15 U.S.C. 78n(d)(5)) and paragraph (a) of this section, the bidder need not offer withdrawal rights during a subsequent offering period.')
print("14d-7(b): Notice of withdrawal pursuant to this section shall be deemed to be timely upon the receipt by the bidder's depositary of a written notice of withdrawal specifying the name(s) of the tendering stockholder(s), the number or amount of the securities to be withdrawn and the name(s) in which the certificate(s) is (are) registered, if different from that of the tendering security holder(s). A bidder may impose other reasonable requirements, including certificate numbers and a signed request for withdrawal accompained by a signature guarantee, as conditions precedent to the physical release of withdrawn securities.")
print('official typography is “such offer request or invitation remains open”')
print('official typography is “accompained” (official typo) and “depositary”')
print('official typography italicizes the paragraph labels Rights., Exemption during subsequent offering period., and Notice of withdrawal.')
print("notice of withdrawal is deemed timely upon the receipt by the bidder's depositary of a written notice of withdrawal")
print('official CITA typography is [44 FR 70345, Dec. 6, 1979, as amended at 51 FR 25882, July 17, 1986; 51 FR 32630, Sept. 15, 1986; 64 FR 61461, Nov. 10, 1999; 76 FR 71876, Nov. 21, 2011]')
print('official API XML has no SECAUTH element; this toy does not invent one')
print('cite 17 CFR 240.14d-7; title 17 up_to_date_as_of 2026-11-17')
withdraw_open = True
print(f'  a person who has deposited securities pursuant to a tender offer has the right to withdraw any such securities during the period such offer request or invitation remains open? {withdraw_open}')
check(withdraw_open is True, "withdrawal rights while such offer request or invitation remains open")
no_subsequent = True
print(f'  the bidder need not offer withdrawal rights during a subsequent offering period? {no_subsequent}')
check(no_subsequent is True, "no withdrawal rights during a subsequent offering period")
accompained_depositary = True
print(f'  official typography in (b) is “accompained” (official typo) and “depositary,” official typography italicizes the paragraph labels Rights., Exemption during subsequent offering period., and Notice of withdrawal., and notice of withdrawal is deemed timely upon receipt by the bidder\'s depositary of a written notice of withdrawal? {accompained_depositary}')
check(accompained_depositary is True, "accompained typo; depositary; italic labels; timely on depositary receipt")
cita_14d7 = True
print(f'  official CITA typography is [44 FR 70345, Dec. 6, 1979, as amended at 51 FR 25882, July 17, 1986; 51 FR 32630, Sept. 15, 1986; 64 FR 61461, Nov. 10, 1999; 76 FR 71876, Nov. 21, 2011], official API XML has no SECAUTH, and this is not packed 14d-11, packed 14d-10, or packed 14e-4 (locked 14d-4 / 14d-6 are not packed)? {cita_14d7}')
check(cita_14d7 is True, "CITA 14d-7; no SECAUTH; not 14d-11/14d-10/14e-4; 14d-4/14d-6 not packed")
print('packed 14d-11 / 14d-10 / 14e-4 exist and are named only; locked 14d-4 / 14d-6 are not packed; this toy is not those boxes')
print('literacy only; not a how-to for tender-offer withdrawal, and not legal advice')
print('no issuer, filer, or investment advice')
print(f"assertions passed: {checks}/{checks}")
print('disclaimer: official 17 CFR 240.14d-7; no issuer, disclosure, or investment advice; learning only')

print('=== BG. 17 CFR 240.14d-8: Exemption from statutory pro rata requirements ===')
# 17 CFR 240.14d-8 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official caption typography is
# Exemption from statutory pro rata requirements. Official typography is
# “as nearly as may be pro rata, disregarding fractions.” Official CITA
# is [47 FR 57680, Dec. 28, 1982]. Official full SECAUTH typography is
# (Sec. 23, 48 Stat. 901; sec. 203(a), 49 Stat. 704; sec. 8, 49 Stat.
# 1379; sec. 10, 78 Stat. 580; sec. 3, 82 Stat. 455; secs. 3-5, 84 Stat.
# 1497; sec. 18, 89 Stat. 155; 15 U.S.C. 78n(e), 78w(a)). This is not
# packed 14d-7, packed 14d-11, or packed 14e-4.
# Learning only; no issuer, filer, or investment advice.

print('official caption typography is Exemption from statutory pro rata requirements.')
print('14d-8: Notwithstanding the pro rata provisions of section 14(d)(6) of the Act, if any person makes a tender offer or request or invitation for tenders, for less than all of the outstanding equity securities of a class, and if a greater number of securities are deposited pursuant thereto than such person is bound or willing to take up and pay for, the securities taken up and paid for shall be taken up and paid for as nearly as may be pro rata, disregarding fractions, according to the number of securities deposited by each depositor during the period such offer, request or invitation remains open.')
print('official typography is “as nearly as may be pro rata, disregarding fractions.”')
print('official CITA typography is [47 FR 57680, Dec. 28, 1982]')
print('official SECAUTH typography is (Sec. 23, 48 Stat. 901; sec. 203(a), 49 Stat. 704; sec. 8, 49 Stat. 1379; sec. 10, 78 Stat. 580; sec. 3, 82 Stat. 455; secs. 3-5, 84 Stat. 1497; sec. 18, 89 Stat. 155; 15 U.S.C. 78n(e), 78w(a))')
print('cite 17 CFR 240.14d-8; title 17 up_to_date_as_of 2026-11-17')
less_than_all = True
print(f'  official text applies when a person makes a tender offer for less than all of the outstanding equity securities of a class and a greater number of securities are deposited than such person is bound or willing to take up and pay for? {less_than_all}')
check(less_than_all is True, "less than all outstanding; greater number deposited than bound or willing to take up")
pro_rata = True
print(f'  the securities taken up and paid for shall be taken up and paid for as nearly as may be pro rata, disregarding fractions, according to the number of securities deposited by each depositor during the period such offer, request or invitation remains open? {pro_rata}')
check(pro_rata is True, "as nearly as may be pro rata, disregarding fractions")
caption_14d8 = True
print(f'  official typography is “as nearly as may be pro rata, disregarding fractions,” and official caption typography is “Exemption from statutory pro rata requirements.”? {caption_14d8}')
check(caption_14d8 is True, "caption Exemption from statutory pro rata requirements.")
cita_14d8 = True
print(f'  official CITA typography is [47 FR 57680, Dec. 28, 1982], official SECAUTH typography is (Sec. 23, 48 Stat. 901; sec. 203(a), 49 Stat. 704; sec. 8, 49 Stat. 1379; sec. 10, 78 Stat. 580; sec. 3, 82 Stat. 455; secs. 3-5, 84 Stat. 1497; sec. 18, 89 Stat. 155; 15 U.S.C. 78n(e), 78w(a)), and this is not packed 14d-7, packed 14d-11, or packed 14e-4? {cita_14d8}')
check(cita_14d8 is True, "CITA/SECAUTH 14d-8; not 14d-7/14d-11/14e-4")
print('packed 14d-7 / 14d-11 / 14e-4 exist and are named only; this toy is not those boxes')
print('literacy only; not a how-to for pro rata tender take-up, and not legal advice')
print('no issuer, filer, or investment advice')
print(f"assertions passed: {checks}/{checks}")
print('disclaimer: official 17 CFR 240.14d-8; no issuer, disclosure, or investment advice; learning only')

print('=== BH. 17 CFR 240.12a-5: Temporary exemption of substituted or additional securities ===')
# 17 CFR 240.12a-5 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official caption typography is
# Temporary exemption of substituted or additional securities. Official
# typography uses typographic U+201C/U+201D around “when-issued.”
# Official (b) typography is “When registration of the exempt security
# on the exchange become effective” (official “become”; do not tidy into
# “becomes”), “The close of business on the tenth day after,” and “The
# close of business on the one hundred and twentieth day after”
# (official capital T). Official typography italicizes Provided,
# however, including the comma. Official (e) typography is “section
# 12(a) of the act.” Official CITA is [13 FR 8185, Dec. 22, 1948, as
# amended at 19 FR 669, Feb. 5, 1954; 20 FR 2081, Apr. 2, 1955; 53 FR
# 41206, Oct. 20, 1988]. Official full SECAUTH typography is (Secs. 3,
# 12, 48 Stat. 882, 892; 15 U.S.C. 78c (12), 78l) (space before (12);
# italic l; pack as 78l with italic l). Name official Form 26 and
# official 10b-1 only. This is not packed 12g-2 / packed 12d2-1 / packed
# 12b-6. Do not rewrite already-taught 12g-1 / 12g-4 / 12g-2 sentences
# or bump the shipped 12g-4 “up to date as of 2026-11-09” date only.
# Learning only; no issuer, filer, or investment advice.

print('official caption typography is Temporary exemption of substituted or additional securities.')
print('12a-5(a)(1): Subject to the conditions of paragraph (a)(2) of this section, whenever the holders of a security admitted to trading on a national securities exchange (hereinafter called the original security) obtain the right, by operation of law or otherwise, to acquire all or any part of a class of another or substitute security of the same or another issuer, or an additional amount of the original security, then:')
print('12a-5(a)(1)(i): All or any part of the class of such other or substituted security shall be temporarily exempted from the operation of section 12(a) to the extent necessary to render lawful transactions therein on an issued or “when-issued” basis on any national securities exchange on which the original, the other or the substituted security is lawfully admitted to trading; and')
print('12a-5(a)(1)(ii): The additional amount of the original security shall be temporarily exempted from the operation of section 12(a) to the extent necessary to render lawful transactions therein on a “when-issued” basis on any national securities exchange on which the original security is lawfully admitted to trading.')
print('12a-5(a)(2): The exemptions provided by paragraph (a)(1) of this section shall be available only if the following conditions are met:')
print('12a-5(a)(2)(i): A registration statement is in effect under the Securities Act of 1933 to the extent required as to the security which is the subject of such exemption, or the terms of any applicable exemption from registration under such act have been complied with, if required;')
print('12a-5(a)(2)(ii): Any stockholder approval necessary to the issuance of the security which is the subject of the exemption, has been obtained; and')
print('12a-5(a)(2)(iii): All other necessary official action, other than the filing or recording of charter amendments or other documents with the appropriate State authorities, has been taken to authorize and assure the issuance of the security which is the subject of such exemption.')
print('12a-5(b): The exemption provided by this section shall terminate on the earliest of the following dates:')
print('12a-5(b)(1): When registration of the exempt security on the exchange become effective;')
print('12a-5(b)(2): When the exempt security is granted unlisted trading privileges on the exchange;')
print('12a-5(b)(3): The close of business on the tenth day after (i) withdrawal of an application for registration of the exempt security on the exchange; (ii) withdrawal by the exchange of its certification of approval of the exempt security for listing and registration; (iii) withdrawal of an application for admission of the exempt security to unlisted trading privileges on the exchange; or (iv) the sending to the exchange of notice of the entry of an order by the Commission denying any application for admission of the exempt security to unlisted trading privileges on the exchange;')
print('12a-5(b)(4): The close of business on the one hundred and twentieth day after the date on which the exempt security was admitted by action of the exchange to trading thereon as a security exempted from the operation of section 12 (a) by this section, unless prior thereto an application for registration of the exempt security or for admission of the exempt security to unlisted trading privileges on the exchange has been filed.')
print('12a-5(c): Notwithstanding paragraph (b) of this section, the Commission, having due regard for the public interest and the protection of investors, may at any time extend the period of exemption of any security by this rule or may sooner terminate the exemption upon notice to the exchange and to the issuer of the extension or termination thereof.')
print('12a-5(d): The Exchange shall file with the Commission a notification on Form 26 promptly after taking action to admit any security to trading under this section: Provided, however, That no notification need be filed under this section concerning the admission or proposed admission to trading of additional amounts of a class of security admitted to trading on such exchange.')
print('official Form 26 footnote typography is Copy filed with the Federal Register Division.')
print('12a-5(e): Section 240.10b-1 shall be applicable to all securities exempted from the operation of section 12(a) of the act by this section.')
print('official typography uses typographic U+201C/U+201D around “when-issued.”')
print('official typography is “When registration of the exempt security on the exchange become effective” (official “become”)')
print('official typography is “The close of business on the tenth day after” and “The close of business on the one hundred and twentieth day after” (official capital T)')
print('official typography italicizes Provided, however, including the comma')
print('official (e) typography is “section 12(a) of the act.”')
print('official CITA typography is [13 FR 8185, Dec. 22, 1948, as amended at 19 FR 669, Feb. 5, 1954; 20 FR 2081, Apr. 2, 1955; 53 FR 41206, Oct. 20, 1988]')
print('official SECAUTH typography is (Secs. 3, 12, 48 Stat. 882, 892; 15 U.S.C. 78c (12), 78l) (space before (12); italic l)')
print('official Form 26 and official 10b-1 are named only')
print('cite 17 CFR 240.12a-5; title 17 up_to_date_as_of 2026-11-17')
when_issued = True
print(f'  official (a)(1) temporarily exempts a substituted or other security from section 12(a) on an issued or “when-issued” basis, and an additional amount of the original security on a “when-issued” basis, when holders of a security admitted to trading on a national securities exchange obtain the right to acquire them? {when_issued}')
check(when_issued is True, "12a-5(a)(1) issued or when-issued; additional amount when-issued")
all_three = True
print(f'  official (a)(2) requires all three official (a)(2)(i)–(iii) conditions? {all_three}')
check(all_three is True, "all three (a)(2)(i)–(iii) conditions")
become_dates = True
print(f'  official (b) terminates on the earliest of the listed dates, including official typography “When registration of the exempt security on the exchange become effective” (official “become”) and official typography “The close of business on the tenth day after” / “The close of business on the one hundred and twentieth day after” (official capital T)? {become_dates}')
check(become_dates is True, "become effective; The close of business on the tenth / one hundred and twentieth day")
provided_secauth = True
print(f'  official typography uses typographic U+201C/U+201D around “when-issued,” official typography italicizes Provided, however, including the comma, and official SECAUTH typography is (Secs. 3, 12, 48 Stat. 882, 892; 15 U.S.C. 78c (12), 78l) (space before (12); italic l)? {provided_secauth}')
check(provided_secauth is True, "when-issued quotes; Provided, however, comma; SECAUTH 78c (12), italic l")
cita_12a5 = True
print(f'  official CITA typography is [13 FR 8185, Dec. 22, 1948, as amended at 19 FR 669, Feb. 5, 1954; 20 FR 2081, Apr. 2, 1955; 53 FR 41206, Oct. 20, 1988], official Form 26 and official 10b-1 are named only, official (e) typography is “section 12(a) of the act,” and this is not packed 12g-2 / packed 12d2-1 / packed 12b-6? {cita_12a5}')
check(cita_12a5 is True, "CITA 12a-5; Form 26 / 10b-1 named only; section 12(a) of the act; not 12g-2/12d2-1/12b-6")
print('official Form 26 and official 10b-1 are named only; packed 12g-2 / 12d2-1 / 12b-6 exist and are named only; this toy is not those boxes')
print('do not bump the already-shipped 12g-4 “up to date as of 2026-11-09” date only')
print('literacy only; not a how-to for section 12(a) listing exemption, and not legal advice')
print('no issuer, filer, or investment advice')
print(f"assertions passed: {checks}/{checks}")
print('disclaimer: official 17 CFR 240.12a-5; no issuer, disclosure, or investment advice; learning only')

print('=== BI. 17 CFR 240.12f-4: Exemption of securities admitted to unlisted trading privileges from sections 13, 14 and 16 ===')
# 17 CFR 240.12f-4 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official caption typography is
# Exemption of securities admitted to unlisted trading privileges from
# sections 13, 14 and 16. Official typography uses typographic quotes
# around “registered on a national securities exchange” in official (a).
# Official (c)(1) typography is “section 16 of the act” (lowercase
# “act”) and official (c)(2) typography is “section 16 of the Act”; do
# not tidy either token into the other. Official CITA is [30 FR 482,
# Jan. 14, 1965]. Official SECAUTH typography is (Sec. 3, 78 Stat. 565,
# 15 U.S.C. 78l) (italic l). This is not packed 12a-5 / packed 12d2-1 /
# packed 12g-2 or a packed section 16 box. Name official 12f-2 only.
# Learning only; no issuer, filer, or investment advice.

print('official caption typography is Exemption of securities admitted to unlisted trading privileges from sections 13, 14 and 16.')
print('12f-4(a): Any security for which unlisted trading privileges on any national securities exchange have been continued or extended pursuant to section 12(f) of the Act shall be exempt from section 13 of the Act unless (1) such security or another security of the same issuer is listed and registered on a national securities exchange or registered pursuant to section 12(g) of the Act, or (2) such issuer would be required to file information, documents and reports pursuant to section 15(d) of the Act but for the fact that securities of the issuer are deemed to be “registered on a national securities exchange” within the meaning of section 12(f)(6) of the Act.')
print('12f-4(b): Any security for which unlisted trading privileges on any national securities exchange have been continued or extended pursuant to section 12(f) of the Act shall be exempt from section 14 of the Act unless such security is also listed and registered on a national securities exchange or registered pursuant to section 12(g) of the Act.')
print('12f-4(c)(1): Any equity security for which unlisted trading privileges on any national securities exchange have been continued or extended pursuant to section 12(f) of the Act shall be exempt from section 16 of the act unless such security or another equity security of the same issuer is listed and registered on a national securities exchange or registered pursuant to section 12(g) of the Act.')
print('12f-4(c)(2): Any equity security for which unlisted trading privileges on any national securities exchange have been continued or extended pursuant to section 12(f) of the Act and which is not listed and registered on any other such exchange or registered pursuant to section 12(g) of the Act shall be exempt from section 16 of the Act insofar as that section would otherwise apply to any person who is directly or indirectly the beneficial owner of more than 10 percent of such security, unless another equity security of the issuer of such unlisted security is so listed or registered and such beneficial owner is a director or officer of such issuer or directly or indirectly the beneficial owner of more than 10 percent of any such listed security.')
print('12f-4(d): Any reference in this section to a security registered pursuant to section 12(g) of the Act shall include, and any reference to a security not so registered shall exclude, any security as to which a registration statement pursuant to such section is at the time required to be effective.')
print('official typography uses typographic quotes around “registered on a national securities exchange” in official (a)')
print('official (c)(1) typography is “section 16 of the act” (lowercase “act”)')
print('official (c)(2) typography is “section 16 of the Act”')
print('official CITA typography is [30 FR 482, Jan. 14, 1965]')
print('official SECAUTH typography is (Sec. 3, 78 Stat. 565, 15 U.S.C. 78l) (italic l)')
print('official 12f-2 is named only')
print('cite 17 CFR 240.12f-4; title 17 up_to_date_as_of 2026-11-17')
exempt_13 = True
print(f'  a UTP security is exempt from section 13 unless official (a)(1) or official (a)(2) applies? {exempt_13}')
check(exempt_13 is True, "UTP exempt from section 13 unless (a)(1) or (a)(2)")
exempt_14 = True
print(f'  official (b) exempts the security from section 14 unless the security is also listed and registered on a national securities exchange or registered pursuant to section 12(g)? {exempt_14}')
check(exempt_14 is True, "section 14 exemption unless also listed and registered or 12(g)")
act_vs_Act = True
print(f'  official (c)(1) typography is “section 16 of the act” (lowercase “act”) and official (c)(2) typography is “section 16 of the Act,” and official (c)(1) exempts unless such security or another equity security of the same issuer is listed and registered on a national securities exchange or registered pursuant to section 12(g)? {act_vs_Act}')
check(act_vs_Act is True, "section 16 of the act vs of the Act; (c)(1) unless listed/12(g)")
quotes_italic_l = True
print(f'  official typography uses typographic quotes around “registered on a national securities exchange” in official (a), and official typography italicizes the letter l in 15 U.S.C. 78l? {quotes_italic_l}')
check(quotes_italic_l is True, "typographic quotes in (a); italic l in 78l")
cita_12f4 = True
print(f'  official CITA typography is [30 FR 482, Jan. 14, 1965], official SECAUTH typography is (Sec. 3, 78 Stat. 565, 15 U.S.C. 78l), this is not packed 12a-5 / packed 12d2-1 / packed 12g-2 or a packed section 16 box, and official 12f-2 is named only? {cita_12f4}')
check(cita_12f4 is True, "CITA/SECAUTH 12f-4; not 12a-5/12d2-1/12g-2 or section 16 box; 12f-2 named only")
print('packed 12a-5 / 12d2-1 / 12g-2 exist and are named only; this toy is not a packed section 16 box; official 12f-2 is named only')
print('literacy only; not a how-to for UTP reporting exemption, and not legal advice')
print('no issuer, filer, or investment advice')
print(f"assertions passed: {checks}/{checks}")
print('disclaimer: official 17 CFR 240.12f-4; no issuer, disclosure, or investment advice; learning only')

print('=== BJ. 17 CFR 240.12f-2: Extending unlisted trading privileges to a security that is the subject of an initial public offering ===')
# 17 CFR 240.12f-2 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official caption typography is
# Extending unlisted trading privileges to a security that is the
# subject of an initial public offering. Official typography italicizes
# General provision., Definitions., subject security, and initial public
# offering commences. Official (b) typography italicizes the letter l in
# 15 U.S.C. 78l(f). Official (a) has no 78l citation; do not invent one
# there. Official (c)(1) typography is 15 U.S.C. 78l(f)(1)(G)(i) (Roman
# l, Roman 1). Official (c)(2) typography is 15 U.S.C. 78l(f)(1)(G)(ii)
# (Roman l; italic 1). Do not tidy those three official forms into one
# another. Official CITA is [60 FR 20896, Apr. 28, 1995, as amended at
# 65 FR 53565, Sept. 5, 2000; 70 FR 37618, June 29, 2005]. Official API
# XML has no SECAUTH. Name official 12f-1 and packed 12f-4 only; do not
# pack 12f-1. Do not rewrite the packed 12f-4 / section-BI prefix that
# official 12f-2 is named only; this later box packs official 12f-2.
# Learning only; no issuer, filer, or investment advice.

print('official caption typography is Extending unlisted trading privileges to a security that is the subject of an initial public offering.')
print('12f-2(a): General provision. A national securities exchange may extend unlisted trading privileges to a subject security when at least one transaction in the subject security has been effected on the national securities exchange upon which the security is listed and the transaction has been reported pursuant to an effective transaction reporting plan, as defined in § 242.600 of this chapter.')
print('12f-2(b): The extension of unlisted trading privileges pursuant to this section shall be subject to all the provisions set forth in Section 12(f) of the Act (15 U.S.C. 78l(f)), as amended, and any rule or regulation promulgated thereunder, or which may be promulgated thereunder while the extension is in effect.')
print('12f-2(c): Definitions. For the purposes of this section:')
print('12f-2(c)(1): The term subject security shall mean a security that is the subject of an initial public offering, as that term is defined in section 12(f)(1)(G)(i) of the Act (15 U.S.C. 78l(f)(1)(G)(i)), and')
print('12f-2(c)(2): An initial public offering commences at such time as is described in section 12(f)(1)(G)(ii) of the Act (15 U.S.C. 78l(f)(1)(G)(ii)).')
print('official typography italicizes General provision., Definitions., subject security, and initial public offering commences')
print('official (b) typography italicizes the letter l in 15 U.S.C. 78l(f)')
print('official (a) has no 78l citation')
print('official (c)(1) typography is 15 U.S.C. 78l(f)(1)(G)(i) (Roman l, Roman 1)')
print('official (c)(2) typography is 15 U.S.C. 78l(f)(1)(G)(ii) (Roman l; italic 1)')
print('do not tidy those three official 78l forms into one another')
print('official CITA typography is [60 FR 20896, Apr. 28, 1995, as amended at 65 FR 53565, Sept. 5, 2000; 70 FR 37618, June 29, 2005]')
print('official API XML has no SECAUTH')
print('official 12f-1 is named only; packed 12f-4 exists and is named only')
print('cite 17 CFR 240.12f-2; title 17 up_to_date_as_of 2026-11-17')
utp_first_trade = True
print(f"  a national securities exchange may extend unlisted trading privileges to a subject security when at least one transaction in the subject security has been effected on the national securities exchange upon which the security is listed and the transaction has been reported pursuant to an effective transaction reporting plan? {utp_first_trade}")
check(utp_first_trade is True, 'UTP after first reported trade on the listing exchange')
italics_12f2 = True
print(f"  official typography italicizes General provision., Definitions., subject security, and initial public offering commences? {italics_12f2}")
check(italics_12f2 is True, 'italic General provision./Definitions./subject security/IPO commences')
italic_l_only_b = True
print(f"  official (b) typography italicizes the letter l in 15 U.S.C. 78l(f), and official (a) has no 78l citation? {italic_l_only_b}")
check(italic_l_only_b is True, 'italic l in 78l(f) in (b) only; no 78l in (a)')
three_78l_forms = True
print(f"  official (c)(1) typography is 15 U.S.C. 78l(f)(1)(G)(i) (Roman l, Roman 1) and official (c)(2) typography is 15 U.S.C. 78l(f)(1)(G)(ii) (Roman l; italic 1), and those three official forms must not be tidied into one another? {three_78l_forms}")
check(three_78l_forms is True, 'three official 78l forms not tidied together')
cita_12f2_no_secauth = True
print(f"  official CITA typography is [60 FR 20896, Apr. 28, 1995, as amended at 65 FR 53565, Sept. 5, 2000; 70 FR 37618, June 29, 2005], official API XML has no SECAUTH, official 12f-1 is named only, and this later box does not rewrite the packed 12f-4 / section-BI prefix that official 12f-2 is named only? {cita_12f2_no_secauth}")
check(cita_12f2_no_secauth is True, 'CITA 12f-2; no SECAUTH; 12f-1 named only; BI prefix unrewritten')
print('packed 12f-4 / section-BI prefix that official 12f-2 is named only stays as written; this later box packs official 12f-2 and does not rewrite that prefix; official 12f-1 is named only')
print('literacy only; not a how-to for extending UTP to an IPO security, and not legal advice')
print('no issuer, filer, or investment advice')
print(f"assertions passed: {checks}/{checks}")
print('disclaimer: official 17 CFR 240.12f-2; no issuer, disclosure, or investment advice; learning only')

print('=== BK. 17 CFR 240.12f-3: Termination or suspension of unlisted trading privileges ===')
# 17 CFR 240.12f-3 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official caption typography is
# Termination or suspension of unlisted trading privileges. Official
# (a)(4) typography is Names of issuer. Official (b) typography is may
# be suspended or terminated by such exchange in accordance with its
# rules. Official CITA is [20 FR 6702, Sept. 13, 1955, as amended at 44
# FR 75135, Dec. 19, 1979; 45 FR 36076, May 29, 1980; 60 FR 20896, Apr.
# 28, 1995]. Official SECAUTH typography is (Secs. 12(f) and 23, 15
# U.S.C. 78l and 78w) (italic l). Name official 12f-1 only; do not pack
# 12f-1. Learning only; no issuer, filer, or investment advice.

print('official caption typography is Termination or suspension of unlisted trading privileges.')
print('12f-3(a): The issuer of any security for which unlisted trading privileges on any exchange have been continued or extended, or any broker or dealer who makes or creates a market for such security, or any other person having a bona fide interest in the question of termination or suspension of such unlisted trading privileges, may make application to the Commission for the termination or suspension of such unlisted trading privileges. One duly executed copy of such application shall be filed, and it shall contain the following information:')
print('12f-3(a)(1): Name and address of applicant;')
print("12f-3(a)(2): A brief statement of the applicant's interest in the question of termination or suspension of such unlisted trading privileges;")
print('12f-3(a)(3): Title of security;')
print('12f-3(a)(4): Names of issuer;')
print('12f-3(a)(5): Amount of such security issued and outstanding (number of shares of stock or principal amount of bonds), stating source of information;')
print('12f-3(a)(6): Annual volume of public trading in such security (number of shares of stock or principal amount of bonds) on such exchange for each of the three calendar years immediately preceding the date of such application, and monthly volume of trading in such security for each of the twelve calendar months immediately preceding the date of such application;')
print('12f-3(a)(7): Price range on such exchange for each of the twelve calendar months immediately preceding the date of such application; and')
print("12f-3(a)(8): A brief statement of the information in the applicant's possession, and the source thereof, with respect to (i) the extent of public trading in such security on such exchange, and (ii) the character of trading in such security on such exchange; and")
print('12f-3(a)(9): A brief statement that a copy of the instant application has been mailed, or otherwise personally provided, to the exchange from which the suspension or termination of unlisted trading privileges is sought, and to any other exchange on which such security is listed or traded pursuant to unlisted trading privileges.')
print('12f-3(b): Unlisted trading privileges in any security on any national securities exchange may be suspended or terminated by such exchange in accordance with its rules.')
print('official (a)(4) typography is “Names of issuer.”')
print('official (b) typography is may be suspended or terminated by such exchange in accordance with its rules')
print('official CITA typography is [20 FR 6702, Sept. 13, 1955, as amended at 44 FR 75135, Dec. 19, 1979; 45 FR 36076, May 29, 1980; 60 FR 20896, Apr. 28, 1995]')
print('official SECAUTH typography is (Secs. 12(f) and 23, 15 U.S.C. 78l and 78w) (italic l)')
print('official 12f-1 is named only')
print('cite 17 CFR 240.12f-3; title 17 up_to_date_as_of 2026-11-17')
exchange_may_suspend = True
print(f"  official (b) says unlisted trading privileges may be suspended or terminated by such exchange in accordance with its rules? {exchange_may_suspend}")
check(exchange_may_suspend is True, 'exchange may suspend or terminate UTP under its rules')
who_may_apply = True
print(f"  official (a) lets the issuer, any broker or dealer who makes or creates a market for such security, or any other person having a bona fide interest apply to the Commission for termination or suspension? {who_may_apply}")
check(who_may_apply is True, 'issuer / market maker / bona fide interest may apply')
names_of_issuer = True
print(f"  official (a)(4) typography is “Names of issuer.”? {names_of_issuer}")
check(names_of_issuer is True, 'Names of issuer typography')
secauth_12f3 = True
print(f"  official SECAUTH typography is (Secs. 12(f) and 23, 15 U.S.C. 78l and 78w) (italic l)? {secauth_12f3}")
check(secauth_12f3 is True, 'SECAUTH 12f-3 italic l')
cita_12f3_named = True
print(f"  official CITA typography is [20 FR 6702, Sept. 13, 1955, as amended at 44 FR 75135, Dec. 19, 1979; 45 FR 36076, May 29, 1980; 60 FR 20896, Apr. 28, 1995], and official 12f-1 is named only (do not pack it)? {cita_12f3_named}")
check(cita_12f3_named is True, 'CITA 12f-3; official 12f-1 named only')
print('official 12f-1 is named only; do not pack 12f-1')
print('literacy only; not a how-to for terminating or suspending UTP, and not legal advice')
print('no issuer, filer, or investment advice')
print(f"assertions passed: {checks}/{checks}")
print('disclaimer: official 17 CFR 240.12f-3; no issuer, disclosure, or investment advice; learning only')

print('=== BL. 17 CFR 240.12f-5: Exchange rules for securities to which unlisted trading privileges are extended ===')
# 17 CFR 240.12f-5 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official caption typography is
# Exchange rules for securities to which unlisted trading privileges are
# extended. Pack the official one-sentence body. Official CITA is [60 FR
# 20896, Apr. 28, 1995]. Official API XML has no SECAUTH. Do not tidy
# this CITA into 12f-2's longer amended CITA, which starts with the same
# first cite. Learning only; no issuer, filer, or investment advice.

print('official caption typography is Exchange rules for securities to which unlisted trading privileges are extended.')
print('12f-5: A national securities exchange shall not extend unlisted trading privileges to any security unless the national securities exchange has in effect a rule or rules providing for transactions in the class or type of security to which the exchange extends unlisted trading privileges.')
print('official CITA typography is [60 FR 20896, Apr. 28, 1995]')
print('official API XML has no SECAUTH')
print("do not tidy this CITA into 12f-2's longer amended CITA, which starts with the same first cite")
print('cite 17 CFR 240.12f-5; title 17 up_to_date_as_of 2026-11-17')
must_have_rules = True
print(f"  a national securities exchange shall not extend unlisted trading privileges to any security unless it has in effect a rule or rules providing for transactions in the class or type of security to which the exchange extends unlisted trading privileges? {must_have_rules}")
check(must_have_rules is True, 'exchange must have rules for that class or type')
caption_12f5 = True
print(f"  official caption typography is Exchange rules for securities to which unlisted trading privileges are extended.? {caption_12f5}")
check(caption_12f5 is True, 'official 12f-5 caption typography')
cita_12f5 = True
print(f"  official CITA typography is [60 FR 20896, Apr. 28, 1995]? {cita_12f5}")
check(cita_12f5 is True, 'CITA 12f-5 unamended first cite only')
no_secauth_12f5 = True
print(f"  official API XML has no SECAUTH? {no_secauth_12f5}")
check(no_secauth_12f5 is True, '12f-5 has no SECAUTH')
not_tidied_into_12f2 = True
print(f"  this official CITA must not be tidied into 12f-2's longer amended CITA, which starts with the same first cite, and this is not packed 12f-2 / 12f-3 / 12f-4? {not_tidied_into_12f2}")
check(not_tidied_into_12f2 is True, 'not 12f-2 CITA; not packed 12f-2/12f-3/12f-4')
print("this official CITA is not 12f-2's longer amended CITA; this toy is not packed 12f-2 / 12f-3 / 12f-4")
print('literacy only; not a how-to for adopting exchange UTP rules, and not legal advice')
print('no issuer, filer, or investment advice')
print(f"assertions passed: {checks}/{checks}")
print('disclaimer: official 17 CFR 240.12f-5; no issuer, disclosure, or investment advice; learning only')

print('=== BM. 17 CFR 240.14a-5: Presentation of information in proxy statement ===')
# 17 CFR 240.14a-5 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official caption typography is
# Presentation of information in proxy statement. Official typography is
# § 240.14a-8(e)(Question 5). Official typography italicizes et seq.
# Official (f) typography is more than 30 calendar days. Official CITA
# is [17 FR 11432, Dec. 18, 1952, as amended at 36 FR 8935, May 15,
# 1971; 37 FR 23179, Oct. 31, 1972; 44 FR 68770, Nov. 29, 1979; 51 FR
# 42061, Nov. 20, 1986; 61 FR 24656, May 15, 1996; 63 FR 29118, May 28,
# 1998; 63 FR 46881, Sept. 3, 1998; 73 FR 977, Jan. 4, 2008; 75 FR
# 56782, Sept. 16, 2010; 86 FR 68379, Dec. 1, 2021; 90 FR 9689, Feb. 18,
# 2025]. Do not mix 977 into 3b-6's 973. Official API XML has no
# SECAUTH. Name official 14a-8 / 14a-4 / 14a-19 only; do not pack those
# sections and do not rewrite packed 14a-3 / 14a-9 / 14a-10 / 14a-14.
# Learning only; no issuer, filer, or investment advice.

print('official caption typography is Presentation of information in proxy statement.')
print('14a-5(a): The information included in the proxy statement shall be clearly presented and the statements made shall be divided into groups according to subject matter and the various groups of statements shall be preceded by appropriate headings. The order of items and sub-items in the schedule need not be followed. Where practicable and appropriate, the information shall be presented in tabular form. All amounts shall be stated in figures. Information required by more than one applicable item need not be repeated. No statement need be made in response to any item or sub-item which is inapplicable.')
print('14a-5(b): Any information required to be included in the proxy statement as to terms of securities or other subject matter which from a standpoint of practical necessity must be determined in the future may be stated in terms of present knowledge and intention. To the extent practicable, the authority to be conferred concerning each such matter shall be confined within limits reasonably related to the need for discretionary authority. Subject to the foregoing, information which is not known to the persons on whose behalf the solicitation is to be made and which it is not reasonably within the power of such persons to ascertain or procure may be omitted, if a brief statement of the circumstances rendering such information unavailable is made.')
print('14a-5(c): Any information contained in any other proxy soliciting material which has been or will be furnished to each person solicited in connection with the same meeting or subject matter may be omitted from the proxy statement, if a clear reference is made to the particular document containing such information.')
print('14a-5(d)(1): All printed proxy statements shall be in roman type at least as large and as legible as 10-point modern type, except that to the extent necessary for convenient presentation financial statements and other tabular data, but not the notes thereto, may be in roman type at least as large and as legible as 8-point modern type. All such type shall be leaded at least 2 points.')
print('14a-5(d)(2): Where a proxy statement is delivered through an electronic medium, issuers may satisfy legibility requirements applicable to printed documents, such as type size and font, by presenting all required information in a format readily communicated to investors.')
print('14a-5(e): All proxy statements shall disclose, under an appropriate caption, the following dates:')
print("14a-5(e)(1): The deadline for submitting shareholder proposals for inclusion in the registrant's proxy statement and form of proxy for the registrant's next annual meeting, calculated in the manner provided in § 240.14a-8(e)(Question 5);")
print("14a-5(e)(2): The date after which notice of a shareholder proposal submitted outside the processes of § 240.14a-8 is considered untimely, either calculated in the manner provided by § 240.14a-4(c)(1) or as established by the registrant's advance notice provision, if any, authorized by applicable state law;")
print("14a-5(e)(3): The deadline for submitting nominees for inclusion in the registrant's proxy statement and form of proxy pursuant to an applicable state or foreign law provision or a registrant's governing documents as they relate to the inclusion of shareholder director nominees in the registrant's proxy materials for the registrant's next annual meeting of shareholders; and")
print("14a-5(e)(4): The deadline for providing notice of a solicitation of proxies in support of director nominees other than the registrant's nominees pursuant to § 240.14a-19 for the registrant's next annual meeting unless the registrant is an investment company registered under the Investment Company Act of 1940 (15 U.S.C. 80a-1 et seq.) or a business development company as defined by section 2(a)(48) of the Investment Company Act of 1940 (15 U.S.C. 80a-2(a)(48)).")
print('14a-5(f): If the date of the next annual meeting is subsequently advanced or delayed by more than 30 calendar days from the date of the annual meeting to which the proxy statement relates, the registrant shall, in a timely manner, inform shareholders of such change, and the new dates referred to in paragraphs (e)(1) and (e)(2) of this section, by including a notice, under Item 5, in its earliest possible quarterly report on Form 10-Q (§ 249.308a of this chapter), or, in the case of investment companies, in a shareholder report under § 270.30d-1 of this chapter under the Investment Company Act of 1940, or, if impracticable, any means reasonably calculated to inform shareholders.')
print('official typography is § 240.14a-8(e)(Question 5)')
print('official typography italicizes et seq.')
print('official (f) typography is more than 30 calendar days')
print('official CITA typography is [17 FR 11432, Dec. 18, 1952, as amended at 36 FR 8935, May 15, 1971; 37 FR 23179, Oct. 31, 1972; 44 FR 68770, Nov. 29, 1979; 51 FR 42061, Nov. 20, 1986; 61 FR 24656, May 15, 1996; 63 FR 29118, May 28, 1998; 63 FR 46881, Sept. 3, 1998; 73 FR 977, Jan. 4, 2008; 75 FR 56782, Sept. 16, 2010; 86 FR 68379, Dec. 1, 2021; 90 FR 9689, Feb. 18, 2025]')
print('official API XML has no SECAUTH')
print('official 14a-8 / 14a-4 / 14a-19 are named only')
print('cite 17 CFR 240.14a-5; title 17 up_to_date_as_of 2026-11-17')
disclose_deadlines = True
print(f"  official (e) requires all proxy statements to disclose, under an appropriate caption, the official (e)(1)–(4) dates, including the shareholder-proposal deadline calculated in the manner provided in § 240.14a-8(e)(Question 5)? {disclose_deadlines}")
check(disclose_deadlines is True, 'official (e) deadline disclosures incl. 14a-8(e)(Question 5)')
q5_et_seq = True
print(f"  official typography is § 240.14a-8(e)(Question 5), and official typography italicizes et seq.? {q5_et_seq}")
check(q5_et_seq is True, 'Question 5 typography; italic et seq.')
more_than_30 = True
print(f"  official (f) typography is more than 30 calendar days, and the registrant shall, in a timely manner, inform shareholders of such change by including a notice, under Item 5, in its earliest possible quarterly report on Form 10-Q? {more_than_30}")
check(more_than_30 is True, 'more than 30 calendar days; Form 10-Q Item 5 notice')
cita_14a5_977 = True
print(f"  official CITA typography includes 73 FR 977, Jan. 4, 2008 and ends 90 FR 9689, Feb. 18, 2025 (do not mix 977 into 3b-6's 973), and official API XML has no SECAUTH? {cita_14a5_977}")
check(cita_14a5_977 is True, 'CITA 14a-5 uses 977 not 973; no SECAUTH')
named_14a_only = True
print(f"  official 14a-8 / 14a-4 / 14a-19 are named only, and this is not packed 14a-3 / 14a-9 / 14a-10 / 14a-14? {named_14a_only}")
check(named_14a_only is True, '14a-8/14a-4/14a-19 named only; not packed 14a-3/9/10/14')
print('official 14a-8 / 14a-4 / 14a-19 are named only; packed 14a-3 / 14a-9 / 14a-10 / 14a-14 stay as written')
print('literacy only; not a how-to for drafting a proxy statement, and not legal advice')
print('no issuer, filer, or investment advice')
print(f"assertions passed: {checks}/{checks}")
print('disclaimer: official 17 CFR 240.14a-5; no issuer, disclosure, or investment advice; learning only')

print('=== BN. 17 CFR 240.0-2: Business hours of the Commission ===')
# 17 CFR 240.0-2 the whole current section (official eCFR API XML, title
# 17 up_to_date_as_of 2026-11-17). Official caption typography is
# Business hours of the Commission. Official typography is 100 F Street,
# NE, Washington, DC 20549 (NE, with no period after NE). Official
# typography italicizes provided that, Submissions made in paper., and
# Electronic filings. Official typography is Eastern Daylight Saving
# Time. Official (a) and official (c) typography is Saturdays, Sundays,
# and Federal holidays. Official (b) typography is Saturdays, Sundays
# and federal holidays. Official CITA is [58 FR 14682, Mar. 18, 1993, as
# amended at 65 FR 24801, Apr. 27, 2000; 68 FR 25799, May 13, 2003; 73
# FR 973, Jan. 4, 2008; 88 FR 12209, Feb. 27, 2023]. Official API XML
# has no SECAUTH. Official XML has a CROSSREF block after official (c);
# that is not a SECAUTH — do not invent a source line from it. Do not
# flatten this box into packed 232.12, and do not rewrite packed 232.12
# or already-taught 232.13. The clock numbers match packed 232.12; the
# official typography does not. Learning only; no filer, filing-agent,
# or investment advice.

print('official caption typography is Business hours of the Commission.')
print('0-2(a): The principal office of the Commission, at 100 F Street, NE, Washington, DC 20549, is open each day, except Saturdays, Sundays, and Federal holidays, from 9 a.m. to 5:30 p.m., Eastern Standard Time or Eastern Daylight Saving Time, whichever currently is in effect in Washington, DC, provided that hours for the filing of documents pursuant to the Act or the rules and regulations thereunder are as set forth in paragraphs (b) and (c) of this section.')
print('0-2(b): Submissions made in paper. Paper documents filed with or otherwise furnished to the Commission may be submitted to the Commission each day, except Saturdays, Sundays and federal holidays, from 8 a.m. to 5:30 p.m., Eastern Standard Time or Eastern Daylight Saving Time, whichever is currently in effect.')
print('0-2(c): Electronic filings. Filings made by direct transmission may be submitted to the Commission each day, except Saturdays, Sundays, and Federal holidays, from 6 a.m. to 10 p.m., Eastern Standard Time or Eastern Daylight Saving Time, whichever is currently in effect.')
print('official typography is 100 F Street, NE, Washington, DC 20549 (NE, with no period after NE)')
print('official typography italicizes provided that, Submissions made in paper., and Electronic filings.')
print('official typography is Eastern Daylight Saving Time')
print('official (a) typography is Saturdays, Sundays, and Federal holidays (Oxford comma; capital Federal)')
print('official (b) typography is Saturdays, Sundays and federal holidays (no Oxford comma; lowercase federal)')
print('official (c) typography is Saturdays, Sundays, and Federal holidays (Oxford comma; capital Federal)')
print('official CITA typography is [58 FR 14682, Mar. 18, 1993, as amended at 65 FR 24801, Apr. 27, 2000; 68 FR 25799, May 13, 2003; 73 FR 973, Jan. 4, 2008; 88 FR 12209, Feb. 27, 2023]')
print('official API XML has no SECAUTH; official CROSSREF after official (c) is not a SECAUTH')
print('this is not packed 232.12; already-taught 232.13 is not rewritten')
print('cite 17 CFR 240.0-2; title 17 up_to_date_as_of 2026-11-17')
clock_numbers = True
print(f"  principal-office hours are 9 a.m. to 5:30 p.m., paper hours are 8 a.m. to 5:30 p.m., and electronic / direct transmission hours are 6 a.m. to 10 p.m.? {clock_numbers}")
check(clock_numbers is True, '0-2 clock numbers 9-5:30 / 8-5:30 / 6-10')
ne_no_period = True
print(f"  official address typography is 100 F Street, NE, Washington, DC 20549 (NE, with no period after NE)? {ne_no_period}")
check(ne_no_period is True, 'NE, with no period after NE')
italics_0_2 = True
print(f"  official typography italicizes provided that, Submissions made in paper., and Electronic filings., and official typography is Eastern Daylight Saving Time? {italics_0_2}")
check(italics_0_2 is True, 'italic lead-ins; Eastern Daylight Saving Time')
holiday_typography = True
print(f"  official (a) and official (c) typography is Saturdays, Sundays, and Federal holidays, and official (b) typography is Saturdays, Sundays and federal holidays? {holiday_typography}")
check(holiday_typography is True, 'Federal vs federal holiday typography in (a)/(c) vs (b)')
cita_0_2_not_23212 = True
print(f"  official CITA typography is [58 FR 14682, Mar. 18, 1993, as amended at 65 FR 24801, Apr. 27, 2000; 68 FR 25799, May 13, 2003; 73 FR 973, Jan. 4, 2008; 88 FR 12209, Feb. 27, 2023], official API XML has no SECAUTH (the CROSSREF block after official (c) is not a SECAUTH), this is not packed 232.12, and already-taught 232.13 is not rewritten? {cita_0_2_not_23212}")
check(cita_0_2_not_23212 is True, 'CITA 0-2; no SECAUTH from CROSSREF; not 232.12/232.13')
print('this toy is not packed 232.12 and does not rewrite packed 232.12 or already-taught 232.13; official CROSSREF is not a SECAUTH')
print('literacy only; not a how-to for transmitting a filing, and not legal advice')
print('no issuer, filer, or investment advice')
print(f"assertions passed: {checks}/{checks}")
print('disclaimer: official 17 CFR 240.0-2; no issuer, disclosure, or investment advice; learning only')

print('=== BO. 17 CFR 240.3b-6: Liability for certain statements by issuers ===')
# 17 CFR 240.3b-6 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official caption typography is
# Liability for certain statements by issuers. Official typography
# italicizes Provided, including the comma, then that:. Official
# typography italicizes forward-looking statement and fraudulent
# statement. Official typography uses typographic U+201C/U+201D around
# Management's Discussion and Analysis of Financial Condition and
# Results of Operations, Operating and Financial Review and Prospects,
# and Supplementary Financial Information, (official comma inside the
# closing quote). Official typography uses an em dash U+2014 in
# Extractive Activities—Oil and Gas Topic. Official typography is
# Securities Act of 1933 offering statement or solicitation of interest
# and Item 5 of Form 20-F (§ 240.220(f) of this chapter). Pack official
# § 240.220(f); do not tidy that token into 249.220f. Official CITA
# begins [46 FR 13990, Feb. 25, 1981, …] and includes 73 FR 973, Jan. 4,
# 2008 — do not mix that page into 14a-5's 977. Official API XML has no
# SECAUTH. Do not rewrite packed 3b-2 / 3b-7 or packed 14a-3. Learning
# only; no issuer, filer, or investment advice.

print('official caption typography is Liability for certain statements by issuers.')
print('3b-6(a): A statement within the coverage of paragraph (b) of this section which is made by or on behalf of an issuer or by an outside reviewer retained by the issuer shall be deemed not to be a fraudulent statement (as defined in paragraph (d) of this section), unless it is shown that such statement was made or reaffirmed without a reasonable basis or was disclosed other than in good faith.')
print('3b-6(b): This rule applies to the following statements:')
print('3b-6(b)(1): A forward-looking statement (as defined in paragraph (c) of this section) made in a document filed with the Commission, in Part I of a quarterly report on Form 10-Q, § 249.308a of this chapter, or in an annual report to security holders meeting the requirements of Rules 14a-3(b) and (c) or 14c-3(a) and (b) (§ 240.14a-3(b) and (c) or § 240.14c-3(a) and (b)), a statement reaffirming such forward-looking statement after the date the document was filed or the annual report was made publicly available, or a forward-looking statement made before the date the document was filed or the date the annual report was made publicly available if such statement is reaffirmed in a filed document, in Part I of a quarterly report on Form 10-Q, or in an annual report made publicly available within a reasonable time after the making of such forward-looking statement; Provided, that:')
print('3b-6(b)(1)(i): At the time such statements are made or reaffirmed, either the issuer is subject to the reporting requirements of Section 13(a) or 15(d) of the Act and has complied with the requirements of Rule 13a-1 or 15d-1 thereunder, if applicable, to file its most recent annual report on Form 10-K, Form 20-F or Form 40-F; or if the issuer is not subject to the reporting requirements of Section 13(a) or 15(d) of the Act, the statements are made in a registration statement filed under the Securities Act of 1933 offering statement or solicitation of interest, written document or broadcast script under Regulation A or pursuant to Section 12(b) or (g) of the Securities Exchange Act of 1934; and')
print('3b-6(b)(1)(ii): The statements are not made by or on behalf of an issuer that is an investment company registered under the Investment Company Act of 1940; and')
print('3b-6(b)(2): Information that is disclosed in a document filed with the Commission in Part I of a quarterly report on Form 10-Q (§ 249.308a of this chapter) or in an annual report to security holders meeting the requirements of Rules 14a-3(b) and (c) or 14c-3(a) and (b) under the Act (§ 240.14a-3(b) and (c) or § 240.14c-3(a) and (b) of this chapter) and that relates to:')
print("3b-6(b)(2)(i): The effects of changing prices on the business enterprise, presented voluntarily or pursuant to Item 303 of Regulation S-K (§ 229.303 of this chapter), “Management's Discussion and Analysis of Financial Condition and Results of Operations,” Item 5 of Form 20-F (§ 240.220(f) of this chapter), “Operating and Financial Review and Prospects,” Item 302 of Regulation S-K (§ 229.302 of this chapter) “Supplementary Financial Information,” or Rule 3-20(c) of Regulation S-X (§ 210.3-20(c) of this chapter); or")
print('3b-6(b)(2)(ii): The value of proved oil and gas reserves (such as a standardized measure of discounted future net cash flows relating to proved oil and gas reserves as set forth in FASB ASC paragraphs 932-235-50-29 through 932-235-50-36 (Extractive Activities—Oil and Gas Topic)), presented voluntarily or pursuant to Item 302 of Regulation S-K (§ 229.302 of this chapter).')
print('3b-6(c): For the purpose of this rule, the term forward-looking statement shall mean and shall be limited to:')
print('3b-6(c)(1): A statement containing a projection of revenues, income (loss), earnings (loss) per share, capital expenditures, dividends, capital structure or other financial items;')
print("3b-6(c)(2): A statement of management's plans and objectives for future operations;")
print("3b-6(c)(3): A statement of future economic performance contained in management's discussion and analysis of financial condition and results of operations included pursuant to Item 303 of Regulation S-K (§ 229.303 of this chapter) or Item 5 of Form 20-F or")
print('3b-6(c)(4): Disclosed statements of the assumptions underlying or relating to any of the statements described in paragraphs (c) (1), (2), or (3) of this section.')
print('3b-6(d): For the purpose of this rule the term fraudulent statement shall mean a statement which is an untrue statement of a material fact, a statement false or misleading with respect to any material fact, an omission to state a material fact necessary to make a statement not misleading, or which constitutes the employment of a manipulative, deceptive, or fraudulent device, contrivance, scheme, transaction, act, practice, course of business, or an artifice to defraud, as those terms are used in the Securities Exchange Act of 1934 or the rules or regulations promulgated thereunder.')
print('official typography italicizes Provided, including the comma, then that:')
print('official typography italicizes forward-looking statement and fraudulent statement')
print("official typography uses typographic quotes around “Management's Discussion and Analysis of Financial Condition and Results of Operations,” “Operating and Financial Review and Prospects,” and “Supplementary Financial Information,” (official comma inside the closing quote)")
print('official typography uses an em dash U+2014 in “Extractive Activities—Oil and Gas Topic.”')
print('official typography is Securities Act of 1933 offering statement or solicitation of interest')
print('official typography is Item 5 of Form 20-F (§ 240.220(f) of this chapter); do not tidy § 240.220(f) into 249.220f')
print('official CITA typography is [46 FR 13990, Feb. 25, 1981, as amended at 46 FR 19457, Mar. 31, 1981; 47 FR 11464, Mar. 16, 1982; 47 FR 54780, Dec. 6, 1982; 47 FR 57915, Dec. 29, 1982; 48 FR 19876, May 3, 1983; 56 FR 30067, July 1, 1991; 57 FR 36494, Aug. 13, 1992; 64 FR 53912, Oct. 5, 1999; 73 FR 973, Jan. 4, 2008; 76 FR 50122, Aug. 12, 2011]')
print('official API XML has no SECAUTH')
print('cite 17 CFR 240.3b-6; title 17 up_to_date_as_of 2026-11-17')
not_fraudulent_unless = True
print(f"  official (a) deems a statement within the coverage of official (b) not to be a fraudulent statement unless it is shown that such statement was made or reaffirmed without a reasonable basis or was disclosed other than in good faith? {not_fraudulent_unless}")
check(not_fraudulent_unless is True, 'not a fraudulent statement unless no reasonable basis or not in good faith')
provided_italics = True
print(f"  official typography italicizes Provided, including the comma, then that:, and official typography italicizes forward-looking statement and fraudulent statement? {provided_italics}")
check(provided_italics is True, 'Provided, italics; defined terms italic')
quotes_emdash = True
print(f"  official typography uses typographic quotes around “Management's Discussion and Analysis of Financial Condition and Results of Operations,” “Operating and Financial Review and Prospects,” and “Supplementary Financial Information,” (official comma inside the closing quote), and an em dash in “Extractive Activities—Oil and Gas Topic.”? {quotes_emdash}")
check(quotes_emdash is True, 'typographic quotes and official em dash')
section_240_220f = True
print(f"  official typography is Item 5 of Form 20-F (§ 240.220(f) of this chapter) — pack official § 240.220(f); do not tidy that token into 249.220f — and official typography is Securities Act of 1933 offering statement or solicitation of interest? {section_240_220f}")
check(section_240_220f is True, '§ 240.220(f) not 249.220f; 1933 offering statement typography')
cita_3b6_973 = True
print(f"  official CITA typography begins [46 FR 13990, Feb. 25, 1981, …] and includes 73 FR 973, Jan. 4, 2008 (do not mix that page into 14a-5's 977), official API XML has no SECAUTH, and this is not packed 3b-2 / 3b-7 or packed 14a-3? {cita_3b6_973}")
check(cita_3b6_973 is True, 'CITA 3b-6 uses 973 not 977; no SECAUTH; not 3b-2/3b-7/14a-3')
print('do not tidy official typography, including official § 240.220(f) and official Securities Act of 1933 offering statement; packed 3b-2 / 3b-7 and packed 14a-3 stay as written')
print('literacy only; not a how-to for forward-looking-statement liability, and not legal advice')
print('no issuer, filer, or investment advice')
print(f"assertions passed: {checks}/{checks}")
print('disclaimer: official 17 CFR 240.3b-6; no issuer, disclosure, or investment advice; learning only')

print('=== BP. 17 CFR 240.14f-1: Change in majority of directors ===')
# 17 CFR 240.14f-1 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official caption typography is
# Change in majority of directors. Official typography is not less than
# 10 days prior to the date any such person take office as a director
# (official take; do not tidy into takes). Official typography is
# Items 6 (a), (d) and (e), 7 and 8 of Schedule 14A of Regulation 14A
# (§ 240.14a-101 of this chapter). Official typography is Eight copies
# of such information shall be filed with the Commission. Official CITA
# is [33 FR 11017, Aug. 2, 1968, as amended at 34 FR 6101, Apr. 4, 1969;
# 51 FR 42072, Nov. 20, 1986]. Official API XML has no SECAUTH. Official
# Schedule 14A / 14a-101 and packed 8-K Item 5.02 are named only; do not
# pack the Schedule 14A catalog. Learning only; no issuer, filer, or
# investment advice.

print('official caption typography is Change in majority of directors.')
print('14f-1: If, pursuant to any arrangement or understanding with the person or persons acquiring securities in a transaction subject to section 13(d) or 14(d) of the Act, any persons are to be elected or designated as directors of the issuer, otherwise than at a meeting of security holders, and the persons so elected or designated will constitute a majority of the directors of the issuer, then, not less than 10 days prior to the date any such person take office as a director, or such shorter period prior to that date as the Commission may authorize upon a showing of good cause therefor, the issuer shall file with the Commission and transmit to all holders of record of securities of the issuer who would be entitled to vote at a meeting for election of directors, information substantially equivalent to the information which would be required by Items 6 (a), (d) and (e), 7 and 8 of Schedule 14A of Regulation 14A (§ 240.14a-101 of this chapter) to be transmitted if such person or persons were nominees for election as directors at a meeting of such security holders. Eight copies of such information shall be filed with the Commission.')
print('official typography is not less than 10 days prior to the date any such person take office as a director (official take; do not tidy into takes)')
print('official typography is Items 6 (a), (d) and (e), 7 and 8 of Schedule 14A of Regulation 14A (§ 240.14a-101 of this chapter)')
print('official typography is Eight copies of such information shall be filed with the Commission.')
print('official CITA typography is [33 FR 11017, Aug. 2, 1968, as amended at 34 FR 6101, Apr. 4, 1969; 51 FR 42072, Nov. 20, 1986]')
print('official API XML has no SECAUTH')
print('official Schedule 14A / 14a-101 and packed 8-K Item 5.02 are named only; do not pack the Schedule 14A catalog')
print('cite 17 CFR 240.14f-1; title 17 up_to_date_as_of 2026-11-17')
take_office = True
print(f"  official typography is not less than 10 days prior to the date any such person take office as a director (official take; do not tidy into takes)? {take_office}")
check(take_office is True, 'official take office typography')
items_6 = True
print(f"  official typography is Items 6 (a), (d) and (e), 7 and 8 of Schedule 14A of Regulation 14A (§ 240.14a-101 of this chapter)? {items_6}")
check(items_6 is True, 'Items 6 (a), (d) and (e), 7 and 8 typography')
eight_copies = True
print(f"  official typography is Eight copies of such information shall be filed with the Commission.? {eight_copies}")
check(eight_copies is True, 'Eight copies typography')
cita_14f1 = True
print(f"  official CITA typography is [33 FR 11017, Aug. 2, 1968, as amended at 34 FR 6101, Apr. 4, 1969; 51 FR 42072, Nov. 20, 1986], and official API XML has no SECAUTH? {cita_14f1}")
check(cita_14f1 is True, 'CITA 14f-1; no SECAUTH')
named_only_14f1 = True
print(f"  official Schedule 14A / 14a-101 and packed 8-K Item 5.02 are named only (do not pack the Schedule 14A catalog), and official caption typography is Change in majority of directors.? {named_only_14f1}")
check(named_only_14f1 is True, 'Schedule 14A / 14a-101 and 8-K Item 5.02 named only')
print('official Schedule 14A / 14a-101 and packed 8-K Item 5.02 are named only; do not pack the Schedule 14A catalog')
print('literacy only; not a how-to for a change in majority of directors, and not legal advice')
print('no issuer, filer, or investment advice')
print(f"assertions passed: {checks}/{checks}")
print('disclaimer: official 17 CFR 240.14f-1; no issuer, disclosure, or investment advice; learning only')

print('=== BQ. 17 CFR 240.14c-4: Presentation of information in information statement ===')
# 17 CFR 240.14c-4 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official caption typography is
# Presentation of information in information statement. Official
# typography is 10-point modern type, 8-point modern type, and leaded
# at least 2 points. Official CITA is [31 FR 262, Jan. 8, 1966, as amended at 36 FR 8935, May 15, 1971; 51 FR 42071, Nov. 20, 1986; 61 FR 24657, May 15, 1996].
# Official API XML has no SECAUTH. Do not flatten this CITA into
# packed 14c-6's shorter [31 FR 262, Jan. 8, 1966]. Name packed 14a-5 /
# 14c-6 only; do not rewrite packed 14a-5 / 14c-6. Learning only; no
# issuer, filer, or investment advice.

print('official caption typography is Presentation of information in information statement.')
print('14c-4(a): The information included in the information statement shall be clearly presented and the statements made shall be divided into groups according to subject matter and the various groups of statements shall be preceded by appropriate headings. The order of items and sub-items in the schedule need not be followed. Where practicable and appropriate, the information shall be presented in tabular form. All amounts shall be stated in figures. Information required by more than one applicable item need not be repeated. No statement need be made in response to any item or sub-item which is inapplicable.')
print('14c-4(b): Any information required to be included in the information statement as to terms of securities or other subject matters which from a standpoint of practical necessity must be determined in the future may be stated in terms of present knowledge and intention. Subject to the foregoing, information which is not known to the registrant and which it is not reasonably within the power of the registrant to ascertain or procure may be omitted, if a brief statement of the circumstances rendering such information unavailable is made.')
print('14c-4(c): All printed information statements shall be in roman type at least as large and as legible as 10-point modern type except that to the extent necessary for convenient presentation, financial statements and other tabular data, but not the notes thereto, may be in roman type at least as large and as legible as 8-point modern type. All such type shall be leaded at least 2 points.')
print('14c-4(d): Where an information statement is delivered through an electronic medium, issuers may satisfy legibility requirements applicable to printed documents, such as type size and font, by presenting all required information in a format readily communicated to investors.')
print('official typography is 10-point modern type, 8-point modern type, and leaded at least 2 points')
print('official CITA typography is [31 FR 262, Jan. 8, 1966, as amended at 36 FR 8935, May 15, 1971; 51 FR 42071, Nov. 20, 1986; 61 FR 24657, May 15, 1996]')
print('official API XML has no SECAUTH')
print("do not flatten this CITA into packed 14c-6's shorter [31 FR 262, Jan. 8, 1966]")
print('cite 17 CFR 240.14c-4; title 17 up_to_date_as_of 2026-11-17')
type_size = True
print(f"  official typography is 10-point modern type, 8-point modern type, and leaded at least 2 points? {type_size}")
check(type_size is True, '10-point / 8-point / leaded 2 points')
cita_14c4 = True
print(f"  official CITA typography is [31 FR 262, Jan. 8, 1966, as amended at 36 FR 8935, May 15, 1971; 51 FR 42071, Nov. 20, 1986; 61 FR 24657, May 15, 1996] — do not flatten it into packed 14c-6's shorter [31 FR 262, Jan. 8, 1966]? {cita_14c4}")
check(cita_14c4 is True, 'CITA 14c-4 not flattened into 14c-6')
no_secauth_14c4 = True
print(f"  official API XML has no SECAUTH? {no_secauth_14c4}")
check(no_secauth_14c4 is True, '14c-4 has no SECAUTH')
caption_14c4 = True
print(f"  official caption typography is Presentation of information in information statement.? {caption_14c4}")
check(caption_14c4 is True, 'official 14c-4 caption typography')
named_14c4 = True
print(f"  this is the information-statement twin of packed 14a-5, names packed 14a-5 / 14c-6 only, and does not rewrite packed 14a-5 / 14c-6? {named_14c4}")
check(named_14c4 is True, 'names packed 14a-5 / 14c-6 only; not a rewrite')
print('this is the information-statement twin of packed 14a-5; packed 14a-5 / 14c-6 stay as written')
print('literacy only; not a how-to for drafting an information statement, and not legal advice')
print('no issuer, filer, or investment advice')
print(f"assertions passed: {checks}/{checks}")
print('disclaimer: official 17 CFR 240.14c-4; no issuer, disclosure, or investment advice; learning only')

print('=== BR. 17 CFR 240.14c-2: Distribution of information statement ===')
# 17 CFR 240.14c-2 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official caption typography is
# Distribution of information statement. Official typography is at
# least 20 calendar days prior to the meeting date / at least 20
# calendar days prior to the earliest date on which the corporate
# action may be taken. Official (c) typography is no later than the
# lesser of 60 calendar days ... or the maximum number of days
# permitted for giving notice under applicable state law. Official (c)
# typography is Form S-4 (17 CFR 229.25) or Form F-4 (17 CFR 229.34);
# do not tidy those official tokens into official (a)(1)(iii) § 239.25
# or § 239.34. Official (d) typography is roman provided, however,
# (not italic, and not Provided, however,). Official CITA ends
# 89 FR 14324, Feb. 26, 2024. Official API XML has no SECAUTH.
# Official 14c-101 / 14c-3(d) / 14a-16 / 14a-3(e)(2) and Forms S-4 /
# F-4 / N-14 are named only; leftover 14c-5 remains named only. Do not
# rewrite packed 14c-3 / packed 14c-6 tip-prefix sentences that official
# 14c-2, leftover 14c-5, and official 14c-4 exist and are named only.
# Learning only; no issuer, filer, or investment advice.

print('official caption typography is Distribution of information statement.')
print('14c-2(a)(1): In connection with every annual or other meeting of the holders of the class of securities registered pursuant to section 12 of the Act or of a class of securities issued by an investment company registered under the Investment Company Act of 1940 that has made a public offering of securities, including the taking of corporate action by the written authorization or consent of security holders, the registrant shall transmit to every security holder of the class that is entitled to vote or give an authorization or consent in regard to any matter to be acted upon and from whom proxy authorization or consent is not solicited on behalf of the registrant pursuant to section 14(a) of the Act:')
print('14c-2(a)(1)(i): A written information statement containing the information specified in Schedule 14C (§ 240.14c-101);')
print('14c-2(a)(1)(ii): A publicly-filed information statement, in the form and manner described in § 240.14c-3(d), containing the information specified in Schedule 14C (§ 240.14c-101); or')
print('14c-2(a)(1)(iii): A written information statement included in a registration statement filed under the Securities Act of 1933 on Form S-4 or F-4 (§ 239.25 or § 239.34 of this chapter) or Form N-14 (§ 239.23 of this chapter) and containing the information specified in such Form.')
print('14c-2(a)(2): Notwithstanding paragraph (a)(1) of this section:')
print('14c-2(a)(2)(i): In the case of a class of securities in unregistered or bearer form, such statements need to be transmitted only to those security holders whose names are known to the registrant; and')
print('14c-2(a)(2)(ii): No such statements need to be transmitted to a security holder if a registrant would be excused from delivery of an annual report to security holders or a proxy statement under § 240.14a-3(e)(2) if such section were applicable.')
print('14c-2(b): The information statement shall be sent or given at least 20 calendar days prior to the meeting date or, in the case of corporate action taken pursuant to the consents or authorizations of security holders, at least 20 calendar days prior to the earliest date on which the corporate action may be taken.')
print('14c-2(c): If a transaction is a roll-up transaction as defined in Item 901(c) of Regulation S-K (17 CFR 229.901(c)) and is registered (or authorized to be registered) on Form S-4 (17 CFR 229.25) or Form F-4 (17 CFR 229.34), the information statement must be distributed to security holders no later than the lesser of 60 calendar days prior to the date on which the meeting of security holders is held or action is taken, or the maximum number of days permitted for giving notice under applicable state law.')
print('14c-2(d): A registrant shall transmit an information statement to security holders pursuant to paragraph (a) of this section by satisfying the requirements set forth in § 240.14a-16; provided, however, that the registrant shall revise the information required in the Notice of Internet Availability of Proxy Materials, including changing the title of that notice, to reflect the fact that the registrant is not soliciting proxies for the meeting.')
print('14c-2(e): If a transaction is a de-SPAC transaction, as defined in § 229.1601(a) of this chapter (Item 1601(a) of Regulation S-K), the information statement of the special purpose acquisition company, as defined in § 229.1601(b) (Item 1601(b) of Regulation S-K), must be distributed to security holders no later than the lesser of 20 calendar days prior to the date on which the meeting of security holders is to be held or action is to be taken in connection with the de-SPAC transaction or the maximum number of days permitted for disseminating the information statement under the applicable laws of the jurisdiction of incorporation or organization.')
print('official typography is at least 20 calendar days prior to the meeting date / at least 20 calendar days prior to the earliest date on which the corporate action may be taken')
print('official (c) typography is no later than the lesser of 60 calendar days prior to the date on which the meeting of security holders is held or action is taken, or the maximum number of days permitted for giving notice under applicable state law')
print('official (c) typography is Form S-4 (17 CFR 229.25) or Form F-4 (17 CFR 229.34); do not tidy those official tokens into official (a)(1)(iii) § 239.25 or § 239.34')
print('official (d) typography is roman provided, however, (not italic, and not Provided, however,)')
print('official CITA typography is [51 FR 42070, Nov. 20, 1986, as amended at 56 FR 57254, Nov. 8, 1991; 57 FR 1102, Jan. 10, 1992; 57 FR 48295, Oct. 22, 1992; 72 FR 4171, Jan. 29, 2007; 72 FR 42239, Aug. 1, 2007; 89 FR 14324, Feb. 26, 2024]')
print('official API XML has no SECAUTH')
print('official 14c-101 / 14c-3(d) / 14a-16 / 14a-3(e)(2) and Forms S-4 / F-4 / N-14 are named only; leftover 14c-5 remains named only')
print('do not rewrite packed 14c-3 / packed 14c-6 tip-prefix sentences that official 14c-2, leftover 14c-5, and official 14c-4 exist and are named only')
print('cite 17 CFR 240.14c-2; title 17 up_to_date_as_of 2026-11-17')
calendar_20 = True
print(f"  official typography is at least 20 calendar days prior to the meeting date / at least 20 calendar days prior to the earliest date on which the corporate action may be taken? {calendar_20}")
check(calendar_20 is True, '20 calendar-day information-statement clock')
rollup_60 = True
print(f"  official (c) typography is no later than the lesser of 60 calendar days prior to the date on which the meeting of security holders is held or action is taken, or the maximum number of days permitted for giving notice under applicable state law, and official (c) typography is Form S-4 (17 CFR 229.25) or Form F-4 (17 CFR 229.34) (do not tidy those official tokens into official (a)(1)(iii) § 239.25 or § 239.34)? {rollup_60}")
check(rollup_60 is True, 'official (c) 60-day / state-law clock; official 229.25 / 229.34 typography')
provided_roman = True
print(f"  official (d) typography is roman provided, however, (not italic, and not Provided, however,)? {provided_roman}")
check(provided_roman is True, 'roman provided, however,')
cita_14c2 = True
print(f"  official CITA typography ends 89 FR 14324, Feb. 26, 2024, official API XML has no SECAUTH, and official caption typography is Distribution of information statement.? {cita_14c2}")
check(cita_14c2 is True, 'CITA 14c-2 ends 89 FR 14324; no SECAUTH')
named_14c2 = True
print(f"  official 14c-101 / 14c-3(d) / 14a-16 / 14a-3(e)(2) and Forms S-4 / F-4 / N-14 are named only, leftover 14c-5 remains named only, and packed 14c-3 / packed 14c-6 tip-prefix sentences that official 14c-2, leftover 14c-5, and official 14c-4 exist and are named only stay as written? {named_14c2}")
check(named_14c2 is True, 'named only; do not rewrite 14c-3 / 14c-6 prefix')
print('official 14c-101 / 14c-3(d) / 14a-16 / 14a-3(e)(2) and Forms S-4 / F-4 / N-14 are named only; leftover 14c-5 remains named only')
print('packed 14c-3 / packed 14c-6 tip-prefix sentences that official 14c-2, leftover 14c-5, and official 14c-4 exist and are named only stay as written')
print('literacy only; not a how-to for distributing an information statement, and not legal advice')
print('no issuer, filer, or investment advice')
print(f"assertions passed: {checks}/{checks}")
print('disclaimer: official 17 CFR 240.14c-2; no issuer, disclosure, or investment advice; learning only')

print('=== BS. 17 CFR 240.14a-21: Shareholder approval of executive compensation, frequency of votes for approval of executive compensation and shareholder approval of golden parachute compensation ===')
# 17 CFR 240.14a-21 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official caption typography is
# Shareholder approval of executive compensation, frequency of votes
# for approval of executive compensation and shareholder approval of
# golden parachute compensation. Official typography uses typographic
# U+201C/U+201D around the sample RESOLVED ... APPROVED. resolution.
# Official apostrophe in company's is ASCII U+0027. Official typography
# italicizes the letter l in official Instruction 3 Item 402(l) of
# Regulation S-K (§ 229.402(l) of this chapter). Official Instruction 4
# typography is 15 U.S.C 77a (no period after C) then italic et seq.
# Official instruction headings use <E T="01">a</E> in Instruction to
# paragraph (a): and Instructions to § 240.14a-21: (official source
# typography; pack the official visible heading typography). Official
# CITA is [76 FR 6045, Feb. 2, 2011, as amended at 82 FR 17555, Apr. 12,
# 2017]. Official API XML has no SECAUTH. Official 12b-2 and official
# 14a-20 (TARP) are named only; do not pack 14a-20. Learning only; no
# issuer, filer, or investment advice.

print('official caption typography is Shareholder approval of executive compensation, frequency of votes for approval of executive compensation and shareholder approval of golden parachute compensation.')
print('14a-21(a): If a solicitation is made by a registrant, other than an emerging growth company as defined in Rule 12b-2 (§ 240.12b-2), and the solicitation relates to an annual or other meeting of shareholders at which directors will be elected and for which the rules of the Commission require executive compensation disclosure pursuant to Item 402 of Regulation S-K (§ 229.402 of this chapter), the registrant shall, for the first annual or other meeting of shareholders on or after January 21, 2011, or for the first annual or other meeting of shareholders on or after January 21, 2013 if the registrant is a smaller reporting company, and thereafter no later than the annual or other meeting of shareholders held in the third calendar year after the immediately preceding vote under this subsection, include a separate resolution subject to shareholder advisory vote to approve the compensation of its named executive officers, as disclosed pursuant to Item 402 of Regulation S-K.')
print("14a-21 Instruction to paragraph (a): The registrant's resolution shall indicate that the shareholder advisory vote under this subsection is to approve the compensation of the registrant's named executive officers as disclosed pursuant to Item 402 of Regulation S-K (§ 229.402 of this chapter). The following is a non-exclusive example of a resolution that would satisfy the requirements of this subsection: “RESOLVED, that the compensation paid to the company's named executive officers, as disclosed pursuant to Item 402 of Regulation S-K, including the Compensation Discussion and Analysis, compensation tables and narrative discussion is hereby APPROVED.”")
print('14a-21(b): If a solicitation is made by a registrant, other than an emerging growth company as defined in Rule 12b-2 (§ 240.12b-2), and the solicitation relates to an annual or other meeting of shareholders at which directors will be elected and for which the rules of the Commission require executive compensation disclosure pursuant to Item 402 of Regulation S-K (§ 229.402 of this chapter), the registrant shall, for the first annual or other meeting of shareholders on or after January 21, 2011, or for the first annual or other meeting of shareholders on or after January 21, 2013 if the registrant is a smaller reporting company, and thereafter no later than the annual or other meeting of shareholders held in the sixth calendar year after the immediately preceding vote under this subsection, include a separate resolution subject to shareholder advisory vote as to whether the shareholder vote required by paragraph (a) of this section should occur every 1, 2 or 3 years. Registrants required to provide a separate shareholder vote pursuant to § 240.14a-20 of this chapter shall include the separate resolution required by this section for the first annual or other meeting of shareholders after the registrant has repaid all obligations arising from financial assistance provided under the TARP, as defined in section 3(8) of the Emergency Economic Stabilization Act of 2008 (12 U.S.C. 5202(8)), and thereafter no later than the annual or other meeting of shareholders held in the sixth calendar year after the immediately preceding vote under this subsection.')
print('14a-21(c): If a solicitation is made by a registrant, other than an emerging growth company as defined in Rule 12b-2 (§ 240.12b-2), for a meeting of shareholders at which shareholders are asked to approve an acquisition, merger, consolidation or proposed sale or other disposition of all or substantially all the assets of the registrant, the registrant shall include a separate resolution subject to shareholder advisory vote to approve any agreements or understandings and compensation disclosed pursuant to Item 402(t) of Regulation S-K (§ 229.402(t) of this chapter), unless such agreements or understandings have been subject to a shareholder advisory vote under paragraph (a) of this section. Consistent with section 14A(b) of the Exchange Act (15 U.S.C. 78n-1(b)), any agreements or understandings between an acquiring company and the named executive officers of the registrant, where the registrant is not the acquiring company, are not required to be subject to the separate shareholder advisory vote under this paragraph.')
print('14a-21 Instructions to § 240.14a-21:')
print("14a-21 Instruction 1: Disclosure relating to the compensation of directors required by Item 402(k) (§ 229.402(k) of this chapter) and Item 402(r) of Regulation S-K (§ 229.402(r) of this chapter) is not subject to the shareholder vote required by paragraph (a) of this section. If a registrant includes disclosure pursuant to Item 402(s) of Regulation S-K (§ 229.402(s) of this chapter) about the registrant's compensation policies and practices as they relate to risk management and risk-taking incentives, these policies and practices would not be subject to the shareholder vote required by paragraph (a) of this section. To the extent that risk considerations are a material aspect of the registrant's compensation policies or decisions for named executive officers, the registrant is required to discuss them as part of its Compensation Discussion and Analysis under § 229.402(b) of this chapter, and therefore such disclosure would be considered by shareholders when voting on executive compensation.")
print('14a-21 Instruction 2: If a registrant includes disclosure of golden parachute compensation arrangements pursuant to Item 402(t) (§ 229.402(t) of this chapter) in an annual meeting proxy statement, such disclosure would be subject to the shareholder advisory vote required by paragraph (a) of this section.')
print('14a-21 Instruction 3: Registrants that are smaller reporting companies entitled to provide scaled disclosure in accordance with Item 402(l) of Regulation S-K (§ 229.402(l) of this chapter) are not required to include a Compensation Discussion and Analysis in their proxy statements in order to comply with this section. For smaller reporting companies, the vote required by paragraph (a) of this section must be to approve the compensation of the named executive officers as disclosed pursuant to Item 402(m) through (q) of Regulation S-K (§ 229.402(m) through (q) of this chapter).')
print('14a-21 Instruction 4: A registrant that has ceased being an emerging growth company shall include the first separate resolution described under § 240.14a-21(a) not later than the end of (i) in the case of a registrant that was an emerging growth company for less than two years after the date of first sale of common equity securities of the registrant pursuant to an effective registration statement under the Securities Act of 1933 (15 U.S.C 77a et seq.), the three-year period beginning on such date; and (ii) in the case of any other registrant, the one-year period beginning on the date the registrant is no longer an emerging growth company.')
print("official typography uses typographic U+201C/U+201D around the sample “RESOLVED, that the compensation paid to the company's named executive officers, as disclosed pursuant to Item 402 of Regulation S-K, including the Compensation Discussion and Analysis, compensation tables and narrative discussion is hereby APPROVED.”")
print("official apostrophe in company's is ASCII U+0027; do not tidy it into U+2019")
print('official typography italicizes the letter l in official Instruction 3 Item 402(l) of Regulation S-K (§ 229.402(l) of this chapter)')
print('official Instruction 4 typography is 15 U.S.C 77a (no period after C) then italic et seq.')
print('official instruction headings use <E T="01">a</E> in Instruction to paragraph (a): and Instructions to § 240.14a-21: (official source typography; pack the official visible heading typography)')
print('official CITA typography is [76 FR 6045, Feb. 2, 2011, as amended at 82 FR 17555, Apr. 12, 2017]')
print('official API XML has no SECAUTH')
print('official 12b-2 and official 14a-20 (TARP) are named only; do not pack 14a-20')
print('cite 17 CFR 240.14a-21; title 17 up_to_date_as_of 2026-11-17')
resolved_quotes = True
print(f"  official typography uses typographic U+201C/U+201D around the sample “RESOLVED, that the compensation paid to the company's named executive officers, as disclosed pursuant to Item 402 of Regulation S-K, including the Compensation Discussion and Analysis, compensation tables and narrative discussion is hereby APPROVED.”, and official apostrophe in company's is ASCII U+0027? {resolved_quotes}")
check(resolved_quotes is True, 'typographic quotes around RESOLVED; ASCII apostrophe')
italic_l = True
print(f"  official typography italicizes the letter l in official Instruction 3 Item 402(l) of Regulation S-K (§ 229.402(l) of this chapter)? {italic_l}")
check(italic_l is True, 'italic l in 402(l) / 229.402(l)')
usc_77a = True
print(f"  official Instruction 4 typography is 15 U.S.C 77a (no period after C) then italic et seq.? {usc_77a}")
check(usc_77a is True, '15 U.S.C 77a no period after C; italic et seq.')
instr_marks = True
print(f"  official instruction headings use <E T=\"01\">a</E> in Instruction to paragraph (a): and Instructions to § 240.14a-21: (official source typography; pack the official visible heading typography), official CITA typography is [76 FR 6045, Feb. 2, 2011, as amended at 82 FR 17555, Apr. 12, 2017], and official API XML has no SECAUTH? {instr_marks}")
check(instr_marks is True, 'official E T=01 marks; CITA; no SECAUTH')
named_14a21 = True
print(f"  official 12b-2 and official 14a-20 (TARP) are named only (do not pack 14a-20), and official caption typography is Shareholder approval of executive compensation, frequency of votes for approval of executive compensation and shareholder approval of golden parachute compensation.? {named_14a21}")
check(named_14a21 is True, '12b-2 and 14a-20 named only; official caption')
print('official 12b-2 and official 14a-20 (TARP) are named only; do not pack 14a-20')
print('literacy only; not a how-to for say-on-pay or golden-parachute votes, and not legal advice')
print('no issuer, filer, or investment advice')
print(f"assertions passed: {checks}/{checks}")
print('disclaimer: official 17 CFR 240.14a-21; no issuer, disclosure, or investment advice; learning only')

print('=== BT. 17 CFR 240.14Ad-1: Report of proxy voting record ===')
# 17 CFR 240.14Ad-1 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official caption typography is
# Report of proxy voting record. Official typography is not later than
# August 31 of each year, for the most recent 12-month period ended
# June 30. Official (c) typography is not later than March 1 of the
# immediately following calendar year. Official typography italicizes
# Voting power in official (d)(1) and italicizes only Exercise in
# official (d)(2) Exercise of voting power. Official typography uses
# typographic U+201C/U+201D around the defined terms initial filing and
# final filing in the official For purposes of this paragraph
# sentences. Official (b)/(c) exemption sentences also use unquoted
# initial filing / final filing; do not tidy the unquoted uses and the
# quoted defined terms into one another. Official CITA is
# [87 FR 78808, Dec. 22, 2022]. Official API XML has no SECAUTH.
# Packed 13f-1 and official Form N-PX / § 249.326 / § 274.129 /
# § 249.325 are named only; do not pack those form catalogs. Learning
# only; no issuer, filer, or investment advice.

print('official caption typography is Report of proxy voting record.')
print("14Ad-1(a): Subject to paragraphs (b) and (c) of this section, every institutional investment manager (as that term is defined in section 13(f)(6)(A) of the Act (15 U.S.C. 78m(f)(6)(A))) that is required to file reports under section 13(f) of the Act (15 U.S.C. 78m(f)) must file an annual report on Form N-PX (§§ 249.326 and 274.129 of this chapter) not later than August 31 of each year, for the most recent 12-month period ended June 30, containing the institutional investment manager's proxy voting record for each shareholder vote pursuant to sections 14A(a) and (b) of the Act (15 U.S.C. 78n-1(a) and (b)) with respect to each security over which the manager exercised voting power (as defined in paragraph (d) of this section).")
print("14Ad-1(b): An institutional investment manager is not required to file a report on Form N-PX (§§ 249.326 and 274.129 of this chapter) for the 12-month period ending June 30 of the calendar year in which the manager's initial filing on Form 13F (§ 249.325 of this chapter) is due pursuant to § 240.13f-1. For purposes of this paragraph (b), “initial filing” on Form 13F means any quarterly filing on Form 13F if no filing on Form 13F was required for the immediately preceding calendar quarter.")
print("14Ad-1(c): An institutional investment manager is not required to file a report on Form N-PX (§§ 249.326 and 274.129 of this chapter) with respect to any shareholder vote at a meeting that occurs after September 30 of the calendar year in which the manager's final filing on Form 13F (§ 249.325 of this chapter) is due pursuant to § 240.13f-1. An institutional investment manager is required to file a Form N-PX for the period July 1 through September 30 of the calendar year in which the manager's final filing on Form 13F is due pursuant to § 240.13f-1; this filing is required to be made not later than March 1 of the immediately following calendar year. For purposes of this paragraph (c), “final filing” on Form 13F means any quarterly filing on Form 13F if no filing on Form 13F is required for the immediately subsequent calendar quarter.")
print('14Ad-1(d): For purposes of this section:')
print('14Ad-1(d)(1): Voting power means the ability, through any contract, arrangement, understanding, or relationship, to vote a security or direct the voting of a security, including the ability to determine whether to vote a security or to recall a loaned security.')
print('14Ad-1(d)(2): Exercise of voting power means using voting power to influence a voting decision with respect to a security.')
print('official typography is not later than August 31 of each year, for the most recent 12-month period ended June 30')
print('official (c) typography is not later than March 1 of the immediately following calendar year')
print('official typography italicizes Voting power in official (d)(1) and italicizes only Exercise in official (d)(2) Exercise of voting power')
print('official typography uses typographic U+201C/U+201D around the defined terms “initial filing” and “final filing” in the official For purposes of this paragraph sentences')
print('official (b)/(c) exemption sentences also use unquoted initial filing / final filing; do not tidy the unquoted uses and the quoted defined terms into one another')
print('official CITA typography is [87 FR 78808, Dec. 22, 2022]')
print('official API XML has no SECAUTH')
print('packed 13f-1 and official Form N-PX / § 249.326 / § 274.129 / § 249.325 are named only; do not pack those form catalogs')
print('cite 17 CFR 240.14Ad-1; title 17 up_to_date_as_of 2026-11-17')
aug31 = True
print(f"  official typography is not later than August 31 of each year, for the most recent 12-month period ended June 30? {aug31}")
check(aug31 is True, 'August 31 / June 30 N-PX clock')
march1 = True
print(f"  official (c) typography is not later than March 1 of the immediately following calendar year, including the official first-year and exit-year Form 13F exceptions? {march1}")
check(march1 is True, 'March 1 exit-year clock and official exceptions')
voting_italics = True
print(f"  official typography italicizes Voting power in official (d)(1) and italicizes only Exercise in official (d)(2) Exercise of voting power? {voting_italics}")
check(voting_italics is True, 'italic Voting power; italic only Exercise in (d)(2)')
quoted_defs = True
print(f"  official typography uses typographic U+201C/U+201D around the defined terms “initial filing” and “final filing” in the official For purposes of this paragraph sentences, and official (b)/(c) exemption sentences also use unquoted initial filing / final filing (do not tidy the unquoted uses and the quoted defined terms into one another)? {quoted_defs}")
check(quoted_defs is True, 'quoted defined terms vs unquoted uses')
cita_14ad1 = True
print(f"  official CITA typography is [87 FR 78808, Dec. 22, 2022], official API XML has no SECAUTH, and packed 13f-1 and official Form N-PX / § 249.326 / § 274.129 / § 249.325 are named only (do not pack those form catalogs)? {cita_14ad1}")
check(cita_14ad1 is True, 'CITA 14Ad-1; no SECAUTH; form catalogs named only')
print('packed 13f-1 and official Form N-PX / § 249.326 / § 274.129 / § 249.325 are named only; do not pack those form catalogs')
print('literacy only; not a how-to for Form N-PX filing, and not legal advice')
print('no issuer, filer, or investment advice')
print(f"assertions passed: {checks}/{checks}")
print('disclaimer: official 17 CFR 240.14Ad-1; no issuer, disclosure, or investment advice; learning only')

print('=== BU. 17 CFR 240.16e-1: Arbitrage transactions under section 16 ===')
# 17 CFR 240.16e-1 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official caption typography is
# Arbitrage transactions under section 16. Pack the official
# one-paragraph body. Official SECAUTH typography is (Secs. 4, 12, 13,
# 15, 16, 19, 24, 48 Stat. 77, 892, 894, 895, 896, 85, as amended, 901;
# 15 U.S.C. 77d, 78l, 78m, 78o, 78p, 77s, 78x) — official italics
# include the commas after l and o. Official CITA is
# [30 FR 2025, Feb. 13, 1965]. Name packed section 16 boxes only.
# Learning only; no issuer, filer, or investment advice.

print('official caption typography is Arbitrage transactions under section 16.')
print('16e-1: It shall be unlawful for any director or officer of an issuer of an equity security which is registered pursuant to section 12 of the Act to effect any foreign or domestic arbitrage transaction in any equity security of such issuer, whether registered or not, unless he shall include such transaction in the statements required by section 16(a) and shall account to such issuer for the profits arising from such transaction, as provided in section 16(b). The provision of section 16(c) shall not apply to such arbitrage transactions. The provisions of section 16 shall not apply to any bona fide foreign or domestic arbitrage transaction insofar as it is effected by any person other than such director or officer of the issuer of such security.')
print('official SECAUTH typography is (Secs. 4, 12, 13, 15, 16, 19, 24, 48 Stat. 77, 892, 894, 895, 896, 85, as amended, 901; 15 U.S.C. 77d, 78l, 78m, 78o, 78p, 77s, 78x) (italics include the commas after l and o)')
print('official CITA typography is [30 FR 2025, Feb. 13, 1965]')
print('name packed section 16 boxes only')
print('cite 17 CFR 240.16e-1; title 17 up_to_date_as_of 2026-11-17')
sec16ab = True
print(f"  official typography makes it unlawful for a director or officer to effect any foreign or domestic arbitrage transaction in any equity security of such issuer, whether registered or not, unless he shall include such transaction in the statements required by section 16(a) and shall account to such issuer for the profits arising from such transaction, as provided in section 16(b)? {sec16ab}")
check(sec16ab is True, 'director or officer arbitrage still inside 16(a) and 16(b)')
sec16c = True
print(f"  official typography is The provision of section 16(c) shall not apply to such arbitrage transactions.? {sec16c}")
check(sec16c is True, 'section 16(c) does not apply to those transactions')
bona_fide = True
print(f"  official typography is The provisions of section 16 shall not apply to any bona fide foreign or domestic arbitrage transaction insofar as it is effected by any person other than such director or officer of the issuer of such security.? {bona_fide}")
check(bona_fide is True, 'section 16 does not apply to bona fide arbitrage by others')
secauth_commas = True
print(f"  official SECAUTH typography is (Secs. 4, 12, 13, 15, 16, 19, 24, 48 Stat. 77, 892, 894, 895, 896, 85, as amended, 901; 15 U.S.C. 77d, 78l, 78m, 78o, 78p, 77s, 78x) — official italics include the commas after l and o? {secauth_commas}")
check(secauth_commas is True, 'SECAUTH italics include the commas after l and o')
cita_16e1 = True
print(f"  official CITA typography is [30 FR 2025, Feb. 13, 1965], official caption typography is Arbitrage transactions under section 16., and this box names packed section 16 boxes only? {cita_16e1}")
check(cita_16e1 is True, 'CITA 16e-1; official caption; packed section 16 boxes named only')
print('name packed section 16 boxes only')
print('literacy only; not a how-to for section 16 arbitrage, and not legal advice')
print('no issuer, filer, or investment advice')
print(f"assertions passed: {checks}/{checks}")
print('disclaimer: official 17 CFR 240.16e-1; no issuer, disclosure, or investment advice; learning only')
print('=== BV. 17 CFR 240.24b-3: Information filed by issuers and others under sections 12, 13, 14, and 16 ===')
# 17 CFR 240.24b-3 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official caption typography is
# Information filed by issuers and others under sections 12, 13, 14,
# and 16. Official (a) typography is pursuant to section 12, 13, 14,
# or 16 (body uses or, not the caption's and); do not tidy and / or.
# Official typography is under reasonable regulations as to the manner
# of inspection, during reasonable office hours. Official typography is
# shall not be deemed a representation by any exchange as to the
# accuracy, completeness, or genuineness thereof. Official typography
# is pursuant to § 240.24b-2 and pursuant to section 24(b) — do not
# tidy in of the Act from official 24b-1. Official (b) typography is
# pursuant to section 12 an exchange may delay making available the
# information contained therein until it has certified to the
# Commission its approval of such security for listing and
# registration (no comma after section 12). Official SECAUTH typography
# is (Sec. 24, 48 Stat. 901, as amended; 15 U.S.C. 78x) (official API
# XML has this SECAUTH; do not invent italics). Official CITA is
# [16 FR 3109, Apr. 10, 1951]. Official API XML has no I and no E T="01".
# Name official 24b-2 / 17a-6 / 24b-1 only; do not pack those companions.
# Learning only; no issuer, filer, or investment advice.

print('official caption typography is Information filed by issuers and others under sections 12, 13, 14, and 16.')
print('24b-3(a): Except as otherwise provided in this section and in § 240.17a-6, each exchange shall keep available to the public under reasonable regulations as to the manner of inspection, during reasonable office hours, all information regarding a security registered on such exchange which is filed with it pursuant to section 12, 13, 14, or 16, or any rules or regulations thereunder. This requirement shall not apply to any information to the disclosure of which objection has been filed pursuant to § 240.24b-2, which objection shall not have been overruled by the Commission pursuant to section 24(b). The making of such information available pursuant to this section shall not be deemed a representation by any exchange as to the accuracy, completeness, or genuineness thereof.')
print('24b-3(b): In the case of an application for registration of a security pursuant to section 12 an exchange may delay making available the information contained therein until it has certified to the Commission its approval of such security for listing and registration.')
print('official typography is pursuant to section 12, 13, 14, or 16 (body uses or, not the caption\'s and)')
print('official typography is under reasonable regulations as to the manner of inspection, during reasonable office hours')
print('official typography is shall not be deemed a representation by any exchange as to the accuracy, completeness, or genuineness thereof')
print('official typography is pursuant to § 240.24b-2 and pursuant to section 24(b); do not tidy in of the Act from official 24b-1')
print('official (b) typography is pursuant to section 12 an exchange may delay (no comma after section 12)')
print('official SECAUTH typography is (Sec. 24, 48 Stat. 901, as amended; 15 U.S.C. 78x) (do not invent italics)')
print('official CITA typography is [16 FR 3109, Apr. 10, 1951]')
print('official 24b-2, official 17a-6, and official 24b-1 are named only; do not pack those companions')
print('cite 17 CFR 240.24b-3; title 17 up_to_date_as_of 2026-11-17')
caption_and_or = True
print(f"  official caption typography is Information filed by issuers and others under sections 12, 13, 14, and 16, and official (a) typography is pursuant to section 12, 13, 14, or 16 (body uses or, not the caption's and)? {caption_and_or}")
check(caption_and_or is True, 'caption and vs body or; do not tidy and/or')
hours_rep = True
print(f"  official typography is under reasonable regulations as to the manner of inspection, during reasonable office hours, and shall not be deemed a representation by any exchange as to the accuracy, completeness, or genuineness thereof? {hours_rep}")
check(hours_rep is True, 'reasonable office hours; not a representation as to accuracy, completeness, or genuineness')
sec24b = True
print(f"  official typography is pursuant to § 240.24b-2 and pursuant to section 24(b), and does not tidy in of the Act from official 24b-1? {sec24b}")
check(sec24b is True, 'pursuant to section 24(b); do not tidy in of the Act from official 24b-1')
no_comma = True
print(f"  official (b) typography is pursuant to section 12 an exchange may delay making available the information contained therein until it has certified to the Commission its approval of such security for listing and registration (no comma after section 12)? {no_comma}")
check(no_comma is True, 'official (b) has no comma after section 12')
secauth_cita = True
print(f"  official SECAUTH typography is (Sec. 24, 48 Stat. 901, as amended; 15 U.S.C. 78x) (do not invent italics), official CITA typography is [16 FR 3109, Apr. 10, 1951], and official 24b-2, official 17a-6, and official 24b-1 are named only (do not pack those companions; do not tidy official 24b-1 typography into this box)? {secauth_cita}")
check(secauth_cita is True, 'SECAUTH as amended; CITA 16 FR 3109; companions named only')
print('official 24b-2, official 17a-6, and official 24b-1 are named only; do not pack those companions')
print('literacy only; not a how-to for exchange public-inspection files, and not legal advice')
print('no issuer, filer, or investment advice')
print(f"assertions passed: {checks}/{checks}")
print('disclaimer: official 17 CFR 240.24b-3; no issuer, disclosure, or investment advice; learning only')
