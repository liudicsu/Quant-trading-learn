"""Event timestamps (FOMC) and IPO data traps (checked 2026-11-10).

Sources (G4): Federal Reserve "Meeting calendars, statements, and minutes (2021-2027)" (eight scheduled
meetings a year; minutes released three weeks after the policy decision; 2026 minutes release dates);
FOMC statement of 2026-10-28 ("For release at 2:00 p.m. EDT").
Sources (G5): investor.gov "Updated Investor Bulletin: Investing in an IPO" (2022-10-14) and glossary
"Initial Public Offerings: Lockup Agreements" (most lock-ups 180 days; terms are in the prospectus).
Synthetic prices. The Oct 27-28 minutes date is projected by the three-week rule, not read from the Fed
page. Learning only: no trading strategy, no return statistics, not investment advice.
"""
from datetime import date, datetime, timedelta, timezone

checks = 0


def check(cond, label):
    global checks
    assert cond, label
    checks += 1


EDT = timezone(timedelta(hours=-4))
CST = timezone(timedelta(hours=8))

print("=== A. FOMC statement time vs the trading session ===")
st = datetime(2026, 10, 28, 14, 0, tzinfo=EDT)
print(f"statement 2026-10-28 14:00 EDT -> Beijing {st.astimezone(CST):%Y-%m-%d %H:%M}")
check(st.astimezone(CST) == datetime(2026, 10, 29, 2, 0, tzinfo=CST), "Beijing time")


def can_trade_on_statement(t):
    return t >= st


print(f"trade on the statement at the 2026-10-28 09:30 open? {can_trade_on_statement(datetime(2026, 10, 28, 9, 30, tzinfo=EDT))} (look-ahead)")
print(f"trade on the statement at 14:01 EDT? {can_trade_on_statement(datetime(2026, 10, 28, 14, 1, tzinfo=EDT))}")
check(not can_trade_on_statement(datetime(2026, 10, 28, 9, 30, tzinfo=EDT)), "open is before the statement")
check(can_trade_on_statement(datetime(2026, 10, 28, 14, 1, tzinfo=EDT)), "after 14:00")

print("=== B. minutes: three weeks after the policy decision ===")
published = {date(2026, 1, 28): date(2026, 2, 18), date(2026, 3, 18): date(2026, 4, 8),
             date(2026, 4, 29): date(2026, 5, 20), date(2026, 6, 17): date(2026, 7, 8),
             date(2026, 7, 29): date(2026, 8, 19), date(2026, 9, 16): date(2026, 10, 7)}
for dec, rel in published.items():
    check(dec + timedelta(days=21) == rel, f"minutes {dec}")
print(f"3-week rule matches all {len(published)} published 2026 minutes dates")
print(f"Oct 27-28 minutes projected by the 3-week rule: {date(2026, 10, 28) + timedelta(days=21)} (projection; check the Fed calendar)")

print("=== C. IPO: the offering price is not your fill ===")
ipo_px, open1, close1 = 20.00, 26.00, 24.00
at_ipo = close1 / ipo_px - 1
at_open = close1 / open1 - 1
print(f"offering {ipo_px:.2f}, first open {open1:.2f}, close {close1:.2f}")
print(f"day-1 return from IPO price {at_ipo:.4%}; from first open {at_open:.4%}")
check(abs(at_ipo - 0.20) < 1e-12, "from offering price")
check(abs(at_open - (24 / 26 - 1)) < 1e-12, "from first open")


def momentum_signal(n_bars, lookback=60):
    return None if n_bars < lookback else "ok"


print(f"listed 45 trading days, 60-day lookback -> signal {momentum_signal(45)}")
check(momentum_signal(45) is None, "not enough history -> no signal")
check(momentum_signal(60) == "ok", "enough history")
ipo = date(2026, 3, 10)
lock = ipo + timedelta(days=180)
print(f"lock-up 180 calendar days after {ipo}: {lock} ({lock:%a}); take the real date from the prospectus")
check(lock == date(2026, 9, 6), "lock-up example date")
print(f"assertions passed: {checks}/{checks}")
print("ASSERT_event_time_ipo_ok")
print("disclaimer: synthetic prices; no FOMC or IPO strategy; learning only")

print("=== D. BLS PFEI 8:30 a.m. ET vs non-PFEI 10:00 a.m. ET ===")
# BLS Dissemination policy (last modified August 28, 2026):
# "All seven PFEIs are scheduled for release at 8:30 a.m. Eastern Time on the
# dates shown on our public calendar." The seven PFEIs are: the Employment
# Situation; Consumer Price Index; Producer Price Indexes; U.S. Import and
# Export Price Indexes; Real Earnings; Employment Cost Index; and Productivity
# and Costs.
# "All non-PFEI releases are scheduled for 10:00 a.m. Eastern Time on the
# dates shown on our public calendar."
# CPI Home (opened 2026-11-12): "The Consumer Price Index for November 2026 is
# scheduled to be released on December 10, 2026, at 8:30 A.M. Eastern Time."
# Use the official calendar for the date; do not invent a "first Friday" rule.
# Regular US equity trading opens at 09:30 ET. An 8:30 a.m. ET PFEI is already
# out before that open, so that day's regular open can already reflect it
# (same rule already taught for a 07:00 earnings release). A 10:00 a.m. ET
# non-PFEI is after the open, so filling that signal at that day's open is
# look-ahead (same idea as FOMC 14:00). This is an event-timestamp literacy
# item, not a CPI or payroll trading strategy.

