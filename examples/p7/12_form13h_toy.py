"""Form 13H identifying-activity level (checked 2026-11-12).

Sources:
- 17 CFR 240.13h-1(a)(7): identifying activity level means aggregate transactions
  in NMS securities equal to or greater than, during a calendar day, either two
  million shares or shares with a fair market value of $20 million; or during a
  calendar month, either twenty million shares or shares with a fair market value
  of $200 million.
- 17 CFR 240.13h-1(c)(1): do not subtract, offset, or net purchase and sale
  transactions, in equity securities or option contracts, and among or within
  accounts. Equity options: aggregate the volume or fair market value of the
  underlying. Index options: aggregate the fair market value of the option
  transactions. Purchases or sales of the underlying pursuant to exercises or
  assignments are excluded from "transaction" (13h-1(a)(6)).
- SEC Large Trader Reporting FAQ (last reviewed or updated 2016-02-22) Q1.2:
  "transactions not be netted within or among accounts."
- Form 13H instructions: a non-voluntary Initial Filing must be submitted
  promptly after first effecting an aggregate number of transactions equal to
  or greater than the identifying activity level. The Form, the rule, and the
  FAQ do not define "promptly" as a fixed number of days. Annual filing within
  45 days after the end of each full calendar year. The Commission will treat
  as confidential the information collected pursuant to this Form.

Synthetic accounts. Learning only; not a registration or broker recommendation,
and not a public point-in-time filing like Form 4 / 13D / 13G / 13F.
"""

checks = 0


def check(cond, label):
    global checks
    assert cond, label
    checks += 1


DAY_SHARES, DAY_VALUE = 2_000_000, 20_000_000
MONTH_SHARES, MONTH_VALUE = 20_000_000, 200_000_000


def crosses(shares, value, shares_th, value_th):
    return shares >= shares_th or value >= value_th


print("=== A. calendar-day identifying activity level; do not net ===")
# Two accounts: account 1 buys 1.2m shares ($12m); account 2 sells 1.0m shares ($10m).
acct1_buy_sh, acct1_buy_val = 1_200_000, 12_000_000
acct2_sell_sh, acct2_sell_val = 1_000_000, 10_000_000
gross_sh = acct1_buy_sh + acct2_sell_sh
gross_val = acct1_buy_val + acct2_sell_val
netted_sh = abs(acct1_buy_sh - acct2_sell_sh)
netted_val = abs(acct1_buy_val - acct2_sell_val)
print(f"  account 1 buy {acct1_buy_sh:,} shares (${acct1_buy_val:,}); account 2 sell {acct2_sell_sh:,} shares (${acct2_sell_val:,})")
print(f"  aggregate (no netting) {gross_sh:,} shares / ${gross_val:,} -> crosses day threshold? {crosses(gross_sh, gross_val, DAY_SHARES, DAY_VALUE)}")
print(f"  if you netted within/among accounts: {netted_sh:,} shares / ${netted_val:,} -> would look like a miss: {crosses(netted_sh, netted_val, DAY_SHARES, DAY_VALUE)}")
check(crosses(gross_sh, gross_val, DAY_SHARES, DAY_VALUE), "2.2m shares crosses the 2m day test")
check(not crosses(netted_sh, netted_val, DAY_SHARES, DAY_VALUE), "netting would hide the crossing")
print("  FAQ Q1.2 / Rule 13h-1(c)(1): do not net within or among accounts")

# Value-only day: 1.5m shares at $15 = $22.5m, under the share test, over the $20m test.
val_sh, val_val = 1_500_000, 22_500_000
print(f"  1,500,000 shares at ${val_val:,} FMV: shares test? {val_sh >= DAY_SHARES}; value test? {val_val >= DAY_VALUE}; crosses? {crosses(val_sh, val_val, DAY_SHARES, DAY_VALUE)}")
check(crosses(val_sh, val_val, DAY_SHARES, DAY_VALUE) and val_sh < DAY_SHARES, "value test alone can cross")

print("=== B. calendar-month identifying activity level ===")
# 18m shares / $180m is under both monthly tests; 21m shares crosses shares; $210m crosses value.
print(f"  18,000,000 shares / $180,000,000 -> crosses month threshold? {crosses(18_000_000, 180_000_000, MONTH_SHARES, MONTH_VALUE)}")
print(f"  21,000,000 shares / $180,000,000 -> crosses month threshold? {crosses(21_000_000, 180_000_000, MONTH_SHARES, MONTH_VALUE)}")
print(f"  18,000,000 shares / $210,000,000 -> crosses month threshold? {crosses(18_000_000, 210_000_000, MONTH_SHARES, MONTH_VALUE)}")
check(not crosses(18_000_000, 180_000_000, MONTH_SHARES, MONTH_VALUE), "under both monthly tests")
check(crosses(21_000_000, 180_000_000, MONTH_SHARES, MONTH_VALUE), "month share test")
check(crosses(18_000_000, 210_000_000, MONTH_SHARES, MONTH_VALUE), "month value test")

print("=== C. equity-option underlying counts; exercise of the underlying does not ===")
# 8,000 call contracts x 100 = 800,000 underlying shares, plus 1,300,000 shares of stock.
# That is 2,100,000 shares, which crosses the day share test.
# A later exercise of 2,000 of those contracts (200,000 shares) is excluded.
stock_sh = 1_300_000
option_contracts, multiplier = 8_000, 100
option_underlying = option_contracts * multiplier
exercise_sh = 2_000 * multiplier
counted = stock_sh + option_underlying
wrong = counted + exercise_sh
print(f"  stock purchases {stock_sh:,} shares")
print(f"  equity calls {option_contracts:,} contracts x {multiplier} = {option_underlying:,} underlying shares (counted)")
print(f"  later exercise of 2,000 contracts = {exercise_sh:,} shares of the underlying (excluded)")
print(f"  counted total {counted:,} shares -> crosses day threshold? {crosses(counted, 0, DAY_SHARES, DAY_VALUE)}")
print(f"  if exercises were added, total would be {wrong:,} (do not add them)")
check(counted == 2_100_000 and crosses(counted, 0, DAY_SHARES, DAY_VALUE), "underlying volume counts")
check(not crosses(stock_sh, 0, DAY_SHARES, DAY_VALUE), "stock alone is under")
check(wrong == 2_300_000, "exercise figure is only for the foil")
print("  index options: aggregate the fair market value of the option transactions, not an underlying share count")
print("  after first crossing, file Form 13H promptly (the Form, the rule, and the FAQ do not say 'promptly = 10 days')")
print("  then file annually within 45 days after each full calendar year; disclose LTID and accounts to each broker")
print("  the Form is confidential; it is not a public PIT source like Form 4 / 13D / 13G / 13F")

print(f"assertions passed: {checks}/{checks}")
