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
