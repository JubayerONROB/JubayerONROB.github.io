---
title: "0. The whole story, in order"
date: 2026-11-10
tags:
  - notes
  - deepfake
  - computer-vision
---

`deepfake` `computer-vision` · Part of the [[notes/pairclip-swa/index|PairCLIP-SWA study guide]]

This page tells the **whole paper as one line of thought**, from zero knowledge to the final result. Each step says what we need, what we do and why. Links go to the detailed pages.

## Step 1. The problem

Neural networks can make fake faces that look real. A **detector** is a classifier that takes an image and gives a score for "fake". The hard part is **generalization**: a detector that is nearly perfect on one family of fakes can fail on another. See [[notes/pairclip-swa/1-the-problem-and-the-data|page 1]].

![The detector](/attachments/notes/pairclip-swa/pc0-task.png)

## Step 2. The data and the baseline

We use the **DF-Wild-Cup** corpus (eight benchmarks merged): 42,690 real and 219,470 fake training images, a 5:1 imbalance. The best published result, **CAE-Net**, fuses three backbones and reaches **94.46%** on the 3,072 validation images. A second corpus, derived from **OpenForensics**, gives a **held-out test** that nothing was trained or selected on.

![Splits](/attachments/notes/pairclip-swa/pc1-data-splits.png)

## Step 3. The whole method on one page

Stage 1 builds a balanced corpus. Stage 2 preprocesses, adapts a CLIP tower and averages the weights. Stage 3 evaluates and analyses.

![Figure 1 of the paper](/attachments/notes/pairclip-swa/paper-figure1.png)
*Figure 1 (Figure 1 of the paper). Overview of PairCLIP-SWA and of the analyses in the paper. Labels P1–P8 are the preprocessing steps of [[notes/pairclip-swa/4-preprocessing|page 4]]. [PDF](/attachments/notes/pairclip-swa/paper-figure1.pdf)*

## Step 4. The model: a vision transformer from CLIP

A 224 × 224 image is cut into 256 patches of 14 × 14 pixels. Each patch becomes a token of width 1024. A class token and positional embeddings are added. 24 transformer blocks mix the tokens by attention. The class token is projected to a 768-number feature $g(x)$ and a linear head gives two scores. We start from **OpenCLIP ViT-L/14**, which was trained to match images with captions. We keep only the image tower. See [[notes/pairclip-swa/2-vision-transformers-and-clip|page 2]].

![ViT](/attachments/notes/pairclip-swa/pc2-vit.png)

## Step 5. Stage 1: balance with similarity

For each real image, pick the **most similar unused fake** in CLIP space (cosine similarity), greedily and without reuse. This gives a 1:1 corpus of **85,380** images, **32.6%** of the training images. Keeping fakes that look like the reals should reduce content shortcuts. Honest limits: no random control exists, and the code double-rescaled its inputs. See [[notes/pairclip-swa/3-balancing-the-data|page 3]].

## Step 6. Preprocess to keep the evidence

Use the **full released frame** (no second face crop), bilinear resize to 224 × 224, CLIP normalization, a horizontal flip only for training, and **class-exact batches** of 16 real + 16 fake. Cropping the face cost about **34 points**. See [[notes/pairclip-swa/4-preprocessing|page 4]].

![Preprocessing](/attachments/notes/pairclip-swa/pc6-preprocessing.png)

## Step 7. Train gradually

Start with a linear probe plus two blocks, then unfreeze one more block every two epochs: $k(e) = \min(2 + \lfloor e/2 \rfloor, 14)$. The run reached $k = 11$. Loss is plain cross-entropy, the optimizer is AdamW with weight decay 0, with float16 mixed precision and early stopping. See [[notes/pairclip-swa/5-training-and-unfreezing|page 5]].

![Unfreezing](/attachments/notes/pairclip-swa/pc7-unfreezing.png)

## Step 8. Average the weights

From epoch 12, keep a running mean of the weights. Keep three checkpoints: best regular, best SWA and final SWA. The non-averaged weights swing by **5.34 points** of validation accuracy while the average is never worse and is up to **5.99** points better. See [[notes/pairclip-swa/6-weight-averaging|page 6]].

![Training dynamics](/attachments/notes/pairclip-swa/pc9-training-dynamics.png)

## Step 9. Measure carefully

Accuracy with Wilson intervals, precision, recall, specificity, F1, MCC, AU-ROC, EER and a tuned threshold $\tau^\star$. The fake class is positive. See [[notes/pairclip-swa/7-evaluation-metrics|page 7]].

## Step 10. The in-domain result

PairCLIP-SWA reaches **97.04%** accuracy (CAE-Net 94.46%), **98.64%** AU-ROC (97.60%) and **4.07%** EER (5.00%). It uses one backbone, one pass and a third of the training images, but is **2.59× larger** and **3.27× more MACs**. See [[notes/pairclip-swa/8-results|page 8]].

![Comparison](/attachments/notes/pairclip-swa/pc11-comparison.png)

## Step 11. The surprise: the best validation checkpoint fails on new data

On the OpenForensics test, the checkpoint chosen by validation accuracy (98.43%) scores **88.85%**, rejecting **21.1%** of genuine photographs as fake. The terminal average, ranked last on validation, scores **94.76%**. The selected checkpoint makes **2.1×** as many errors. See [[notes/pairclip-swa/8-results|page 8]] and [[notes/pairclip-swa/9-selection-and-validation-bias|page 9]].

![OpenForensics](/attachments/notes/pairclip-swa/pc13-openforensics-gap.png)

## Step 12. Why: selection on noise

Picking the best of many noisy scores overstates quality (the winner's curse). The non-averaged weights are very noisy. Averaging reduces the variance. The loss was **one-sided** (specificity), so scalar accuracy on a balanced split could not see it. The paper recommends selecting on balanced accuracy or MCC, on a split disjoint from early stopping, with per-class recall, and preferring weight averaging. See [[notes/pairclip-swa/9-selection-and-validation-bias|page 9]].

## Step 13. What drives accuracy

Across **22 configurations**: CLIP pre-training dominates (ImageNet CNNs 71.70–75.79%, OpenCLIP ViT-L/14 93.36–97.04%). Face cropping and frequency inputs discard evidence (56.05% and 49.61%). Averaging weights beats averaging predictions. Cluster separability does **not** predict decision quality. See [[notes/pairclip-swa/10-ablations-and-design-space|page 10]] and [[notes/pairclip-swa/11-representation-geometry|page 11]].

![Design space](/attachments/notes/pairclip-swa/pc16-design-space.png)

## Step 14. Limits and next steps

Single seed, an unisolated Stage 1 with a rescaling bug, selection-split numbers for the main comparison, uncontrolled survey runs, no adversarial test, and a model too big for edge use. Next: fix Stage 1 and add a random control, more seeds, adversarial tests, class-symmetric corruption, and distillation. See [[notes/pairclip-swa/12-cost-limits-future|page 12]].

## One-paragraph summary

A single OpenCLIP ViT-L/14 tower, adapted by progressive unfreezing on a one-to-one balanced corpus and averaged in weight space, beats the best published three-backbone ensemble on DF-Wild-Cup (97.04% vs 94.46%). But its training log shows that the checkpoint picked by validation accuracy is a noisy maximum. On an independent held-out test, the selected checkpoint makes 2.1 times as many errors as the terminal average, through a one-sided collapse in real-photo recall that balanced accuracy cannot see. The main lesson is about **how checkpoints are selected**: use per-class measures on a separate split and prefer weight averaging.

Symbols and terms: [[notes/pairclip-swa/13-glossary|Glossary]]
