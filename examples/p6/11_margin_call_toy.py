"""Margin account basics: Reg T initial margin, FINRA 4210 maintenance, margin-call trigger price
(checked 2026-11-10), plus short-sale margin (checked 2026-11-12).

Sources: 12 CFR 220.12(a) (50% initial margin on margin equity securities);
FINRA Rule 4210(b)(4) ($2,000 minimum equity, or full cost if less) and 4210(c)(1)
(25% maintenance on long margin securities); SEC investor bulletin "Understanding Margin
Accounts" (2021-06-10) for the $16,000 / $8,000 / $12,000 example and typical 30-40% house levels.
FINRA Notice 26-10 (2026): the intraday margin rule "does not change the regular maintenance
margin requirements".
Short sales (enrich17): 12 CFR 220.12(c) required margin is 150 percent of the current
market value, or 100 percent if a security exchangeable or convertible within 90 calendar
days without restriction other than the payment of money into the security sold short is
held in the account (with the stated American-style listed-call conditions). Do not invent
"the customer must deposit 150% in cash on top of the short proceeds." FINRA 4210(c)(2)-(3)
maintenance: selling below $5.00, $2.50 per share or 100 percent of CMV, whichever greater;
selling at $5.00 or above, $5.00 per share or 30 percent of CMV, whichever greater.
Long 50/25 stays as already taught. House rates may be stricter. Learning only.
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

# ---------------- enrich17 (2026-11-12): short-sale margin ----------------
print("=== E. short-sale margin (Reg T 150% / FINRA 4210(c)(2)-(3)) ===")
sm_checks = 0


def sm_check(cond, label):
    global sm_checks
    assert cond, label
    sm_checks += 1


def short_initial(cmv, convertible_held=False):
    """Reg T 220.12(c): 150% of CMV, or 100% if a qualifying convertible is held."""
    return (1.00 if convertible_held else 1.50) * cmv


def short_maint(price, shares=100):
    """FINRA 4210(c)(2)-(3). price is the current selling price per share."""
    cmv = price * shares
    if price < 5:
        return max(2.50 * shares, 1.00 * cmv)
    return max(5.00 * shares, 0.30 * cmv)


# 100 shares short at $50: CMV $5,000; initial 150% = $7,500 (not "$7,500 cash on top of proceeds")
cmv50 = 50 * 100
init50 = short_initial(cmv50)
init50_conv = short_initial(cmv50, convertible_held=True)
maint50 = short_maint(50, 100)
print(f"  short 100 sh @ $50: CMV ${cmv50:,.0f}")
print(f"  Reg T initial 150% of CMV = ${init50:,.0f} (100% if a qualifying convertible is held = ${init50_conv:,.0f})")
print("  do not invent 'deposit 150% cash on top of the short proceeds'")
print(f"  FINRA maintenance at $50 (>= $5): max($5 x 100 = $500, 30% x $5,000 = $1,500) = ${maint50:,.0f}")
sm_check(init50 == 7500 and init50_conv == 5000, "150% / convertible 100%")
sm_check(maint50 == 1500, "$50: 30% wins over $5")

# 100 shares short at $4: CMV $400; maintenance max($2.50 x 100 = $250, 100% x $400 = $400) = $400
cmv4 = 4 * 100
maint4 = short_maint(4, 100)
print(f"  short 100 sh @ $4: CMV ${cmv4:,.0f}")
print(f"  FINRA maintenance below $5: max($2.50 x 100 = $250, 100% x $400 = $400) = ${maint4:,.0f}")
sm_check(maint4 == 400, "$4: 100% wins over $2.50")

# Contrast: at $2 the $2.50 floor wins; at $10 the $5 floor wins (literacy rows)
maint2 = short_maint(2, 100)
maint10 = short_maint(10, 100)
print(f"  contrast, 100 sh @ $2: max($250, 100% x $200 = $200) = ${maint2:,.0f}")
print(f"  contrast, 100 sh @ $10: max($500, 30% x $1,000 = $300) = ${maint10:,.0f}")
sm_check(maint2 == 250 and maint10 == 500, "floors can bind")
print("  long initial/maintenance remain 50%/25% as already taught; house rates may be stricter")
print(f"assertions passed: {sm_checks}/{sm_checks}")
print("ASSERT_short_margin_ok")
print("disclaimer: strategy-based short-margin toy; house rates may be stricter; learning only")
