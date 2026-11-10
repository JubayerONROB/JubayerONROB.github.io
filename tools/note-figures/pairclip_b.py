from common import *
from fig6 import style
import numpy as np
from matplotlib.patches import Patch

def title(fig, s, x=0.02, y=0.95):
    fig.text(x, y, s, fontsize=FS + 0.5, fontweight="bold")

EP = list(range(12, 20))
NONAVG = [95.70, 95.61, 91.05, 93.88, 92.22, 90.36, 93.49, 95.67]
SWA = [95.70, 95.61, 95.61, 95.31, 95.80, 96.35, 97.17, 97.04]
TRAIN = [93.58, 97.01, 95.93, 97.44, 96.65, 97.89, 97.29, 98.48]
L_TR = [.1628, .0802, .1060, .0669, .0885, .0538, .0697, .0351]
L_NA = [.1677, .1684, .2552, .2005, .2344, .3603, .2307, .2226]
L_SW = [.1677, .1684, .1383, .1426, .1386, .1334, .1178, .1227]

def pc9_dynamics():
    W, H = FULL, 2.7
    fig = plt.figure(figsize=(W, H))
    a1 = fig.add_axes([0.08, 0.2, 0.4, 0.6]); style(a1)
    a2 = fig.add_axes([0.58, 0.2, 0.4, 0.6]); style(a2)
    a1.plot(EP, TRAIN, color=BLK, lw=0.7, marker="o", ms=2.5, mfc="white", label="training (running)")
    a1.plot(EP, NONAVG, color=BLK, lw=1.0, ls="--", marker="o", ms=3, label="validation, non-averaged")
    a1.plot(EP, SWA, color=RED, lw=1.2, marker="o", ms=3, label="validation, SWA average")
    a1.annotate("", xy=(17, 96.35), xytext=(17, 90.36), arrowprops=dict(arrowstyle="<|-|>", lw=0.6, color=BLK, mutation_scale=5))
    a1.text(17.12, 93.1, "+5.99", fontsize=6.0)
    a1.set_ylim(89, 102.2); a1.set_xlim(11.7, 19.3); a1.set_yticks([90, 92, 94, 96, 98, 100])
    a1.set_xlabel("epoch", fontsize=FS); a1.set_ylabel("accuracy (%)", fontsize=FS)
    a1.legend(frameon=False, fontsize=5.5, loc="upper left")
    a1.set_xticks(EP)
    a2.plot(EP, L_TR, color=BLK, lw=0.7, marker="o", ms=2.5, mfc="white")
    a2.plot(EP, L_NA, color=BLK, lw=1.0, ls="--", marker="o", ms=3)
    a2.plot(EP, L_SW, color=RED, lw=1.2, marker="o", ms=3)
    a2.text(17, 0.3603 + 0.012, "0.3603", fontsize=5.8, ha="center")
    a2.text(18, 0.1178 - 0.028, "0.1178", fontsize=5.8, ha="center", color=RED)
    a2.text(19, 0.0351 - 0.025, "0.0351", fontsize=5.8, ha="center")
    a2.set_ylim(0, 0.4); a2.set_xlim(11.7, 19.3); a2.set_xticks(EP)
    a2.set_xlabel("epoch", fontsize=FS); a2.set_ylabel("cross-entropy loss", fontsize=FS)
    fig.text(0.02, 0.9, "(a) Accuracy: the average never falls below the iterate", fontsize=FS + 0.3, fontweight="bold")
    fig.text(0.52, 0.9, "(b) Loss: the iterate overfits, the average does not", fontsize=FS + 0.3, fontweight="bold")
    fig.text(0.08, 0.03, "Blocks unfrozen at epochs 12–19: 8, 8, 9, 9, 10, 10, 11, 11 (in-loop values, Table VI)", fontsize=5.8)
    save(fig, "pc9-training-dynamics")


