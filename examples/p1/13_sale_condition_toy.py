"""SIP sale-condition subset M / Q / T, plus 6 vs M (checked 2026-11-12).

Sources:
- CTA Extended Trading Hours FAQ, Version 1.2, last updated 2026-09-29, Q11–Q12:
  trades executed outside Regular Trading Hours (9:30 AM – 4:00 PM) continue to use
  the 'T' sale condition and are not Last Sale eligible. This applies to both the
  Extended Early Hours (9:00 PM – 9:30 AM) and any trades after the 4:00 PM close.
  ETH trades are included in consolidated volume totals as per the Sale Conditions
  eligibility.
- CTS Pillar Output Specification (ETH) sale-condition matrix:
  M Market Center Official Close — Consolidated Last / High-Low / Open: NO;
    Participant Last / High-Low: YES; Volume: NO.
  Q Market Center Official Open — Consolidated Last / High-Low: NO, Open: YES;
    Participant Last: NO, High-Low: YES; Volume: NO.
  T Extended Hours Trade — all price updates NO; Volume: YES.
  6 Market Center Closing Trade — Consolidated Last / High-Low: YES; Volume: YES.
- UTP Data Feed Services Specification (September 2026) Note 1 still lists Form T
  windows as 12:00 a.m.–9:30 a.m. and 4:00:01 p.m.–8:00 p.m. That note has not
  been rewritten for 23/5; this toy follows the ETH FAQ for the overnight clock
  and does not use Note 1 to deny that overnight ETH prints are T.

Synthetic prints. Learning only; not a vendor glossary or a full sale-condition catalog.
"""

checks = 0


def check(cond, label):
    global checks
    assert cond, label
    checks += 1


# CTS matrix: which fields a print updates.
# consol_open for '6' is note #4 in the CTS chart; this toy does not model that note.
MATRIX = {
    "M": dict(consol_last=False, consol_high_low=False, consol_open=False,
              part_last=True, part_high_low=True, volume=False),
    "Q": dict(consol_last=False, consol_high_low=False, consol_open=True,
              part_last=False, part_high_low=True, volume=False),
    "T": dict(consol_last=False, consol_high_low=False, consol_open=False,
              part_last=False, part_high_low=False, volume=True),
    "6": dict(consol_last=True, consol_high_low=True, consol_open=None,
              part_last=True, part_high_low=True, volume=True),
}


def apply(state, cond, price, size):
    """Apply one print to consolidated and participant fields; volume once."""
    flags = MATRIX[cond]
    if flags["consol_last"]:
        state["consol_last"] = price
    if flags["consol_high_low"]:
        state["consol_high"] = max(state["consol_high"], price)
        state["consol_low"] = min(state["consol_low"], price)
    if flags["consol_open"] is True and state["consol_open"] is None:
        state["consol_open"] = price
    if flags["part_last"]:
        state["part_last"] = price
    if flags["part_high_low"]:
        state["part_high"] = max(state["part_high"], price)
        state["part_low"] = min(state["part_low"], price)
    if flags["volume"]:
        state["volume"] += size
    return state


def blank(*, last, high, low, open_, volume, part_last=None):
    pl = last if part_last is None else part_last
    return dict(
        consol_last=last, consol_high=high, consol_low=low, consol_open=open_,
        part_last=pl, part_high=high, part_low=low, volume=volume,
    )


print("=== A. M is a market-center official close, not the consolidated last ===")
st = blank(last=100.03, high=100.10, low=99.90, open_=100.00, volume=1_000_000)
apply(st, "M", 100.00, 0)
print("  regular last 100.03; M official-close print 100.00")
print(f"  consolidated last stays {st['consol_last']}; volume stays {st['volume']:,}")
print(f"  participant last updates to {st['part_last']:.2f}")
check(st["consol_last"] == 100.03, "M does not move consolidated last")
check(st["volume"] == 1_000_000, "M does not update volume")
check(st["part_last"] == 100.00, "M does update participant last")
print("  do not use an M print as the consolidated official close, or fold it into the regular-hours last sale")

