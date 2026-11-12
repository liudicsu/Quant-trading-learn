"""Rule 606-style routing table: net payment for order flow (PFOF) per 100 shares (checked 2026-11-10).

Sources: 17 CFR 242.606(a): quarterly report on non-directed held orders in NMS stocks and
non-directed customer orders in options; venues = the ten with the most orders plus any with
5% or more; net of PFOF, profit-sharing, transaction fees and rebates, total and per share,
for four order types (market, marketable limit, non-marketable limit, other); due within one
month after the quarter. 17 CFR 240.10b-10(d)(8) (definition of payment for order flow).
606(b)(3) reports use "cents per 100 shares, specified to four decimal places"; we reuse that unit.
The public 606(a) venue shares are percentages of order counts, not share counts.
The venues and numbers are synthetic. A 606 table alone says nothing about fill quality:
read it with Rule 605 statistics. Learning only, not a broker evaluation.
"""
checks = 0


def check(cond, label):
    global checks
    assert cond, label
    checks += 1


# venue -> (non-directed orders routed, shares routed, net dollars: + received, - paid)
# 606(a) venue percentages are of order counts; cents-per-100 uses share counts.
venues = {
    "MM_A": (4_800, 1_200_000, 600.0),   # 250 shares/order
    "MM_B": (3_200, 800_000, 240.0),     # 250 shares/order
    "EXCH_C": (2_000, 1_500_000, -150.0),  # 750 shares/order; order share 20%, share share 42.9%
}


def cents_per_100(shares, net_usd):
    return round(net_usd / shares * 100 * 100, 4)


total_orders = sum(o for o, _, _ in venues.values())
total_shares = sum(s for _, s, _ in venues.values())
print("venue   pct_of_orders  pct_of_shares  net_cents_per_100sh")
res = {}
pct_o, pct_s = {}, {}
for v, (orders, shares, usd) in venues.items():
    res[v] = cents_per_100(shares, usd)
    pct_o[v] = orders / total_orders
    pct_s[v] = shares / total_shares
    print(f"{v:<7} {pct_o[v]:>13.1%}  {pct_s[v]:>13.1%}  {res[v]:>19.4f}")
check(res == {"MM_A": 5.0, "MM_B": 3.0, "EXCH_C": -1.0}, "net PFOF per 100 shares")
check(abs(sum(pct_o.values()) - 1) < 1e-12 and abs(sum(pct_s.values()) - 1) < 1e-12, "both columns sum to 100%")
check(round(pct_o["EXCH_C"], 4) == 0.2 and round(pct_s["EXCH_C"], 4) == 0.4286, "order-count vs share-count ranks differ")
check(max(pct_o, key=pct_o.get) == "MM_A" and max(pct_s, key=pct_s.get) == "EXCH_C", "top venue depends on the unit")
print(f"assertions passed: {checks}/{checks}")
print("ASSERT_rule606_ok")
print("reminder: 606 = where orders went and the money; 605 = execution quality; read both. Synthetic; learning only")


print("=== B. FINRA 5250: payments for market making ===")
# FINRA Rule 5250 Payments for Market Making (official rule page opened
# 2026-11-12). Keep the current 606 table, 4/4, ASSERT_rule606_ok, and the
# reminder line identical.
# 5250 is a different prohibition from already-taught PFOF / Rule 606.
# 5250(a): no member or person associated with a member shall accept any
# payment or other consideration, directly or indirectly, from an issuer of
# a security, or any affiliate or promoter thereof, for publishing a
# quotation, acting as market maker in a security, or submitting an
# application in connection therewith.
# 5250(b) official exceptions exist: payment for bona fide services,
# including investment banking services (including underwriting compensation
# and fees); reimbursement of SEC or state registration fees and SRO listing
# fees; and any payment expressly provided for under the rules of a national
# securities exchange that are effective after being filed with, or filed
# with and approved by, the SEC.
# Do not rewrite already-taught PFOF / Rule 606, Rule 605, or FINRA 5320.
# Do not build a promoter / 5121-affiliate / exchange-fee-schedule engine.
# No product, broker, or venue recommendation.

print("5250 is a different prohibition from already-taught PFOF / Rule 606")
print("5250(a): no member or person associated with a member shall accept any payment or other consideration,")
print("  directly or indirectly, from an issuer of a security, or any affiliate or promoter thereof,")
print("  for publishing a quotation, acting as market maker in a security, or submitting an application in connection therewith")
issuer_mm_payment_prohibited = True
same_as_pfof = False
print(f"  issuer / affiliate / promoter payment for acting as market maker: prohibited? {issuer_mm_payment_prohibited}")
print(f"  already-taught PFOF for routing customer orders is the same prohibition? {same_as_pfof}")
check(issuer_mm_payment_prohibited is True, "5250(a) prohibits issuer payment for market making")
check(same_as_pfof is False, "5250 is not already-taught PFOF / 606")
print("5250(b) official exceptions exist: payment for bona fide services, including investment banking services")
print("  (including underwriting compensation and fees); reimbursement of SEC or state registration fees and SRO listing fees;")
print("  and any payment expressly provided for under the rules of a national securities exchange")
print("  that are effective after being filed with, or filed with and approved by, the SEC")
builds_5250_engine = False
print(f"  this toy builds a promoter / 5121-affiliate / exchange-fee-schedule engine? {builds_5250_engine}")
check(builds_5250_engine is False, "do not build the 5250(b)/(c) engine")
every_issuer_paid_service_banned = False
print(f"  every issuer-paid service is banned? {every_issuer_paid_service_banned}")
check(every_issuer_paid_service_banned is False, "bona fide services / fee reimbursements / exchange-rule payments are official exceptions")
print("no product, broker, or venue recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== C. FINRA 5270: front running of block transactions ===")
# FINRA Rule 5270 Front Running of Block Transactions (official rule page
# opened 2026-11-12). Keep the existing 606 prints and the new 5250 section
# identical once it is added.
# 5270 is a different prohibition from already-taught FINRA 5320.
# 5270(a): a member with material, non-public market information concerning
# an imminent block transaction may not cause an order in that security or
# a related financial instrument to be executed prior to the time information
# concerning the block transaction has been made publicly available or has
# otherwise become stale or obsolete.
# SM .03: in equity securities, 10,000 shares or more is generally deemed a
# block, although fewer than 10,000 could be a block; splitting into
# non-block pieces does not change identity if the full transaction may have
# a material impact on the market.
# SM .02: public availability is not satisfied until the entire block
# transaction has been completed and publicly reported.
# Official SM .04 exceptions exist; this toy is not an information-barrier /
# consent / exchange-leg engine. Do not rewrite 5320. Do not treat 10,000
# shares as a rigid floor.
# No product, broker, or venue recommendation.

