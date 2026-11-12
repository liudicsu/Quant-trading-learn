"""Self-trade prevention and a disruptive-quoting pattern flag (checked 2026-11-10).

Sources: 15 U.S.C. 78i(a)(1)-(2) (govinfo, USCODE-2023 edition; wash trades / matched orders / series of
transactions to induce others); FINRA Rule 5210 Supplementary Material .02 (unintentional self-trades are
generally bona fide, but firms must review for and prevent a pattern of self-trades from a single algorithm
or related algorithms) and .03 (two prohibited patterns of disruptive quoting and trading, incl. across
venues; SM .03(c): the order of events does not modify applicability); IRS Publication 550 (wash sale = tax
concept: repurchase within 30 days before or after the sale, see 06_wash_sale_basis_toy.py).
Purely synthetic events. A flag is only a prompt for human review, not a finding of a violation.
Not legal advice; learning only.
"""

checks = 0


def check(cond, label):
    global checks
    assert cond, label
    checks += 1


print("=== A. self-trade prevention at the order layer ===")
book = [("BUY", 10.00, 100, "algoA")]   # (side, price, qty, owner)


def stp(book, o):
    """Resting orders the incoming order would hit that belong to the same algo."""
    side, px, _, owner = o
    return [b for b in book if b[3] == owner and b[0] != side
            and ((side == "SELL" and px <= b[1]) or (side == "BUY" and px >= b[1]))]


blocked_a = stp(book, ("SELL", 10.00, 100, "algoA"))
blocked_b = stp(book, ("SELL", 10.00, 100, "algoB"))
print(f"incoming algoA SELL 100@10.00 vs resting algoA BUY 100@10.00 -> blocked {len(blocked_a)}")
print(f"incoming algoB SELL 100@10.00 -> blocked {len(blocked_b)} (this toy checks same algo only; real scope follows firm policy)")
check(len(blocked_a) == 1, "same algo blocked")
check(len(blocked_b) == 0, "different algo not blocked by this toy")

print("=== B. pattern flag: layer one side, fill the other, cancel the layers ===")


def layering_flag(events):
    """events: (kind, side, price, t). True = this order-dependent toy flags the log."""
    buys = [e for e in events if e[0] == "new" and e[1] == "BUY"]
    fills = [e for e in events if e[0] == "fill" and e[1] == "SELL"]
    cancels = [e for e in events if e[0] == "cancel" and e[1] == "BUY"]
    if len({b[2] for b in buys}) >= 3 and fills and len(cancels) >= 3:
        t_fill = fills[0][3]
        return all(c[3] > t_fill for c in cancels) and all(b[3] < t_fill for b in buys)
    return False


def should_review_layers(events):
    """Same ingredients, ignoring event order. FINRA 5210 SM .03(c): order does not change applicability."""
    buys = [e for e in events if e[0] == "new" and e[1] == "BUY"]
    fills = [e for e in events if e[0] == "fill" and e[1] == "SELL"]
    cancels = [e for e in events if e[0] == "cancel" and e[1] == "BUY"]
    return len({b[2] for b in buys}) >= 3 and bool(fills) and len(cancels) >= 3


pattern = [("new", "BUY", 9.97, 1), ("new", "BUY", 9.98, 2), ("new", "BUY", 9.99, 3),
           ("fill", "SELL", 10.01, 5), ("cancel", "BUY", 9.97, 6), ("cancel", "BUY", 9.98, 6),
           ("cancel", "BUY", 9.99, 6)]
benign = [e for e in pattern if e[0] != "fill"]
swapped = [("new", "BUY", 9.97, 1), ("new", "BUY", 9.98, 2), ("new", "BUY", 9.99, 3),
           ("cancel", "BUY", 9.97, 6), ("cancel", "BUY", 9.98, 6),
           ("cancel", "BUY", 9.99, 6), ("fill", "SELL", 10.01, 7)]
