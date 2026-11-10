"""Official open vs "first trade at 09:30", and on-open order cutoffs (checked 2026-11-11).

Sources:
- NYSE Auctions page (nyse.com/trade/auctions): NYSE Opening Auction - order entry from 6:30 a.m.,
  imbalance publication from 8:00 a.m., "9:30 a.m. Opening auction process begins"; "Orders can be
  entered and cancelled until the security is opened by the DMM, which may occur after 9:30 a.m."
- Nasdaq "The Nasdaq Opening and Closing Crosses" FAQ (2025): the Opening Cross sets the Nasdaq Official
  Opening Price (NOOP); without a cross, the NOOP is the first last-sale eligible trade at or after
  9:30 a.m.; "MOOs ... entered after the cut-off at 9:28 a.m. ... are not accepted".
Synthetic prints only. Other exchanges use other schedules. Learning only.
"""
from datetime import datetime, time, timedelta, timezone

checks = 0


def check(cond, label):
    global checks
    assert cond, label
    checks += 1


print("=== A. the NYSE open can print after 09:30 ===")
open_print = time(9, 31, 40)  # synthetic: the DMM opened this stock at 09:31:40
bar_label = time(9, 30)
print(f"daily bar label 09:30, official open printed {open_print} -> do not assume the open is 09:30:00")
check(open_print > bar_label, "open after 09:30")

print("=== B. Nasdaq MOO entry cutoff 09:28 ET ===")


def moo_accepted(t):
    return t < time(9, 28)


for t in (time(9, 20), time(9, 27, 59), time(9, 28), time(9, 29)):
    print(f"signal ready {t} ET -> new MOO accepted for today's cross: {moo_accepted(t)}")
check(moo_accepted(time(9, 27, 59)), "before cutoff")
check(not moo_accepted(time(9, 28)), "at cutoff")
EDT = timezone(timedelta(hours=-4))
EST = timezone(timedelta(hours=-5))
CST = timezone(timedelta(hours=8))
s = datetime(2026, 7, 1, 9, 28, tzinfo=EDT).astimezone(CST)
w = datetime(2026, 12, 1, 9, 28, tzinfo=EST).astimezone(CST)
print(f"2026-07-01 09:28 ET = Shanghai {s:%Y-%m-%d %H:%M}; 2026-12-01 09:28 ET = Shanghai {w:%Y-%m-%d %H:%M}")
check((s.hour, s.minute) == (21, 28) and (w.hour, w.minute) == (22, 28), "Beijing time")

print("=== C. signal from today's open, filled at today's open = look-ahead ===")
official_open = 50.12
signal_uses = "today's official open"
fill_at = "today's official open"
print(f"signal uses {signal_uses}; fill at {fill_at} -> look-ahead: {signal_uses == fill_at}")
check(signal_uses == fill_at, "same price used twice")
print("honest options: (1) signal from data available before 09:28 ET -> MOO in today's cross;")
print(f"                (2) signal uses the official open ({official_open}) -> fill at a later tradable time")
print(f"assertions passed: {checks}/{checks}")