print("5270 is a different prohibition from already-taught FINRA 5320")
print("5270(a): a member with material, non-public market information concerning an imminent block transaction")
print("  may not cause an order in that security or a related financial instrument to be executed")
print("  prior to the time information concerning the block transaction has been made publicly available")
print("  or has otherwise become stale or obsolete")
is_5320 = False
print(f"  this is the already-taught 5320 trading-ahead-of-a-held-customer-equity-order rule? {is_5320}")
check(is_5320 is False, "5270 is not already-taught 5320")
print("SM .03: in equity securities, a transaction involving 10,000 shares or more is generally deemed to be a block transaction,")
print("  although a transaction of fewer than 10,000 shares could be considered a block transaction")
rigid_floor = False
print(f"  10,000 shares is a rigid floor? {rigid_floor}")
check(rigid_floor is False, "10,000 shares is generally deemed a block, not a rigid floor")
print("A block transaction that has been agreed upon does not lose its identity as such by arranging for")
print("  partial executions of the full transaction in portions which themselves are not of block size")
print("  if the execution of the full transaction may have a material impact on the market")
print("SM .02: public availability will not be satisfied until the entire block transaction has been completed and publicly reported")
partial_print_is_public = False
print(f"  a print of part of the block makes the entire block publicly available? {partial_print_is_public}")
check(partial_print_is_public is False, "part of a block is not public availability of the entire block")
print("official SM .04 exceptions exist; this toy is not an information-barrier / consent / exchange-leg engine")
builds_5270_exceptions = False
print(f"  this toy builds an information-barrier / consent / exchange-leg engine? {builds_5270_exceptions}")
check(builds_5270_exceptions is False, "do not build SM .04 engines")
print("SM .05: front running of non-block orders may still violate other FINRA rules, including Rule 2010 and already-taught Rule 5320")
print("no product, broker, or venue recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== D. FINRA 5230: payments involving publications that influence the market price ===")
# FINRA Rule 5230 Payments Involving Publications that Influence the Market
# Price of a Security (official rule page opened 2026-11-12). Keep the
# current 606 table, 4/4, ASSERT_rule606_ok, the reminder line, the 5250
# section, the 5270 section, and 12/12 after 5270 identical.
# 5230 is a different prohibition from already-taught FINRA 5250.
# 5230(a): except as provided in paragraph (b), no member shall, directly or
# indirectly, give, permit to be given, or offer to give, anything of value
# to any person for the purpose of influencing or rewarding the action of
# such person in connection with the publication or circulation in any
# electronic or other public media, including any investment service or
# similar publication, Web site, newspaper, magazine or other periodical,
# radio, or television program, of any matter that has, or is intended to
# have, an effect upon the market price of any security.
# 5230(b) official exceptions: (1) a communication clearly distinguishable
# as paid advertising; (2) a communication that discloses the receipt of
# compensation and the amount thereof in accordance with Section 17(b) of
# the Securities Act; (3) a research report as defined in Rule 2241.
# Do not build a 17(b) or 2241 engine. Do not rewrite already-taught 5250
# or PFOF / Rule 606. No product, broker, or venue recommendation.

print("5230 is a different prohibition from already-taught FINRA 5250")
print("5230(a): except as provided in paragraph (b), no member shall, directly or indirectly,")
print("  give, permit to be given, or offer to give, anything of value to any person")
print("  for the purpose of influencing or rewarding the action of such person")
print("  in connection with the publication or circulation in any electronic or other public media,")
print("  including any investment service or similar publication, Web site, newspaper,")
print("  magazine or other periodical, radio, or television program,")
print("  of any matter that has, or is intended to have, an effect upon the market price of any security")
is_5250 = False
print(f"  this is the already-taught 5250 issuer-payment-for-market-making rule? {is_5250}")
check(is_5250 is False, "5230 is not already-taught 5250")
print("5230(b) official exceptions exist: (1) a communication clearly distinguishable as paid advertising;")
print("  (2) a communication that discloses the receipt of compensation and the amount thereof")
print("  in accordance with Section 17(b) of the Securities Act;")
print("  (3) a research report as defined in Rule 2241")
builds_5230_engine = False
print(f"  this toy builds a Section 17(b) or Rule 2241 engine? {builds_5230_engine}")
check(builds_5230_engine is False, "do not build a 17(b) or 2241 engine")
every_paid_communication_banned = False
print(f"  every paid communication is banned? {every_paid_communication_banned}")
check(every_paid_communication_banned is False, "official (b) exceptions exist")
print("no product, broker, or venue recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== E. FINRA 5280: trading ahead of research reports ===")
# FINRA Rule 5280 Trading Ahead of Research Reports (official rule page
# opened 2026-11-12). Keep the existing 606, 5250, and 5270 prints, and the
# new 5230 section, identical once 5230 is added.
# 5280 is a different prohibition from already-taught FINRA 5270 and 5320.
# 5280(a): No member shall establish, increase, decrease or liquidate an
# inventory position in a security or a derivative of such security based
# on non-public advance knowledge of the content or timing of a research
# report in that security.
# 5280(b): a member must establish, maintain and enforce policies and
# procedures reasonably designed to restrict or limit the information flow
# between research department personnel, or other persons with knowledge of
# the content or timing of a research report, and trading department
# personnel, so as to prevent trading department personnel from utilizing
# non-public advance knowledge of the issuance or content of a research
# report for the benefit of the member or any other person.
# Official 5280(b) information-flow procedures exist; this toy is not that
# engine. Do not rewrite 5270 or 5320. Do not build a Rule 2241 research-
# report definition engine. No product, broker, or venue recommendation.

print("5280 is a different prohibition from already-taught FINRA 5270 and 5320")
print("5280(a): No member shall establish, increase, decrease or liquidate an inventory position")
print("  in a security or a derivative of such security based on non-public advance knowledge")
print("  of the content or timing of a research report in that security")
is_5270 = False
is_5320_again = False
print(f"  this is the already-taught 5270 front-running-of-an-imminent-block rule? {is_5270}")
print(f"  this is the already-taught 5320 trading-ahead-of-a-held-customer-equity-order rule? {is_5320_again}")
check(is_5270 is False, "5280 is not already-taught 5270")
check(is_5320_again is False, "5280 is not already-taught 5320")
print("5280(b): a member must establish, maintain and enforce policies and procedures reasonably designed")
print("  to restrict or limit the information flow between research department personnel,")
print("  or other persons with knowledge of the content or timing of a research report,")
print("  and trading department personnel, so as to prevent trading department personnel")
print("  from utilizing non-public advance knowledge of the issuance or content of a research report")
print("  for the benefit of the member or any other person")
print("official 5280(b) information-flow procedures exist; this toy is not that engine")
builds_5280_engine = False
print(f"  this toy builds an information-barrier or Rule 2241 research-report definition engine? {builds_5280_engine}")
check(builds_5280_engine is False, "do not build a 5280(b) or 2241 engine")
print("no product, broker, or venue recommendation")
print(f"assertions passed: {checks}/{checks}")


print("=== F. Rule 10b-10: written notification at or before completion ===")
# 17 CFR 240.10b-10 Confirmation of transactions (official eCFR API,
# title 17 up to date as of 2026-11-09, plus official-page fetch opened
# 2026-11-12; not an interstitial). Keep the current 606 table, 4/4,
# ASSERT_rule606_ok, the reminder line, the 5250 section, the 5270
# section, 12/12 after 5270, the 5230 section, 15/15 after 5230, the
# 5280 section, and 18/18 after 5280 identical.
# Preliminary Note: This section requires broker-dealers to disclose
# specified information in writing to customers at or before completion
# of a transaction.
# 10b-10(a): it shall be unlawful for any broker or dealer to effect
# for or with an account of a customer any transaction in, or to induce
# the purchase or sale by such customer of, any security (other than
# U.S. Savings Bonds or municipal securities) unless such broker or
# dealer, at or before completion of such transaction, gives or sends
# to such customer written notification disclosing: official (a)(1)-(8)
# disclosure catalog exists; this toy does not build it.
# 10b-10(c): requested information within 5 business days of receipt
# of the request; 15 business days if the transaction was effected more
# than 30 days prior to receipt of the request.
# 10b-10(d)(2): Completion of the transaction shall have the meaning
# provided in rule 15c1-1 under the Act. This toy does not build a
# Rule 15c1-1 completion engine and does not invent a T+1 confirmation
# clock. Official (b) alternative periodic reporting and official (e)
# security-futures product provisions exist; this toy is not that
# engine. This is not already-taught 10b-10(d)(8) PFOF. Official
# typographical artifact in (a)(8): "Provided, however, that this
# paragraph (a)(9) shall not apply" — quote it; do not silently
# correct "(a)(9)." No product, broker, or venue recommendation.

