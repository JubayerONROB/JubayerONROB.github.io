---
title: "8. Results"
date: 2026-11-10
tags:
  - notes
  - deepfake
---

`deepfake` · Part of the [[notes/pairclip-swa/index|PairCLIP-SWA study guide]]

## 8.1 The paper's argument in one table

Table V already holds the whole story. Accuracy (%) of the three checkpoints, at $\tau = 0.5$, with 95% Wilson intervals:

| Split (n) | Best regular | Best SWA | Final SWA |
|---|---|---|---|
| DF-Wild-Cup validation (3,072) | 95.67 | **97.04** | **97.04** |
| 95% CI | [94.89, 96.34] | [96.38, 97.58] | [96.38, 97.58] |
| OpenForensics validation (39,428) | **98.43** | **98.43** | 97.67 |
| 95% CI | [98.30, 98.55] | [98.30, 98.55] | [97.52, 97.81] |
| OpenForensics test (10,905) | 88.85 | 88.85 | **94.76** |
| 95% CI | [88.24, 89.43] | [88.24, 89.43] | [94.33, 95.17] |

On the two selection splits, the winner differs: averaging wins by **1.37** points on DF-Wild-Cup and **loses** by 0.76 on OpenForensics validation. On the only split used for neither training nor selection, averaging wins by **5.91** points.

## 8.2 Comparison with CAE-Net

![Comparison](/attachments/notes/pairclip-swa/pc11-comparison.png)
*Figure 13. Accuracy of every baseline reported by CAE-Net, with our checkpoints. [PDF](/attachments/notes/pairclip-swa/pc11-comparison.pdf)*

PairCLIP-SWA improves on CAE-Net on **every metric both systems report** (Tables VII and VIII):

| Metric | CAE-Net | PairCLIP-SWA, $\tau = 0.5$ | $\tau^\star = 0.680$ |
|---|---|---|---|
| Accuracy (%) | 94.46 | **97.04** | 97.30 |
| 95% CI | [93.60, 95.22] | [96.38, 97.58] | [96.66, 97.82] |
| Errors / 3,072 | 170 | **91** | 83 |
| AU-ROC (%) | 97.60 | **98.64** | |
| EER (%) | 5.00 | **4.07** | |
| Precision (%) | 93.70 | not logged | 98.98 |
| Recall (%) | 95.60 | not logged | 95.54 |
| Specificity (%) | – | not logged | 99.03 |
| F1 (%) | 94.64 | not logged | 97.23 |
| MCC | – | not logged | 0.947 |

- Accuracy rises **2.58 points**, a **46.5% reduction in errors** (170 → 91). The Wilson intervals do not overlap.
- AU-ROC shows 43% less area above the curve: $(100 - 98.64)/(100 - 97.60) = 0.57$.
- The 2.58-point margin is **4.4 times** the seed standard deviation CAE-Net reports for its final ensemble (±0.58). We cannot give our own seed spread (single run).
- Even the **non-averaged** checkpoint (95.67%) beats the ensemble.
- At $\tau^\star$ the operating point is asymmetric: specificity 99.03% and fake recall 95.54%. Of the 83 errors, **68 are forgeries accepted as real**. Moving the threshold from 0.5 to 0.680 gains only 0.26 points, and since $\tau^\star$ is chosen on the evaluation split, that gain is an upper bound.

## 8.3 What it costs

![Cost](/attachments/notes/pairclip-swa/pc12-cost.png)
*Figure 14. The cost side. [PDF](/attachments/notes/pairclip-swa/pc12-cost.pdf)*

The detector is **2.59× larger** (304.0 M vs 117.4 M parameters), needs **3.27× the MACs** (81.0 vs 24.8 G), and measured **2.7× the per-image latency** (28.1 vs 10.4 ms, on different hardware). In exchange it uses **one backbone, one forward pass, one training stage and a third of the training images** (85,380 vs 262,160), with no wavelet branch and no fusion weights to tune.

## 8.4 OpenForensics: the held-out test

The OpenForensics run converges quickly. At epoch 11, training and validation accuracy are 98.46% and 98.64% (in-loop), with a validation loss of 0.0426. Re-evaluated in full precision, best-regular and best-SWA score **98.43%** (38,809 of 39,428) and final SWA **97.67%** (38,509 of 39,428). At most seven of the 24 blocks are trainable by then, and validation accuracy slightly exceeds training accuracy. There is no sign of memorization on the training distribution.

