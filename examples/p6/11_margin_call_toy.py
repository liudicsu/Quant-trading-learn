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

# ---------------- enrich9 (2026-11-10): portfolio margin toy ----------------
# Source: FINRA Rule 4210(g) (alternative to "strategy-based" margin; ten equidistant valuation points;
# +/-15% for an equity security or narrow-based index; greater of largest theoretical loss or $.375 x
# multiplier per listed option; only for customers approved for uncovered options; not for IRAs).
# Toy reading: "ten equidistant valuation points" = 10 evenly spaced points from -15% to +15% INCLUDING
# both ends. Real calculations use an SEC-approved theoretical pricing model, not expiry intrinsic value.
print("=== D. portfolio margin (toy) ===")
pm_checks = 0


def pm_check(cond, label):
    global pm_checks
    assert cond, label
    pm_checks += 1


S, n = 100.0, 100
moves = [-0.15 + i * (0.30 / 9) for i in range(10)]


def pnl_stock(m):
    return S * m * n


def pnl_hedged(m, K=95.0, prem=2.0):
    """Long 100 shares + one 95-strike put bought for 2.00, valued at intrinsic only."""
    return S * m * n + (max(K - S * (1 + m), 0.0) - prem) * n


pm_stock = max(0.0, -min(pnl_stock(m) for m in moves))
pm_hedged = max(-min(pnl_hedged(m) for m in moves), 0.375 * 100)
regt_init, maint = 0.5 * S * n, 0.25 * S * n
print(f"valuation points (%): {[round(m * 100, 2) for m in moves]}")
print(f"stock only (100 sh @ 100): Reg T initial {regt_init:.2f}, FINRA maint {maint:.2f}, PM max loss {pm_stock:.2f}")
print(f"stock + 95 put (intrinsic-only toy, premium 2.00): PM max loss {pm_hedged:.2f} (> per-contract minimum {0.375 * 100:.2f})")
pm_check(len(moves) == 10 and abs(moves[0] + 0.15) < 1e-12 and abs(moves[-1] - 0.15) < 1e-12, "10 points incl. ends")
pm_check(abs(pm_stock - 1500.0) < 1e-6, "pm stock")
pm_check(abs(pm_hedged - 700.0) < 1e-6, "pm hedged")
pm_check(pm_stock < maint < regt_init, "unhedged PM can be lower -> more leverage, more risk")
print(f"assertions passed: {pm_checks}/{pm_checks}")
print("ASSERT_portfolio_margin_ok")
print("disclaimer: intrinsic-value toy, not a broker's PM model; eligibility rules apply; learning only")
