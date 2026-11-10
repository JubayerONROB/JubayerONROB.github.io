---
title: "4. Preprocessing"
date: 2026-11-10
tags:
  - notes
  - deepfake
  - data
---

`deepfake` `data` · Part of the [[notes/pairclip-swa/index|PairCLIP-SWA study guide]]

**Preprocessing** is everything that happens to a stored image before the network sees it. In forensics this is not a minor detail. A step that looks harmless can remove the evidence the detector needs. The paper lists **every** step, with a reason and the evidence for it.

![Preprocessing pipeline](/attachments/notes/pairclip-swa/pc6-preprocessing.png)
*Figure 8. The pipeline from stored file to network input. [PDF](/attachments/notes/pairclip-swa/pc6-preprocessing.pdf)*

## 4.1 The math in three lines

Let $R$ be an anisotropic bilinear resize to 224 × 224. Let $F_b$ be a horizontal flip applied when $b = 1$. Let $N$ be per-channel standardization:

$$
N(v)_c = \frac{v_c/255 - \mu_c}{\sigma_c}, \qquad c \in \{R, G, B\} \tag{1}
$$

with the **CLIP statistics** $\mu = (0.4815,\ 0.4578,\ 0.4082)$ and $\sigma = (0.2686,\ 0.2613,\ 0.2758)$. Then

$$
T_{tr}(x) = N\!\left(F_b(R(x))\right),\quad b \sim \text{Bern}(0.5) \tag{2}
$$

$$
T_{ev}(x) = N\!\left(R(x)\right) \tag{3}
$$

$T_{tr}$ is for training and $T_{ev}$ for evaluation. "Bern(0.5)" means a fair coin: flip half the time.

## 4.2 The eight steps (Table I of the paper)

| Step | Setting | Why | Evidence |
|---|---|---|---|
| **P1** Input region | Image as released. No second face detection or crop | Blending boundaries and face-context mismatches are among the most generator-agnostic cues. A tight crop removes them. The images are already aligned by DeepfakeBench, so a second pass adds variation and fails silently on profile or occluded faces | dlib crop: **56.05%** validation, about **34 points** below the full frame |
| **P2** Decoding | 3-channel RGB (greyscale and alpha converted) | Matches CLIP's input format. Greyscale images exist in the wild | design |
| **P3** Resampling | Bilinear resize to 224 × 224, **no crop** | Matches the pre-training patch grid (16 × 16 patches of 14 px), so positional embeddings need no interpolation. Resizing keeps the edges. The stretch is the same for both classes, so it cannot become a label cue | design |
| **P4** Normalization | Equation (1) with CLIP $\mu, \sigma$ | The frozen patch embedding cannot adapt to another input scale. ImageNet statistics would shift what the frozen part sees | a double rescale compresses inputs 255× (see below) |
| **P5** Augmentation | Horizontal flip only, $p = 0.5$, training only | A flip keeps the label and leaves pixel statistics untouched. Colour jitter, blur, JPEG and random crops alter the very evidence of manipulation | ViT + LoRA: augmentation raises the early peak but the gain is not kept |
| **P6** Class balancing | One-to-one CLIP-similarity subsample, no replacement | One balanced corpus in one stage ([[notes/pairclip-swa/3-balancing-the-data\|page 3]]) | random undersampling: 93.36% |
| **P7** Batches | Interleaved, class-exact, batch 32 | Removes label variance between batches: under random batching the real fraction has a standard deviation of **8.8 points** | design |
| **P8** Evaluation | $T_{ev}$ only. No flip, no test-time augmentation | Predictions are deterministic, so checkpoint comparisons reflect only the weights | design |

"design" means the choice is motivated by argument only, not by an ablation.

## 4.3 The choices that go against common practice

**P1 and P3: do not crop.** Whatever crop happens upstream, we do not crop again. The best evidence of a forgery lives at the **boundary** between the changed region and its surroundings. A second crop cuts it away.

**P5: be minimal.** In forensics, photo-style augmentation is **not neutral**. Blur, noise and compression are themselves "forgery-like" changes. If a detector never sees degraded **real** images, it can learn that "degraded means fake". This is exactly what the OpenForensics error analysis hints at ([[notes/pairclip-swa/8-results|page 8]]). The suggested remedy is **class-symmetric corruption**: apply the same noise, blur and compression to both classes so degradation carries no label. The paper has not tested it yet.

**P4: the double rescale.** If values are divided by 255 twice, the normalized inputs span only $[-1.792, -1.466]$. The tower sees almost-black images. This bug affected **Stage 1** (the similarity search), not the training of the detector itself.

## 4.4 Why 224 × 224 and why normalize

- **224.** ViT-L/14 was pre-trained on a 16 × 16 grid of 14-pixel patches ($16 \times 14 = 224$). Keeping that grid means the learned positional embeddings fit without being stretched.
- **Normalization (standardization).** Subtracting the mean and dividing by the standard deviation gives inputs a similar scale to what the model saw in pre-training. The frozen early layers expect that scale.

## 4.5 P7: class-exact batches

Each epoch draws independent random orderings $\sigma_r$ and $\sigma_f$ of the real and fake indices. It **interleaves** them:

$$
L = (\sigma_r(1),\ \sigma_f(1),\ \sigma_r(2),\ \sigma_f(2),\ \ldots)
$$

cuts $L$ to a multiple of 32, and splits it into batches. Every batch holds **exactly 16 real and 16 fake** images. Because the order is interleaved, each of the two halves that `nn.DataParallel` sends to the two GPUs is also exactly balanced. Layer normalization is per-sample, so splitting the batch over GPUs does not change the result.

## 4.6 Words used on this page

- **Normalization / standardization.** Shifting and scaling values to a standard range.
- **Bilinear interpolation.** A smooth way to resize an image by averaging nearby pixels.
- **Augmentation.** Randomly changing training images to add variety.
- **Anisotropic resize.** Stretching width and height by different factors to reach a target size.
- **Blending boundary.** The seam where a forged face region meets the original image.
- **DataParallel.** Splitting each batch over several GPUs.
- **Class-exact.** Every batch has the same number of examples per class.
- **Class-symmetric.** Applying a change equally to both classes.

## 4.7 Check yourself

- Which three steps keep the image as it was released?
- Why is photo-style augmentation risky in forensics?
- Why does the interleaved sampler give each GPU a balanced half-batch?

Next: [[notes/pairclip-swa/5-training-and-unfreezing|5. Training and progressive unfreezing]]
