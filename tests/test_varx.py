"""Simulation tests: the VARX* system recovers a known El Niño impulse response.

1. Stationary system (levels VARX*): estimated IRF matches the true IRF.
2. Cointegrated home block (VECMX*, r = 1): reduced-rank regression recovers the long-run
   matrix Pi = alpha beta' and the IRF; the levels mapping reproduces the VECM fitted values.
3. The bootstrap centres on the truth.
"""

import numpy as np
import pandas as pd
import pytest

from elnino.varx import VECMX, AR1, LevelsVARX, System, bootstrap_irf, fit_system

PHI = 0.6
SIG = 1.0


def true_irf(Bf, Df, A_h, G_h, H=8):
    """Truth for: s AR(1); F_t = Bf F_{t-1} + Df0 s_t + Df1 s_{t-1}; X_t = A1 X_{t-1} + A2 X_{t-2} + G0 Z_t + G1 Z_{t-1}."""
    s = np.zeros(H + 1); F = np.zeros((H + 1, Bf.shape[0])); X = np.zeros((H + 1, A_h[0].shape[0]))
    for h in range(H + 1):
        s[h] = -SIG if h == 0 else PHI * s[h - 1]
        F[h] = (Bf @ F[h - 1] if h else 0) + Df[0] * s[h] + (Df[1] * s[h - 1] if h else 0)
        Z = lambda j: np.concatenate([F[j], [s[j]]])  # noqa: E731
        X[h] = (A_h[0] @ X[h - 1] if h else 0) + (A_h[1] @ X[h - 2] if h > 1 else 0) \
            + G_h[0] @ Z(h) + (G_h[1] @ Z(h - 1) if h else 0)
    return X, F, s


def simulate_stationary(T, seed):
    rng = np.random.default_rng(seed)
    Bf = np.array([[0.5, 0.1], [0.0, 0.4]])
    Df = [np.array([0.3, -0.2]), np.array([0.1, 0.0])]
    A1 = np.array([[0.5, 0.1], [0.05, 0.3]])
    A2 = np.array([[0.1, 0.0], [0.0, 0.1]])
    G0 = np.array([[0.4, 0.0, -0.2], [0.0, 0.3, 0.1]])
    G1 = np.array([[0.1, 0.1, 0.0], [0.0, 0.0, 0.05]])
    s = np.zeros(T); F = np.zeros((T, 2)); X = np.zeros((T, 2))
    for t in range(2, T):
        s[t] = PHI * s[t - 1] + rng.normal(0, SIG)
        F[t] = Bf @ F[t - 1] + Df[0] * s[t] + Df[1] * s[t - 1] + rng.normal(0, 0.5, 2)
        Z0, Z1 = np.r_[F[t], s[t]], np.r_[F[t - 1], s[t - 1]]
        X[t] = A1 @ X[t - 1] + A2 @ X[t - 2] + G0 @ Z0 + G1 @ Z1 + rng.normal(0, 0.5, 2)
    df = pd.DataFrame(np.column_stack([X, F, s]), columns=["x1", "x2", "f1", "f2", "soi"])
    return df, (Bf, Df, [A1, A2], [G0, G1])


def test_levels_system_recovers_irf():
    df, (Bf, Df, A, G) = simulate_stationary(20000, 1)
    sysm = fit_system(df, ["x1", "x2"], ["f1", "f2"], p=2, q=1, pf=1)
    est = sysm.irf(8)
    X, F, s = true_irf(Bf, Df, A, G, 8)
    assert np.allclose(est[["x1", "x2"]].to_numpy(), X, atol=0.03)
    assert np.allclose(est[["f1", "f2"]].to_numpy(), F, atol=0.03)
    assert abs(sysm.soi.sigma - SIG) < 0.03


def simulate_cointegrated(T, seed):
    """Home X = (x1, x2) cointegrated with an I(1) foreign variable f; r = 1: x1 - f is stationary."""
    rng = np.random.default_rng(seed)
    s = np.zeros(T); f = np.zeros(T); X = np.zeros((T, 2))
    alpha = np.array([-0.3, 0.1])
    for t in range(2, T):
        s[t] = PHI * s[t - 1] + rng.normal(0, SIG)
        f[t] = f[t - 1] + 0.2 * s[t] + rng.normal(0, 0.3)               # I(1) foreign, hit by SOI
        ect = X[t - 1, 0] - f[t - 1]
        dX = alpha * ect + np.array([0.2, 0.0]) * (X[t - 1] - X[t - 2]) + np.array([0.5, 0.1]) * (f[t] - f[t - 1]) \
            + np.array([0.0, -0.3]) * (s[t] - s[t - 1]) + rng.normal(0, 0.3, 2)
        X[t] = X[t - 1] + dX
    df = pd.DataFrame(np.column_stack([X, f, s]), columns=["x1", "x2", "f", "soi"])
    return df, alpha


def test_vecm_recovers_long_run_matrix():
    df, alpha = simulate_cointegrated(20000, 2)
    Y, Z = df[["x1", "x2"]].to_numpy(), df[["f", "soi"]].to_numpy()
    m = VECMX.fit(Y, Z, p=2, q=1, r=1)
    Pi = m.alpha @ m.beta.T                              # columns: x1, x2, f, soi, trend
    true = np.outer(alpha, [1, 0, -1, 0, 0])
    assert np.allclose(Pi[:, :3], true[:, :3], atol=0.02)
    assert m.eigvals[0] > 0.05 and m.eigvals[1] < 0.01  # one clear cointegrating relation


def test_vecm_levels_mapping_matches_fitted_values():
    df, _ = simulate_cointegrated(400, 3)
    Y, Z = df[["x1", "x2"]].to_numpy(), df[["f", "soi"]].to_numpy()
    m = VECMX.fit(Y, Z, p=2, q=1, r=1)
    L = m.levels
    rows = np.arange(2, len(Y))
    fit = np.array([L.c + L.d * t + L.A[0] @ Y[t - 1] + L.A[1] @ Y[t - 2] + L.G[0] @ Z[t] + L.G[1] @ Z[t - 1]
                    for t in rows])
    assert np.allclose(Y[rows] - fit, L.resid, atol=1e-8)


def test_vecm_system_irf_matches_levels_when_full_rank():
    df, _ = simulate_stationary(3000, 4)
    a = fit_system(df, ["x1", "x2"], ["f1", "f2"], p=2, q=1, pf=1)
    b = fit_system(df, ["x1", "x2"], ["f1", "f2"], p=2, q=1, pf=1, rank=2)
    # full-rank VECM with restricted trend = unrestricted levels VARX with trend: identical IRFs
    assert np.allclose(a.irf(8).to_numpy(), b.irf(8).to_numpy(), atol=1e-8)


def test_bootstrap_centres_on_truth():
    df, (Bf, Df, A, G) = simulate_stationary(1500, 5)
    sysm = fit_system(df, ["x1", "x2"], ["f1", "f2"], p=2, q=1, pf=1)
    draws = bootstrap_irf(sysm, p=2, q=1, pf=1, rank=None, H=4, reps=200, seed=1)
    X, _, _ = true_irf(Bf, Df, A, G, 4)
    lo, hi = np.percentile(draws[:, :, :2], [2.5, 97.5], axis=0)
    inside = ((X >= lo) & (X <= hi)).mean()
    assert inside >= 0.8