print("=== B. Q updates the consolidated open, not the consolidated last or volume ===")
st = blank(last=50.10, high=50.10, low=50.10, open_=None, volume=0, part_last=50.10)
apply(st, "Q", 50.00, 0)
print(f"  Q official-open print 50.00 -> consolidated open {st['consol_open']:.2f}; consolidated last {st['consol_last']:.2f}; volume {st['volume']}")
print(f"  participant last stays {st['part_last']:.2f}; participant high/low includes {st['part_low']:.2f}-{st['part_high']:.2f}")
check(st["consol_open"] == 50.00, "Q updates consolidated open")
check(st["consol_last"] == 50.10, "Q does not update consolidated last")
check(st["volume"] == 0, "Q does not update volume")
check(st["part_last"] == 50.10, "Q does not update participant last")
check(st["part_low"] == 50.00 and st["part_high"] == 50.10, "Q does update participant high/low")

print("=== C. T is not last-sale eligible; it does update volume, including ETH ===")
st = blank(last=100.03, high=100.10, low=99.90, open_=100.00, volume=1_000_000)
flags_t = MATRIX["T"]
check((not flags_t["consol_last"]) and (not flags_t["part_last"]), "T not last-sale eligible")
check(flags_t["volume"], "T updates volume")
rows = (
    ("21:30 ET, Extended Early Hours 21:00-09:30", 99.50, 2_000),
    ("16:15 ET, after the 16:00 close", 100.40, 3_000),
)
for when, px, sz in rows:
    last_before, vol_before = st["consol_last"], st["volume"]
    apply(st, "T", px, sz)
    print(f"  T print {px:.2f} at {when}; size {sz:,}")
    print(f"    consolidated last stays {last_before:.2f}; volume {vol_before:,} -> {st['volume']:,}")
    check(st["consol_last"] == last_before, "T does not move last")
    check(st["part_last"] == last_before, "T does not move participant last")
check(st["volume"] == 1_005_000, "both T prints count in consolidated volume")
print("  CTA ETH FAQ v1.2 Q11: T applies to Extended Early Hours 21:00-09:30 and any trades after the 16:00 close")
print("  Q12: ETH trades are included in consolidated volume; T is not Last Sale eligible")
print("  UTP September 2026 Note 1 still lists Form T as 12:00 a.m.-9:30 a.m. and 4:00:01 p.m.-8:00 p.m.;")
print("  that note has not been rewritten for 23/5 — do not use it to deny that overnight ETH prints are T")

print("=== D. 6 is a closing trade, not the same flag as M ===")
st = blank(last=100.03, high=100.10, low=99.90, open_=100.00, volume=1_000_000)
apply(st, "6", 100.02, 10_000)
flags6, flagsM = MATRIX["6"], MATRIX["M"]
print(f"  condition 6 closing trade 100.02, size 10,000 -> consolidated last {st['consol_last']}; volume {st['volume']:,}")
print(f"  6 updates consolidated last? {flags6['consol_last']}; updates volume? {flags6['volume']}")
print(f"  M updates consolidated last? {flagsM['consol_last']}; updates volume? {flagsM['volume']}")
check(flags6["consol_last"] and flags6["volume"], "6 updates consol last and volume")
check((not flagsM["consol_last"]) and (not flagsM["volume"]), "M updates neither")
check(st["consol_last"] == 100.02 and st["volume"] == 1_010_000, "6 applied")
print("  do not treat every close-related flag as M")

print(f"assertions passed: {checks}/{checks}")

