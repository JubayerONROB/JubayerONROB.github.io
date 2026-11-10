---
title: "PairCLIP-SWA: Study Guide"
date: 2026-11-10
tags:
  - notes
  - computer-vision
  - deepfake
  - deep-learning
---

`computer-vision` `deepfake` `clip` · A from-scratch guide to my paper, [arXiv:2610.37874](https://arxiv.org/abs/2610.37874)

> **PairCLIP-SWA: Similarity-Guided Balancing and Stochastic Weight Averaging for Generalized Deepfake Image Detection with OpenCLIP.**
> Md. Nakib, Sudipto Sarkar, A. J. A. Jubayer Talukder and Mohammad Ariful Haque. Paper summary: [[work/research/pairclip-swa-deepfake-detection|research page]] · Project page: [[work/projects/deepfake-detection-clip-vit|project write-up]]

This guide is for a reader who knows **nothing** about the topic. Each page explains one group of ideas with plain words, small formulas and figures. Every number comes from the paper. Small made-up examples are marked **toy example**. It is the second guide on this site, after the [[notes/proactive-assistant/index|Proactive Assistant guide]]. Where an idea is already explained there (cross-entropy, confidence intervals, precision and recall), I link to it.

## Start here

If you want everything in one straight line, read page 0. If you only need one topic, jump to it.

| # | Page | You will learn |
|---|---|---|
| 0 | [[notes/pairclip-swa/0-the-whole-story\|The whole story, in order]] | The full paper from zero, step by step |
| 1 | [[notes/pairclip-swa/1-the-problem-and-the-data\|The problem and the data]] | What deepfakes are, why detectors fail to generalize, the datasets and splits |
| 2 | [[notes/pairclip-swa/2-vision-transformers-and-clip\|Vision transformers and CLIP]] | Patches, tokens, attention, contrastive pre-training, the model we use |
| 3 | [[notes/pairclip-swa/3-balancing-the-data\|Balancing the data (Stage 1)]] | CLIP-similarity-guided one-to-one subsampling and its honest limits |
| 4 | [[notes/pairclip-swa/4-preprocessing\|Preprocessing]] | Every transformation from file to network input, and why |
| 5 | [[notes/pairclip-swa/5-training-and-unfreezing\|Training and progressive unfreezing]] | Which weights move, the optimizer, mixed precision, early stopping |
| 6 | [[notes/pairclip-swa/6-weight-averaging\|Stochastic weight averaging]] | Averaging weights, the three checkpoints, the training log |
| 7 | [[notes/pairclip-swa/7-evaluation-metrics\|Evaluation metrics]] | Accuracy, Wilson interval, precision, recall, MCC, ROC, AU-ROC, EER |
| 8 | [[notes/pairclip-swa/8-results\|Results]] | Comparison with CAE-Net, cost, and the OpenForensics test |
| 9 | [[notes/pairclip-swa/9-selection-and-validation-bias\|Selection and validation bias]] | Why the best validation checkpoint can be the wrong one |
| 10 | [[notes/pairclip-swa/10-ablations-and-design-space\|Ablations and design space]] | 22 configurations, the negative results, what drives accuracy |
| 11 | [[notes/pairclip-swa/11-representation-geometry\|Representation geometry]] | t-SNE, separation score, k-NN probe, DBSCAN |
| 12 | [[notes/pairclip-swa/12-cost-limits-future\|Cost, limits and future work]] | Compute formula, eight limitations, next experiments |
| 13 | [[notes/pairclip-swa/13-glossary\|Glossary]] | Every symbol and term on one page |

## The paper in six lines

1. A single **OpenCLIP ViT-L/14** detector reaches **97.04%** accuracy on DF-Wild-Cup, against **94.46%** for the best published three-backbone ensemble (CAE-Net). AU-ROC is 98.64% against 97.60%. EER is 4.07% against 5.00%.
2. Its training log shows that the **non-averaged checkpoint swings by 5.34 points** of validation accuracy. The **weight average** is never worse and up to 5.99 points better.
3. On an OpenForensics-derived benchmark, the checkpoint chosen by validation accuracy scores **98.43%** on validation but **88.85%** on a held-out test partition. The terminal average, ranked last on validation, scores **94.76%**.
4. The loss is **one-sided**: 21.1% of genuine photographs are rejected as fake. Scalar accuracy on a balanced split cannot see this.
5. Across **22 configurations**, CLIP pre-training, not ensembling, drives accuracy. Secondary face cropping costs about **34 points**.
6. The paper recommends **per-class selection criteria measured off the early-stopping split**.

## Figures

All figures here are made with Python and matplotlib as vector PDF (fonts embedded) plus a PNG. Each has a PDF link under it. Black is normal and red is the important path. Two figures are cropped from the paper itself and say so in the caption.
