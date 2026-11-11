"""NYSE early-close MOC/LOC cutoff, and Nasdaq vs NYSE regular-day close cutoffs
(checked 2026-11-11).

Sources:
- NYSE Rule 7.35(a)(8), as quoted in NYSE Regulatory Memo 3.20.2026 n.2: "Closing Auction
  Imbalance Freeze Time" means 10 minutes before the scheduled end of Core Trading Hours.
  Specific clock times such as 3:50 p.m. apply on days the scheduled close is 4 p.m.; "On days
  when the NYSE is scheduled to close at a time other than 4 p.m., such deadlines—tied to the
  scheduled end of Core Trading Hours—move accordingly."
- NYSE Group 2026–2028 holiday and early-closings calendar (ICE press; also the NYSE 2026
  yearly calendar PDF and nyse.com/trade/hours-calendars): cash equity markets close at
  1:00 p.m. ET on 2026-11-27 (the day after Thanksgiving) and 2026-12-24.
- Nasdaq Closing Cross FAQ: 3:50 p.m. ET early dissemination; MOC/LOC/IO may not be canceled
  or modified after 3:50; Nasdaq stops accepting MOC orders at 3:55 p.m. ET; LOC orders may be
  entered until 3:58 p.m. ET. The FAQ states these as clock times against a 4:00 p.m. close;
  this script does not invent Nasdaq early-close times.
- NYSE Auctions page: 3:50 p.m. cutoff for free MOC/LOC entry on a regular day.

Synthetic times only. Learning only; not a trading recipe.
"""
from datetime import date, datetime, time, timedelta, timezone

checks = 0


def check(cond, label):
    global checks
    assert cond, label
    checks += 1


def nyse_moc_free_entry_cutoff(scheduled_close):
    """Latest time a new MOC/LOC may be entered freely (before the imbalance freeze)."""
    h, m = scheduled_close.hour, scheduled_close.minute
    total = h * 60 + m - 10
    return time(total // 60, total % 60)


print("=== A. NYSE early-close days: freeze is 10 minutes before the scheduled close ===")
EARLY_CLOSES_2026 = (date(2026, 11, 27), date(2026, 12, 24))
regular_close = time(16, 0)
early_close = time(13, 0)
print(f"regular day scheduled close {regular_close.strftime('%H:%M')} ET -> MOC/LOC free-entry cutoff {nyse_moc_free_entry_cutoff(regular_close).strftime('%H:%M')} ET")
print(f"early-close day scheduled close {early_close.strftime('%H:%M')} ET -> MOC/LOC free-entry cutoff {nyse_moc_free_entry_cutoff(early_close).strftime('%H:%M')} ET")
check(nyse_moc_free_entry_cutoff(regular_close) == time(15, 50), "regular 15:50")
check(nyse_moc_free_entry_cutoff(early_close) == time(12, 50), "early 12:50")
print("2026 NYSE early closes at 13:00 ET:", ", ".join(d.isoformat() for d in EARLY_CLOSES_2026))
check(EARLY_CLOSES_2026 == (date(2026, 11, 27), date(2026, 12, 24)), "2026 early-close dates")

EST = timezone(timedelta(hours=-5))
CST = timezone(timedelta(hours=8))


def beijing(d, t):
    return datetime(d.year, d.month, d.day, t.hour, t.minute, tzinfo=EST).astimezone(CST)


for d in EARLY_CLOSES_2026:
    b = beijing(d, time(12, 50))
    print(f"{d.isoformat()} 12:50 ET = Shanghai {b:%Y-%m-%d %H:%M}")
    check((b.hour, b.minute) == (1, 50) and b.date() == d + timedelta(days=1), f"Beijing for {d}")

print("honest fill-at-the-close on an early-close day: signal ready before 12:50 ET, not before 15:50")
check(not (time(15, 0) < time(12, 50)), "15:00 is after the early-close cutoff")

print("=== B. regular 16:00 close: Nasdaq MOC/LOC cutoffs are later than NYSE 15:50 ===")
# NYSE: free MOC/LOC entry until 15:50 (then only offsetting).
# Nasdaq: cancels freeze at 15:50; new MOC accepted until 15:55; new LOC until 15:58.


def nasdaq_new_moc_accepted(t):
    return t < time(15, 55)


def nasdaq_new_loc_accepted(t):
    return t < time(15, 58)


def nyse_free_moc_loc(t):
    return t < time(15, 50)


for t in (time(15, 49), time(15, 50), time(15, 54), time(15, 55), time(15, 57), time(15, 58)):
    print(
        f"signal ready {t.strftime('%H:%M')} ET -> "
        f"NYSE free MOC/LOC: {nyse_free_moc_loc(t)}; "
        f"Nasdaq new MOC: {nasdaq_new_moc_accepted(t)}; "
        f"Nasdaq new LOC: {nasdaq_new_loc_accepted(t)}"
    )
check(nyse_free_moc_loc(time(15, 49)) and not nyse_free_moc_loc(time(15, 50)), "NYSE 15:50")
check(nasdaq_new_moc_accepted(time(15, 54)) and not nasdaq_new_moc_accepted(time(15, 55)), "Nasdaq MOC 15:55")
check(nasdaq_new_loc_accepted(time(15, 57)) and not nasdaq_new_loc_accepted(time(15, 58)), "Nasdaq LOC 15:58")
print("do not copy the NYSE 15:50 cutoff onto a Nasdaq-listed close-fill; do not invent Nasdaq early-close clock times")

print(f"OK {checks} assertions")
