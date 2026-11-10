from common import *
from fig6 import style
from pairclip_b import title
import numpy as np
from matplotlib.patches import Patch


def pc14_confusion_of():
    W, H = FULL, 3.8
    fig, ax = canvas(W, H)
    label(ax, 0.08, H - 0.12, "OpenForensics confusion matrices (counts, and row percentages = per-class recall)", ha="left", bold=True)
    mats = {("val", 0): ((19451, 99.0), (190, 1.0), (429, 2.2), (19358, 97.8)),
            ("val", 1): ((18802, 95.7), (839, 4.3), (80, 0.4), (19707, 99.6)),
            ("test", 0): ((5419, 98.7), (73, 1.3), (1143, 21.1), (4270, 78.9)),
            ("test", 1): ((5196, 94.6), (296, 5.4), (275, 5.1), (5138, 94.9))}
    ox, oy = 1.25, 0.55
    cw, ch = 1.05, 0.5
    for c, nm in enumerate(["validation-selected checkpoint\n(best regular = best SWA)", "terminal average\n(final SWA)"]):
        label(ax, ox + c * 2.9 + cw, H - 0.55, nm, fs=6.0, bold=True)
    for r, (key, nm) in enumerate([("val", "validation\nn = 39,428\nacc 98.43 / 97.67"), ("test", "held-out test\nn = 10,905\nacc 88.85 / 94.76")]):
        yb = H - 1.0 - r * 1.35 - 0.95
        label(ax, 0.08, yb + ch, nm, ha="left", fs=5.8)
        for c in range(2):
            x = ox + c * 2.9
            (tp, tpp), (fn, fnp), (fp, fpp), (tn, tnp) = mats[(key, c)]
            label(ax, x + cw / 2, yb + 2 * ch + 0.1, "pred. fake", fs=5.5)
            label(ax, x + 1.5 * cw, yb + 2 * ch + 0.1, "pred. real", fs=5.5)
            label(ax, x - 0.05, yb + 1.5 * ch, "fake", ha="right", fs=5.5)
            label(ax, x - 0.05, yb + 0.5 * ch, "real", ha="right", fs=5.5)
            hot = (key == "test" and c == 0)
            box(ax, x, yb + ch, cw, ch, f"{tp:,}\n({tpp}%)", fs=5.7)
            box(ax, x + cw, yb + ch, cw, ch, f"{fn:,}\n({fnp}%)", fs=5.7)
            box(ax, x, yb, cw, ch, f"{fp:,}\n({fpp}%)", fs=5.7, color=RED if hot else BLK, lw=1.2 if hot else 0.6)
            box(ax, x + cw, yb, cw, ch, f"{tn:,}\n({tnp}%)", fs=5.7)
    label(ax, 0.08, 0.2, "Red: 1,143 of the 1,216 test errors (94.0%) are genuine photographs rejected as fake, a 15.7 : 1 asymmetry. After averaging: 275 vs 296 (0.93 : 1).", ha="left", fs=5.8, color=RED)
    save(fig, "pc14-confusion-openforensics")


def pc15_ablation():
    W, H = FULL, 2.7
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0.28, 0.17, 0.68, 0.65]); style(ax)
    rows = [("Full released frame (reported run)", 98.48, 97.04), ("Triplet metric learning", 98.70, 90.85),
            ("Wavelet-coefficient input", 91.60, 73.20), ("Face crop (dlib) + OpenCLIP", 84.34, 56.05), ("FFT-domain input", 83.72, 49.61)]
    n = len(rows)
    for i, (nm, tr, va) in enumerate(rows):
        y = n - i
        ax.plot([va, tr], [y, y], color=BLK, lw=0.8, zorder=1)
        ax.scatter([tr], [y], s=18, facecolor="white", edgecolor=BLK, linewidth=0.8, zorder=3)
        ax.scatter([va], [y], s=18, color=RED if i == 0 else BLK, zorder=3)
        ax.text(max(tr, va) + 1.2, y, f"gap {tr - va:.1f}", fontsize=5.8, va="center")
        ax.text(va, y - 0.34, f"{va:.2f}", fontsize=5.6, ha="center", color=RED if i == 0 else BLK)
    ax.axvline(50, color=BLK, lw=0.5, ls=":")
    ax.text(50.5, n + 0.35, "chance", fontsize=5.6)
    ax.set_yticks(range(n, 0, -1)); ax.set_yticklabels([r[0] for r in rows], fontsize=5.9)
    ax.set_xlim(45, 106); ax.set_ylim(0.3, n + 0.7)
    ax.set_xlabel("accuracy (%)", fontsize=FS)
    ax.legend(handles=[plt.Line2D([], [], marker="o", ls="", mfc="white", mec=BLK, label="training"), plt.Line2D([], [], marker="o", ls="", color=BLK, label="validation")],
              frameon=False, fontsize=5.7, loc="lower right")
    title(fig, "What each preprocessing or objective choice costs: training vs validation accuracy", y=0.94)
    save(fig, "pc15-ablation-gaps")


