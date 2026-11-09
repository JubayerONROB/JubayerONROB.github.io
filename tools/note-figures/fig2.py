from common import *

# ---------- Figure 2: threshold, confusion matrix, gate metrics ----------
def fig_threshold():
    W, H = FULL, 2.35
    fig, ax = canvas(W, H)
    label(ax, 0.08, H - 0.12, "(a) The gate turns a score into a decision", ha="left", bold=True)
    x0, x1, y = 0.4, 3.2, 1.35
    line(ax, (x0, y), (x1, y))
    for v, s_ in [(0, "0"), (1, "1")]:
        xx = x0 + v * (x1 - x0)
        line(ax, (xx, y - 0.05), (xx, y + 0.05))
        label(ax, xx, y - 0.17, s_, fs=6)
    label(ax, (x0 + x1) / 2, y - 0.32, r"gate score $p_i \in [0,1]$", fs=6.5)
    tx = x0 + 0.6 * (x1 - x0)
    line(ax, (tx, y - 0.25), (tx, y + 0.45), color=RED, lw=0.9)
    label(ax, tx, y + 0.57, r"threshold $t$", color=RED, fs=6.5)
    label(ax, (x0 + tx) / 2, y + 0.25, "$p_i < t$\n$g_i = 0$: silent", fs=6.3)
    label(ax, (tx + x1) / 2, y + 0.25, "$p_i \\geq t$\n$g_i = 1$: fire", fs=6.3, color=RED)
    arrow(ax, (tx + 0.05, y + 0.02), (x1 - 0.05, y + 0.02), color=RED)
    label(ax, (x0 + x1) / 2, 0.58, "$t$ higher: fewer false alarms, more misses.\n$t$ lower: fewer misses, more false alarms.", fs=6.2)
    label(ax, (x0 + x1) / 2, 0.14, r"$t$ is chosen by trying $0.01, 0.02, \ldots, 0.99$ on validation data", fs=5.8)
    label(ax, 3.75, H - 0.12, "(b) Four outcomes at each marker", ha="left", bold=True)
    cx, cy, cw, ch = 4.7, 0.65, 1.0, 0.5
    label(ax, cx + cw, cy + 2 * ch + 0.3, "reference says", fs=6.2)
    label(ax, cx + cw / 2, cy + 2 * ch + 0.12, "trigger", fs=6.2)
    label(ax, cx + 1.5 * cw, cy + 2 * ch + 0.12, "no trigger", fs=6.2)
    label(ax, cx - 0.1, cy + ch * 1.5, "gate\nfires", ha="right", fs=6.2)
    label(ax, cx - 0.1, cy + ch * 0.5, "gate\nsilent", ha="right", fs=6.2)
    box(ax, cx + cw, cy + ch, cw, ch, "FP\nfalse alarm")
    box(ax, cx, cy, cw, ch, "FN\nmiss")
    box(ax, cx + cw, cy, cw, ch, "TN\nright quiet")
    box(ax, cx, cy + ch, cw, ch, "TP\nright call", color=RED)
    label(ax, 3.75, 0.45, "TP + FN = 3,356 triggers\nTN + FP = 24,702 silence markers", ha="left", fs=6.1)
    label(ax, 5.2, 0.14, r"precision $= \frac{TP}{TP+FP}$   recall $= \frac{TP}{TP+FN}$   FAR $= \frac{FP}{TN+FP}$", ha="center", fs=6.3)
    save(fig, "fig2-threshold")

# ---------- Figure 3: transformer, prefill vs decode ----------
def fig_transformer():
    W, H = FULL, 2.0
    fig, ax = canvas(W, H)
    label(ax, 0.08, H - 0.12, "(a) Prefill: the whole prompt goes through all L layers once", ha="left", bold=True)
    label(ax, 3.6, H - 0.12, "(b) Decoding: one new token per pass", ha="left", bold=True)

    def stack(x0, y0, n, bw=0.22, bh=0.34, gap=0.07, d=0.06):
        for i in range(n):
            block3d(ax, x0 + i * (bw + gap), y0, bw, bh, d, BLK)
    ya = 1.0
    box(ax, 0.1, ya - 0.1, 0.8, 0.56, "prompt tokens\n$x_1 \\ldots x_n$", fs=6.2)
    arrow(ax, (0.9, ya + 0.18), (1.1, ya + 0.18))
    stack(1.12, ya, 8)
    label(ax, 2.2, ya + 0.6, r"layers $1, 2, \ldots, L$  (8 drawn; $L = 16$ in Llama-3.2-1B)", fs=6.1)
    label(ax, 2.2, ya - 0.22, r"hidden state $h_j$ for every token $j$", fs=6.1)
    label(ax, 2.2, 0.3, "all prompt tokens are processed together,\nso this costs one pass", fs=6.0)
    yb = 1.0
    box(ax, 3.62, yb - 0.1, 0.62, 0.56, "last\ntoken", fs=6.2)
    arrow(ax, (4.24, yb + 0.18), (4.38, yb + 0.18))
    stack(4.4, yb, 6, bw=0.2, gap=0.06)
    arrow(ax, (5.98, yb + 0.18), (6.15, yb + 0.18))
    box(ax, 6.15, yb - 0.1, 0.62, 0.56, "next\ntoken", fs=6.2)
    ax.plot([6.46, 6.46, 3.93], [yb - 0.1, yb - 0.3, yb - 0.3], color=BLK, lw=0.6, zorder=2)
    arrow(ax, (3.93, yb - 0.3), (3.93, yb - 0.1))
    ax.plot([3.93, 3.93], [yb - 0.3, yb - 0.1], color=BLK, lw=0.6, zorder=2)
    label(ax, 5.15, yb - 0.42, "repeat until the hint is done (1 to 3 tokens here)", fs=6.0)
    label(ax, 5.15, 0.3, "earlier tokens' keys and values are reused,\nso only the new token is computed", fs=6.0)
    save(fig, "fig3-transformer")

if __name__ == "__main__":
    fig_threshold(); fig_transformer()