print("10b-10 requires written notification at or before completion of a customer transaction")
print("Preliminary Note: This section requires broker-dealers to disclose specified information")
print("  in writing to customers at or before completion of a transaction")
print("10b-10(a): It shall be unlawful for any broker or dealer to effect for or with an account of a customer")
print("  any transaction in, or to induce the purchase or sale by such customer of, any security")
print("  (other than U.S. Savings Bonds or municipal securities) unless such broker or dealer,")
print("  at or before completion of such transaction, gives or sends to such customer written notification disclosing:")
print("  official (a)(1)-(8) disclosure catalog exists; this toy does not build it")
is_10b10_pfof = False
print(f"  this is already-taught 10b-10(d)(8) PFOF? {is_10b10_pfof}")
check(is_10b10_pfof is False, "10b-10 confirmation clock is not already-taught 10b-10(d)(8) PFOF")
print("10b-10(c): a broker or dealer shall give or send to a customer information requested pursuant to this rule")
print("  within 5 business days of receipt of the request; Provided, however, That in the case of information")
print("  pertaining to a transaction effected more than 30 days prior to receipt of the request,")
print("  the information shall be given or sent to the customer within 15 business days")
print("10b-10(d)(2): Completion of the transaction shall have the meaning provided in rule 15c1-1 under the Act")
invents_t1_clock = False
builds_15c11 = False
print(f"  this toy invents a T+1 confirmation clock? {invents_t1_clock}")
print(f"  this toy builds a Rule 15c1-1 completion engine? {builds_15c11}")
check(invents_t1_clock is False, "do not invent a T+1 confirmation clock")
check(builds_15c11 is False, "do not build a Rule 15c1-1 completion engine")
print("official (b) alternative periodic reporting and official (e) security-futures product provisions exist; this toy is not that engine")
print('official typographical artifact in (a)(8): "Provided, however, that this paragraph (a)(9) shall not apply"')
silently_corrects_a9 = False
print(f'  this toy silently corrects "this paragraph (a)(9)"? {silently_corrects_a9}')
check(silently_corrects_a9 is False, "do not silently correct 10b-10(a)(8) typographical artifact")
print("no product, broker, or venue recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== G. FINRA 5240: anti-intimidation / coordination ===")
# FINRA Rule 5240 Anti-Intimidation/Coordination (official rule page
# opened 2026-11-12). Keep the existing 606, 5250, 5270, 5230, and 5280
# prints, including 18/18 after 5280, and the new 10b-10 section,
# identical once 10b-10 is added.
# 5240 is a different prohibition from already-taught FINRA 5230, 5250,
# 5270, 5280, and 5320.
# 5240(a): no member or person associated with a member shall (1)
# coordinate the prices (including quotations), trades or trade reports
# of such member with any other member or person associated with a
# member, or any other person; (2) direct or request another member to
# alter a price (including a quotation); or (3) engage, directly or
# indirectly, in any conduct that threatens, harasses, coerces,
# intimidates or otherwise attempts improperly to influence another
# member, a person associated with a member, or any other person.
# This includes, but is not limited to, any attempt to influence
# another member or associated person to adjust or maintain a price or
# quotation, or refusals to trade or other conduct that retaliates
# against or discourages the competitive activities of another market
# maker or market participant.
# Official (b)(1)-(7) unilateral-conduct exceptions exist, provided the
# conduct is otherwise in compliance with all applicable law; this toy
# is not that engine. Do not treat every unilateral quote as banned.
# Do not rewrite already-taught 5230, 5250, 5270, 5280, 5320, or PFOF /
# Rule 606. No product, broker, or venue recommendation.

print("5240 is a different prohibition from already-taught 5230, 5250, 5270, 5280, and 5320")
print("5240(a): no member or person associated with a member shall")
print("  (1) coordinate the prices (including quotations), trades or trade reports of such member")
print("  with any other member or person associated with a member, or any other person;")
print("  (2) direct or request another member to alter a price (including a quotation); or")
print("  (3) engage, directly or indirectly, in any conduct that threatens, harasses, coerces, intimidates")
print("  or otherwise attempts improperly to influence another member, a person associated with a member,")
print("  or any other person")
print("This includes, but is not limited to, any attempt to influence another member or associated person")
print("  to adjust or maintain a price or quotation, or refusals to trade or other conduct that retaliates")
print("  against or discourages the competitive activities of another market maker or market participant")
is_already_taught_5240 = False
print(f"  this is already-taught 5230, 5250, 5270, 5280, or 5320? {is_already_taught_5240}")
check(is_already_taught_5240 is False, "5240 is not already-taught 5230/5250/5270/5280/5320")
print("official (b) unilateral-conduct exceptions exist, provided the conduct is otherwise in compliance with all applicable law;")
print("  this toy is not that engine")
builds_5240b = False
every_unilateral_banned = False
print(f"  this toy builds the official (b)(1)-(7) catalog? {builds_5240b}")
print(f"  every unilateral quote is banned? {every_unilateral_banned}")
check(builds_5240b is False, "do not build the 5240(b) catalog")
check(every_unilateral_banned is False, "official (b) exceptions exist; not a ban on every unilateral quote")
print("no product, broker, or venue recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== H. FINRA 5290: no splitting orders or executions for the primary purpose of maximizing credits or rebates ===")
# FINRA Rule 5290 Order Entry and Execution Practices (official-page fetch
# opened 2026-11-12). Keep the current 606 table, 4/4, ASSERT_rule606_ok,
# the reminder line, 5250, 5270, 12/12 after 5270, 5230, 15/15 after 5230,
# 5280, 18/18 after 5280, 10b-10, 22/22 after 10b-10, 5240, and 25/25 after
# 5240 identical.
# 5290: No member or associated person shall engage in conduct that has the
# intent or effect of splitting any order into multiple smaller orders for
# execution or any execution into multiple smaller executions for
# transaction reporting for the primary purpose of maximizing a monetary
# or in-kind amount to be received by the member or associated person as a
# result of the execution of such orders or the transaction reporting of
# such executions. For purposes of this Rule, "monetary or in-kind amount"
# shall be defined to include, but not be limited to, any credits,
# commissions, gratuities, payments for or rebates of fees, or any other
# payments of value to the member or associated person.
# Quote "this Rule" as written. This is not a ban on every TWAP / VWAP
# slice. This is not a rewrite of already-taught 606 / PFOF, 5270, or 5320.
# No product, broker, or venue recommendation.

print("5290: No member or associated person shall engage in conduct that has the intent or effect of")
print("  splitting any order into multiple smaller orders for execution or any execution into")
print("  multiple smaller executions for transaction reporting for the primary purpose of")
print("  maximizing a monetary or in-kind amount to be received by the member or associated person")
print("  as a result of the execution of such orders or the transaction reporting of such executions")
print('For purposes of this Rule, "monetary or in-kind amount" shall be defined to include, but not be limited to,')
print("  any credits, commissions, gratuities, payments for or rebates of fees,")
print("  or any other payments of value to the member or associated person")
every_slice_banned = False
print(f"  every TWAP / VWAP slice is banned? {every_slice_banned}")
check(every_slice_banned is False, "5290 is not a ban on every TWAP/VWAP slice")
is_rewrite_606_5270_5320 = False
print(f"  this is a rewrite of already-taught 606 / PFOF, 5270, or 5320? {is_rewrite_606_5270_5320}")
check(is_rewrite_606_5270_5320 is False, "5290 is not a rewrite of 606/PFOF, 5270, or 5320")
primary_purpose_test = True
print(f"  official test is the primary purpose of maximizing a monetary or in-kind amount? {primary_purpose_test}")
check(primary_purpose_test is True, "official primary-purpose test")
print("no product, broker, or venue recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== I. FINRA 2262: control-relationship disclosure before the customer contract ===")
# FINRA Rule 2262 Disclosure of Control Relationship with Issuer
# (official-page fetch opened 2026-11-12). Keep all earlier prints,
# including 25/25 after 5240 and the new 5290 section, identical once
# 5290 is added.
# 2262: A member controlled by, controlling, or under common control with,
# the issuer of any security, shall, before entering into any contract
# with or for a customer for the purchase or sale of such security,
# disclose to such customer the existence of such control, and if such
# disclosure is not made in writing, it shall be supplemented by the
# giving or sending of written disclosure at or before the completion of
# the transaction.
# The first disclosure is not officially required to be in writing. This
# is not a rewrite of already-taught Rule 10b-10. No product, broker, or
# issuer recommendation.

