"""P7 lab 05: overnight session classification + trade-date assignment + Shanghai-time view (offline fixture).
Broker side follows Alpaca's 24/5 doc (overnight 20:00-04:00 ET via the BOATS ATS; limit orders only; TIF day/gtc;
an overnight trade is dated to the NEXT trading day and settles T+1 from that date; `overnight_tradable` /
`overnight_halted` asset flags). Exchange overnight (21:00-04:00 ET) is PLANNED from 2026-12-06, dependent on
Processor systems changes (SEC 34-106042; CTA ETH FAQ). checked_on 2026-11-08. No API keys, no network.
Toy simplifications: holidays ignored except weekends; this is not Alpaca's actual rule engine.
"""
from __future__ import annotations
import json
from datetime import datetime, timedelta, time
from pathlib import Path
from zoneinfo import ZoneInfo

ET, SH = ZoneInfo("America/New_York"), ZoneInfo("Asia/Shanghai")
fx = json.loads((Path(__file__).resolve().parent / "fixtures" / "overnight_sessions_fixture.json").read_text())
assets = {a["symbol"]: a for a in fx["assets"]}


def session(t: time) -> str:
    if t >= time(20, 0) or t < time(4, 0):
        return "overnight"
    if t < time(9, 30):
        return "pre_market"
    if t < time(16, 0):
        return "regular"
    return "after_hours"


def next_weekday(d):
    d += timedelta(days=1)
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d


def trade_date(dt: datetime):
    # overnight session that starts in the evening belongs to the NEXT trading day
    return next_weekday(dt.date()) if session(dt.time()) == "overnight" and dt.time() >= time(20, 0) else dt.date()


def check(o) -> str:
    a = assets[o["symbol"]]
    dt = datetime.fromisoformat(o["et"]).replace(tzinfo=ET)
    s = session(dt.time())
    if s == "overnight" and dt.weekday() == 4 and dt.time() >= time(20, 0):
        return "rejected: no overnight session on Friday evening"
    if s == "overnight":
        if not a["overnight_tradable"]:
            return "rejected: overnight_tradable=false"
        if o["type"] != "limit":
            return "rejected: overnight accepts limit orders only"
        if o["tif"] not in ("day", "gtc"):
            return "rejected: overnight TIF must be day or gtc"
        if a["overnight_halted"]:
            return "accepted but pending: overnight_halted=true (broker holds it; exchange halts would reject)"
    return "accepted"


rows = []
for o in fx["orders"]:
    dt = datetime.fromisoformat(o["et"]).replace(tzinfo=ET)
    td = trade_date(dt)
    st = next_weekday(td)
    res = check(o)
    rows.append((o["id"], res))
    print(f"{o['id']} {o['symbol']} ET {dt:%a %m-%d %H:%M} | Shanghai {dt.astimezone(SH):%a %m-%d %H:%M} | "
          f"{session(dt.time()):11s} | trade_date {td} | settle(T+1) {st} | {o['type']}/{o['tif']} -> {res}")
d = dict(rows)
assert d["n1"] == "accepted" and d["n2"].startswith("rejected: overnight accepts limit")
assert d["n3"].startswith("rejected: overnight TIF") and d["n4"].startswith("accepted but pending")
assert d["n5"].startswith("rejected: overnight_tradable") and d["n6"] == "accepted" and d["n7"] == "accepted"
assert d["n8"].startswith("rejected: no overnight session on Friday")
print("assertions passed: 8/8")
print("note: a Monday 21:00 ET order shows a TUESDAY trade date and Shanghai Tuesday 10:00 (EST, UTC-5).")
print("exchange Overnight Protected Hours 21:00-04:00 ET = 10:00-17:00 Shanghai while US is on EST (planned 2026-12-06).")
