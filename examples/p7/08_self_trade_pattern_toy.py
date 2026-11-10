"""Self-trade prevention and a disruptive-quoting pattern flag (checked 2026-11-10).

Sources: 15 U.S.C. 78i(a)(1)-(2) (govinfo, USCODE-2023 edition; wash trades / matched orders / series of
transactions to induce others); FINRA Rule 5210 Supplementary Material .02 (unintentional self-trades are
generally bona fide, but firms must review for and prevent a pattern of self-trades from a single algorithm
or related algorithms) and .03 (two prohibited patterns of disruptive quoting and trading, incl. across
venues; SM .03(c): the order of events does not modify applicability); IRS Publication 550 (wash sale = tax
concept: repurchase within 30 days before or after the sale, see 06_wash_sale_basis_toy.py).
Purely synthetic events. A flag is only a prompt for human review, not a finding of a violation.
Not legal advice; learning only.
"""

checks = 0


def check(cond, label):
    global checks
    assert cond, label
    checks += 1


print("=== A. self-trade prevention at the order layer ===")
book = [("BUY", 10.00, 100, "algoA")]   # (side, price, qty, owner)


def stp(book, o):
    """Resting orders the incoming order would hit that belong to the same algo."""
    side, px, _, owner = o
    return [b for b in book if b[3] == owner and b[0] != side
            and ((side == "SELL" and px <= b[1]) or (side == "BUY" and px >= b[1]))]


blocked_a = stp(book, ("SELL", 10.00, 100, "algoA"))
blocked_b = stp(book, ("SELL", 10.00, 100, "algoB"))
print(f"incoming algoA SELL 100@10.00 vs resting algoA BUY 100@10.00 -> blocked {len(blocked_a)}")
print(f"incoming algoB SELL 100@10.00 -> blocked {len(blocked_b)} (this toy checks same algo only; real scope follows firm policy)")
check(len(blocked_a) == 1, "same algo blocked")
check(len(blocked_b) == 0, "different algo not blocked by this toy")

print("=== B. pattern flag: layer one side, fill the other, cancel the layers ===")


def layering_flag(events):
    """events: (kind, side, price, t). True = this order-dependent toy flags the log."""
    buys = [e for e in events if e[0] == "new" and e[1] == "BUY"]
    fills = [e for e in events if e[0] == "fill" and e[1] == "SELL"]
    cancels = [e for e in events if e[0] == "cancel" and e[1] == "BUY"]
    if len({b[2] for b in buys}) >= 3 and fills and len(cancels) >= 3:
        t_fill = fills[0][3]
        return all(c[3] > t_fill for c in cancels) and all(b[3] < t_fill for b in buys)
    return False


def should_review_layers(events):
    """Same ingredients, ignoring event order. FINRA 5210 SM .03(c): order does not change applicability."""
    buys = [e for e in events if e[0] == "new" and e[1] == "BUY"]
    fills = [e for e in events if e[0] == "fill" and e[1] == "SELL"]
    cancels = [e for e in events if e[0] == "cancel" and e[1] == "BUY"]
    return len({b[2] for b in buys}) >= 3 and bool(fills) and len(cancels) >= 3


pattern = [("new", "BUY", 9.97, 1), ("new", "BUY", 9.98, 2), ("new", "BUY", 9.99, 3),
           ("fill", "SELL", 10.01, 5), ("cancel", "BUY", 9.97, 6), ("cancel", "BUY", 9.98, 6),
           ("cancel", "BUY", 9.99, 6)]
benign = [e for e in pattern if e[0] != "fill"]
swapped = [("new", "BUY", 9.97, 1), ("new", "BUY", 9.98, 2), ("new", "BUY", 9.99, 3),
           ("cancel", "BUY", 9.97, 6), ("cancel", "BUY", 9.98, 6),
           ("cancel", "BUY", 9.99, 6), ("fill", "SELL", 10.01, 7)]
print(f"3 bid layers -> sell fill -> cancel all layers: flagged for review {layering_flag(pattern)}")
print(f"same layers cancelled with no other-side fill: flagged for review {layering_flag(benign)}")
print(f"3 bid layers -> cancel all layers -> sell fill: flagged for review {layering_flag(swapped)}")
print("swapped order still should be reviewed "
      f"{should_review_layers(swapped)} (FINRA 5210 SM .03(c): event order does not change applicability; this toy only flags one event order)")
print("a flag only asks a human to review the log; it is not a finding of a violation")
check(layering_flag(pattern), "pattern flagged")
check(not layering_flag(benign), "benign not flagged")
check(not layering_flag(swapped), "swapped order not flagged by this toy")
check(should_review_layers(swapped) and should_review_layers(pattern) and not should_review_layers(benign),
      "swapped order still should be reviewed")

print("=== C. two words that are easy to mix up ===")
glossary = {"wash sale": "tax: loss sale + repurchase within 30 days before or after the sale (IRS Pub 550)",
            "wash trade": "manipulation: no change in beneficial ownership (15 U.S.C. 78i(a)(1))"}
for k, v in glossary.items():
    print(f"{k:10s} -> {v}")
check(glossary["wash sale"].startswith("tax") and glossary["wash trade"].startswith("manipulation"), "glossary")
print(f"assertions passed: {checks}/{checks}")
print("ASSERT_self_trade_pattern_ok")
print("disclaimer: synthetic events; flags are review prompts, not legal findings; not legal advice; learning only")