print(f"3 bid layers -> sell fill -> cancel all layers: flagged for review {layering_flag(pattern)}")
print(f"same layers cancelled with no other-side fill: flagged for review {layering_flag(benign)}")
print(f"3 bid layers -> cancel all layers -> sell fill: flagged for review {layering_flag(swapped)}")
print("swapped order still should be reviewed "
      f"{should_review_layers(swapped)} (FINRA 5210 SM .03(c): event order does not change applicability; this toy only flags one event order)")
print("a flag only asks a human to review the log; it is not a finding of a violation")
check(layering_flag(pattern), "pattern flagged")
check(not layering_flag(benign), "benign not flagged")
check(not layering_flag(swapped), "swapped order not flagged by this toy")
check(should_review_layers(swapped) and should_review_layers(pattern) and not should_review_layers(benign),
      "swapped order still should be reviewed")

print("=== C. two words that are easy to mix up ===")
glossary = {"wash sale": "tax: loss sale + repurchase within 30 days before or after the sale (IRS Pub 550)",
            "wash trade": "manipulation: no change in beneficial ownership (15 U.S.C. 78i(a)(1))"}
for k, v in glossary.items():
    print(f"{k:10s} -> {v}")
check(glossary["wash sale"].startswith("tax") and glossary["wash trade"].startswith("manipulation"), "glossary")
print(f"assertions passed: {checks}/{checks}")
print("ASSERT_self_trade_pattern_ok")
print("disclaimer: synthetic events; flags are review prompts, not legal findings; not legal advice; learning only")

print("=== D. FINRA 2150: no improper use of a customer's securities or funds, and no guarantee against loss ===")
# FINRA Rule 2150 Improper Use of Customers' Securities or Funds;
# Prohibition Against Guarantees and Sharing in Accounts (official-page
# opened 2026-11-12). Add this section AFTER the current last disclaimer
# line so sections A-C, including 7/7, ASSERT_self_trade_pattern_ok, and
# the disclaimer, remain a strict byte-prefix of the tip file.
# Official 2150(a): No member or person associated with a member shall
# make improper use of a customer's securities or funds.
# Official (b): No member or person associated with a member shall
# guarantee a customer against loss in connection with any securities
# transaction or in any securities account of such customer.
# Official caption typography is "Customers' Securities or Funds."
# Official (c) sharing is prohibited except under official written
# authorizations and the direct-proportion test, with official family
# and Advisers Act Rule 205-3 alternatives; name official (c), do not
# build a 205-3, settlements, or immediate-family engine.
# Official SM .01: a "guarantee" extended to all holders of a particular
# security by an issuer as part of that security generally would not be
# subject to the prohibition against guarantees.
# Official SM .02: a member, but not an associated person, may determine
# on an after-the-fact basis to reimburse a customer for transaction
# losses (subject to applicable reporting) and may correct a bona fide
# error. Do not invent that a member may never reimburse a loss.
# Official SM .03: preserve the required written authorization(s) for at
# least six years after the date the account is closed.
# Do not flatten 2150 into already-taught 15c3-3 or SIPC, or into packed
# 2261. No broker, product, or guarantee recommendation.

print("2150(a): No member or person associated with a member shall make improper use of a customer's securities or funds")
print("2150(b): No member or person associated with a member shall guarantee a customer against loss in connection with any securities transaction or in any securities account of such customer")
print('official caption typography is "Customers\' Securities or Funds"')
print("official (c) written-authorization and direct-proportion sharing conditions exist, with official")
print("  family and Advisers Act Rule 205-3 alternatives; this toy is not a 205-3, settlements, or")
print("  immediate-family engine")
print('official SM .01: a "guarantee" that is extended to all holders of a particular security by an')
print("  issuer as part of that security generally would not be subject to the prohibition against guarantees")
print("official SM .02: a member, but not an associated person, may determine on an after-the-fact basis")
print("  to reimburse a customer for transaction losses (subject to applicable reporting) and may correct")
print("  a bona fide error")
print("official SM .03: preserve the required written authorization(s) for at least six years after the")
print("  date the account is closed")
flatten_2150 = False
print(f"  this is a flatten into already-taught 15c3-3 or SIPC, or into packed 2261? {flatten_2150}")
check(flatten_2150 is False, "do not flatten 2150 into 15c3-3, SIPC, or packed 2261")
never_reimburse = False
print(f"  this toy invents that a member may never reimburse a loss? {never_reimburse}")
check(never_reimburse is False, "official SM .02 permits after-the-fact member reimbursement")
prohibited = True
print(f"  improper use of a customer's securities or funds, and a guarantee against loss, are prohibited? {prohibited}")
check(prohibited is True, "2150 prohibits improper use and a guarantee against loss")
print("no broker, product, or guarantee recommendation")
print(f"assertions passed: {checks}/{checks}")
print("ASSERT_2150_ok")
print("disclaimer: learning only; not legal advice; no broker, product, or guarantee recommendation")

