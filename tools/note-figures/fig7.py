from common import *
from fig6 import style
import numpy as np
from matplotlib.patches import Patch

def title(fig, s, x=0.02):
    fig.text(x, 0.94, s, fontsize=FS + 0.5, fontweight="bold")

# ---- 11: from text to hidden state (concept) ----
def fig_text_to_hidden():
    W, H = FULL, 2.1
    fig, ax = canvas(W, H)
    label(ax, 0.08, H - 0.12, "From text to a decision: what happens inside the model", ha="left", bold=True)
    y = 1.2
    xs = [0.08, 1.13, 2.18, 3.23]
    names = ["text", "tokens\n(toy split)", "token IDs\n(integers)", "embeddings\n(vectors, length $d$)"]
    for x, n in zip(xs, names):
        box(ax, x, y, 0.85, 0.5, n, fs=5.9)
    for a_, b_ in zip(xs[:-1], xs[1:]):
        arrow(ax, (a_ + 0.85, y + 0.25), (b_, y + 0.25))
    label(ax, 0.5, y - 0.15, "dance performance", fs=5.6)
    label(ax, 1.55, y - 0.15, "dance | performance", fs=5.6)
    arrow(ax, (xs[3] + 0.85, y + 0.25), (4.2, y + 0.25))
    for i in range(6):
        block3d(ax, 4.25 + i * 0.26, y + 0.05, 0.2, 0.34, 0.06, RED if i == 2 else BLK)
    label(ax, 4.25 + 3 * 0.26, y + 0.62, "layers 1 … $L$", fs=6.0)
    hx = 4.25 + 2 * 0.26 + 0.13
    label(ax, hx, y - 0.15, "$h_k$", fs=6.2, color=RED)
    arrow(ax, (hx, y - 0.25), (hx, 0.82), color=RED)
    box(ax, 4.0, 0.42, 1.55, 0.4, "classifier head $W_c$\n2 scores → $p_i$", color=RED, fs=5.9)
    arrow(ax, (4.25 + 6 * 0.26 + 0.06, y + 0.22), (6.15, y + 0.22))
    box(ax, 6.15, y - 0.03, 0.62, 0.5, "LM head\n→ next\ntoken", fs=5.6)
    label(ax, 0.08, 0.65, "Each layer rewrites every token's vector\nusing attention and an MLP.", ha="left", fs=6.0)
    save(fig, "fig11-text-to-hidden")

# ---- 13: focal loss curves ----
def fig_focal():
    W, H = COL * 1.5, 2.4
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0.14, 0.2, 0.82, 0.66]); style(ax)
    p = np.linspace(0.02, 0.999, 400)
    ce = -np.log(p)
    ax.plot(p, ce, color=BLK, lw=0.9, label=r"cross-entropy ($\gamma=0$)")
    ax.plot(p, (1 - p) ** 1.5 * ce, color=RED, lw=1.1, label=r"focal loss, $\gamma=1.5$ (our code)")
    ax.plot(p, (1 - p) ** 2 * ce, color=BLK, lw=0.9, ls="--", label=r"focal loss, $\gamma=2$")
    ax.set_ylim(0, 3.2); ax.set_xlim(0, 1)
    ax.set_xlabel(r"probability given to the true class, $p_t$", fontsize=FS)
    ax.set_ylabel("loss", fontsize=FS)
    ax.legend(frameon=False, fontsize=5.9, loc="upper right")
    ax.annotate("easy example:\nthe loss almost vanishes", xy=(0.9, 0.0035 * 1.0 + 0.02), xytext=(0.52, 0.75), fontsize=5.8,
                arrowprops=dict(arrowstyle="-|>", lw=0.5, color=BLK, mutation_scale=5))
    title(fig, "Focal loss shrinks the loss on easy examples")
    save(fig, "fig13-focal-loss")