On validation, the selected checkpoint is **nearly symmetric** (fake recall 99.03%, specificity 97.83%, MCC 0.969) and it beats the terminal average. Read alone, this split would recommend it without hesitation.

![OpenForensics gap](/attachments/notes/pairclip-swa/pc13-openforensics-gap.png)
*Figure 15. (a) Accuracy on validation and on held-out test. (b) Per-class recall on the test set. [PDF](/attachments/notes/pairclip-swa/pc13-openforensics-gap.pdf)*

**On the held-out test, the picture reverses.**

- The validation-selected checkpoints fall to **88.85%**, **9.58 points** below their validation accuracy.
- The loss is **one-sided**: fake recall barely moves (99.03 → 98.67%), but specificity collapses (97.83 → **78.88%**).
- Of **1,216 test errors**, **1,143 (94.0%)** are genuine photographs rejected as forgeries, a **15.7 : 1** asymmetry.
- The **terminal average**, ranked last on validation, reaches **94.76%**: false positives fall from 1,143 to 275, false negatives rise from 73 to 296, the asymmetry becomes **0.93 : 1**, MCC rises from 0.792 to 0.895, and test error falls by **53.0%**.
- The Wilson intervals, [88.24, 89.43] and [94.33, 95.17], are more than five points apart.

Selecting by validation accuracy would have deployed the model that makes **2.1 times as many errors**.

![Confusion matrices](/attachments/notes/pairclip-swa/pc14-confusion-openforensics.png)
*Figure 16. Confusion matrices for the validation-selected checkpoint and the terminal average. [PDF](/attachments/notes/pairclip-swa/pc14-confusion-openforensics.pdf)*

Complete metrics at $\tau = 0.5$ (Table IX):

| Split | Checkpoint | Acc. | Prec. | Rec. | Spec. | F1 | MCC |
|---|---|---|---|---|---|---|---|
| Validation (39,428) | Best reg./SWA | 98.43 | 97.84 | 99.03 | 97.83 | 98.43 | 0.969 |
| | Final SWA | 97.67 | 99.58 | 95.73 | 99.60 | 97.61 | 0.954 |
| Test (10,905) | Best reg./SWA | 88.85 | 82.58 | 98.67 | 78.88 | 89.91 | 0.792 |
| | Final SWA | 94.76 | 94.97 | 94.61 | 94.92 | 94.79 | 0.895 |

## 8.5 A mechanism, shown on ten images

The paper shows ten randomly drawn test images under both checkpoints. Each tile's title gives the label, the prediction and the softmax confidence. A **green border** is a correct prediction and a **red border** is an error. The same ten images appear in a different order in the two blocks.

![Ten random test images, from the paper](/attachments/notes/pairclip-swa/paper-figure6-test-images.png)
*Figure 17 (Figure 6 of the paper). Ten randomly drawn OpenForensics test images under the validation-selected checkpoint (top) and the terminal average (bottom). The photographs come from the public OpenForensics-derived test set. [PDF](/attachments/notes/pairclip-swa/paper-figure6-test-images.pdf)*

The sample spans sensor noise, low light, greyscale, motion blur, JPEG blocking, colour casts, occlusion and multi-face crops. The two images the selected checkpoint gets wrong are both **genuine** and both **severely degraded**: a heavily noised crowd scene (0.90) and a portrait with an extreme magenta colour cast (0.99). It rejects them as fake **with high confidence**. The average classifies both correctly, with its two lowest confidences (0.93 and 0.62).

![Close-up of the two genuine photographs](/attachments/notes/pairclip-swa/pc19-degraded-genuine-photos.png)
*Figure 18. The two genuine photographs that the selected checkpoint rejects, cropped from Figure 6 of the paper, with the verdict of each checkpoint. [PDF](/attachments/notes/pairclip-swa/pc19-degraded-genuine-photos.pdf)*

This fits the idea that the selected checkpoint learned **"low-level degradation means synthesis"**. Preprocessing step P5, which never shows the network degraded real images, does nothing to discourage this. The paper treats it as a **hypothesis consistent with the evidence**, not a proven cause: **ten images illustrate; the 10,905 quantify.**

## 8.6 Check yourself

- Which checkpoint is best on SP-Cup validation? On the held-out test?
- What fraction of the 1,216 test errors are genuine photographs rejected as fake?
- Why is the 2.58-point margin over CAE-Net not a seed-level comparison?

Next: [[notes/pairclip-swa/9-selection-and-validation-bias|9. Selection and validation bias]]
