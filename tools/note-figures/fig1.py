from common import *

def fig_decision_points():
    W, H = FULL, 2.7
    fig, ax = canvas(W, H)
    label(ax, 0.08, H - 0.12, "At every silence the assistant makes one decision", ha="left", bold=True)
    ys, uh = 1.75, 0.5
    us = [(0.08, 1.55, "“I’m trying to remember\nthat performance I went to…”"),
          (2.05, 0.95, "“Which one?”"),
          (3.4, 1.45, "“The one in the spring,\nI think it was…”")]
    marks = [x + w + 0.18 for x, w, _ in us]
    for x, w, t in us:
        box(ax, x, ys, w, uh, t)
    for i, mx in enumerate(marks):
        ax.plot([mx, mx], [ys - 0.02, ys + uh + 0.02], color=BLK, lw=0.6, ls=(0, (1.5, 1.5)), zorder=2)
        label(ax, mx, ys + uh + 0.13, f"silence {i+1}", fs=6)
    gy, gh = 1.1, 0.34
    for i, mx in enumerate(marks):
        fire = i == 2
        col = RED if fire else BLK
        box(ax, mx - 0.45, gy, 0.9, gh, r"$p_i \geq t$ ?", color=col)
        arrow(ax, (mx, ys - 0.03), (mx, gy + gh), color=col)
        txt = r"yes: $g_i=1$" if fire else r"no: $g_i=0$, stay quiet"
        label(ax, mx, 0.93, txt, fs=6, color=col)
    box(ax, marks[2] + 0.75, gy - 0.02, 0.95, gh + 0.04, "dance\nperformance", color=RED, fs=6)
    arrow(ax, (marks[2] + 0.45, gy + gh / 2), (marks[2] + 0.75, gy + gh / 2), color=RED)
    label(ax, marks[2] + 1.24, 0.93, "hint $h_i$ (1–3 words)", fs=5.8)
    # corpus bar
    by, bh = 0.35, 0.14
    total, sil = 28058, 24702
    x0, x1 = 0.08, W - 0.08
    ww = x1 - x0
    label(ax, x0, 0.64, "Our test set: N = 28,058 markers over 866 dialogues", ha="left", fs=6)
    label(ax, x1, 0.64, "illustrative example, adapted from Figure 1 of the paper", ha="right", fs=5.6)
    ax.add_patch(Rectangle((x0, by), ww * sil / total, bh, fc="white", ec=BLK, lw=0.6, zorder=2))
    ax.add_patch(Rectangle((x0 + ww * sil / total, by), ww * (total - sil) / total, bh, fc=RED, ec=RED, lw=0.6, zorder=2))
    label(ax, x0 + ww * sil / total / 2, by - 0.12, "24,702 silence markers (no hint needed)", fs=6)
    label(ax, x1, by - 0.12, "3,356 triggers (11.96%)", ha="right", fs=6, color=RED)
    save(fig, "fig1-decision-points")

if __name__ == "__main__":
    fig_decision_points()
