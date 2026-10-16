"""Local projections with the Teulings-Zubanov correction (as in Kpodar and Liu 2022, eq. 1).

For each horizon h the outcome y_{t+h} is regressed on p lags of y and of the
shock x, the shock x_t, the Teulings-Zubanov leads x_{t+1}, ..., x_{t+h-1},
optional controls (contemporaneous plus p lags), a linear time trend and,
for panels, unit fixed effects. beta_h is the coefficient on x_t.

The lead set follows Annex Tables 1-2 of the reference paper: no lead at h = 0
or h = 1, leads 1..h-1 thereafter. Change the lead range in _design() if your
reference paper differs, and log it in the decisions log.

Copy into the project package (e.g. <pkg>/lp.py). Requires pandas, numpy,
statsmodels, linearmodels, scipy.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm
from linearmodels.panel import PanelOLS
from scipy import stats


def _design(df, y, x, unit, time, h, p, controls, interact, cumulative, tz, exog=()):
    g = df.groupby(unit, sort=False) if unit else None

    def shift(col, k):
        return g[col].shift(k) if g is not None else df[col].shift(k)

    out = pd.DataFrame(index=df.index)
    if cumulative:
        out["dep"] = sum(shift(y, -j) for j in range(h + 1))
    else:
        out["dep"] = shift(y, -h)
    out["shock"] = df[x]
    for name in interact:
        out[f"shock_x_{name}"] = df[x] * df[name]
    for q in range(1, p + 1):
        out[f"{y}_l{q}"] = shift(y, q)
        out[f"{x}_l{q}"] = shift(x, q)
    if tz:
        for lead in range(1, h):
            out[f"{x}_f{lead}"] = shift(x, -lead)
    for c in controls:
        out[c] = df[c]
        for q in range(1, p + 1):
            out[f"{c}_l{q}"] = shift(c, q)
    for c in exog:
        out[c] = df[c]
    out["trend"] = df[time]
    return out


def local_projection(
    df: pd.DataFrame,
    y: str,
    x: str,
    time: str,
    unit: str | None = None,
    horizons: int = 12,
    p: int = 12,
    controls: tuple[str, ...] = (),
    interact: tuple[str, ...] = (),
    exog: tuple[str, ...] = (),
    sample: pd.Series | None = None,
    cumulative: bool = False,
    tz: bool = True,
    trend: bool = True,
    se: str = "cluster",
    level: float = 0.90,
) -> pd.DataFrame:
    """Estimate beta_h for h = 0..horizons.

    df must be sorted by unit then time with consecutive months (gaps as NaN).
    `time` is an integer month counter used for the trend and panel index.
    controls enter with p lags; exog (e.g. dummies) enter contemporaneously only.
    sample: boolean mask on df rows; observations outside it are dropped after
    lags and leads are built, so pre-sample data still supply the lags.
    se: 'cluster' (by unit), 'robust', 'driscoll_kraay' (panels) or
    'newey_west' (single series, h + 1 lags).
    Returns one row per horizon and coefficient of interest ('shock' and each
    'shock_x_<name>').
    """
    z = stats.norm.ppf(0.5 + level / 2)
    rows = []
    for h in range(horizons + 1):
        d = _design(df, y, x, unit, time, h, p, list(controls), list(interact), cumulative, tz, list(exog))
        if sample is not None:
            d = d[sample.reindex(d.index).fillna(False).astype(bool)]
        if not trend:
            d = d.drop(columns="trend")
        if unit:
            d[unit] = df[unit]
        d = d.dropna()
        regs = [c for c in d.columns if c not in ("dep", unit)]
        regs = [c for c in regs if d[c].nunique() > 1]  # drop dummies with no variation in sample
        if unit:
            idx = pd.MultiIndex.from_arrays([d[unit], df.loc[d.index, time]])
            mod = PanelOLS(d["dep"].set_axis(idx), d[regs].set_axis(idx).assign(const=1.0),
                           entity_effects=True, drop_absorbed=True)
            kw = {"cluster": dict(cov_type="clustered", cluster_entity=True),
                  "robust": dict(cov_type="robust"),
                  "driscoll_kraay": dict(cov_type="kernel", kernel="bartlett", bandwidth=h + 1)}[se]
            res = mod.fit(**kw)
            params, ses, nobs, r2 = res.params, res.std_errors, res.nobs, res.rsquared_within
            n_units = d[unit].nunique()
        else:
            X = sm.add_constant(d[regs])
            if se == "newey_west":
                res = sm.OLS(d["dep"], X).fit(cov_type="HAC", cov_kwds={"maxlags": h + 1})
            else:
                res = sm.OLS(d["dep"], X).fit(cov_type="HC1")
            params, ses, nobs, r2 = res.params, res.bse, int(res.nobs), res.rsquared_adj
            n_units = 1
        for term in ["shock"] + [f"shock_x_{n}" for n in interact]:
            b, s = params[term], ses[term]
            rows.append(dict(h=h, term=term, beta=b, se=s, lo=b - z * s, hi=b + z * s,
                             nobs=nobs, n_units=n_units, r2=r2))
    return pd.DataFrame(rows)
