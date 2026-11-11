"""P2 lab 08: dividend dates under T+1, and yfinance return shapes (offline, hand-made fixtures).
Learning only — not investment advice. No network; no yfinance import.

A. Ex-dividend date under T+1 (investor.gov, checked_on 2026-11-10): usually = record date,
   or the business day before if the record date is not a business day; a dividend of 25%+
   of the stock value defers the ex-date to one business day after payment.
B. Ledger: total return is booked on the ex-date, cash arrives on the pay date; never both.
C. yfinance shapes (docs + CHANGELOG, checked_on 2026-11-10): since 0.2.51 download() defaults
   auto_adjust=True -> 'Close' is split+dividend adjusted and there is no 'Adj Close';
   auto_adjust=False -> 'Close' is still split-adjusted, plus a dividend-adjusted 'Adj Close'.
"""
from __future__ import annotations
from datetime import date, timedelta

checks = 0


def check(cond: bool, msg: str) -> None:
    global checks
    assert cond, msg
    checks += 1


HOLIDAYS = set()   # fixture: no holidays in the dates used


def is_bday(d: date) -> bool:
    return d.weekday() < 5 and d not in HOLIDAYS


def prev_bday(d: date) -> date:
    d -= timedelta(days=1)
    while not is_bday(d):
        d -= timedelta(days=1)
    return d


def next_bday(d: date) -> date:
    d += timedelta(days=1)
    while not is_bday(d):
        d += timedelta(days=1)
    return d


def ex_date(record: date, pay: date | None = None, ratio: float = 0.0) -> date:
    if ratio >= 0.25:
        assert pay is not None, "25%+ dividends need the pay date"
        return next_bday(pay)
    return record if is_bday(record) else prev_bday(record)


def entitled(buy_trade_date: date, ex: date) -> bool:
    return buy_trade_date < ex


print("=== A. ex-dividend date (investor.gov examples) ===")
cases = [
    ("normal, record Mon", date(2026, 3, 16), None, 0.0),
    ("record on Sunday", date(2026, 3, 15), None, 0.0),
    ("special dividend >= 25%", date(2026, 3, 16), date(2026, 3, 17), 0.30),
]
for name, rec, pay, ratio in cases:
    print(f"{name}: record {rec} ({rec:%a}) pay {pay} ratio {ratio:.2f} -> ex {ex_date(rec, pay, ratio)} ({ex_date(rec, pay, ratio):%a})")
check(ex_date(date(2026, 3, 16)) == date(2026, 3, 16), "ex = record when record is a business day")
check(ex_date(date(2026, 3, 15)) == date(2026, 3, 13), "Sunday record -> Friday ex")
check(ex_date(date(2026, 3, 16), date(2026, 3, 17), 0.30) == date(2026, 3, 18), "25%+ -> day after pay")
ex = date(2026, 3, 16)
for buy in (date(2026, 3, 13), date(2026, 3, 16)):
    print(f"buy on {buy} -> gets this dividend: {entitled(buy, ex)}")
check(entitled(date(2026, 3, 13), ex) is True and entitled(date(2026, 3, 16), ex) is False, "buy on ex-date gets nothing")

print("=== B. ledger: ex-date vs pay-date (100 shares, $0.50 dividend) ===")
shares, dps = 100, 0.50
ledger = [
    (date(2026, 3, 13), "price", 100.00, 0.0),
    (date(2026, 3, 16), "ex-date: price drops, dividend receivable", 99.60, dps * shares),
    (date(2026, 3, 17), "pay-date: receivable -> cash", 99.80, 0.0),
]
receivable, cash = 0.0, 0.0
for d, what, px, accrue in ledger:
    receivable += accrue
    if "pay-date" in what:
        cash += receivable
        receivable = 0.0
    print(f"{d} {what}: px {px:.2f} receivable {receivable:.2f} cash {cash:.2f} total {shares * px + receivable + cash:.2f}")
check(cash == 50.0 and receivable == 0.0, "dividend counted once: accrued on ex-date, paid on pay-date")
tr_ex = (shares * 99.60 + 50.0) / (shares * 100.00) - 1
print(f"total return on ex-date: {tr_ex:+.4%} (price-only would show {99.60 / 100 - 1:+.4%})")
check(abs(tr_ex - 0.001) < 1e-12, "total return on ex-date includes the dividend")

print("=== C. yfinance-like return shapes (synthetic, 2-for-1 split + $1 dividend) ===")
# unadjusted history: day0 200 (pre-split), day1 split 2:1 -> 101, day2 ex-div $1 -> 100.5
raw = [200.0, 101.0, 100.5]
split_adj = [100.0, 101.0, 100.5]                 # Yahoo 'Close' with auto_adjust=False
div_factor = 1 - 1.0 / 101.0                       # back-adjust rows before the ex-date
adj = [split_adj[0] * div_factor, split_adj[1] * div_factor, split_adj[2]]


