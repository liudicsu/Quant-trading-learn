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


print("=== D. Pub 550 capital-loss deduction cap and carryover ===")
# IRS Publication 550 (2025), "Capital Losses": "If your capital losses are
# more than your capital gains, you can claim a capital loss deduction."
# "Limit on deduction. Your allowable capital loss deduction, figured on
# Schedule D (Form 1040), is the lesser of: • $3,000 ($1,500 if you are
# married and file a separate return), or • Your total net loss as shown on
# line 16 of Schedule D (Form 1040). You can use your total net loss to
# reduce your income dollar for dollar, up to the $3,000 limit."
# "Capital loss carryover. ... you can carry over the unused part to the next
# year and treat it as if you had incurred it in that next year. ... When you
# carry over a loss, it remains long-term or short-term."
# Official example: "Bob and Shelly sold securities in 2025. The sales
# resulted in a capital loss of $7,000. They had no other capital
# transactions. Their taxable income was $26,000. On their joint 2025 return,
# they can deduct $3,000. The unused part of the loss, $4,000 ($7,000 −
# $3,000), can be carried over to 2026. If their capital loss had been
# $2,000, their capital loss deduction would have been $2,000. They would
# have no carryover."
# The cap is on the total net loss; there is not a different cap for
# short-term vs long-term. General information, not tax advice. Backtests
# stay pre-tax unless labelled otherwise.


def cap_loss_deduction(net_loss, married_filing_separately=False):
    cap = 1500 if married_filing_separately else 3000
    loss = int(net_loss)
    deduct = min(cap, loss)
    return deduct, loss - deduct


d, c = cap_loss_deduction(7000, False)
print(f"Bob and Shelly, joint return, $7,000 net capital loss: deduct ${d:,}, carry over ${c:,}")
check((d, c) == (3000, 4000), "Pub 550 Bob-and-Shelly example")
d, c = cap_loss_deduction(2000, False)
print(f"same joint return, $2,000 net capital loss: deduct ${d:,}, carry over ${c:,}")
check((d, c) == (2000, 0), "a $2,000 net loss is fully deductible with no carryover")
d, c = cap_loss_deduction(7000, True)
print(f"married filing a separate return, $7,000 net capital loss: deduct ${d:,}, carry over ${c:,}")
check((d, c) == (1500, 5500), "MFS cap is $1,500")
print("when you carry over a loss, it remains long-term or short-term")
print("there is not a different annual cap for short-term vs long-term; the cap is on the total net loss")
print("do not write that a $7,000 net loss all hits the same year's taxable income")

print(f"assertions passed: {checks}/{checks}")
print("disclaimer: general information, not tax advice; backtests stay pre-tax unless labelled otherwise")

print("=== E. Pub 550 short-sale tax character (Ace Corporation) ===")
# IRS Publication 550 (2025), "Short Sales": "You do not realize gain or loss
# until delivery of property to close the short sale." "As a general rule, you
# determine whether you have short-term or long-term capital gain or loss on
# a short sale by the amount of time you actually hold the property that's
# eventually delivered to the lender to close the short sale."
# Official example: "Even though you do not own any stock of Ace Corporation,
# you contract to sell 100 shares of it, which you borrow from your broker.
# After 13 months, when the price of the stock has risen, you buy 100 shares
# of Ace Corporation stock and immediately deliver them to your broker to
# close out the short sale. Your loss is a short-term capital loss because
# your holding period for the delivered property is less than 1 day."
# Report the short sale on Form 8949 in the year it closes. Special rules may
# apply if substantially identical property was held or acquired; this toy
# names that they exist and is not that engine. This is not IRC §1259.
# General information, not tax advice. Backtests stay pre-tax unless labelled
# otherwise.

from datetime import date

