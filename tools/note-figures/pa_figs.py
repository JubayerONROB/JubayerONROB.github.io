"""Figures for the deep-dive pages of the Proactive Assistant guide."""
from common import *
from fig6 import style
import numpy as np

def ttl(fig, s, y=0.95, x=0.02):
    fig.text(x, y, s, fontsize=FS + 0.5, fontweight="bold")

# ---- pa1: toy 10 markers (toy numbers) ----
def pa1_toy_markers():
    W, H = FULL, 3.4
    fig, ax = canvas(W, H)
    label(ax, 0.08, H - 0.12, "Toy example: 10 markers at threshold $t = 0.5$ (made-up numbers)", ha="left", bold=True)
    p = [0.62, 0.91, 0.10, 0.05, 0.45, 0.20, 0.72, 0.30, 0.85, 0.15]
    T = {2, 5, 7, 9}
    m = {2: 1, 5: 1, 7: 0, 9: 1}
    t = 0.5
    x0, cw, ch = 1.45, 0.53, 0.3
    rows = ["marker $i$", "score $p_i$", "reference trigger?", "gate $g_i = \\mathbf{1}[p_i \\geq t]$", "hint exact? $m_i$", "outcome"]
    ys = [H - 0.55 - j * 0.38 for j in range(len(rows))]
    for r, y in zip(rows, ys):
        label(ax, x0 - 0.08, y + ch / 2, r, ha="right", fs=5.8)
    for i in range(1, 11):
        x = x0 + (i - 1) * cw
        g = int(p[i - 1] >= t)
        trig = i in T
        box(ax, x, ys[0], cw - 0.04, ch, str(i), fs=5.8)
        box(ax, x, ys[1], cw - 0.04, ch, f"{p[i-1]:.2f}", fs=5.8)
        box(ax, x, ys[2], cw - 0.04, ch, "yes" if trig else "–", fs=5.8)
        box(ax, x, ys[3], cw - 0.04, ch, "fire" if g else "quiet", fs=5.8, color=RED if g else BLK, lw=1.0 if g else 0.6)
        box(ax, x, ys[4], cw - 0.04, ch, (str(m[i]) if trig else "–"), fs=5.8)
        if g and not trig: out, col = "false\nalarm", RED
        elif g and trig and m[i] == 1: out, col = "correct\nhint", BLK
        elif g and trig: out, col = "wrong\nhint", BLK
        elif trig: out, col = "miss", RED
        else: out, col = "ok", BLK
        box(ax, x, ys[5] - 0.07, cw - 0.04, ch + 0.07, out, fs=5.3, color=col)
    label(ax, 0.08, 0.5, "$|\\mathcal{T}| = 4$ triggers. Emitted hints: 4 (markers 1, 2, 7, 9).   $\\sum_{i\\in\\mathcal{T}} g_i m_i = 2$ (markers 2 and 9).", ha="left", fs=6.0)
    label(ax, 0.08, 0.25, "$EM_{e2e} = 2/4 = 0.50$,   $P_{e2e} = 2/4 = 0.50$,   $R = 3/4 = 0.75$,   $EM_{fwd} = 2/3 \\approx 0.667$,   $R \\cdot EM_{fwd} = 0.50$.", ha="left", fs=6.0, color=RED)
    save(fig, "pa1-toy-markers")

# ---- pa2: toy sweep ----
def pa2_toy_sweep():
    p = {1: .62, 2: .91, 3: .10, 4: .05, 5: .45, 6: .20, 7: .72, 8: .30, 9: .85, 10: .15}
    T = {2, 5, 7, 9}; m = {2: 1, 5: 1, 7: 0, 9: 1}
    ts = np.linspace(0.0, 1.0, 1001)
    EM, P, R = [], [], []
    for t in ts:
        g = {i: int(p[i] >= t) for i in p}
        num = sum(g[i] * m[i] for i in T); emit = sum(g.values())
        EM.append(num / 4); R.append(sum(g[i] for i in T) / 4); P.append(num / emit if emit else np.nan)
    W, H = FULL, 2.6
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0.09, 0.2, 0.62, 0.62]); style(ax)
    ax.plot(ts, EM, color=RED, lw=1.4, label=r"$EM_{e2e}$ (never rises)")
    ax.plot(ts, P, color=BLK, lw=1.0, ls="--", label=r"$P_{e2e}$ (can rise)")
    ax.plot(ts, R, color=BLK, lw=0.8, ls=":", label=r"$R$ (gate recall)")
    ax.axhline(0.75, color=RED, lw=0.6, ls=(0, (1, 2)))
    ax.text(0.02, 0.775, "oracle ceiling 0.75", fontsize=5.8, color=RED)
    ax.set_xlabel("threshold $t$", fontsize=FS); ax.set_ylabel("score", fontsize=FS)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1.08)
    ax.legend(frameon=False, fontsize=5.8, loc="lower left")
    fig.text(0.76, 0.84, "Reading the toy sweep", fontsize=6.2, fontweight="bold", va="top")
    fig.text(0.76, 0.46, "$t = 0.4$:  EM 0.75, P 0.60\n$t = 0.5$:  EM 0.50, P 0.50\n$t = 0.8$:  EM 0.50, P 1.00\n$t = 0.9$:  EM 0.25, P 1.00\n$t = 0.95$: nothing emitted", fontsize=5.8, linespacing=1.5, va="top")
    fig.text(0.76, 0.76, "Raising $t$ only switches\ngates off, so EM falls\nor stays. Precision\ncan climb because\nfalse alarms go first.", fontsize=5.8, linespacing=1.4, va="top")
    ttl(fig, "Toy threshold sweep (same 10 made-up markers)")
    save(fig, "pa2-toy-sweep")

