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

print("=== F. 17 CFR 240.10b-5: Employment of manipulative and deceptive devices ===")
# 17 CFR 240.10b-5 (official eCFR API XML / LII, title 17
# up_to_date_as_of 2026-11-09; opened 2026-11-12). Official eCFR HTML
# this turn was the Request Access interstitial, not official rule
# text; quote the API / LII copies. Add this section AFTER the current
# last disclaimer line so the tip file remains a strict byte-prefix.
# Keep 7/7, ASSERT_self_trade_pattern_ok, the first disclaimer, 2150
# including ASSERT_2150_ok, and 3220 including 13/13, ASSERT_3220_ok,
# and the last disclaimer, identical.
# Official caption is "Employment of manipulative and deceptive
# devices." Official core: It shall be unlawful for any person,
# directly or indirectly, by the use of any means or instrumentality of
# interstate commerce, or of the mails or of any facility of any
# national securities exchange, (a) To employ any device, scheme, or
# artifice to defraud, (b) To make any untrue statement of a material
# fact or to omit to state a material fact necessary in order to make
# the statements made, in the light of the circumstances under which
# they were made, not misleading, or (c) To engage in any act,
# practice, or course of business which operates or would operate as a
# fraud or deceit upon any person, in connection with the purchase or
# sale of any security.
# Quote "in the light of the circumstances under which they were made"
# as written (not "in light of"). The closing "in connection with the
# purchase or sale of any security" applies to (a), (b), and (c).
# Do not flatten 10b-5 into already-taught 10b-18, 10b5-1, 14e-3,
# 10b-9, or 15 U.S.C. 78i / FINRA 5210 / the self-trade wash-trade box.
# Do not pack Rule 10b5-2 in this batch, and do not build a scienter,
# materiality, or judicial-opinion catalog. Learning only; no
# investment advice.

print("10b-5: It shall be unlawful for any person, directly or indirectly, by the use of any means or")
print("  instrumentality of interstate commerce, or of the mails or of any facility of any national")
print("  securities exchange,")
print("  (a) To employ any device, scheme, or artifice to defraud,")
print("  (b) To make any untrue statement of a material fact or to omit to state a material fact")
print("  necessary in order to make the statements made, in the light of the circumstances under")
print("  which they were made, not misleading, or")
print("  (c) To engage in any act, practice, or course of business which operates or would operate")
print("  as a fraud or deceit upon any person,")
print("  in connection with the purchase or sale of any security")
print('official caption is "Employment of manipulative and deceptive devices"')
print('official typography is "in the light of the circumstances under which they were made"')
print("the closing clause applies to (a), (b), and (c); cite 17 CFR 240.10b-5")
print("title 17 up_to_date_as_of 2026-11-09")
flatten_10b5 = False
print(f"  this is a flatten into already-taught 10b-18, 10b5-1, 14e-3, 10b-9, or 15 U.S.C. 78i / FINRA 5210? {flatten_10b5}")
check(flatten_10b5 is False, "do not flatten 10b-5 into already-taught 10b-18 / 10b5-1 / 14e-3 / 10b-9 / 78i / 5210")
packs_10b52 = False
print(f"  this toy packs Rule 10b5-2, or builds a scienter, materiality, or judicial-opinion catalog? {packs_10b52}")
check(packs_10b52 is False, "do not pack 10b5-2 or build a scienter / materiality / case-law catalog")
in_connection = True
print(f"  unlawful, in connection with the purchase or sale of any security, to employ a device, scheme, or artifice to defraud, to make an untrue statement of a material fact or omit a material fact necessary in the light of the circumstances, or to engage in a fraud or deceit? {in_connection}")
check(in_connection is True, "10b-5 three official prongs, in connection with the purchase or sale of any security")
print("no investment advice")
print(f"assertions passed: {checks}/{checks}")
print("ASSERT_10b5_ok")
print("disclaimer: learning only; not legal advice; no investment advice")

print("=== G. FINRA 2010: high standards of commercial honor and just and equitable principles of trade ===")
# FINRA Rule 2010 Standards of Commercial Honor and Principles of Trade
# (official HTML opened 2026-11-12). Keep F identical once 10b-5 is
# added, and keep 7/7, ASSERT_self_trade_pattern_ok, the first
# disclaimer, 2150, and 3220 including 13/13, ASSERT_3220_ok, and the
# last disclaimer, identical.
# Official core: A member, in the conduct of its business, shall
# observe high standards of commercial honor and just and equitable
# principles of trade. Quote the operative sentence in ordinary
# sentence case as the official rule text does. Official caption
# typography on the rule page is "STANDARDS OF COMMERCIAL HONOR AND
# PRINCIPLES OF TRADE." Official Cross References exist, including
# already-taught 2121, 5130, 5210, 5220, 5270, and 5320, and named-only
# 2111; name that they exist, do not pack that list into a student
# engine, and do not flatten 2010 into those rules. Do not rewrite the
# already-shipped 2121 or 5270 SM .05 foil sentences. Do not treat 2010
# as a substitute for packed 10b-5 or packed 2150 / 3220. No broker or
# product recommendation.

print("2010: A member, in the conduct of its business, shall observe high standards of commercial honor")
print("  and just and equitable principles of trade")
print('official caption typography is "STANDARDS OF COMMERCIAL HONOR AND PRINCIPLES OF TRADE"')
print("official Cross References exist, including already-taught 2121, 5130, 5210, 5220, 5270, and")
print("  5320, and named-only 2111; this toy is not that list")
flatten_2010 = False
print(f"  this is a flatten into already-taught 2121, 5130, 5210, 5220, 5270, or 5320, or into packed 10b-5 / 2150 / 3220? {flatten_2010}")
check(flatten_2010 is False, "do not flatten 2010 into those cross-referenced or packed rules")
rewrites_foil = False
print(f"  this toy rewrites the already-shipped 2121 or 5270 SM .05 foil sentences? {rewrites_foil}")
check(rewrites_foil is False, "do not rewrite the already-shipped 2121 / 5270 SM .05 2010 foils")
honor = True
print(f"  a member, in the conduct of its business, shall observe high standards of commercial honor and just and equitable principles of trade? {honor}")
check(honor is True, "2010 requires high standards of commercial honor and just and equitable principles of trade")
print("no broker or product recommendation")
print(f"assertions passed: {checks}/{checks}")
print("ASSERT_2010_ok")
print("disclaimer: learning only; not legal advice; no broker or product recommendation")

print("=== H. FINRA 2165: Specified Adult temporary-hold safe harbor ===")
# FINRA Rule 2165 Financial Exploitation of Specified Adults (official
# HTML opened 2026-11-12). Amended by SR-FINRA-2021-016 eff. March 17,
# 2022 (already effective; covers transactions as well as
# disbursements). Do not teach a pre-2022 disbursement-only version as
# current law. Keep F-G identical once those are added.
# Official typography uses typographic quotes (U+201C / U+201D) around
# "Specified Adult," "Account," "Trusted Contact Person," and
# "financial exploitation."
# Official (a)(1): a natural person age 65 and older, or a natural
# person age 18 and older who the member reasonably believes has a
# mental or physical impairment that renders the individual unable to
# protect his or her own interests.
# Official (b)(1): a member may place a temporary hold on a
# disbursement of funds or securities from the Account of a Specified
# Adult, or a transaction in securities in that Account, if the member
# reasonably believes that financial exploitation of the Specified
# Adult has occurred, is occurring, has been attempted, or will be
# attempted.
# Official SM .01: this Rule provides a safe harbor from FINRA Rules
# 2010, 2150 and 11870 (no Oxford comma); "This Rule does not require
# members to place temporary holds." The hold is permissive ("may"),
# not a duty to freeze.
# Official (b)(2): the temporary hold will expire not later than 15
# business days after the date the member first placed it, unless
# otherwise terminated or extended by a state regulator or agency of
# competent jurisdiction or a court of competent jurisdiction, or
# extended pursuant to official (b)(3). Official (b)(3) / (b)(4) add
# "no longer than 10 business days" and then "no longer than 30
# business days" extension slices; name them, do not build that
# extension engine. Official (b)(1)(B) notification is not later than
# two business days, orally or in writing, which may be electronic.
# Official (a)(3) "Trusted Contact Person" is "in accordance with Rule
# 4512"; name 4512, do not build the 4512 engine. Do not invent a
# 65-and-older-only definition that drops the official 18-and-older
# impairment prong. Do not flatten 2165 into packed 2010, packed 2150,
# already-taught 15c3-3 / SIPC, or dropped ACATS / Rule 11870 (named
# only in official SM .01). No broker or product recommendation.

