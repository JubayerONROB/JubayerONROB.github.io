from common import *

def blocks(ax, x0, y0, n, red_idx=(), bw=0.12, gap=0.04, bh=0.3, d=0.05):
    for i in range(n):
        block3d(ax, x0 + i * (bw + gap), y0, bw, bh, d, RED if i in red_idx else BLK)
    return x0 + n * (bw + gap) - gap + d

def fig_architectures():
    W, H = FULL, 3.7
    fig, ax = canvas(W, H)
    label(ax, 0.08, H - 0.12, "(a) Two-model cascade (LlamaPIE-style, our reimplementation)", ha="left", bold=True)
    ya = 2.75
    box(ax, 0.08, ya - 0.05, 0.9, 0.5, "prompt\n(no profile)", fs=6.2)
    arrow(ax, (0.98, ya + 0.2), (1.1, ya + 0.2))
    xe = blocks(ax, 1.12, ya + 0.05, 16)
    label(ax, 1.12 + 0.5 * (xe - 1.12), ya + 0.5, "gate: Llama-3.2-1B, layers 1 … 16", fs=6.1)
    arrow(ax, (xe + 0.04, ya + 0.2), (xe + 0.2, ya + 0.2))
    px = xe + 0.2
    box(ax, px, ya - 0.02, 0.72, 0.44, "$p_i \\geq t$ ?", fs=6.3)
    arrow(ax, (px + 0.36, ya - 0.02), (px + 0.36, ya - 0.3))
    label(ax, px + 0.36, ya - 0.42, "no: silent, no output", fs=6.0)
    gx = px + 0.72
    arrow(ax, (gx, ya + 0.2), (gx + 0.2, ya + 0.2))
    label(ax, gx + 0.1, ya + 0.33, "yes", fs=5.8)
    box(ax, gx + 0.2, ya - 0.15, 1.15, 0.7, "generator\nLlama-3.1-8B\nprompt + $M_w$", fs=6.0)
    arrow(ax, (gx + 1.35, ya + 0.2), (gx + 1.5, ya + 0.2))
    box(ax, gx + 1.5, ya + 0.0, 0.55, 0.4, "hint\n$h_i$", fs=6.0)
    label(ax, 0.08, 2.1, "silent marker: one full 1B pass.   triggered marker: one 1B pass plus one full 8B pass.   two base models resident.", ha="left", fs=6.0)
    line(ax, (0.08, 1.98), (W - 0.08, 1.98), lw=0.4, ls=(0, (2, 2)))
    label(ax, 0.08, 1.86, "(b) Unified early-exit decoder (this work)", ha="left", bold=True)
    yb = 1.0
    box(ax, 0.08, yb - 0.05, 0.9, 0.5, "one prompt\nwith $M_w$", fs=6.2)
    arrow(ax, (0.98, yb + 0.2), (1.1, yb + 0.2))
    k = 6
    xe = blocks(ax, 1.12, yb + 0.05, 16, red_idx=(k - 1,))
    label(ax, 1.12 + 0.5 * (xe - 1.12), yb + 0.5, "one Llama-3.2-1B, layers 1 … 16 ($L = 16$)", fs=6.1)
    mid = 1.12 + (k - 1) * 0.16 + 0.06
    arrow(ax, (mid, yb + 0.02), (mid, yb - 0.25), color=RED)
    box(ax, mid - 0.45, yb - 0.5, 0.9, 0.25, "head $W_c$ on $h_k$", color=RED, fs=5.9)
    label(ax, mid + 0.55, yb - 0.375, "exit at layer $k \\in \\{6, 10\\}$", fs=6.0, color=RED, ha="left")
    arrow(ax, (xe + 0.04, yb + 0.2), (xe + 0.2, yb + 0.2), color=RED)
    box(ax, xe + 0.2, yb - 0.02, 0.6, 0.44, "hint\n$h_i$", color=RED, fs=6.0)
    label(ax, xe + 0.5, yb - 0.32, "if $p_i \\geq t$: the same pass\ncontinues through layers $k{+}1 \\ldots L$", fs=5.8, color=RED)
    label(ax, 0.08, 0.15, "silent marker: only layers 1 … $k$.   triggered marker: exactly one pass.   one base + one shared adapter, up to 1.05 GB resident.", ha="left", fs=6.0)
    save(fig, "fig6-architectures")

if __name__ == "__main__":
    fig_architectures()
