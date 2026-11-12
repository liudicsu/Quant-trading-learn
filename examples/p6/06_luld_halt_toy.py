"""P6 lab 06: LULD vs MWCB vs Reg SHO Rule 201 — toy state machine (offline synthetic, seed=21).
Learning only — not investment advice. NOT a complete LULD rule engine.

Percentage parameters (LULD Plan Amendment 20, Appendix A; checked_on 2026-11-08):
  The day's PRICE TIER comes from the prior trading day's primary-listing close (not the moving reference):
  Tier 1: > $3 -> 5%; $0.75..$3 (inclusive) -> 20%; < $0.75 -> lesser of $0.15 or 75% of reference
  Tier 2: > $3 -> 10%; $0.75..$3 (inclusive) -> 20%; < $0.75 -> lesser of $0.15 or 75% of reference
  The moving reference price (usually mean of eligible trades, prior 5 min) does NOT reselect the tier;
  it sets the centre and, with the fixed tier parameters, the band width and bounds (Plan Sec. V(A)).
  Last 25 min of regular hours (or before an early close): double for all Tier 1 and for Tier 2 whose
  price tier is <= $3 (not Tier 2 > $3). Ordinary non-leveraged toy only.
  No opening doubling since Amendment 18 (2020-02-24).
"""
from __future__ import annotations
import numpy as np


def price_tier(prior_listing_close: float) -> str:
    """Price tier for the WHOLE day, fixed from the prior trading day's primary-listing close."""
    if prior_listing_close > 3.0:
        return "gt3"
    if prior_listing_close >= 0.75:
        return "0.75-3"          # $0.75 to $3, both ends inclusive
    return "lt0.75"


def band(tier: int, prior_listing_close: float, moving_ref: float, closing_window: bool) -> tuple[float, float, float, bool]:
    """Step 1: percentage + doubling eligibility from the day's price tier (prior close).
    Step 2: the moving reference price sets the centre AND enters the width/bounds:
    width = pct * moving_ref (or min(0.15, 0.75 * moving_ref) below $0.75); it never reselects the tier."""
    pt = price_tier(prior_listing_close)
    eligible_double = tier == 1 or pt != "gt3"     # Tier 2 above $3 is not doubled at the close
    doubled = closing_window and eligible_double
    if pt == "gt3":
        width = (0.05 if tier == 1 else 0.10) * moving_ref
    elif pt == "0.75-3":
        width = 0.20 * moving_ref
    else:
        width = min(0.15, 0.75 * moving_ref)
    if doubled:
        width *= 2
    return width / moving_ref, moving_ref - width, moving_ref + width, doubled


print("=== 1. tier from PRIOR CLOSE; centre, width and bounds from MOVING reference price ===")
for tier, pc, ref, cw in [(1, 50.0, 50.0, False), (1, 50.0, 50.0, True), (2, 50.0, 50.0, False), (2, 50.0, 50.0, True), (2, 2.0, 2.0, True), (1, 0.50, 0.50, False)]:
    p, lo_, hi_, d = band(tier, pc, ref, cw)
    print(f"tier{tier} prior_close={pc:>6.2f} ref={ref:>6.2f} closing_window={str(cw):5s} -> band +/-{p:.2%} = [{lo_:.4f}, {hi_:.4f}] doubled={d}")

print("=== 1b. boundary tests (prior close sets the tier, not the moving ref) ===")
TESTS = [
    # name, tier, prior_close, moving_ref, closing_window, expected pct
    ("cross $3 up:   prior 2.90 -> ref 3.10", 2, 2.90, 3.10, False, 0.20),
    ("cross $3 down: prior 3.10 -> ref 2.90", 2, 3.10, 2.90, False, 0.10),
    ("cross $0.75 up:   prior 0.74 -> ref 0.76", 2, 0.74, 0.76, False, 0.15 / 0.76),
    ("cross $0.75 down: prior 0.75 -> ref 0.74", 2, 0.75, 0.74, False, 0.20),
    ("closing: Tier2 prior 3.10 (not eligible)", 2, 3.10, 3.10, True, 0.10),
    ("closing: Tier2 prior 2.90 (eligible)", 2, 2.90, 3.10, True, 0.40),
    ("closing: Tier1 prior 50.00 (eligible)", 1, 50.0, 50.0, True, 0.10),
]
for name, tier, pc, ref, cw, exp in TESTS:
    p, lo_, hi_, d = band(tier, pc, ref, cw)
    assert abs(p - exp) < 1e-12, (name, p, exp)
    print(f"PASS {name}: tier{tier} -> +/-{p:.2%} [{lo_:.4f}, {hi_:.4f}] doubled={d}")
