from common import *
from fig6 import style
import numpy as np
from matplotlib.patches import Patch


def T(ax, text):
    label(ax, 0.08, ax.get_ylim()[1] - 0.12, text, ha="left", bold=True)


# ---------- pc0: what a detector does ----------
def pc0_task():
    W, H = FULL, 2.1
    fig, ax = canvas(W, H)
    T(ax, "A deepfake detector gives one score per image, then a threshold decides")
    y = 1.0
    box(ax, 0.08, y, 0.95, 0.6, "image $x$\n(real or fake?)", fs=6.0)
    arrow(ax, (1.03, y + 0.3), (1.3, y + 0.3))
    box(ax, 1.3, y, 1.2, 0.6, "detector $f_\\theta$\n(a neural network)", fs=6.0)
    arrow(ax, (2.5, y + 0.3), (2.8, y + 0.3))
    box(ax, 2.8, y, 1.15, 0.6, "score\n$p(\\mathrm{fake}\\mid x) \\in [0,1]$", fs=5.9)
    arrow(ax, (3.95, y + 0.3), (4.25, y + 0.3))
    box(ax, 4.25, y, 0.85, 0.6, "threshold\n$\\tau = 0.5$ ?", fs=6.0, color=RED)
    arrow(ax, (5.1, y + 0.42), (5.45, y + 0.6), color=RED)
    arrow(ax, (5.1, y + 0.18), (5.45, y + 0.0))
    box(ax, 5.45, y + 0.45, 1.3, 0.3, "$p \\geq \\tau$: fake", fs=6.0, color=RED)
    box(ax, 5.45, y - 0.15, 1.3, 0.3, "$p < \\tau$: real", fs=6.0)
    label(ax, 0.08, 0.5, "Training: show many labelled images and adjust $\\theta$.   Generalization: the test images come from generators, cameras or compression that training never showed.", ha="left", fs=5.9)
    label(ax, 0.08, 0.28, "A detector that is nearly perfect inside one family of fakes can fail badly outside it.", ha="left", fs=5.9)
    save(fig, "pc0-task")


# ---------- pc1: data splits ----------
def pc1_splits():
    W, H = FULL, 2.55
    fig, ax = canvas(W, H)
    T(ax, "The four data splits and what each one is used for")
    rows = [("SP-Cup train", 42690, 219470, "source of the Stage-1 subsample", False),
            ("SP-Cup validation", 1548, 1524, "selection and evaluation", False),
            ("OpenForensics validation", 19787, 19641, "selection", False),
            ("OpenForensics test", 5413, 5492, "held-out: never used for training or selection", True)]
    x0, bw = 1.55, 3.3
    label(ax, x0, 2.2, "real", fs=6.0)
    label(ax, x0 + bw, 2.2, "fake", fs=6.0)
    for i, (nm, r, f, role, held) in enumerate(rows):
        y = 1.65 - i * 0.4
        tot = r + f
        label(ax, x0 - 0.08, y + 0.14, nm, ha="right", fs=6.1, color=RED if held else BLK, bold=held)
        ax.add_patch(Rectangle((x0, y), bw * r / tot, 0.28, fc="white", ec=RED if held else BLK, lw=0.8, zorder=2))
        ax.add_patch(Rectangle((x0 + bw * r / tot, y), bw * f / tot, 0.28, fc=RED if held else BLK, ec=RED if held else BLK, lw=0.8, zorder=2))
        if r / tot > 0.2:
            label(ax, x0 + bw * r / tot / 2, y + 0.14, f"{r:,}", fs=5.8)
        else:
            label(ax, x0 + bw * r / tot / 2, y + 0.4, f"{r:,}", fs=5.6)
        label(ax, x0 + bw * r / tot + bw * f / tot / 2, y + 0.14, f"{f:,}", fs=5.8, color="white")
        label(ax, x0 + bw + 0.1, y + 0.14, role, ha="left", fs=5.8, color=RED if held else BLK)
    label(ax, 0.08, 0.15, "Bars show each split's real/fake share. SP-Cup train is about 5:1 fake-to-real; the Stage-1 subsample makes it 1:1 (85,380 images).", ha="left", fs=5.8)
    save(fig, "pc1-data-splits")


