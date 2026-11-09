"""Shared helpers for the Proactive Assistant note figures.
Style: white background, black text/lines, one red accent (#C0392B) for the active path.
Units: 1 data unit = 1 inch, so layouts are easy to reason about."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon

RED = "#C0392B"
BLK = "#000000"
OUT = os.environ.get("FIG_OUT", "out")
FS = 6.5
FULL, COL = 6.85, 3.3

plt.rcParams.update({
    "font.family": ["Liberation Sans"],
    "font.size": FS,
    "pdf.fonttype": 42, "ps.fonttype": 42,
    "mathtext.fontset": "custom",
    "mathtext.rm": "Liberation Sans",
    "mathtext.it": "Liberation Sans:italic",
    "mathtext.bf": "Liberation Sans:bold",
    "text.color": BLK, "axes.edgecolor": BLK, "axes.labelcolor": BLK,
    "xtick.color": BLK, "ytick.color": BLK,
    "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
})


def canvas(w, h):
    fig = plt.figure(figsize=(w, h))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w); ax.set_ylim(0, h); ax.axis("off")
    return fig, ax


def save(fig, name):
    os.makedirs(OUT, exist_ok=True)
    fig.savefig(f"{OUT}/{name}.pdf")
    fig.savefig(f"{OUT}/{name}.png", dpi=300)
    plt.close(fig)


def box(ax, x, y, w, h, text="", color=BLK, lw=0.6, fs=FS, ls="-", bold=False, ha="center", pad=0.0):
    ax.add_patch(Rectangle((x, y), w, h, fill=True, fc="white", ec=color, lw=lw, ls=ls, zorder=2))
    if text:
        tx = x + w / 2 if ha == "center" else x + 0.05 + pad
        ax.text(tx, y + h / 2, text, ha=ha, va="center", fontsize=fs, color=BLK,
                fontweight="bold" if bold else "normal", zorder=3, linespacing=1.25)


def label(ax, x, y, s, ha="center", va="center", fs=FS, color=BLK, bold=False, style="normal"):
    ax.text(x, y, s, ha=ha, va=va, fontsize=fs, color=color, zorder=4,
            fontweight="bold" if bold else "normal", fontstyle=style, linespacing=1.25)


def arrow(ax, p0, p1, color=BLK, lw=0.6, ls="-"):
    ax.annotate("", xy=p1, xytext=p0, zorder=3,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, ls=ls,
                                shrinkA=0, shrinkB=0, mutation_scale=6))


def line(ax, p0, p1, color=BLK, lw=0.6, ls="-"):
    ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=color, lw=lw, ls=ls, zorder=2, solid_capstyle="butt")


def block3d(ax, x, y, w, h, d, color=BLK):
    """Small 3D block: front face, top face, right face; white edges separate faces."""
    front = Rectangle((x, y), w, h, fc=color, ec="white", lw=0.4, zorder=3)
    top = Polygon([(x, y + h), (x + d, y + h + d), (x + w + d, y + h + d), (x + w, y + h)],
                  closed=True, fc=color, ec="white", lw=0.4, zorder=3)
    right = Polygon([(x + w, y), (x + w + d, y + d), (x + w + d, y + h + d), (x + w, y + h)],
                    closed=True, fc=color, ec="white", lw=0.4, zorder=3)
    for p in (front, top, right):
        ax.add_patch(p)
