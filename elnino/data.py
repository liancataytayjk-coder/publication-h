"""Read the raw files and build the quarterly series used by the Philippine VARX* model.

GVAR transformations follow Dees, di Mauro, Pesaran and Smith (2007) and the GVAR
Toolbox 2.0 (Smith and Galesi 2014), which the reference paper used:

    y  = ln(RGDP)                 log real GDP
    Dp = ln(CPI_t) - ln(CPI_t-1)  quarterly inflation (log change)
    eq = ln(nomEQ / CPI)          log real equity prices
    ep = ln(FXdol) - ln(CPI)      log real exchange rate (LCU per USD deflated by domestic CPI)
    r  = 0.25 ln(1 + Rshort/100)  short rate, quarterly
    lr = 0.25 ln(1 + Rlong/100)   long rate, quarterly

Foreign ("star") variables are trade-weighted averages over the other 20 units of the
reference paper's GVAR: 7 Asia-Pacific economies other than the home country, 3 North
American, 5 South American, 2 Middle East/Africa, and one Europe region of 13 countries
built with PPP-GDP weights. Weights are 2009-2011 averages (CMR eq. 3).
"""

from __future__ import annotations

import io
import re
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

EUROPE = ["Austria", "Belgium", "Finland", "France", "Germany", "Italy", "Netherlands",
          "Norway", "Spain", "Sweden", "Switzerland", "Turkey", "UK"]
CODES = {"China": 160, "Austria": 122, "Belgium": 124, "Finland": 172, "France": 132, "Germany": 134,
         "Italy": 136, "Netherlands": 138, "Spain": 184, "Japan": 158, "Argentina": 213, "Brazil": 223,
         "Chile": 228, "Mexico": 273, "Peru": 293, "Australia": 193, "Canada": 156, "New Zealand": 196,
         "Indonesia": 536, "Korea": 542, "Malaysia": 548, "Philippines": 566, "Singapore": 576,
         "Thailand": 578, "India": 534, "South Africa": 199, "Saudi Arabia": 456, "Turkey": 186,
         "Norway": 142, "Sweden": 144, "Switzerland": 146, "UK": 112, "USA": 110}
STAR_VARS = ["y", "Dp", "eq", "r", "lr"]
WEIGHT_YEARS = (2009, 2010, 2011)


def _zip_member(zpath, pattern):
    z = zipfile.ZipFile(zpath)
    name = next(n for n in z.namelist() if re.search(pattern, n))
    return io.BytesIO(z.read(name))


# ---------------------------------------------------------------- GVAR 2013 vintage
def gvar2013_levels() -> dict[str, pd.DataFrame]:
    """Raw level data per country, indexed by quarterly period."""
    zp = RAW / "gvar" / "GVAR_Database_1979Q1-2013Q1.zip"
    xl = pd.ExcelFile(_zip_member(zp, r"Country Data.*\.xlsx$"))
    out = {}
    for s in xl.sheet_names:
        d = pd.read_excel(xl, sheet_name=s)
        d.index = pd.PeriodIndex(d.pop("date"), freq="Q")
        name = {"China ": "China"}.get(s, s)
        out[name] = d
    return out


def transform(d: pd.DataFrame) -> pd.DataFrame:
    """GVAR transformations; non-positive levels and empty series become missing."""
    pos = lambda s: s.where(s > 0)  # noqa: E731
    cpi = pos(d["CPI"])
    t = pd.DataFrame(index=d.index)
    t["y"] = np.log(pos(d["RGDP"]))
    t["Dp"] = np.log(cpi).diff()
    t["eq"] = np.log(pos(d["nomEQ"]) / cpi)
    t["ep"] = np.log(pos(d["FXdol"])) - np.log(cpi)
    t["r"] = 0.25 * np.log1p(d["Rshort"] / 100)
    t["lr"] = 0.25 * np.log1p(d["Rlong"] / 100)
    return t


def ppp_weights_2013() -> pd.Series:
    zp = RAW / "gvar" / "GVAR_Database_1979Q1-2013Q1.zip"
    w = pd.read_excel(_zip_member(zp, r"PPP-GDP.*\.xls$"), sheet_name="WDI")
    w = w.set_index("Country Name")
    w.index = w.index.str.strip().str.replace("Korea, Rep.", "Korea", regex=False)
    cols = [f"YR{y}" for y in WEIGHT_YEARS]
    v = w[cols].apply(pd.to_numeric, errors="coerce").mean(axis=1)
    v = v.rename(index={"United Kingdom": "UK", "United States": "USA"})
    return v


