"""Figures for page 18 (optimization). Toy figures say so; the schedule uses the paper's 53,772 steps."""
from common import *
from fig6 import style
import numpy as np, math

def ttl(fig, s, y=0.95, x=0.02):
    fig.text(x, y, s, fontsize=FS + 0.5, fontweight="bold")

# --- o1: gradient descent on a bowl ---
def o1_descent():
    W, H = FULL, 2.7
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0.07, 0.2, 0.42, 0.52]); style(ax)
    x = np.linspace(-4.6, 4.6, 300); ax.plot(x, x**2, color=BLK, lw=1.0)
    xs = [4.0]
    for _ in range(5): xs.append(xs[-1] - 0.1 * 2 * xs[-1])
    ax.plot(xs, [v**2 for v in xs], color=RED, lw=0.8, marker="o", ms=3.5)
    for i, v in enumerate(xs): ax.text(v, v**2 + 1.2, f"{v:.2f}", fontsize=5.4, ha="center", color=RED)
    ax.set_xlabel("weight $x$", fontsize=FS); ax.set_ylabel("loss $f(x) = x^2$", fontsize=FS)
    ax.set_ylim(0, 20)
    fig.text(0.02, 0.97, "(a) Walk downhill: $x \\leftarrow x - \\eta\\, f'(x)$", fontsize=FS + 0.3, fontweight="bold")
    b = fig.add_axes([0.58, 0.2, 0.4, 0.52]); style(b)
    t = np.arange(0, 8)
    for lr, ls, col, lab in ((0.05, ":", BLK, r"$\eta=0.05$ (slow)"), (0.4, "-", RED, r"$\eta=0.4$ (good)"), (0.95, "--", BLK, r"$\eta=0.95$ (zig-zag)"), (1.1, "-.", BLK, r"$\eta=1.1$ (blows up)")):
        v = [4.0]
        for _ in range(7): v.append(v[-1] * (1 - 2 * lr))
        b.plot(t, v, ls=ls, color=col, lw=1.1, marker="o", ms=2.2, label=lab)
    b.axhline(0, color=BLK, lw=0.4); b.set_ylim(-9, 9)
    b.set_xlabel("step", fontsize=FS); b.set_ylabel("weight $x$", fontsize=FS); b.legend(frameon=False, fontsize=5.4, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2)
    fig.text(0.52, 0.97, "(b) The learning rate $\\eta$ sets the step size", fontsize=FS + 0.3, fontweight="bold")
    fig.text(0.02, 0.03, "Toy: $f(x)=x^2$, so $f'(x)=2x$ and each step multiplies $x$ by $(1-2\\eta)$. Start $x=4$. With $\\eta=0.1$: 4, 3.20, 2.56, 2.05, 1.64, 1.31.", fontsize=5.6)
    save(fig, "o1-descent")

# --- o2: Adam vs plain steps ---
def o2_adam():
    W, H = FULL, 2.6
    fig = plt.figure(figsize=(W, H))
    a = fig.add_axes([0.08, 0.2, 0.38, 0.6]); style(a)
    g = np.logspace(-1, 2, 100); lr = 0.1
    a.plot(g, lr * g, color=BLK, lw=1.1, ls="--", label="plain step $\\eta g$")
    a.plot(g, np.full_like(g, lr), color=RED, lw=1.4, label="Adam, first step")
    a.set_xscale("log"); a.set_yscale("log"); a.set_ylim(0.03, 20)
    a.set_xlabel("size of the gradient $g$", fontsize=FS); a.set_ylabel("size of the first step", fontsize=FS); a.legend(frameon=False, fontsize=5.6, loc="upper left")
    fig.text(0.02, 0.9, "(a) First step: Adam ignores the gradient's scale", fontsize=FS + 0.3, fontweight="bold")
    b = fig.add_axes([0.58, 0.2, 0.4, 0.6]); style(b)
    b1, b2 = 0.9, 0.999; m = v = 0; th = 1.0; ths = [th]; ups = []
    for t, gg in enumerate([0.5, 0.25, -0.1], 1):
        m = b1 * m + (1 - b1) * gg; v = b2 * v + (1 - b2) * gg * gg
        up = 0.1 * (m / (1 - b1**t)) / (math.sqrt(v / (1 - b2**t)) + 1e-8); th -= up; ths.append(th); ups.append(up)
    b.plot([0, 1, 2, 3], ths, color=RED, lw=1.2, marker="o", ms=3)
    for i, tv in enumerate(ths): b.text(i, tv + 0.03, f"{tv:.4f}", fontsize=5.6, ha="center")
    b.set_xticks([0, 1, 2, 3]); b.set_xlabel("step $t$", fontsize=FS); b.set_ylabel("weight $\\theta$", fontsize=FS); b.set_ylim(0.65, 1.1)
    fig.text(0.52, 0.9, "(b) Three Adam steps (toy)", fontsize=FS + 0.3, fontweight="bold")
    fig.text(0.52, 0.03, "gradients 0.5, 0.25, −0.1; $\\eta = 0.1$; steps 0.1000, 0.0932, 0.0597", fontsize=5.6)
    save(fig, "o2-adam")