# ---------- pc2: ViT ----------
def pc2_vit():
    W, H = FULL, 2.5
    fig, ax = canvas(W, H)
    T(ax, "From an image to a score: OpenCLIP ViT-L/14 visual tower and linear head")
    y0 = 1.0
    # image with grid
    ax.add_patch(Rectangle((0.1, y0), 0.9, 0.9, fc="white", ec=BLK, lw=0.7, zorder=2))
    for i in range(1, 4):
        line(ax, (0.1 + i * 0.225, y0), (0.1 + i * 0.225, y0 + 0.9), lw=0.35)
        line(ax, (0.1, y0 + i * 0.225), (1.0, y0 + i * 0.225), lw=0.35)
    label(ax, 0.55, y0 - 0.2, "image 224 × 224", fs=5.8)
    label(ax, 0.55, y0 - 0.38, "(grid drawn 4×4;\nreal grid 16×16)", fs=5.4)
    arrow(ax, (1.05, y0 + 0.45), (1.35, y0 + 0.45))
    # tokens
    names = ["CLS", "$p_1$", "$p_2$", "$p_3$", "…", "$p_{256}$"]
    for i, n in enumerate(names):
        box(ax, 1.4, y0 + 0.9 - 0.15 - i * 0.16, 0.5, 0.14, n, fs=5.2, color=RED if n == "CLS" else BLK)
    label(ax, 1.65, y0 - 0.3, "257 tokens: 256 patches\n(14×14 px each) + class\ntoken, each of width 1024", fs=5.4)
    arrow(ax, (1.95, y0 + 0.45), (2.25, y0 + 0.45))
    # blocks
    for i in range(12):
        block3d(ax, 2.3 + i * 0.15, y0 + 0.25, 0.1, 0.4, 0.05, BLK)
    label(ax, 2.3 + 6 * 0.15, y0 + 0.85, "24 transformer blocks (12 drawn)", fs=5.8)
    label(ax, 2.3 + 6 * 0.15, y0 - 0.1, "each: attention (16 heads) + MLP", fs=5.4)
    arrow(ax, (4.2, y0 + 0.45), (4.45, y0 + 0.45), color=RED)
    box(ax, 4.45, y0 + 0.15, 0.85, 0.6, "class token\n→ $W_{proj}$\n1024 → 768", fs=5.5, color=RED)
    arrow(ax, (5.3, y0 + 0.45), (5.5, y0 + 0.45), color=RED)
    box(ax, 5.5, y0 + 0.15, 1.2, 0.6, "$g(x) \\in \\mathbb{R}^{768}$\nlinear head 768 → 2\nsoftmax", fs=5.5, color=RED)
    label(ax, 3.4, 0.4, "Parameters: 303,967,746 in total. 99.45% sit in the 24 blocks; the linear head has only 1,538.", fs=5.9)
    save(fig, "pc2-vit")


# ---------- pc3: CLIP ----------
def pc3_clip():
    W, H = FULL, 2.3
    fig, ax = canvas(W, H)
    T(ax, "CLIP learns by matching images with their captions; we keep only the image tower")
    box(ax, 0.1, 1.2, 0.8, 0.4, "image", fs=6.0)
    arrow(ax, (0.9, 1.4), (1.1, 1.4))
    box(ax, 1.1, 1.2, 1.1, 0.4, "image tower", fs=6.0, color=RED)
    arrow(ax, (2.2, 1.4), (2.5, 1.4), color=RED)
    label(ax, 2.9, 1.4, "image vectors\n$u_1 \\ldots u_N$", fs=5.8)
    box(ax, 0.1, 0.4, 0.8, 0.4, "caption", fs=6.0)
    arrow(ax, (0.9, 0.6), (1.1, 0.6))
    box(ax, 1.1, 0.4, 1.1, 0.4, "text tower", fs=6.0, ls=(0, (3, 2)))
    arrow(ax, (2.2, 0.6), (2.5, 0.6))
    label(ax, 2.9, 0.6, "text vectors\n$v_1 \\ldots v_N$", fs=5.8)
    label(ax, 1.65, 0.2, "discarded in our detector", fs=5.6)
    # similarity matrix
    mx, my, c = 4.3, 0.55, 0.42
    for i in range(3):
        for j in range(3):
            on = i == j
            ax.add_patch(Rectangle((mx + j * c, my + (2 - i) * c), c, c, fc=RED if on else "white", ec=BLK, lw=0.5, zorder=2))
            label(ax, mx + j * c + c / 2, my + (2 - i) * c + c / 2, f"$u_{i+1}\\!\\cdot\\! v_{j+1}$", fs=5.2, color="white" if on else BLK)
    label(ax, mx + 1.5 * c, my + 3 * c + 0.15, "similarity of every image with every caption", fs=5.8)
    label(ax, mx + 3 * c + 0.1, my + 1.5 * c, "training pulls\nmatching pairs\n(red diagonal)\ntogether and\npushes others\napart", ha="left", fs=5.6)
    arrow(ax, (3.45, 1.2), (4.2, 1.2), lw=0.4)
    label(ax, 6.0, 0.3, "Layout is schematic.", fs=5.4, ha="center")
    save(fig, "pc3-clip")


