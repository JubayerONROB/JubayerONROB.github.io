---
title: "13. Glossary"
date: 2026-11-10
tags:
  - notes
  - deepfake
---

`deepfake` · Part of the [[notes/pairclip-swa/index|PairCLIP-SWA study guide]]

## Symbols

| Symbol | Meaning |
|---|---|
| $x$ | An input image (RGB) |
| $y$ | Label. In the code $y = 1$ is real and $y = 0$ is fake; metrics use **fake as positive** |
| $\mathcal{R}, \mathcal{F}$ | Real pool and fake pool; sizes $n_r = 42{,}690$, $n_f = 219{,}470$ |
| $\phi(\cdot)$ | Frozen CLIP image encoder used in Stage 1, output in $\mathbb{R}^{768}$ |
| $\hat U, \hat V$ | Row-normalized embeddings of reals and fakes |
| $S = \hat U \hat V^\top$ | Cosine-similarity matrix |
| $\pi$ | Assignment: which fake is paired with each real |
| $\mathcal{D}_{pair}$ | The balanced corpus (85,380 images) |
| $R, F_b, N$ | Resize, horizontal flip (with $b \sim \text{Bern}(0.5)$), standardization |
| $\mu, \sigma$ | CLIP channel means and standard deviations |
| $T_{tr}, T_{ev}$ | Training and evaluation transforms |
| $N_p, N, d_m$ | Patches (256), tokens (257), width (1024) |
| $L$ | Number of blocks (24) |
| $Z_\ell$ | Token matrix after block $\ell$ |
| $g(x) \in \mathbb{R}^{768}$ | Image feature (Equation 8) |
| $W_{proj}, W_c, b_c$ | Output projection; linear head and its bias |
| $f_\theta(x)$ | Softmax output of the detector |
| $k(e)$ | Number of trainable blocks at epoch $e$ |
| $K_{max}$ | Cap on trainable blocks (14) |
| $\eta_0, \eta_{swa}$ | Learning rate ($10^{-4}$) and SWA learning rate ($10^{-5}$) |
| $\lambda$ | Weight decay (0) |
| $\theta_t, \theta_{SWA}$ | Weights at epoch $t$; their running mean |
| $e_{swa}$ | Epoch at which averaging starts (12) |
| $\tau, \tau^\star$ | Decision threshold (default 0.5); tuned threshold (0.680) |
| $\Delta, \sigma_f, \sigma_r, S$ | Centroid distance, spreads, separation score |
| $z$ | 1.96, for 95% intervals |

## Terms

**Ablation.** Removing or changing one part to measure its effect.

**Accuracy.** Share of images classified correctly.

**Adversarial robustness.** Resistance to small deliberate changes that fool a model.

**AMP.** Automatic mixed precision: 16-bit math where safe.

**AU-ROC.** Area under the ROC curve; threshold-free ranking score.

**AdamW.** An optimizer; with weight decay 0 it is Adam.

**Attention.** The step where each token mixes in information from other tokens.

**Augmentation.** Random changes to training images to add variety.

**Averaged model (SWA).** The running mean of the weights.

**Backbone.** The main feature-extraction network of a detector.

**Benchmark.** A public dataset with fixed splits.

**Best regular / best SWA / final SWA.** The three checkpoints kept ([[notes/pairclip-swa/6-weight-averaging|page 6]]).

**Blending boundary.** The seam between a forged face region and the original image.

**CAE-Net.** The strongest published three-backbone ensemble on DF-Wild-Cup (94.46%).

**Checkpoint.** A saved copy of the model weights.

**CLIP / OpenCLIP.** Models trained to match images with captions; OpenCLIP is the open re-implementation.

**Class token (CLS).** The extra token that summarizes the image.

**Confusion matrix.** The 2 × 2 table of TP, FP, FN, TN.

**Cosine similarity.** Closeness in direction of two vectors.

**DBSCAN.** A clustering algorithm that needs no preset number of clusters.

**Davies–Bouldin index.** A cluster-quality score; lower is better.

**Deepfake.** An image or video made or changed by a neural network to look real.

**DeepfakeBench.** A benchmark protocol for preprocessing deepfake datasets.

**DF-Wild-Cup (SP Cup 2025).** The in-domain corpus merging eight benchmarks.

**Diffusion model.** A generator that paints an image by removing noise step by step.

**EER.** Equal error rate: where the false-positive rate equals the false-negative rate.

**Embedding.** A vector that represents an item.

**Ensemble.** Several models combined.

**Epoch.** One pass over the training data.

**FFT / DCT / wavelet.** Transforms that show an image's frequency content.

**F1.** The harmonic mean of precision and recall.

**Fine-tuning.** Continuing training of a pre-trained model on a new task.

**Frozen.** Not changed by training.

**GAN.** Generative adversarial network: a generator and a discriminator trained against each other.

**Generalization.** Doing well on data unlike the training data.

**Greedy.** Making the best local choice at each step.

**In-domain.** Test data from the same distribution as training.

**Iterate.** The weights at one point on the training path.

**k-NN probe.** Classifying by the votes of nearest neighbours.

**Layer normalization.** Rescaling each vector to a standard range, per sample.

**LoRA.** Training small low-rank add-on matrices on a frozen model.

**MACs / GMACs.** Multiply-accumulates / billions of them.

**MCC.** Matthews correlation coefficient; uses all four confusion-matrix cells.

**MLP.** The feed-forward network inside each block.

**Noise floor.** See [[notes/proactive-assistant/8-statistics|the earlier guide]].

**Optimistic bias.** A reported score that is too high because it was chosen as the best of many.

**Oversampling / undersampling.** Repeating minority / dropping majority examples.

**Patch.** A small square piece of the image treated as one token.

**Positional embedding.** Numbers that tell the model where a patch came from.

**Precision / recall / specificity.** Share of flagged items that are right / share of true items caught / share of negatives accepted.

**Preprocessing.** Everything done to an image before the network sees it.

**Progressive unfreezing.** Making more blocks trainable as training goes on.

**ROC curve.** True-positive rate against false-positive rate for all thresholds.

**Residual connection.** Adding a layer's input to its output.

**Separation score $S$.** Distance between class centres divided by the sum of their spreads.

**Shortcut.** A cue that predicts the label in training but not in the real task.

**SMOTE.** Inventing minority examples by interpolating between neighbours.

**Specificity.** Real-class recall.

**SWA.** Stochastic weight averaging.

**SWALR.** The PyTorch learning-rate schedule used while averaging.

**t-SNE.** A method that squeezes vectors into 2-D for plotting.

**Triplet loss.** A loss that pulls same-class pairs together and pushes different-class pairs apart.

**ViT.** Vision transformer.

**Weight decay.** A penalty that pulls weights toward zero.

**Wilson interval.** A confidence interval for a proportion that stays inside 0–100%.

**Winner's curse.** The best of many noisy scores tends to include lucky error.
