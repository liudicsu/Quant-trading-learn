"""P1 lab 06: official close vs last trade, NYSE MOC/LOC cutoff, tiered round lots (offline).
Learning only — not investment advice.

A. Official closing price (closing auction) is not always the consolidated last trade.
B. "Signal from today's close, filled at the same close" is look-ahead unless the signal
   is ready before the NYSE MOC/LOC entry cutoff (3:50 p.m. ET, NYSE-listed stocks; other venues differ).
C. Tiered round lots per 17 CFR 242.600(b)(93) (in effect since 2025-11-03):
   <=$250.00 -> 100, $250.01-$1,000 -> 40, $1,000.01-$10,000 -> 10, >=$10,000.01 -> 1 share.
D. Odd-lot quotes (BOLO, since 2026-04-27) do not change the NBBO.
Sources checked_on 2026-11-10: nyse.com/trade/auctions, eCFR 242.600(b)(93), UTP SIP Odd Lot FAQ v1.2.
"""
from __future__ import annotations
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

NY, SH = ZoneInfo("America/New_York"), ZoneInfo("Asia/Shanghai")
checks = 0


def check(cond: bool, msg: str) -> None:
    global checks
    assert cond, msg
    checks += 1


print("=== A. official close vs last trade (synthetic day) ===")
day = {"last_trade_1559_59": 100.07, "official_close_auction": 100.03, "after_hours_last": 100.40}
print(f"last trade 15:59:59 {day['last_trade_1559_59']} | official close (auction) {day['official_close_auction']} | after-hours last {day['after_hours_last']}")
check(day["official_close_auction"] != day["last_trade_1559_59"], "official close can differ from last trade")
data_note = {"close_field": "official_close_auction"}
check(data_note["close_field"] in day, "the close field used must be written in the data note")
print(f"data note: close field = {data_note['close_field']} (after-hours trades do not change it)")

print("=== B. NYSE MOC/LOC cutoff 15:50 ET ===")
CUTOFF = time(15, 50)


def moc_ok(signal_ready_et: str, venue: str = "NYSE") -> bool:
    if venue != "NYSE":
        raise ValueError("toy only models NYSE-listed stocks; other venues have different schedules")
    h, m = map(int, signal_ready_et.split(":"))
    return time(h, m) < CUTOFF


for t in ("15:45", "15:55", "16:00"):
    print(f"signal ready {t} ET -> free MOC entry allowed: {moc_ok(t)}")
check(moc_ok("15:45") is True, "15:45 before cutoff")
check(moc_ok("15:55") is False, "15:55 after cutoff (only imbalance-offsetting orders, no cancels)")
check(moc_ok("16:00") is False, "a signal computed from the 16:00 close cannot trade at that close")
for d in (date(2026, 7, 1), date(2026, 12, 1)):
    sh = datetime.combine(d, CUTOFF, NY).astimezone(SH)
    print(f"{d} 15:50 ET = Shanghai {sh:%Y-%m-%d %H:%M}")
check(datetime.combine(date(2026, 7, 1), CUTOFF, NY).astimezone(SH).strftime("%m-%d %H:%M") == "07-02 03:50", "DST")
check(datetime.combine(date(2026, 12, 1), CUTOFF, NY).astimezone(SH).strftime("%m-%d %H:%M") == "12-02 04:50", "standard time")

print("=== C. tiered round lots (prior evaluation-period avg close) ===")


def round_lot(avg_close: float) -> int:
    if avg_close <= 250.00:
        return 100
    if avg_close <= 1000.00:
        return 40
    if avg_close <= 10000.00:
        return 10
    return 1


for px in (250.00, 250.01, 1000.00, 1000.01, 10000.00, 10000.01):
    print(f"avg close ${px:,.2f} -> round lot {round_lot(px)}")
for px, lot in ((250.00, 100), (250.01, 40), (1000.00, 40), (1000.01, 10), (10000.00, 10), (10000.01, 1)):
    check(round_lot(px) == lot, f"round lot at {px}")


def display_size(shares: int, lot: int) -> int:
    # Reg NMS 600(b)(26)(iii) states this for competing consolidators; check your feed's own spec.
    return shares // lot * lot


def is_odd_lot(shares: int, lot: int) -> bool:
    return shares < lot


print(f"135 shares at lot 40 -> displayed {display_size(135, 40)}; 39 shares odd lot: {is_odd_lot(39, 40)}")
check(display_size(135, 40) == 120, "display rounds down to whole round lots")
check(is_odd_lot(39, 40) is True, "39 < 40 is an odd lot")


def operative_period(d: date) -> tuple[str, str, str]:
    # Nov assignment (first business day of Nov) uses September; May uses March. Fixture for 2026-27 only.
    if date(2026, 11, 2) <= d <= date(2027, 4, 30):
        return ("2026-11-02", "2027-04-30", "Sep-2026 evaluation")
    raise ValueError("fixture covers 2026-11-02..2027-04-30 only")


print(f"2026-11-10 operative period: {operative_period(date(2026, 11, 10))}")
check(operative_period(date(2026, 11, 10)) == ("2026-11-02", "2027-04-30", "Sep-2026 evaluation"), "operative period")

print("=== D. odd-lot quote does not move the NBBO (stock with lot 40) ===")
lot = round_lot(500.0)
bids = [("VENUE_A", 499.90, 80), ("VENUE_B", 499.95, 30)]   # 30 shares is an odd lot here
nbb = max((p for _, p, s in bids if s >= lot))
bolo_bid = max(p for _, p, s in bids if s < lot)
print(f"lot {lot}: NBB {nbb} (round lots only) | BOLO bid {bolo_bid} (odd lot, better price, not protected)")
check(nbb == 499.90 and bolo_bid == 499.95, "NBBO ignores the better odd-lot bid")

print(f"assertions passed: {checks}/{checks}")
print("ASSERT_close_roundlot_ok")
print("disclaimer: synthetic fixtures; learning only")