# --- o3: OneCycle schedule (paper's 53,772 steps) ---
def o3_schedule():
    T = 53772; w = int(0.1 * T) - 1; mx = 2e-5; ini = mx / 25; fin = ini / 1e4
    def cos(s, e, p): return e + (s - e) / 2 * (1 + math.cos(math.pi * p))
    t = np.arange(0, T, 20)
    lr = [cos(ini, mx, x / w) if x <= w else cos(mx, fin, (x - w) / (T - 1 - w)) for x in t]
    W, H = FULL, 2.5
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0.09, 0.2, 0.6, 0.62]); style(ax)
    ax.plot(t, np.array(lr) * 1e5, color=RED, lw=1.4)
    ax.axvspan(0, w, facecolor="white", edgecolor=BLK, hatch="////", lw=0.3, alpha=0.5)
    ax.text(w / 2, 1.0, "warm-up\n(10%)", fontsize=5.6, ha="center", bbox=dict(fc="white", ec="none", pad=0.8))
    ax.text(30000, 1.2, "anneal (cosine)", fontsize=5.8)
    ax.set_xlabel("optimizer step (2 epochs = 53,772 steps)", fontsize=FS); ax.set_ylabel(r"learning rate ($\times10^{-5}$)", fontsize=FS)
    ax.set_ylim(0, 2.35); ax.set_xlim(0, T)
    fig.text(0.73, 0.78, "Computed values", fontsize=6.2, fontweight="bold", va="top")
    rows = [(0, 8.0e-7), (1000, 2.393e-6), (5376, 2.0e-5), (15000, 1.811e-5), (26886, 1.174e-5), (40000, 3.737e-6), (53771, 8.0e-11)]
    fig.text(0.73, 0.7, "\n".join(f"step {a:>6,}:  {b:.2e}" for a, b in rows), fontsize=5.8, va="top", linespacing=1.55)
    ttl(fig, "The learning rate rises, then falls (peak $2\\times10^{-5}$, shape from the code)")
    save(fig, "o3-schedule")

# --- o4: accumulation ---
def o4_accum():
    W, H = FULL, 2.4
    fig, ax = canvas(W, H)
    label(ax, 0.08, H - 0.12, "Gradient accumulation: 4 small batches, 1 weight update (code defaults)", ha="left", bold=True)
    for j in range(4):
        x = 0.2 + j * 1.2
        box(ax, x, 1.5, 0.95, 0.45, f"micro-batch {j+1}\n2 rows", fs=5.8)
        arrow(ax, (x + 0.47, 1.5), (x + 0.47, 1.2))
        box(ax, x, 0.8, 0.95, 0.4, f"gradient $g_{j+1}$", fs=5.8)
        line(ax, (x + 0.47, 0.8), (x + 0.47, 0.55), lw=0.5)
    line(ax, (0.67, 0.55), (5.0, 0.55), lw=0.5)
    arrow(ax, (5.0, 0.55), (5.3, 0.55), lw=0.5)
    box(ax, 5.3, 0.3, 1.5, 0.5, "add up, average:\n$g = \\frac{1}{4}(g_1+g_2+g_3+g_4)$", fs=5.6, color=RED)
    label(ax, 6.05, 0.12, "ONE optimizer step on 8 rows", fs=5.9, color=RED)
    label(ax, 0.2, 0.2, "Why: 8 rows may not fit in memory at once; 2 rows do.", ha="left", fs=5.8)
    save(fig, "o4-accumulation")