# ---------- pc4: stage 1 ----------
def pc4_stage1():
    W, H = FULL, 2.75
    fig, ax = canvas(W, H)
    T(ax, "Stage 1: build a balanced training set by CLIP-similarity-guided subsampling")
    y = 1.65
    box(ax, 0.08, y + 0.3, 0.95, 0.45, "real pool $\\mathcal{R}$\n$n_r = 42{,}690$", fs=5.9)
    box(ax, 0.08, y - 0.35, 0.95, 0.45, "fake pool $\\mathcal{F}$\n$n_f = 219{,}470$", fs=5.9)
    arrow(ax, (1.03, y + 0.52), (1.3, y + 0.25)); arrow(ax, (1.03, y - 0.12), (1.3, y + 0.15))
    box(ax, 1.3, y - 0.05, 1.05, 0.5, "frozen CLIP ViT-L/14\n$\\phi(\\cdot) \\in \\mathbb{R}^{768}$", fs=5.7)
    arrow(ax, (2.35, y + 0.2), (2.6, y + 0.2))
    box(ax, 2.6, y - 0.1, 1.45, 0.6, "cosine similarity\n$S = \\hat U \\hat V^{\\top}$\n$42{,}690 \\times 219{,}470$ values", fs=5.6)
    arrow(ax, (4.05, y + 0.2), (4.3, y + 0.2))
    box(ax, 4.3, y - 0.05, 1.05, 0.5, "greedy one-to-one\nno reuse", fs=5.7, color=RED)
    arrow(ax, (5.35, y + 0.2), (5.6, y + 0.2), color=RED)
    box(ax, 5.6, y - 0.05, 1.15, 0.5, "$\\mathcal{D}_{pair}$\n85,380 images, 1:1", fs=5.7, color=RED)
    # bar
    by = 0.62
    x0, ww = 0.08, W - 0.16
    tot = 219470; kept = 42690
    label(ax, x0, by + 0.42, "What happens to the 219,470 fakes", ha="left", fs=6.0)
    ax.add_patch(Rectangle((x0, by), ww * kept / tot, 0.2, fc=RED, ec=RED, lw=0.7, zorder=2))
    ax.add_patch(Rectangle((x0 + ww * kept / tot, by), ww * (tot - kept) / tot, 0.2, fc="white", ec=BLK, lw=0.7, zorder=2))
    label(ax, x0 + ww * kept / tot / 2, by - 0.14, "kept: 42,690 (19.5%)", fs=5.8, color=RED)
    label(ax, x0 + ww * kept / tot + ww * (tot - kept) / tot / 2, by + 0.1, "discarded: 176,780", fs=5.9)
    label(ax, x0, 0.12, "The subsample uses 32.6% of the 262,160 training images. Most generator diversity in the fake pool never reaches the detector.", ha="left", fs=5.8)
    save(fig, "pc4-stage1")


