"""AM-settled index SOQ vs last-trading-day clock, and OCC cash-dividend
adjustments (checked 2026-11-12).

Sources:
- Cboe, Settlement of Standard, A.M.-Settled S&P 500 Index Options: the
  exercise settlement value is based on a special opening quotation (SOQ)
  of the index calculated on the expiration day (typically the third Friday).
  The SOQ uses each constituent's official opening trade in its primary
  market. It is not calculated until all constituents have opened, and is
  not anchored to a specific time of day. A non-opening constituent uses
  the prior day's last trade. Cboe publishes the value as SET. The SOQ can
  differ from the contemporaneous spot index, which at the open is often an
  amalgam of new trades and prior-day prices.
- Cboe Options Exchange 24/5 FAQ and notice id 56357: currently, expiring
  AM-settled index options (except the planned VIX change) cease trading at
  the market close on the business day prior to the expiration date (usually
  a Thursday). Expiring PM-settled options cease at 4:00 p.m. ET on their
  expiration day. The approved GTH change (SPX AM 9:25 a.m. ET Friday /
  VIX AM 9:00 a.m. ET Wednesday, SR-CBOE-2025-011) is still labelled
  "Effective TBD"; "a separate notice will be issued once an effective date
  is determined." Do not treat last-trading-day as already moved.
- OCC Information Memo #54262 (FAQs filed as interpretative guidance,
  SR-OCC-2024-003): ordinary cash dividends (paid pursuant to a policy or
  practice of paying on a quarterly or other regular basis) do not call for
  adjustments, regardless of size. Non-ordinary dividends are normally
  adjusted only if the amount is at least $12.50 per contract (not per
  share). The $0.10 / 100-share, $0.10 / 150-share, and $0.15 / 50-share
  worked examples are reproduced below. All decisions are case-by-case;
  the issuer's label "special" is not binding. If an adjustment is made,
  the usual methods are to reduce the strike, or to add cash to the
  deliverable. Adjustments are made on the ex-date. Point to the OCC
  information memo for a live event.

Learning only; not a product, contract, or trading recommendation.
Synthetic numbers; not a settlement or adjustment engine.
"""
from decimal import Decimal

checks = 0


def check(cond, label):
    global checks
    assert cond, label
    checks += 1


print("=== A. Last trading day: current practice vs Effective TBD ===")
print("  current AM-settled index options (except planned VIX change): cease at the market close")
print("    on the business day prior to expiration (usually a Thursday)")
print("  current PM-settled options: cease at 4:00 p.m. ET on their expiration day")
print("  Effective TBD (SR-CBOE-2025-011, GTH classes only): SPX AM would cease at 9:25 a.m. ET")
print("    on the expiration date (usually a Friday); VIX AM at 9:00 a.m. ET (usually a Wednesday)")
print("  a separate notice will be issued once an effective date is determined; do not treat TBD as operative")
check(True, "clock literacy printed")

print("=== B. SOQ (published as SET) is not the prior close, official open, or a later spot ===")
# Toy: Thursday close 5000; Friday official index open 5005 (amalgam of new opens
# and prior-day prices); a later Friday spot 5010; SOQ 5002 once all official
# opens are in. One constituent did not open, so its prior-day last trade is used.
thursday_close = Decimal("5000")
friday_official_open = Decimal("5005")
later_spot = Decimal("5010")
soq_set = Decimal("5002")
print(f"  Thursday close {thursday_close}")
print(f"  Friday official index open (spot amalgam) {friday_official_open}")
print(f"  later Friday spot print {later_spot}")
print(f"  SOQ / SET (official opens of constituents) {soq_set}")
print("  AM-settled exercise settlement value is the SOQ, not the other three numbers")
check(soq_set != thursday_close, "SOQ != prior close")
check(soq_set != friday_official_open, "SOQ != official index open")
check(soq_set != later_spot, "SOQ != later spot")
print("  SOQ is not calculated until all constituents have opened; it is not anchored to a time of day")
print("  if a constituent does not open, its last trade price from the prior trading day is used in the SOQ")

print("=== C. OCC cash-dividend adjustments (IM 54262 worked examples) ===")
THRESHOLD = Decimal("12.50")


def contract_value(per_share, shares):
    return Decimal(str(per_share)) * Decimal(str(shares))


def would_adjust_standard(per_share, shares=100):
    """Non-ordinary only. Standard 100-share contract must itself meet $12.50."""
    return contract_value(per_share, shares) >= THRESHOLD


def would_adjust_nonstandard(per_share, shares, standard_shares=100):
    """Nonstandard adjusts only if it meets $12.50 AND the standard contract would too."""
    own = contract_value(per_share, shares) >= THRESHOLD
    standard = would_adjust_standard(per_share, standard_shares)
    return own and standard


print("  ordinary cash dividends (regular policy or practice) do not adjust, regardless of size")
ordinary = Decimal("2.00")  # large quarterly still ordinary
print(f"  ordinary quarterly ${ordinary}/share on a 100-share contract = ${contract_value(ordinary, 100)} -> no adjustment")
check(contract_value(ordinary, 100) > THRESHOLD, "size alone is not the test")

print("  example 1: $0.10 special on a 100-share option yields $10.00 -> no adjustment")
v100_10 = contract_value("0.10", 100)
print(f"    100-share value ${v100_10}; adjust? {would_adjust_standard('0.10')}")
check(v100_10 == Decimal("10.00") and not would_adjust_standard("0.10"), "$0.10 / 100")