# ---- 14: gate comparison (Table 2) ----
def fig_gates():
    W, H = FULL, 2.7
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0.27, 0.16, 0.69, 0.72]); style(ax)
    rows = [("RoBERTa-large, ASL recipe", 0.8113), ("Llama-3.2-1B (our gate)", 0.8002), ("Qwen2.5-0.5B", 0.7849),
            ("SmolLM2-360M", 0.7800), ("Gemma-3-1B", 0.7600), ("RoBERTa-large, matched LoRA", 0.7483),
            ("Gemma-3-270M", 0.7212), ("Logistic regression, 21 features", 0.3456),
            ("Prompted LLM, few-shot", 0.1914), ("Prompted LLM, zero-shot", 0.1381)]
    for i, (n, v) in enumerate(rows):
        y = len(rows) - i
        ax.barh(y, v, height=0.62, color=RED if "our gate" in n else BLK)
        ax.text(v + 0.01, y, f"{v:.4f}", va="center", fontsize=5.9)
    ax.set_yticks(range(len(rows), 0, -1)); ax.set_yticklabels([r[0] for r in rows])
    ax.set_xlim(0, 0.95); ax.set_xlabel("gate PA-F1 on the test set", fontsize=FS)
    title(fig, "Which model makes the best gate? (Table 2)")
    save(fig, "fig14-gate-comparison")

# ---- 15: ranking vs calibration (Table S4) ----
def fig_calibration():
    W, H = FULL, 2.6
    fig = plt.figure(figsize=(W, H))
    rows = [("RoBERTa-large ASL", 0.8902, 0.3036), ("Llama-3.2-1B", 0.8883, 0.0909), ("Qwen2.5-0.5B", 0.8642, 0.0813),
            ("SmolLM2-360M", 0.8596, 0.0977), ("Gemma-3-1B", 0.8415, 0.0425), ("RoBERTa-large (E0b, 256)", 0.8150, 0.0923),
            ("RoBERTa-large (E0b, 512)", 0.8132, 0.0979), ("Gemma-3-270M", 0.7784, 0.0761)]
    a1 = fig.add_axes([0.25, 0.17, 0.3, 0.7]); style(a1)
    a2 = fig.add_axes([0.66, 0.17, 0.3, 0.7]); style(a2)
    n = len(rows)
    for i, (nm, au, ece) in enumerate(rows):
        y = n - i
        a1.barh(y, au, height=0.62, color=BLK)
        a1.text(au + 0.005, y, f"{au:.4f}", va="center", fontsize=5.6)
        a2.barh(y, ece, height=0.62, color=RED if nm in ("RoBERTa-large ASL", "Gemma-3-1B") else BLK)
        a2.text(ece + 0.008, y, f"{ece:.4f}", va="center", fontsize=5.6)
    a1.set_yticks(range(n, 0, -1)); a1.set_yticklabels([r[0] for r in rows])
    a2.set_yticks(range(n, 0, -1)); a2.set_yticklabels([])
    a1.set_xlim(0.7, 0.95); a2.set_xlim(0, 0.38)
    a1.set_xlabel("AUPRC (higher = ranks better)", fontsize=FS)
    a2.set_xlabel("ECE (lower = better probabilities)", fontsize=FS)
    title(fig, "The best-ranking gate is the worst calibrated (Table S4)")
    save(fig, "fig15-ranking-vs-calibration")

# ---- 16: retrieval grid ----
def fig_retrieval():
    W, H = FULL, 2.3
    fig, ax = canvas(W, H)
    label(ax, 0.08, H - 0.12, "Retrieval never beats the full profile (exact match, 200-marker subsample)", ha="left", bold=True)
    ks = [1, 3, 5, 7, 10, 15, 20]
    data = {"bm25": [0.20, 0.25, 0.28, 0.30, 0.30, 0.31, 0.32],
            "tfidf": [0.21, 0.26, 0.28, 0.29, 0.29, 0.30, 0.32],
            "embed": [0.16, 0.27, 0.29, 0.30, 0.31, 0.31, 0.32],
            "hybrid": [0.18, 0.28, 0.29, 0.29, 0.29, 0.32, 0.32]}
    x0, y0, cw, ch = 1.0, 0.45, 0.58, 0.34
    for j, k in enumerate(ks):
        label(ax, x0 + j * cw + cw / 2, y0 + 4 * ch + 0.13, str(k), fs=6.2)
    label(ax, x0 - 0.1, y0 + 4 * ch + 0.13, "units kept $k$:", ha="right", fs=6.2)
    for i, (nm, vals) in enumerate(data.items()):
        yy = y0 + (3 - i) * ch
        label(ax, x0 - 0.1, yy + ch / 2, nm, ha="right", fs=6.2)
        for j, v in enumerate(vals):
            box(ax, x0 + j * cw, yy, cw, ch, f"{v:.2f}", fs=6.0)
    bx = x0 + len(ks) * cw + 0.25
    box(ax, bx, y0 + 1.5 * ch, 1.05, 0.7, "full profile\n(control)\n0.305", color=RED, fs=6.2)
    label(ax, bx + 0.55, y0 + 0.9 * ch, "none of the 45\nconfigurations beats\nit after Holm\ncorrection", fs=5.8)
    save(fig, "fig16-retrieval-grid")