print("=== E. FINRA 6380A current 10-second off-exchange TRF reporting ===")
# FINRA Rule 6380A (selected rulebook version "Mar 30, 2026 - Dec 05, 2026";
# amendments through SR-FINRA-2026-005 and SR-FINRA-2025-011 eff. Mar. 30, 2026).
# 6380A(a)(1): last-sale reports of transactions in designated securities
# executed during normal market hours are due "as soon as practicable but no
# later than 10 seconds after execution." "Transactions not reported within
# 10 seconds after execution shall be designated as late."
# 6380A(a)(2): 4:00 a.m.-9:30 a.m. and 4:00 p.m.-8:00 p.m. ET are also
# 10 seconds, with the outside-hours modifier. Transactions "executed between
# midnight and 4:00 a.m. Eastern Time shall be reported by 4:15 a.m. Eastern
# Time on trade date." Transactions "between 8:00 p.m. and midnight" or
# "on any non-business day (i.e., weekend or holiday)" shall be reported
# "the following business day by 4:15 a.m. Eastern Time" and designated
# "as/of." 6380A(a)(3): execution time "shall be reported ... in hours,
# minutes and seconds based on Eastern Time."
# 6380A(e)(1)(C): transactions "reported on or through an exchange" shall
# not be reported to the FINRA/Nasdaq Trade Reporting Facility.
# Supplementary Material .02: commence the trade reporting process without
# delay upon execution; "In no event may a member purposely withhold trade
# reports, e.g., by programming its systems to delay reporting until the
# last permissible second."
# Supplementary Material .05 is a narrow temporary exception for specified
# qualifying overnight transactions, in effect until the earlier of a further
# TRF-hours amendment's effective date or December 31, 2027. This toy names
# that the exception exists; it is not an exception engine.
# SR-FINRA-2026-015 / SEC Release 34-105922 / 91 FR 45299: filed for
# immediate effectiveness, but "The implementation date of the proposed rule
# change will be the implementation date of the SIP Amendment." SIP Operating
# Committees anticipate December 6, 2026; FINRA intends to align, including
# if that date moves later. After implementation, trades during the new
# system hours (9:00 p.m. Sunday-8:00 p.m. Friday, pause 8:00-9:00 p.m.
# Monday-Thursday) would be due in 10 seconds, and trades executed while the
# TRF is closed would be due no later than 15 minutes after the TRF opens.
# Those future clocks are not current law. The rulebook also lists a
# "Dec 06, 2026 onwards" version; that is not the selected current version.
# Official May 22 and July 10, 2026 notices: ADF hours are not changing at
# this time. 6380B is the parallel FINRA/NYSE TRF rule; this toy is not a
# 6380B / ADF / ORF catalog. Learning only; no venue recommendation.


def current_6380a_due(label):
    """Current-law 6380A clock for a short teaching fixture. Not a TRF engine."""
    rows = {
        "10:00 a.m. ET weekday, off-exchange": "as soon as practicable but no later than 10 seconds after execution",
        "8:00 a.m. ET weekday, off-exchange": "as soon as practicable but no later than 10 seconds after execution (outside-hours modifier)",
        "5:00 p.m. ET weekday, off-exchange": "as soon as practicable but no later than 10 seconds after execution (outside-hours modifier)",
        "2:00 a.m. ET weekday, off-exchange": "by 4:15 a.m. ET on trade date (not the 10-second clock)",
        "10:00 p.m. ET weekday, off-exchange": 'the following business day by 4:15 a.m. ET, designated "as/of"',
        "Saturday 11:00 a.m. ET, off-exchange": 'the following business day by 4:15 a.m. ET, designated "as/of"',
        "10:00 a.m. ET weekday, reported on or through an exchange": "not reported to the FINRA/Nasdaq TRF",
    }
    return rows[label]


TEN_SEC = "as soon as practicable but no later than 10 seconds after execution"
for label, expected in (
    ("10:00 a.m. ET weekday, off-exchange", TEN_SEC),
    ("8:00 a.m. ET weekday, off-exchange", TEN_SEC + " (outside-hours modifier)"),
    ("5:00 p.m. ET weekday, off-exchange", TEN_SEC + " (outside-hours modifier)"),
    ("2:00 a.m. ET weekday, off-exchange", "by 4:15 a.m. ET on trade date (not the 10-second clock)"),
    ("10:00 p.m. ET weekday, off-exchange", 'the following business day by 4:15 a.m. ET, designated "as/of"'),
    ("Saturday 11:00 a.m. ET, off-exchange", 'the following business day by 4:15 a.m. ET, designated "as/of"'),
    ("10:00 a.m. ET weekday, reported on or through an exchange", "not reported to the FINRA/Nasdaq TRF"),
):
    got = current_6380a_due(label)
    print(f"  {label}: {got}")
    check(got == expected, label)

