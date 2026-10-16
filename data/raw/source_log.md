# Raw data source log

Every file in `data/raw/` is an untouched download. All files were pulled on 2026-10-16 by `scripts/01_download.py`.

| File | Source / URL | Units, base | Coverage | Notes |
| --- | --- | --- | --- | --- |
| `gvar/GVAR_Database_1979Q1-2013Q1.zip` | GVAR 2013 Vintage (Mariscal, Cesa-Bianchi and Rebucci, IDB), via https://sites.google.com/site/gvarmodelling/data → SourceForge | Levels: real GDP index, CPI index, nominal equity index, LCU per USD, short and long rates (% p.a.), oil and metals prices (USD) | 33 countries, 1979Q1–2013Q1, quarterly | **The vintage the reference paper used** (CMR 2015, p. 15, cite the GVAR website and Smith and Galesi 2014). Philippines has no long rate. Also holds trade matrices 1980–2012 and PPP-GDP 1980–2012. sha256 c271267d… |
| `gvar/GVAR_Database_1979Q2-2023Q3.zip` | Mohaddes and Raissi (2024), Mendeley DOI 10.17632/kfp5fhgkvf.1 | Levels plus transformed GVAR series (`GVAR_2023Q3.xls`) | 1979Q2–2023Q3 | Used for the update to 2023 and as a check on the 2013 vintage. Euro area is one unit in this vintage. sha256 4050430c… |
| `gvar/GVAR_Database_1979Q2-2023Q3_documentation.pdf` | http://files.econ.cam.ac.uk/people-files/faculty/km418/ | — | — | Data documentation. |
| `noaa/soi_cpc_monthly.txt` | NOAA Climate Prediction Center, https://www.cpc.ncep.noaa.gov/data/indices/soi | Two blocks: "(STAND TAHITI − STAND DARWIN) SEA LEVEL PRESS ANOMALY" and its STANDARDIZED version | 1951M1–2026M9 | Missing coded −999.9. The reference paper uses NOAA "SOI anomalies". The CPC's current base period may differ from the 2014 vintage they used. |
| `noaa/oni_cpc.txt` | NOAA CPC, https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt | °C, 3-month running mean of the Niño-3.4 anomaly | DJF 1950–JAS 2026 | Robustness measure; positive = El Niño (opposite sign to SOI). |
| `worldbank/CMO-Historical-Data-Monthly_2026-10.xlsx` | World Bank Pink Sheet, updated 2 Oct 2026 | Nominal USD indices, 2010 = 100 | 1960M1–2026M9 | Non-energy index used as the non-fuel commodity price. It substitutes for the IMF index the reference paper used, which starts only in 1992 in the current IMF release (D5). |
| `imf/pcps_G001_PNFUEL_INDEX_M.xml` | IMF Primary Commodity Price System, SDMX API `IMF.RES,PCPS/G001.PNFUEL.INDEX.M` | Nominal USD index | 1992M1–2026M9 | Used only to validate the World Bank substitute over the overlap. |