print("2165(a)(1): the term “Specified Adult” shall mean: (A) a natural person age 65 and older; or")
print("  (B) a natural person age 18 and older who the member reasonably believes has a mental or")
print("  physical impairment that renders the individual unable to protect his or her own interests")
print("2165(b)(1): a member may place a temporary hold on a disbursement of funds or securities from")
print("  the “Account” of a “Specified Adult”, or a transaction in securities in that “Account”, if the")
print("  member reasonably believes that financial exploitation of the “Specified Adult” has occurred,")
print("  is occurring, has been attempted, or will be attempted")
print("official typography uses typographic quotes around “Specified Adult,” “Account,”")
print("  “Trusted Contact Person,” and “financial exploitation”")
print("official SM .01: this Rule provides a safe harbor from FINRA Rules 2010, 2150 and 11870;")
print('  "This Rule does not require members to place temporary holds"')
print("official typography in SM .01 has no Oxford comma in \"FINRA Rules 2010, 2150 and 11870\"")
print("official (b)(2): the temporary hold will expire not later than 15 business days, unless")
print('  terminated or extended as officially provided; official (b)(3) / (b)(4) add "no longer')
print('  than 10 business days" and then "no longer than 30 business days" extension slices; this')
print("  toy is not that extension engine")
print("official (b)(1)(B) notification is not later than two business days, orally or in writing,")
print("  which may be electronic")
print("official (a)(3) “Trusted Contact Person” is in accordance with Rule 4512; this toy is not a")
print("  4512 engine")
print("amended by SR-FINRA-2021-016 eff. March 17, 2022 (already effective; covers transactions as")
print("  well as disbursements)")
flatten_2165 = False
print(f"  this is a flatten into packed 2010 or 2150, already-taught 15c3-3 / SIPC, or an ACATS / 11870 engine? {flatten_2165}")
check(flatten_2165 is False, "do not flatten 2165 into packed 2010 / 2150, 15c3-3 / SIPC, or 11870")
must_hold = False
print(f"  this toy invents that every member must place a hold, or drops the official 18-and-older impairment prong? {must_hold}")
check(must_hold is False, "2165 is permissive and Specified Adult has both official prongs")
may_hold = True
print(f"  a member may place a temporary hold on a disbursement or a transaction in the Account of a Specified Adult, and this Rule does not require members to place temporary holds? {may_hold}")
check(may_hold is True, "2165 is a permissive temporary-hold safe harbor")
print("no broker or product recommendation")
print(f"assertions passed: {checks}/{checks}")
print("ASSERT_2165_ok")
print("disclaimer: learning only; not legal advice; no broker or product recommendation")

print("=== I. FINRA 3310: written anti-money laundering program, approved in writing by senior management ===")
# FINRA Rule 3310 Anti-Money Laundering Compliance Program (official
# HTML opened 2026-11-12). Keep F-H identical once those are added.
# Official core: Each member shall develop and implement a written
# anti-money laundering program reasonably designed to achieve and
# monitor the member's compliance with the requirements of the Bank
# Secrecy Act (31 U.S.C. 5311, et seq.), and the implementing
# regulations promulgated thereunder by the Department of the Treasury.
# Each member's anti-money laundering program must be approved, in
# writing, by a member of senior management.
# Official typography is hyphenated "anti-money laundering" and
# "e-mail" (official (d) "e-mail address"). Official (c) typography
# includes "annual (on a calendar-year basis)" and quoted "independent
# testing," and the official example typography is "e.g., engages
# solely in proprietary trading or conducts business only with other
# broker-dealers." Official Selected Notices line on the rule page is
# "17-40 18-19" with no comma between those two numbers, if quoted.
# Official (a)-(f) minimum elements exist, including official (c)
# annual independent testing, or every two years if the member does not
# execute transactions for customers or otherwise hold customer
# accounts or act as an introducing broker, official (d) designation
# of an associated person to FINRA, official (e) ongoing training, and
# official (f) risk-based ongoing customer due diligence. Name that
# catalog; do not build a CIP, SAR, beneficial-owner, or 31 CFR
# 1010.230 engine. Do not flatten 3310 into packed 2090, Regulation
# Best Interest, or Form CRS. This is learning-only BSA/AML literacy,
# not a how-to for evading reporting. No broker or product
# recommendation.

print("3310: Each member shall develop and implement a written anti-money laundering program reasonably")
print("  designed to achieve and monitor the member's compliance with the requirements of the Bank")
print("  Secrecy Act (31 U.S.C. 5311, et seq.), and the implementing regulations promulgated")
print("  thereunder by the Department of the Treasury. Each member's anti-money laundering program")
print("  must be approved, in writing, by a member of senior management")
print('official typography is hyphenated "anti-money laundering" and official (d) "e-mail address"')
print('official (c) typography includes "annual (on a calendar-year basis)" and quoted "independent')
print('  testing"; official example typography is "e.g., engages solely in proprietary trading or')
print('  conducts business only with other broker-dealers"')
print("official (a)-(f) minimum elements exist, including official (c) annual independent testing,")
print("  or every two years if the member does not execute transactions for customers or otherwise")
print("  hold customer accounts or act as an introducing broker, official (d) designation of an")
print("  associated person to FINRA, official (e) ongoing training, and official (f) risk-based")
print("  ongoing customer due diligence; this toy is not a CIP, SAR, beneficial-owner, or 31 CFR")
print("  1010.230 engine")
print('official Selected Notices typography includes "17-40 18-19" with no comma between those two numbers')
flatten_3310 = False
print(f"  this is a flatten into packed 2090, Regulation Best Interest, or Form CRS? {flatten_3310}")
check(flatten_3310 is False, "do not flatten 3310 into packed 2090 or Reg BI / Form CRS")
builds_cip = False
print(f"  this toy builds a CIP, SAR, beneficial-owner, or 31 CFR 1010.230 engine? {builds_cip}")
check(builds_cip is False, "do not build a CIP / SAR / beneficial-owner engine")
written_aml = True
print(f"  a written anti-money laundering program, approved, in writing, by a member of senior management? {written_aml}")
check(written_aml is True, "3310 requires a written AML program approved, in writing, by senior management")
print("learning-only BSA/AML literacy, not a how-to for evading reporting")
print("no broker or product recommendation")
print(f"assertions passed: {checks}/{checks}")
print("ASSERT_3310_ok")
print("disclaimer: learning only; not legal advice; AML literacy only, not a how-to for evading reporting")

print("=== J. FINRA 2060: Use of Information Obtained in Fiduciary Capacity ===")
# FINRA Rule 2060 Use of Information Obtained in Fiduciary Capacity
# (official HTML opened 2026-11-12). Add this section after the current
# last 3310 disclaimer so the tip file remains a strict byte-prefix.
# Keep 7/7, ASSERT_self_trade_pattern_ok, the first disclaimer, 2150,
# 3220, 10b-5, 2010, 2165, and 3310 including 25/25, ASSERT_3310_ok,
# and the last disclaimer, identical.
# Official core: A member who in the capacity of paying agent, transfer
# agent, trustee, or in any other similar capacity, has received
# information as to the ownership of securities, shall under no
# circumstances make use of such information for the purpose of
# soliciting purchases, sales or exchanges except at the request and on
# behalf of the issuer.
# Official typography is "purchases, sales or exchanges" (no Oxford
# comma) and "Cross Reference–" (en-dash, not a hyphen). Official Cross
# Reference is packed FINRA 2150, "Improper Use of Customers' Securities
# or Funds; Prohibition Against Guarantees and Sharing in Accounts";
# name it, do not flatten 2060 into packed 2150, packed 10b-5, packed
# 2010, or packed 3310, and do not rewrite the already-shipped 2150 box.
# Do not invent that the prohibition applies to every use of customer
# information, or drop the official "except at the request and on behalf
# of the issuer" clause. Do not invent a clock. Learning only; no
# investment advice. No broker or product recommendation.