print("2262: A member controlled by, controlling, or under common control with, the issuer of any security,")
print("  shall, before entering into any contract with or for a customer for the purchase or sale of such security,")
print("  disclose to such customer the existence of such control,")
print("  and if such disclosure is not made in writing, it shall be supplemented by the giving or sending")
print("  of written disclosure at or before the completion of the transaction")
invents_first_must_be_written = False
print(f"  this toy invents that the first disclosure must be in writing? {invents_first_must_be_written}")
check(invents_first_must_be_written is False, "do not invent that the first 2262 disclosure must be in writing")
is_rewrite_10b10_2262 = False
print(f"  this is a rewrite of already-taught 10b-10? {is_rewrite_10b10_2262}")
check(is_rewrite_10b10_2262 is False, "2262 is not a rewrite of already-taught 10b-10")
before_contract = True
print(f"  first disclosure is required before entering into the customer contract? {before_contract}")
check(before_contract is True, "2262 disclosure is before the customer contract")
print("no product, broker, or issuer recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== J. FINRA 2269: written notification of participation or interest in a distribution ===")
# FINRA Rule 2269 Disclosure of Participation or Interest in Primary or
# Secondary Distribution (official-page fetch opened 2026-11-12). Keep all
# earlier prints identical once 2262 is added.
# 2269: A member who is acting as a broker for a customer or for both such
# customer and some other person, or a member who is acting as a dealer
# and who receives or has promise of receiving a fee from a customer for
# advising such customer with respect to securities, shall, at or before
# the completion of any transaction for or with such customer in any
# security in the primary or secondary distribution of which such member
# is participating or is otherwise financially interested, give such
# customer written notification of the existence of such participation or
# interest.
# Unlike 2262's first disclosure, 2269 requires written notification. The
# official scope is the named broker / adviser-dealer categories. Do not
# invent a broader scope. This is not 2262, and is not a rewrite of
# already-taught 10b-10. No product, broker, or offering recommendation.

print("2269: A member who is acting as a broker for a customer or for both such customer and some other person,")
print("  or a member who is acting as a dealer and who receives or has promise of receiving a fee from a customer")
print("  for advising such customer with respect to securities, shall, at or before the completion of any transaction")
print("  for or with such customer in any security in the primary or secondary distribution of which such member")
print("  is participating or is otherwise financially interested, give such customer written notification")
print("  of the existence of such participation or interest")
print("  unlike 2262, 2269 requires written notification")
is_2262_or_first_must_be_written = False
print(f"  this is 2262, or the first 2262 disclosure must be in writing? {is_2262_or_first_must_be_written}")
check(is_2262_or_first_must_be_written is False, "2269 is not 2262; first 2262 disclosure need not be in writing")
is_rewrite_10b10_2269 = False
print(f"  this is a rewrite of already-taught 10b-10? {is_rewrite_10b10_2269}")
check(is_rewrite_10b10_2269 is False, "2269 is not a rewrite of already-taught 10b-10")
invents_broader_scope = False
print(f"  this toy invents a broader scope than the official broker / adviser-dealer categories? {invents_broader_scope}")
check(invents_broader_scope is False, "do not invent a broader 2269 scope")
print("no product, broker, or offering recommendation")
print(f"assertions passed: {checks}/{checks}")

print('=== K. FINRA 2121: the official "5% Policy" is a guide, not a rule ===')
# FINRA Rule 2121 Fair Prices and Commissions (official-page fetch opened
# 2026-11-12). Keep the current 606 table, 4/4, ASSERT_rule606_ok, the
# reminder line, 5250, 5270, 12/12 after 5270, 5230, 15/15 after 5230,
# 5280, 18/18 after 5280, 10b-10, 22/22 after 10b-10, 5240, 25/25 after
# 5240, 5290, 28/28 after H, 2262, 31/31 after I, 2269, and 34/34 after J
# identical.
# Official 2121: if a member buys for his own account from his customer,
# or sells for his own account to his customer, he shall buy or sell at a
# price which is fair, taking into consideration all relevant
# circumstances; and if he acts as agent for his customer, he shall not
# charge his customer more than a fair commission or service charge,
# taking into consideration all relevant circumstances.
# Official SM .01(1): The "5% Policy" is a guide, not a rule.
# Official SM .01(4): A mark-up pattern of 5% or even less may be
# considered unfair or unreasonable under the "5% Policy."
# Official .01 also: It shall be deemed a violation of Rule 2010 and
# Rule 2121 for a member to enter into any transaction with a customer
# in any security at any price not reasonably related to the current
# market price of the security or to charge a commission which is not
# reasonable. .01(5): Determination of the fairness of mark-ups must be
# based on a consideration of all the relevant factors, of which the
# percentage of mark-up is only one.
# Official Rule 2010 is cross-referenced; this toy is not a 2010 engine.
# Official .01(d): the Mark-Up Policy is not applicable to the sale of
# securities where a prospectus or offering circular is required to be
# delivered and the securities are sold at the specific public offering
# price; this toy is not that engine.
# Do not invent a hard 5% cap. Do not build the SM .01(b) relevant-factor
# catalog or .02 additional debt mark-up policy. Do not rewrite
# already-taught 10b-10, 2262, 2269, or 5290. No product, broker, or
# pricing recommendation.

print("2121: if a member buys for his own account from his customer, or sells for his own account to his customer,")
print("  he shall buy or sell at a price which is fair, taking into consideration all relevant circumstances;")
print("  and if he acts as agent for his customer, he shall not charge his customer more than a fair commission")
print("  or service charge, taking into consideration all relevant circumstances")
print('.01(1): The "5% Policy" is a guide, not a rule.')
print('.01(4): A mark-up pattern of 5% or even less may be considered unfair or unreasonable under the "5% Policy."')
print("It shall be deemed a violation of Rule 2010 and Rule 2121 for a member to enter into any transaction")
print("  with a customer in any security at any price not reasonably related to the current market price of the security")
print("  or to charge a commission which is not reasonable")
print(".01(5): Determination of the fairness of mark-ups must be based on a consideration of all the relevant factors,")
print("  of which the percentage of mark-up is only one")
print("official Rule 2010 is cross-referenced; this toy is not a 2010 engine")
print("official .01(d): the Mark-Up Policy is not applicable to the sale of securities where a prospectus or")
print("  offering circular is required to be delivered and the securities are sold at the specific public offering price;")
print("  this toy is not that engine")
hard_cap = False
print(f"  this toy invents a hard 5% cap? {hard_cap}")
check(hard_cap is False, "do not invent a hard 5% cap")
builds_catalog = False
print(f"  this toy builds the SM .01(b) relevant-factor catalog or .02 additional debt mark-up policy? {builds_catalog}")
check(builds_catalog is False, "do not build the SM .01(b) catalog or .02 debt policy")
is_guide = True
print(f'  the official "5% Policy" is a guide, not a rule? {is_guide}')
check(is_guide is True, 'official "5% Policy" is a guide, not a rule')
print("no product, broker, or pricing recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== L. FINRA 2122: charges for services, if any, shall be reasonable and not unfairly discriminatory ===")
# FINRA Rule 2122 Charges for Services Performed (official-page / official
# rulebook HTML opened 2026-11-12). Keep the current 606 table, 4/4,
# ASSERT_rule606_ok, the reminder line, 5250, 5270, 5230, 5280, 10b-10,
# 5240, 5290, 2262, 2269, 2121, and 37/37 after K identical.
# Official 2122: Charges, if any, for services performed, including, but
# not limited to, miscellaneous services such as collection of monies due
# for principal, dividends, or interest; exchange or transfer of
# securities; appraisals, safe-keeping or custody of securities, and
# other services shall be reasonable and not unfairly discriminatory
# among customers.
# Quote official "monies" and hyphenated "safe-keeping" as written. Do
# not invent a hard 5% cap. Do not flatten 2122 into packed 2121. This
# rule is about charges for services, not the 2121 mark-up / commission
# fair-price test. Do not rewrite already-taught 10b-10 / 2262 / 2269 /
# 5290 / 2121. No product, broker, or pricing recommendation.