def trade_weights_2013(home: str) -> pd.Series:
    """w_ij = sum_y T_ij,y / sum_y T_i,y over 2009-2011 (row = reporting country i)."""
    zp = RAW / "gvar" / "GVAR_Database_1979Q1-2013Q1.zip"
    m = pd.read_excel(_zip_member(zp, r"Trade Matrices.*\.xls$"))
    m = m[(m["year"].isin(WEIGHT_YEARS)) & (m["country_primary"] == CODES[home])]
    inv = {v: k for k, v in CODES.items()}
    tot = {inv[int(c.strip("_"))]: m[c].sum() for c in m.columns if c.startswith("_") and int(c.strip("_")) != CODES[home]}
    s = pd.Series(tot)
    return s / s.sum()


def europe_region(tr: dict[str, pd.DataFrame], ppp: pd.Series) -> pd.DataFrame:
    """PPP-GDP-weighted Europe aggregate; weights renormalised over members with data."""
    out = pd.DataFrame(index=next(iter(tr.values())).index)
    for v in ["y", "Dp", "eq", "ep", "r", "lr"]:
        avail = [c for c in EUROPE if tr[c][v].notna().sum() > 0]
        w = ppp[avail] / ppp[avail].sum()
        out[v] = sum(w[c] * tr[c][v] for c in avail)
    return out


def star_variables(units: dict[str, pd.DataFrame], weights: pd.Series) -> pd.DataFrame:
    """x*_t = sum_j w_j x_jt; for each variable, weights renormalised over units that have it."""
    out = pd.DataFrame(index=next(iter(units.values())).index)
    for v in STAR_VARS:
        avail = [u for u in weights.index if units[u][v].notna().sum() > 0]
        w = weights[avail] / weights[avail].sum()
        out[v + "s"] = sum(w[u] * units[u][v] for u in avail)
        out.attrs[v + "s_coverage"] = float(weights[avail].sum())
    return out


def units_2013(home: str):
    """The 21 GVAR units (Europe aggregated) and the home country's 20-unit trade weights."""
    lev = gvar2013_levels()
    tr = {c: transform(d) for c, d in lev.items()}
    ppp = ppp_weights_2013()
    units = {c: tr[c] for c in tr if c not in EUROPE}
    units["Europe"] = europe_region(tr, ppp)
    w = trade_weights_2013(home)
    w_units = w.drop(EUROPE, errors="ignore")
    w_units["Europe"] = w[[c for c in EUROPE if c in w.index]].sum()
    return lev, units, w_units


# ---------------------------------------------------------------- global variables
def soi_quarterly(block="anomaly") -> pd.Series:
    """Quarterly mean of NOAA CPC monthly SOI (block 'anomaly' or 'standardized')."""
    txt = (RAW / "noaa" / "soi_cpc_monthly.txt").read_text()
    parts = txt.split("STANDARDIZED")
    body = parts[0] if block == "anomaly" else parts[1]
    rows = []
    for line in body.splitlines():
        if re.match(r"^\d{4}", line):
            year = int(line[:4])
            vals = [float(line[4 + 6 * k: 10 + 6 * k]) for k in range(12)]
            for m, v in enumerate(vals, 1):
                rows.append((pd.Period(year=year, month=m, freq="M"), np.nan if v <= -999 else v))
    s = pd.Series(dict(rows)).sort_index()
    q = s.groupby(s.index.asfreq("Q")).agg(lambda x: x.mean() if x.notna().all() else np.nan)
    return q.rename("soi")


def oni_quarterly() -> pd.Series:
    """ONI by quarter: the 3-month season centred on the quarter's middle month (JFM, AMJ, JAS, OND)."""
    d = pd.read_csv(RAW / "noaa" / "oni_cpc.txt", sep=r"\s+")
    centre = {"DJF": 1, "JFM": 2, "FMA": 3, "MAM": 4, "AMJ": 5, "MJJ": 6,
              "JJA": 7, "JAS": 8, "ASO": 9, "SON": 10, "OND": 11, "NDJ": 12}
    d["p"] = [pd.Period(year=int(y), month=centre[s], freq="M") for s, y in zip(d["SEAS"], d["YR"])]
    s = d.set_index("p")["ANOM"]
    # quarter value = ONI season centred on the quarter's middle month (Feb, May, Aug, Nov)
    s = s[s.index.month.isin([2, 5, 8, 11])]
    s.index = s.index.asfreq("Q")
    return s.rename("oni")


