"""Which lot did you sell? FIFO default vs adequate identification (checked 2026-11-11).

Source: IRS Publication 550 (2025), "Identifying stock or bonds sold": if you can adequately identify
the shares sold, their basis is the basis of those particular shares; with a broker holding the stock,
adequate identification = you tell the broker which shares at the time of sale AND receive a written
confirmation within a reasonable time. "Identification not possible": the basis is that of the
securities acquired first; except for certain mutual fund shares, you cannot use the average price
per share. The FIFO example (XYZ, 130 shares sold in April 2025, basis $1,380) is reproduced below.
Taxable US account only; not tax advice.
"""
checks = 0


def check(cond, label):
    global checks
    assert cond, label
    checks += 1


# IRS example: 100 @ $10 (2010), 200 @ $11 (Jan 2011), gave 50 away (Jul 2011, from the 2010 lot), 100 @ $9 (Dec 2013)
lots = [["2010", 100, 10.0], ["2011-01", 200, 11.0], ["2013-12", 100, 9.0]]
lots[0][1] -= 50  # the gift came out of the first lot under FIFO (basis 50 x 10 = 500)


def fifo_basis(lots, qty):
    basis, used = 0.0, []
    for name, n, px in lots:
        take = min(n, qty)
        if take:
            basis += take * px
            used.append((name, take))
            qty -= take
    assert qty == 0
    return basis, used


def specific_basis(picks, lots):
    table = {name: px for name, _, px in lots}
    return sum(n * table[name] for name, n in picks)


print("=== A. IRS Pub 550 FIFO example: 130 shares sold in April 2025 ===")
b, used = fifo_basis(lots, 130)
print(f"lots used {used} -> basis {b:,.0f}")
check(b == 1380, "IRS: 50 x 10 + 80 x 11 = 1,380")

print("=== B. same sale with adequate identification (toy choice) ===")
picks = [("2013-12", 100), ("2011-01", 30)]
sb = specific_basis(picks, lots)
print(f"told the broker: {picks}, written confirmation received -> basis {sb:,.0f}")
check(sb == 900 + 330, "100 x 9 + 30 x 11")
print("without the written confirmation this identification does not count -> FIFO basis 1,380")

print("=== C. stock (not certain mutual fund shares): no average price per share ===")
held = sum(n for _, n, _ in lots)
avg = sum(n * px for _, n, px in lots) / held
print(f"toy average of remaining lots {avg:.4f}/share -> 130 x avg = {130 * avg:,.2f} (not allowed for this stock)")
check(round(130 * avg, 2) != 1380, "average differs from FIFO")
print("backtest/ledger rule: store lots (date, shares, cost); record the lot method next to every sale.")
print(f"assertions passed: {checks}/{checks}")