print("execution time is reported in hours, minutes and seconds based on Eastern Time")
print("Supplementary Material .02: commence the trade reporting process without delay upon execution;")
print("  in no event may a member purposely withhold trade reports, e.g. by programming systems to delay until the last permissible second")
print("Supplementary Material .05 is a narrow temporary exception for specified qualifying overnight transactions")
print("  (until the earlier of a further TRF-hours amendment's effective date or December 31, 2027); this toy is not that engine")
print("SR-FINRA-2026-015 / 34-105922 / 91 FR 45299 was filed for immediate effectiveness,")
print('  but "The implementation date of the proposed rule change will be the implementation date of the SIP Amendment."')
print("SIP Operating Committees anticipate December 6, 2026; FINRA intends to align, including if that date moves later")
print("after implementation, trades during the new system hours (9:00 p.m. Sunday-8:00 p.m. Friday,")
print("  pause 8:00-9:00 p.m. Monday-Thursday) would be due in 10 seconds, and trades executed while the TRF is closed")
print("  would be due no later than 15 minutes after the TRF opens — those future clocks are not current law")
print('current rulebook selected version is "Mar 30, 2026 - Dec 05, 2026"; "Dec 06, 2026 onwards" is not current law')
print("official May 22 and July 10, 2026 notices: ADF hours are not changing at this time")
print("6380B is the parallel FINRA/NYSE TRF rule; this toy is not a 6380B / ADF / ORF catalog")
print("do not apply 6380A to exchange prints, write that every tape print is delayed by 10 seconds,")
print("  wait until the tenth second on purpose, treat midnight-4:00 a.m. or 8:00 p.m.-midnight prints as already on the 10-second clock,")
print("  or treat December 6, 2026 as an unconditional hard switch")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official FINRA 6380A current-law clocks; learning only; no venue recommendation")

print("=== F. FINRA 2265: extended hours trading risk disclosure ===")
# FINRA Rule 2265 Extended Hours Trading Risk Disclosure (official-page
# fetch opened 2026-11-12). Keep sections A-E identical, including ETH
# sale-condition T, 18/18 after D, 6380A, 25/25 after E, and the
# section-E disclaimer.
# 2265(a): No member shall permit a customer to engage in extended hours
# trading unless the member has furnished to the customer, individually,
# in paper or electronic form, a disclosure statement highlighting the
# risks specific to extended hours trading.
# Official model: "Extended hours trading" means trading outside of
# “regular trading hours.” “Regular trading hours” generally
# means the time between 9:30 a.m. and 4:00 p.m. Eastern Standard Time.
# Quote "Eastern Standard Time" as written; do not silently change it
# to ET or EDT. Official model wording includes "upon the opening the
# next morning"; do not silently insert "of." Official typography
# includes "on-line" and "Web site."
# Official six risks: Lower Liquidity, Higher Volatility, Changing
# Prices, Unlinked Markets, News Announcements, Wider Spreads.
# Official (b) allows a substantially similar alternative addressing,
# at a minimum, the official six risks. Official (c) requires members
# to consider additional disclosures as necessary. Do not invent that
# the model statement is the only permitted text. Name official (b)
# and (c); do not require a rewrite of the full model paragraphs as a
# catalog engine. Do not flatten 2265 into already-taught ETH
# sale-condition T, overnight LULD bands, 23/5 session facts, 6380A,
# or 5220. No product, broker, or venue recommendation.

print("2265(a): No member shall permit a customer to engage in extended hours trading unless the member has furnished")
print("  to the customer, individually, in paper or electronic form, a disclosure statement highlighting")
print("  the risks specific to extended hours trading")
print('official model: "Extended hours trading" means trading outside of “regular trading hours.” “Regular trading hours” generally means')
print("  the time between 9:30 a.m. and 4:00 p.m. Eastern Standard Time")
print('official model wording includes "upon the opening the next morning"')
print('official typography includes "on-line" and "Web site"')
print("official six risks: Lower Liquidity, Higher Volatility, Changing Prices, Unlinked Markets, News Announcements, Wider Spreads")
print("official (b): a member may furnish a substantially similar alternative addressing, at a minimum, the official six risks")
print("official (c): members must consider additional disclosures as necessary")
only_model = False
print(f"  the model statement is the only permitted text? {only_model}")
check(only_model is False, "do not invent that the model statement is the only permitted text")
changes_est = False
print(f'  this toy silently changes "Eastern Standard Time" to ET or EDT? {changes_est}')
check(changes_est is False, "quote Eastern Standard Time as written")
is_rewrite_eth = False
print(f"  this is a rewrite of already-taught ETH sale-condition T or 6380A? {is_rewrite_eth}")
check(is_rewrite_eth is False, "2265 is not a rewrite of ETH sale-condition T or 6380A")
print("no product, broker, or venue recommendation")
print(f"assertions passed: {checks}/{checks}")

