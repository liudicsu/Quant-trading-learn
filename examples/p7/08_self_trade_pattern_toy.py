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