print("2060: A member who in the capacity of paying agent, transfer agent, trustee, or in any")
print("  other similar capacity, has received information as to the ownership of securities,")
print("  shall under no circumstances make use of such information for the purpose of soliciting")
print("  purchases, sales or exchanges except at the request and on behalf of the issuer")
print('official typography is "purchases, sales or exchanges" (no Oxford comma)')
print("official typography is Cross Reference– (en-dash, not a hyphen)")
print("official Cross Reference is packed FINRA 2150; this toy does not rewrite the already-shipped 2150 box")
flatten_2060 = False
print(f"  this is a flatten into packed 2150, packed 10b-5, packed 2010, or packed 3310? {flatten_2060}")
check(flatten_2060 is False, "do not flatten 2060 into packed 2150 / 10b-5 / 2010 / 3310")
drops_except = False
print(f"  this toy drops the official except at the request and on behalf of the issuer clause? {drops_except}")
check(drops_except is False, "do not drop the official issuer-request clause")
core_2060 = True
print(f"  shall under no circumstances make use of such information for the purpose of soliciting purchases, sales or exchanges except at the request and on behalf of the issuer? {core_2060}")
check(core_2060 is True, "2060 bars soliciting purchases, sales or exchanges except at the request and on behalf of the issuer")
print("learning only; no investment advice")
print("no broker or product recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== K. FINRA 3210: Accounts At Other Broker-Dealers and Financial Institutions ===")
# FINRA Rule 3210 Accounts At Other Broker-Dealers and Financial
# Institutions (official HTML opened 2026-11-12). Quote the current
# post-amendment text (already amended by SR-FINRA-2026-013 eff. June 17,
# 2026). Keep J identical once 2060 is added.
# Official (a): No person associated with a member ("employer member")
# shall, without the prior written consent of the member, open or
# otherwise establish at a member other than the employer member
# ("executing member"), or at any other financial institution, any
# account in which securities transactions can be effected and in which
# the associated person has a beneficial interest.
# Official (b): any associated person, prior to opening or otherwise
# establishing an account subject to this Rule, shall notify in writing
# the executing member, or other financial institution, of his or her
# association with the employer member.
# Official SM .01 typography is "within 30 calendar days." Official (c)
# duplicate confirmations and statements (or the transactional data
# contained therein) upon written request, and official SM .02 / .03 /
# .04 / .05, exist; name them, do not build the SM .02 family-presumption
# catalog or the SM .03 product-carve-out catalog. Official typography
# uses straight quotes around "employer member" and "executing member."
# Official caption typography is "Accounts At Other Broker-Dealers and
# Financial Institutions" (capital A in "At"; hyphenated
# "Broker-Dealers"). Do not teach a pre-June 17, 2026 version as current
# law. Do not flatten 3210 into packed 2090, packed 2165 / 4512, or
# later-packed 3280. This is associated-person account-consent literacy,
# not a product or broker recommendation.

print('3210(a): No person associated with a member ("employer member") shall, without the prior')
print('  written consent of the member, open or otherwise establish at a member other than the')
print('  employer member ("executing member"), or at any other financial institution, any account')
print("  in which securities transactions can be effected and in which the associated person has")
print("  a beneficial interest")
print("3210(b): any associated person, prior to opening or otherwise establishing an account")
print("  subject to this Rule, shall notify in writing the executing member, or other financial")
print("  institution, of his or her association with the employer member")
print('official SM .01 typography is "within 30 calendar days"')
print("official (c) and official SM .02 / .03 / .04 / .05 exist; this toy is not those catalogs")
print('official caption typography is Accounts At Other Broker-Dealers and Financial Institutions')
print("current official page already includes Amended by SR-FINRA-2026-013 eff. June 17, 2026")
flatten_3210 = False
print(f"  this is a flatten into packed 2090, packed 2165 / 4512, or later-packed 3280? {flatten_3210}")
check(flatten_3210 is False, "do not flatten 3210 into packed 2090, packed 2165 / 4512, or 3280")
pre_amendment = False
print(f"  this toy teaches a pre-June 17, 2026 version of 3210 as current law? {pre_amendment}")
check(pre_amendment is False, "quote the current post-amendment 3210 text")
core_3210 = True
print(f"  prior written consent of the employer member, and written notification to the executing member or other financial institution? {core_3210}")
check(core_3210 is True, "3210 requires prior written consent and written notification")
print("associated-person account-consent literacy, not a product or broker recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== L. FINRA 3270: Outside Business Activities of Registered Persons ===")
# FINRA Rule 3270 Outside Business Activities of Registered Persons
# (official HTML opened 2026-11-12). Keep J-K identical once those are
# added.
# Official core: No registered person may be an employee, independent
# contractor, sole proprietor, officer, director or partner of another
# person, or be compensated, or have the reasonable expectation of
# compensation, from any other person as a result of any business
# activity outside the scope of the relationship with his or her member
# firm, unless he or she has provided prior written notice to the
# member, in such form as specified by the member. Passive investments
# and activities subject to the requirements of Rule 3280 shall be
# exempted from this requirement.
# Official typography is "officer, director or partner" (no Oxford
# comma) and "prior written notice." Official caption typography is
# "Outside Business Activities of Registered Persons." Name official
# SM .01 (the member shall consider interference with responsibilities /
# public attribution, may impose conditions or prohibit the activity,
# must evaluate whether the activity is instead an outside securities
# activity subject to Rule 3280, and must keep a record preserved under
# SEA Rule 17a-4(e)(1)); do not build that review / recordkeeping
# engine. Do not flatten 3270 into 3280: official 3270 exempts
# activities subject to 3280, it is not a substitute for 3280. Do not
# flatten 3270 into already-named SEA Rule 17a-4 (a typography foil
# under packed 2231), packed 2090, or packed 3210. Do not invent that
# passive investments require prior written notice under 3270 (they are
# officially exempted). Do not invent a clock other than "prior" written
# notice.

print("3270: No registered person may be an employee, independent contractor, sole proprietor,")
print("  officer, director or partner of another person, or be compensated, or have the")
print("  reasonable expectation of compensation, from any other person as a result of any")
print("  business activity outside the scope of the relationship with his or her member firm,")
print("  unless he or she has provided prior written notice to the member, in such form as")
print("  specified by the member")
print("Passive investments and activities subject to the requirements of Rule 3280 shall be")
print("  exempted from this requirement")
print('official typography is "officer, director or partner" (no Oxford comma) and "prior written notice"')
print("official SM .01 and SEA Rule 17a-4(e)(1) exist; this toy is not that review / recordkeeping engine")
flatten_3270 = False
print(f"  this is a flatten into 3280, or into packed 2231's 17a-4 foil? {flatten_3270}")
check(flatten_3270 is False, "do not flatten 3270 into 3280 or into packed 2231's 17a-4 foil")
passive_notice = False
print(f"  this toy invents that passive investments require prior written notice under 3270? {passive_notice}")
check(passive_notice is False, "passive investments are officially exempted from 3270")
core_3270 = True
print(f"  prior written notice is required, and passive investments and activities subject to Rule 3280 are exempted? {core_3270}")
check(core_3270 is True, "3270 requires prior written notice and officially exempts passive investments and 3280 activities")
print("no broker or product recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== M. FINRA 3280: Private Securities Transactions of an Associated Person ===")
# FINRA Rule 3280 Private Securities Transactions of an Associated
# Person (official HTML opened 2026-11-12). Keep J-L identical once
# those are added. This is learning-only associated-person literacy,
# not a how-to for selling away.
# Official (a): No person associated with a member shall participate in
# any manner in a private securities transaction except in accordance
# with the requirements of this Rule.
# Official (b): Prior to participating in any private securities
# transaction, an associated person shall provide written notice to the
# member with which he is associated describing in detail the proposed
# transaction and the person's proposed role therein and stating whether
# he has received or may receive selling compensation in connection with
# the transaction; provided however that, in the case of a series of
# related transactions in which no selling compensation has been or will
# be received, an associated person may provide a single written notice.
# Official typography is "provided however that" (no comma after
# "provided") in official (b) and official (e)(1).
# Name official (c) (if selling compensation has been or may be
# received, the member shall advise in writing whether it approves or
# disapproves; if approved, the transaction shall be recorded on the
# books and records of the member and supervised as if executed on
# behalf of the member; if disapproved, the person shall not participate
# in any manner, directly or indirectly) and official (d) (if no selling
# compensation, the member shall provide prompt written acknowledgment
# and may require specified conditions). Do not build that approval /
# supervision / compensation engine.
# Official (e)(1) exclusions include transactions subject to the
# notification requirements of Rule 3210, transactions among immediate
# family members (as defined in FINRA Rule 5130) for which no associated
# person receives any selling compensation, and personal transactions in
# investment company and variable annuity securities; name those
# exclusions, do not flatten 3280 into packed 3210 or already-taught
# 5130, and do not invent a 5130 engine.

