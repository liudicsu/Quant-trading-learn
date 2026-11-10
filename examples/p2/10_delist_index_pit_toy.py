"""Delisting returns, permanent IDs vs tickers, and index membership as of a date (checked 2026-11-10).

Sources: CRSP US Stock Databases Guide for CIZ (July 2026): MthRet "Will include delisting returns
if appropriate"; aggregate delisting flags G (excluded, value more than 10 trading days after delisting) and
M (excluded, delisting return missing); PERMNO = "CRSP unique permanent security level identifier".
Shumway (1997, JF 52(1):327-340): correct delisting returns are missing for most negative-reason
delists, and the omitted returns are large. FTSE Russell 2026 schedule: semi-annual (June and December);
December 2026 preliminary list published after the US close on 2026-11-13, effective after the close
on 2026-12-11 (markets open 2026-12-14 with new membership). All securities are synthetic. Learning only.
"""
import math
from datetime import date

checks = 0


def check(cond, label):
    global checks
    assert cond, label
    checks += 1


def compound(rets):
    return math.prod(1 + r for r in rets) - 1


print("=== A. a delisting is a return, not 'end of data' ===")
before, dl = [0.02, -0.01, 0.03], -0.42  # made-up toy figure, not a literature substitute
print(f"last three months only: {compound(before):+.2%}; including delisting return -42%: {compound(before + [dl]):+.2%}")
check(round(compound(before), 4) == 0.0401 and round(compound(before + [dl]), 4) == -0.3967, "delisting changes the result")


def month_return(mth_ret, del_flag):
    """CIZ: MthRet already includes the delisting return when appropriate -> never multiply again.
    Flags G / M mean it was EXCLUDED: the caller must decide and document a treatment."""
    if del_flag in {"G", "M"}:
        raise ValueError(f"delisting return excluded (flag {del_flag}): choose and document a treatment")
    return mth_ret


check(month_return(-0.25, "P") == -0.25, "flag P: use MthRet as is")
try:
    month_return(None, "M")
    silent = True
except ValueError as e:
    silent = False
    print(f"flag M -> {e}")
check(not silent, "missing delisting return is never silently 0")

print("=== B. survivorship: drop the dead and the mean looks better ===")
univ = {"A": 0.10, "B": 0.05, "C": -0.30, "D": -0.50}
alive = ["A", "B"]
full_mean, surv_mean = sum(univ.values()) / len(univ), sum(univ[k] for k in alive) / len(alive)
print(f"all four names: {full_mean:+.2%}; survivors only: {surv_mean:+.2%}")
check(round(full_mean, 4) == -0.1625 and round(surv_mean, 4) == 0.075, "survivor mean is biased up")

print("=== C. tickers get reused; key on a permanent ID ===")
rows = [  # (permno, ticker, year, return)
    (10001, "XYZ", 2018, -0.40), (10001, "XYZ", 2019, -0.90),
    (20002, "XYZ", 2024, 0.15), (20002, "XYZ", 2025, 0.10)]
by_ticker = [r for _, t, _, r in rows if t == "XYZ"]
by_permno = {p: [r for q, _, _, r in rows if q == p] for p in {p for p, *_ in rows}}
print(f"merge on ticker 'XYZ': one 'history' of {len(by_ticker)} years (two companies glued together)")
print(f"merge on PERMNO: {sorted(by_permno)} -> two separate histories")
check(len(by_ticker) == 4 and len(by_permno) == 2, "ticker merge glues two firms; PERMNO does not")

print("=== D. index membership as of a date (Russell December 2026 schedule) ===")
PRELIM_PUBLISHED, EFFECTIVE_OPEN = date(2026, 11, 13), date(2026, 12, 14)
membership = {date(2026, 6, 29): {"A", "B", "C"}, EFFECTIVE_OPEN: {"A", "B", "E"}}   # effective-from -> members


def members_asof(d):
    return membership[max(k for k in membership if k <= d)]


def list_known(decision_day):
    """Preliminary list comes out AFTER the US close on 11-13: usable from the next trading day."""
    return decision_day > PRELIM_PUBLISHED


for d in (date(2026, 11, 1), date(2026, 11, 16)):
    print(f"decision {d}: December preliminary list known? {list_known(d)}")
for d in (date(2026, 12, 11), date(2026, 12, 14)):
    print(f"members used on {d}: {sorted(members_asof(d))}")
check(not list_known(date(2026, 11, 1)) and list_known(date(2026, 11, 16)), "announcement date gates use")
check(members_asof(date(2026, 12, 11)) == {"A", "B", "C"} and members_asof(date(2026, 12, 14)) == {"A", "B", "E"}, "effective date")
print(f"assertions passed: {checks}/{checks}")
print("ASSERT_delist_index_pit_ok")
print("disclaimer: synthetic securities and membership; schedule dates from FTSE Russell; learning only")