# ---------- pc5: greedy toy ----------
def pc5_greedy():
    W, H = FULL, 2.55
    fig, ax = canvas(W, H)
    T(ax, "The greedy one-to-one rule on a toy example (made-up numbers)")
    S = [[0.2, 0.9, 0.4, 0.1], [0.3, 0.8, 0.7, 0.2], [0.6, 0.5, 0.9, 0.3]]
    steps = [(0, 1, []), (1, 2, [1]), (2, 0, [1, 2])]
    cw, ch = 0.4, 0.3
    for s, (row, col, used) in enumerate(steps):
        x0 = 0.35 + s * 2.25
        y0 = 0.75
        label(ax, x0 + 2 * cw, y0 + 3 * ch + 0.62, f"step {s+1}: real $r_{row+1}$ picks", fs=6.0, bold=True)
        for j in range(4):
            label(ax, x0 + j * cw + cw / 2, y0 + 3 * ch + 0.15, f"$f_{j+1}$" + ("\n×" if j in used else ""), fs=5.6)
        for i in range(3):
            label(ax, x0 - 0.1, y0 + (2 - i) * ch + ch / 2, f"$r_{i+1}$", fs=5.6, ha="right")
            for j in range(4):
                done = any((i == r and j == c) for r, c, _ in steps[:s])
                now = (i == row and j == col)
                ax.add_patch(Rectangle((x0 + j * cw, y0 + (2 - i) * ch), cw, ch,
                                       fc=RED if now else "white", ec=RED if (done or now) else BLK, lw=1.0 if (done or now) else 0.5, zorder=2))
                label(ax, x0 + j * cw + cw / 2, y0 + (2 - i) * ch + ch / 2, f"{S[i][j]:.1f}", fs=5.6, color="white" if now else BLK)
        note = {0: "$r_1$: best is $f_2$ (0.9).",
                1: "$r_2$: best is $f_2$, but it is used (×).\nTake the next best, $f_3$ (0.7).",
                2: "$r_3$: $f_3$ and $f_2$ are used (×).\nTake the best left, $f_1$ (0.6)."}[s]
        label(ax, x0 + 2 * cw, 0.4, note, fs=5.6)
    label(ax, 0.08, 0.1, "Rows are real images, columns are fakes, cells are cosine similarities. Each fake is used at most once.", ha="left", fs=5.8)
    save(fig, "pc5-greedy-toy")


# ---------- pc6: preprocessing ----------
def pc6_preprocess():
    W, H = FULL, 2.15
    fig, ax = canvas(W, H)
    T(ax, "Preprocessing: keep the evidence, change as little as possible")
    y = 1.2
    items = [("P1", "image as released\nno face crop"), ("P2", "3-channel RGB"), ("P3", "resize to 224×224\nbilinear, no crop"),
             ("P5", "horizontal flip\np = 0.5, train only"), ("P4", "normalize with\nCLIP mean, std"), ("", "network")]
    w, g = 0.98, 0.12
    for i, (p, t) in enumerate(items):
        x = 0.08 + i * (w + g)
        box(ax, x, y, w, 0.6, t, fs=5.6, color=RED if i == 5 else BLK)
        if p:
            label(ax, x + w / 2, y + 0.75, p, fs=6.0, bold=True)
        if i < 5:
            arrow(ax, (x + w, y + 0.3), (x + w + g, y + 0.3))
    box(ax, 0.08, 0.3, 2.15, 0.5, "P7: class-exact batches of 32\n16 real + 16 fake, interleaved", fs=5.7)
    box(ax, 2.4, 0.3, 2.15, 0.5, "P8: evaluation = resize + normalize\nno flip, no test-time augmentation", fs=5.7)
    box(ax, 4.72, 0.3, 2.05, 0.5, "not used: secondary face crop\n(56.05% vs 97.04% validation)", fs=5.6, ls=(0, (3, 2)))
    label(ax, 0.08, 0.1, "Colour jitter, blur, JPEG and random crops are left out because they alter or remove the traces of manipulation.", ha="left", fs=5.8)
    save(fig, "pc6-preprocessing")


