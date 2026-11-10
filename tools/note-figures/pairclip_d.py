"""Close-up figure built from tiles of Figure 6 of the PairCLIP-SWA paper."""
from common import *
from PIL import Image
import numpy as np

SRC = "content/attachments/notes/pairclip-swa/paper-figure6-test-images.png"
# tile boxes (x0, y0, x1, y1) in the cropped Figure 6 image (1710 x 1340 px)
TILES = {
    "noise_sel": (1020, 95, 1290, 365),     # best regular, noisy crowd scene (error)
    "magenta_sel": (700, 395, 970, 665),    # best regular, magenta portrait (error)
    "noise_avg": (380, 738, 650, 1008),     # final SWA, noisy crowd scene
    "magenta_avg": (380, 1037, 650, 1307),  # final SWA, magenta portrait
}

def pc19_degraded():
    im = Image.open(SRC).convert("RGB")
    W, H = FULL, 4.6
    fig, ax = canvas(W, H)
    label(ax, 0.08, H - 0.12, "The two genuine photographs that the validation-selected checkpoint rejects", ha="left", bold=True)
    s = 1.55
    xs = [2.0, 4.55]
    rows = [("validation-selected\ncheckpoint", 2.7, True, [("noise_sel", "genuine, heavy noise\npredicted FAKE (0.90)"), ("magenta_sel", "genuine, magenta colour cast\npredicted FAKE (0.99)")]),
            ("terminal average\n(final SWA)", 0.55, False, [("noise_avg", "same photo\npredicted REAL (0.93)"), ("magenta_avg", "same photo\npredicted REAL (0.62), low confidence")])]
    for name, y, err, tiles in rows:
        label(ax, 0.08, y + s / 2, name, ha="left", fs=6.2, bold=True, color=RED if err else BLK)
        for x, (key, cap) in zip(xs, tiles):
            t = np.asarray(im.crop(TILES[key]))[8:-8, 8:-8]
            ax.imshow(t, extent=(x, x + s, y, y + s), zorder=1, interpolation="lanczos", aspect="auto")
            ax.add_patch(Rectangle((x, y), s, s, fill=False, ec=RED if err else BLK, lw=1.4 if err else 0.7, zorder=3))
            label(ax, x + s / 2, y - 0.22, cap, fs=5.9, color=RED if err else BLK)
    ax.set_xlim(0, W); ax.set_ylim(0, H)
    label(ax, W - 0.08, 0.1, "tiles cropped from Figure 6 of the paper (OpenForensics test images)", ha="right", fs=5.4)
    save(fig, "pc19-degraded-genuine-photos")

if __name__ == "__main__":
    pc19_degraded()
