"""Small-open-economy VARX* system for one GVAR country, with an exogenous El Niño (SOI) shock.

The system has three blocks, estimated separately and solved together:

1. SOI (dominant, causal):         s_t = a + phi s_{t-1} + e_t                         (AR(1), CMR p. 16)
2. Foreign block F_t = (x*_t, poil_t, pnf_t), driven by SOI but not by the home country:
                                   F_t = c + d t + sum_{l=1}^{pf} B_l F_{t-l} + sum_{l=0}^{1} D_l s_{t-l} + v_t
   This replaces the rest of the GVAR. A small economy like the Philippines does not move world
   output, prices or rates, so its foreign variables are modelled as a block that responds to
   El Niño but not to Philippine shocks (block exogeneity).
3. Home VARX*(p, q) with weakly exogenous Z_t = (F_t, s_t), as in CMR eq. (10):
                                   X_t = c + d t + sum_{l=1}^{p} Phi_l X_{t-l} + sum_{l=0}^{q} Lam_l Z_{t-l} + u_t
   estimated either unrestricted in levels, or as the error-correction form (VECMX*) with r
   cointegrating relations, unrestricted intercept and restricted trend (Pesaran, Shin and Smith
   2000, case IV; the GVAR Toolbox default), by reduced-rank regression.

Impulse response: e_0 = -1 standard error of the SOI residual (an El Niño), all other shocks zero.
Because every block includes s_t and s_{t-1} as regressors, their residuals are orthogonal to e_t,
so this response equals the generalised impulse response used in the GVAR.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


# ----------------------------------------------------------------------------- helpers
def _lag(a: np.ndarray, k: int) -> np.ndarray:
    out = np.full_like(a, np.nan, dtype=float)
    if k == 0:
        return a.astype(float).copy()
    out[k:] = a[:-k]
    return out


def _ols(Y, X):
    B, *_ = np.linalg.lstsq(X, Y, rcond=None)
    U = Y - X @ B
    return B, U


# ----------------------------------------------------------------------------- blocks
@dataclass
class AR1:
    a: float
    phi: float
    sigma: float
    resid: np.ndarray

    @classmethod
    def fit(cls, s: np.ndarray):
        Y, X = s[1:], np.column_stack([np.ones(len(s) - 1), s[:-1]])
        B, U = _ols(Y, X)
        return cls(B[0], B[1], float(np.sqrt(U @ U / (len(U) - 2))), U)


@dataclass
class LevelsVARX:
    """Y_t = c + d t + sum_{l=1}^{p} A_l Y_{t-l} + sum_{l=0}^{q} G_l Z_{t-l} + u_t (OLS, equation by equation)."""
    p: int
    q: int
    c: np.ndarray
    d: np.ndarray
    A: list
    G: list
    resid: np.ndarray
    trend: bool = True
    first: int = 0  # first usable row in the estimation arrays

    @classmethod
    def fit(cls, Y: np.ndarray, Z: np.ndarray, p: int, q: int, trend: bool = True):
        T, k = Y.shape
        m = max(p, q)
        rows = np.arange(m, T)
        cols = [np.ones(len(rows))]
        if trend:
            cols.append(rows.astype(float))
        cols += [Y[rows - l] for l in range(1, p + 1)]
        cols += [Z[rows - l] for l in range(0, q + 1)]
        X = np.column_stack([c if c.ndim == 2 else c[:, None] for c in cols])
        B, U = _ols(Y[rows], X)
        i = 0
        c = B[i]; i += 1
        d = B[i] if trend else np.zeros(k)
        i += 1 if trend else 0
        A = [B[i + k * j: i + k * (j + 1)].T for j in range(p)]
        i += k * p
        kz = Z.shape[1]
        G = [B[i + kz * j: i + kz * (j + 1)].T for j in range(q + 1)]
        return cls(p, q, c, d, A, G, U, trend, m)

    def aic(self) -> float:
        T, k = self.resid.shape
        S = self.resid.T @ self.resid / T
        npar = k * (1 + int(self.trend) + k * self.p + self.G[0].shape[1] * (self.q + 1))
        return float(np.log(np.linalg.det(S)) + 2 * npar / T)


@dataclass
class VECMX:
    """Conditional VECMX*(p, q) with r cointegrating relations, case IV (restricted trend).

    DX_t = c + alpha beta' (z_{t-1}; t-1) + sum_{l=0}^{q-1} L_l DZ_{t-l} + sum_{l=1}^{p-1} P_l DX_{t-l} + u_t
    with z = (X, Z). Estimated by reduced-rank regression (Johansen 1991; Pesaran, Shin and Smith 2000).
    Stored as its levels VARX representation so the same impulse-response code applies.
    """
    r: int
    levels: LevelsVARX
    alpha: np.ndarray
    beta: np.ndarray
    eigvals: np.ndarray

    @classmethod
    def fit(cls, Y: np.ndarray, Z: np.ndarray, p: int, q: int, r: int):
        T, k = Y.shape
        kz = Z.shape[1]
        z = np.column_stack([Y, Z])
        dY, dZ = np.diff(Y, axis=0, prepend=np.nan), np.diff(Z, axis=0, prepend=np.nan)
        m = max(p, q)  # need Y_{t-p}, Z_{t-q} in levels
        rows = np.arange(m, T)
        W = [np.ones(len(rows))]
        W += [dZ[rows - l] for l in range(0, q)]          # DZ_t ... DZ_{t-q+1}
        W += [dY[rows - l] for l in range(1, p)]          # DY_{t-1} ... DY_{t-p+1}
        W = np.column_stack([w if w.ndim == 2 else w[:, None] for w in W])
        Z1 = np.column_stack([z[rows - 1], (rows - 1).astype(float)])  # levels and restricted trend
        Y0 = dY[rows]
        _, R0 = _ols(Y0, W)
        _, R1 = _ols(Z1, W)
        n = len(rows)
        S00, S01, S11 = R0.T @ R0 / n, R0.T @ R1 / n, R1.T @ R1 / n
        # generalised eigenproblem |lam S11 - S10 S00^-1 S01| = 0 via Cholesky of S11
        Lc = np.linalg.cholesky(S11)
        Li = np.linalg.inv(Lc)
        M = Li @ S01.T @ np.linalg.solve(S00, S01) @ Li.T
        lam, V = np.linalg.eigh(M)
        order = np.argsort(lam)[::-1]
        lam, V = lam[order], V[:, order]
        beta = Li.T @ V[:, :r]                           # normalised so beta' S11 beta = I
        ect = Z1 @ beta
        X2 = np.column_stack([ect, W])
        B, U = _ols(Y0, X2)
        alpha = B[:r].T                                  # k x r
        c = B[r]
        i = r + 1
        Ls = [B[i + kz * j: i + kz * (j + 1)].T for j in range(q)]
        i += kz * q
        Ps = [B[i + k * j: i + k * (j + 1)].T for j in range(p - 1)]
        Pi = alpha @ beta.T                              # k x (k + kz + 1)
        Pi_y, Pi_z, Pi_t = Pi[:, :k], Pi[:, k:k + kz], Pi[:, -1]
        # levels representation: X_t = c' + d t + sum A_l X_{t-l} + sum G_l Z_{t-l}
        A = [np.zeros((k, k)) for _ in range(p)]
        A[0] += np.eye(k) + Pi_y
        for j, P in enumerate(Ps, start=1):              # P_j DX_{t-j} = P_j X_{t-j} - P_j X_{t-j-1}
            A[j - 1] += P
            A[j] -= P
        G = [np.zeros((k, kz)) for _ in range(q + 1)]
        G[1] += Pi_z
        for j, L in enumerate(Ls):                       # L_j DZ_{t-j}
            G[j] += L
            G[j + 1] -= L
        # trend: Pi_t (t-1) = Pi_t t - Pi_t
        lev = LevelsVARX(p, q, c - Pi_t, Pi_t, A, G, U, True, m)
        return cls(r, lev, alpha, beta, lam)


# ----------------------------------------------------------------------------- system
@dataclass
class System:
    home: list
    foreign: list
    soi: AR1
    fblock: LevelsVARX
    hblock: LevelsVARX | VECMX
    data: pd.DataFrame = field(repr=False)

    @property
    def hlev(self) -> LevelsVARX:
        return self.hblock.levels if isinstance(self.hblock, VECMX) else self.hblock

    def irf(self, H: int = 12, shock: float | None = None) -> pd.DataFrame:
        """Responses of all variables to an El Niño (negative SOI) shock of one residual s.e."""
        e0 = -self.soi.sigma if shock is None else shock
        kf, kh = len(self.foreign), len(self.home)
        s = np.zeros(H + 1); F = np.zeros((H + 1, kf)); X = np.zeros((H + 1, kh))
        fb, hb = self.fblock, self.hlev
        for h in range(H + 1):
            s[h] = (self.soi.phi * s[h - 1] if h else 0.0) + (e0 if h == 0 else 0.0)
            f = sum(fb.A[l - 1] @ F[h - l] for l in range(1, fb.p + 1) if h - l >= 0)
            f = f + sum(fb.G[l][:, 0] * s[h - l] for l in range(0, fb.q + 1) if h - l >= 0)
            F[h] = f
            Zh = lambda j: np.concatenate([F[j], [s[j]]])  # noqa: E731
            x = sum(hb.A[l - 1] @ X[h - l] for l in range(1, hb.p + 1) if h - l >= 0)
            x = x + sum(hb.G[l] @ Zh(h - l) for l in range(0, hb.q + 1) if h - l >= 0)
            X[h] = x
        out = pd.DataFrame(np.column_stack([X, F, s]), columns=self.home + self.foreign + ["soi"])
        out.index.name = "h"
        return out


def fit_system(df: pd.DataFrame, home: list, foreign: list, p: int = 2, q: int = 1, pf: int = 2,
               rank: int | None = None, soi: str = "soi") -> System:
    """Estimate the three blocks on the rows of df with no missing values (contiguous sample)."""
    d = df[home + foreign + [soi]].dropna()
    assert (d.index[1:] - d.index[:-1] == d.index.freq * 1).all() if hasattr(d.index, "freq") else True
    Y, F, s = d[home].to_numpy(float), d[foreign].to_numpy(float), d[soi].to_numpy(float)
    ar = AR1.fit(s)
    fb = LevelsVARX.fit(F, s[:, None], p=pf, q=1, trend=True)
    Z = np.column_stack([F, s])
    hb = VECMX.fit(Y, Z, p, q, rank) if rank is not None else LevelsVARX.fit(Y, Z, p, q, trend=True)
    return System(home, foreign, ar, fb, hb, d)


# ----------------------------------------------------------------------------- bootstrap
def simulate_from(system: System, rng: np.random.Generator) -> pd.DataFrame:
    """Recursive residual bootstrap: resample residual vectors jointly by date, rebuild the data."""
    d = system.data
    T = len(d)
    fb, hb, ar = system.fblock, system.hlev, system.soi
    kf, kh = len(system.foreign), len(system.home)
    m_f, m_h = fb.first, hb.first
    m = max(m_f, m_h, 1)
    # align residuals on common dates t = m..T-1
    e = ar.resid[m - 1:]
    v = fb.resid[m - m_f:]
    u = hb.resid[m - m_h:]
    n = min(len(e), len(v), len(u))
    e, v, u = e[-n:], v[-n:], u[-n:]
    idx = rng.integers(0, n, size=T)
    s = d["soi"].to_numpy(float).copy() if "soi" in d else d.iloc[:, -1].to_numpy(float).copy()
    F = d[system.foreign].to_numpy(float).copy()
    X = d[system.home].to_numpy(float).copy()
    for t in range(m, T):
        j = idx[t]
        s[t] = ar.a + ar.phi * s[t - 1] + e[j]
        f = fb.c + fb.d * t + v[j]
        f = f + sum(fb.A[l - 1] @ F[t - l] for l in range(1, fb.p + 1))
        f = f + sum(fb.G[l][:, 0] * s[t - l] for l in range(0, fb.q + 1))
        F[t] = f
        Z = lambda k: np.concatenate([F[k], [s[k]]])  # noqa: E731
        x = hb.c + hb.d * t + u[j]
        x = x + sum(hb.A[l - 1] @ X[t - l] for l in range(1, hb.p + 1))
        x = x + sum(hb.G[l] @ Z(t - l) for l in range(0, hb.q + 1))
        X[t] = x
    out = pd.DataFrame(np.column_stack([X, F, s]), columns=system.home + system.foreign + ["soi"], index=d.index)
    return out


def bootstrap_irf(system: System, p: int, q: int, pf: int, rank: int | None, H: int = 12,
                  reps: int = 1000, seed: int = 20261016) -> np.ndarray:
    """Array (reps, H+1, n_vars) of bootstrap IRFs; each replication re-estimates every block.
    The shock is one s.e. of the SOI residual estimated in that replication."""
    rng = np.random.default_rng(seed)
    draws = []
    for _ in range(reps):
        sim = simulate_from(system, rng)
        try:
            b = fit_system(sim, system.home, system.foreign, p=p, q=q, pf=pf, rank=rank)
            draws.append(b.irf(H).to_numpy())
        except np.linalg.LinAlgError:
            continue
    return np.array(draws)


def companion_max_root(lev: LevelsVARX) -> float:
    k = lev.A[0].shape[0]
    p = lev.p
    C = np.zeros((k * p, k * p))
    C[:k, :] = np.hstack(lev.A)
    if p > 1:
        C[k:, :-k] = np.eye(k * (p - 1))
    return float(np.max(np.abs(np.linalg.eigvals(C))))