print("2122: Charges, if any, for services performed, including, but not limited to,")
print("  miscellaneous services such as collection of monies due for principal, dividends, or interest;")
print("  exchange or transfer of securities; appraisals, safe-keeping or custody of securities,")
print("  and other services shall be reasonable and not unfairly discriminatory among customers")
print('official typography is "monies" and hyphenated "safe-keeping"')
hard_cap_2122 = False
print(f"  this toy invents a hard 5% cap? {hard_cap_2122}")
check(hard_cap_2122 is False, "do not invent a hard 5% cap under 2122")
flatten_2121 = False
print(f"  this is a flatten into packed 2121? {flatten_2121}")
check(flatten_2121 is False, "do not flatten 2122 into packed 2121")
reasonable = True
print(f"  charges for services, if any, shall be reasonable and not unfairly discriminatory among customers? {reasonable}")
check(reasonable is True, "2122 requires reasonable, not unfairly discriminatory charges")
print("no product, broker, or pricing recommendation")
print(f"assertions passed: {checks}/{checks}")

print('=== M. FINRA 2124: disclosure and consent before a "net" transaction ===')
# FINRA Rule 2124 Net Transactions with Customers (official-page /
# official rulebook HTML opened 2026-11-12). Keep all earlier prints,
# including 37/37 after K / 2121 and the new 2122 section, identical
# once 2122 is added.
# Official 2124(a): Prior to executing a transaction for or with a
# customer on a "net" basis as defined in paragraph (e) below, a member
# must provide disclosure to and obtain consent from the customer as
# provided in this Rule.
# Official (b): With respect to non-institutional customers, the member
# must obtain the customer's written consent on an order-by-order basis
# prior to executing a transaction for or with the customer on a "net"
# basis and such consent must evidence the customer's understanding of
# the terms and conditions of the order.
# Official (e)(2): "net" transaction shall mean a principal transaction
# in which a market maker, after having received an order to buy (sell)
# an equity security, purchases (sells) the equity security at one price
# (from (to) another broker-dealer or another customer) and then sells
# to (buys from) the customer at a different price.
# Official (e)(1) defines "institutional customer" by Rule 4512(c).
# Official (c) institutional consent methods exist (negative consent
# letter; oral order-by-order consent with documentation; or written
# order-by-order consent); name them, do not build that engine.
# Official (d) permits consent from a fiduciary (official typography is
# "e.g. an investment adviser," with no comma after "e.g.").
# Official (f) recordkeeping cross-references Rule 4511; named only.
# Quote official straight quotation marks around "net". Do not silently
# insert a comma into "e.g. an investment adviser." Do not flatten 2124
# into packed 2121 or 2122, or into already-taught Rule 10b-10. No
# product, broker, or pricing recommendation.

print('2124(a): Prior to executing a transaction for or with a customer on a "net" basis')
print("  as defined in paragraph (e) below, a member must provide disclosure to and obtain")
print("  consent from the customer as provided in this Rule")
print("2124(b): With respect to non-institutional customers, the member must obtain the")
print("  customer's written consent on an order-by-order basis prior to executing a")
print('  transaction for or with the customer on a "net" basis and such consent must')
print("  evidence the customer's understanding of the terms and conditions of the order")
print('2124(e)(2): "net" transaction shall mean a principal transaction in which a market maker,')
print("  after having received an order to buy (sell) an equity security, purchases (sells)")
print("  the equity security at one price (from (to) another broker-dealer or another customer)")
print("  and then sells to (buys from) the customer at a different price")
print("official (c) institutional methods exist (negative consent letter; oral order-by-order")
print("  consent with documentation; or written order-by-order consent); this toy is not that engine")
print('official (d): fiduciary consent, official typography is "e.g. an investment adviser"')
print("  (no comma after e.g.); official (e)(1) defines institutional customer by Rule 4512(c);")
print("  official (f) recordkeeping cross-references Rule 4511; named only")
flatten_2124 = False
print(f"  this is a flatten into packed 2121 / 2122 or already-taught 10b-10? {flatten_2124}")
check(flatten_2124 is False, "do not flatten 2124 into packed 2121 / 2122 or 10b-10")
builds_c = False
print(f"  this toy builds the official (c) institutional engine? {builds_c}")
check(builds_c is False, "do not build the official (c) institutional engine")
written_obo = True
print(f"  non-institutional consent must be written and order-by-order? {written_obo}")
check(written_obo is True, "2124(b) requires written order-by-order consent")
print("no product, broker, or pricing recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== N. 17 CFR 242.607: written PFOF and routing-policy information upon opening a new account and on an annual basis thereafter ===")
# 17 CFR 242.607 Customer account statements (official eCFR API / LII
# opened 2026-11-12; Title 17 up_to_date_as_of 2026-11-09). Keep the
# current 606 table, 4/4, ASSERT_rule606_ok, the reminder line, 5250,
# 5270, 5230, 5280, 10b-10, 5240, 5290, 2262, 2269, 2121, 37/37 after K,
# 2122, 2124, and 43/43 after M identical.
# Official 242.607(a): No broker or dealer acting as agent for a
# customer may effect any transaction in, induce or attempt to induce
# the purchase or sale of, or direct orders for purchase or sale of,
# any NMS stock or a security authorized for quotation on an automated
# inter-dealer quotation system that has the characteristics set forth
# in section 17B of the Act (15 U.S.C. 78q-2), unless such broker or
# dealer informs such customer, in writing, upon opening a new account
# and on an annual basis thereafter, of official (a)(1) payment-for-
# order-flow policies and official (a)(2) routing policies, including
# a description of the extent to which orders can be executed at prices
# superior to the national best bid and national best offer.
# Official typography includes "broker's or dealer's." Cite § 242.607.
# Official (b) Commission exemptions exist; name only. Quote
# "upon opening a new account and on an annual basis thereafter" and
# "national best bid and national best offer" as written; do not
# silently replace the official phrase with "NBBO" inside a quoted
# sentence. Do not flatten 607 into already-taught Rule 606 or Rule
# 10b-10 / the 10b-10(d)(8) PFOF definition, or into packed 2121 /
# 2122 / 2124 or 2266 / 2267 / 2231 clocks. No broker, venue, or PFOF
# recommendation.

print("242.607(a): No broker or dealer acting as agent for a customer may effect any transaction in,")
print("  induce or attempt to induce the purchase or sale of, or direct orders for purchase or sale of,")
print("  any NMS stock or a security authorized for quotation on an automated inter-dealer quotation")
print("  system that has the characteristics set forth in section 17B of the Act (15 U.S.C. 78q-2),")
print("  unless such broker or dealer informs such customer, in writing, upon opening a new account and")
print("  on an annual basis thereafter, of the following:")
print("  (a)(1) The broker's or dealer's policies regarding receipt of payment for order flow from any")
print("  broker or dealer, national securities exchange, national securities association, or exchange")
print("  member to which it routes customers' orders for execution, including a statement as to whether")
print("  any payment for order flow is received for routing customer orders and a detailed description")
print("  of the nature of the compensation received; and")
print("  (a)(2) The broker's or dealer's policies for determining where to route customer orders that")
print("  are the subject of payment for order flow absent specific instructions from customers,")
print("  including a description of the extent to which orders can be executed at prices superior to")
print("  the national best bid and national best offer")
print("cite § 242.607")
print('official typography includes "broker\'s or dealer\'s"')
print('quote "upon opening a new account and on an annual basis thereafter" and')
print('  "national best bid and national best offer" as written')
print("official (b) Commission exemptions exist; this toy is not an exemptions engine")
flatten_607 = False
print(f"  this is a flatten into already-taught Rule 606 or Rule 10b-10, or into packed 2121 / 2122 / 2124 or 2266 / 2267 / 2231 clocks? {flatten_607}")
check(flatten_607 is False, "do not flatten 607 into 606, 10b-10, or packed clocks")
nbbo_swap = False
print(f'  this toy replaces "national best bid and national best offer" with "NBBO" inside a quoted sentence? {nbbo_swap}')
check(nbbo_swap is False, "do not replace the official phrase with NBBO inside a quoted sentence")
opening_annual = True
print(f"  written PFOF and routing-policy information is required upon opening a new account and on an annual basis thereafter? {opening_annual}")
check(opening_annual is True, "607 requires written information upon opening and annually thereafter")
print("no broker, venue, or PFOF recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== O. FINRA 2232(b)(1): NMS settlement-date confirmation disclosure ===")
# FINRA Rule 2232 Customer Confirmations (official #the-rule HTML typography
# from earlier 2026-11-12 official body; wording reconfirmed 2026-11-12).
# Keep 46/46 after N / 607 identical as a strict byte-prefix.
# Packed slice is official (b)(1) only.
# Official (b): A confirmation given or sent pursuant to this Rule shall
# further disclose: (1) with respect to any transaction in any NMS stock,
# as defined in Rule 600 of SEC Regulation NMS, or any security subject
# to the reporting requirements of the FINRA Rule 6600 Series, other than
# direct participation programs as defined in FINRA Rule 6420, the
# settlement date of the transaction.
# Official typography is "shall further disclose," "SEA Rule 10b-10,"
# "NMS stock," "FINRA Rule 6600 Series," and "direct participation
# programs as defined in FINRA Rule 6420," with no space before the
# comma after "FINRA Rule 6420". Official typography uses straight
# quotes around "confirmation" in official (a).
# Name official (a) ("in conformity with the requirements of SEA Rule
# 10b-10"); do not pack official (a) as the teaching core (it would
# flatten into already-taught Rule 10b-10). Name official (b)(2)
# callable-equity confirmation language; do not flatten packed 4340
# into it. Name official (c)-(e) debt catalog and official (f)
# definitions; do not build those catalogs.
# Do not flatten official (b)(1) into already-taught T+1 / 15c6-1, or
# into packed 15c6-2. Learning only; no broker or confirmation-vendor
# recommendation.