PFEI = (
    "Employment Situation",
    "Consumer Price Index",
    "Producer Price Indexes",
    "U.S. Import and Export Price Indexes",
    "Real Earnings",
    "Employment Cost Index",
    "Productivity and Costs",
)
PFEI_TIME = "8:30 a.m. Eastern Time"
NON_PFEI_TIME = "10:00 a.m. Eastern Time"
print(f"seven PFEIs scheduled for {PFEI_TIME} on the public-calendar date:")
for name in PFEI:
    print(f"  {name}")
check(len(PFEI) == 7, "seven PFEIs")
print(f"non-PFEI releases are scheduled for {NON_PFEI_TIME} on the public-calendar date")
check(PFEI_TIME != NON_PFEI_TIME, "do not write that every BLS release is at 8:30")

cpi = datetime(2026, 12, 10, 8, 30, tzinfo=EDT)
print(f"CPI for November 2026: scheduled {cpi:%Y-%m-%d} at {cpi:%H:%M} Eastern Time")
check(cpi.date() == date(2026, 12, 10) and (cpi.hour, cpi.minute) == (8, 30), "CPI Home date and 8:30 a.m. ET")

REGULAR_OPEN = datetime(2026, 12, 10, 9, 30, tzinfo=EDT)


def can_fill_at_that_days_open(release_dt, open_dt):
    return release_dt <= open_dt


print(f"PFEI 8:30 a.m. ET on 2026-12-10: fill at that day's 09:30 open? {can_fill_at_that_days_open(cpi, REGULAR_OPEN)}")
check(can_fill_at_that_days_open(cpi, REGULAR_OPEN) is True, "8:30 is before the 09:30 open")
non_pfei = datetime(2026, 12, 10, 10, 0, tzinfo=EDT)
print(f"non-PFEI 10:00 a.m. ET on 2026-12-10: fill at that day's 09:30 open? {can_fill_at_that_days_open(non_pfei, REGULAR_OPEN)} (look-ahead)")
check(can_fill_at_that_days_open(non_pfei, REGULAR_OPEN) is False, "10:00 is after the open, like FOMC 14:00")
print("use the official BLS calendar for the date; this toy does not invent a first-Friday rule")

print(f"assertions passed: {checks}/{checks}")
print("ASSERT_event_time_ipo_ok")
print("disclaimer: official BLS times; no CPI or payroll strategy; learning only")

print("=== E. Fed G.17 9:15 a.m. vs annual revision at noon; BEA 8:30 vs 10:00 ===")
# Federal Reserve G.17 page (opened 2026-11-12): "The G.17 release will be
# issued on the following dates. The monthly releases are issued at 9:15 a.m.
# The annual revision is issued at noon." 2026 dates include November 17 and
# November 24 (annual revision).
# BEA Release Schedule (page last modified 11/11/26): GDP (Second Estimate)
# and Corporate Profits, 3rd Quarter 2026, and Personal Income and Outlays,
# October 2026, on November 25, 2026 at 8:30 AM. Other items on the same page
# include 10:00 AM rows.
# Regular US equity trading opens at 09:30 ET. A monthly G.17 at 9:15 a.m. is
# already out before that open. A G.17 annual revision issued at noon cannot
# be filled at that day's 09:30 open. A BEA 8:30 AM GDP release can; a
# 10:00 AM BEA item cannot. Same look-ahead idea as the already-taught BLS /
# FOMC clocks. Do not copy the BLS sentence "All seven PFEIs are scheduled
# for 8:30 a.m." onto every US PFEI — that sentence is about BLS's seven
# PFEIs. Do not invent a clock for Fed G.19 (official page: "around the fifth
# business day of each month," with no time of day). No first-Friday rule.
# No macro-trading strategy.
# November 2026 is US standard time; times below are Eastern Time.

EST = timezone(timedelta(hours=-5))
g17_monthly = datetime(2026, 11, 17, 9, 15, tzinfo=EST)
g17_annual = datetime(2026, 11, 24, 12, 0, tzinfo=EST)
bea_gdp = datetime(2026, 11, 25, 8, 30, tzinfo=EST)
bea_1000 = datetime(2026, 11, 25, 10, 0, tzinfo=EST)
open_1117 = datetime(2026, 11, 17, 9, 30, tzinfo=EST)
open_1124 = datetime(2026, 11, 24, 9, 30, tzinfo=EST)
open_1125 = datetime(2026, 11, 25, 9, 30, tzinfo=EST)