def pc16_design():
    W, H = FULL, 3.7
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0.31, 0.2, 0.66, 0.72]); style(ax)
    R = [("PairCLIP-SWA (reported run)", 97.04, "ours"), ("PairCLIP, non-averaged", 95.67, "L14"),
         ("OpenCLIP L/14, earlier checkpoint", 95.51, "L14"), ("5 × OpenCLIP B/32 ensemble", 94.95, "ens"),
         ("OpenCLIP L/14, 8 epochs", 94.11, "L14"), ("OpenCLIP B/32, 30 epochs", 93.62, "B32"),
         ("OpenCLIP L/14, random undersample", 93.36, "L14"), ("OpenCLIP B/32, 24 epochs", 93.07, "B32"),
         ("ViT + Swin", 93.03, "nc"), ("ViT + LoRA + augmentation (peak)", 91.44, "nc"), ("OpenCLIP B/32, 20 epochs", 90.20, "B32"),
         ("ViT, full fine-tuning", 89.58, "nc"), ("ViT + LoRA", 86.75, "nc"), ("ViT + OpenCLIP + Xception fusion", 81.22, "ens"),
         ("ViT, near-linear probe", 80.70, "nc"), ("Xception, 5 epochs", 75.79, "cnn"), ("Xception, undersampled", 75.03, "cnn"),
         ("ResNet-50, gradual unfreezing", 71.70, "cnn")]
    st = {"ours": dict(color=RED), "L14": dict(color=CAT_BLUE), "B32": dict(color=CAT_LBLUE), "ens": dict(color=CAT_PURPLE),
          "nc": dict(color=CAT_TEAL), "cnn": dict(color=CAT_TAN)}
    n = len(R)
    for i, (nm, v, f) in enumerate(R):
        y = n - i
        ax.barh(y, v, height=0.64, **st[f]); ax.text(v + 0.5, y, f"{v:.2f}", va="center", fontsize=5.6, bbox=dict(fc="white", ec="none", pad=0.6), zorder=5)
    ax.axvline(94.46, color=BLK, lw=0.7, ls="--")
    ax.text(94.3, 0.1, "CAE-Net 94.46", fontsize=5.6, ha="right", rotation=90, va="bottom")
    ax.set_yticks(range(n, 0, -1)); ax.set_yticklabels([r[0] for r in R], fontsize=5.8)
    ax.set_xlim(60, 102); ax.set_xlabel("SP-Cup validation accuracy (%), identical 3,072-image split", fontsize=FS)
    fig.legend(handles=[Patch(fc=RED, label="PairCLIP-SWA (reported)"), Patch(fc=CAT_BLUE, label="OpenCLIP ViT-L/14"),
                       Patch(fc=CAT_LBLUE, label="OpenCLIP ViT-B/32"), Patch(fc=CAT_TEAL, label="non-CLIP transformer"),
                       Patch(fc=CAT_PURPLE, label="fusion / ensemble"), Patch(fc=CAT_TAN, label="ImageNet CNN")],
              frameon=False, fontsize=5.5, loc="lower center", ncol=3, bbox_to_anchor=(0.6, 0.0))
    title(fig, "18 of the 22 in-house configurations (the other 4 are the preprocessing ablations)", y=0.955)
    save(fig, "pc16-design-space")