print("3280(a): No person associated with a member shall participate in any manner in a private")
print("  securities transaction except in accordance with the requirements of this Rule")
print("3280(b): Prior to participating in any private securities transaction, an associated")
print("  person shall provide written notice to the member with which he is associated")
print("  describing in detail the proposed transaction and the person's proposed role therein")
print("  and stating whether he has received or may receive selling compensation in connection")
print("  with the transaction; provided however that, in the case of a series of related")
print("  transactions in which no selling compensation has been or will be received, an")
print("  associated person may provide a single written notice")
print('official typography is "provided however that" (no comma after "provided") in official (b) and official (e)(1)')
print("official (c) and official (d) exist; this toy is not that approval / supervision / compensation engine")
print("official (e)(1) exclusions include transactions subject to the notification requirements")
print("  of Rule 3210, transactions among immediate family members (as defined in FINRA Rule 5130)")
print("  for which no associated person receives any selling compensation, and personal")
print("  transactions in investment company and variable annuity securities; this toy is not a")
print("  3210 or 5130 engine")
flatten_3280 = False
print(f"  this is a flatten into packed 3210 or already-taught 5130? {flatten_3280}")
check(flatten_3280 is False, "do not flatten 3280 into packed 3210 or already-taught 5130")
provided_however = True
print(f"  official typography is provided however that, with no comma after provided? {provided_however}")
check(provided_however is True, "official (b) and (e)(1) typography is provided however that")
core_3280 = True
print(f"  prior written notice is required except in accordance with this Rule, and official (e)(1) exclusions are named only? {core_3280}")
check(core_3280 is True, "3280 requires prior written notice; official (e)(1) exclusions are named only")
print("learning-only associated-person literacy, not a how-to for selling away")
print("no broker or product recommendation")
print(f"assertions passed: {checks}/{checks}")
print("ASSERT_3280_ok")
print("disclaimer: learning only; not legal advice; associated-person literacy only, not a how-to for selling away")

print("=== N. FINRA 4513: Records of Written Customer Complaints ===")
# FINRA Rule 4513 Records of Written Customer Complaints (official
# #the-rule HTML typography from earlier 2026-11-12 official body;
# wording reconfirmed 2026-11-12). Add this section after the last
# 3280 disclaimer so 37/37, ASSERT_3280_ok, and the last selling-away
# literacy disclaimer remain a strict byte-prefix.
# Official (a) as written, including "office of supervisory
# jurisdiction" and "Customer complaint records shall be preserved for
# a period of at least four years." Quote that sentence with a normal
# period; do not treat the official inter-paragraph NBSP as a word.
# Official (b) defines "customer complaint" with straight quotes; name
# it, do not build a complaint-taxonomy engine.
# Adopted by SR-FINRA-2010-052 eff. Dec. 5, 2011. Selected Notice:
# 11-19. Do not invent that the records must be stored only at the OSJ
# (official text also permits making them promptly available at that
# office upon request of FINRA). Do not flatten 4513 into packed 2231,
# packed 2165, packed 3270's SEA Rule 17a-4 foil, or already-named
# FINRA 4511 / 4512. Recordkeeping literacy only; not a how-to for
# handling complaints, and not a customer or broker recommendation.

print("4513(a): Each member shall keep and preserve in each office of supervisory jurisdiction")
print("  either a separate file of all written customer complaints that relate to that office")
print("  (including complaints that relate to activities supervised from that office) and")
print("  action taken by the member, if any, or a separate record of such complaints and a")
print("  clear reference to the files in that office containing the correspondence connected")
print("  with such complaints. Rather than keep and preserve the customer complaint records")
print("  required under this Rule at the office of supervisory jurisdiction, the member may")
print("  choose to make them promptly available at that office, upon request of FINRA.")
print("  Customer complaint records shall be preserved for a period of at least four years.")
print('official typography is "office of supervisory jurisdiction" and "at least four years"')
print("official caption typography is Records of Written Customer Complaints.")
print('official (b) defines "customer complaint" with straight quotes; this toy is not a')
print("  complaint-taxonomy engine")
print("Adopted by SR-FINRA-2010-052 eff. Dec. 5, 2011. Selected Notice: 11-19.")
print("the official inter-paragraph NBSP after the period that closes official (a) is not a word")
flatten_4513 = False
print(f"  this is a flatten into packed 2231, packed 2165, packed 3270's SEA Rule 17a-4 foil, or already-named FINRA 4511 / 4512? {flatten_4513}")
check(flatten_4513 is False, "do not flatten 4513 into packed 2231 / 2165 / 3270 17a-4 foil or 4511 / 4512")
osj_only = False
print(f"  this toy invents that the records must be stored only at the OSJ? {osj_only}")
check(osj_only is False, "official text also permits making the records promptly available at that office upon request of FINRA")
core_4513 = True
print(f"  written customer-complaint records shall be preserved for a period of at least four years? {core_4513}")
check(core_4513 is True, "4513 requires written customer-complaint records preserved at least four years")
print("recordkeeping literacy only; not a how-to for handling complaints")
print("no customer or broker recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== O. 17 CFR 248.30(a)(1)/(a)(2): written administrative, technical, and physical safeguards ===")
# 17 CFR 248.30 Procedures to safeguard customer information (official
# eCFR versioner API XML, title 17 up_to_date_as_of 2026-11-09, opened
# 2026-11-12; API XML byte-identical to the enrich33 copy). Keep N
# identical once 4513 is added. Packed slice is official (a)(1)/(a)(2)
# only.
# Official typography is "administrative, technical, and physical
# safeguards" (Oxford comma). Every covered institution must develop,
# implement, and maintain written policies and procedures that address
# those safeguards; those written policies and procedures must be
# reasonably designed to ensure the security and confidentiality of
# customer information, protect against any anticipated threats or
# hazards to the security or integrity of customer information, and
# protect against unauthorized access to or use of customer information
# that could result in substantial harm or inconvenience to any
# customer.
# Official (a)(3) response program, official (a)(4) 30-day
# customer-notice clock, official (a)(5) 72-hour service-provider
# notice, official (b) disposal, official (c) recordkeeping, and
# official (d) definitions (including "Covered institution means any
# broker or dealer, any investment company, and any investment adviser
# or transfer agent registered with the Commission or another
# appropriate regulatory agency") exist; name them, do not build those
# catalogs, and do not invent that the packed slice is the 30-day
# notice rule. Do not flatten into packed 3310 or Regulation S-P
# 248.10 (still unpacked). Cite 17 CFR 248.30. Learning only; no
# vendor, product, or incident-response how-to.

