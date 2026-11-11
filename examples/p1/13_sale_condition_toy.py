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
