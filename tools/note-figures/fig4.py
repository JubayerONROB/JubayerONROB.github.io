from common import *

def fig_prompt():
    W, H = FULL, 2.0
    fig, ax = canvas(W, H)
    label(ax, 0.08, H - 0.12, "What the model reads at one silence marker", ha="left", bold=True)
    def row(y, parts, title):
        label(ax, 0.08, y + 0.52, title, ha="left", fs=6.2)
        x = 0.08
        for w, t, col in parts:
            box(ax, x, y, w, 0.36, t, color=col, fs=6.2)
            x += w
    row(1.0, [(1.0, "system prompt", BLK), (1.5, "memory profile $M_w$", RED), (2.6, "dialogue $D_{\\leq i}$ (up to 1,300 characters)", BLK)],
        "Unified decoder, and the generator in the cascade: profile + dialogue")
    row(0.28, [(1.0, "system prompt", BLK), (2.6, "dialogue $D_{\\leq i}$ (up to 1,300 characters)", BLK)],
        "Gate of the cascade: dialogue only, no profile")
    label(ax, 6.77, 1.18, "the profile adds\n306 tokens to every prompt", ha="right", fs=6.0, color=RED)
    label(ax, 6.77, 0.46, "test split: 676 tokens with the profile,\n370 without", ha="right", fs=6.0)
    save(fig, "fig4-prompt")

def fig_lora():
    W, H = FULL, 2.1
    fig, ax = canvas(W, H)
    label(ax, 0.08, H - 0.12, "LoRA: freeze the big weight matrix, train a small low-rank update", ha="left", bold=True)
    # input x
    box(ax, 0.1, 0.85, 0.45, 0.5, "$x$")
    # W frozen
    box(ax, 1.4, 0.9, 1.1, 1.0 - 0.0 - 0.0 if False else 0.9, "")
    label(ax, 1.95, 1.35, "$W$\n$d \\times d$\nfrozen,\n4-bit (NF4)", fs=6.2)
    # A and B
    box(ax, 1.4, 0.0 + 0.1, 0.5, 0.5, "", color=RED)
    label(ax, 1.65, 0.35, "$A$\n$r \\times d$", fs=6.2, color=RED)
    box(ax, 2.0, 0.1, 0.5, 0.5, "", color=RED)
    label(ax, 2.25, 0.35, "$B$\n$d \\times r$", fs=6.2, color=RED)
    arrow(ax, (0.55, 1.1), (1.4, 1.35))
    arrow(ax, (0.55, 1.1), (1.4, 0.35), color=RED)
    arrow(ax, (1.9, 0.35), (2.0, 0.35), color=RED)
    # plus
    ax.add_patch(plt.Circle((3.15, 1.1), 0.15, fc="white", ec=BLK, lw=0.6, zorder=3))
    label(ax, 3.15, 1.1, "+", fs=8)
    arrow(ax, (2.5, 1.35), (3.02, 1.17))
    arrow(ax, (2.5, 0.35), (3.02, 1.03), color=RED)
    arrow(ax, (3.3, 1.1), (3.7, 1.1))
    box(ax, 3.7, 0.85, 0.5, 0.5, "$y$")
    label(ax, 5.35, 1.45, "$y = Wx + \\frac{\\alpha}{r}\\,B A x$", fs=7.5)
    label(ax, 5.35, 0.95, "our setting: rank $r = 16$, scale $\\alpha = 32$,\nadapters on every attention and MLP projection", fs=6.2)
    label(ax, 5.35, 0.45, "only $A$ and $B$ are trained;\none adapter is about 42 MB", fs=6.2, color=RED)
    save(fig, "fig5-lora")

if __name__ == "__main__":
    fig_prompt(); fig_lora()
