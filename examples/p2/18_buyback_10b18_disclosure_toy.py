"""Rule 10b-18 safe-harbor volume and timing, and Item 703 disclosure lag
(checked 2026-11-11; section E 2026-11-12).

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

- 17 CFR 240.10b-18(b)(2)(iv) and the SEC 10b-18 FAQ (Timing Condition, last
  reviewed 2016-12-02): limited after-hours safe harbor until last-sale reporting
  ends in the consolidated system; not the opening transaction of that session;
  price cap is the lower of the principal-market close and any later lower bid
  or sale; volume and other conditions still apply. Official 10b-18 sources have
  not mapped this window onto 21:00-04:00 overnight / 23/5.

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


print("=== E. after-hours prong: not the opening print; price cap; volume still counts ===")
# 17 CFR 240.10b-18(b)(2)(iv): purchases may be effected following the close of the
# primary trading session until last-sale prices cease to be reported in the
# consolidated system, so long as: not the opening transaction of that session;
# the price does not exceed the lower of the primary-market close and any later
# lower bid or sale in the consolidated system; and the other conditions (including
# the day's volume limit) are met. The issuer may use one broker in this period
# that may be different from the primary-session broker.
primary_close = 40.00
later_prints = (39.80, 39.90)  # later lower bid or sale in the consolidated system
cap = min(primary_close, min(later_prints))
print(f"  primary-market close {primary_close:.2f}; later lower bid or sale {min(later_prints):.2f} -> price cap {cap:.2f} (lower of the two)")
check(cap == 39.80, "cap is the lower of the primary close and any later lower bid or sale")
print("  after-hours purchase at 39.80: inside the price condition; at 39.81: outside")
check(39.80 <= cap and 39.81 > cap, "39.80 at the cap; 39.81 over")
print("  the purchase may not be the opening transaction of the session following the primary close")
print("  the day's 25% ADTV volume limit still applies to after-hours Rule 10b-18 purchases")
print("  the issuer may use one broker in this period that may be different from the primary-session broker")
print("  official 10b-18 sources (FAQ last reviewed 2016-12-02; NYSE ETH FAQ does not discuss 10b-18)")
print("  have not mapped this window onto 21:00-04:00 overnight / 23/5; this toy does not fill that gap")

print(f"OK {checks} assertions")