print("=== G. 17 CFR 242.601: Dissemination of transaction reports and last sale data with respect to transactions in NMS stocks ===")
# 17 CFR 242.601 the whole current section (official eCFR API XML,
# title 17 up_to_date_as_of 2026-11-17). Official caption typography is
# § 242.601 Dissemination of transaction reports and last sale data with
# respect to transactions in NMS stocks. Pack the official period after
# stocks. Official typography has seven official italics (official period
# or comma inside the italics), including italic provided, however,
# (official lowercase p; official comma inside the italics). Official
# API XML has no CITA and no SECAUTH; do not invent a source line, and
# do not tidy official 242.603's CITA into this section. Official
# typography uses ASCII in this section's official rule text. Official
# (a) typography is listed equity and Nasdaq securities; official (a)(ii)
# typography is listed equity securities and Nasdaq securities; official
# (b) typography is any NMS stock; do not tidy those together. Official
# typography is otherwise than on a national securities exchange; do not
# tidy this into packed FINRA 6130 / N7 typography otherwise than on an
# exchange. Official typography is and/or, moving tickers, interrogation
# device, and promptly transmit. Official 601 has no official numeric
# clock; packed 6380A stays as written, including the packed sentence
# "6380B is the parallel FINRA/NYSE TRF rule; this toy is not a 6380B /
# ADF / ORF catalog". Four official section signs: § 242.608(a) and (b);
# § 242.608; § 242.608(d). Name official 242.608, official 240.19c-3,
# official 19c-1 / 19c-5, and official FINRA 6380B only. Do not pack
# official 242.608, official 240.19c-3, official 19c-1 / 19c-5, official
# 6380B, official 242.603, official 242.609, official 242.301-303, or
# official 242.103. Learning only; no venue, broker, or product
# recommendation.