def pc10_metrics():
    W, H = FULL, 2.75
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 0.58, 1]); ax.set_xlim(0, W * 0.58); ax.set_ylim(0, H); ax.axis("off")
    label(ax, 0.08, H - 0.12, "(a) Confusion matrix, SP-Cup validation, $\\tau^\\star = 0.680$", ha="left", bold=True)
    cx, cy, cw, ch = 1.1, 0.95, 1.2, 0.55
    label(ax, cx + cw, cy + 2 * ch + 0.3, "predicted", fs=6.0)
    label(ax, cx + cw / 2, cy + 2 * ch + 0.12, "fake", fs=6.0)
    label(ax, cx + 1.5 * cw, cy + 2 * ch + 0.12, "real", fs=6.0)
    label(ax, cx - 0.1, cy + 1.5 * ch, "true\nfake", ha="right", fs=6.0)
    label(ax, cx - 0.1, cy + 0.5 * ch, "true\nreal", ha="right", fs=6.0)
    box(ax, cx + cw, cy + ch, cw, ch, "FN: 68\nfake accepted as real", fs=5.6)
    box(ax, cx, cy, cw, ch, "FP: 15\nreal flagged fake", fs=5.6)
    box(ax, cx + cw, cy, cw, ch, "TN: 1,533", fs=6.0)
    box(ax, cx, cy + ch, cw, ch, "TP: 1,456", fs=6.0, color=RED)
    label(ax, 0.08, 0.6, "1,524 fake and 1,548 real images in all.", ha="left", fs=5.8)
    label(ax, 0.08, 0.38, "The fake class is the positive class.", ha="left", fs=5.8)
    label(ax, 0.08, 0.16, "Errors: 68 + 15 = 83 of 3,072.", ha="left", fs=5.8)
    a2 = fig.add_axes([0.66, 0.2, 0.31, 0.58]); style(a2)
    x = np.linspace(0, 1, 200)
    a2.plot(x, x, color=BLK, lw=0.6, ls=":")
    a2.plot(x, 1 - (1 - x) ** 6, color=RED, lw=1.2)
    a2.plot(x, 1 - x, color=BLK, lw=0.6, ls="--")
    xe = 0.2
    # EER: where curve meets anti-diagonal
    lo, hi = 0.01, 0.99
    for _ in range(60):
        mid = (lo + hi) / 2
        if (1 - (1 - mid) ** 6) - (1 - mid) > 0: hi = mid
        else: lo = mid
    xe = (lo + hi) / 2
    a2.scatter([xe], [1 - xe], s=14, color=BLK, zorder=4)
    a2.annotate("EER: FPR = FNR", xy=(xe, 1 - xe), xytext=(0.42, 0.66), fontsize=5.6, arrowprops=dict(arrowstyle="-|>", lw=0.5, color=BLK, mutation_scale=5))
    a2.text(0.5, 0.2, "area under\nthe curve =\nAU-ROC", fontsize=5.6, ha="center")
    a2.text(0.55, 0.52, "chance", fontsize=5.4, rotation=33)
    a2.set_xlim(0, 1); a2.set_ylim(0, 1.02)
    a2.set_xlabel("false-positive rate", fontsize=FS); a2.set_ylabel("true-positive rate", fontsize=FS)
    fig.text(0.6, 0.9, "(b) ROC curve (schematic)", fontsize=FS + 0.5, fontweight="bold")
    fig.text(0.6, 0.03, "Ours: AU-ROC 98.64%, EER 4.07%.", fontsize=5.8)
    save(fig, "pc10-metrics")


def pc11_comparison():
    W, H = FULL, 4.3
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0.27, 0.12, 0.7, 0.78]); style(ax)
    rows = [("PairCLIP-SWA, tuned $\\tau^\\star$ (†)", 97.30, "ours_o"), ("PairCLIP-SWA", 97.04, "ours"), ("PairCLIP, best regular", 95.67, "ours2"),
            ("CAE-Net (3 backbones)", 94.46, "ens"), ("EfficientNet + ConvNeXt", 93.14, "ens"), ("EfficientNet + DeiT", 92.59, "ens"),
            ("EfficientNet-B0", 90.79, "cnn"), ("ConvNeXt + Wavelet", 89.49, "freq"), ("DeiT-B", 89.32, "tr"), ("ResNet-34 + SE", 88.90, "cnn"),
            ("Xception + Wavelet", 87.76, "freq"), ("MobileViT", 87.04, "tr"), ("Swin-T", 86.52, "tr"), ("Inception-V3", 84.38, "cnn"),
            ("ResNet-34", 80.32, "cnn"), ("ViT-B", 78.12, "tr"), ("MobileNet-V2", 78.12, "cnn"), ("ResNet-34 + DCT", 71.48, "freq"),
            ("ResNet-50", 69.00, "cnn"), ("ResNet-34 + FFT", 66.55, "freq"), ("VGG-19", 62.25, "cnn")]
    st = {"ours": dict(color=RED), "ours_o": dict(facecolor="white", edgecolor=RED, linewidth=0.9), "ours2": dict(color=RED, alpha=0.55),
          "ens": dict(facecolor="white", edgecolor=BLK, hatch="xxxx", linewidth=0.5), "cnn": dict(facecolor="white", edgecolor=BLK, linewidth=0.7),
          "tr": dict(facecolor="white", edgecolor=BLK, hatch="////", linewidth=0.5), "freq": dict(color=BLK)}
    n = len(rows)
    for i, (nm, v, f) in enumerate(rows):
        y = n - i
        ax.barh(y, v, height=0.64, **st[f])
        ax.text(v + 0.5, y, f"{v:.2f}", va="center", fontsize=5.6)
    ax.set_yticks(range(n, 0, -1)); ax.set_yticklabels([r[0] for r in rows], fontsize=5.8)
    ax.set_xlim(50, 102); ax.set_xlabel("accuracy on the SP-Cup validation split (n = 3,072), %", fontsize=FS)
    ax.legend(handles=[Patch(fc="white", ec=BLK, label="spatial CNN"), Patch(fc="white", ec=BLK, hatch="////", label="transformer"),
                       Patch(fc=BLK, ec=BLK, label="frequency input"), Patch(fc="white", ec=BLK, hatch="xxxx", label="ensemble"),
                       Patch(fc=RED, ec=RED, label="OpenCLIP (ours)")], frameon=False, fontsize=5.6, loc="lower right")
    title(fig, "Accuracy against every baseline reported by CAE-Net (Table VII)", y=0.955)
    fig.text(0.02, 0.01, "† threshold tuned on the same split, so optimistic. Baselines as reported in the CAE-Net paper.", fontsize=5.6)
    save(fig, "pc11-comparison")


