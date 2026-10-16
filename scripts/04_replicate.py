"""Replication gate (pre-registered 2026-10-16 in CLAUDE.md): CMR (2017) Philippine results.

Writes output/tables/replication_irf.csv (all IRFs with bootstrap bands) and
output/tables/replication_gate.csv (each criterion: target, estimate, pass/fail).
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from elnino.varx import LevelsVARX, bootstrap_irf, companion_max_root, fit_system  # noqa: E402

P, T = ROOT / "data" / "processed", ROOT / "output" / "tables"
H, REPS = 12, 1000
FOREIGN = ["ys", "Dps", "eqs", "rs", "lrs", "poil", "pnf"]
SPEC = {  # CMR Table 2: (p, q, r)
    "Philippines": (2, 1, 2),
    "Indonesia": (2, 1, 3),
    "Thailand": (1, 1, 1),
}


def choose_pf(d, foreign):
    """AIC over p_f in {1, 2} on a common effective sample (CMR: AIC, maximum lag 2)."""
    F, s = d[foreign].to_numpy(float), d[["soi"]].to_numpy(float)
    a1 = LevelsVARX.fit(F[1:], s[1:], p=1, q=1).aic()
    a2 = LevelsVARX.fit(F, s, p=2, q=1).aic()
    return (1 if a1 <= a2 else 2), a1, a2


def summarise(draws, point, cols, country, model):
    rows = []
    for j, v in enumerate(cols):
        for h in range(draws.shape[1]):
            x = draws[:, h, j]
            rows.append(dict(country=country, model=model, variable=v, h=h, point=point[h, j],
                             median=np.median(x), p05=np.percentile(x, 5), p16=np.percentile(x, 16),
                             p84=np.percentile(x, 84), p95=np.percentile(x, 95)))
    return rows


def run(country, rank):
    df = pd.read_parquet(P / f"panel_2013v_{country}.parquet").loc["1979Q2":"2013Q1"]
    home = [c for c in ["y", "Dp", "eq", "ep", "r", "lr"] if c in df and df[c].notna().all()]
    d = df[home + FOREIGN + ["soi"]]
    assert d.notna().all().all(), d.isna().sum()
    p, q, r = SPEC[country]
    pf, a1, a2 = choose_pf(d, FOREIGN)
    sysm = fit_system(d, home, FOREIGN, p=p, q=q, pf=pf, rank=rank)
    point = sysm.irf(H)
    draws = bootstrap_irf(sysm, p=p, q=q, pf=pf, rank=rank, H=H, reps=REPS)
    cols = list(point.columns)
    point_np = point.to_numpy() * 100
    draws = draws * 100
    model = f"VECMX*({p},{q}) r={rank}" if rank else f"levels VARX*({p},{q})"
    rows = summarise(draws, point_np, cols, country, model)
    # secondary reading of Table 7: running sum of the inflation response
    j = cols.index("Dp")
    cum = np.cumsum(draws[:, :, j], axis=1)
    rows += summarise(cum[:, :, None], np.cumsum(point_np[:, j])[:, None], ["Dp_cumsum"], country, model)
    info = dict(country=country, model=model, nobs=len(sysm.hlev.resid), pf=pf, aic_pf1=a1, aic_pf2=a2,
                soi_phi=sysm.soi.phi, soi_sigma=sysm.soi.sigma, reps_ok=len(draws),
                max_root_home=companion_max_root(sysm.hlev), max_root_foreign=companion_max_root(sysm.fblock),
                home=",".join(home))
    return rows, info


def main():
    rows, infos = [], []
    for c, (p, q, r) in SPEC.items():
        for rank in (r, None):
            rr, info = run(c, rank)
            rows += rr
            infos.append(info)
            print(info)
    irf = pd.DataFrame(rows)
    irf.to_csv(T / "replication_irf.csv", index=False)
    pd.DataFrame(infos).to_csv(T / "replication_models.csv", index=False)

    def get(c, model_prefix, v, h, stat):
        m = irf[(irf.country == c) & irf.model.str.startswith(model_prefix) & (irf.variable == v) & (irf.h == h)]
        return float(m[stat].iloc[0])

    V = "VECMX*"
    g = []
    ph_band = [(get("Philippines", V, "y", h, "p16"), get("Philippines", V, "y", h, "p84")) for h in range(5)]
    g.append(dict(id="G1a", criterion="PH GDP: 16-84% band contains 0 at h=0..4", target="not significant",
                  estimate="; ".join(f"h{h}:[{lo:.2f},{hi:.2f}]" for h, (lo, hi) in enumerate(ph_band)),
                  passed=all(lo <= 0 <= hi for lo, hi in ph_band)))
    y4 = get("Philippines", V, "y", 4, "median")
    g.append(dict(id="G1b", criterion="PH GDP median h=4 in [-0.29, 0.71]", target=0.21, estimate=round(y4, 3),
                  passed=-0.29 <= y4 <= 0.71))
    p0 = get("Philippines", V, "Dp", 0, "median")
    g.append(dict(id="G2a", criterion="PH inflation median h=0 > 0", target=0.11, estimate=round(p0, 3), passed=p0 > 0))
    p4 = get("Philippines", V, "Dp", 4, "median")
    g.append(dict(id="G2b", criterion="PH inflation median h=4 in [0.02, 0.52]", target=0.27, estimate=round(p4, 3),
                  passed=0.02 <= p4 <= 0.52))
    iy4, ilo, ihi = (get("Indonesia", V, "y", 4, s) for s in ("median", "p16", "p84"))
    g.append(dict(id="G3a", criterion="IDN GDP median h=4 < 0 and 16-84% band excludes 0", target=-1.01,
                  estimate=f"{iy4:.3f} [{ilo:.2f},{ihi:.2f}]", passed=(iy4 < 0) and (ihi < 0)))
    ip4 = get("Indonesia", V, "Dp", 4, "median")
    g.append(dict(id="G3b", criterion="IDN inflation median h=4 > 0", target=0.91, estimate=round(ip4, 3), passed=ip4 > 0))
    o4, n4 = get("Philippines", V, "poil", 4, "median"), get("Philippines", V, "pnf", 4, "median")
    g.append(dict(id="G4", criterion="real oil and non-fuel medians h=4 > 0", target="13.87; 5.31",
                  estimate=f"{o4:.2f}; {n4:.2f}", passed=(o4 > 0) and (n4 > 0)))
    gate = pd.DataFrame(g)
    gate["passed"] = gate["passed"].map({True: "PASS", False: "FAIL"})
    gate.to_csv(T / "replication_gate.csv", index=False)
    print(gate.to_string())
    print("GATE:", "PASS" if (gate.passed == "PASS").all() else "FAIL")

    # side-by-side with every target cell (information, not part of the gate)
    tg = pd.read_csv(ROOT / "replication" / "cmr2017_targets.csv")
    vmap = {"real GDP (cumulated growth)": ["y"], "inflation": ["Dp", "Dp_cumsum"],
            "real oil price": ["poil"], "real non-fuel commodity prices": ["pnf"]}
    comp = []
    for _, t in tg.iterrows():
        c = "Philippines" if t["unit"] == "Global" else t["unit"]
        for v in vmap[t["outcome"]]:
            for prefix in ("VECMX*", "levels"):
                m = irf[(irf.country == c) & irf.model.str.startswith(prefix) & (irf.variable == v) & (irf.h == t["h"])]
                r = m.iloc[0]
                sig = "5-95%" if (r.p05 > 0 or r.p95 < 0) else "16-84%" if (r.p16 > 0 or r.p84 < 0) else "none"
                comp.append(dict(unit=t["unit"], outcome=t["outcome"], variable=v, model=r.model, h=t["h"],
                                 target=t["beta"], target_sig=t["sig"], median=round(r["median"], 3),
                                 p16=round(r.p16, 3), p84=round(r.p84, 3), sig=sig))
    pd.DataFrame(comp).to_csv(T / "replication_comparison.csv", index=False)


if __name__ == "__main__":
    main()