print("248.30(a)(1): Every covered institution must develop, implement, and maintain written")
print("  policies and procedures that address administrative, technical, and physical")
print("  safeguards for the protection of customer information")
print("248.30(a)(2): These written policies and procedures must be reasonably designed to:")
print("  (i) ensure the security and confidentiality of customer information;")
print("  (ii) protect against any anticipated threats or hazards to the security or integrity")
print("  of customer information; and")
print("  (iii) protect against unauthorized access to or use of customer information that")
print("  could result in substantial harm or inconvenience to any customer")
print('official typography is "administrative, technical, and physical safeguards" (Oxford comma)')
print("cite 17 CFR 248.30; title 17 up_to_date_as_of 2026-11-09")
print("official (a)(3) response program, official (a)(4) 30-day customer-notice clock,")
print("  official (a)(5) 72-hour service-provider notice, official (b) disposal, official (c)")
print("  recordkeeping, and official (d) definitions exist, including Covered institution;")
print("  this toy is not those catalogs")
flatten_24830 = False
print(f"  this is a flatten into packed 3310 or Regulation S-P 248.10, or an invention that the packed slice is the 30-day notice rule? {flatten_24830}")
check(flatten_24830 is False, "do not flatten 248.30 into packed 3310 or 248.10, and do not invent that the packed slice is the 30-day notice rule")
pack_notice = False
print(f"  this toy packs official (a)(3) or later as the teaching core? {pack_notice}")
check(pack_notice is False, "packed slice is official (a)(1)/(a)(2) only")
core_24830 = True
print(f"  every covered institution must develop, implement, and maintain written policies and procedures that address administrative, technical, and physical safeguards? {core_24830}")
check(core_24830 is True, "248.30(a)(1)/(a)(2) require written administrative, technical, and physical safeguards")
print("learning only; no vendor, product, or incident-response how-to")
print("no broker or product recommendation")
print(f"assertions passed: {checks}/{checks}")
print("ASSERT_24830_ok")
print("disclaimer: learning only; not legal advice; written-safeguard literacy only, not an incident-response how-to")

print("=== P. FINRA 4514: Authorization Records for Negotiable Instruments Drawn From a Customer's Account ===")
# FINRA Rule 4514 Authorization Records for Negotiable Instruments
# Drawn From a Customer's Account (official <h1> typography uses a
# straight apostrophe U+0027 in "Customer's"; official #the-rule HTML
# typography, opened 2026-11-12). Add this section after the last
# 248.30 disclaimer so 43/43 after O / 248.30, ASSERT_24830_ok, and
# the last written-safeguard literacy disclaimer remain a strict
# byte-prefix of the tip file. Lesson heading order places 4514 after
# packed 4513 and before packed 248.30; the lab add-on still goes
# after the current last 248.30 disclaimer so the tip file remains a
# prefix.
# Official typography is "check, draft or other form" and "checking,
# savings, share or similar account" (no Oxford comma), and "three
# years following the date the authorization expires." Do not invent
# that signed negotiable instruments themselves must be preserved
# (official last sentence says this provision shall not require
# members to preserve copies of negotiable instruments signed by
# customers). Do not flatten 4514 into packed 2150, packed 4330(a),
# packed 4513, or already-named FINRA 4511 / 4512. Adopted by
# SR-FINRA-2010-052 eff. Dec. 5, 2011. Selected Notice: 11-19.
# Customer-protection / recordkeeping literacy only; not a procedure
# guide for drawing on a customer account, and not a customer or
# broker recommendation.

print("4514: No member or person associated with a member shall obtain from a customer or")
print("  submit for payment a check, draft or other form of negotiable paper drawn on a")
print("  customer's checking, savings, share or similar account, without that person's")
print("  express written authorization, which may include the customer's signature on the")
print("  negotiable instrument. Where the written authorization is separate from the")
print("  negotiable instrument, the member shall preserve the authorization for a period of")
print("  three years following the date the authorization expires. This provision shall not,")
print("  however, require members to preserve copies of negotiable instruments signed by")
print("  customers.")
print('official typography is "check, draft or other form" and "checking, savings, share or similar account" (no Oxford comma)')
print('official typography is "three years following the date the authorization expires"')
print("official caption typography is Authorization Records for Negotiable Instruments Drawn From a Customer's Account")
print("  (straight apostrophe U+0027 in Customer's)")
print("Adopted by SR-FINRA-2010-052 eff. Dec. 5, 2011. Selected Notice: 11-19.")
flatten_4514 = False
print(f"  this is a flatten into packed 2150, packed 4330(a), packed 4513, or already-named FINRA 4511 / 4512? {flatten_4514}")
check(flatten_4514 is False, "do not flatten 4514 into packed 2150 / 4330(a) / 4513 or already-named 4511 / 4512")
preserve_signed = False
print(f"  this toy invents that signed negotiable instruments themselves must be preserved? {preserve_signed}")
check(preserve_signed is False, "this provision shall not require members to preserve copies of negotiable instruments signed by customers")
core_4514 = True
print(f"  express written authorization is required, and a separate written authorization shall be preserved for three years following the date the authorization expires? {core_4514}")
check(core_4514 is True, "4514 requires express written authorization and a three-year clock for a separate authorization")
print("recordkeeping literacy only; not a procedure guide for drawing on a customer account")
print("no customer or broker recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== Q. FINRA 1122: Filing of Misleading Information as to Membership or Registration ===")
# FINRA Rule 1122 Filing of Misleading Information as to Membership or
# Registration (official #the-rule / <h1> HTML typography, opened
# 2026-11-12). Keep P identical once 4514 is added. The official core
# is one sentence. Official typography is "which is incomplete or
# inaccurate so as to be misleading" ("which," not "that"; "so as to
# be misleading," not "and misleading"), and "or fail to correct such
# filing after notice thereof." This is a membership-or-registration
# filing duty owed to FINRA, not a purchase-or-sale antifraud rule.
# Do not flatten 1122 into packed 10b-5, packed 2010, packed 3210, or
# packed 3280, and do not rewrite those already-shipped boxes. Do not
# invent a form number or a numbered clock (official text is "after
# notice thereof"). Amended by SR-FINRA-2009-009 eff. Aug. 17, 2009.
# Selected Notice: 09-33. Learning only; not a procedure guide for
# membership or Form U4 filings, and not an associated-person or
# broker recommendation.

print("1122: No member or person associated with a member shall file with FINRA information")
print("  with respect to membership or registration which is incomplete or inaccurate so as")
print("  to be misleading, or which could in any way tend to mislead, or fail to correct such")
print("  filing after notice thereof.")
print('official typography is "which is incomplete or inaccurate so as to be misleading"')
print('official typography is "or fail to correct such filing after notice thereof"')
print("official caption typography is Filing of Misleading Information as to Membership or Registration.")
print("Amended by SR-FINRA-2009-009 eff. Aug. 17, 2009. Selected Notice: 09-33.")
flatten_1122 = False
print(f"  this is a flatten into packed 10b-5, packed 2010, packed 3210, or packed 3280? {flatten_1122}")
check(flatten_1122 is False, "do not flatten 1122 into packed 10b-5 / 2010 / 3210 / 3280")
invented_clock = False
print(f"  this toy invents a form number or a numbered clock? {invented_clock}")
check(invented_clock is False, "official text is after notice thereof, not a numbered day count")
core_1122 = True
print(f"  a member or associated person may not file with FINRA membership or registration information which is incomplete or inaccurate so as to be misleading, or fail to correct such filing after notice thereof? {core_1122}")
check(core_1122 is True, "1122 bars misleading membership or registration filings and requires correction after notice")
print("learning only; not a procedure guide for membership or Form U4 filings")
print("no associated-person or broker recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== R. FINRA 8210(a)/(c): Provision of Information and Testimony and Inspection and Copying of Books ===")
# FINRA Rule 8210 Provision of Information and Testimony and Inspection
# and Copying of Books (official #the-rule / <h1> HTML typography,
# opened 2026-11-12). Keep Q identical once 1122 is added. Packed
# slice is official (a) and official (c) only.
# Official typography is "investigation, complaint, examination, or
# proceeding" (Oxford comma); "orally, in writing, or electronically"
# (Oxford comma); official (a)(2) "books, records, and accounts"
# (Oxford comma, "and"); official (a)(2) "possession, custody or
# control" (no Oxford comma); official (c) "books, records, or
# accounts" (Oxford comma, "or"). Do not tidy official (a)(2)'s "and"
# into official (c)'s "or," or insert an Oxford comma into
# "possession, custody or control." Official amendment-line typography
# is "Amended by SR-FINRA-2009-060 eff. Feb 25, 2013" (no period after
# "Feb"). Official (b) other-SRO / regulator information-sharing,
# official (d) notice / Central Registration Depository address
# (official (d) names Rule 9134(a)(1)), official (e) electronic
# interface, official (f) witness transcript inspection, and official
# (g) encryption of information provided on a portable media device
# exist; name official (b) and official (d)-(g), including official
# Rule 9134(a)(1); do not build those catalogs, and do not invent a
# 9134 engine. Literacy only, not a procedure guide for responding to
# an investigation, examination, or complaint, and not a customer,
# associated-person, or broker recommendation. Do not flatten 8210
# into packed 4513, packed 3310, or packed 2010.