# --- o5: float16 scaling number line ---
def o5_fp16():
    W, H = FULL, 2.4
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0.07, 0.25, 0.9, 0.5]); style(ax)
    xs = np.array([-12, -10, -8, -6, -4]); ax.set_xlim(-12.5, -2.5); ax.set_ylim(0, 1)
    ax.set_xticks(xs); ax.set_xticklabels([f"$10^{{{x}}}$" for x in xs], fontsize=6); ax.set_yticks([])
    ax.axvspan(-12.5, math.log10(2**-24), facecolor="white", edgecolor=RED, hatch="////", lw=0.3)
    ax.text(-11.3, 0.7, "float16 rounds\nthese to 0", fontsize=5.8, color=RED, ha="center", bbox=dict(fc="white", ec="none", pad=1.0))
    ax.axvline(math.log10(2**-24), color=RED, lw=1.0); ax.text(math.log10(2**-24) + 0.1, 0.9, r"smallest float16 $\approx 6\times10^{-8}$", fontsize=5.6, color=RED)
    ax.axvline(math.log10(2**-14), color=BLK, lw=0.8, ls="--"); ax.text(math.log10(2**-14) + 0.1, 0.78, r"smallest normal $\approx 6.1\times10^{-5}$", fontsize=5.6)
    ax.scatter([-8], [0.3], color=BLK, s=20, zorder=4); ax.text(-8, 0.12, "a gradient $10^{-8}$", ha="center", fontsize=5.6, bbox=dict(fc="white", ec="none", pad=1.0), zorder=6)
    ax.annotate("", xy=(math.log10(1e-8 * 65536), 0.3), xytext=(-8, 0.3), arrowprops=dict(arrowstyle="-|>", lw=0.8, color=RED, mutation_scale=6))
    ax.scatter([math.log10(1e-8 * 65536)], [0.3], color=RED, s=22, zorder=4); ax.text(math.log10(1e-8 * 65536), 0.14, "× 65,536 = $6.6\\times10^{-4}$", ha="center", fontsize=5.6, color=RED)
    ax.set_xlabel("size of a gradient value", fontsize=FS)
    ttl(fig, "Loss scaling lifts tiny gradients out of float16's zero zone, then divides back")
    save(fig, "o5-fp16-scaling")

# --- o6: clipping ---
def o6_clip():
    W, H = FULL, 2.7
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0.06, 0.12, 0.3, 0.72]); ax.set_aspect("equal"); ax.axis("off")
    th = np.linspace(0, 2 * np.pi, 200); ax.plot(np.cos(th), np.sin(th), color=BLK, lw=0.7, ls="--")
    ax.annotate("", xy=(0.28, 0.28), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=BLK, lw=1.0, mutation_scale=7))
    ax.annotate("", xy=(2.4, 1.8), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=BLK, lw=0.6, ls=":", mutation_scale=7))
    ax.annotate("", xy=(0.8, 0.6), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.3, mutation_scale=7))
    ax.text(-0.55, -0.62, "norm 0.4: kept as is", fontsize=5.6); ax.text(1.9, 2.05, "norm 3 (dotted):\nscaled by 1/3", fontsize=5.6, color=BLK, ha="center"); ax.text(1.0, 0.25, "clipped to\nnorm 1", fontsize=5.6, color=RED)
    ax.text(-1.25, -1.2, "dashed circle: norm 1", fontsize=5.6); ax.set_xlim(-1.3, 3); ax.set_ylim(-1.3, 2.3)
    fig.text(0.02, 0.9, "(a) Same direction, capped length", fontsize=FS + 0.3, fontweight="bold")
    b = fig.add_axes([0.5, 0.2, 0.46, 0.62]); style(b)
    n = np.linspace(0.05, 6, 200); b.plot(n, n, color=BLK, lw=0.9, ls="--", label="before clipping"); b.plot(n, np.minimum(n, 1), color=RED, lw=1.5, label="after clipping (max norm 1)")
    b.set_xlabel("gradient norm $\\|g\\|$", fontsize=FS); b.set_ylabel("norm used in the update", fontsize=FS); b.legend(frameon=False, fontsize=5.6, loc="upper left")
    fig.text(0.44, 0.9, "(b) $g \\leftarrow g \\cdot \\min(1,\\ 1/\\|g\\|)$", fontsize=FS + 0.3, fontweight="bold")
    save(fig, "o6-clipping")

