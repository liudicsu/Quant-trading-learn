"""SEC XBRL "companyfacts"-style records as point-in-time data, and Rule 10b5-1 plan flags on Form 4
(checked 2026-11-11).

Sources:
- SEC, "EDGAR Application Programming Interfaces": data.sec.gov serves JSON without API keys; the
  companyconcept / companyfacts APIs aggregate XBRL facts across filings; the frames API returns ONE fact
  per company and period, "last filed". Fair access: no more than 10 requests per second (SEC Developer
  Resources) and a declared User-Agent.
- The four FACTS below are copied from https://data.sec.gov/api/xbrl/companyconcept/CIK0000320193/us-gaap/
  NetIncomeLoss.json (Apple Inc., fiscal year 2008-09-28..2009-09-26), read on 2026-11-11. The original
  10-K (filed 2009-10-27) reported 5,704 million; the 10-K/A filed 2010-01-25 reported 8,235 million for the
  same fiscal year. This script does not fetch anything.
- 17 CFR 240.10b5-1(c)(1)(ii)(B) (eCFR, current; amended 2022-12-29 / 2023-02-27): directors and officers may
  not trade under a new plan until the later of 90 days after adoption or two business days after the
  10-Q/10-K for the fiscal quarter of adoption is disclosed, capped at 120 days; other persons (not the
  issuer): 30 days.
- SEC Form 4 Instruction 10 and press release 2022-222: a check box marks a transaction made under a plan
  intended to satisfy Rule 10b5-1(c), with the adoption date; required for Forms 4/5 filed on or after
  2023-04-01.
Weekends only; no holidays (the example dates avoid them). Learning only; not a trading signal.
"""
from datetime import date, timedelta

checks = 0


def check(cond, label):
    global checks
    assert cond, label
    checks += 1


FACTS = [  # NetIncomeLoss, USD; fields as in the SEC JSON (val shortened to millions)
    {"start": "2008-09-28", "end": "2009-09-26", "val_m": 5704, "fy": 2009, "fp": "FY", "form": "10-K", "filed": "2009-10-27"},
    {"start": "2008-09-28", "end": "2009-09-26", "val_m": 8235, "fy": 2009, "fp": "FY", "form": "10-K/A", "filed": "2010-01-25"},
    {"start": "2008-09-28", "end": "2009-09-26", "val_m": 8235, "fy": 2010, "fp": "FY", "form": "10-K", "filed": "2010-10-27"},
    {"start": "2008-09-28", "end": "2009-09-26", "val_m": 8235, "fy": 2011, "fp": "FY", "form": "10-K", "filed": "2011-10-26", "frame": "CY2009"},
]


def as_of(facts, start, end, decision):
    """Latest fact for this exact period whose filing date is before the decision date."""
    known = [f for f in facts if f["start"] == start and f["end"] == end and f["filed"] < decision]
    return max(known, key=lambda f: f["filed"]) if known else None


print("=== A. one period, four filings: pick by 'filed', not by 'fy' or 'frame' ===")
for f in FACTS:
    print(f"  {f['form']:6s} filed {f['filed']} fy={f['fy']} fp={f['fp']} val={f['val_m']:,}m frame={f.get('frame', '-')}")
P = ("2008-09-28", "2009-09-26")
for dec in ("2009-10-20", "2009-11-02", "2010-02-01"):
    f = as_of(FACTS, *P, dec)
    print(f"decision {dec}: {('not yet filed' if f is None else str(f['val_m']) + 'm from ' + f['form'] + ' filed ' + f['filed'])}")
framed = [f for f in FACTS if f.get("frame") == "CY2009"][0]
print(f"frames API value for CY2009 = {framed['val_m']:,}m (the last filed); using it on 2009-11-02 = look-ahead of the amendment")
check(as_of(FACTS, *P, "2009-10-20") is None, "before the 10-K")
check(as_of(FACTS, *P, "2009-11-02")["val_m"] == 5704, "original value before the amendment")
check(as_of(FACTS, *P, "2010-02-01")["val_m"] == 8235, "amended value after 2010-01-25")
check(framed["val_m"] != as_of(FACTS, *P, "2009-11-02")["val_m"], "frame value differs from what was known")
print("'fy' describes the FILING (the 2011 10-K repeats FY2009 as a comparative); identify periods by start/end.")
check(sum(f["fy"] == 2009 for f in FACTS) == 2 and all(f["end"] == "2009-09-26" for f in FACTS), "fy is the filing's year")


def add_bd(d, n):
    while n:
        d += timedelta(days=1)
        if d.weekday() < 5:
            n -= 1
    return d


def cooling_off_end(adopted, periodic_report_filed, director_or_officer=True):
    """Last day of the Rule 10b5-1 cooling-off period (trading allowed after it ends)."""
    if not director_or_officer:
        return adopted + timedelta(days=30)
    later = max(adopted + timedelta(days=90), add_bd(periodic_report_filed, 2))
    return min(later, adopted + timedelta(days=120))


print("=== B. Rule 10b5-1 cooling-off (directors/officers: later of 90 days or 2 business days after the 10-Q/10-K, max 120) ===")
cases = [
    ("officer, adopted 2026-02-10, Q1 10-Q filed 2026-05-06", date(2026, 2, 10), date(2026, 5, 6), True),
    ("officer, adopted 2026-03-25, Q1 10-Q filed 2026-05-06", date(2026, 3, 25), date(2026, 5, 6), True),
    ("officer, adopted 2026-01-05, Q1 10-Q filed 2026-05-08", date(2026, 1, 5), date(2026, 5, 8), True),
    ("other insider (not D&O), adopted 2026-02-10", date(2026, 2, 10), date(2026, 5, 6), False),
]
out = {}
for label, a, r, dno in cases:
    out[label] = cooling_off_end(a, r, dno)
    print(f"  {label}: cooling-off ends {out[label]}")
check(out[cases[0][0]] == date(2026, 5, 11), "90 days binds")
check(out[cases[1][0]] == date(2026, 6, 23), "90 days after a late adoption")
check(out[cases[2][0]] == date(2026, 5, 5), "120-day cap binds (05-12 would exceed it)")
check(out[cases[3][0]] == date(2026, 3, 12), "30 days for others")

print("=== C. the Form 4 plan check box exists only for filings from 2023-04-01 ===")
CHECKBOX_FROM = "2023-04-01"
for filed, box in [("2022-11-15", None), ("2023-05-02", True), ("2024-08-20", False)]:
    if filed < CHECKBOX_FROM:
        label = "unknown (field did not exist; not the same as 'not a plan')"
    else:
        label = "plan trade" if box else "not marked as a plan trade"
    print(f"  Form 4 filed {filed}: {label}")
check("2022-11-15" < CHECKBOX_FROM <= "2023-05-02", "field availability date")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: real public numbers in A (Apple FY2009 NetIncomeLoss) are for PIT mechanics only; no insider-trading signal; learning only")
