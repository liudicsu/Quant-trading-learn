"""Where a non-zero risk-free rate comes from: T-bill discount quotes and point-in-time use (checked 2026-11-10).

Sources: TreasuryDirect "Understanding Pricing and Interest Rates" (Price = Face value (1 - (discount
rate x time)/360); $1,000 26-week bill at 0.145% -> $999.27); Treasury "Interest Rate Statistics"
(Daily Treasury Bill Rates are indicative closing bid quotes obtained by the New York Fed at about
3:30 PM each business day). T-bills are a teaching example of a risk-free proxy, not the only choice.
The "simple 365-day yield" below is a teaching formula; Treasury's COUPON EQUIVALENT column follows
Treasury's own method. Synthetic rates and returns; learning only, not investment advice.
"""
from datetime import date

checks = 0


def check(cond, label):
    global checks
    assert cond, label
    checks += 1


def bill_price(face, discount_rate, days):
    """TreasuryDirect: Price = Face value x (1 - discount rate x days / 360)."""
    return face * (1 - discount_rate * days / 360)


print("=== A. the discount rate is not your yield ===")
p = bill_price(1000, 0.00145, 182)
print(f"TreasuryDirect example (26 weeks, 0.145%): price {p:.5f} -> {round(p, 2):.2f}")
check(round(p, 2) == 999.27, "TreasuryDirect example price")
p91 = bill_price(1000, 0.04, 91)
hpr = 1000 / p91 - 1
simple365 = hpr * 365 / 91
print(f"4.00% discount, 91 days: price {p91:.4f}, holding return {hpr:.4%}, simple 365-day yield {simple365:.4%}")
check(abs(p91 - 989.8889) < 1e-4, "91-day price")
check(simple365 > 0.04, "yield from price is above the discount rate")

print("=== B. Sharpe with and without Rf (declare it) ===")
mu, sd = 0.0005, 0.01
rf_d = 0.04 / 252
s0 = mu / sd * 252 ** 0.5
s4 = (mu - rf_d) / sd * 252 ** 0.5
print(f"daily mean {mu}, daily std {sd}: Sharpe Rf=0: {s0:.4f}; Sharpe Rf=4%/252: {s4:.4f}")
check(round(s0, 4) == 0.7937 and round(s4, 4) == 0.5417, "Sharpe values")
check(s4 < s0, "a positive Rf lowers Sharpe")

print("=== C. point in time: a ~15:30 ET quote on day t applies from day t+1 ===")
rates = {date(2026, 11, 5): 0.0400, date(2026, 11, 6): 0.0410}   # synthetic quotes


def rf_for(day):
    prior = [k for k in rates if k < day]
    return rates[max(prior)] if prior else None


print(f"rf for the 2026-11-06 return uses the 2026-11-05 quote: {rf_for(date(2026, 11, 6)):.4f}")
print(f"rf for the 2026-11-05 return (no earlier quote): {rf_for(date(2026, 11, 5))}")
check(rf_for(date(2026, 11, 6)) == 0.0400, "use the prior day's quote")
check(rf_for(date(2026, 11, 5)) is None, "no future quote")
print(f"assertions passed: {checks}/{checks}")
print("ASSERT_tbill_rf_ok")
print("disclaimer: synthetic rates; T-bill is a teaching proxy; no Treasury data downloaded; learning only")