delivered_holding_days = 0  # bought and immediately delivered
character = "short-term" if delivered_holding_days < 365 else "long-term"
# The official test is the holding period of the delivered property, which
# here is less than 1 day, so short-term — even though the short was open
# 13 months. Do not treat "open more than a year" as automatically long-term.
print("Ace Corporation: short opened with no shares owned; after 13 months, buy 100 shares and immediately deliver")
print("gain or loss is not realized until delivery of property to close the short sale")
print(f"holding period of the delivered property: less than 1 day -> {character} capital loss")
check(delivered_holding_days < 1 and character == "short-term", "Ace example is short-term; delivered holding period < 1 day")
print("do not write that a short open more than a year is automatically long-term")
print("special rules may apply if substantially identical property was held; this toy is not that engine")
print("report the short sale on Form 8949 in the year it closes")
print("this is not IRC 1259")

print("=== F. Worthless securities treated as sold on the last day of the tax year ===")
# IRC §165(g)(1): if a capital-asset security "becomes worthless during the
# taxable year, the loss ... shall ... be treated as a loss from the sale or
# exchange, on the last day of the taxable year, of a capital asset."
# Pub 550 (2025), "Worthless Securities": "treated as though they were sold
# on the last day of the tax year. This affects whether your capital loss is
# long-term or short-term." Worthless securities also include securities
# abandoned after March 12, 2008, with a facts-and-circumstances test; this
# toy is not an abandonment engine. Affiliated-corporation exceptions exist
# in 165(g)(3); name them, do not teach a corporate-affiliation engine.
# Do not use the bankruptcy, halt, or delisting date as the tax sale date
# under this rule. This is a tax-character clock, not the already-taught
# delisting return. General information, not tax advice.

tax_sale = date(2026, 12, 31)
print(f"calendar-year taxpayer, security becomes worthless during 2026: treated as sold {tax_sale}")
check(tax_sale == date(2026, 12, 31), "last day of tax year 2026")
print("do not use the bankruptcy, halt, or delisting date as the tax sale date under this rule")
print("this is a tax-character clock, not the already-taught delisting return")
print("affiliated-corporation exceptions exist in 165(g)(3); this toy is not that engine")

print(f"assertions passed: {checks}/{checks}")
print("disclaimer: general information, not tax advice; backtests stay pre-tax unless labelled otherwise")


print("=== G. Pub 550 investment interest (including margin-account interest) ===")
# IRS Publication 550 (2025), Chapter 3, "Investment Interest": "If you borrow
# money to buy property you hold for investment, the interest you pay is
# investment interest. You can deduct investment interest subject to the limit
# discussed later. However, you cannot deduct interest you incurred to produce
# tax-exempt income." "Investment interest does not include any qualified home
# mortgage interest or any interest taken into account in computing income or
# loss from a passive activity." "Interest on margin accounts. If you are a
# cash method taxpayer, you can deduct interest on margin accounts to buy
# taxable securities as investment interest in the year you paid it. You are
# considered to have paid interest on these accounts only when you actually
# pay the broker or when payment becomes available to the broker through your
# account." "Generally, your deduction for investment interest expense is
# limited to your net investment income." "You can carry over the amount of
# investment interest you could not deduct because of this limit to the next
# tax year. The interest carried over is treated as investment interest paid
# or accrued in that next year." Official allocation Example 1: borrow $10,000,
# use $8,000 to buy stock and $2,000 for home items → 80% is investment
# interest. Name that allocation rules exist; this toy is not an allocation
# engine. Do not write that all margin interest is always fully deductible in
# the year the broker posts it. Do not confuse this with qualified home-
# mortgage interest, or with the already-taught $3,000 / $1,500 capital-loss
# cap. Do not compute a named person's deduction or recommend leverage.
# General information, not tax advice. Backtests stay pre-tax unless labelled
# otherwise.

print("interest paid on money borrowed to buy property held for investment is investment interest")
print("margin-account interest to buy taxable securities is investment interest")
print("cash-method: deductible in the year you paid it, or when payment becomes available to the broker")
print("generally limited to net investment income; disallowed amount carries over to the next year")
interest, nii = 5000, 3000  # unlabeled teaching arithmetic, not a named person
deduct = min(interest, nii)
carry = interest - deduct
print(f"teaching arithmetic, not a named person: investment interest {interest}, net investment income {nii} -> deduct {deduct}, carry over {carry}")
check((deduct, carry) == (3000, 2000), "limit is net investment income; remainder carries over")
print("official allocation Example 1: borrow $10,000, use $8,000 to buy stock and $2,000 for home items -> 80% is investment interest")
check(8000 / 10000 == 0.8, "official $8,000 / $2,000 allocation example")
print("allocation rules exist when a loan is mixed-use; this toy is not an allocation engine")
print("do not write that all margin interest is always fully deductible in the year the broker posts it")
print("this is not qualified home-mortgage interest, and it is not the already-taught $3,000 / $1,500 capital-loss cap")

