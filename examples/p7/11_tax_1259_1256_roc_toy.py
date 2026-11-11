"""Pub 550 return-of-capital Example 1, a 1259 / 1256 classification table,
and payments in lieu / preferred-stock QDI (checked 2026-11-12).

Sources:
- IRS Publication 550 (2025), "Nondividend Distributions": a nondividend
  distribution is not paid out of earnings and profits; it appears in Form
  1099-DIV box 3; it reduces the basis of the stock and is not taxed until basis
  is fully recovered (also called a return of capital). After basis is zero,
  further nondividend distributions are capital gain; long-term vs short-term
  follows the holding period of the stock. Example 1: stock bought in 2012 for
  $100; 2015 nondividend distribution of $80 reduces basis to $20; 2025
  distribution of $30: the first $20 reduces basis to zero, the other $10 is
  long-term capital gain.
- 26 U.S.C. §1259 / Pub 550 "Constructive Sales of Appreciated Financial
  Positions": entering into a short sale of the same or substantially identical
  property can be a constructive sale of an appreciated financial position;
  you recognize gain as if the position were sold at FMV on that date; the
  holding period starts over; later actual close-out is adjusted for the gain
  already taken into account. Not every hedge is a constructive sale: positions
  already marked to market, including Section 1256 contracts, are excluded, and
  the statute has a closed-transaction exception. This is not a wash sale and
  not Section 16(b).
- Pub 550 / IRC §1256: a Section 1256 contract includes a regulated futures
  contract, a foreign currency contract, a nonequity option, a dealer equity
  option, or a dealer securities futures contract. A nonequity option is a
  listed option that is not an equity option and includes broad-based stock
  index options (Pub 550 example: S&P 500). An equity option is an option to
  buy or sell stock, or one valued by reference to any stock or a narrow-based
  index, so ordinary single-stock equity options are not 1256 contracts. Under
  the 60/40 rule, 60% of the capital gain or loss is long-term and 40% is
  short-term, regardless of how long you actually held the property.

- investor.gov, "An Introduction to Short Sales" (updated 2026-09-09):
  "If the stock you borrow pays a dividend, you must pay the dividend to the
  person or firm making the loan."
- Pub 550 (2025), "Reporting Substitute Payments": if a broker transferred
  your securities for use in a short sale or similar transaction and received
  certain substitute dividend payments on your behalf, it must report them on
  Form 1099-MISC (or a similar statement). "Do not treat these substitute
  payments as dividends or interest." Report them as "Other income." A
  substitute payment in lieu of a dividend is one whose ex-dividend date is
  after the transfer of stock for use in a short sale and before the closing
  of the short sale. Under "Dividends that are not qualified dividends," Pub
  550 lists, among others, "Dividends on any share of stock to the extent you
  are obligated (whether under a short sale or otherwise) to make related
  payments for positions in substantially similar or related property," and
  "Payments in lieu of dividends, but only if you know or have reason to know
  the payments are not qualified dividends." Those items "are not qualified
  dividends even if they are shown on Form 1099-DIV, box 1b."
- Pub 550 "Exception for preferred stock": you must have held the stock more
  than 90 days during the 181-day period that begins 90 days before the
  ex-dividend date if the dividends are due to periods totaling more than 366
  days. If the preferred dividends are due to periods totaling less than 367
  days, the ordinary more-than-60-days-in-121-day-window test applies. Do not
  apply 90/181 to common stock, and do not call every preferred dividend a
  90-day test. "Qualified REIT dividends" (IRC §199A / 1099-DIV box 5) are a
  different concept; a REIT can still designate a box 1b qualified-dividend
  portion.

General information, not tax or investment advice. Backtests stay pre-tax
unless labelled otherwise. Applies only if US tax rules apply to you.
"""
from decimal import Decimal

checks = 0


def check(cond, label):
    global checks
    assert cond, label
    checks += 1


def apply_nondividend(basis, distribution):
    """Reduce basis; any excess after basis is zero is capital gain."""
    basis = Decimal(str(basis))
    distribution = Decimal(str(distribution))
    if distribution <= basis:
        return basis - distribution, Decimal("0")
    return Decimal("0"), distribution - basis


print("=== A. IRS Pub 550 Example 1: return of capital / 1099-DIV box 3 ===")
basis = Decimal("100")
print(f"  bought in 2012 for ${basis}")
basis, gain = apply_nondividend(basis, 80)
print(f"  2015 nondividend distribution $80 -> basis ${basis}, gain ${gain}")
check(basis == Decimal("20") and gain == 0, "2015")
basis, gain = apply_nondividend(basis, 30)
print(f"  2025 nondividend distribution $30 -> basis ${basis}, long-term capital gain ${gain}")
check(basis == 0 and gain == Decimal("10"), "2025")
print("  a nondividend distribution is not a dividend; it is not taxed until basis is fully recovered")
print("  after basis is zero, further nondividend distributions are capital gain (holding period of the stock)")

print("=== B. Classification table (literacy only; not a product recommendation) ===")
rows = (
    ("ordinary single-stock equity option", "not a section 1256 contract; 60/40 does not apply"),
    ("narrow-based index option (an equity option)", "not a section 1256 contract; 60/40 does not apply"),
    ("listed broad-based stock index option (Pub 550 example: S&P 500)", "nonequity option; section 1256 60/40 may apply if it meets the listed / qualified-board tests"),
    ("short sale of the same stock against an appreciated long stock position", "may be a constructive sale under IRC 1259; not a wash sale and not section 16(b); not every hedge is 1259"),
    ("section 1256 contract already marked to market", "excluded from 'appreciated financial position' under 1259(b); do not layer a homemade 1259 rule on top"),
)
for instrument, treatment in rows:
    print(f"  {instrument}:")
    print(f"    -> {treatment}")
check(len(rows) == 5, "five rows")
print("do not apply 60/40 to ordinary equity options; do not call every index product 1256")
print("do not teach that any short against a long is always 1259")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: general information, not tax advice; backtests stay pre-tax unless labelled otherwise")

print("=== C. Payments in lieu are not QDI; preferred QDI is 90/181 only when periods > 366 days ===")
rows = (
    ("cash the short seller owes the lender when borrowed stock pays a dividend", "a cash obligation (investor.gov short-sales bulletin); a backtest that 'pays no dividends' omits this cost"),
    ("substitute payment in lieu of a dividend (ex-date after transfer for the short and before close-out)", "reported on Form 1099-MISC; do not treat as dividends or interest; not QDI even if shown in Form 1099-DIV box 1b"),
    ("common-stock qualified dividend", "more than 60 days in the 121-day window beginning 60 days before the ex-date"),
    ("preferred dividend due to periods totaling more than 366 days", "more than 90 days in the 181-day window beginning 90 days before the ex-date"),
    ("preferred dividend due to periods totaling less than 367 days", "ordinary 60/121 test; do not call every preferred dividend a 90-day test"),
    ("REIT ordinary dividend / 1099-DIV box 5 qualified REIT dividend (IRC 199A)", "a different concept from box 1b QDI; do not claim that REIT dividends are never QDI; a REIT can still designate a box 1b portion"),
)
for instrument, treatment in rows:
    print(f"  {instrument}:")
    print(f"    -> {treatment}")
check(len(rows) == 6, "six tax-character rows")
print("do not apply 90/181 to common stock")
print("do not treat payments in lieu as qualified dividends")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: general information, not tax advice; backtests stay pre-tax unless labelled otherwise")

