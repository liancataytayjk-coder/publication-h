"""Download every raw file, unchanged, into data/raw/. Log each one in data/raw/source_log.md.

Run: python scripts/01_download.py   (skips files that already exist; --force re-downloads)
"""

import hashlib
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

SOURCES = [
    # (path under data/raw, url)
    ("gvar/GVAR_Database_1979Q1-2013Q1.zip",
     "https://sourceforge.net/projects/gvar/files/GVAR%20Database%20%281979Q1-2013Q1%29.zip/download"),
    ("gvar/GVAR_Database_1979Q2-2023Q3.zip",
     "https://data.mendeley.com/public-files/datasets/kfp5fhgkvf/files/6a67972a-4dc1-46a4-8c15-e15550f05b5f/file_downloaded"),
    ("gvar/GVAR_Database_1979Q2-2023Q3_documentation.pdf",
     "http://files.econ.cam.ac.uk/people-files/faculty/km418/GVAR%20Database%20(1979Q2-2023Q3).pdf"),
    ("noaa/soi_cpc_monthly.txt", "https://www.cpc.ncep.noaa.gov/data/indices/soi"),
    ("noaa/oni_cpc.txt", "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"),
    ("worldbank/CMO-Historical-Data-Monthly_2026-10.xlsx",
     "https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx"),
    ("imf/pcps_G001_PNFUEL_INDEX_M.xml",
     "https://api.imf.org/external/sdmx/2.1/data/IMF.RES,PCPS/G001.PNFUEL.INDEX.M?startPeriod=1979"),
]


def main(force=False):
    for rel, url in SOURCES:
        path = RAW / rel
        if path.exists() and not force:
            print("exists ", rel)
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, timeout=120, allow_redirects=True)
        r.raise_for_status()
        path.write_bytes(r.content)
        print("fetched", rel, hashlib.sha256(r.content).hexdigest()[:16])


if __name__ == "__main__":
    main(force="--force" in sys.argv)