print("=== H. Pub 550 stock dividends and stock rights ===")
# IRS Publication 550 (2025), "Distributions of Stock and Stock Rights":
# "Distributions by a corporation of its own stock are commonly known as stock
# dividends. Stock rights (known as 'stock options') are distributions by a
# corporation of rights to acquire the corporation's stock. Generally, stock
# dividends and stock rights are not taxable to you, and you do not report
# them on your return." Official exceptions exist (choice of cash or other
# property; disproportionate distributions; certain preferred-stock
# distributions; constructive distributions); name them, do not build a
# taxability engine. Basis, when the new stock received as a nontaxable
# dividend is identical to the old stock: "divide the adjusted basis of the
# old stock by the number of shares of old and new stock." Official Example 1:
# "You owned one share of common stock that you bought for $45. The
# corporation distributed two new shares of common stock for each share held.
# You then had three shares of common stock. Your basis in each share is $15
# ($45 ÷ 3)." "The holding period for new stock you received as a nontaxable
# stock dividend begins on the same day as the holding period of the old
# stock. This rule also applies to stock acquired in a spin-off." "Any cash
# you receive for fractional shares under such a plan is treated as an amount
# realized on the sale of the fractional shares." Do not leave the old
# per-share basis unchanged. Do not start a new holding period on the
# distribution date. Do not treat fractional-share cash as a cash dividend,
# QDI, or 1099-DIV box 3 return of capital. Pub 550's parenthetical that
# stock rights are "known as 'stock options'" is official language; do not
# confuse those rights with listed call or put options, or with intermarket
# sweep orders (ISO). General information, not tax advice.

old_basis, old_shares, new_per_old = 45, 1, 2
total_shares = old_shares * (1 + new_per_old)
basis_each = old_basis / total_shares
print("Pub 550 Example 1: one share bought for $45; corporation distributed two new shares for each share held")
print(f"three shares after the distribution; basis in each share is ${basis_each:.0f} ($45 / 3)")
check(total_shares == 3 and basis_each == 15, "Example 1: three shares at $15 each")
print("holding period of the nontaxable new stock begins on the same day as the old stock (also applies to stock acquired in a spin-off)")
print("fractional-share cash under a sell-the-fraction plan is an amount realized on the sale of the fractional shares, not a cash dividend, not QDI, and not 1099-DIV box 3 return of capital")
print("generally, stock dividends and stock rights are not taxable, and you do not report them on your return")
print("official exceptions exist (choice of cash or other property; disproportionate distributions; certain preferred-stock distributions; constructive distributions); this toy is not a taxability engine")
print("Pub 550 also writes that stock rights are known as 'stock options'; do not confuse those rights with listed call or put options, or with ISO")
print("do not leave the old per-share basis unchanged after a nontaxable identical-stock dividend")
print("do not start a new holding period on the distribution date for nontaxable new shares")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: general information, not tax advice; backtests stay pre-tax unless labelled otherwise")