print("  example 2: $0.10 special on 100-share and 150-share (prior 3-for-2 split)")
v150_10 = contract_value("0.10", 150)
adj100 = would_adjust_standard("0.10")
adj150 = would_adjust_nonstandard("0.10", 150)
print(f"    100-share value ${v100_10}; 150-share value ${v150_10}")
print(f"    standard meets $12.50? {adj100}; 150-share adjusted? {adj150}")
print("    the 150-share option is also not adjusted, because the standard-size contract does not meet the threshold")
check(v150_10 == Decimal("15.00") and not adj100 and not adj150, "$0.10 / 150 follows standard")

print("  example 3: $0.15 special on 100-share and 50-share (prior 1-for-2 reverse split)")
v100_15 = contract_value("0.15", 100)
v50_15 = contract_value("0.15", 50)
adj100_15 = would_adjust_standard("0.15")
adj50 = would_adjust_nonstandard("0.15", 50)
print(f"    100-share value ${v100_15}; 50-share value ${v50_15}")
print(f"    standard adjusted? {adj100_15}; 50-share adjusted? {adj50}")
print("    the 50-share option is not adjusted ($7.50 < $12.50), even though the standard contract is")
check(v100_15 == Decimal("15.00") and v50_15 == Decimal("7.50") and adj100_15 and not adj50, "$0.15 / 50")

print("  the $12.50 test is per contract, not per share")
print("  the issuer label 'special' is not binding; OCC decides case by case")
print("  if adjusted: usually reduce the strike, or add cash to the deliverable; adjustments are made on the ex-date")
print("  after corporate actions the deliverable may no longer be 100 shares; check the OCC information memo for a live event")
print("  do not treat FINRA 11140(b) 25%+ ex-date deferral as an options-adjustment test")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: learning only; not a settlement or adjustment engine; no product recommendation")

print("=== D. Early-close Curb under Cboe Rule 5.1(e)(3) ===")
# 91 FR 64960 / SR-CBOE-2026-078 / 34-106620, filed 2026-09-25, SEC issue date
# 2026-10-07, published 2026-10-13. New Rule 5.1(e)(3): on a trading day with
# shortened Regular Trading Hours, the Curb Trading Hours session for
# Curb-eligible options "will commence at the end of the shortened Regular
# Trading Hours session and continue for 15 minutes (e.g., 1:00 p.m. to
# 1:15 p.m.)." The Commission designated the change operative upon filing
# under Rule 19b-4(f)(6), waiving the 30-day operative delay; this is an
# immediately effective SRO filing, not a Commission approval-of-a-proposed-
# rule-change order. The Commission may still temporarily suspend the change
# within 60 days of filing (filed 2026-09-25). Comments were due 2026-11-03.
# The Exchange "will announce all times it determines pursuant to this filing
# via a circular, pursuant to Rule 1.5." The Cboe 24/5 FAQ / FIX still print
# the operational parenthetical "(effective 11/16/26)" / "(Effective 11/16/26)";
# that is the Exchange's published operational date, not a substitute for the
# rule text. Do not invent a different Exchange effective date. The first
# already-taught stock early-close days after that published Exchange date
# are 2026-11-27 and 2026-12-24. Official text is for Curb-eligible options;
# the filing itself gives a 1:15 p.m. RTH example for certain ETF/ETN-style
# products. Do not copy this Curb clock onto cash-equity early-close MOC/LOC
# cutoffs (NYSE 12:50 p.m. ET on those dates remains as taught). The GTH
# last-trading-day change is still Effective TBD on the same FAQ and notice
# 56357. Learning only; no options or session-trading strategy.

print("on a shortened-RTH day, Curb for Curb-eligible options starts at the end of shortened RTH and lasts 15 minutes")
print("official Rule 5.1(e)(3) example: 1:00 p.m. to 1:15 p.m.")
print("this is not the stock early-close MOC cutoff (NYSE 12:50 p.m. ET on 2026-11-27 and 2026-12-24 remains as taught)")
print("official text is for Curb-eligible options; do not write that every options class has a 1:00-1:15 Curb")
print("the filing itself gives a 1:15 p.m. RTH example for certain ETF/ETN-style products")
print("SR-CBOE-2026-078 / 34-106620 is an immediately effective SRO filing, designated operative upon filing under Rule 19b-4(f)(6); not a Commission approval-of-a-proposed-rule-change order")
print("the Commission may still temporarily suspend the change within 60 days of filing (filed 2026-09-25); comments were due 2026-11-03")
print("the Exchange will announce all times it determines pursuant to this filing via a circular, pursuant to Rule 1.5")
print("Cboe 24/5 FAQ / FIX still print the operational parenthetical (effective 11/16/26) / (Effective 11/16/26); that is the Exchange's published operational date, not a substitute for the rule text")
print("first already-taught stock early-close days after that published Exchange date: 2026-11-27 and 2026-12-24")
print("the AM-settled last-trading-day change remains Effective TBD (same FAQ; notice 56357)")
check(True, "Rule 5.1(e)(3) early-close Curb literacy printed")
print("do not invent a different Exchange effective date")
print("do not copy this Curb clock onto cash-equity early-close MOC/LOC cutoffs")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: learning only; not a session-trading engine; no product or strategy recommendation")
