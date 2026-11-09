"""P7 lab 05: overnight session classification + trade-date assignment + Shanghai-time view (offline fixture).
Broker side follows Alpaca's 24/5 doc (overnight 20:00-04:00 ET via the BOATS ATS; limit orders only; TIF day/gtc;
an overnight trade is dated to the NEXT trading day and settles T+1 from that date; `overnight_tradable` /
`overnight_halted` asset flags). Exchange overnight (21:00-04:00 ET) is PLANNED from 2026-12-06, dependent on
Processor systems changes (SEC 34-106042; CTA ETH FAQ). checked_on 2026-11-09. No API keys, no network.
Session hours follow the broker doc (trading week Sunday evening to Friday evening). Rejecting every input from
Friday 20:00 ET (inclusive) to Sunday 20:00 ET (exclusive) is THIS TOY's own rule: a real broker may accept such an
order and queue it for the next session -- check the broker doc and the API response. Only weekends are modelled;
other market/settlement holidays are NOT modelled. This is not Alpaca's actual rule engine.
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


def in_weekly_closure(dt: datetime) -> bool:
    """Friday 20:00 ET (inclusive) .. Sunday 20:00 ET (exclusive): no session at all."""
    wd, t = dt.weekday(), dt.time()
    return (wd == 4 and t >= time(20, 0)) or wd == 5 or (wd == 6 and t < time(20, 0))


def check(o) -> str:
    a = assets[o["symbol"]]
    dt = datetime.fromisoformat(o["et"]).replace(tzinfo=ET)
    s = session(dt.time())
    if in_weekly_closure(dt):
        return "rejected: weekly closure (toy rule; Fri 20:00 to Sun 20:00 ET)"
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
    res = check(o)
    rows.append((o["id"], res))
    if res.startswith("rejected"):
        dates = "trade_date -          | settle(T+1) -         "   # rejected: no trade, no settlement record
        sess = "closed" if in_weekly_closure(dt) else session(dt.time())
    else:
        td = trade_date(dt)
        dates = f"trade_date {td} | settle(T+1) {next_weekday(td)}"
        sess = session(dt.time())
    print(f"{o['id']:>3} {o['symbol']} ET {dt:%a %m-%d %H:%M} | Shanghai {dt.astimezone(SH):%a %m-%d %H:%M} | "
          f"{sess:11s} | {dates} | {o['type']}/{o['tif']} -> {res}")
d = dict(rows)
n_ok = 0
def check_(cond, msg):
    global n_ok
    assert cond, msg
    n_ok += 1
check_(d["n1"] == "accepted" and d["n2"].startswith("rejected: overnight accepts limit"), 'd["n1"] == "accepted" and d["n2"].startswith("rejected: overnight accepts limit")')
check_(d["n3"].startswith("rejected: overnight TIF") and d["n4"].startswith("accepted but pending"), 'd["n3"].startswith("rejected: overnight TIF") and d["n4"].startswith("accepted but pending")')
check_(d["n5"].startswith("rejected: overnight_tradable") and d["n6"] == "accepted" and d["n7"] == "accepted", 'd["n5"].startswith("rejected: overnight_tradable") and d["n6"] == "accepted" and d["n7"] == "accepted"')
check_(all(d[k].startswith("rejected: weekly closure") for k in ("n8", "n9", "n10", "n11", "n12")), 'all(d[k].startswith("rejected: weekly closure") for k in ("n8", "n9", "n10", "n11", "n12"))')
check_(d["n13"] == "accepted" and d["n14"] == "accepted" and d["n15"] == "accepted", 'd["n13"] == "accepted" and d["n14"] == "accepted" and d["n15"] == "accepted"')
from datetime import date
check_(trade_date(datetime(2026, 11, 15, 20, 0)) == date(2026, 11, 16) , 'trade_date(datetime(2026, 11, 15, 20, 0)) == date(2026, 11, 16) ')
check_(trade_date(datetime(2026, 11, 16, 1, 0)) == date(2026, 11, 16), 'trade_date(datetime(2026, 11, 16, 1, 0)) == date(2026, 11, 16)')
def sh(et):
    return datetime.fromisoformat(et).replace(tzinfo=ET).astimezone(SH)
by_id = {o["id"]: o for o in fx["orders"]}
# DST-switch weeks: 2026-11-01 (EDT->EST) and 2027-03-14 (EST->EDT); Sunday 20:00 ET boundary
check_(d["n16"].startswith("rejected: weekly closure") and d["n18"].startswith("rejected: weekly closure"), "Sun 19:59 rejected")
check_(d["n17"] == "accepted" and d["n19"] == "accepted", "Sun 20:00 accepted")
check_(sh(by_id["n17"]["et"]).strftime("%a %H:%M") == "Mon 09:00", "n17 Shanghai Mon 09:00 (EST, UTC-5)")
check_(sh(by_id["n19"]["et"]).strftime("%a %H:%M") == "Mon 08:00", "n19 Shanghai Mon 08:00 (EDT, UTC-4)")
check_(trade_date(datetime(2026, 11, 1, 20, 0)) == date(2026, 11, 2), "n17 trade_date Mon")
check_(trade_date(datetime(2027, 3, 14, 20, 0)) == date(2027, 3, 15), "n19 trade_date Mon")
print(f"assertions passed: {n_ok}/{n_ok}")
print("note: a Monday 21:00 ET order shows a TUESDAY trade date and Shanghai Tuesday 10:00 (EST, UTC-5).")
print("exchange Overnight Protected Hours 21:00-04:00 ET = 10:00-17:00 Shanghai while US is on EST (planned 2026-12-06).")