# ---- 17: noise floor and seeds ----
def fig_noise():
    plt.rcParams["hatch.linewidth"] = 0.4
    W, H = FULL, 2.4
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0.2, 0.28, 0.76, 0.56]); style(ax)
    wb = dict(fc="white", ec="none", pad=0.8)
    c = 0.8002
    m6 = 0.7846
    ax.axvspan(m6 - 0.0035, m6 + 0.0035, facecolor="white", edgecolor=BLK, hatch="//", lw=0.4)
    ax.axvline(c, color=BLK, lw=0.7, ls="--", zorder=1)
    ax.text(c, 2.65, "cascade 1B gate: 0.8002", fontsize=5.8, ha="center", bbox=wb)
    ax.errorbar([0.7846], [2], xerr=[0.0033], fmt="o", color=RED, ms=4, capsize=2, lw=0.8, zorder=3)
    ax.errorbar([0.8022], [1], xerr=[0.0029], fmt="o", color=RED, ms=4, capsize=2, lw=0.8, zorder=3)
    ax.scatter([0.8022, 0.8164], [2, 1], marker="D", s=14, facecolor="white", edgecolor=BLK, linewidth=0.7, zorder=4)
    ax.text(0.7846, 1.68, "0.7846 ± 0.0033", fontsize=5.8, ha="center", color=RED, bbox=wb, zorder=5)
    ax.text(0.8022, 0.68, "0.8022 ± 0.0029", fontsize=5.8, ha="center", color=RED, bbox=wb)
    ax.text(0.8062, 2.25, "final checkpoint 0.8022", fontsize=5.6, ha="left", bbox=wb)
    ax.text(0.8164, 1.3, "final checkpoint 0.8164", fontsize=5.6, ha="center", bbox=wb)
    ax.set_yticks([2, 1]); ax.set_yticklabels(["unified $k=6$", "unified $k=10$"])
    ax.set_ylim(0.4, 2.9); ax.set_xlim(0.775, 0.822)
    ax.set_xlabel("gate PA-F1", fontsize=FS)
    title(fig, "Seeds, noise floor and the cascade gate")
    fig.text(0.2, 0.03, "red: mean ± SD over 3 seeds at step 21,703.  open diamonds: final checkpoint, one seed.  hatched band: noise floor (0.0070 wide) around the $k=6$ mean.", fontsize=5.6)
    save(fig, "fig17-noise-floor")

# ---- 18: CPU savings ----
def fig_cpu():
    W, H = COL * 1.5, 2.3
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0.13, 0.2, 0.84, 0.64]); style(ax)
    vals = {"ideal $16/k$": [2.67, 1.60], "ONNX Runtime, NF4": [2.86, 1.51], "PyTorch eager": [1.75, 1.35]}
    w = 0.26
    styles = [dict(facecolor="white", edgecolor=BLK, linewidth=0.7, hatch="////"), dict(color=RED), dict(color=BLK)]
    for i, ((nm, v), st) in enumerate(zip(vals.items(), styles)):
        xs = [0 + (i - 1) * w, 1 + (i - 1) * w]
        ax.bar(xs, v, w, label=nm, **st)
        for x, y in zip(xs, v):
            ax.text(x, y + 0.05, f"{y:.2f}", ha="center", fontsize=5.6)
    ax.set_xticks([0, 1]); ax.set_xticklabels(["exit at $k=6$", "exit at $k=10$"])
    ax.set_ylim(0, 3.5); ax.set_ylabel("speed-up of the gate (×)", fontsize=FS)
    ax.legend(frameon=False, fontsize=5.8, loc="upper right")
    title(fig, "How much time the early exit really saves on a CPU")
    save(fig, "fig18-cpu-savings")

