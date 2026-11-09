"""P6 lab 09: US equity options basics for quant learners (offline, math stdlib only).
Learning only — not investment advice; no strategy, no return claims, no 0DTE.

A. Contract unit: most US equity options cover 100 shares; a $4 premium is $400 per contract (OCC ODD, June 2024).
B. Expiry P&L for long call / short put / covered call, premium included.
C. Put-call parity (European, no dividends; Stoll 1969): C - P = S - K*exp(-r*T). Model-free.
D. Black-Scholes-Merton (1973) as a REFERENCE price only: constant vol, lognormal, frictionless.
   Model price != market price is not "mispricing" or alpha.
E. Ordinary cash dividends do not adjust option terms -> a deep in-the-money call holder may exercise
   before the ex-date, so a call writer may be assigned (teaching flag, not a trade rule).
"""
from __future__ import annotations
from math import erf, exp, log, sqrt

checks = 0


def check(cond: bool, msg: str) -> None:
    global checks
    assert cond, msg
    checks += 1


MULT = 100


def contract_value(premium: float, multiplier: int = MULT) -> float:
    return premium * multiplier


print("=== A. contract unit ===")
print(f"premium $4.00 per share x {MULT} shares = ${contract_value(4.0):.2f} per contract")
check(contract_value(4.0) == 400.0, "a $4 premium is $400 per contract")

print("=== B. expiry P&L per contract (premium included) ===")
K, prem_c, prem_p = 100.0, 3.0, 2.5


def long_call(st: float) -> float:
    return (max(st - K, 0) - prem_c) * MULT


def short_put(st: float) -> float:
    return (prem_p - max(K - st, 0)) * MULT


def covered_call(st: float, s0: float = 100.0) -> float:   # long 100 shares at s0 + short 1 call
    return (st - s0) * MULT + (prem_c - max(st - K, 0)) * MULT


print("S_T     long_call  short_put  covered_call")
for st in (80.0, 100.0, 120.0):
    print(f"{st:6.1f} {long_call(st):10.2f} {short_put(st):10.2f} {covered_call(st):13.2f}")
check(long_call(80.0) == -prem_c * MULT, "long call max loss = premium")
check(short_put(0.0) == -(K * MULT - prem_p * MULT), "short put max loss = K*100 - premium*100")
check(covered_call(120.0) == covered_call(150.0), "covered call upside is capped")
print(f"short put worst case (stock to 0): {short_put(0.0):.2f}")


def N(x: float) -> float:
    return 0.5 * (1 + erf(x / sqrt(2)))


def bsm(S: float, K: float, r: float, T: float, sigma: float) -> tuple[float, float]:
    d1 = (log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)
    call = S * N(d1) - K * exp(-r * T) * N(d2)
    put = K * exp(-r * T) * N(-d2) - S * N(-d1)
    return call, put


print("=== C/D. BSM reference price and put-call parity ===")
S, r, T, sig = 100.0, 0.05, 1.0, 0.20
C, P = bsm(S, K, r, T, sig)
lhs, rhs = C - P, S - K * exp(-r * T)
print(f"BSM(S=100,K=100,r=5%,T=1,vol=20%): call {C:.4f} put {P:.4f}")
print(f"parity: C-P {lhs:.4f} vs S-K*exp(-rT) {rhs:.4f}")
check(abs(C - 10.4506) < 5e-5 and abs(P - 5.5735) < 5e-5, "BSM reference values")
check(abs(lhs - rhs) < 1e-9, "put-call parity holds for European no-dividend inputs")
market_call = 11.20   # synthetic quote
print(f"synthetic market call {market_call:.2f} vs model {C:.4f}: a gap is model error or inputs, NOT alpha")

print("=== E. dividends and early assignment (teaching flag) ===")


def early_assignment_risk(call_itm: bool, extrinsic: float, dividend: float) -> bool:
    return call_itm and extrinsic < dividend


for itm, ext, div in ((True, 0.10, 0.50), (True, 0.80, 0.50), (False, 0.05, 0.50)):
    print(f"call ITM={itm} extrinsic {ext:.2f} dividend {div:.2f} -> assignment risk before ex-date: {early_assignment_risk(itm, ext, div)}")
check(early_assignment_risk(True, 0.10, 0.50) is True, "deep ITM call, small time value")
check(early_assignment_risk(True, 0.80, 0.50) is False, "time value above dividend")
check(early_assignment_risk(False, 0.05, 0.50) is False, "out-of-the-money")

print(f"assertions passed: {checks}/{checks}")
print("ASSERT_options_toy_ok")
print("disclaimer: synthetic numbers; learning only; read the OCC ODD before trading options")