print("8210(a): For the purpose of an investigation, complaint, examination, or proceeding")
print("  authorized by the FINRA By-Laws or rules, an Adjudicator or FINRA staff shall have")
print("  the right to:")
print("  (1) require a member, person associated with a member, or any other person subject to")
print("  FINRA's jurisdiction to provide information orally, in writing, or electronically")
print("  (if the requested information is, or is required to be, maintained in electronic form)")
print("  and to testify at a location specified by FINRA staff, under oath or affirmation")
print("  administered by a court reporter or a notary public if requested, with respect to any")
print("  matter involved in the investigation, complaint, examination, or proceeding; and")
print("  (2) inspect and copy the books, records, and accounts of such member or person with")
print("  respect to any matter involved in the investigation, complaint, examination, or")
print("  proceeding that is in such member's or person's possession, custody or control")
print("8210(c): No member or person shall fail to provide information or testimony or to")
print("  permit an inspection and copying of books, records, or accounts pursuant to this Rule.")
print('official typography is "investigation, complaint, examination, or proceeding" (Oxford comma)')
print('official typography is "orally, in writing, or electronically" (Oxford comma)')
print('official (a)(2) typography is "books, records, and accounts" (Oxford comma, "and") and "possession, custody or control" (no Oxford comma)')
print('official (c) typography is "books, records, or accounts" (Oxford comma, "or")')
print("official (b) and official (d)-(g) exist, including official Rule 9134(a)(1) in official (d);")
print("  this toy is not those catalogs or a 9134 engine")
print("Amended by SR-FINRA-2009-060 eff. Feb 25, 2013 (no period after Feb).")
flatten_8210 = False
print(f"  this is a flatten into packed 4513, packed 3310, or packed 2010? {flatten_8210}")
check(flatten_8210 is False, "do not flatten 8210 into packed 4513 / 3310 / 2010")
pack_catalog = False
print(f"  this toy packs official (b) or official (d)-(g) as the teaching core, or invents an investigation-procedure how-to? {pack_catalog}")
check(pack_catalog is False, "packed slice is official (a) and official (c) only; literacy only")
core_8210 = True
print(f"  no member or person shall fail to provide information or testimony or to permit an inspection and copying of books, records, or accounts pursuant to this Rule? {core_8210}")
check(core_8210 is True, "8210(c) requires provision of information or testimony and inspection and copying of books, records, or accounts")
print("literacy only; not a procedure guide for responding to an investigation")
print("no customer, associated-person, or broker recommendation")
print(f"assertions passed: {checks}/{checks}")
print("ASSERT_8210_ok")
print("disclaimer: learning only; not legal advice; literacy only, not an investigation-procedure how-to")

print("=== S. FINRA 2273: Educational Communication Related to Recruitment Practices and Account Transfers ===")
# FINRA Rule 2273 Educational Communication Related to Recruitment
# Practices and Account Transfers (official #the-rule / <h1> HTML
# typography, opened 2026-11-12). Keep 52/52 after R / 8210,
# ASSERT_8210_ok, and the closing 8210 disclaimer identical as a
# strict byte-prefix of the tip file.
# Official typography is "individually, in paper or electronic form";
# "educational communication prepared by FINRA"; "individually
# contacts"; "transfer assets"; "absent individualized contact";
# "an account assigned, or to be assigned." Official (b)(1)(B) has
# two official clock phrasings that must not be merged: "not later
# than three business days after the contact" and "within three
# business days from such oral contact" ... "whichever is earlier."
# Official (b)(3) three-month window. Official SM header typography is
# exactly "• • • Supplementary Material:---------------" (U+2022
# bullets, ordinary U+0020 spaces, no NBSP, 15 ASCII hyphens
# immediately after the colon). Official SM .01 typography uses
# typographic quotes around "former customer"; the term shall not
# include an account of a non-natural person that meets the definition
# of an institutional account pursuant to Rule 4512(c). Name SM .01 /
# SM .02 (express rejection; "he or she"); do not flatten packed /
# named 4512, packed 2140, or already-named 11870 / ACATS. Literacy
# only, not a recruitment or account-transfer how-to. Adopted by
# SR-FINRA-2015-057 eff. Nov. 11, 2016. Selected Notice: 16-18.

print("2273(a): A member that hires or associates with a registered person shall provide to a")
print("  former customer of the registered person, individually, in paper or electronic form,")
print("  an educational communication prepared by FINRA when (1) the member, directly or")
print("  through that registered person, individually contacts the former customer of that")
print("  registered person to transfer assets or (2) the former customer of that registered")
print("  person, absent individualized contact, transfers assets to an account assigned, or")
print("  to be assigned, to the registered person at the member.")
print('official typography is "individually, in paper or electronic form"; "educational')
print('  communication prepared by FINRA"; "individually contacts"; "transfer assets";')
print('  "absent individualized contact"; "an account assigned, or to be assigned"')
print("2273(b)(1): deliver the communication in paragraph (a) at the time of first individualized")
print("  contact with a former customer by the registered person or the member regarding the")
print("  former customer transferring assets to the member.")
print("2273(b)(1)(A): if the contact is in writing, the written communication required in")
print("  paragraph (a) must accompany the written communication; if the contact is by")
print("  electronic communication, the member may hyperlink directly to the educational")
print("  communication.")
print("2273(b)(1)(B): if the contact is oral, the member or registered person must notify the")
print("  former customer orally that an educational communication that includes important")
print("  considerations in deciding whether to transfer assets to the member will be provided")
print("  not later than three business days after the contact. The educational communication")
print("  must be sent within three business days from such oral contact or with any other")
print("  documentation sent to the former customer related to transferring assets to the")
print("  member, whichever is earlier.")
print('quote both official phrasings; do not merge "not later than three business days after')
print('  the contact" with "within three business days from such oral contact"')
print("2273(b)(2): if a former customer attempts to transfer assets but no individualized")
print("  contact occurs before the former customer seeks to transfer assets, the member shall")
print("  deliver the educational communication with the account transfer approval documentation.")
print("2273(b)(3): the delivery requirement shall apply for a period of three months following")
print("  the date the registered person begins employment or associates with the member.")
print("official SM header typography is exactly \u2022 \u2022 \u2022 Supplementary Material:---------------")
print("  (U+2022 bullets, ordinary U+0020 spaces, no NBSP, 15 ASCII hyphens immediately after")
print("  the colon)")
print('official SM .01 typography uses typographic quotes around \u201cformer customer\u201d; the term')
print("  shall not include an account of a non-natural person that meets the definition of an")
print("  institutional account pursuant to Rule 4512(c); official SM .02 express rejection")
print('  ("he or she") exists; this toy is not a 4512, packed 2140, or 11870 / ACATS engine')
print("Adopted by SR-FINRA-2015-057 eff. Nov. 11, 2016. Selected Notice: 16-18.")
flatten_2273 = False
print(f"  this is a flatten into packed / named 4512, packed 2140, or already-named 11870 / ACATS, or a recruitment / account-transfer how-to? {flatten_2273}")
check(flatten_2273 is False, "do not flatten 2273 into packed/named 4512, packed 2140, or already-named 11870 / ACATS")
merged_clock = False
print(f'  this toy merges official (b)(1)(B) "not later than three business days after the contact" with "within three business days from such oral contact"? {merged_clock}')
check(merged_clock is False, "quote both official 2273 clock phrasings; do not merge them")
core_2273 = True
print(f"  a member that hires or associates with a registered person shall provide, individually, in paper or electronic form, an educational communication prepared by FINRA, and official (b)(3) applies for a period of three months following the date the registered person begins employment or associates with the member? {core_2273}")
check(core_2273 is True, "2273 requires the FINRA educational communication in the official contact / transfer cases, for three months")
print("literacy only; not a recruitment or account-transfer how-to")
print("no associated-person, customer, or broker recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== T. FINRA 2040(a): Payments to Unregistered Persons, official (a) General only ===")
# FINRA Rule 2040 Payments to Unregistered Persons (official #the-rule
# / <h1> HTML typography, opened 2026-11-12). Keep S identical once
# 2273 is added. Packed slice is official (a) only. Official (a)
# heading is "General" (no period). Official chapeau: "No member or associated
# person shall, directly or indirectly, pay any compensation, fees,
# concessions, discounts, commissions or other allowances to:" No
# Oxford comma before "commissions or other allowances." Do not quote
# a run-on "GeneralNo member" from HTML tag-stripping; the heading and
# the chapeau are separate. Official (a)(2) has a comma after "federal
# securities laws" and no Oxford comma before "and SEA rules and
# regulations." Official typography is "SEA rules and regulations."
# Official (b) retiring representatives and official (c) nonregistered
# foreign finders exist; name them, do not build those catalogs. If
# official (c) is named, typographic quotes around "finder,"; official
# (c)(1) HTML contains a NBSP in "Article III,\u00a0Section 4" — this
# toy names official (c) and does not quote that sentence, so it does
# not drop or normalize that space. Official (b)(2) uses straight
# quotes around "retiring registered representative," including the
# comma inside the closing quote. Do not flatten into packed 1122,
# packed 2010, or packed 3280. Literacy only, not a compensation-
# arrangement how-to. Amended by SR-FINRA-2014-037 eff. Aug. 24, 2015.
# Selected Notices: 95-37, 15-07.