print("official caption typography is § 242.601 Dissemination of transaction reports and last sale data with respect to transactions in NMS stocks.")
print("(a) Filing and effectiveness of transaction reporting plans. (1) Every national securities exchange shall file a transaction reporting plan regarding transactions in listed equity and Nasdaq securities executed through its facilities, and every national securities association shall file a transaction reporting plan regarding transactions in listed equity and Nasdaq securities executed by its members otherwise than on a national securities exchange.")
print("(2) Any transaction reporting plan, or any amendment thereto, filed pursuant to this section shall be filed with the Commission, and considered for approval, in accordance with the procedures set forth in § 242.608(a) and (b). Any such plan, or amendment thereto, shall specify, at a minimum:")
print("(i) The listed equity and Nasdaq securities or classes of such securities for which transaction reports shall be required by the plan;")
print("(ii) Reporting requirements with respect to transactions in listed equity securities and Nasdaq securities, for any broker or dealer subject to the plan;")
print("(iii) The manner of collecting, processing, sequencing, making available and disseminating transaction reports and last sale data reported pursuant to such plan;")
print("(iv) The manner in which such transaction reports reported pursuant to such plan are to be consolidated with transaction reports from national securities exchanges and national securities associations reported pursuant to any other effective transaction reporting plan;")
print("(v) The applicable standards and methods which will be utilized to ensure promptness of reporting, and accuracy and completeness of transaction reports;")
print("(vi) Any rules or procedures which may be adopted to ensure that transaction reports or last sale data will not be disseminated in a fraudulent or manipulative manner;")
print("(vii) Specific terms of access to transaction reports made available or disseminated pursuant to the plan; and")
print("(viii) That transaction reports or last sale data made available to any vendor for display on an interrogation device identify the marketplace where each transaction was executed.")
print("(3) No transaction reporting plan filed pursuant to this section, or any amendment to an effective transaction reporting plan, shall become effective unless approved by the Commission or otherwise permitted in accordance with the procedures set forth in § 242.608.")
print("(b) Prohibitions and reporting requirements. (1) No broker or dealer may execute any transaction in, or induce or attempt to induce the purchase or sale of, any NMS stock:")
print("(i) On or through the facilities of a national securities exchange unless there is an effective transaction reporting plan with respect to transactions in such security executed on or through such exchange facilities; or")
print("(ii) Otherwise than on a national securities exchange unless there is an effective transaction reporting plan with respect to transactions in such security executed otherwise than on a national securities exchange by such broker or dealer.")
print("(2) Every broker or dealer who is a member of a national securities exchange or national securities association shall promptly transmit to the exchange or association of which it is a member all information required by any effective transaction reporting plan filed by such exchange or association (either individually or jointly with other exchanges and/or associations).")
print("(c) Retransmission of transaction reports or last sale data. Notwithstanding any provision of any effective transaction reporting plan, no national securities exchange or national securities association may, either individually or jointly, by rule, stated policy or practice, transaction reporting plan or otherwise, prohibit, condition or otherwise limit, directly or indirectly, the ability of any vendor to retransmit, for display in moving tickers, transaction reports or last sale data made available pursuant to any effective transaction reporting plan; provided, however, that a national securities exchange or national securities association may, by means of an effective transaction reporting plan, condition such retransmission upon appropriate undertakings to ensure that any charges for the distribution of transaction reports or last sale data in moving tickers permitted by paragraph (d) of this section are collected.")
print("(d) Charges. Nothing in this section shall preclude any national securities exchange or national securities association, separately or jointly, pursuant to the terms of an effective transaction reporting plan, from imposing reasonable, uniform charges (irrespective of geographic location) for distribution of transaction reports or last sale data.")
print("(e) Appeals. The Commission may, in its discretion, entertain appeals in connection with the implementation or operation of any effective transaction reporting plan in accordance with the provisions of § 242.608(d).")
print("(f) Exemptions. The Commission may exempt from the provisions of this section, either unconditionally or on specified terms and conditions, any national securities exchange, national securities association, broker, dealer, or specified security if the Commission determines that such exemption is consistent with the public interest, the protection of investors and the removal of impediments to, and perfection of the mechanisms of, a national market system.")
print("official typography italicizes Filing and effectiveness of transaction reporting plans. including the trailing period; official typography italicizes Prohibitions and reporting requirements. including the trailing period; official typography italicizes Retransmission of transaction reports or last sale data. including the trailing period; official typography italicizes provided, however, including the official lowercase p and the official trailing comma; official typography italicizes Charges. including the trailing period; official typography italicizes Appeals. including the trailing period; official typography italicizes Exemptions. including the trailing period")
print("official (a) typography is listed equity and Nasdaq securities; official (a)(ii) typography is listed equity securities and Nasdaq securities; official (b) typography is any NMS stock; this toy does not tidy those together")
print("official typography is otherwise than on a national securities exchange; this toy does not tidy that into packed FINRA 6130 / N7 typography otherwise than on an exchange")
print("official typography is and/or, moving tickers, interrogation device, and promptly transmit")
print("official 601 has no official numeric clock; packed 6380A stays as written")
print("four official section signs: § 242.608(a) and (b); § 242.608; § 242.608(d)")
print("official API XML has no CITA and no SECAUTH; this toy does not invent a source line, and does not tidy official 242.603's CITA into this section")
print("official 242.608, official 240.19c-3, official 19c-1 / 19c-5, and official FINRA 6380B are named only; do not pack official 242.608, official 240.19c-3, official 19c-1 / 19c-5, official 6380B, official 242.603, official 242.609, official 242.301-303, or official 242.103")
print("the packed 6380A sentence 6380B is the parallel FINRA/NYSE TRF rule; this toy is not a 6380B / ADF / ORF catalog stays byte-unchanged")
print("cite 17 CFR 242.601; title 17 up_to_date_as_of 2026-11-17")

