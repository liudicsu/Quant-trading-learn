"""OCC exercise-by-exception threshold for expiring equity options (checked 2026-11-11).

Sources:
- OIC Options Exercise FAQ, quoting OCC Rule 805 and Interpretation .02:
  OCC exercises expiring options that are in-the-money by the specified threshold
  unless the clearing member submits instructions not to exercise. Equity options:
  $0.01 per contract in-the-money in customer, firm and market-maker accounts.
  The threshold is an administrative convenience between OCC and clearing members
  and "is not intended to dictate to clearing members which positions in customers'
  accounts should or must be exercised." A broker may use a different customer
  threshold. People sometimes incorrectly call this "automatic exercise."
- In-the-money is measured from the official closing price of the underlying vs the
  strike (OIC: "the difference between the exercise price and the closing price").
- Assignment of one standard equity call (unit of trading 100 shares, already taught
  from the OCC ODD) leaves the writer short 100 shares; a put assignment leaves the
  writer long 100 shares. Stock-option exercise/assignment settles T+1 (ODD p.57).

Learning only; not a recommendation to write or exercise options.
"""
from decimal import Decimal

checks = 0


def check(cond, label):
    global checks
    assert cond, label
    checks += 1


THRESHOLD = Decimal("0.01")


def itm_amount(kind, strike, close):
    strike = Decimal(str(strike))
    close = Decimal(str(close))
    if kind == "call":
        return close - strike
    if kind == "put":
        return strike - close
    raise ValueError(kind)


def exception_exercise(kind, strike, close):
    return itm_amount(kind, strike, close) >= THRESHOLD


print("=== OCC exercise-by-exception ($0.01 in-the-money, unless contrary instructions) ===")
cases = (
    ("call", 100, 100.01, True),
    ("call", 100, 100.00, False),
    ("call", 100, 99.99, False),
    ("put", 100, 99.99, True),
    ("put", 100, 100.00, False),
    ("put", 100, 100.01, False),
)
for kind, strike, close, expect in cases:
    amt = itm_amount(kind, strike, close)
    got = exception_exercise(kind, strike, close)
    print(f"  {kind} K={strike} close={close} ITM={amt} -> exception exercise? {got}")
    check(got is expect, f"{kind} {close}")

print("a clearing member may still instruct OCC not to exercise an ITM option, or to exercise one that is below the threshold")
print("this procedure is between OCC and clearing members; a broker may use a different customer threshold")

print("=== Assignment creates a stock position (standard 100-share equity contract) ===")
assigned_call_shares = -100  # writer delivered 100 shares
assigned_put_shares = 100    # writer bought 100 shares
print(f"writer assigned on 1 call: stock position {assigned_call_shares} shares")
print(f"writer assigned on 1 put: stock position {assigned_put_shares} shares")
check(assigned_call_shares == -100 and assigned_put_shares == 100, "assignment")
print("those stock trades settle T+1 after exercise; a backtest that 'expires worthless' every option will miss this inventory")
print(f"assertions passed: {checks}/{checks}")
