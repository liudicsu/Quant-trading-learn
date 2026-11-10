"""ETF NAV vs market price, and the daily reset of leveraged/inverse ETFs (checked 2026-11-10).

Sources: 17 CFR 270.6c-11 (premium/discount definition; daily website disclosure;
">2% for more than seven consecutive trading days" statement); SEC investor bulletins
"Exchange-Traded Funds (ETFs)" (2023-02-23) and "Leveraged and Inverse ETFs" (2023-08-29,
the 1000 -> 900 -> 990 / 800 -> 960 example). All prices are synthetic.
Not modelled: fees, financing, tracking error, intraday NAV. Learning only, not investment advice.
"""
checks = 0


def check(cond, label):
    global checks
    assert cond, label
    checks += 1


def prem_disc(market_price, nav):
    """6c-11: (market price - NAV) as a percent of NAV."""
    return (market_price - nav) / nav * 100


def flag_2pct_7days(daily_pct):
    """True once |premium/discount| > 2% for MORE than seven consecutive trading days."""
    run = 0
    for x in daily_pct:
        run = run + 1 if abs(x) > 2 else 0
        if run > 7:
            return True
    return False


def median_spread_pct(quotes):
    spreads = sorted((ask - bid) / ((ask + bid) / 2) * 100 for bid, ask in quotes)
    return spreads[len(spreads) // 2]


def path(daily_index_returns, multiple, start=1000.0):
    """A fund that hits multiple x the index's DAILY return exactly, compounded daily."""
    v, out = start, [start]
    for r in daily_index_returns:
        v *= 1 + multiple * r
        out.append(v)
    return out


print("=== A. premium / discount (Rule 6c-11 definition) ===")
p, d = prem_disc(50.10, 50.00), prem_disc(49.75, 50.00)
print(f"market 50.10 vs NAV 50.00 -> {p:+.2f}% (premium)")
print(f"market 49.75 vs NAV 50.00 -> {d:+.2f}% (discount)")
check(round(p, 2) == 0.20 and round(d, 2) == -0.50, "premium/discount in percent of NAV")
print(f"|prem/disc| 2.1% for 8 days -> statement needed: {flag_2pct_7days([2.1] * 8)}")
print(f"|prem/disc| 2.1% for 7 days -> statement needed: {flag_2pct_7days([2.1] * 7)}")
check(flag_2pct_7days([2.1] * 8) and not flag_2pct_7days([2.1] * 7), "more than seven consecutive days")
q = [(49.98, 50.02), (49.99, 50.01), (49.97, 50.03), (49.99, 50.01), (49.98, 50.02)]
m = median_spread_pct(q)
print(f"median bid-ask spread of 5 synthetic quotes: {m:.2f}%")
check(round(m, 2) == 0.08, "median spread 0.08%")

print("=== B. SEC two-day example: daily target hit, two-day result is not 2x ===")
idx, x2, inv2 = path([-0.10, 0.10], 1), path([-0.10, 0.10], 2), path([-0.10, 0.10], -2)
print(f"index: {' -> '.join(f'{v:.0f}' for v in idx)}  ({idx[-1] / idx[0] - 1:+.0%})")
print(f"2x   : {' -> '.join(f'{v:.0f}' for v in x2)}  ({x2[-1] / x2[0] - 1:+.0%})")
print(f"-2x  : {' -> '.join(f'{v:.0f}' for v in inv2)}  ({inv2[-1] / inv2[0] - 1:+.0%})")
check(round(idx[-1], 6) == 990 and round(x2[-1], 6) == 960, "SEC bulletin numbers 990 / 960")
check([round(v, 6) for v in inv2] == [1000, 1200, 960], "-2x path 1000 -> 1200 -> 960")

print("=== C. choppy market: +5% / -5% repeated for 20 days ===")
chop = [0.05, -0.05] * 10
ends = {k: path(chop, k)[-1] for k in (1, 2, 3, -2)}
for k, v in ends.items():
    print(f"{k:+d}x final {v:.4f}")
check(ends[2] < ends[1] and ends[3] < ends[2], "decay grows with the multiple")
check(abs(ends[1] - 975.2794) < 1e-4 and abs(ends[2] - 904.3821) < 1e-4, "choppy finals")
print(f"assertions passed: {checks}/{checks}")
print("ASSERT_etf_nav_letf_ok")
print("disclaimer: synthetic prices; no fees, financing or tracking error; learning only")