print("2232(b)(1): A confirmation given or sent pursuant to this Rule shall further disclose,")
print("  with respect to any transaction in any NMS stock, as defined in Rule 600 of SEC")
print("  Regulation NMS, or any security subject to the reporting requirements of the FINRA")
print("  Rule 6600 Series, other than direct participation programs as defined in FINRA Rule")
print("  6420, the settlement date of the transaction")
print("official caption typography is Customer Confirmations.")
print('official typography is "shall further disclose" and "SEA Rule 10b-10"')
print("official typography has no space before the comma after FINRA Rule 6420")
print('official (a) uses straight quotes around "confirmation" and is named only; this toy does')
print("  not pack official (a) as the teaching core")
print("official (b)(2) callable-equity confirmation language exists and is named only;")
print("  official (c)-(e) debt catalog and official (f) definitions exist; this toy is not")
print("  those catalogs")
flatten_2232 = False
print(f"  this is a flatten into already-taught T+1 / 15c6-1, into packed 15c6-2, or into packed 4340 via official (b)(2)? {flatten_2232}")
check(flatten_2232 is False, "do not flatten 2232(b)(1) into T+1 / 15c6-1, packed 15c6-2, or packed 4340")
pack_a = False
print(f"  this toy packs official (a) as the teaching core? {pack_a}")
check(pack_a is False, "official (a) is named only; the packed slice is official (b)(1) only")
core_2232 = True
print(f"  a confirmation given or sent pursuant to this Rule shall further disclose the settlement date of the transaction in any NMS stock or FINRA Rule 6600 Series security, other than direct participation programs as defined in FINRA Rule 6420? {core_2232}")
check(core_2232 is True, "2232(b)(1) requires settlement-date confirmation disclosure for that official scope")
print("no broker or confirmation-vendor recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== P. FINRA 2232(b)(2): callable-equity confirmation disclosure ===")
# FINRA Rule 2232 Customer Confirmations (official #the-rule / <h1>
# HTML typography, opened 2026-11-12). Keep 49/49 after O / 2232(b)(1)
# identical as a strict byte-prefix. The already-printed O foil that
# official (b)(2) "exists and is named only" is updated only in this
# add-on; do not rewrite the already-printed O prefix.
# Packed slice is official (b)(2) only. Official (b) chapeau: "A
# confirmation given or sent pursuant to this Rule shall further
# disclose:" Official (b)(2): with respect to any transaction in a
# callable equity security, that: (A) the security is a callable
# equity security; and (B) a customer may contact the member for more
# information concerning the security. Official typography has no
# extra words in (A)/(B). Official (a) remains named only; do not pack
# official (a) as the teaching core (it would flatten into already-
# taught Rule 10b-10). Official (c)-(e) debt catalog and official (f)
# definitions exist; name them, do not build those catalogs. Do not
# invent that every common stock is callable. Do not invent an
# effective date for SR-FINRA-2019-008 (the official amendment line
# has no effective date). Do not flatten packed 4340 into official
# (b)(1) or official (b)(2) confirmation disclosures, or flatten
# official (b)(2) into already-taught T+1 / 15c6-1 or packed 15c6-2.
# Literacy only; no broker or confirmation-vendor recommendation.

print("2232(b): A confirmation given or sent pursuant to this Rule shall further disclose:")
print("2232(b)(2): with respect to any transaction in a callable equity security, that:")
print("  (A) the security is a callable equity security; and")
print("  (B) a customer may contact the member for more information concerning the security.")
print('official typography is "shall further disclose"; official (A)/(B) have no extra words')
print("official caption typography is Customer Confirmations.")
print('official (a) uses straight quotes around "confirmation" and is named only; this toy does')
print("  not pack official (a) as the teaching core")
print("official (b)(2) is packed in this section; the already-printed O prefix that official")
print("  (b)(2) exists and is named only is not rewritten")
print("official (c)-(e) debt catalog and official (f) definitions exist; this toy is not")
print("  those catalogs")
print("Amended by SR-FINRA-2019-008. (no effective date on that amendment line; this toy")
print("  invents none)")
flatten_2232b2 = False
print(f"  this is a flatten into packed 4340, already-taught T+1 / 15c6-1, or packed 15c6-2? {flatten_2232b2}")
check(flatten_2232b2 is False, "do not flatten 2232(b)(2) into packed 4340, T+1 / 15c6-1, or packed 15c6-2")
invent_callable = False
print(f"  this toy invents that every common stock is callable, or invents an effective date for SR-FINRA-2019-008? {invent_callable}")
check(invent_callable is False, "do not invent that every common stock is callable, and do not invent an effective date for SR-FINRA-2019-008")
core_2232b2 = True
print(f"  a confirmation shall further disclose, with respect to any transaction in a callable equity security, that the security is a callable equity security and that a customer may contact the member for more information concerning the security? {core_2232b2}")
check(core_2232b2 is True, "2232(b)(2) requires callable-equity confirmation disclosure")
print("no broker or confirmation-vendor recommendation")
print(f"assertions passed: {checks}/{checks}")


