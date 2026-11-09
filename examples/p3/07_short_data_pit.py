"""Short-side public data: point-in-time alignment toy (checked 2026-11-10).

Three different public datasets, three different meanings:
  1. FINRA short interest (Rule 4560): a STOCK of open short positions,
     reported twice a month, published ~7 business days after the
     settlement date. Align by PUBLISH date, never by settlement date.
  2. FINRA daily short sale volume: a FLOW of short-sale trades reported to
     FINRA's TRF/ADF/ORF only (off-exchange). Not short interest.
  3. SEC fails-to-deliver (FTD): an outstanding BALANCE at NSCC CNS, not a
     daily amount, and not evidence of naked short selling.
Dates below are from FINRA's published 2026 short interest schedule; all
positions/volumes are synthetic. Learning only, not investment advice.
"""
from datetime import date

# (settlement date, FINRA publish date) from FINRA's 2026 schedule
SCHEDULE = [
    (date(2026, 9, 30), date(2026, 10, 9)),
    (date(2026, 10, 15), date(2026, 10, 26)),
    (date(2026, 10, 30), date(2026, 11, 10)),
]
SYNTH_SHORT_INTEREST = {  # settlement date -> synthetic shares short
    date(2026, 9, 30): 1_000_000,
    date(2026, 10, 15): 1_400_000,
    date(2026, 10, 30): 1_250_000,
}


def asof_join(signal_date):
    """Latest snapshot whose PUBLISH date is on or before signal_date."""
    usable = [(s, p) for s, p in SCHEDULE if p <= signal_date]
    if not usable:
        return None
    s, p = max(usable, key=lambda sp: sp[1])
    return s, p, SYNTH_SHORT_INTEREST[s]


def naive_join(signal_date):
    """WRONG: aligns by settlement date (look-ahead)."""
    s = max(s for s, _ in SCHEDULE if s <= signal_date)
    return s, SYNTH_SHORT_INTEREST[s]


def short_ratio(short_vol, total_vol):
    return short_vol / total_vol


def ftd_new_fails(balance_prev, balance_today):
    """A running balance cannot tell you how many NEW fails occurred."""
    return "unknown"


RULE_STATUS = {"SR-FINRA-2026-012": "withdrawn 2026-08-05"}
CURRENT_FREQUENCY = "twice monthly"

checks = 0
print("=== 1. short interest: publish-date alignment ===")
for s, p in SCHEDULE:
    print(f"settlement {s} -> published {p}")
sig = date(2026, 10, 23)
s, p, v = asof_join(sig)
ns, nv = naive_join(sig)
print(f"signal {sig}: point-in-time uses settlement {s} (published {p}), shares short {v:,}")
print(f"signal {sig}: naive join would use settlement {ns} (not public until 2026-10-26) -> look-ahead")
assert s == date(2026, 9, 30) and p == date(2026, 10, 9); checks += 1
assert ns == date(2026, 10, 15) and ns != s; checks += 1
assert asof_join(date(2026, 11, 10))[0] == date(2026, 10, 30); checks += 1

print("=== 2. daily short sale volume is off-exchange only ===")
off = short_ratio(3000, 15000)
comb = short_ratio(3000 + 12000, 15000 + 125000)
print(f"off-exchange only: 3,000 / 15,000 = {off:.2f}")
print(f"with exchange volume added: 15,000 / 140,000 = {comb:.4f}  (FINRA notice example: 10.7%)")
assert abs(off - 0.20) < 1e-12; checks += 1
assert abs(comb - 0.1071) < 1e-4; checks += 1

print("=== 3. FTD is a balance, not a daily flow ===")
r = ftd_new_fails(100, 100)
print(f"balance 100 -> 100: new fails today = {r} (could be 0, or 100 settled and 100 new)")
assert r == "unknown"; checks += 1

print("=== 4. proposal is not rule ===")
print(f"SR-FINRA-2026-012 (weekly reporting): {RULE_STATUS['SR-FINRA-2026-012']}; current: {CURRENT_FREQUENCY}")
assert RULE_STATUS["SR-FINRA-2026-012"].startswith("withdrawn"); checks += 1
assert CURRENT_FREQUENCY == "twice monthly"; checks += 1

print(f"assertions passed: {checks}/8")
assert checks == 8
print("ASSERT_short_data_pit_ok")
print("disclaimer: synthetic positions/volumes; real FINRA schedule dates; no squeeze signals; learning only")