# --- o7: LoRA zero start ---
def o7_lora_zero():
    W, H = FULL, 2.9
    fig, ax = canvas(W, H)
    label(ax, 0.08, H - 0.12, "LoRA starts with $B = 0$: first $B$ learns, then $A$ can learn (toy numbers)", ha="left", bold=True)
    box(ax, 0.2, 1.55, 0.6, 0.5, "$x$\n(2, 1)", fs=5.8)
    box(ax, 1.3, 1.55, 0.95, 0.5, "$A$ = (1, 1)\nmakes $u=Ax=3$", fs=5.6)
    box(ax, 2.7, 1.55, 0.95, 0.5, "$B$ = (0, 0)ᵀ\nstart at zero", fs=5.6, color=RED)
    box(ax, 4.1, 1.55, 0.9, 0.5, "update to\n$y$: $B u = 0$", fs=5.6)
    for a, b in ((0.8, 1.3), (2.25, 2.7), (3.65, 4.1)): arrow(ax, (a, 1.8), (b, 1.8))
    label(ax, 5.55, 1.8, "gradient from the loss\narriving at $y$:  $\\delta = (1, -1)$", fs=5.8)
    label(ax, 0.2, 1.1, "gradient on $B$:  $s\\,\\delta\\,u^{\\top} = 2\\cdot(1,-1)\\cdot3 = (6, -6)$  → big, so $B$ moves first", ha="left", fs=6.0, color=RED)
    label(ax, 0.2, 0.8, "gradient on $A$:  $s\\,B^{\\top}\\delta\\,x^{\\top}$;  with $B=0$ this is $(0, 0)$  → $A$ waits", ha="left", fs=6.0)
    label(ax, 0.2, 0.5, "after $B = (0.1, -0.2)$:  $B^{\\top}\\delta = 0.3$,  gradient on $A$ = $2\\cdot0.3\\cdot(2,1) = (1.2, 0.6)$  → now $A$ learns too", ha="left", fs=6.0)
    label(ax, 0.2, 0.2, "Here $s=\\alpha/r=2$. The model equals the pre-trained model at step 0, so training starts from a safe point.", ha="left", fs=5.8)
    save(fig, "o7-lora-zero")

# --- o8: which layers get which gradient ---
def o8_gradient_flow():
    W, H = FULL, 3.7
    fig, ax = canvas(W, H)
    label(ax, 0.08, H - 0.12, "Which layers learn from which loss? (16 layers; gate reads layer $k$)", ha="left", bold=True)
    for row, k in enumerate((6, 10)):
        y = 2.35 - row * 1.45
        label(ax, 0.08, y + 0.18, f"$k = {k}$", ha="left", fs=6.4, bold=True)
        for j in range(16):
            block3d(ax, 0.85 + j * 0.27, y, 0.18, 0.34, 0.06, RED if j < k else BLK)
        xk = 0.85 + (k - 1) * 0.27 + 0.09
        arrow(ax, (xk, y - 0.02), (xk, y - 0.28), color=RED)
        box(ax, xk - 0.5, y - 0.52, 1.0, 0.24, "gate head $W_c$", fs=5.6, color=RED)
        ax.plot([0.85, 0.85 + (k - 1) * 0.27 + 0.18], [y + 0.55, y + 0.55], color=RED, lw=0.8)
        label(ax, 0.85 + (k - 1) * 0.27 / 2 + 0.09, y + 0.67, "gate loss AND hint loss", fs=5.5, color=RED)
        ax.plot([0.85 + k * 0.27, 0.85 + 15 * 0.27 + 0.18], [y + 0.55, y + 0.55], color=BLK, lw=0.8)
        label(ax, 0.85 + (k + 15) * 0.27 / 2 + 0.09, y + 0.67, "hint loss only", fs=5.5)
    label(ax, 0.08, 0.15, "Red blocks are shared by both jobs. Black blocks learn only to write the hint. The head learns only from the gate loss.", ha="left", fs=5.9)
    save(fig, "o8-gradient-flow")

if __name__ == "__main__":
    for f in (o1_descent, o2_adam, o3_schedule, o4_accum, o5_fp16, o6_clip, o7_lora_zero, o8_gradient_flow): f()