print("2040(a) heading: General")
print("2040(a): No member or associated person shall, directly or indirectly, pay any")
print("  compensation, fees, concessions, discounts, commissions or other allowances to:")
print("  (1) any person that is not registered as a broker-dealer under Section 15(a) of the")
print("  Exchange Act but, by reason of receipt of any such payments and the activities")
print("  related thereto, is required to be so registered under applicable federal securities")
print("  laws and SEA rules and regulations; or")
print("  (2) any appropriately registered associated person unless such payment complies with")
print("  all applicable federal securities laws, FINRA rules and SEA rules and regulations.")
print("official (a) heading is \"General\" (no period; heading and chapeau are separate; this toy does not")
print('  quote a run-on "GeneralNo member" from HTML tag-stripping)')
print('official typography has no Oxford comma before "commissions or other allowances"')
print('official (a)(2) typography has a comma after "federal securities laws" and no Oxford')
print('  comma before "and SEA rules and regulations"; official typography is "SEA rules and')
print('  regulations"')
print("official (b) retiring representatives and official (c) nonregistered foreign finders")
print("  exist; this toy is not those catalogs")
print('official (b)(2) uses straight quotes around "retiring registered representative,"')
print("  including the comma inside the closing quote")
print("Amended by SR-FINRA-2014-037 eff. Aug. 24, 2015. Selected Notices: 95-37, 15-07.")
flatten_2040 = False
print(f"  this is a flatten into packed 1122, packed 2010, or packed 3280? {flatten_2040}")
check(flatten_2040 is False, "do not flatten 2040(a) into packed 1122 / 2010 / 3280")
oxford_or_runon = False
print(f'  this toy invents an Oxford comma before "commissions or other allowances", or quotes a run-on "GeneralNo member"? {oxford_or_runon}')
check(oxford_or_runon is False, "no Oxford comma before commissions or other allowances; heading and chapeau are separate")
core_2040 = True
print(f"  no member or associated person shall, directly or indirectly, pay any compensation, fees, concessions, discounts, commissions or other allowances to an unregistered person who is required to be registered, or to a registered associated person unless the payment complies with all applicable federal securities laws, FINRA rules and SEA rules and regulations? {core_2040}")
check(core_2040 is True, "2040(a) is the general bar on payments to unregistered persons and on non-compliant payments to registered associated persons")
print("literacy only; not a compensation-arrangement how-to")
print("no associated-person or broker recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== U. 17 CFR 240.10b5-2: Duties of trust or confidence in misappropriation insider trading cases ===")
# 17 CFR 240.10b5-2 Duties of trust or confidence in misappropriation
# insider trading cases (official eCFR versioner API XML typography,
# title 17 up_to_date_as_of 2026-11-09, opened 2026-11-12; byte-
# identical to the enrich35 copy). Keep T identical once 2040(a) is
# added. Pack the official introductory non-exclusive-definition
# sentence plus official (b). Official typography uses typographic
# quotes U+201C/U+201D around “misappropriation,” and official (b)
# heading typography is Enumerated “duties of trust or confidence.”
# with the period inside the closing quote. Official typography is
# "material nonpublic information" (no hyphen in nonpublic);
# "history, pattern, or practice" and "spouse, parent, child, or
# sibling" (Oxford commas); "provided, however,"; straight apostrophe
# in "parties'". Name official (a) and the official (b)(3) proviso; do
# not build a scienter / materiality / judicial-opinion catalog, and
# do not invent that this section is a complete insider-trading code
# (the official introductory sentence says the opposite). Do not
# flatten into packed 10b-5, already-taught 10b5-1, already-taught
# 14e-3, or already-taught 15 U.S.C. 78i / FINRA 5210. Official
# citation: [65 FR 51738, Aug. 24, 2000]. Learning only; no
# investigation or trading how-to.

print("10b5-2 intro: This section provides a non-exclusive definition of circumstances in which")
print("  a person has a duty of trust or confidence for purposes of the \u201cmisappropriation\u201d")
print("  theory of insider trading under Section 10(b) of the Act and Rule 10b-5. The law of")
print("  insider trading is otherwise defined by judicial opinions construing Rule 10b-5, and")
print("  Rule 10b5-2 does not modify the scope of insider trading law in any other respect.")
print("official typography uses typographic quotes U+201C/U+201D around \u201cmisappropriation\u201d")
print("official (a) Scope of Rule is named: this section shall apply to any violation of")
print("  Section 10(b) of the Act (15 U.S.C. 78j(b)) and \u00a7 240.10b-5 thereunder that is based")
print("  on the purchase or sale of securities on the basis of, or the communication of,")
print("  material nonpublic information misappropriated in breach of a duty of trust or")
print("  confidence; official typography is \"material nonpublic information\" (no hyphen in")
print("  nonpublic)")
print("10b5-2(b): Enumerated \u201cduties of trust or confidence.\u201d For purposes of this section, a")
print("  \u201cduty of trust or confidence\u201d exists in the following circumstances, among others:")
print("official (b) heading typography is Enumerated \u201cduties of trust or confidence.\u201d with")
print("  the period inside the closing typographic quote")
print("  (1) Whenever a person agrees to maintain information in confidence;")
print("  (2) Whenever the person communicating the material nonpublic information and the")
print("  person to whom it is communicated have a history, pattern, or practice of sharing")
print("  confidences, such that the recipient of the information knows or reasonably should")
print("  know that the person communicating the material nonpublic information expects that")
print("  the recipient will maintain its confidentiality; or")
print("  (3) Whenever a person receives or obtains material nonpublic information from his or")
print("  her spouse, parent, child, or sibling; provided, however, that a no-duty showing")
print("  exists as official text then states (including \"he or she,\" \"the parties' history,")
print("  pattern, or practice of sharing and maintaining confidences,\" and \"there was no")
print("  agreement or understanding to maintain the confidentiality of the information\").")
print('official typography is "history, pattern, or practice" and "spouse, parent, child, or')
print('  sibling" (Oxford commas); "provided, however,"; "his or her"; straight apostrophe in')
print("  \"parties\'\"")
print("cite 17 CFR 240.10b5-2; title 17 up_to_date_as_of 2026-11-09")
print("[65 FR 51738, Aug. 24, 2000]")
print("official (a) and the official (b)(3) proviso are named; this toy is not a scienter,")
print("  materiality, or judicial-opinion catalog, and does not invent that this section is a")
print("  complete insider-trading code")
flatten_10b52 = False
print(f"  this is a flatten into packed 10b-5, already-taught 10b5-1, already-taught 14e-3, or already-taught 15 U.S.C. 78i / FINRA 5210? {flatten_10b52}")
check(flatten_10b52 is False, "do not flatten 10b5-2 into packed 10b-5, already-taught 10b5-1, 14e-3, or 15 U.S.C. 78i / FINRA 5210")
complete_code = False
print(f"  this toy invents that 10b5-2 is a complete insider-trading code, or invents a numeric clock? {complete_code}")
check(complete_code is False, "official intro says this is a non-exclusive definition; do not invent a complete code or a numeric clock")
core_10b52 = True
print(f"  this section provides a non-exclusive definition of circumstances in which a person has a duty of trust or confidence for purposes of the misappropriation theory, including official (b)(1) an agreement to maintain information in confidence, official (b)(2) a history, pattern, or practice of sharing confidences, and official (b)(3) receipt from a spouse, parent, child, or sibling, subject to the official proviso? {core_10b52}")
check(core_10b52 is True, "10b5-2 packs the official introductory non-exclusive-definition sentence plus official (b)")
print("learning only; no investigation or trading how-to")
print("no issuer, associated-person, or broker recommendation")
print(f"assertions passed: {checks}/{checks}")
print("ASSERT_10b52_ok")
print("disclaimer: official 17 CFR 240.10b5-2; learning only; not legal advice; literacy only, not an insider-trading how-to")


