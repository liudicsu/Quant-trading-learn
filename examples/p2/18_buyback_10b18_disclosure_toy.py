"""Rule 10b-18 safe-harbor volume and timing, and Item 703 disclosure lag
(checked 2026-11-11).

Sources:
- 17 CFR 240.10b-18: voluntary safe harbor; each of the four daily conditions must be met or
  that day's purchases fall outside the harbor. ADTV = average daily trading volume reported
  for the security during the four calendar weeks preceding the week of the purchase.
  Volume: 25% of ADTV, except once a week the issuer may effect one block purchase in lieu of
  the 25% limit if it makes no other Rule 10b-18 purchases that day (and that block is left
  out of later ADTV). Timing: not the opening (regular way) purchase reported in the
  consolidated system; last 10 minutes before the scheduled close in the principal market
  (and in the market of the purchase) if ADTV value is $1 million or more and public float
  value is $150 million or more; otherwise last 30 minutes. Price: not higher than the higher
  of the highest independent bid and the last independent transaction price.
- 17 CFR 229.703 (Item 703): monthly aggregate repurchase table in Forms 10-Q and 10-K.
- SEC, "Further Announcement Regarding Share Repurchase Disclosure Modernization Rule"
  (2024-02-09): Fifth Circuit vacatur 2023-12-19; disclosure requirements revert to those in
  effect before the vacated rule. Technical amendments, 89 FR 24372 (2024-04-08).

Synthetic figures. Learning only; not a buyback or trading signal. The safe harbor is
optional and is not a required trading rule.
"""
from datetime import date

checks = 0


def check(cond, label):
    global checks
    assert cond, label
    checks += 1


print("=== A. volume: 25% of four-week ADTV ===")
# Four preceding calendar weeks, shares traded (zeros for days the market was open but no
# prints would still enter the average; holidays when the market is closed would not).
WEEK_VOLUMES = (800_000, 1_000_000, 1_200_000, 1_000_000)
adtv = sum(WEEK_VOLUMES) / 4
cap = 0.25 * adtv
print(f"four-week volumes {WEEK_VOLUMES} -> ADTV {adtv:,.0f} -> 25% cap {cap:,.0f} shares")
check(adtv == 1_000_000 and cap == 250_000, "ADTV and 25% cap")
check(250_000 <= cap and 250_001 > cap, "250,000 is at the cap; 250,001 is over")
print("purchases 250,000 shares: inside the volume condition; 250,001: outside (and then the whole day is outside the harbor)")

print("=== B. once-a-week block in lieu of the 25% cap ===")
block = 400_000
print(f"one block of {block:,} shares and no other Rule 10b-18 purchases that day: volume condition met via the weekly block exception")
print("same block plus any other Rule 10b-18 purchase that day: volume condition fails")
check(block > cap, "the block is larger than 25% of ADTV")
# The excepted block is left out of later ADTV calculations (rule text).

print("=== C. timing: last 10 vs last 30 minutes, measured from the scheduled close ===")


def restricted_window_minutes(adtv_value, public_float):
    if adtv_value >= 1_000_000 and public_float >= 150_000_000:
        return 10
    return 30


def window_start(scheduled_close_hm, minutes):
    h, m = map(int, scheduled_close_hm.split(":"))
    total = h * 60 + m - minutes
    return f"{total // 60:02d}:{total % 60:02d}"


print(
    f"ADTV value $2,000,000 and public float $200,000,000 -> last {restricted_window_minutes(2_000_000, 200_000_000)} minutes "
    f"(regular close 16:00 starts at {window_start('16:00', 10)}; early close 13:00 starts at {window_start('13:00', 10)})"
)
print(
    f"ADTV value $400,000 and public float $80,000,000 -> last {restricted_window_minutes(400_000, 80_000_000)} minutes "
    f"(regular close starts at {window_start('16:00', 30)})"
)
check(restricted_window_minutes(2_000_000, 200_000_000) == 10, "actively traded: 10 minutes")
check(restricted_window_minutes(400_000, 80_000_000) == 30, "other securities: 30 minutes")
check(window_start("16:00", 10) == "15:50" and window_start("13:00", 10) == "12:50", "window follows the scheduled close")
print("also: a Rule 10b-18 purchase must not be the opening (regular way) purchase reported in the consolidated system")
print("the issuer must not pay more than the higher of the highest independent bid and the last independent transaction price")

print("=== D. Item 703 is monthly, and you see it when the 10-Q/10-K is filed ===")
# Issuer bought in January; Q1 10-Q filed 2026-05-06 (a statutory-deadline-style date, not a prediction).
january_shares = 1_200_000
filed = date(2026, 5, 6)


def item703_known(decision_date):
    return decision_date >= filed


for d in (date(2026, 2, 2), date(2026, 5, 5), date(2026, 5, 6)):
    known = item703_known(d)
    print(f"decision {d.isoformat()}: January Item 703 monthly total known? {known}")
check(not item703_known(date(2026, 2, 2)), "February is too early")
check(not item703_known(date(2026, 5, 5)), "day before the 10-Q")
check(item703_known(date(2026, 5, 6)), "on the filing date, after the file is public")
print(f"when known, Item 703 reports the January total {january_shares:,} shares (a monthly aggregate, not a daily tape)")
print("the 2023 daily Form SR / repurchase-modernization rule was vacated 2023-12-19; disclosure reverted to Item 703")
print("a board authorization press release is not the same as executed daily volume")

print(f"OK {checks} assertions")