def pc17_geometry():
    W, H = FULL, 3.2
    fig = plt.figure(figsize=(W, H))
    labels = ["best\nregular", "best\nSWA", "final\nSWA"]
    S = {"dwc": [2.033, 1.927, 1.917], "of": [2.228, 2.228, 2.257]}
    A = {"dwc": [95.67, 97.04, 97.04], "of": [88.85, 88.85, 94.76]}
    names = {"dwc": "DF-Wild-Cup (validation)", "of": "OpenForensics (held-out test accuracy)"}
    for c, key in enumerate(["dwc", "of"]):
        for r, (data, yl, fmt) in enumerate([(S[key], "separation score $S$", "{:.3f}"), (A[key], "accuracy (%)", "{:.2f}")]):
            ax = fig.add_axes([0.07 + c * 0.5, 0.6 - r * 0.36, 0.39, 0.22]); style(ax)
            ax.bar(range(3), data, 0.55, color=RED if r == 0 else BLK)
            for i, v in enumerate(data):
                ax.text(i, v + (max(data) - min(data)) * 0.03 + (0.01 if r == 0 else 0.15), fmt.format(v), ha="center", fontsize=5.6)
            ax.set_xticks(range(3)); ax.set_xticklabels(labels if r == 1 else [""] * 3, fontsize=5.7)
            lo = min(data); hi = max(data); pad = (hi - lo) * 0.9 + (0.05 if r == 0 else 1.0)
            ax.set_ylim(lo - pad, hi + pad * 0.7)
            ax.set_ylabel(yl, fontsize=5.8)
    fig.text(0.07, 0.94, "DF-Wild-Cup: separation falls while accuracy rises", fontsize=FS + 0.3, fontweight="bold")
    fig.text(0.57, 0.94, "OpenForensics: same separation, 5.9-point accuracy gap", fontsize=FS + 0.3, fontweight="bold")
    fig.text(0.07, 0.015, "Bars start above zero to show small differences. Separation score $S = \\Delta/(\\sigma_f + \\sigma_r)$ is computed in t-SNE space (Table X).", fontsize=5.7)
    save(fig, "pc17-geometry-vs-accuracy")


def pc18_winners():
    W, H = FULL, 2.5
    fig, ax = canvas(W, H)
    label(ax, 0.08, H - 0.12, "Why the best validation score is optimistic (schematic, no data)", ha="left", bold=True)
    # left panel: candidates
    x0 = 0.5
    ytrue = 1.2
    ax.plot([x0 - 0.1, x0 + 2.9], [ytrue, ytrue], color=BLK, lw=0.7, ls="--")
    label(ax, x0 + 1.4, ytrue - 0.28, "true quality (the same for every candidate)", fs=5.7)
    offs = [0.12, -0.18, 0.05, 0.38, -0.08, 0.2, -0.25, 0.1]
    for i, o in enumerate(offs):
        cx = x0 + 0.2 + i * 0.36
        ax.plot([cx, cx], [ytrue, ytrue + o], color=BLK, lw=0.5)
        ax.scatter([cx], [ytrue + o], s=14, facecolor="white", edgecolor=BLK, linewidth=0.7, zorder=3)
    # highlight max
    mi = int(np.argmax(offs)); cx = x0 + 0.2 + mi * 0.36
    ax.scatter([cx], [ytrue + offs[mi]], s=18, color=RED, zorder=4)
    label(ax, cx, ytrue + offs[mi] + 0.25, "highest validation score:\nselected", fs=5.7, color=RED)
    label(ax, x0 + 1.4, 0.55, "8 candidates: each validation score = true quality + luck (±)", fs=5.8)
    # arrow to right panel
    arrow(ax, (3.6, 1.35), (4.1, 1.35), color=RED)
    label(ax, 3.85, 1.55, "new\ndata", fs=5.6)
    # right: test
    rx = 4.25
    ax.plot([rx - 0.1, rx + 1.7], [ytrue, ytrue], color=BLK, lw=0.7, ls="--")
    ax.scatter([rx + 0.5], [ytrue - 0.12], s=18, color=RED, zorder=4)
    ax.plot([rx + 0.5, rx + 0.5], [ytrue + offs[mi], ytrue - 0.12], color=RED, lw=0.5, ls=":")
    label(ax, rx + 0.5, ytrue - 0.4, "the same model on\nheld-out data: the luck\nis gone", fs=5.7, color=RED)
    label(ax, rx + 1.6, ytrue + 0.45, "taking the maximum of noisy scores\noverstates the true quality", ha="right", fs=5.7)
    label(ax, 0.08, 0.2, "The more variable the candidates, the bigger the overstatement. Averaging the weights reduces the variance of the thing you deploy.", ha="left", fs=5.8)
    save(fig, "pc18-selection-bias")
