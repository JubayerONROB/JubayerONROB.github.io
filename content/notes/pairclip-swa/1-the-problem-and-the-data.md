---
title: "1. The problem and the data"
date: 2026-11-10
tags:
  - notes
  - deepfake
  - computer-vision
---

`deepfake` · Part of the [[notes/pairclip-swa/index|PairCLIP-SWA study guide]]

## 1.1 What is a deepfake?

A **deepfake** is an image or video that looks real but was made or changed by a neural network. Two families of generators matter here:

- **GANs (generative adversarial networks).** Two networks play a game. A *generator* makes fake images. A *discriminator* tries to tell fake from real. Both improve until the fakes look real.
- **Diffusion models (latent diffusion).** A network learns to remove noise step by step. Starting from pure noise, it paints a picture.

Both can now make photorealistic faces. This causes real harm: fraud, non-consensual images and disinformation. So **detection** is a safety problem.

## 1.2 What a detector does

A detector is a classifier. It takes an image $x$ and gives a score for "fake". A threshold $\tau$ turns the score into a decision.

![What a detector does](/attachments/notes/pairclip-swa/pc0-task.png)
*Figure 2. A detector gives one score per image. A threshold turns it into "fake" or "real". [PDF](/attachments/notes/pairclip-swa/pc0-task.pdf)*

**Notation.** Let $y \in \{0,1\}$ be the label. In the code, $y = 1$ means real and $y = 0$ means fake. But **all precision, recall and F1 values in the paper use the fake class as positive**, to match the earlier work (CAE-Net). Keep this in mind when you read the metrics page.

A training corpus has a **real pool** $\mathcal{R}$ with $n_r$ images and a **fake pool** $\mathcal{F}$ with $n_f$ images. Training produces a path of parameters $\theta_0, \theta_1, \ldots$. A **selection rule** picks one point on that path as the deployed classifier $f_\theta$. The paper studies **both** the classifier and the rule.

## 1.3 The central difficulty: generalization

A detector can be almost perfect on the generators it was trained on. It can then fail when something changes:

- a **new generator**,
- a different **compression** pipeline (for example JPEG),
- different **cameras** or lighting.

This is **generalization** (or **domain shift**). Testing on the *same distribution* as training is called **in-domain**. The paper's main numbers are in-domain. The OpenForensics test checks a second, independent sample.

## 1.4 The datasets

**SP Cup 2025 (DF-Wild-Cup).** The IEEE Signal Processing Cup 2025 corpus was built to stress generalization. It merges **eight public benchmarks** under the DeepfakeBench protocol: Celeb-DF v1 and v2, FaceForensics++, DeepfakeDetection, FaceShifter, UADFV, and the DFDC preview and full releases. It removes provenance metadata (so a detector cannot cheat by reading file information). It has a **5:1 fake-to-real imbalance**.

- Training partition: **42,690 real** and **219,470 fake** images.
- Official validation partition: **1,548 real** and **1,524 fake** images (**3,072** in all).

**OpenForensics-derived benchmark.** A public in-the-wild face corpus with fixed partitions. A second, independent run of the same backbone, schedule and averaging is trained on its training partition. It is selected on its validation partition (39,428 images: 19,787 real, 19,641 fake) and evaluated **once** on its test partition (10,905 images: 5,413 real, 5,492 fake).

![The four data splits](/attachments/notes/pairclip-swa/pc1-data-splits.png)
*Figure 3. Real/fake share in each split and what each split is used for. [PDF](/attachments/notes/pairclip-swa/pc1-data-splits.pdf)*

| Corpus | Split | Images | Real / Fake | Role |
|---|---|---|---|---|
| DF-Wild-Cup | train (Stage-1 subsample of 262,160) | 85,380 | 1:1 | training |
| DF-Wild-Cup | validation | 3,072 | 1,548 / 1,524 | selection and evaluation |
| OpenForensics | validation | 39,428 | 19,787 / 19,641 | selection |
| OpenForensics | test | 10,905 | 5,413 / 5,492 | **held-out test** |

**Only the OpenForensics test partition is untouched by both training and selection.** Everything else was used to train, tune or choose. This matters a lot in [[notes/pairclip-swa/9-selection-and-validation-bias|page 9]].

## 1.5 The strongest published baseline: CAE-Net

CAE-Net fuses three different backbones: **EfficientNet-B0** (a small CNN), **DeiT** (a vision transformer) and a **wavelet-fed ConvNeXt**. It handles the 5:1 imbalance by splitting the 219,470 fakes into **five disjoint subsets** and training in five stages, each with all 42,690 reals. It reaches **94.46%** accuracy on the DF-Wild-Cup validation images. It is trained on the training partition and evaluated on the same 3,072 images. Its fusion weights are tuned on them, so the comparison is **in-domain and like-for-like**.

## 1.6 Three research gaps

The paper names three gaps in how deepfake detectors are built and reported.

- **G1: Checkpoint selection is treated as free.** Detectors are reported as the best checkpoint on a validation split, often the same split used to tune thresholds. Selecting from many candidates on a finite validation set gives an **optimistic bias**. Nobody had measured how unstable the selected checkpoint is in deepfake work.
- **G2: Narrow pre-training priors.** Almost all DF-Wild-Cup detectors start from **ImageNet**-supervised weights. Web-scale image-text pre-training (CLIP) gives features that separate synthetic from natural images across generators. But how much to adapt, and whether one CLIP tower can replace an ensemble, were open.
- **G3: Preprocessing is rarely justified.** Face cropping, frequency transforms, augmentation and balancing are adopted by habit. Several can remove the very evidence a detector needs.

## 1.7 Contributions

1. A **measurement** of checkpoint-selection reliability.
2. A **single-backbone detector** that beats the best published ensemble.
3. A **justified and ablated preprocessing pipeline**.
4. A **22-configuration design-space study**, including negative results.
5. Evidence that **cluster separability is not decision quality**.

## 1.8 Words used on this page

- **Benchmark.** A public dataset with fixed splits that many papers use.
- **Validation split.** Data used to choose settings or checkpoints.
- **Test split.** Data used once at the end to report performance.
- **In-domain.** Test data from the same distribution as training data.
- **Provenance metadata.** Information about where a file came from. Removed here so it cannot leak the label.
- **Ensemble.** Several models whose outputs are combined.
- **ImageNet-supervised.** A model pre-trained to classify the ImageNet photo collection.

## 1.9 Check yourself

- In the code, which class is $y = 1$? Which class is "positive" for the metrics?
- Why does a detector that is near-perfect in-domain still fail in the wild?
- Which one split was never used for training or selection?

Next: [[notes/pairclip-swa/2-vision-transformers-and-clip|2. Vision transformers and CLIP]]
