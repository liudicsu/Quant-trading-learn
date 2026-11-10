"""Margin account basics: Reg T initial margin, FINRA 4210 maintenance, margin-call trigger price (checked 2026-11-10).

Sources: 12 CFR 220.12(a) (50% initial margin on margin equity securities);
FINRA Rule 4210(b)(4) ($2,000 minimum equity, or full cost if less) and 4210(c)(1)
(25% maintenance on long margin securities); SEC investor bulletin "Understanding Margin
Accounts" (2021-06-10) for the $16,000 / $8,000 / $12,000 example and typical 30-40% house levels.
FINRA Notice 26-10 (2026): the intraday margin rule "does not change the regular maintenance
margin requirements". Long-only toy, no interest, no intraday margin; learning only.
"""
checks = 0


def check(cond, label):
    global checks
    assert cond, label
    checks += 1


def max_loan(purchase, initial=0.50):
    """Reg T: deposit at least 50%, so borrow at most the rest."""
    return purchase * (1 - initial)


def maint_ok(market_value, loan, m):
    equity = market_value - loan
    required = m * market_value
    return equity, required, equity >= required


def call_price(loan, shares, m):
    """Long only, no new deposits: equity < m x value once price < loan / (shares x (1 - m))."""
    return loan / (shares * (1 - m))


print("=== A. Reg T initial margin ===")
print(f"buy $16,000 of stock -> may borrow at most ${max_loan(16000):,.0f}")
check(max_loan(16000) == 8000, "Reg T 50%")

print("=== B. SEC bulletin example: value falls to $12,000, loan $8,000 ===")
for m in (0.25, 0.40):
    eq, req, ok = maint_ok(12000, 8000, m)
    print(f"maintenance {m:.0%}: equity ${eq:,.0f} vs required ${req:,.0f} -> {'ok' if ok else f'margin call ${req - eq:,.0f}'}")
check(maint_ok(12000, 8000, 0.25) == (4000, 3000, True), "25%: fine")
eq, req, ok = maint_ok(12000, 8000, 0.40)
check(not ok and req - eq == 800, "40%: $800 call")

print("=== C. trigger price (160 shares bought at $100, loan $8,000) ===")
for m in (0.25, 0.40):
    print(f"maintenance {m:.0%}: call when price < {call_price(8000, 160, m):.4f}")
check(abs(call_price(8000, 160, 0.25) - 66.6667) < 1e-4, "25% trigger 66.6667")
check(abs(call_price(8000, 160, 0.40) - 83.3333) < 1e-4, "40% trigger 83.3333")
price = 12000 / 160
print(f"price {price:.2f}: below 40% trigger? {price < call_price(8000, 160, 0.40)}; below 25% trigger? {price < call_price(8000, 160, 0.25)}")
check(price < call_price(8000, 160, 0.40) and price >= call_price(8000, 160, 0.25), "75 triggers 40% only")
print(f"assertions passed: {checks}/{checks}")
print("ASSERT_margin_call_ok")
print("disclaimer: long-only toy; no interest, no intraday margin, broker may sell without notice; learning only")