# ---- pa3: expected cost vs fire rate ----
def pa3_cost_rate():
    W, H = FULL, 2.6
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0.09, 0.2, 0.6, 0.62]); style(ax)
    pi = np.linspace(0, 0.3, 200); L = 16
    ax.plot(pi, 1 + pi * 1.0, color=BLK, lw=1.2, label=r"cascade, $c_{gen}=1$ (assumption)")
    ax.plot(pi, 10 / L + pi * (1 - 10 / L), color=BLK, lw=1.0, ls="--", label=r"unified, $k=10$")
    ax.plot(pi, 6 / L + pi * (1 - 6 / L), color=RED, lw=1.4, label=r"unified, $k=6$")
    for x, ls in ((3356 / 28058, ":"), (3682 / 28058, "-")):
        ax.axvline(x, color=BLK, lw=0.5, ls=ls)
    ax.text(0.1196, 1.19, "oracle\n0.1196", fontsize=5.4, ha="right")
    ax.text(0.1312, 1.19, "deployed\n0.1312", fontsize=5.4, ha="left")
    ax.set_xlabel(r"fraction of markers where the gate fires, $\pi$", fontsize=FS)
    ax.set_ylabel("expected cost per marker\n(full 1B passes)", fontsize=FS)
    ax.set_ylim(0, 1.45); ax.set_xlim(0, 0.3)
    ax.legend(frameon=False, fontsize=5.7, loc="center right", bbox_to_anchor=(1.0, 0.64))
    fig.text(0.73, 0.84, r"At $\pi = 0.1312$:", fontsize=6.2, fontweight="bold", va="top")
    fig.text(0.73, 0.76, "unified $k=6$:   0.457\nunified $k=10$: 0.674\ncascade ($c_{gen}=1$): 1.131\n\nideal gain: 2.48× ($k=6$),\n1.68× ($k=10$)", fontsize=5.8, linespacing=1.5, va="top")
    ttl(fig, r"Expected cost: $E[c] = k/L + \pi\,(1 - k/L)$ against $E[c] = 1 + \pi\, c_{gen}$")
    save(fig, "pa3-cost-vs-rate")

# ---- pa4: Amdahl ----
def pa4_amdahl():
    W, H = FULL, 2.5
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0.09, 0.2, 0.6, 0.62]); style(ax)
    pi = 3682 / 28058
    r = np.logspace(-2, 0.4, 300)
    ax.plot(r, 1 / (r + pi), color=BLK, lw=1.2)
    ax.axhline(1 / pi, color=BLK, lw=0.6, ls="--"); ax.text(0.011, 1 / pi + 0.15, r"ceiling $1/\pi = 7.62$ (gate for free)", fontsize=5.8)
    for rr, s, lab in ((0.0966, 4.39, "8B generator\n4.39× measured"), (0.5934, 1.38, "1B generator\n1.38× measured")):
        ax.scatter([rr], [s], color=RED, s=22, zorder=4)
        ax.annotate(lab, xy=(rr, s), xytext=(rr * 1.5, s + 1.4), fontsize=5.8, color=RED, arrowprops=dict(arrowstyle="-|>", lw=0.5, color=RED, mutation_scale=5))
    ax.set_xscale("log"); ax.set_ylim(0, 8.6)
    ax.set_xlabel(r"gate cost / generator cost per marker, $r = T_{gate}/T_{gen}$", fontsize=FS)
    ax.set_ylabel("saving from gating", fontsize=FS)
    fig.text(0.73, 0.84, "Saving $S = 1/(r + \\pi)$", fontsize=6.4, fontweight="bold", va="top")
    fig.text(0.73, 0.74, "Solving for $r$ from the paper:\n8B: $r = 1/4.39 - 0.1312 = 0.097$\n1B: $r = 1/1.38 - 0.1312 = 0.593$\n\nGate share $r/(r+\\pi)$:\n8B: 42%    1B: 81.9%\nPaper reports 82% for 1B.", fontsize=5.8, linespacing=1.45, va="top")
    ttl(fig, "Why the saving from a gate depends on the generator's size")
    save(fig, "pa4-amdahl-gate")

