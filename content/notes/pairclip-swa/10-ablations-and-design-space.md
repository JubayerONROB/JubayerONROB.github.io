---
title: "10. Ablations and design space"
date: 2026-11-10
tags:
  - notes
  - deepfake
  - deep-learning
---

`deepfake` `deep-learning` · Part of the [[notes/pairclip-swa/index|PairCLIP-SWA study guide]]

An **ablation** removes or changes one part of a system to see how much it mattered. This page covers two things: the **preprocessing ablations** (Table XI) and the **design-space survey** of 22 configurations (Table XII). All are evaluated on the identical 3,072-image DF-Wild-Cup validation split.

> **Read this first.** Only one block of Table XI (block E) is a **controlled** comparison. In the others, the schedule, epochs or backbone also differ, so they give **honest bounds**, not clean single-factor effects. Never over-read a single difference.

## 10.1 Preprocessing ablations (Table XI)

![Ablation gaps](/attachments/notes/pairclip-swa/pc15-ablation-gaps.png)
*Figure 20. Training accuracy (open) and validation accuracy (filled) for alternative inputs and objectives. The gap is the memorization that a choice fails to turn into validation accuracy. [PDF](/attachments/notes/pairclip-swa/pc15-ablation-gaps.pdf)*

| Variant | Train | Validation | Note |
|---|---|---|---|
| **A. Input representation (P1)** | | | |
| Full released frame (reported run) | 98.48 | **97.04** | reference |
| Face crop (dlib) + OpenCLIP | 84.34 | 56.05 | |
| FFT-domain input | 83.72 | 49.61 | chance level |
| Wavelet-coefficient input, 30 epochs | 91.60 | 73.20 | |
| **B. Class balancing (P6), OpenCLIP ViT-L/14** | | | |
| Similarity-guided 1:1, $k \to 11$, non-averaged | – | 95.67 | reference |
| Random 1:1, $k$: 2 → 5 | – | 93.36 | |
| **C. Augmentation (P5), ViT + LoRA** | | | |
| None, 3 epochs | – | 86.75 | |
| Augmented, 10 epochs: peak / final | – | 91.44 / 87.99 | |
| **D. Training objective** | | | |
| Cross-entropy (reported run) | 98.48 | 97.04 | reference |
| Triplet loss + classifier | 98.70 | 90.85 | |
| **E. Same run, single factor (controlled)** | | | |
| SWA vs non-averaged | – | 97.04 / 95.67 | |
| $\tau^\star$ vs 0.5 (tuned on split) | – | 97.30 / 97.04 | |
| Before adaptation (random head) | – | 45.80 | |

**What each result teaches.**

- **Secondary face cropping is the most damaging choice.** Cropping to a dlib face box gives **56.05%**, about **34 points** below the same model on full frames, even though it fits 84.34% of the training data. The **28-point memorization gap** is the signature of a model that lost transferable evidence and learned something corpus-specific. The band of context around the face, where blending boundaries live, is worth more than the extra resolution a tighter crop gives.
- **Frequency inputs transferred poorly.** A classifier on FFT spectra fits 83.72% of training data and gets **49.61%, chance level**, on validation. Wavelet coefficients reach 73.20%, which is 16 points below the ConvNeXt + wavelet result reported by CAE-Net. That result shows wavelets *can* work with a suitable backbone, but it is still 7.55 points below spatial RGB with CLIP initialization. So we feed spatial RGB and let the pre-trained filters handle spectral sensitivity.
- **Balancing.** Similarity-guided gives 95.67% against 93.36% for random undersampling. But unfreezing depth also differs (11 vs 5 blocks) and Stage 1 had the rescaling bug ([[notes/pairclip-swa/3-balancing-the-data|page 3]]). The 2.31-point gap is **consistent with, but does not establish**, a benefit.
- **Augmentation.** With a LoRA-tuned ViT, augmentation raised the early peak from 86.75 to 91.44%, but the model ended at 87.99% after ten epochs. It kept little of the gain. Together with the forensic argument for P5, this led to flip-only training.
- **Objective.** Triplet metric learning reaches the highest training accuracy of any variant (98.70%) and a validation accuracy **6.19 points below** cross-entropy. A pair-based approach **memorizes** instead of generalizing.

## 10.2 The design-space survey (Table XII, Figure 8a)

![Design space](/attachments/notes/pairclip-swa/pc16-design-space.png)
*Figure 21. Eighteen of the 22 configurations on the identical split. The other four are the preprocessing ablations above. The dashed line is CAE-Net. [PDF](/attachments/notes/pairclip-swa/pc16-design-space.pdf)*

The schedules, epochs and sometimes training data differ between rows, so this is a **survey** of the design space, not a controlled ablation. Four patterns are robust even so.

### Pattern 1: Pre-training dominates

Group by how the model was initialized:

| Initialization | Validation accuracy range |
|---|---|
| ImageNet CNNs | 71.70 – 75.79% |
| Non-CLIP transformers | 80.70 – 93.03% |
| OpenCLIP ViT-B/32 | 90.20 – 93.62% |
| OpenCLIP ViT-L/14 | 93.36 – 97.04% |

Every untrained head starts at **chance** (45.61–53.74%), so the ordering reflects **adaptation, not leakage**. CLIP initialization is worth more than any architecture or schedule change within a family. This is the empirical form of gap G2.

### Pattern 2: Adapting too little or too much both lose

- A near-linear probe on a non-CLIP ViT: **80.70%**.
- Full fine-tuning: **89.58%** after one epoch, falling to **87.60%** after two.
- LoRA adapters sit between.
- Progressive unfreezing of an OpenCLIP tower is the best strategy tried.

(**LoRA** is a method that adds small trainable matrices to a frozen model; see [[notes/proactive-assistant/4-training|the earlier guide]].)

### Pattern 3: Averaging weights beats averaging predictions

Five OpenCLIP ViT-B/32 models trained on **disjoint** data parts average **92.75%** individually. As an **ensemble** they reach **94.95%** (94.66% by **majority vote**) at **five forward passes**. A single ViT-L/14 with SWA reaches **97.04%** in **one pass** (although each pass costs more). Feature-level **fusion** of three different backbones (81.22%) falls below every single-backbone transformer except the near-linear probe.

### Pattern 4: Scale helps, schedule helps more

OpenCLIP ViT-L/14 after 8 epochs (94.11%) is only 0.49 points above the best ViT-B/32 (93.62%). The reported run gains **1.56** more points from a longer schedule and deeper progressive unfreezing, and **1.37** from averaging.

## 10.3 Words used on this page

- **Ablation.** Removing or changing one part to measure its effect.
- **Memorization gap.** The difference between training and validation accuracy.
- **FFT (fast Fourier transform).** Converts an image to its spatial frequencies.
- **DCT.** A related frequency transform used in JPEG.
- **Wavelet.** A transform that mixes position and frequency information.
- **Triplet loss.** A loss that pulls an anchor toward a same-class example and away from a different-class one.
- **Metric learning.** Learning a space where distance reflects class similarity.
- **Majority vote.** The ensemble answer is whatever most members predict.
- **Fusion.** Combining features from several networks before the final decision.
- **Full fine-tuning.** Updating all weights.

## 10.4 Check yourself

- Which preprocessing choice cost the most, and by how many points?
- Why is a bigger train–validation gap a bad sign?
- Why does "weights vs predictions" favour a single model for deployment?

Next: [[notes/pairclip-swa/11-representation-geometry|11. Representation geometry]]
