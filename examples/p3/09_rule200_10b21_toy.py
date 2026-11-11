"""Rule 200 long-marking test and Rule 10b-21 deception-and-fail checklist
(checked 2026-11-12).

Sources:
- 17 CFR 242.200(a): a short sale is a sale of a security the seller does not own,
  or a sale consummated by the delivery of a borrowed security.
- 17 CFR 242.200(c): a person is deemed to own a security only to the extent of a
  net long position.
- 17 CFR 242.200(g): a broker-dealer must mark every equity sell order "long",
  "short", or "short exempt". An order may be marked "long" only if the seller is
  deemed to own the security under (a)–(f) and either (i) the security to be
  delivered is in the physical possession or control of the broker or dealer, or
  (ii) it is reasonably expected that the security will be in the physical
  possession or control of the broker or dealer no later than the settlement of
  the transaction. "Short exempt" only if Rule 201(c) or (d) is met.
- 17 CFR 240.10b-21(a): it is a manipulative or deceptive device for any person
  to submit an order to sell an equity security if that person deceives a broker
  or dealer, a participant of a registered clearing agency, or a purchaser about
  its intention or ability to deliver the security on or before the settlement
  date, and such person fails to deliver the security on or before the settlement
  date. Both prongs are required. An honest fail, or a fail without deception, is
  not automatically a 10b-21 violation. Settlement date is the business day on
  which delivery and payment are to be made through a registered clearing agency
  (10b-21(b)) — teach that term, not the 2008 guide's historical "three day
  settlement period" / T+3 prose.
- The SEC small-entity compliance guide states that the rule targets, among other
  things, short sellers who deceive their broker about the locate source under
  Rule 203(b)(1), and sellers who misrepresent that they own the shares. Scienter
  is an element (adopting release). This toy is a checklist, not a finding of
  fraud and not a synonym for every fail-to-deliver.

Learning only; not a short-sale recipe or a legal conclusion.
"""
from decimal import Decimal

checks = 0


def check(cond, label):
    global checks
    assert cond, label
    checks += 1


def mark_sell(net_long_shares, in_possession_or_control, reasonably_expected_by_settlement, short_exempt_201=False):
    """Return the Rule 200(g) mark. A same-day purchase is not automatically 'long'."""
    deemed_to_own = Decimal(str(net_long_shares)) > 0
    if deemed_to_own and (in_possession_or_control or reasonably_expected_by_settlement):
        return "long"
    if short_exempt_201:
        return "short exempt"
    return "short"


print("=== A. Rule 200(g): 'long' is a statutory test, not a nickname ===")
cases = (
    ("net long, shares already in the broker's possession or control", 100, True, False, False, "long"),
    ("net long, purchase not yet received but reasonably expected by settlement", 100, False, True, False, "long"),
    ("net long on paper, but neither possession/control nor reasonably expected by settlement", 100, False, False, False, "short"),
    ("not deemed to own (flat or net short); plans to buy the shares later", 0, False, False, False, "short"),
    ("short, but Rule 201(c) or (d) is met", -50, False, False, True, "short exempt"),
)
for label, net, poss, expected, exempt, expect in cases:
    got = mark_sell(net, poss, expected, exempt)
    print(f"  {label}: mark={got}")
    check(got == expect, label)
print("a same-day purchase does not automatically make a same-day sale 'long'")
print("a sale of shares you do not own is a short sale even if you plan to buy them later")

print("=== B. Rule 10b-21 checklist: deception about delivery AND a fail ===")


def tenb21_both_prongs(deceived_about_delivery, failed_to_deliver_by_settlement):
    """Both statutory prongs are required. Not a finding of scienter or of liability."""
    return bool(deceived_about_delivery) and bool(failed_to_deliver_by_settlement)


for label, deceived, failed, expect in (
    ("deceived the broker about the locate source, and failed to deliver by the settlement date", True, True, True),
    ("honest fail: no deception, but failed to deliver by the settlement date", False, True, False),
    ("deceived about the ability to deliver, but delivered on or before the settlement date", True, False, False),
    ("no deception and delivered on time", False, False, False),
):
    got = tenb21_both_prongs(deceived, failed)
    print(f"  {label}: both_prongs={got}")
    check(got is expect, label)
print("an honest fail, or a fail without deception, is not automatically a 10b-21 violation")
print("do not recast an FTD file as proof of fraud; teach the rule's 'settlement date', not historical T+3 prose")
print(f"assertions passed: {checks}/{checks}")
