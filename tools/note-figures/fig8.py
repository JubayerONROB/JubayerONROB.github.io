from common import *

def fig_bootstrap_mcnemar():
    W, H = FULL, 5.05
    fig, ax = canvas(W, H)
    oy = 1.6
    # ---------------- (a) bootstrap ----------------
    label(ax, 0.08, H - 0.12, "(a) Bootstrap: a confidence interval without formulas", ha="left", bold=True)
    label(ax, 0.08, oy + 3.0, "original sample:\n866 test dialogues", ha="left", fs=6.0)
    for i, t in enumerate(["$D_1$", "$D_2$", "$D_3$", "$D_4$", "$D_5$", "…"]):
        box(ax, 0.08 + i * 0.4, oy + 2.55, 0.36, 0.3, t, fs=6.0)
    label(ax, 3.85, oy + 3.0, "resample with replacement,\nsame size, $B$ times", fs=6.0)
    rows = [(oy + 2.55, "$D_3\\ D_1\\ D_3\\ D_5\\ D_2$ …", "$s_1$"),
            (oy + 2.2, "$D_2\\ D_2\\ D_4\\ D_1\\ D_5$ …", "$s_2$"),
            (oy + 1.65, "$D_5\\ D_3\\ D_1\\ D_1\\ D_4$ …", "$s_B$")]
    label(ax, 5.55, oy + 3.0, "score on the\nresample", fs=6.0)
    for y, t, s in rows:
        box(ax, 3.1, y, 1.5, 0.28, t, fs=5.8)
        arrow(ax, (2.5, oy + 2.7), (3.1, y + 0.14))
        arrow(ax, (4.6, y + 0.14), (5.15, y + 0.14))
        box(ax, 5.15, y, 0.8, 0.28, s, fs=6.2)
    for cx in (3.85, 5.55):
        for dy in (-0.06, 0.0, 0.06):
            ax.plot([cx], [oy + 2.01 + dy], marker="o", ms=1.3, color=BLK)
    label(ax, 6.2, oy + 2.55 + 0.14, "", fs=5)
    # sorted scores line
    yl = oy + 0.9
    x0, x1 = 1.2, 6.0
    line(ax, (x0, yl), (x1, yl))
    for xx in [x0 + 0.07 + i * 0.28 for i in range(17)]:
        line(ax, (xx, yl - 0.04), (xx, yl + 0.04), lw=0.4)
    xl, xh = x0 + 0.12 * (x1 - x0), x1 - 0.12 * (x1 - x0)
    line(ax, (xl, yl - 0.15), (xl, yl + 0.15), color=RED, lw=1.0)
    line(ax, (xh, yl - 0.15), (xh, yl + 0.15), color=RED, lw=1.0)
    line(ax, (xl, yl - 0.5), (xh, yl - 0.5), color=RED, lw=0.9)
    label(ax, (xl + xh) / 2, yl - 0.65, "middle 95% of the scores = the 95% confidence interval", color=RED, fs=6.2)
    label(ax, xl, yl - 0.3, "2.5th percentile", fs=5.8, color=RED)
    label(ax, xh, yl - 0.3, "97.5th percentile", fs=5.8, color=RED)
    label(ax, x0 - 0.1, yl, "all $B$ scores,\nsorted:", ha="right", fs=6.0)
    arrow(ax, (5.55, oy + 1.62), (5.55, yl + 0.06))
    label(ax, 0.08, oy + 0.05, "Whole dialogues are resampled, not single markers, because the markers of one dialogue are not independent.", ha="left", fs=5.9)
    line(ax, (0.08, 1.4), (W - 0.08, 1.4), lw=0.4, ls=(0, (2, 2)))
    # ---------------- (b) McNemar ----------------
    label(ax, 0.08, 1.2, "(b) McNemar's test: compare two systems on the same items", ha="left", bold=True)
    tx, cw, ch = 1.05, 1.2, 0.34
    label(ax, tx + cw / 2, 0.98, "B right", fs=6.0)
    label(ax, tx + 1.5 * cw, 0.98, "B wrong", fs=6.0)
    label(ax, tx - 0.08, 0.17 + ch * 1.5, "A right", ha="right", fs=6.0)
    label(ax, tx - 0.08, 0.17 + ch * 0.5, "A wrong", ha="right", fs=6.0)
    box(ax, tx, 0.17 + ch, cw, ch, "both right\n(ignored)", fs=5.7)
    box(ax, tx + cw, 0.17 + ch, cw, ch, "$b$: only A right", color=RED, fs=5.9)
    box(ax, tx, 0.17, cw, ch, "$c$: only B right", color=RED, fs=5.9)
    box(ax, tx + cw, 0.17, cw, ch, "both wrong\n(ignored)", fs=5.7)
    label(ax, 4.0, 0.95, "If A and B are equally good,\n$b$ and $c$ should be about equal.", ha="left", fs=6.0)
    label(ax, 4.0, 0.55, r"$\chi^2 = \dfrac{(b - c)^2}{b + c}$", ha="left", fs=8, color=RED)
    label(ax, 4.0, 0.2, "A large $\\chi^2$ gives a small $p$-value:\none system is really better on these items.", ha="left", fs=6.0)
    save(fig, "fig21-bootstrap-mcnemar")

if __name__ == "__main__":
    fig_bootstrap_mcnemar()