def pc12_cost():
    W, H = FULL, 2.0
    fig = plt.figure(figsize=(W, H))
    panels = [("parameters (million)", 117.4, 304.0, "{:.1f}"), ("GMACs per image", 24.8, 81.0, "{:.1f}"),
              ("ms per image (different GPUs)", 10.4, 28.1, "{:.1f}"), ("training images", 262160, 85380, "{:,.0f}")]
    for i, (nm, a, b, fmt) in enumerate(panels):
        ax = fig.add_axes([0.06 + i * 0.24, 0.2, 0.17, 0.55]); style(ax)
        ax.bar([0], [a], 0.7, facecolor="white", edgecolor=BLK, linewidth=0.8)
        ax.bar([1], [b], 0.7, color=RED)
        ax.set_xticks([0, 1]); ax.set_xticklabels(["CAE-Net", "ours"], fontsize=5.8)
        ax.set_ylim(0, max(a, b) * 1.25); ax.set_title(nm, fontsize=5.9, pad=3)
        for x, v in ((0, a), (1, b)):
            ax.text(x, v + max(a, b) * 0.03, fmt.format(v), ha="center", fontsize=5.6)
        ax.tick_params(labelsize=5.4)
    title(fig, "The cost side: bigger and slower per image, but one model, one pass, one stage", y=0.93)
    fig.text(0.02, 0.03, "CAE-Net: 3 backbones, 3 passes, 5 stages; latency on a P100.   Ours: 1 backbone, 1 pass, 1 stage; latency on 2× T4.", fontsize=5.7)
    save(fig, "pc12-cost")


def pc13_openforensics():
    W, H = FULL, 2.6
    fig = plt.figure(figsize=(W, H))
    a1 = fig.add_axes([0.08, 0.2, 0.4, 0.58]); style(a1)
    a2 = fig.add_axes([0.58, 0.2, 0.4, 0.58]); style(a2)
    groups = ["best regular", "best SWA", "final SWA"]
    val = [98.43, 98.43, 97.67]; tes = [88.85, 88.85, 94.76]
    x = np.arange(3); w = 0.36
    a1.bar(x - w / 2, val, w, facecolor="white", edgecolor=BLK, linewidth=0.8, label="validation (n = 39,428)")
    a1.bar(x + w / 2, tes, w, color=RED, label="held-out test (n = 10,905)")
    for i in range(3):
        a1.text(x[i] - w / 2, val[i] + 0.3, f"{val[i]:.2f}", ha="center", fontsize=5.6)
        a1.text(x[i] + w / 2, tes[i] + 0.3, f"{tes[i]:.2f}", ha="center", fontsize=5.6, color=RED)
        a1.text(x[i], 100.6, f"gap {tes[i]-val[i]:+.2f}", ha="center", fontsize=5.6)
    a1.set_xticks(x); a1.set_xticklabels(groups, fontsize=5.8); a1.set_ylim(84, 103.5)
    a1.set_ylabel("accuracy (%)", fontsize=FS); a1.legend(frameon=False, fontsize=5.4, loc="lower right")
    fr = [98.67, 98.67, 94.61]; rr = [78.88, 78.88, 94.92]
    a2.bar(x - w / 2, fr, w, facecolor="white", edgecolor=BLK, linewidth=0.8, label="fake recall")
    a2.bar(x + w / 2, rr, w, color=RED, label="real recall (specificity)")
    for i in range(3):
        a2.text(x[i] - w / 2, fr[i] + 0.4, f"{fr[i]:.2f}", ha="center", fontsize=5.6)
        a2.text(x[i] + w / 2, rr[i] + 0.4, f"{rr[i]:.2f}", ha="center", fontsize=5.6, color=RED)
    a2.set_xticks(x); a2.set_xticklabels(groups, fontsize=5.8); a2.set_ylim(70, 104)
    a2.set_ylabel("recall on the test set (%)", fontsize=FS); a2.legend(frameon=False, fontsize=5.4, loc="lower right")
    fig.text(0.02, 0.9, "(a) Validation accuracy vs held-out test", fontsize=FS + 0.3, fontweight="bold")
    fig.text(0.52, 0.9, "(b) Per-class recall on the test set", fontsize=FS + 0.3, fontweight="bold")
    fig.text(0.02, 0.03, "On OpenForensics, best regular and best SWA are the same checkpoint.", fontsize=5.7)
    save(fig, "pc13-openforensics-gap")