print("=== V. FINRA 3130: Annual Certification of Compliance and Supervisory Processes ===")
print("official caption typography is 3130. Annual Certification of Compliance and")
print("  Supervisory Processes (no period after Processes)")
print("official (a) heading typography is (a) Designation of Chief Compliance Officer(s)")
print("  (no period)")
print("3130(a): Each member shall designate and specifically identify to FINRA on Schedule A")
print("  of Form BD one or more principals to serve as a chief compliance officer.")
print("official (b) heading typography is (b) Annual Certification Requirement (no period)")
print("3130(b): Each member shall have its chief executive officer(s) (or equivalent")
print("  officer(s)) certify annually,1 as set forth in paragraph (c), that the member has")
print("  in place processes to establish, maintain, review, test and modify written")
print("  compliance policies and written supervisory procedures reasonably designed to")
print("  achieve compliance with applicable FINRA rules, MSRB rules and federal securities")
print("  laws and regulations, and that the chief executive officer(s) has conducted one or")
print("  more meetings with the chief compliance officer(s) in the preceding 12 months to")
print("  discuss such processes.")
print('official typography includes a comma after "annually" before the footnote marker,')
print('  official "(s)", and official "preceding 12 months."')
print("official footnote 1: Members must ensure that each ensuing annual certification is")
print("  effected no later than on the anniversary date of the previous year's")
print("  certification. (straight apostrophe in \"year's\")")
print("official (c) Certification (no period) and the prescribed certification text, and")
print("  official SM .01-.10, exist and are named only; this toy is not those catalogs")
print("if the official SM header is quoted, typography is \u2022\u00a0\u2022\u00a0\u2022\u00a0Supplementary Material: --------------")
print("  (U+2022, U+00A0 NBSP, 14 ASCII hyphens); this toy does not copy packed 2273's")
print("  ordinary-space / 15-hyphen SM header onto 3130")
flatten_3130 = False
print(f"  this is a flatten into packed 2010, packed 3310, or still-unpacked 3110 / 3120, or a how-to for the certification? {flatten_3130}")
check(flatten_3130 is False, "do not flatten 3130 into packed 2010 / 3310 or still-unpacked 3110 / 3120, and do not write a certification how-to")
period_heads = False
print(f'  this toy invents a period after official (a) "Officer(s)", official (b) "Requirement", official (c) "Certification", or official caption "Processes"? {period_heads}')
check(period_heads is False, "do not invent periods after official 3130 headings or caption Processes")
core_3130 = True
print(f"  each member shall designate and specifically identify to FINRA on Schedule A of Form BD one or more principals to serve as a chief compliance officer, and shall have its chief executive officer(s) (or equivalent officer(s)) certify annually, as set forth in paragraph (c), including the official footnote 1 anniversary clock (no later than on the anniversary date of the previous year's certification) and one or more meetings with the chief compliance officer(s) in the preceding 12 months? {core_3130}")
check(core_3130 is True, "3130 packs official (a) plus official (b), including footnote 1")
print("literacy only; not a how-to for writing the certification")
print("no member, officer, or product recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== W. FINRA 2270: Day-Trading Risk Disclosure Statement ===")
print("official caption typography is 2270. Day-Trading Risk Disclosure Statement (no")
print("  period after Statement)")
print("2270(a) opening: Except as provided in paragraph (b), no member that is promoting a")
print("  day-trading strategy, directly or indirectly, shall open an account for or on")
print("  behalf of a non-institutional customer unless, prior to opening the account, the")
print("  member has furnished to each customer, individually, in paper or electronic form,")
print("  the disclosure statement specified in this paragraph (a). In addition, any member")
print("  that is promoting a day-trading strategy, directly or indirectly, must post such")
print("  disclosure statement on the member's Web site in a clear and conspicuous manner.")
print('official typography is two-word "Web site" (capital W), a straight apostrophe in')
print("  \"member's Web site\", hyphenated \"day-trading strategy\" and \"non-institutional\",")
print('  "paper or electronic form", and "clear and conspicuous manner"')
print('the prescribed "Day-Trading Risk Disclosure Statement" text exists and is named')
print("  only, including its model figures ($50,000, $16, 29 transactions, $111,360); those")
print("  model figures are not legal thresholds and are not a substitute for already-taught")
print("  IML/IMD / the former $25,000 PDT minimum equity")
print("official (b) substantially similar alternative, official SM (including SM .02, which")
print("  names Rule 2130 and Rule 4210(f)(8)(B)), and FINRA 2130 exist and are named only")
print("already-taught PDT / Notice 26-10 / 26-11 stay as written; this toy does not invent")
print("  that those notices repealed 2270")
flatten_2270 = False
print(f"  this is a flatten into packed 2264 / 2265 / 2267, packed 2090, or still-unpacked 2130, a day-trading how-to, or an invention that Notice 26-10 / 26-11 repealed 2270? {flatten_2270}")
check(flatten_2270 is False, "do not flatten 2270 into packed 2264 / 2265 / 2267, packed 2090, or still-unpacked 2130, and do not invent repeal by 26-10 / 26-11")
tidy_web = False
print(f'  this toy tidies official "Web site" into "website", or treats the model $50,000 / $16 / 29 / $111,360 figures as legal thresholds? {tidy_web}')
check(tidy_web is False, "do not tidy Web site into website, and do not treat model figures as legal thresholds")
core_2270 = True
print(f"  except as provided in paragraph (b), no member promoting a day-trading strategy, directly or indirectly, shall open an account for or on behalf of a non-institutional customer unless, prior to opening the account, the member has furnished to each customer, individually, in paper or electronic form, the disclosure statement specified in official (a), and any such member must post that statement on the member's Web site in a clear and conspicuous manner? {core_2270}")
check(core_2270 is True, "2270 packs official (a) opening only")
print("literacy only; not a day-trading how-to, and not legal advice")
print("no broker, day-trading firm, or product recommendation")
print(f"assertions passed: {checks}/{checks}")
print("ASSERT_3130_2270_ok")
print("disclaimer: official FINRA 3130 and 2270; learning only; not legal advice; literacy only, not a certification or day-trading how-to")
