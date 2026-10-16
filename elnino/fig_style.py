"""Black-and-white journal figure style.

No colour: series differ by line style and marker; bands are light grey fill
(series 1) or dotted bounds (series 2); serif font; no title inside the image
(captions belong in the document). save() writes 300-dpi PNG and TIFF and a
vector PDF without CreationDate, so reruns are byte-identical.

    from fig_style import setup, save, irf, A, B
    setup()
    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    irf(ax, df_all, A, "All income"); irf(ax, df_b30, B, "Bottom 30%", band="lines")
    ax.set_ylabel("Percentage points"); ax.legend(); save(fig, "fig1_rq1", outdir)
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

BLACK, DARK, MID, LIGHT = "0.0", "0.25", "0.55", "0.85"
A = dict(color=BLACK, linestyle="-", marker="o", markersize=3.5, markerfacecolor=BLACK)     # series 1
B = dict(color=BLACK, linestyle="--", marker="s", markersize=3.5, markerfacecolor="white")  # series 2
C = dict(color=DARK, linestyle=":", marker="^", markersize=3.5, markerfacecolor="white")    # series 3


def setup():
    plt.rcParams.update({
        "font.family": "DejaVu Serif", "font.size": 9, "axes.edgecolor": BLACK, "axes.labelcolor": BLACK,
        "xtick.color": BLACK, "ytick.color": BLACK, "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": False, "legend.frameon": False, "figure.dpi": 100, "hatch.linewidth": 0.6,
        "lines.linewidth": 1.4,
    })


def save(fig, name, outdir):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    fig.savefig(outdir / f"{name}.png", dpi=300, bbox_inches="tight")
    fig.savefig(outdir / f"{name}.tiff", dpi=300, bbox_inches="tight", pil_kwargs={"compression": "tiff_lzw"})
    fig.savefig(outdir / f"{name}.pdf", bbox_inches="tight", metadata={"CreationDate": None})
    plt.close(fig)


def zero(ax, horizontal=True):
    (ax.axhline if horizontal else ax.axvline)(0, color=BLACK, linewidth=0.6)


def irf(ax, q, style, label=None, band="fill", H=12):
    """Plot an impulse response from a frame with columns h, beta, lo, hi."""
    if band == "fill":
        ax.fill_between(q.h, q.lo, q.hi, color=LIGHT, linewidth=0)
    elif band == "lines":
        for col in ("lo", "hi"):
            ax.plot(q.h, q[col], color=BLACK, linestyle=":", linewidth=0.8)
    ax.plot(q.h, q.beta, label=label, **style)
    zero(ax)
    ax.set_xticks(range(0, H + 1, 2))
    ax.set_xlabel("Months after the shock")
