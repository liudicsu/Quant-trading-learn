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
