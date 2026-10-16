"""Phase 2 gate checks: proxies, vintages, El Niño measures, unit roots, episodes.

Writes output/tables/data_checks.csv, output/tables/unit_roots.csv, output/tables/episodes.csv.
No model estimates here.
"""

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from elnino.data import imf_pnfuel_quarterly, oni_quarterly, soi_quarterly, wb_nonenergy_quarterly  # noqa: E402

warnings.filterwarnings("ignore", category=FutureWarning)

P = ROOT / "data" / "processed"
T = ROOT / "output" / "tables"
v13 = pd.read_parquet(P / "panel_2013v_Philippines.parquet")
v23 = pd.read_parquet(P / "panel_2023v_Philippines.parquet")
rows = []


def corr_row(check, a, b, note=""):
    d = pd.concat([a, b], axis=1).dropna()
    rows.append(dict(check=check, n=len(d), corr=d.corr().iloc[0, 1],
                     mean_abs_diff=(d.iloc[:, 0] - d.iloc[:, 1]).abs().mean(), note=note))


# (a) proxy: World Bank non-energy vs IMF non-fuel, quarterly log changes
wb, imf = np.log(wb_nonenergy_quarterly()), np.log(imf_pnfuel_quarterly())
corr_row("pnf proxy: dln WB non-energy vs dln IMF non-fuel (1992Q2-2026Q3)", wb.diff(), imf.diff())
corr_row("pnf proxy: dln WB vs IMF, 1992Q2-2013Q1 only", wb.diff()[:"2013Q1"], imf.diff()[:"2013Q1"])

# (b) vintage agreement for the Philippines, 1979Q3-2013Q1 (changes for I(1) series)
for v in ["y", "eq", "ep", "r", "ys", "eqs", "rs", "lrs"]:
    corr_row(f"vintage: d{v} 2013v vs 2023v", v13[v].diff(), v23[v].diff()[:"2013Q1"])
for v in ["Dp", "Dps"]:
    corr_row(f"vintage: {v} 2013v vs 2023v", v13[v], v23[v][:"2013Q1"])

# (c) El Niño measures: SOI (anomaly) vs ONI, and vs the standardized SOI block
s_an, s_st = soi_quarterly("anomaly"), soi_quarterly("standardized")
corr_row("SOI anomaly vs ONI, 1979Q1-2023Q3 (expect strongly negative)", v23["soi"], v23["oni"])
corr_row("SOI anomaly vs SOI standardized (linear rescaling; expect 1)", s_an["1979":"2023"], s_st["1979":"2023"])

out = pd.DataFrame(rows)
out.to_csv(T / "data_checks.csv", index=False)
print(out.round(4).to_string())

# (d) unit roots (ADF with constant and trend on levels; constant on changes), 2013 vintage
ur = []
for v in ["y", "Dp", "eq", "ep", "r", "ys", "Dps", "eqs", "rs", "lrs", "poil", "pnf", "soi"]:
    s = v13[v].dropna()
    lv = adfuller(s, regression="ct", autolag="AIC")
    df = adfuller(s.diff().dropna(), regression="c", autolag="AIC")
    ur.append(dict(variable=v, adf_level_ct=lv[0], p_level=lv[1], adf_diff_c=df[0], p_diff=df[1]))
ur = pd.DataFrame(ur)
ur.to_csv(T / "unit_roots.csv", index=False)
print(ur.round(3).to_string())

# (e) El Niño episodes by ONI (>= 0.5 for at least 2 consecutive quarters), full ONI record 1979Q1 onward
o = oni_quarterly()["1979Q1":]
soi_all = soi_quarterly("anomaly")
flag = o >= 0.5
grp = (flag != flag.shift()).cumsum()
ep = []
for _, g in o[flag].groupby(grp[flag]):
    if len(g) >= 2:
        ep.append(dict(start=str(g.index[0]), end=str(g.index[-1]), quarters=len(g), peak_oni=g.max(),
                       min_soi=soi_all.reindex(g.index).min(),
                       strength="very strong" if g.max() >= 2.0 else "strong" if g.max() >= 1.5 else
                       "moderate" if g.max() >= 1.0 else "weak"))
ep = pd.DataFrame(ep)
ep.to_csv(T / "episodes.csv", index=False)
print(ep.to_string())