def wb_nonenergy_quarterly() -> pd.Series:
    f = RAW / "worldbank" / "CMO-Historical-Data-Monthly_2026-10.xlsx"
    d = pd.read_excel(f, sheet_name="Monthly Indices", header=None, skiprows=9)
    d = d[d[0].astype(str).str.match(r"^\d{4}M\d{2}$")]
    p = pd.PeriodIndex([pd.Period(year=int(x[:4]), month=int(x[5:]), freq="M") for x in d[0]])
    s = pd.Series(pd.to_numeric(d[3], errors="coerce").values, index=p)  # column 3 = Non-energy
    return s.groupby(s.index.asfreq("Q")).mean().rename("pnf_nom")


def imf_pnfuel_quarterly() -> pd.Series:
    txt = (RAW / "imf" / "pcps_G001_PNFUEL_INDEX_M.xml").read_text()
    obs = re.findall(r'TIME_PERIOD="(\d{4})-M(\d{2})" OBS_VALUE="([\d.Ee+-]+)"', txt)
    s = pd.Series({pd.Period(year=int(y), month=int(m), freq="M"): float(v) for y, m, v in obs}).sort_index()
    return s.groupby(s.index.asfreq("Q")).mean().rename("pnf_imf_nom")


# ---------------------------------------------------------------- analysis frame
def build_country_2013(home: str) -> pd.DataFrame:
    """Domestic, star and global variables for `home` from the 2013 vintage."""
    lev, units, w = units_2013(home)
    dom = units[home][["y", "Dp", "eq", "ep", "r", "lr"]].dropna(axis=1, how="all")
    star = star_variables({k: v for k, v in units.items() if k != home}, w)
    us_cpi = lev["USA"]["CPI"]
    glob = pd.DataFrame(index=dom.index)
    glob["poil"] = np.log(lev["USA"]["POILdol"] / us_cpi)  # real oil price (Brent, USD / US CPI)
    pnf = wb_nonenergy_quarterly().reindex(dom.index)
    glob["pnf"] = np.log(pnf / us_cpi)
    soi = soi_quarterly("anomaly")
    glob["soi"] = soi.reindex(dom.index)
    glob["oni"] = oni_quarterly().reindex(dom.index)
    df = pd.concat([dom, star, glob], axis=1)
    df.attrs["weights"] = w.to_dict()
    df.attrs["coverage"] = {k: v for k, v in star.attrs.items()}
    return df


# ---------------------------------------------------------------- GVAR 2023 vintage
def build_country_2023(home: str) -> pd.DataFrame:
    """Domestic and star variables as published in the 2023 vintage (Mohaddes and Raissi 2024),
    plus the same global variables as the 2013 build. Star variables are theirs, not rebuilt."""
    zp = RAW / "gvar" / "GVAR_Database_1979Q2-2023Q3.zip"
    xl = pd.ExcelFile(_zip_member(zp, r"Country Data.*\.xls$"))
    d = pd.read_excel(xl, sheet_name=home.upper())
    d.index = pd.PeriodIndex(d.pop("date"), freq="Q")
    keep = [c for c in ["y", "Dp", "eq", "ep", "r", "lr", "ys", "Dps", "eqs", "rs", "lrs"] if c in d]
    df = d[keep].copy()
    us = pd.read_excel(xl, sheet_name="USA")
    us.index = pd.PeriodIndex(us.pop("date"), freq="Q")
    # US price level from US inflation: ln P_t = cumulative sum of Dp (normalised at 1979Q2 = 0)
    lnp_us = us["Dp"].fillna(0).cumsum()
    df["poil"] = d["poil"] - lnp_us
    pnf = wb_nonenergy_quarterly().reindex(df.index)
    df["pnf"] = np.log(pnf) - lnp_us
    df["soi"] = soi_quarterly("anomaly").reindex(df.index)
    df["oni"] = oni_quarterly().reindex(df.index)
    return df