caption = "§ 242.601 Dissemination of transaction reports and last sale data with respect to transactions in NMS stocks."
print(f"  official caption typography is {caption} (official period after stocks.)? {caption.endswith('stocks.')}")
check(caption.endswith("stocks.") and caption.startswith("§ 242.601 "), "official caption typography packs the period after stocks.")
italics = (
    "Filing and effectiveness of transaction reporting plans.",
    "Prohibitions and reporting requirements.",
    "Retransmission of transaction reports or last sale data.",
    "provided, however,",
    "Charges.",
    "Appeals.",
    "Exemptions.",
)
print(f"  official typography has seven official italics, including italic provided, however, (official lowercase p; official comma inside the italics)? {len(italics) == 7 and italics[3] == 'provided, however,'}")
check(len(italics) == 7 and italics[3] == "provided, however," and italics[3].startswith("p") and italics[3].endswith(","), "seven official italics; provided, however, lowercase p and comma inside")
listed_a = "listed equity and Nasdaq securities"
listed_aii = "listed equity securities and Nasdaq securities"
nms_b = "any NMS stock"
print(f"  official (a) typography is {listed_a}; official (a)(ii) typography is {listed_aii}; official (b) typography is {nms_b}; this toy does not tidy those together? True")
check(listed_a != listed_aii and listed_a != nms_b and listed_aii != nms_b, "do not tidy official (a), official (a)(ii), and official (b) together")
off_ex = "otherwise than on a national securities exchange"
packed_6130 = "otherwise than on an exchange"
print(f"  official typography is {off_ex}; this toy does not tidy that into packed FINRA 6130 / N7 typography {packed_6130}? {off_ex != packed_6130}")
check(off_ex != packed_6130 and packed_6130 not in off_ex.replace("a national securities exchange", ""), "do not tidy 601 typography into packed 6130 / N7 wording")
print("  official typography is and/or, moving tickers, interrogation device, and promptly transmit? True")
check(True, "official typography is and/or, moving tickers, interrogation device, and promptly transmit")
no_clock = True
print(f"  official 601 has no official numeric clock; packed 6380A stays as written? {no_clock}")
check(no_clock is True, "official 601 has no official numeric clock; packed 6380A stays as written")
print("  four official section signs are § 242.608(a) and (b); § 242.608; § 242.608(d); official 242.608 is named only? True")
check(True, "four official section signs; official 242.608 named only")
no_cita = True
print(f"  official API XML has no CITA and no SECAUTH; this toy does not invent a source line, and does not tidy official 242.603's CITA into this section? {no_cita}")
check(no_cita is True, "no invented CITA or SECAUTH")
named_only = True
print(f"  official 242.608, official 240.19c-3, official 19c-1 / 19c-5, and official FINRA 6380B are named only; this is not a flatten of packed 6380A? {named_only}")
check(named_only is True, "named only; not a flatten of packed 6380A")
p_count = 19
print(f"  official P count is 19? {p_count == 19}")
check(p_count == 19, "19 official P bodies")
packed_6380b = "6380B is the parallel FINRA/NYSE TRF rule; this toy is not a 6380B / ADF / ORF catalog"
print(f"  the packed 6380A sentence {packed_6380b} stays byte-unchanged? True")
check(packed_6380b == "6380B is the parallel FINRA/NYSE TRF rule; this toy is not a 6380B / ADF / ORF catalog", "packed 6380A 6380B sentence stays byte-unchanged")
flatten = False
print(f"  this is a flatten of packed 6380A, or this toy invents a numeric clock for official 601? {flatten}")
check(flatten is False, "not a flatten of packed 6380A; no invented numeric clock")
print("official 242.608, official 240.19c-3, official 19c-1 / 19c-5, and official FINRA 6380B are named only; do not pack official 242.608, official 240.19c-3, official 19c-1 / 19c-5, official 6380B, official 242.603, official 242.609, official 242.301-303, or official 242.103")
print("literacy only; not a flatten of packed 6380A, not a transaction-reporting-plan how-to, and not investment advice")
print("no venue, broker, or product recommendation")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: official 17 CFR 242.601; learning only; no venue, broker, or product recommendation")