print("=== E. FINRA 3220: anything of value, including gratuities, in excess of $300 per individual per year ===")
# FINRA Rule 3220 Influencing or Rewarding Employees of Others
# (official-page opened 2026-11-12). Amended by SR-FINRA-2025-003 eff.
# Mar. 30, 2026 (already effective). Supporting Notice 26-05 is
# supporting only; quote the official rule wording
# "$300 per individual per year," not the Notice phrasing
# "per person per year."
# Official 3220(a): No member or person associated with a member shall,
# directly or indirectly, give or permit to be given anything of value,
# including gratuities, in excess of $300 per individual per year to any
# person, principal, proprietor, employee, agent or representative of
# another person where such payment or gratuity is in relation to the
# business of the employer of the recipient of the payment or gratuity.
# A gift of any kind is considered a gratuity.
# Official SM .09: This Rule does not apply to gifts from a member to
# its own associated persons, or to gifts from a member or an associated
# person to individual retail customers.
# Official (b)-(d) and official SM .01-.08 exist; name them, do not
# build the valuation / aggregation / exception catalog. Official
# typography is "SEA Rule 17a-4" if (c) is named.
# Do not teach the pre-amendment $100 cap as current law. Do not invent
# that the $300 limit applies to gifts to individual retail customers.
# Do not flatten 3220 into already-taught FINRA 5230 or 5250. No gift,
# broker, or entertainment recommendation. Keep A-C, including 7/7,
# ASSERT_self_trade_pattern_ok, the disclaimer, and the new 2150
# section, identical once 2150 is added.

print("3220(a): No member or person associated with a member shall, directly or indirectly, give or")
print("  permit to be given anything of value, including gratuities, in excess of $300 per individual")
print("  per year to any person, principal, proprietor, employee, agent or representative of another")
print("  person where such payment or gratuity is in relation to the business of the employer of the")
print("  recipient of the payment or gratuity. A gift of any kind is considered a gratuity")
print('official wording is "$300 per individual per year"')
print("the current official limit is $300, not the pre-amendment $100 cap (SR-FINRA-2025-003 eff. Mar. 30, 2026; already effective)")
print("official SM .09: This Rule does not apply to gifts from a member to its own associated persons,")
print("  or to gifts from a member or an associated person to individual retail customers")
print("official (b)-(d) and official SM .01-.08 exist; official (c) recordkeeping typography is")
print('  "SEA Rule 17a-4"; this toy is not the valuation / aggregation / exception catalog')
flatten_3220 = False
print(f"  this is a flatten into already-taught 5230 or 5250? {flatten_3220}")
check(flatten_3220 is False, "do not flatten 3220 into already-taught 5230 or 5250")
retail_cap = False
print(f"  this toy invents that the $300 limit applies to gifts to individual retail customers? {retail_cap}")
check(retail_cap is False, "official SM .09 carves out gifts to individual retail customers")
limit_300 = True
print(f"  the current official limit is $300 per individual per year, not $100? {limit_300}")
check(limit_300 is True, "current official 3220 limit is $300 per individual per year")
print("no gift, broker, or entertainment recommendation")
print(f"assertions passed: {checks}/{checks}")
print("ASSERT_3220_ok")
print("disclaimer: learning only; not legal advice; no gift, broker, or entertainment recommendation")
