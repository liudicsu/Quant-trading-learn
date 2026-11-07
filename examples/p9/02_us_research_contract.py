"""US research contract checker (M8). Offline: validates a JSON contract + a local fixture; NO downloads.
Prints source_mode / fallback_reason. Contract fields follow the US-first brief. Learning only."""
import hashlib, json, pathlib
here = pathlib.Path(__file__).resolve().parent
c = json.loads((here / "us_research_contract.json").read_text())
REQ = ["market", "currency", "session_scope", "source", "feed", "licence", "snapshot_sha256", "adjustment_policy",
       "dividend_policy", "universe", "availability_ts_rule", "calendar_version", "rule_version", "short_borrow_mode",
       "benchmark", "risk_free", "cost_model", "paper_is_not_live", "source_mode", "fallback_reason"]
missing = [k for k in REQ if k not in c]
print("A) required fields:", len(REQ), "missing:", missing)
fx = here.parent / "p2" / "data" / "us_fixtures" / "alfred_like_vintages.json"
h = hashlib.sha256(fx.read_bytes()).hexdigest()
print("B) fixture sha256 prefix:", h[:12], "matches_contract:", h == c["snapshot_sha256"])
checks = {"market": c["market"] == "US-equity", "currency": c["currency"] == "USD",
          "no_live_download": c["source_mode"] in ("fixture", "user_snapshot"),
          "historical_universe": c["universe"]["survivorship"] == "historical_membership",
          "paper_ne_live": c["paper_is_not_live"] is True,
          "short_mode_declared": c["short_borrow_mode"] in ("none", "constrained", "naive_flagged")}
for k, v in checks.items(): print(f"C) {k}: {v}")
print("D) source_mode =", c["source_mode"], "| fallback_reason =", c["fallback_reason"])
print("E) contract_ok =", not missing and all(checks.values()) and h == c["snapshot_sha256"])