print("The monthly releases are issued at 9:15 a.m. The annual revision is issued at noon.")
print(f"monthly G.17 9:15 a.m. on 2026-11-17: fill at that day's 09:30 open? {can_fill_at_that_days_open(g17_monthly, open_1117)}")
check(can_fill_at_that_days_open(g17_monthly, open_1117) is True, "monthly 9:15 is before the 09:30 open")
print(f"annual revision at noon on 2026-11-24: fill at that day's 09:30 open? {can_fill_at_that_days_open(g17_annual, open_1124)}")
check(can_fill_at_that_days_open(g17_annual, open_1124) is False, "noon annual revision cannot fill at 09:30")
print(f"BEA GDP second estimate 2026-11-25 8:30 AM: fill at that day's 09:30 open? {can_fill_at_that_days_open(bea_gdp, open_1125)}")
check(can_fill_at_that_days_open(bea_gdp, open_1125) is True, "BEA 8:30 can fill at that open")
print(f"a 10:00 AM BEA item on the same calendar: fill at that day's 09:30 open? {can_fill_at_that_days_open(bea_1000, open_1125)} (look-ahead)")
check(can_fill_at_that_days_open(bea_1000, open_1125) is False, "BEA 10:00 cannot fill at that open")
print("do not copy the BLS sentence 'All seven PFEIs are scheduled for 8:30 a.m.' onto every US PFEI")
print("this toy does not invent a G.19 clock or a first-Friday rule")

print(f"assertions passed: {checks}/{checks}")
print("ASSERT_event_time_ipo_ok")
print("disclaimer: official Fed / BEA times; no macro strategy; learning only")

print("=== F. FINRA 5130: a new issue is an equity IPO, not every offering ===")
# FINRA Rule 5130 (opened 2026-11-12): a member or a person associated with a
# member "may not sell, or cause to be sold, a new issue to any account in
# which a restricted person has a beneficial interest, except as otherwise
# permitted herein." "New issue" means any initial public offering of an
# equity security as defined in Section 3(a)(11) of the Exchange Act, made
# pursuant to a registration statement or offering circular, and shall not
# include the official carve-outs (including preferred, convertibles,
# registered investment companies, rights / exchange / merger offerings, and
# ordinary shares or Form F-6 ADRs with a pre-existing market outside the
# United States). Listed exemptions include a registered investment company
# and an account in which restricted-person beneficial interests do not
# exceed in the aggregate 10%. This toy is not a restricted-person or
# exemption engine. FINRA 5131 is a different rule and is not taught here.
# Do not treat a follow-on, a preferred or convertible offering, or a
# security that already traded abroad, as automatically a 5130 new issue.
# The already-taught offering-price / lock-up facts stay as they are.
# No product, broker, or allocation recommendation.

print("a member may not sell a new issue to an account in which a restricted person has a beneficial interest, except as the rule permits")
print("new issue means an initial public offering of an equity security, made pursuant to a registration statement or offering circular")
print("the offering-price first-day return is not a fill every account could have earned")

def is_5130_new_issue(kind):
    # Official "shall not include" list plus the definition: a new issue is an
    # equity IPO, not every offering. This is a teaching classifier, not a
    # restricted-person / exemption engine.
    if kind in {
        "follow-on",
        "preferred",
        "convertible",
        "already-traded-abroad",
        "registered investment company",
    }:
        return False
    return kind == "equity IPO"

rows = (
    ("equity IPO", True),
    ("follow-on / additional offering of already-public stock", False),
)
# Map labels used in the print to the classifier keys.
key = {
    "equity IPO": "equity IPO",
    "follow-on / additional offering of already-public stock": "follow-on",
}
for label, expect in rows:
    got = is_5130_new_issue(key[label])
    print(f"  {label}: 5130 new issue? {got}")
    check(got is expect, label)

carveouts = {
    "preferred offering": "preferred",
    "convertible offering": "convertible",
    "ordinary shares or Form F-6 ADRs with a pre-existing market outside the United States": "already-traded-abroad",
}
for label, kind in carveouts.items():
    in_list = not is_5130_new_issue(kind)
    print(f"  {label}: in the official shall-not-include list? {in_list}")
    check(in_list is True, label)

print("restricted-person categories and listed exemptions exist (including a registered investment company,")
print("  and an account in which restricted-person beneficial interests do not exceed in the aggregate 10%);")
print("  this toy is not that engine")
print("FINRA 5131 is a different rule (new-issue allocation / spinning) and is not taught here")
print("no product, broker, or allocation recommendation")
print(f"assertions passed: {checks}/{checks}")
print("ASSERT_event_time_ipo_ok")
print("disclaimer: official allocation rule; no product, broker, or allocation recommendation; learning only")
