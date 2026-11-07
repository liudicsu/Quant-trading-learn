"""P3 lab 05 (optional): Kalman dynamic hedge ratio — filtered vs smoothed (offline synthetic, seed=5).
Learning only — not investment advice.

State: beta_t = beta_{t-1} + w_t ;  observation: y_t = beta_t * x_t + v_t.
Filtered beta_t uses data up to t (one-sided). Smoothed beta_t uses the WHOLE sample (two-sided),
as described in the statsmodels state-space docs -> smoothed values leak the future.
"""
from __future__ import annotations
import numpy as np

rng = np.random.default_rng(5)
T = 300
x = 50 + np.cumsum(rng.normal(0, 1, T))
true_beta = np.where(np.arange(T) < 150, 1.0, 1.5)          # hedge ratio jumps at t=150
y = true_beta * x + rng.normal(0, 1.0, T)
Q, R = 1e-4, 1.0


def kalman(y, x, Q=Q, R=R):
    n = len(y); bf = np.zeros(n); Pf = np.zeros(n); bp = np.zeros(n); Pp = np.zeros(n)
    b, P = 0.0, 10.0
    for t in range(n):
        bp[t], Pp[t] = b, P + Q                      # predict
        K = Pp[t] * x[t] / (x[t] ** 2 * Pp[t] + R)  # gain
        b = bp[t] + K * (y[t] - bp[t] * x[t]); P = (1 - K * x[t]) * Pp[t]
        bf[t], Pf[t] = b, P
    bs = bf.copy()                                   # RTS smoother (backward pass)
    for t in range(n - 2, -1, -1):
        C = Pf[t] / Pp[t + 1]
        bs[t] = bf[t] + C * (bs[t + 1] - bp[t + 1])
    return bf, bs


bf, bs = kalman(y, x)
print("=== Kalman hedge ratio (true beta 1.0 -> 1.5 at t=150) ===")
for t in (140, 149, 155, 170):
    print(f"t={t}: true={true_beta[t]:.2f} filtered={bf[t]:.4f} smoothed={bs[t]:.4f}")
print(f"mean |beta error| filtered={np.abs(bf[20:]-true_beta[20:]).mean():.4f} "
      f"smoothed={np.abs(bs[20:]-true_beta[20:]).mean():.4f}")
print("-> smoothed looks 'better' because it already saw the future")

print("=== future-perturbation test (change data after t0=200) ===")
t0 = 200
y2 = y.copy(); y2[t0 + 1:] += 30.0
bf2, bs2 = kalman(y2, x)
print(f"max |filtered change| for t<=t0: {np.abs(bf2[:t0+1]-bf[:t0+1]).max():.6f}")
print(f"max |smoothed change| for t<=t0: {np.abs(bs2[:t0+1]-bs[:t0+1]).max():.6f}")
print("-> a causal signal must pass: future edits do not change past values")

print("=== spread signal using lagged filtered beta (beta_{t-1}) ===")
spread = y[1:] - bf[:-1] * x[1:]
print(f"spread std (filtered, lagged) = {spread[20:].std():.4f}")
print("disclaimer: synthetic; learning only")
