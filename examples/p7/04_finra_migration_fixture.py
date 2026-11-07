"""P7 lab 04: FINRA 26-10 four dates + member migration status, as a runnable offline fixture (R04/R34).
Reads fixtures/finra_26_10_fixture.json (hand-made). No broker connection, no network.
Learning only — NOT legal or compliance advice; a toy cannot certify any account's status.
"""
from __future__ import annotations
import json
from pathlib import Path

fx = json.loads((Path(__file__).resolve().parent / "fixtures" / "finra_26_10_fixture.json").read_text())
D = fx["dates"]


def regime(trade_date: str, account_category: str, member_adoption_date: str | None, broker_checked_on: str | None) -> str:
    if account_category == "cash":
        return "out_of_scope_cash"
    if account_category in ("good_faith", "portfolio_margin"):
        return "not_subject_to_d2_deficit"
    if trade_date < D["effective"]:
        return "old_pdt"
    if trade_date > D["phase_in_end"]:
        return "intraday_margin"
    # inside the phase-in window: the trade date alone proves nothing
    if member_adoption_date is None or broker_checked_on is None:
        return "needs_broker_verification"
    return "intraday_margin" if trade_date >= member_adoption_date else "old_pdt"


print(f"rule: {fx['rule']}  (checked_on {fx['checked_on']}; read by the author, not fetched by this script)")
for k in ("sec_approval", "notice_published", "effective", "phase_in_end"):
    print(f"  {k:17s} {D[k]}")
print("account categories:")
for k, v in fx["account_categories"].items():
    print(f"  {k:17s} {v}")
passed = 0
for c in fx["cases"]:
    got = regime(c["trade_date"], c["account_category"], c["member_adoption_date"], c["broker_checked_on"])
    ok = got == c["expect"]
    passed += ok
    print(f"{'PASS' if ok else 'FAIL'} {c['case']:26s} trade={c['trade_date']} acct={c['account_category']:16s} "
          f"adopted={c['member_adoption_date']} broker_checked_on={c['broker_checked_on']} -> {got}")
print(f"cases passed: {passed}/{len(fx['cases'])}")
assert passed == len(fx["cases"])
print("disclaimer: toy only; confirm with your broker and the current rule text")