# ---- 19: error types ----
def fig_errors():
    W, H = FULL, 2.2
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0.2, 0.2, 0.76, 0.48]); style(ax)
    rows = [("Llama-3.2-1B (1B gen)", [29.7, 17.8, 35.9, 16.6]), ("Llama-3.1-8B (8B gen)", [29.5, 27.9, 23.5, 19.1]),
            ("Qwen2.5-7B (7B gen)", [35.8, 18.5, 27.3, 18.4])]
    cats = ["exact", "partial overlap", "grounded, other", "hallucinated"]
    styles = [dict(color=RED), dict(facecolor="white", edgecolor=BLK, linewidth=0.7), dict(facecolor="white", edgecolor=BLK, hatch="////", linewidth=0.5), dict(color=BLK)]
    for i, (nm, v) in enumerate(rows):
        y = len(rows) - i; left = 0
        for j, (c, val) in enumerate(zip(cats, v)):
            ax.barh(y, val, left=left, height=0.6, **styles[j])
            ax.text(left + val / 2, y, f"{val:.1f}", ha="center", va="center", fontsize=5.6, color="white" if j in (0, 3) else BLK,
                    bbox=dict(fc="white", ec="none", pad=0.6) if j == 2 else None)
            left += val
    ax.set_yticks([3, 2, 1]); ax.set_yticklabels([r[0] for r in rows])
    ax.set_xlim(0, 100); ax.set_xlabel("% of the 3,356 true triggers", fontsize=FS)
    ax.legend(handles=[Patch(**{k: v for k, v in s.items() if k != "color"}, **({"facecolor": s["color"], "edgecolor": s["color"]} if "color" in s else {}), label=c) for s, c in zip(styles, cats)],
              frameon=False, fontsize=5.6, ncol=4, loc="lower center", bbox_to_anchor=(0.5, 1.02))
    title(fig, "What the wrong hints look like (Table 6)")
    save(fig, "fig19-error-types")

# ---- 20: human forest plot ----
def fig_forest():
    W, H = FULL, 2.4
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0.34, 0.2, 0.44, 0.62]); style(ax)
    rows = [("H1: 8B with memory vs without (95% CI)", 0.83, 0.48, 1.23, True),
            ("H2a: unified $k=6$ vs 1B", 0.04, -0.31, 0.41, False),
            ("H2b: unified $k=10$ vs 1B", -0.02, -0.35, 0.30, False),
            ("H2a: unified $k=6$ vs 8B (memory)", -0.38, -0.69, -0.04, False),
            ("H2b: unified $k=10$ vs 8B (memory)", -0.44, -0.83, -0.07, False)]
    n = len(rows)
    for i, (nm, d, lo, hi, red) in enumerate(rows):
        y = n - i
        ax.plot([lo, hi], [y, y], color=RED if red else BLK, lw=1.0)
        ax.scatter([d], [y], s=14, color=RED if red else BLK, zorder=3)
        ax.text(1.04, y, f"{d:+.2f}  [{lo:+.2f}, {hi:+.2f}]", fontsize=5.7, va="center", transform=ax.get_yaxis_transform())
    ax.axvline(0, color=BLK, lw=0.7)
    ax.axvline(-0.25, color=BLK, lw=0.6, ls="--")
    ax.text(-0.25, n + 0.55, "non-inferiority\nmargin −0.25", fontsize=5.6, ha="center", va="bottom")
    ax.set_yticks(range(n, 0, -1)); ax.set_yticklabels([r[0] for r in rows])
    ax.set_xlim(-1.0, 1.3); ax.set_ylim(0.4, n + 0.5)
    ax.set_xlabel("difference in mean uptake (A − B, 1–5 scale)", fontsize=FS)
    fig.text(0.02, 0.94, "Human uptake: paired differences with confidence intervals (Table 7a)", fontsize=FS + 0.5, fontweight="bold")
    save(fig, "fig20-human-forest")

if __name__ == "__main__":
    for f in (fig_text_to_hidden, fig_focal, fig_gates, fig_calibration, fig_retrieval, fig_noise, fig_cpu, fig_errors, fig_forest):
        f()
