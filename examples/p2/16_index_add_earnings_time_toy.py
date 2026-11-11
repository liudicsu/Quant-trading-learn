"""S&P 500 addition rules as of a date, the announcement timeline, and earnings release times as event
timestamps (checked 2026-11-11).

Sources:
- S&P Dow Jones Indices, "S&P U.S. Indices Methodology" (November 2026 edition), sections Eligibility
  Criteria, Index Maintenance, Index Policy and Appendix A:
  * evaluation date for S&P Composite 1500 eligibility = the open of trading two business days before the
    announcement date;
  * S&P 500: total company market cap >= US$22.7 billion (Appendix A: 18.0 bn after the close of 2024-04-01,
    20.5 bn after the close of 2025-01-02, 22.7 bn after the close of 2025-07-01); security float-adjusted
    market cap (FMC) >= 50% of that threshold; IWF >= 0.10; float-adjusted liquidity ratio >= 0.75; at least
    250,000 shares traded in each of the six months before the evaluation date; GAAP net income from
    continuing operations positive for the most recent quarter AND for the sum of the last four quarters;
    IPOs (and de-SPACs) need 12 months of trading;
  * constituent selection is at the Index Committee's discretion (sector balance is also considered); the
    criteria are for ADDITION, not continued membership; no scheduled reconstitution; additions and
    deletions are announced with at least three business days' notice, at 05:15 PM Eastern Time.
- SEC Form 8-K General Instruction B.1 and Item 2.02: an earnings release triggers an 8-K that states the
  date of the announcement and attaches the release; unless otherwise specified, an 8-K is due within four
  business days. 17 CFR 243.100 (Regulation FD): intentional disclosure to market professionals or holders
  must be made public simultaneously.
Dates in sections B and C are synthetic examples (no real company or real index change). Weekends only:
the example dates avoid US market holidays. Learning only; no claim about price moves around inclusion
and no earnings-trading strategy.
"""
from datetime import date, datetime, time, timedelta

checks = 0


def check(cond, label):
    global checks
    assert cond, label
    checks += 1


def add_bd(d, n):
    step = 1 if n > 0 else -1
    while n:
        d += timedelta(days=step)
        if d.weekday() < 5:
            n -= step
    return d


def bd_between(a, b):
    """Business days strictly after a and strictly before b."""
    n, d = 0, a + timedelta(days=1)
    while d < b:
        n += d.weekday() < 5
        d += timedelta(days=1)
    return n


# (effective after the close of this date, S&P 500 minimum total market cap in USD bn)
SP500_MIN_CAP = [(date(2024, 4, 1), 18.0), (date(2025, 1, 2), 20.5), (date(2025, 7, 1), 22.7)]


def min_cap(d):
    cap = None
    for eff, v in SP500_MIN_CAP:
        if d > eff:  # "after close" of the effective date
            cap = v
    if cap is None:
        raise ValueError(f"{d}: before this toy's table; read Appendix A")
    return cap


def sp500_screen(c, d):
    """Return a list of failed addition criteria as of evaluation date d. Empty list = eligible, not 'added'."""
    t = min_cap(d)
    fails = []
    if not c["us_domicile"]:
        fails.append("domicile")
    if c["cap_bn"] < t:
        fails.append(f"total cap {c['cap_bn']} < {t}")
    if c["fmc_bn"] < 0.5 * t:
        fails.append(f"FMC {c['fmc_bn']} < {0.5 * t:.2f}")
    if c["iwf"] < 0.10:
        fails.append("IWF < 0.10")
    if c["falr"] < 0.75:
        fails.append("FALR < 0.75")
    if min(c["monthly_shares_6m"]) < 250_000:
        fails.append("a month < 250,000 shares")
    if c["ni_q"][-1] <= 0:
        fails.append("latest quarter GAAP NI <= 0")
    if sum(c["ni_q"][-4:]) <= 0:
        fails.append("4-quarter GAAP NI sum <= 0")
    if c["months_trading"] < 12:
        fails.append("traded < 12 months")
    return fails


base = dict(us_domicile=True, cap_bn=25.0, fmc_bn=20.0, iwf=0.8, falr=1.1,
            monthly_shares_6m=[900_000] * 6, ni_q=[0.2, 0.3, 0.1, 0.4], months_trading=60)
cands = {
    "P (passes all)": dict(base),
    "Q (cap 21.0 bn)": dict(base, cap_bn=21.0, fmc_bn=18.0),
    "R (latest quarter loss)": dict(base, ni_q=[0.5, 0.5, 0.5, -0.1]),
    "S (IPO 10 months ago)": dict(base, months_trading=10),
    "T (IWF 0.08)": dict(base, iwf=0.08, fmc_bn=2.0),
}