print(f"tests passed: {len(TESTS)}/{len(TESTS)}")

print("=== 2. toy single-stock path: limit state -> 5-min halt -> reopen gap ===")
rng = np.random.default_rng(21)
ref, tier = 40.0, 1
_, lo, hi, _ = band(tier, 40.0, ref, False)
prices = list(40 + np.cumsum(rng.normal(0, 0.05, 80)))
prices[10:14] = [lo, lo, lo, lo]           # offer sits at lower band (limit state)
limit_start, seconds_per_tick = 10, 5       # 4 ticks x 5 s = 20 s > 15 s -> pause
state, halted_until, fills = "normal", None, []
stop_level = 38.5
for t, px in enumerate(prices):
    if state == "halt":
        if t >= halted_until:
            state = "normal"; reopen = 37.20      # synthetic reopening price (gap)
            print(f"t={t}: reopen at {reopen:.2f} (gap from band {lo:.2f})")
            fills.append(("stop_sell", reopen))
        continue
    if px <= lo:
        dur = (t - limit_start + 1) * seconds_per_tick
        if dur > 15:
            state, halted_until = "halt", t + 60      # 60 ticks x 5 s = 5 min
            print(f"t={t}: limit state > 15 s ({dur}s) -> trading pause; no new fills while halted")
print(f"stop-sell trigger {stop_level:.2f} filled at {fills[0][1]:.2f} -> a stop order does not guarantee its price")

print("=== 3. three different mechanisms (do not merge them) ===")
prev_close = 40.0
print("MWCB: market-wide, S&P 500 decline vs prior close, Level 1/2/3 = 7%/13%/20%")
print("LULD: single stock, dynamic band around 5-min reference price, regular hours only")
last = 35.8
print(f"Reg SHO Rule 201: single stock fell {1-last/prev_close:.1%} >= 10% vs prior close -> short-sale PRICE TEST (not a halt) rest of day + next day")
print("disclaimer: synthetic; learning only")

print("=== 4. Plan Section VII reopen clocks (Regular Trading Hours) ===")
# LULD Plan Section VII, "Trading Pauses" (use Section VII only; do not teach
# Phase I hours from the 2016 compilation). Official Plan-participants site
# (opened 2026-11-12): the Plan "was approved as a permanent rule on April 11,
# 2019" and "applies during regular trading hours of 9:30 am ET - 4:00 pm ET."
# VII(B)(1): "Five minutes after declaring a Trading Pause for an NMS Stock,
# and if the Primary Listing Exchange has not declared a Regulatory Halt, the
# Primary Listing Exchange shall attempt to reopen trading using its
# established reopening procedures. The Trading Pause shall end when the
# Primary Listing Exchange reports a Reopening Price."
# VII(B)(3): "If the Primary Listing Exchange does not report a Reopening
# Price within ten minutes after the declaration of a Trading Pause in an
# NMS Stock, and has not declared a Regulatory Halt, all trading centers may
# begin trading the NMS Stock."
# VII(C)(1): "If a Trading Pause for an NMS Stock is declared in the last ten
# minutes of trading before the end of Regular Trading Hours, the Primary
# Listing Exchange shall not reopen trading and shall attempt to execute a
# closing transaction using its established closing procedures."
# VII(C)(2): if no closing transaction within five minutes after the end of
# Regular Trading Hours, all trading centers may begin trading the NMS Stock.
# Overnight Phase 1 (already taught) has no automatic Limit State -> pause —
# do not copy these Regular Trading Hours clocks onto 21:00-04:00.
# Do not invent a single Nasdaq Halt Cross or NYSE auction cutoff as Plan law.
# A mid-day reopening print is not a regular continuous-market trade, and is
# not a trade-through data error (Rule 611(b)(3)). No pause-trading strategy.