def classify(cols: set[str]) -> str:
    if "Adj Close" in cols:
        return "split_adjusted_close_plus_adj"
    if {"Open", "High", "Low", "Close", "Volume"} <= cols:
        return "auto_adjusted_close"
    return "unknown"


shape_true = {"cols": {"Open", "High", "Low", "Close", "Volume"}, "Close": adj}
shape_false = {"cols": {"Open", "High", "Low", "Close", "Adj Close", "Volume"}, "Close": split_adj, "Adj Close": adj}
print(f"auto_adjust=True  -> {classify(shape_true['cols'])}")
print(f"auto_adjust=False -> {classify(shape_false['cols'])}")
check(classify(shape_true["cols"]) == "auto_adjusted_close", "True shape has no Adj Close")
check(classify(shape_false["cols"]) == "split_adjusted_close_plus_adj", "False shape has Adj Close")
check(shape_false["Close"][0] != raw[0], "even auto_adjust=False Close is split-adjusted, not raw")

ret = lambda s: s[2] / s[1] - 1
print(f"ex-date return: Close(True) {ret(shape_true['Close']):+.4%} vs Close(False) {ret(shape_false['Close']):+.4%}")
check(abs(ret(shape_true["Close"]) - ret(shape_false["Close"])) > 1e-6, "same column name, different meaning on a dividend day")


def require_explicit_auto_adjust(call_kwargs: dict) -> None:
    if "auto_adjust" not in call_kwargs:
        raise ValueError("write auto_adjust explicitly and pin the yfinance version")


try:
    require_explicit_auto_adjust({})
    raised = False
except ValueError:
    raised = True
print(f"call without auto_adjust rejected: {raised}")
check(raised, "implicit default rejected")

print(f"assertions passed: {checks}/{checks}")
print("ASSERT_dividend_yf_ok")
print("disclaimer: synthetic fixtures; learning only")

print("=== D. Rule 10b-17 issuer notice (calendar days as written; not business days) ===")
# 17 CFR 240.10b-17(b)(1): notice is deemed given only if given to the National
# Association of Securities Dealers, Inc., "no later than 10 days prior to the
# record date involved" or, for a rights subscription or other offering if such
# 10 days advance notice is not practical, "on or before the record date and in
# no event later than the effective date of the registration statement to which
# the offering relates," or given under substantially comparable listing-exchange
# procedures. The Commission may exempt an issuer.
# 10b-17(c): the rule does not apply to redeemable securities issued by open-end
# investment companies and unit investment trusts. This toy does not invent a
# FINRA-substituted addressee. A late or missing notice is a data-quality /
# timing flag, not proof the dividend did not happen. 10b-17 itself does not
# move the ex-date (FINRA 11140(b) already covers 25%+ deferral).


def notice_due(record):
    """10 calendar days prior to the record date, as written in 10b-17(b)(1)."""
    return record - timedelta(days=10)


rec = date(2026, 3, 16)  # Monday, same record date as section A
due = notice_due(rec)
print(f"cash dividend, record {rec}: notice generally due no later than {due} (10 calendar days prior)")
check(due == date(2026, 3, 6), "10 calendar days, not 10 business days")
ten_bdays_before = rec
n = 0
while n < 10:
    ten_bdays_before -= timedelta(days=1)
    if ten_bdays_before.weekday() < 5:
        n += 1
print(f"10 business days before the same record date would be {ten_bdays_before}; that is not the 10b-17 clock")
check(ten_bdays_before != due, "do not rewrite 10 days as 10 business days")


def rights_notice_ok(notice, record, registration_effective, practical_10_days):
    if practical_10_days:
        return notice <= record - timedelta(days=10)
    return notice <= record and notice <= registration_effective


reg_eff = date(2026, 4, 1)
print(f"rights offering, 10 days not practical: notice on record date {rec} and before registration effective {reg_eff}? {rights_notice_ok(rec, rec, reg_eff, False)}")
check(rights_notice_ok(rec, rec, reg_eff, False) is True, "rights fallback: on or before record, no later than effective date")
check(rights_notice_ok(date(2026, 4, 2), rec, reg_eff, False) is False, "rights notice after the effective date is late")

def tenb17_applies(security_class):
    # 10b-17(c): redeemable securities issued by open-end investment companies
    # and unit investment trusts are excepted.
    return security_class not in {"open-end redeemable", "UIT redeemable"}


for kind, expect in (
    ("listed common stock", True),
    ("open-end redeemable", False),
    ("UIT redeemable", False),
):
    got = tenb17_applies(kind)
    print(f"  10b-17 notice rule applies to {kind}? {got}")
    check(got is expect, kind)
print("a late or missing 10b-17 notice is a data-quality / timing flag, not proof the dividend did not happen")
print("10b-17 does not itself defer the ex-date; the 25%+ deferral is already taught under FINRA 11140(b)")

print(f"assertions passed: {checks}/{checks}")
print("ASSERT_dividend_yf_ok")
print("disclaimer: synthetic fixtures; learning only")