print("=== I. Pub 550 gift and inherited basis ===")
# IRS Publication 550 (2025), Chapter 4.
# "Property Received as Inheritance": "If you sell or dispose of inherited
# property that is a capital asset, the gain or loss is considered long-term,
# regardless of how long you held the property." Basis is generally fair
# market value on the date of the decedent's death, or the later alternate
# valuation date if the estate qualifies for and elects it.
# "Property Received as a Gift": you must know the donor's adjusted basis
# just before the gift, FMV at the time of the gift, any gift tax paid, and
# the date of the gift. If FMV was equal to or more than the donor's
# adjusted basis, basis for gain or loss is the donor's adjusted basis plus
# or minus later required adjustments (gift tax paid after 1976 may increase
# basis by a listed fraction — this toy names that the addition exists; it
# is not a gift-tax engine). If FMV was less than the donor's adjusted
# basis, basis for gain is the donor's adjusted basis and basis for loss is
# FMV at the time of the gift, each plus or minus later adjustments.
# Official example: gift basis $10,000, FMV $9,000, later sale $9,500 —
# "You have neither gain nor loss."
# Holding period: if basis is determined by the donor's adjusted basis, the
# holding period "is considered to have started on the same day the donor's
# holding period started"; if basis is determined by FMV, it "starts on the
# day after the date of the gift."
# More detail lives in Pub 551 / Pub 559 (2010 Form 8939, community-property
# / joint-tenancy, the one-year appreciated-property-you-gave-the-decedent
# exception); this toy is not those engines. Spouse transfers under the
# separate "Property Received From Your Spouse" heading are a different
# official rule; do not conflate them with a gift from a parent.
# General information, not tax advice. No tax, estate, or gifting advice.
# Backtests stay pre-tax unless labelled otherwise.

# Inherited capital-asset shares: usual FMV basis, always long-term.
decedent_purchase = 10_000
fmv_at_death = 50_000
heir_basis = fmv_at_death  # usual FMV case; not the decedent's purchase price
print(f"inherited capital-asset shares: decedent's purchase price {decedent_purchase}, FMV at death {fmv_at_death}")
print(f"heir's basis is generally FMV on the date of death {heir_basis} (or the later alternate valuation date if elected)")
print("a later sale of that inherited capital asset is long-term, regardless of how long the heir held the property")
check(heir_basis == 50_000, "usual inherited basis is FMV, not the decedent's purchase price")
inherited_character = "long-term"  # official: regardless of how long the heir held the property
check(inherited_character == "long-term", "inherited capital-asset character is long-term regardless of holding period")

# Official gift dual-basis example.
donor_basis = 10_000
gift_fmv = 9_000
sale = 9_500
gain_basis = donor_basis  # FMV < donor's adjusted basis
loss_basis = gift_fmv
gain_result = sale - gain_basis  # -500, a loss under the gain basis
loss_result = sale - loss_basis  # +500, a gain under the loss basis
print(f"official gift example: donor adjusted basis {donor_basis}, FMV at gift {gift_fmv}, later sale {sale}")
print(f"basis for gain {gain_basis} -> {sale} minus {gain_basis} is a {abs(gain_result)} loss")
print(f"basis for loss {loss_basis} -> {sale} minus {loss_basis} is a {loss_result} gain")
print("You have neither gain nor loss")
check(gain_result == -500 and loss_result == 500, "official 10000/9000/9500 dual-basis arithmetic")
neither = (gain_result < 0) and (loss_result > 0)
check(neither, "neither gain nor loss")

print("if FMV at the gift is equal to or more than the donor's adjusted basis, basis for gain or loss is the donor's adjusted basis")
print("  plus or minus later required adjustments (gift tax paid after 1976 may increase basis by a listed fraction;")
print("  this toy names that the addition exists and is not a gift-tax engine)")
print("holding period: if basis is determined by the donor's adjusted basis, it is considered to have started")
print("  on the same day the donor's holding period started")
print("if basis is determined by the fair market value of the property, the holding period starts on the day after the date of the gift")
print("more detail lives in Pub 551 / Pub 559 (2010 Form 8939, community-property / joint-tenancy,")
print("  the one-year appreciated-property-you-gave-the-decedent exception); this toy is not those engines")
print("spouse transfers under the separate Property Received From Your Spouse heading are a different official rule;")
print("  do not conflate them with a gift from a parent")
print("do not use the decedent's original purchase price as the heir's basis in the usual FMV case,")
print("  and do not start a new short-term clock on inherited capital-asset shares")
print("do not skip the dual-basis rule when FMV at the gift is lower than the donor's adjusted basis")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: general information, not tax advice; backtests stay pre-tax unless labelled otherwise")