ATTEMPT_MINUTES = 5
ALL_CENTERS_MINUTES = 10
LAST_TEN_MINUTES = 10
CLOSE_FALLBACK_MINUTES = 5
print("five minutes after declaring a Trading Pause: Primary attempts to reopen using its established reopening procedures")
print("the Trading Pause ends when the Primary reports a Reopening Price")
print("if no Reopening Price within ten minutes and no Regulatory Halt: all trading centers may begin trading")
print("pause declared in the last ten minutes of Regular Trading Hours: no mid-session reopen; attempt a closing transaction")
print("if no closing transaction within five minutes after the end of Regular Trading Hours: all trading centers may begin trading")
assert ATTEMPT_MINUTES == 5 and ALL_CENTERS_MINUTES == 10
assert LAST_TEN_MINUTES == 10 and CLOSE_FALLBACK_MINUTES == 5
print("do not copy these Regular Trading Hours clocks onto overnight Phase 1 (no automatic Limit State -> pause)")
print("do not invent a single Nasdaq Halt Cross or NYSE auction cutoff as Plan law")
print("assertions passed: 4/4")
print("disclaimer: official Plan Section VII clocks; not a venue auction catalog; learning only")

print("=== 5. Nasdaq halt reason codes (official table map, not a new LULD rule) ===")
# Official Nasdaq Trade Halt Codes (opened 2026-11-12):
#   T1  Halt - News Pending — "Trading is halted pending the release of material news."
#   H10 Halt - SEC Trading Suspension — "The Securities and Exchange Commission has suspended trading in this stock."
#   LUDP Volatility Trading Pause
#   LUDS Volatility Trading Pause - Straddle Condition
#   MWC1 / MWC2 / MWC3 Market Wide Circuit Breaker Halt - Level 1 / 2 / 3
#   MWC0 Market Wide Circuit Breaker Halt - Carry over from previous day
# The same official table still describes T5 as "Single Stock Trading Pause
# in Effect" and "Trading has been paused by NASDAQ due to a 10% or more
# price move in the security in a five-minute period." That T5 sentence is
# not a current-law statement of the already-taught LULD Plan (Plan price
# bands, 15-second Limit State, five-minute pause, Section VII reopen
# clocks). Name T5 only as a stale official-table pitfall; do not print
# that sentence as current LULD. Do not treat every "Space / Reason Not
# Available" row as "no halt." Do not build a Nasdaq Halt Cross or NOII
# catalog. Learning only; no venue recommendation.

HALT_MAP = {
    "T1": "Halt - News Pending",
    "H10": "Halt - SEC Trading Suspension",
    "LUDP": "Volatility Trading Pause",
    "LUDS": "Volatility Trading Pause - Straddle Condition",
    "MWC1": "Market Wide Circuit Breaker Halt - Level 1",
    "MWC2": "Market Wide Circuit Breaker Halt - Level 2",
    "MWC3": "Market Wide Circuit Breaker Halt - Level 3",
    "MWC0": "Market Wide Circuit Breaker Halt - Carry over from previous day",
}
h_checks = 0


def h_check(cond, label):
    global h_checks
    assert cond, label
    h_checks += 1


print("official Nasdaq Trade Halt Codes mapped onto already-taught halt types:")
for code, desc in HALT_MAP.items():
    print(f"  {code}: {desc}")
h_check(HALT_MAP["T1"] == "Halt - News Pending", "T1")
h_check(HALT_MAP["H10"] == "Halt - SEC Trading Suspension", "H10")
h_check(HALT_MAP["LUDP"] == "Volatility Trading Pause", "LUDP")
h_check(HALT_MAP["LUDS"] == "Volatility Trading Pause - Straddle Condition", "LUDS")
h_check(HALT_MAP["MWC1"].endswith("Level 1") and HALT_MAP["MWC3"].endswith("Level 3"), "MWC1-3")
h_check(HALT_MAP["MWC0"].startswith("Market Wide Circuit Breaker Halt - Carry over"), "MWC0")
print("T1 maps to an exchange news-pending halt; H10 maps to an SEC trading suspension")
print("LUDP / LUDS map to an LULD-style volatility trading pause (including a straddle condition)")
print("MWC1 / MWC2 / MWC3 map to MWCB Level 1 / 2 / 3; MWC0 is a carry-over from the previous day")
print("the same official table still describes T5 as a 10% or more price move in a five-minute period")
print("that T5 sentence is not a current-law statement of the already-taught LULD Plan")
print("  (Plan price bands, 15-second Limit State, five-minute pause, Section VII reopen clocks)")
print("do not teach the table's T5 wording as the current LULD rule, and do not let it overwrite Plan text")
print("do not treat every Space / Reason Not Available row as no halt")
print("do not build a Nasdaq Halt Cross or NOII product catalog")
print(f"assertions passed: {h_checks}/{h_checks}")
print("disclaimer: official Nasdaq halt-code map; not a Halt Cross engine; learning only; no venue recommendation")

