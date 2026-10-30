---
title: "Generalized Deepfake Image Detection with OpenCLIP"
date: 2026-10-27
tags:
  - research
  - computer-vision
  - deepfake-detection
  - preprint
status: preprint
---

`computer-vision` `deepfake-detection` `openclip` · Project Oct 2024 – Jan 2025, arXiv Oct 2026 · **Status: Preprint · [arXiv:2610.37874](https://arxiv.org/abs/2610.37874)**

[GitHub →](https://github.com/DarkJ0Y/PairCLIP-SWA) · [[work/projects/deepfake-detection-clip-vit|Project page]]

## Abstract

Deepfake detectors are almost always deployed as the single checkpoint that scored best on a validation split, yet nobody measures how reliable that choice is. This paper measures it with **PairCLIP-SWA**, a single-backbone detector that adapts an OpenCLIP ViT-L/14 visual tower on a class-balanced corpus and averages the fine-tuning trajectory in weight space. It was written with Md. Nakib, Sudipto Sarkar and Prof. Mohammad Ariful Haque: *PairCLIP-SWA: Similarity-Guided Balancing and Stochastic Weight Averaging for Generalized Deepfake Image Detection with OpenCLIP* ([arXiv:2610.37874](https://arxiv.org/abs/2610.37874)).

![PairCLIP-SWA pipeline](/attachments/projects/deepfake-detection-clip-vit/pipeline.png)
*The three stages: similarity-guided balancing, partial adaptation with weight averaging, and evaluation.*

## Methodology

The training data has 42,690 real images and 219,470 fake ones. A frozen CLIP ViT-L/14 embeds all of them, and each real image is paired with its most similar unused fake image (greedy one-to-one selection), which gives a balanced corpus of 85,380 images. The OpenCLIP ViT-L/14 visual tower is then unfrozen progressively, one more block every two epochs, with a linear head on top. Each batch has exactly 16 real and 16 fake images. Stochastic weight averaging (SWA) averages the weights along the fine-tuning trajectory from epoch 12. Models are trained in-domain on the IEEE SP Cup 2025 (DF-Wild-Cup) benchmark under the same protocol as the strongest published three-backbone ensemble (CAE-Net), and tested on a second, OpenForensics-derived benchmark.

## Key findings

- **One backbone beats an ensemble.** The weight-averaged detector reaches 97.04% accuracy, 98.64% AU-ROC and a 4.07% equal error rate, against 94.46%, 97.60% and 5.00% for the three-backbone ensemble, using about a third of the training images.
- **Averaging matters.** Over the averaged epochs, the non-averaged checkpoint swings across 5.34 points of validation accuracy while its validation loss more than doubles. The average is never worse and is up to 5.99 points better.
- **The best validation checkpoint can fail.** On the OpenForensics-derived benchmark, the checkpoint that validation accuracy picks scores 98.43% on validation but 88.85% on a disjoint test set of 10,905 images, and it rejects 21.1% of genuine photographs. The final SWA model, which ranks last on validation, scores 94.76%.
- **CLIP pre-training does the work.** In a study of 22 in-house configurations on the same split, CLIP pre-training, not ensembling, drives accuracy. Secondary face cropping costs about 34 points, and frequency-domain inputs transfer poorly.

## Results

On the SP Cup 2025 validation set (3,072 images):

| Metric | CAE-Net ensemble | PairCLIP-SWA |
|---|---|---|
| Accuracy | 94.46% | **97.04%** |
| AU-ROC | 97.60% | **98.64%** |
| Equal error rate | 5.00% | **4.07%** |
| Backbones / forward passes | 3 / 3 | **1 / 1** |
| Training images used | 262,160 | **85,380** |
| Parameters | **117.4 M** | 304.0 M |

![Accuracy and loss during the averaged epochs](/attachments/projects/deepfake-detection-clip-vit/trajectory.png)
*Left: validation accuracy of the non-averaged checkpoint against the SWA average. Right: the running model overfits, but the average does not.*

![Validation accuracy against held-out test accuracy](/attachments/projects/deepfake-detection-clip-vit/val_test_tradeoff.png)
*Validation ranking and held-out test ranking disagree.*

![Design-space study of 22 configurations](/attachments/projects/deepfake-detection-clip-vit/design_space.png)
*Left: every configuration on the identical validation split. Right: how different input representations and objectives change validation accuracy.*

## Recommendation

The paper recommends choosing checkpoints with per-class selection criteria measured on the early-stopping split, instead of one overall validation accuracy.

## Related

[[work/projects/deepfake-detection-clip-vit|Deepfake Detection using CLIP-ViT]] — the project page, with the implementation details.

[[work/research/proactive-conversation-assistant|Proactive Conversation Assistant]] — the other preprint from the same research group.