# ---- pa5: precision vs prevalence ----
def pa5_precision():
    W, H = FULL, 2.5
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0.09, 0.2, 0.55, 0.62]); style(ax)
    far = np.linspace(0.0005, 0.1, 300)
    tpr = 0.8391
    for prev, ls, col, lab in ((3356 / 28058, "-", RED, "prevalence 11.96% (our corpus)"), (0.5, "--", BLK, "prevalence 50% (balanced)")):
        ax.plot(far * 100, tpr * prev / (tpr * prev + far * (1 - prev)), color=col, lw=1.3, ls=ls, label=lab)
    ax.scatter([3.51], [0.7646], color=RED, s=26, zorder=4)
    ax.annotate("deployed gate:\nrecall 0.8391, FAR 3.51%\nprecision 0.7646", xy=(3.51, 0.7646), xytext=(4.6, 0.42), fontsize=5.8, color=RED,
                arrowprops=dict(arrowstyle="-|>", lw=0.5, color=RED, mutation_scale=5))
    ax.set_xlabel("false-alarm rate FAR (%)", fontsize=FS); ax.set_ylabel("precision", fontsize=FS)
    ax.set_ylim(0.2, 1.02); ax.set_xlim(0, 10)
    ax.legend(frameon=False, fontsize=5.8, loc="lower left")
    fig.text(0.68, 0.84, "Bayes' rule for precision", fontsize=6.4, fontweight="bold", va="top")
    fig.text(0.68, 0.74, "precision = TPR·π / (TPR·π + FAR·(1−π))\n\nwith TPR = 0.8391, FAR = 0.0351,\nπ = prevalence = 0.1196:\n= 0.1003 / 0.1312 = 0.7646", fontsize=5.8, linespacing=1.5, va="top")
    ttl(fig, "Same recall and false-alarm rate, lower precision when positives are rare")
    save(fig, "pa5-precision-prevalence")

# ---- pa6: loss shapes ----
def pa6_loss():
    W, H = FULL, 2.6
    fig = plt.figure(figsize=(W, H))
    a1 = fig.add_axes([0.07, 0.2, 0.4, 0.6]); style(a1)
    a2 = fig.add_axes([0.57, 0.2, 0.4, 0.6]); style(a2)
    pt = np.linspace(0.01, 0.999, 400)
    a1.plot(pt, (1 - pt) ** 1.5, color=RED, lw=1.3, label=r"$\gamma = 1.5$")
    a1.plot(pt, (1 - pt) ** 2, color=BLK, lw=1.0, ls="--", label=r"$\gamma = 2$")
    a1.plot(pt, (1 - pt) ** 0, color=BLK, lw=0.7, ls=":", label=r"$\gamma = 0$ (plain CE)")
    for x, c in ((0.9, 0), (0.5, 0), (0.1, 0)):
        a1.scatter([x], [(1 - x) ** 1.5], color=RED, s=10, zorder=4)
        a1.text(x + 0.02, (1 - x) ** 1.5 + 0.05, f"{(1-x)**1.5:.3f}", fontsize=5.5, color=RED)
    a1.set_xlabel(r"probability of the true class, $p_t$", fontsize=FS); a1.set_ylabel(r"focal factor $(1-p_t)^{\gamma}$", fontsize=FS)
    a1.legend(frameon=False, fontsize=5.6, loc="upper right"); a1.set_xlim(0, 1.02); a1.set_ylim(0, 1.1)
    p = np.linspace(0, 1, 300)
    for w, ls, col in ((1, ":", BLK), (2.5, "-", RED), (4, "--", BLK)):
        a2.plot(p, w * p / (w * p + 1 - p), color=col, lw=1.2 if w == 2.5 else 0.9, ls=ls, label=f"$w = {w}$")
    a2.plot(p, p, color=BLK, lw=0.4)
    a2.set_xlabel(r"true $P(\mathrm{trigger}\mid x)$", fontsize=FS); a2.set_ylabel(r"probability the loss is minimized at", fontsize=FS)
    a2.legend(frameon=False, fontsize=5.6, loc="lower right", title="trigger weight", title_fontsize=5.6)
    a2.text(0.03, 0.9, "weighted CE inflates\nthe score; $t$ must move", fontsize=5.7)
    fig.text(0.02, 0.9, "(a) How much focal loss down-weights an example", fontsize=FS + 0.3, fontweight="bold")
    fig.text(0.52, 0.9, "(b) Class weight $w$ shifts the optimum", fontsize=FS + 0.3, fontweight="bold")
    save(fig, "pa6-loss-shapes")

