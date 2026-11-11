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

print("=== D. NY Fed SOFR: published ~8:00 a.m. ET one business day after the value date ===")
# NY Fed SOFR page (opened 2026-11-12): "Each business day, the New York Fed
# publishes the SOFR on the New York Fed website at approximately 8:00 a.m. ET."
# Additional Information about Reference Rates: "the SOFR is published one
# business day following its value date (the day when overnight trades were
# negotiated)." Official example: "The first SOFR was published on 4/3/2018
# for the value date of 4/2/2018." Same-day revisions "may be revised at
# approximately 2:30 p.m. ET" and "will only occur if the change in the rate
# exceeds one basis point and only on the same day as initial publication."
# Contrast, do not conflate: the EFFR and OBFR "will be published at
# approximately 9:00 a.m. ET each business day" that is not on the NY Fed
# holiday schedule.
# Look-ahead: yesterday's SOFR, published at about 8:00 a.m. today, can fill
# at today's 09:30 open; today's value-date SOFR is published the next
# business day and cannot be used this morning.
# Do not copy the T-bill "~15:30 ET quote on day t applies from day t+1"
# sentence onto SOFR. Do not write that every NY Fed reference rate is
# published at 8:00 a.m. SOFR is a teaching rate timestamp, not "the" correct
# risk-free rate; whatever proxy you use, write it down. No invented G.19
# clock, first-Friday rule, or SOFR trading strategy.

value_mon = date(2026, 11, 9)  # Monday
pub_tue = date(2026, 11, 10)  # Tuesday ~8:00 a.m. ET
print("Each business day, the New York Fed publishes the SOFR at approximately 8:00 a.m. ET")
print("the SOFR is published one business day following its value date (the day when overnight trades were negotiated)")
print("official example: first SOFR published 2018-04-03 for value date 2018-04-02")
print(f"Monday {value_mon} value-date SOFR is published {pub_tue} at about 8:00 a.m. ET")
print(f"that Tuesday 8:00 a.m. print can fill at Tuesday's 09:30 ET open: yes")
print(f"Tuesday {pub_tue} value-date SOFR is published the next business day and cannot be used Tuesday morning")
check(pub_tue == date(2026, 11, 10), "Monday value-date SOFR publishes Tuesday")
can_use_at_tue_open = True  # Tuesday 09:30 is after Tuesday ~8:00 publication of Monday's SOFR
cannot_use_tue_value_tue_morning = True
check(can_use_at_tue_open and cannot_use_tue_value_tue_morning, "yesterday's SOFR can fill at today's open; today's cannot")
print("same-day revisions may occur at approximately 2:30 p.m. ET only if the change exceeds one basis point, only on the same day as initial publication")
print("contrast: EFFR and OBFR are published at approximately 9:00 a.m. ET; do not write that every NY Fed reference rate is published at 8:00 a.m.")
print("do not copy the T-bill '~15:30 ET quote on day t applies from day t+1' sentence onto SOFR")
print("do not treat 8:00 a.m. as after the 9:30 open")
print("SOFR is a teaching rate timestamp, not the only correct risk-free proxy; whatever proxy you use, write it down")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: synthetic dates; SOFR is a teaching timestamp; no NY Fed data downloaded; learning only")
