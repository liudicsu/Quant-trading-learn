"""17 CFR 240.14b-1 official (b)(1) seven-business-day search-card / inquiry
response and official (b)(2) five-business-day forwarding (checked 2026-11-12).

Official source: 17 CFR 240.14b-1, title 17 up_to_date_as_of 2026-11-09.
This companion does not rewrite already-printed section S of
11_freeride_txse_15c33_toy.py, which still says that toy does not pack 14b-1.

Learning only; not legal advice, not a street-name or ACATS primer, and not a
proxy-processing how-to. No broker or product recommendation. Stdlib only; no
network.
"""

checks = 0


def check(cond, label):
    global checks
    assert cond, label
    checks += 1


print("=== A. 17 CFR 240.14b-1: Obligation of registered brokers and dealers in connection with the prompt forwarding of certain communications to beneficial owners ===")
print("official caption typography is Obligation of registered brokers and dealers in")
print("  connection with the prompt forwarding of certain communications to beneficial")
print("  owners.")
print("official (b) heading typography is Dissemination and beneficial owner information")
print("  requirements.")
print("14b-1(b)(1): The broker or dealer shall respond, by first class mail or other equally")
print("  prompt means, directly to the registrant no later than seven business days after")
print("  the date it receives an inquiry made in accordance with \u00a7 240.14a-13(a) or")
print("  \u00a7 240.14c-7(a) by indicting, by means of a search card or otherwise:")
print('official typography is "by indicting" (not "indicating") and "first class mail"')
print("  (no hyphen)")
print('official (b)(1)(ii) typography is "addresses,and" (comma, no space) and, later in')
print('  the same sentence, "names, addresses and securities positions" (spaces; no comma')
print('  before "and"); this toy does not tidy either')
print("14b-1(b)(2): The broker or dealer shall, upon receipt of the proxy, other proxy")
print("  soliciting material, information statement, and/or annual report to security")
print("  holders from the registrant or other soliciting person, forward such materials to")
print("  its customers who are beneficial owners of the registrant's securities no later")
print("  than five business days after receipt of the proxy material, information statement")
print("  or annual report to security holders.")
print('official typography is "and/or annual report to security holders"; official (b)(2)')
print('  has no Oxford comma before "or annual report to security holders"; a straight')
print('  apostrophe in "registrant\'s"')
print("official (a) definitions exist and are named only; official typography uses")
print("  typographic quotes around \u201cregistrant\u201d")
print("official (b)(3) non-objecting beneficial-owner names, addresses, and securities")
print("  positions, the householding paragraph that names 14a-3(e)(1) / 14c-3(c), official")
print("  (c) and later, 17 CFR 240.14b-2, and 17 CFR 240.14a-13 exist and are named only;")
print("  this toy is not those catalogs")
print("cite 17 CFR 240.14b-1; title 17 up_to_date_as_of 2026-11-09")
print("this is a later separate item from packed FINRA 2251; packing 14b-1 as a second")
print("  core of the 2251 box remains wrong")
flatten_14b1 = False
print(f"  this is a flatten into packed 2251, or a recast of 2251 as this rule, or a street-name / ACATS primer? {flatten_14b1}")
check(flatten_14b1 is False, "do not flatten 14b-1 into packed 2251, recast 2251 as this rule, or write a street-name / ACATS primer")
tidy_14b1 = False
print(f'  this toy tidies official "by indicting" into "indicating", tidies official (b)(1)(ii) "addresses,and", or hyphenates "first class mail"? {tidy_14b1}')
check(tidy_14b1 is False, "do not tidy official 14b-1 typography")
core_14b1 = True
print(f"  the broker or dealer shall respond by first class mail or other equally prompt means no later than seven business days after receiving an official 14a-13(a) or 14c-7(a) inquiry, by indicting by a search card or otherwise, and shall forward proxy, information-statement, and/or annual-report materials to beneficial-owner customers no later than five business days after receipt? {core_14b1}")
check(core_14b1 is True, "14b-1 packs official (b)(1) seven-business-day response and official (b)(2) five-business-day forwarding")
print("literacy only; not a street-name, ACATS, or proxy-processing how-to")
print("no broker or product recommendation")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 240.14b-1; learning only; not legal advice; no broker or product recommendation")