# ---- pa7: memory bars (paper numbers) ----
def pa7_memory():
    W, H = FULL, 2.3
    fig = plt.figure(figsize=(W, H))
    a1 = fig.add_axes([0.09, 0.2, 0.25, 0.58]); style(a1)
    a2 = fig.add_axes([0.46, 0.2, 0.25, 0.58]); style(a2)
    a1.bar([0, 1], [4.99, 1.65], 0.6, color=[BLK, RED])
    for x, v in ((0, 4.99), (1, 1.65)): a1.text(x, v + 0.1, f"{v:.2f} GB", ha="center", fontsize=5.8)
    a1.set_xticks([0, 1]); a1.set_xticklabels(["fp32", "NF4"], fontsize=5.8); a1.set_ylim(0, 6); a1.set_ylabel("16-layer decoder on disk", fontsize=5.8)
    a2.bar([0, 1], [957, 42], 0.6, color=[BLK, RED])
    for x, v in ((0, 957), (1, 42)): a2.text(x, v + 25, f"{v} MB", ha="center", fontsize=5.8)
    a2.set_xticks([0, 1]); a2.set_xticklabels(["second\n4-bit base", "second\nadapter"], fontsize=5.8); a2.set_ylim(0, 1100); a2.set_ylabel("cost of a second copy", fontsize=5.8)
    fig.text(0.02, 0.9, "(a) 4-bit weights shrink memory", fontsize=FS + 0.3, fontweight="bold")
    fig.text(0.40, 0.9, "(b) A second adapter is cheap", fontsize=FS + 0.3, fontweight="bold")
    fig.text(0.77, 0.84, "Arithmetic from the paper", fontsize=6.2, fontweight="bold", va="top")
    fig.text(0.77, 0.74, "4.99 / 1.65 = 3.02× smaller\n(not 8×)\n\n957 − 42 = 915 MB saved\n957 / 42 = 22.8×\n\n957 + 2 × 42 = 1,041 MB\n≈ 1.05 GB resident", fontsize=5.8, linespacing=1.4, va="top")
    save(fig, "pa7-memory")

# ---- pa8: FAR(t) as survival function; threshold = quantile ----
def pa8_quantile():
    negs = np.array(sorted([0.02, 0.03, 0.05, 0.07, 0.08, 0.10, 0.12, 0.15, 0.22, 0.45, 0.30, 0.18, 0.09, 0.06, 0.04, 0.55, 0.11, 0.13, 0.17, 0.25]))
    W, H = FULL, 2.6
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0.09, 0.2, 0.55, 0.62]); style(ax)
    t = np.linspace(0, 1, 1001)
    far = lambda s: np.array([(s >= x).mean() for x in t])
    ax.step(t, far(negs), where="post", color=BLK, lw=1.2, label="model A scores")
    ax.step(t, far(np.sqrt(negs)), where="post", color=RED, lw=1.2, label=r"model B = $\sqrt{\mathrm{score}}$ (same ranking)")
    ax.axhline(0.15, color=BLK, lw=0.5, ls=":")
    ax.scatter([0.30, np.sqrt(0.30)], [0.15, 0.15], color=[BLK, RED], s=18, zorder=4)
    ax.text(0.31, 0.19, "$t_A = 0.30$", fontsize=5.8); ax.text(np.sqrt(0.30) + 0.01, 0.19, f"$t_B = {np.sqrt(0.30):.2f}$", fontsize=5.8, color=RED)
    ax.set_xlabel("threshold $t$", fontsize=FS); ax.set_ylabel(r"FAR$(t)$ = share of negatives with $p \geq t$", fontsize=FS)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1.02); ax.legend(frameon=False, fontsize=5.7, loc="upper right")
    fig.text(0.68, 0.84, "Same ranking,\nsame AUROC,\ndifferent threshold", fontsize=6.4, fontweight="bold", va="top")
    fig.text(0.68, 0.58, "20 toy negative scores.\nA 15% FAR budget needs\n$t_A = 0.30$ for model A\nand $t_B = 0.55$ for model B.\n\nSo a threshold cannot be\ncarried across models.", fontsize=5.8, linespacing=1.4, va="top")
    ttl(fig, "The threshold for a false-alarm budget is a quantile of the negative scores (toy data)")
    save(fig, "pa8-threshold-quantile")

if __name__ == "__main__":
    for f in (pa1_toy_markers, pa2_toy_sweep, pa3_cost_rate, pa4_amdahl, pa5_precision, pa6_loss, pa7_memory, pa8_quantile):
        f()
