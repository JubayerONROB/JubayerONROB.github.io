from common import *

def style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_linewidth(0.6)
    ax.tick_params(width=0.6, length=2.5, labelsize=FS)
    ax.set_facecolor("white")

def fig_cost():
    W, H = FULL, 2.3
    fig, ax = canvas(W, H)
    label(ax, 0.08, H - 0.12, r"Cost of one marker, in full passes of the 1B model (before any hint token is decoded)", ha="left", bold=True)
    x0, u = 2.1, 2.2   # inches per 1.0 pass
    def bar(y, segs, text_left, text_right=None):
        label(ax, x0 - 0.1, y + 0.12, text_left, ha="right", fs=6.1)
        x = x0
        for w, t, col, dashed in segs:
            ax.add_patch(Rectangle((x, y), w * u, 0.24, fc="white", ec=col, lw=0.7, ls="--" if dashed else "-", zorder=2))
            label(ax, x + w * u / 2, y + 0.12, t, fs=5.9)
            x += w * u
        if text_right:
            label(ax, x + 0.08, y + 0.12, text_right, ha="left", fs=6.0)
    ys = [1.7, 1.32, 0.94, 0.56, 0.18]
    bar(ys[0], [(1.0, "1 pass", BLK, False)], "cascade, silent marker")
    bar(ys[1], [(1.0, "1 pass", BLK, False), (1.0, r"$c_{gen}$", BLK, True)], r"cascade, triggered ($1 + c_{gen}$)")
    bar(ys[2], [(6 / 16, "", RED, False)], "unified $k=6$, silent", r"$k/L = 6/16$: ideal saving $16/k = 2.67\times$")
    bar(ys[3], [(10 / 16, "", RED, False)], "unified $k=10$, silent", r"$k/L = 10/16$: ideal saving $16/k = 1.60\times$")
    bar(ys[4], [(6 / 16, "layers 1…$k$", RED, False), (10 / 16, "layers $k{+}1$…$L$", BLK, False)], "unified $k=6$, triggered", "exactly 1 pass")
    save(fig, "fig7-cost")

def fig_e2e():
    W, H = FULL, 2.35
    fig = plt.figure(figsize=(W, H))
    a1 = fig.add_axes([0.2, 0.2, 0.33, 0.62]); style(a1)
    rows = [("1B gate + 1B gen", 0.2971, 0.2619), ("1B gate + 8B gen", 0.2947, 0.2548), ("1B gate + Qwen2.5-7B", 0.3579, 0.3084)]
    for i, (n, c, e) in enumerate(rows):
        y = len(rows) - i
        a1.plot([e, c], [y, y], color=BLK, lw=0.6, zorder=1)
        a1.scatter([c], [y], s=14, facecolor="white", edgecolor=BLK, linewidth=0.7, zorder=3)
        a1.scatter([e], [y], s=14, color=RED, zorder=3)
        a1.text(c + 0.004, y + 0.17, f"{c:.4f}", fontsize=5.8, ha="center")
        a1.text(e, y - 0.3, f"{e:.4f}", fontsize=5.8, ha="center", color=RED)
    a1.set_yticks([3, 2, 1]); a1.set_yticklabels([r[0] for r in rows])
    a1.set_xlim(0.22, 0.40); a1.set_ylim(0.4, 3.6)
    a1.set_xlabel("end-to-end exact match", fontsize=FS)
    fig.text(0.02, 0.93, "(a) Ceiling (open) vs behind a real gate (red)", fontsize=FS + 0.5, fontweight="bold")
    a2 = fig.add_axes([0.66, 0.2, 0.31, 0.62]); style(a2)
    a2.plot([0.2122, 0.2619], [0.3011, 0.2387], color=BLK, lw=0.6, zorder=1)
    a2.scatter([0.2619], [0.2387], color=RED, s=16, zorder=3)
    a2.scatter([0.2122], [0.3011], facecolor="white", edgecolor=BLK, s=16, linewidth=0.7, zorder=3)
    a2.text(0.2619, 0.2387 - 0.011, "deployed point\n(0.2619, 0.2387)", fontsize=5.8, ha="center", va="top", color=RED)
    a2.text(0.2122, 0.3011 + 0.006, "1% false-alarm budget\n(0.2122, 0.3011)", fontsize=5.8, ha="left", va="bottom")
    a2.set_xlim(0.19, 0.29); a2.set_ylim(0.20, 0.34)
    a2.set_xlabel("end-to-end exact match (finds more triggers →)", fontsize=FS)
    a2.set_ylabel("end-to-end precision", fontsize=FS)
    fig.text(0.60, 0.93, "(b) A stricter gate trades recall for precision", fontsize=FS + 0.5, fontweight="bold")
    save(fig, "fig8-end-to-end")

def fig_memory():
    W, H = FULL, 2.2
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0.28, 0.2, 0.68, 0.68]); style(ax)
    rows = [("full profile (control)", 0.2947, True), ("retrieval, 20 units", 0.2935, False), ("retrieval, 10 units", 0.2864, False),
            ("retrieval, 5 units", 0.2810, False), ("trained without a profile", 0.0584, False),
            ("no profile at inference", 0.0474, False), ("mismatched profile (other sample)", 0.0441, False)]
    for i, (n, v, hi) in enumerate(rows):
        y = len(rows) - i
        ax.barh(y, v, height=0.6, color=RED if hi else BLK, edgecolor="none")
        ax.text(v + 0.004, y, f"{v:.4f}", va="center", fontsize=5.9)
    ax.set_yticks(range(len(rows), 0, -1)); ax.set_yticklabels([r[0] for r in rows])
    ax.set_xlim(0, 0.34); ax.set_xlabel("exact match on the 3,356 true triggers", fontsize=FS)
    fig.text(0.02, 0.93, "The memory profile drives hint quality", fontsize=FS + 0.5, fontweight="bold")
    save(fig, "fig9-memory")

def fig_human():
    W, H = COL * 1.5, 2.3
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0.14, 0.2, 0.84, 0.62]); style(ax)
    names = ["native\njudge", "ROUGE-1", "BERTScore", "exact\nmatch"]
    r8 = [0.55, 0.51, 0.47, 0.31]; r1 = [0.67, 0.62, 0.61, 0.43]
    xs = range(4); w = 0.36
    for i in xs:
        ax.bar(i - w / 2, r8[i], w, color=BLK)
        ax.bar(i + w / 2, r1[i], w, facecolor="white", edgecolor=BLK, linewidth=0.7)
        ax.text(i - w / 2, r8[i] + 0.012, f"{r8[i]:.2f}", ha="center", fontsize=5.6)
        ax.text(i + w / 2, r1[i] + 0.012, f"{r1[i]:.2f}", ha="center", fontsize=5.6)
    ax.set_xticks(list(xs)); ax.set_xticklabels(names)
    ax.set_ylim(0, 0.85); ax.set_ylabel("Pearson $r$ with human uptake", fontsize=FS)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(fc=BLK, ec=BLK, label="8B hints, with memory"), Patch(fc="white", ec=BLK, label="1B hints")], frameon=False, fontsize=5.8, loc="upper right")
    fig.text(0.02, 0.93, "Which automatic score tracks people?", fontsize=FS + 0.5, fontweight="bold")
    save(fig, "fig10-human-correlation")

if __name__ == "__main__":
    fig_cost(); fig_e2e(); fig_memory(); fig_human()
