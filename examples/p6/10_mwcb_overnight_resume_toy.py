"""P6 lab 10: MWCB Level 3 resumption under 23/5 trading (offline toy).
NYSE SR-NYSE-2026-43 (SEC 34-106380, checked_on 2026-11-10) replaces "remainder of the trading day" with:
trading halts on the Exchange until 4:00 a.m. ET or later on the following trading day. As of 2026-11-10 the
NYSE group (5), Nasdaq group (3), Cboe group (4), MEMX, MIAX Pearl, IEX, LTSE and MX2 had filed the same change
(immediately effective); none found yet for FINRA, Nasdaq BX, NYSE Chicago, 24X. Check each venue. Learning only.
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
sunday_night = datetime(2026, 12, 13, 20, 0, tzinfo=NY)
print(f"order at {sunday_night:%Y-%m-%d %H:%M} ET (Sunday) -> {order_status(sunday_night, fri)}")
check([level(x) for x in (0.07, 0.13, 0.20)] == [1, 2, 3], "7/13/20% levels")
check(earliest_resume_l3(trig) == next_morning, "resume >= 04:00 ET next trading day")
check(order_status(same_night, trig).startswith("rejected"), "no overnight session the same night")
check(earliest_resume_l3(fri).date() == date(2026, 12, 14), "Friday -> Monday 04:00 ET")
check(order_status(sunday_night, fri).startswith("rejected"), "Sunday overnight session still halted")
print(f"assertions passed: {checks}/{checks}")
print("ASSERT_mwcb_resume_ok")
print("disclaimer: toy calendar (weekdays only); filings by 17 exchanges, not all venues; learning only")

print('=== N7. FINRA Rule 6121.02(c)(2): filed, not-yet-implemented 23/5 Level 3 otherwise-than-on-an-exchange clock ===')
# FINRA Rule 6121.02(c)(2) taught as a filed, not-yet-implemented
# amendment (official SR-FINRA-2026-025 / 34-106879 / 91 FR 73851).
# Official current typography, still on the live FINRA rulebook page,
# is: "If a Level 3 Market Decline occurs at any time during the
# trading day, FINRA shall halt trading otherwise than on an exchange
# in all NMS stocks for the remainder of the trading day." Official
# future typography is: "FINRA shall halt trading otherwise than on an
# exchange in all NMS stocks until 4:00 a.m. Eastern Time or later on
# the following trading day." Official typography is "otherwise than
# on an exchange"; do not tidy into "off-exchange." Official
# implementation typography is "the implementation date of the proposed
# rule change will be December 6, 2026." Official FR comment-deadline
# typography is "should be submitted on or before December 8, 2026."
# The comment period is not the implementation date. Do not teach the
# future text as current law. Do not claim all venues have filed.
# The 2026-11-10 snapshot in the module docstring is left unchanged.
# Learning only; no venue, member, or investment advice.

print('FINRA has filed SR-FINRA-2026-025 / 34-106879')
print('official implementation typography is the implementation date of the proposed rule change will be December 6, 2026')
print('official FR comment-deadline typography is should be submitted on or before December 8, 2026')
print('the comment period is not the implementation date')
print('official current typography is still: If a Level 3 Market Decline occurs at any time during the trading day, FINRA shall halt trading otherwise than on an exchange in all NMS stocks for the remainder of the trading day.')
print('official future typography is: FINRA shall halt trading otherwise than on an exchange in all NMS stocks until 4:00 a.m. Eastern Time or later on the following trading day.')
print('official typography is otherwise than on an exchange; do not tidy into off-exchange')
print('do not teach the future text as current law; do not claim all venues have filed')
filed_not_current = True
print(f"  FINRA has filed SR-FINRA-2026-025 / 34-106879, official implementation typography is the implementation date of the proposed rule change will be December 6, 2026, official current typography is still for the remainder of the trading day, official future typography is until 4:00 a.m. Eastern Time or later on the following trading day, official typography is otherwise than on an exchange, and this is not current law and not a claim that all venues have filed? {filed_not_current}")
check(filed_not_current is True, "N7 filed amendment; current remainder typography; future 4:00 a.m.; not all venues")
print(f"assertions passed: {checks}/{checks}")
print('ASSERT_finra_612102_filed_ok')
print('disclaimer: official SR-FINRA-2026-025 / 34-106879; filed, not-yet-implemented; not all venues have filed; learning only')