print("=== A. S&P 500 addition screen as of an evaluation date (eligible != added) ===")
for d in (date(2025, 6, 2), date(2025, 7, 15)):
    print(f"evaluation {d}: minimum total cap {min_cap(d)} bn, minimum FMC {0.5 * min_cap(d):.2f} bn")
    for name, c in cands.items():
        f = sp500_screen(c, d)
        print(f"  {name:24s} -> {'eligible' if not f else 'fails: ' + '; '.join(f)}")
check(min_cap(date(2025, 7, 1)) == 20.5 and min_cap(date(2025, 7, 2)) == 22.7, "threshold changes after the close of 2025-07-01")
check(sp500_screen(cands["Q (cap 21.0 bn)"], date(2025, 6, 2)) == [], "21.0 bn passes under the 20.5 bn guideline")
check(sp500_screen(cands["Q (cap 21.0 bn)"], date(2025, 7, 15)) != [], "21.0 bn fails under 22.7 bn")
check(sp500_screen(cands["R (latest quarter loss)"], date(2025, 7, 15)) == ["latest quarter GAAP NI <= 0"], "both earnings tests")
check("traded < 12 months" in sp500_screen(cands["S (IPO 10 months ago)"], date(2025, 7, 15)), "12-month rule")
print("  the Index Committee still chooses among eligible names (fixed count 500, sector balance);")
print("  a member that later fails a criterion is not removed automatically.")

print("=== B. announcement timeline (synthetic dates) ===")
ann = datetime(2026, 3, 2, 17, 15)      # Monday, 05:15 PM ET, after the 16:00 close
eff = date(2026, 3, 9)                   # change effective before the open of Monday 2026-03-09
evaluation = add_bd(ann.date(), -2)
print(f"announcement {ann:%Y-%m-%d %a %H:%M} ET; evaluation date = open of {evaluation:%Y-%m-%d %a}")
print(f"business days between announcement and effective date: {bd_between(ann.date(), eff)} (methodology: at least 3)")
first_fill = datetime.combine(add_bd(ann.date(), 1), time(9, 30))
print(f"daily backtest: earliest fill on the news = {first_fill:%Y-%m-%d %H:%M} ET open (the 03-02 close came before the news)")
print(f"decision at the 2026-03-02 16:00 close: is the change known? {datetime(2026, 3, 2, 16, 0) >= ann} (using it = look-ahead)")
check(evaluation == date(2026, 2, 26), "two business days before the announcement")
check(bd_between(ann.date(), eff) >= 3, "at least three business days' notice")
check(first_fill.date() == date(2026, 3, 3), "next session open")

print("=== C. earnings release time -> first session that can react ===")
OPEN, CLOSE = time(9, 30), time(16, 0)


def day0(ts):
    """First regular session (date) that starts after ts, and whether that day's open is usable."""
    d = ts.date()
    if d.weekday() >= 5 or ts.time() >= CLOSE:
        d = add_bd(d if d.weekday() < 5 else d - timedelta(days=1), 1)
        return d, True
    if ts.time() < OPEN:
        return d, True
    return d, False  # released during the session: today's open came before the news


cases = [
    ("before the open", datetime(2026, 2, 3, 7, 0)),
    ("during the session", datetime(2026, 2, 4, 12, 30)),
    ("after the close (Thu)", datetime(2026, 2, 5, 16, 5)),
    ("after the close (Fri)", datetime(2026, 2, 6, 16, 5)),
]
res = {}
for label, ts in cases:
    d, open_ok = day0(ts)
    res[label] = (d, open_ok)
    print(f"release {ts:%Y-%m-%d %a %H:%M} ET ({label}): day 0 = {d:%Y-%m-%d %a}; that day's open usable? {open_ok}")
check(res["before the open"] == (date(2026, 2, 3), True), "pre-open release")
check(res["during the session"] == (date(2026, 2, 4), False), "intraday release: open is look-ahead")
check(res["after the close (Thu)"] == (date(2026, 2, 6), True), "after close -> next day")
check(res["after the close (Fri)"] == (date(2026, 2, 9), True), "Friday after close -> Monday")
rel = datetime(2026, 2, 5, 16, 5)
acc = datetime(2026, 2, 5, 16, 20)
print(f"only the 8-K is stored: accepted {acc:%Y-%m-%d %H:%M} ET -> day 0 {day0(acc)[0]} (same as the release here;")
print("  an 8-K is due within four business days, so its time can be later than the release; using it never looks ahead)")
check(day0(acc)[0] == day0(rel)[0], "8-K acceptance after the release maps to the same day 0 here")
print(f"assertions passed: {checks}/{checks}")
print("disclaimer: synthetic candidates and dates; no index-inclusion or earnings strategy; learning only")
