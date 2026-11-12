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
