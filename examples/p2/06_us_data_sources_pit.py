"""P2 lab 06: US data-source roles + point-in-time (PIT) as-of joins on HAND-MADE fixtures.
Learning only — not investment advice. No network, no API key, no real SEC/FRED data.
"""
from __future__ import annotations
import json
from datetime import datetime, date
from pathlib import Path

D = Path(__file__).resolve().parent / "data" / "us_fixtures"
print("source_mode=synthetic_fixture (no download, no cache)")

print("=== 1. which source answers which question ===")
roles = [
    ("SEC EDGAR (companyfacts/submissions)", "filings & XBRL facts; NOT price bars"),
    ("FRED / ALFRED", "macro series & vintages; NOT tick data; API needs key; service terms restrict"),
    ("Ken French Data Library", "research factor returns; NOT raw single-stock prices"),
    ("CRSP (subscription)", "security-level returns, delistings, PERMNO; not free"),
    ("Alpaca Basic / Massive Basic", "vendor feeds with plan limits (IEX real-time / EOD); check entitlement"),
    ("yfinance", "unofficial wrapper, not affiliated with Yahoo; no reliability or licence promise"),
]
for s, r in roles:
    print(f"- {s}: {r}")

print("=== 2. EDGAR-like facts: align by availability, not period end ===")
facts = json.loads((D / "edgar_like_facts.json").read_text())["facts"]
decision = datetime.fromisoformat("2026-05-08T09:30:00-04:00")
def asof_fact(decision_time):
    ok = [f for f in facts if f["period_end"] == "2026-03-31" and datetime.fromisoformat(f["accepted"]) <= decision_time]
    return max(ok, key=lambda f: f["accepted"]) if ok else None
naive = [f for f in facts if f["period_end"] == "2026-03-31"][-1]      # "latest facts" backfilled
pit = asof_fact(decision)
print(f"decision {decision.isoformat()}: PIT value={pit['value']} ({pit['revision_id']}, accepted {pit['accepted']})")
print(f"naive latest-facts value={naive['value']} ({naive['revision_id']}, accepted {naive['accepted']}) -> look-ahead")
early = asof_fact(datetime.fromisoformat("2026-04-15T09:30:00-04:00"))
print(f"decision 2026-04-15: PIT value={early} (period ended 03-31 but nothing filed yet)")
assert datetime.fromisoformat(pit["accepted"]) <= decision
print("ASSERT available_at <= decision_time: ok")

print("=== 3. ALFRED-like vintages: observation date != when it was known ===")
v = json.loads((D / "alfred_like_vintages.json").read_text())
obs = v["observations"]
def known_on(obs_date, asof):
    for o in obs:
        if o["date"] == obs_date and o["realtime_start"] <= asof <= o["realtime_end"]:
            return o["value"]
    return None
for asof in ("2026-05-15", "2026-06-15", "2026-07-15"):
    print(f"value of 2026-04 obs as known on {asof}: {known_on('2026-04-01', asof)}")
final = [o for o in obs if o["date"] == "2026-04-01"][-1]["value"]
print(f"'current' (FRED-mode default = today) value backfilled to May decision: {final} vs as-known 2.0")

print("=== 4. S-A: two feature sets differ ===")
decisions = ["2026-05-15", "2026-06-15", "2026-07-15"]
asof_feat = [known_on("2026-04-01", d) for d in decisions]
final_feat = [final] * len(decisions)
print(f"as-of feature   : {asof_feat}")
print(f"final-value feat: {final_feat}")
print(f"rows that differ: {sum(a != b for a, b in zip(asof_feat, final_feat))}/{len(decisions)}")
nr = v["no_release_time_series"]
print(f"{nr['series_id']}: realtime_start={nr['realtime_start']} -> EXCLUDED from signal (cannot guess when it was known)")
print("disclaimer: hand-made fixtures; learning only")
