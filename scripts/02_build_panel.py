"""Build the analysis frames from data/raw/ and save them to data/processed/.

2013 vintage (the reference paper's data): Philippines, plus Indonesia and Thailand for the
method cross-check. 2023 vintage: Philippines, for the update.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from elnino.data import build_country_2013, build_country_2023  # noqa: E402

OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

meta = {}
for c in ["Philippines", "Indonesia", "Thailand"]:
    df = build_country_2013(c)
    meta[c] = {"weights_2009_2011": df.attrs["weights"], "star_coverage": df.attrs["coverage"]}
    df.attrs = {}
    df.to_parquet(OUT / f"panel_2013v_{c}.parquet")
    print(c, "2013v", df.index[0], df.index[-1], df.shape)

df = build_country_2023("Philippines")
df.to_parquet(OUT / "panel_2023v_Philippines.parquet")
print("Philippines 2023v", df.index[0], df.index[-1], df.shape)

(ROOT / "output" / "tables").mkdir(parents=True, exist_ok=True)
(ROOT / "output" / "tables" / "trade_weights_2013v.json").write_text(json.dumps(meta, indent=1))
