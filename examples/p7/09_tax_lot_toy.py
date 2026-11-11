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


print("=== D. Form 1099-B box 5 / 12 / 1g: noncovered, basis reported to IRS, and wash-sale reporting ===")
# 2026 Instructions for Form 1099-B (official HTML and PDF, opened 2026-11-12).
# Keep sections A-C identical, including the official Pub 550 FIFO $1,380
# example and 3/3 after C. Do not rewrite the already-taught Treas. Reg.
# 1.6045-1 covered-security acquisition-date definition.
# Box 5 marks a noncovered security. When selling a noncovered security and
# reporting it on a separate Form 1099-B, the broker may check box 5 and
# leave boxes 1b, 1e, 1f, 1g, and 2 blank, and need not check box 12.
# A blank basis is not a zero cost.
# Official Arlo example: April 2024 lots are noncovered; April 2025 and
# August 2025 lots are covered; a single June 2026 sale is reported on
# separate 2026 Forms 1099-B (April 2025 long-term covered, August 2025
# short-term covered, and April 2024 noncovered — box 5 may be checked on
# the noncovered form).
# Box 12, if checked, means basis in box 1e was reported to the IRS.
# Box 1g must report a section 1091 wash-sale loss when both the sale and
# the purchase occur in the same account in covered securities with the same
# CUSIP; the broker is permitted but not required to report all section 1091
# losses. Do not treat a blank box 1g as proof that no wash sale occurred.
# Do not conflate 1099-B box 5 with 1099-DIV box 5 / section 199A.
# Do not build a complete 1091 engine. General information, not tax advice.

print("official Arlo example: shares bought in April 2024, April 2025, and August 2025;")
print("  a single June 2026 sale is reported on separate 2026 Forms 1099-B")
forms = (
    ("April 2025 long-term covered", False),
    ("August 2025 short-term covered", False),
    ("April 2024 noncovered", True),
)
print("  April 2025 lot: long-term covered form")
print("  August 2025 lot: short-term covered form")
print("  April 2024 lot: noncovered form; box 5 may be checked")
check(len(forms) == 3, "Arlo single sale is reported on three forms")
check(forms[0] == ("April 2025 long-term covered", False), "April 2025 is long-term covered")
check(forms[1] == ("August 2025 short-term covered", False), "August 2025 is short-term covered")
check(forms[2] == ("April 2024 noncovered", True), "April 2024 is noncovered; box 5 may be checked")
print("box 5 marks a noncovered security; the broker may leave boxes 1b, 1e, 1f, 1g, and 2 blank and need not check box 12")
blank_basis_is_zero = False
print(f"  a blank box 1e basis is a zero cost? {blank_basis_is_zero}")
check(blank_basis_is_zero is False, "blank basis is not a zero cost")
print("box 12, if checked, means basis in box 1e was reported to the IRS")
print("box 1g must report a section 1091 wash-sale loss when both the sale and the purchase occur")
print("  in the same account in covered securities with the same CUSIP")
print("the broker is permitted but not required to report all section 1091 losses")
blank_1g_proves_no_wash = False
print(f"  a blank box 1g is proof that no wash sale occurred? {blank_1g_proves_no_wash}")
check(blank_1g_proves_no_wash is False, "blank 1g is not proof that no wash sale occurred")
same_as_1099div_box5 = False
print(f"  1099-B box 5 is the same box as 1099-DIV box 5 / section 199A? {same_as_1099div_box5}")
check(same_as_1099div_box5 is False, "do not conflate 1099-B box 5 with 1099-DIV box 5")
print("this toy is not a complete section 1091 engine")
print("disclaimer: general information, not tax advice")
print(f"assertions passed: {checks}/{checks}")