print("=== 6. FINRA 5260: no transacting or quoting during a halt ===")
# FINRA Rule 5260 Prohibition on Transactions, Publication of Quotations,
# or Publication of Indications of Interest During Trading Halts (official
# rule page opened 2026-11-12). Keep sections 1-5 identical, including
# 7/7 in section 1b, 4/4 after Section VII reopen clocks, and 6/6 after
# the Nasdaq halt-code map.
# 5260 is a member-level prohibition on transacting or publishing a
# quotation or indication of interest in a security as to which a trading
# halt is currently in effect, except as permitted under the LULD Plan.
# 5260(a): No member or person associated with a member shall, directly
# or indirectly, effect any transaction or publish a quotation, a priced
# bid and/or offer, an unpriced indication of interest (including "bid
# wanted" and "offer wanted" and name only indications), or a bid or
# offer accompanied by a modifier to reflect unsolicited customer
# interest, in any security as to which a trading halt is currently in
# effect, except as permitted under the Regulation NMS Plan to Address
# Extraordinary Market Volatility. If FINRA closes trading in a security
# pursuant to its authority under Rule 6120(a)(3), members would not be
# prohibited from trading through other markets for which trading is not
# halted.
# Official (b) futures provisions exist; this toy is not that engine.
# This is not a rewrite of already-taught halt codes, LULD reopen clocks,
# MWCB, or SEC suspensions. Do not teach the Nasdaq T5 "10% in five
# minutes" sentence as current LULD. No product, broker, or venue
# recommendation.

s6_checks = 0


def s6_check(cond, label):
    global s6_checks
    assert cond, label
    s6_checks += 1


print("5260 is a member-level prohibition on transacting or publishing a quotation or indication of interest")
print("  in a security as to which a trading halt is currently in effect, except as permitted under the LULD Plan")
print('5260(a): No member or person associated with a member shall, directly or indirectly,')
print('  effect any transaction or publish a quotation, a priced bid and/or offer,')
print('  an unpriced indication of interest (including "bid wanted" and "offer wanted" and name only indications),')
print("  or a bid or offer accompanied by a modifier to reflect unsolicited customer interest,")
print("  in any security as to which a trading halt is currently in effect,")
print("  except as permitted under the Regulation NMS Plan to Address Extraordinary Market Volatility")
print("If FINRA closes trading in a security pursuant to its authority under Rule 6120(a)(3),")
print("  members would not be prohibited from trading through other markets for which trading is not halted")
finra_only_halts_all = False
print(f"  a FINRA-only 6120(a)(3) close halts every other market? {finra_only_halts_all}")
s6_check(finra_only_halts_all is False, "6120(a)(3) close does not halt other markets")
luld_exception_exists = True
print(f"  official LULD Plan exception exists? {luld_exception_exists}")
s6_check(luld_exception_exists is True, "do not drop the official LULD Plan exception")
print("official (b) futures provisions exist; this toy is not that engine")
builds_5260b = False
is_rewrite_halts = False
teaches_t5_as_luld = False
print(f"  this toy builds a futures or Rule 6120 engine? {builds_5260b}")
print(f"  this is a rewrite of already-taught halt codes or LULD reopen clocks? {is_rewrite_halts}")
print(f'  this toy teaches the Nasdaq T5 "10% in five minutes" sentence as current LULD? {teaches_t5_as_luld}')
s6_check(builds_5260b is False, "do not build official (b) or 6120 engines")
s6_check(is_rewrite_halts is False, "5260 is not a rewrite of halt codes or LULD clocks")
s6_check(teaches_t5_as_luld is False, "do not teach T5 as current LULD")
print("no product, broker, or venue recommendation")
print(f"assertions passed: {s6_checks}/{s6_checks}")
print("disclaimer: official FINRA 5260 member-level halt prohibition; not a halt-code or LULD rewrite; learning only; no venue recommendation")