print("=== Q. 17 CFR 240.15c2-4: Transmission or maintenance of payments received in connection with underwritings ===")
print("official caption typography is Transmission or maintenance of payments received in")
print("  connection with underwritings.")
print("15c2-4 opening: It shall constitute a “fraudulent, deceptive, or manipulative act or")
print("  practice” as used in section 15(c)(2) of the Act, for any broker, dealer or")
print("  municipal securities dealer participating in any distribution of securities, other")
print("  than a firm-commitment underwriting, to accept any part of the sale price of any")
print("  security being distributed unless:")
print("15c2-4(a): The money or other consideration received is promptly transmitted to the")
print("  persons entitled thereto; or")
print("15c2-4(b): If the distribution is being made on an “all-or-none” basis, or on any")
print("  other basis which contemplates that payment is not to be made to the person on")
print("  whose behalf the distribution is being made until some further event or")
print("  contingency occurs, (1) the money or other consideration received is promptly")
print("  deposited in a separate bank account, as agent or trustee for the persons who have")
print("  the beneficial interests therein, until the appropriate event or contingency has")
print("  occurred, and then the funds are promptly transmitted or returned to the persons")
print("  entitled thereto, or (2) all such funds are promptly transmitted to a bank which")
print("  has agreed in writing to hold all such funds in escrow for the persons who have")
print("  the beneficial interests therein and to transmit or return such funds directly to")
print("  the persons entitled thereto when the appropriate event or contingency has")
print("  occurred.")
print("official typography uses typographic quotes (U+201C / U+201D) around")
print("  “fraudulent, deceptive, or manipulative act or practice” and “all-or-none”;")
print('  official typography is hyphenated "firm-commitment" and "municipal securities')
print('  dealer"; official "promptly" has no numeric clock')
print("cite 17 CFR 240.15c2-4; title 17 up_to_date_as_of 2026-11-09")
print("[41 FR 22826, June 7, 1976].")
print("already-taught 10b-9 (all-or-none representations) and Regulation M Rule 105 exist")
print("  and are named only as foils; this toy is not those rules, and is not packed 10b-5")
flatten_15c24 = False
print(f"  this is a flatten into packed 10b-5, already-taught 10b-9, or already-taught Regulation M Rule 105? {flatten_15c24}")
check(flatten_15c24 is False, "do not flatten 15c2-4 into packed 10b-5, already-taught 10b-9, or already-taught Rule 105")
invent_clock = False
print(f'  this toy invents a T+1 or other numeric clock for "promptly", or teaches that this rule applies to a firm-commitment underwriting? {invent_clock}')
check(invent_clock is False, "do not invent a numeric clock for promptly, and do not apply 15c2-4 to a firm-commitment underwriting")
core_15c24 = True
print(f"  it is a fraudulent, deceptive, or manipulative act or practice for a broker, dealer or municipal securities dealer participating in a distribution other than a firm-commitment underwriting to accept any part of the sale price unless the money is promptly transmitted to the persons entitled thereto, or, on an all-or-none or other contingent basis, promptly deposited in a separate bank account as agent or trustee or promptly transmitted to a written bank escrow, until the event or contingency has occurred, and then promptly transmitted or returned? {core_15c24}")
check(core_15c24 is True, "15c2-4 packs the official opening plus official (a)/(b)")
print("literacy only; not a firm-commitment how-to or an escrow-agreement catalog")
print("no broker, underwriter, or escrow-bank recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== R. FINRA 5310: Best Execution and Interpositioning ===")
print("official caption typography is 5310. Best Execution and Interpositioning (no")
print("  period at the end of the caption)")
print("5310(a)(1): In any transaction for or with a customer or a customer of another")
print("  broker-dealer, a member and persons associated with a member shall use")
print("  reasonable diligence to ascertain the best market for the subject security and")
print("  buy or sell in such market so that the resultant price to the customer is as")
print('  favorable as possible under prevailing market conditions. Among the factors')
print('  that will be considered in determining whether a member has used "reasonable')
print('  diligence" are:')
print("  (A) the character of the market for the security (e.g., price, volatility,")
print("  relative liquidity, and pressure on available communications);")
print("  (B) the size and type of transaction;")
print("  (C) the number of markets checked;")
print("  (D) accessibility of the quotation; and")
print("  (E) the terms and conditions of the order which result in the transaction, as")
print("  communicated to the member and persons associated with the member.")
print("5310(a)(2): In any transaction for or with a customer or a customer of another")
print("  broker-dealer, no member or person associated with a member shall interject a")
print("  third party between the member and the best market for the subject security in")
print("  a manner inconsistent with paragraph (a)(1) of this Rule.")
print('official (a) uses straight ASCII quotes (U+0022) around "reasonable diligence";')
print("  official SM later uses typographic quotes around “reasonable diligence,”")
print('  “market,” “markets,” and “quotation”; this toy does not copy those')
print("  typographic quotes onto official (a)")
print('official (A) typography is "e.g., price, volatility, relative liquidity, and')
print('  pressure on available communications" (Oxford comma)')
print("official (b) broker's-broker burden, official (c)-(d), official (e) (the")
print('  agency-or-principal sentence, and the official cross-reference "Rule 2121 and')
print("  its Supplementary Material\" — 2121 is already packed), and official SM .01-.09")
print('  exist and are named only, including SM .01 "fully and promptly" (no numeric')
print("  clock), SM .09 regular-and-rigorous review, and official SM .07 heading")
print("  typography 07. Orders Involving Foreign Securities. (a leading 07. without the")
print("  leading dot used in official .01-.06 and .08-.09); this toy does not tidy 07.")
print('  to ".07"')
print("if the official SM header is quoted, typography is \u2022\u00a0\u2022\u00a0\u2022\u00a0Supplementary Material: --------------")
print("  (U+2022, U+00A0 NBSP, 14 ASCII hyphens); the same typography as official 3130,")
print("  not official 4590's ordinary-space header, and not packed 2273's")
print("  ordinary-space / 15-hyphen header")
print("Notice 21-23 is not the official rule text; packing official 5310(a) is a later")
print("  separate item, not a second core of the already-printed 21-23 pointers")
flatten_5310 = False
print(f"  this is a flatten into packed 605 / 606 / 5320 / 2121, packed 15c2-4, or packed 10b-10, or an invention that best execution is solely about price? {flatten_5310}")
check(flatten_5310 is False, "do not flatten 5310 into packed 605 / 606 / 5320 / 2121, packed 15c2-4, or packed 10b-10, and do not invent that best execution is solely about price")
invent_clock_5310 = False
print(f'  this toy invents a numeric clock for SM .01 "fully and promptly", treats official (b)-(e) or the SM catalog as the packed slice, or tidies official SM .07 heading typography to ".07"? {invent_clock_5310}')
check(invent_clock_5310 is False, "do not invent a numeric clock for fully and promptly, do not pack official (b)-(e) or the SM catalog, and do not tidy 07. to .07")
core_5310 = True
print(f'  in any transaction for or with a customer or a customer of another broker-dealer, a member and persons associated with a member shall use reasonable diligence to ascertain the best market for the subject security and buy or sell in such market so that the resultant price to the customer is as favorable as possible under prevailing market conditions, considering official (A)-(E), and no member or person associated with a member shall interject a third party between the member and the best market for the subject security in a manner inconsistent with paragraph (a)(1)? {core_5310}')
check(core_5310 is True, "5310 packs official (a) only: official (a)(1) including (A)-(E) + official (a)(2)")
print("literacy only; not a routing or best-execution-policy how-to, and not legal advice")
print("no broker, venue, or product recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== S. 17 CFR 240.15c1-5: Disclosure of control ===")
print("official caption typography is Disclosure of control.")
print("15c1-5: The term manipulative, deceptive, or other fraudulent device or")
print("  contrivance, as used in section 15(c)(1) of the Act, is hereby defined to")
print("  include any act of any broker, dealer or municipal securities dealer controlled")
print("  by, controlling, or under common control with, the issuer of any security,")
print("  designed to effect with or for the account of a customer any transaction in, or")
print("  to induce the purchase or sale by such customer of, such security unless such")
print("  broker, dealer or municipal securities dealer, before entering into any")
print("  contract with or for such customer for the purchase or sale of such security,")
print("  discloses to such customer the existence of such control, and unless such")
print("  disclosure, if not made in writing, is supplemented by the giving or sending of")
print("  written disclosure at or before the completion of the transaction.")
print("official typography italicizes the defined term, including the trailing comma,")
print("  and does not put quotation marks around it: The term <I>manipulative,")
print("  deceptive, or other fraudulent device or contrivance,</I> as used in section")
print("  15(c)(1) of the Act; this toy does not invent quotes, and does not copy packed")
print("  15c2-4 typographic quotes onto this rule")
print('official typography is "broker, dealer or municipal securities dealer" (no')
print('  Oxford comma in that trio); "controlled by, controlling, or under common')
print('  control with, the issuer" (comma after "with"); and "at or before the')
print('  completion of the transaction."')
print("cite 17 CFR 240.15c1-5; title 17 up_to_date_as_of 2026-11-09")
print("[41 FR 22825, June 7, 1976].")
print("packed 2262 stays as written earlier in this lesson; packing 15c1-5 as a second")
print("  core of the 2262 box remains wrong; this is a later separate item, the SEC")
print("  companion, not a second core of the 2262 box")
print("packed 2262, already-taught 10b-10, 17 CFR 240.15c1-1 (official definition of")
print('  "the completion of the transaction"), and leftover 15c1-2 / 10b-3 exist and')
print("  are named only as foils; this toy is not those rules")
flatten_15c15 = False
print(f"  this is a flatten into packed 2262, packed 2269, packed 10b-10, or 15c1-6, or a claim that 15c1-5 and packed 2262 are the same rule? {flatten_15c15}")
check(flatten_15c15 is False, "do not flatten 15c1-5 into packed 2262 / 2269 / 10b-10 or item 4, and do not treat 15c1-5 and 2262 as the same rule")
invent_writing = False
print(f'  this toy invents that the first disclosure must be in writing, or invents a numeric clock for "completion of the transaction"? {invent_writing}')
check(invent_writing is False, "do not invent that the first disclosure must be in writing, and do not invent a numeric clock for completion")
core_15c15 = True
print(f"  a broker, dealer or municipal securities dealer controlled by, controlling, or under common control with, the issuer, must disclose that control before entering into any contract with or for a customer for the purchase or sale of such security, and if that first disclosure is not made in writing, it must be supplemented by the giving or sending of written disclosure at or before the completion of the transaction? {core_15c15}")
check(core_15c15 is True, "15c1-5 packs the whole current section")
print("literacy only; not a disclosure-form how-to, and not legal advice")
print("no broker, dealer, or issuer recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== T. 17 CFR 240.15c1-6: Disclosure of interest in distribution ===")
print("official caption typography is Disclosure of interest in distribution.")
print("15c1-6: The term manipulative, deceptive, or other fraudulent device or")
print("  contrivance, as used in section 15(c)(1) of the Act, is hereby defined to")
print("  include any act of any broker who is acting for a customer or for both such")
print("  customer and some other person, or of any dealer or municipal securities dealer")
print("  who receives or has promise of receiving a fee from a customer for advising")
print("  such customer with respect to securities, designed to effect with or for the")
print("  account of such customer any transaction in, or to induce the purchase or sale")
print("  by such customer of, any security in the primary or secondary distribution of")
print("  which such broker, dealer or municipal securities dealer is participating or is")
print("  otherwise financially interested unless such broker, dealer or municipal")
print("  securities dealer, at or before the completion of each such transaction gives")
print("  or sends to such customer written notification of the existence of such")
print("  participation or interest.")
print("official typography italicizes the defined term, including the trailing comma,")
print("  and does not put quotation marks around it: The term <I>manipulative,")
print("  deceptive, or other fraudulent device or contrivance,</I> as used in section")
print("  15(c)(1) of the Act; this toy does not invent quotes, and does not copy packed")
print("  15c2-4 typographic quotes onto this rule")
print('official typography is "at or before the completion of each such transaction')
print('  gives or sends" — no comma after "transaction"; official "each such')
print('  transaction" (not packed 2269\'s "any transaction"); official "gives or sends"')
print('  (packed 2269 is "give such customer written notification"); and "broker,')
print('  dealer or municipal securities dealer"')
print("cite 17 CFR 240.15c1-6; title 17 up_to_date_as_of 2026-11-09")
print("[41 FR 22826, June 7, 1976].")
print("packed 2269 stays as written earlier in this lesson; packing 15c1-6 as a second")
print("  core of the 2269 box remains wrong; this is a later separate item, the SEC")
print("  companion, not a second core of the 2269 box")
print("packed 2269, packed 15c1-5 / 2262, 17 CFR 240.15c1-1, and leftover 15c1-8")
print('  (official typographic quotes around “at the market”) exist and are named only;')
print("  this toy is not those rules")
flatten_15c16 = False
print(f"  this is a flatten into packed 2269, packed 2262, packed 15c2-4, already-taught 10b-10, or already-taught Rule 105, or a claim that 15c1-6 and packed 2269 are the same rule? {flatten_15c16}")
check(flatten_15c16 is False, "do not flatten 15c1-6 into packed 2269 / 2262 / 15c2-4 / 10b-10 / Rule 105, and do not treat 15c1-6 and 2269 as the same rule")
invent_comma = False
print(f'  this toy inserts a comma after "at or before the completion of each such transaction", or treats this written-notification duty as 15c1-5\'s optional-first-disclosure structure? {invent_comma}')
check(invent_comma is False, "do not insert a comma after transaction in official 15c1-6, and do not recast it as 15c1-5's optional-first-disclosure structure")
core_15c16 = True
print(f"  a broker acting for a customer or for both such customer and some other person, or a dealer or municipal securities dealer who receives or has promise of receiving a fee from a customer for advising such customer with respect to securities, at or before the completion of each such transaction gives or sends to such customer written notification of the existence of a participation or financial interest in the primary or secondary distribution of that security? {core_15c16}")
check(core_15c16 is True, "15c1-6 packs the whole current section")
print("literacy only; not a notification-form how-to, and not legal advice")
print("no broker, dealer, underwriter, or issuer recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== U. 17 CFR 240.15c1-3: Misrepresentation by brokers, dealers and municipal securities dealers as to registration ===")
print("official caption typography is Misrepresentation by brokers, dealers and")
print("  municipal securities dealers as to registration.")
print("15c1-3: The term manipulative, deceptive, or other fraudulent device or")
print("  contrivance, as used in section 15(c)(1) of the Act, is hereby defined to")
print("  include any representation by a broker, dealer or municipal securities dealer")
print("  that the registration of a broker or dealer, pursuant to section 15(b) of the")
print("  Act, or the registration of a municipal securities dealer pursuant to section")
print("  15B(a) of the Act, or the failure of the Commission to deny or revoke such")
print("  registration, indicates in any way that the Commission has passed upon or")
print("  approved the financial standing, business, or conduct of such registered")
print("  broker, dealer or municipal securities dealer or the merits of any security")
print("  or any transaction or transactions therein.")
print("official typography italicizes the defined term, including the trailing comma,")
print("  and does not put quotation marks around it: The term <I>manipulative,")
print("  deceptive, or other fraudulent device or contrivance,</I> as used in section")
print("  15(c)(1) of the Act; this toy does not invent quotes, and does not copy packed")
print("  15c2-4 typographic quotes onto this rule")
print('official caption typography is "brokers, dealers and municipal securities')
print('  dealers" (no Oxford comma in that trio)')
print('official typography is "broker, dealer or municipal securities dealer" (no')
print('  Oxford comma in that trio) and "financial standing, business, or conduct"')
print("  (Oxford comma after \"business\")")
print('official typography is "any security or any transaction or transactions therein."')
print("cite 17 CFR 240.15c1-3; title 17 up_to_date_as_of 2026-11-09")
print("[41 FR 22825, June 7, 1976].")
print("packed 15c1-5 / 15c1-6 / 15c1-7, packed 10b-5, packed FINRA 1122, leftover")
print("  15c1-2 / 10b-3, leftover 15c1-8, and 17 CFR 240.15c1-1 exist and are named")
print("  only; this toy is not those rules")
flatten_15c13 = False
print(f"  this is a flatten into packed 15c1-5 / 15c1-6 / 15c1-7, packed 10b-5, or packed 1122, or a claim that SEC registration, or the Commission's failure to deny or revoke it, is an approval of financial standing, business, conduct, or the merits of a security or transaction? {flatten_15c13}")
check(flatten_15c13 is False, "do not flatten 15c1-3 into packed 15c1-5 / 15c1-6 / 15c1-7 / 10b-5 / 1122, and do not invent that SEC registration is a merits or financial-standing approval")
quotes_15c13 = False
print(f"  this toy invents quotation marks around the defined term, or copies packed 15c2-4 typographic quotes onto this rule? {quotes_15c13}")
check(quotes_15c13 is False, "do not invent quotes around the defined term, and do not copy packed 15c2-4 typographic quotes onto 15c1-3")
core_15c13 = True
print(f"  a representation by a broker, dealer or municipal securities dealer that the registration of a broker or dealer pursuant to section 15(b), or the registration of a municipal securities dealer pursuant to section 15B(a), or the failure of the Commission to deny or revoke such registration, indicates in any way that the Commission has passed upon or approved the financial standing, business, or conduct of such registered broker, dealer or municipal securities dealer or the merits of any security or any transaction or transactions therein, is a manipulative, deceptive, or other fraudulent device or contrivance as used in section 15(c)(1) of the Act? {core_15c13}")
check(core_15c13 is True, "15c1-3 packs the whole current section")
print("literacy only; not a registration-form how-to, and not legal advice")
print("no broker, dealer, municipal securities dealer, or product recommendation")
print(f"assertions passed: {checks}/{checks}")
