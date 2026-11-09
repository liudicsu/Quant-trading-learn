"""P6 lab 10: MWCB Level 3 resumption under 23/5 trading (offline toy).
NYSE SR-NYSE-2026-43 (SEC 34-106380, checked_on 2026-11-10) replaces "remainder of the trading day" with:
trading halts on the Exchange until 4:00 a.m. ET or later on the following trading day. Other SROs say they
intend to file the same change; this toy models the NYSE (SR-NYSE-2026-43) and Nasdaq (SR-NASDAQ-2026-080) rule text; check each venue. Learning only — not investment advice.
"""
from __future__ import annotations
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")
checks = 0


def check(cond: bool, msg: str) -> None:
    global checks
    assert cond, msg
    checks += 1


def next_trading_day(d: date) -> date:   # toy calendar: weekdays only
    d += timedelta(days=1)
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d


def level(decline: float) -> int:
    return 3 if decline >= 0.20 else 2 if decline >= 0.13 else 1 if decline >= 0.07 else 0


def earliest_resume_l3(trigger: datetime) -> datetime:
    return datetime.combine(next_trading_day(trigger.date()), time(4, 0), NY)


def order_status(ts: datetime, l3_trigger: datetime) -> str:
    return "rejected (MWCB L3 halt)" if l3_trigger <= ts < earliest_resume_l3(l3_trigger) else "not blocked by the L3 halt (actual reopening may be later)"


trig = datetime(2026, 12, 9, 13, 0, tzinfo=NY)   # Wednesday, synthetic 20% S&P 500 decline
print(f"S&P 500 decline 7% / 13% / 20% -> levels {level(0.07)} / {level(0.13)} / {level(0.20)}")
print(f"Level 3 at {trig:%Y-%m-%d %H:%M} ET -> earliest resume {earliest_resume_l3(trig):%Y-%m-%d %H:%M} ET (or later)")
same_night = datetime(2026, 12, 9, 21, 0, tzinfo=NY)
next_morning = datetime(2026, 12, 10, 4, 0, tzinfo=NY)
for ts in (same_night, next_morning):
    print(f"order at {ts:%Y-%m-%d %H:%M} ET -> {order_status(ts, trig)}")
fri = datetime(2026, 12, 11, 14, 0, tzinfo=NY)
print(f"Level 3 on Friday {fri:%Y-%m-%d} -> earliest resume {earliest_resume_l3(fri):%Y-%m-%d %H:%M} ET")
check([level(x) for x in (0.07, 0.13, 0.20)] == [1, 2, 3], "7/13/20% levels")
check(earliest_resume_l3(trig) == next_morning, "resume >= 04:00 ET next trading day")
check(order_status(same_night, trig).startswith("rejected"), "no overnight session the same night")
check(earliest_resume_l3(fri).date() == date(2026, 12, 14), "Friday -> Monday 04:00 ET")
print(f"assertions passed: {checks}/{checks}")
print("ASSERT_mwcb_resume_ok")
print("disclaimer: toy calendar (weekdays only); NYSE + Nasdaq rule text; other exchanges coordinating; learning only")