# ---------- pc7: unfreezing ----------
def pc7_unfreeze():
    W, H = FULL, 3.95
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
    label(ax, 0.08, H - 0.12, "Progressive unfreezing: the trainable suffix grows, the prefix stays frozen", ha="left", bold=True)
    rows = [("epoch 0:  $k=2$ blocks", "8.29% trainable", 2, False),
            ("epochs 12–13:  $k=8$", "33.15% trainable", 8, False),
            ("epochs 18–19:  $k=11$ (reported run)", "45.58% trainable", 11, False),
            ("design cap:  $k=14$ (not reached)", "58.02% trainable", 14, True)]
    for i, (a, b, k, dashed) in enumerate(rows):
        y = H - 0.8 - i * 0.42
        label(ax, 0.08, y + 0.12, a, ha="left", fs=5.9)
        label(ax, 0.08, y - 0.04, b, ha="left", fs=5.5)
        for j in range(24):
            tr = j >= 24 - k
            block3d(ax, 2.35 + j * 0.18, y - 0.02, 0.12, 0.26, 0.04, RED if tr else BLK)
        if dashed:
            ax.add_patch(Rectangle((2.3, y - 0.07), 24 * 0.18 + 0.1, 0.4, fill=False, ec=BLK, lw=0.5, ls=(0, (3, 2))))
    label(ax, 3.4, H - 0.32, "24 transformer blocks. Black = frozen, red = trainable. Patch embedding, positional embedding\nand $W_{proj}$ stay frozen; the linear head is always trained.", fs=5.5)
    a2 = fig.add_axes([0.3, 0.1, 0.45, 0.27]); style(a2)
    e = np.arange(0, 20)
    k = np.minimum(2 + e // 2, 14)
    a2.step(e, k, where="post", color=RED, lw=1.1)
    a2.axhline(14, color=BLK, lw=0.6, ls="--")
    a2.text(0.3, 14.4, "design cap $K_{max}=14$", fontsize=5.8)
    a2.text(19.3, 12.0, "reported run ended at $k=11$", fontsize=5.8, ha="right")
    a2.set_xticks(range(0, 20, 2))
    a2.set_xlabel("epoch $e$", fontsize=FS); a2.set_ylabel("blocks trainable $k(e)$", fontsize=FS)
    a2.set_ylim(0, 16); a2.set_xlim(0, 19.5)
    fig.text(0.78, 0.22, "$k(e) = \\min(2 + \\lfloor e/2 \\rfloor,\\ 14)$", fontsize=7)
    save(fig, "pc7-unfreezing")


# ---------- pc8: SWA concept ----------
def pc8_swa():
    W, H = FULL, 2.6
    fig, ax = canvas(W, H)
    T(ax, "Stochastic weight averaging: keep a running mean of the weights")
    y = 1.65
    names = ["$\\theta_{12}$", "$\\theta_{13}$", "$\\theta_{14}$", "$\\theta_{15}$", "$\\theta_{16}$", "$\\theta_{17}$", "$\\theta_{18}$", "$\\theta_{19}$"]
    for i, n in enumerate(names):
        cx = 0.5 + i * 0.58
        ax.add_patch(plt.Circle((cx, y), 0.19, fc="white", ec=BLK, lw=0.6, zorder=2))
        label(ax, cx, y, n, fs=5.5)
        label(ax, cx, y - 0.32, f"epoch {12 + i}", fs=5.2)
    label(ax, 2.4, y + 0.38, "weights at the end of each epoch (the first update copies; the average mixes epochs 13–19)", fs=5.6)
    arrow(ax, (5.3, y), (5.55, y), color=RED)
    box(ax, 5.55, y - 0.3, 1.2, 0.6, "$\\theta_{SWA}$\nrunning mean", fs=5.8, color=RED)
    label(ax, 3.4, 0.95, "$\\theta_{SWA}^{(t)} = \\theta_{SWA}^{(t-1)} + \\dfrac{\\theta_t - \\theta_{SWA}^{(t-1)}}{n_t + 1}$", fs=7.5)
    label(ax, 3.4, 0.55, "three deployable models are kept: best regular (a single epoch's weights), best SWA (average at its best validation epoch), final SWA (average of all)", fs=5.5)
    label(ax, 3.4, 0.28, "the learning rate is lowered to $10^{-5}$ with a ten-epoch cosine schedule while averaging", fs=5.5)
    save(fig, "pc8-swa-concept")
