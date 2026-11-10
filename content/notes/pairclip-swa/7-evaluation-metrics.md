---
title: "7. Evaluation metrics"
date: 2026-11-10
tags:
  - notes
  - deepfake
  - statistics
---

`deepfake` `statistics` · Part of the [[notes/pairclip-swa/index|PairCLIP-SWA study guide]]

This page explains every number the paper reports, from scratch. The basics of precision, recall and F1 are also in [[notes/proactive-assistant/6-evaluation-metrics|the earlier guide]].

## 7.1 The four outcomes

For each image, compare the prediction with the truth. **The fake class is the positive class.**

| | Truth: fake | Truth: real |
|---|---|---|
| **Predicted fake** | TP (forgery caught) | FP (real image wrongly flagged) |
| **Predicted real** | FN (forgery accepted as real) | TN (real image accepted) |

![Metrics](/attachments/notes/pairclip-swa/pc10-metrics.png)
*Figure 12. (a) The confusion matrix of the best-SWA checkpoint at its tuned threshold. (b) A schematic ROC curve (not our curve). [PDF](/attachments/notes/pairclip-swa/pc10-metrics.pdf)*

## 7.2 Metrics from the table

Let TP, FP, FN, TN be the counts.

- **Accuracy** $= \dfrac{TP + TN}{TP + FP + FN + TN}$: the share of images classified correctly.
- **Precision** $= \dfrac{TP}{TP + FP}$: of the images called fake, how many really are.
- **Recall** (sensitivity) $= \dfrac{TP}{TP + FN}$: of the real forgeries, how many were caught.
- **Specificity** $= \dfrac{TN}{TN + FP}$: of the real photographs, how many were accepted. This is also the **real-class recall**.
- **F1** $= \dfrac{2 \cdot \text{precision} \cdot \text{recall}}{\text{precision} + \text{recall}}$.
- **MCC** (Matthews correlation coefficient):

$$
\text{MCC} = \frac{TP \cdot TN - FP \cdot FN}{\sqrt{(TP+FP)(TP+FN)(TN+FP)(TN+FN)}}
$$

MCC uses all four cells, and it is high only if the model does well on **both** classes. It runs from −1 to +1. It is robust when classes are unequal.

**Worked example** (best SWA at $\tau^\star = 0.680$ on SP-Cup validation). The paper recovers the counts: 1,533 of 1,548 real and 1,456 of 1,524 fake images are correct. So TP = 1,456, FN = 68, TN = 1,533, FP = 15.

- Accuracy $= (1456 + 1533)/3072 = 97.30\%$
- Precision $= 1456/(1456 + 15) = 98.98\%$
- Recall $= 1456/1524 = 95.54\%$
- Specificity $= 1533/1548 = 99.03\%$
- MCC $\approx 0.947$

**Where the counts come from.** The training loop logged precision, recall and F1 with the *real* class positive. Because the class sizes are known, the confusion matrix is uniquely recoverable from the four logged numbers (the only integer solution). The paper then reports the fake-positive values from it.

## 7.3 The Wilson confidence interval

Accuracy on a finite test set is an estimate. The **95% Wilson score interval** says how uncertain it is. With $\hat p = k/n$ and $z = 1.96$:

$$
\text{CI}_{95} = \frac{\hat p + \dfrac{z^2}{2n} \pm z\sqrt{\dfrac{\hat p(1-\hat p)}{n} + \dfrac{z^2}{4n^2}}}{1 + \dfrac{z^2}{n}} \tag{13}
$$

It behaves well even when $\hat p$ is close to 0 or 1 (where the simple textbook interval can go above 100%). For the best SWA checkpoint, $\hat p = 0.9704$ and $n = 3{,}072$ give **[96.38, 97.58]**. CAE-Net's interval is [93.60, 95.22]. The two intervals **do not overlap**. For a bootstrap-based interval, see [[notes/proactive-assistant/8-statistics|the statistics page of the earlier guide]].

## 7.4 Thresholds, ROC and AU-ROC

The detector gives a **score** $p$ = probability of fake. The decision rule uses a threshold $\tau$. Moving $\tau$ changes TP, FP, FN and TN.

- **ROC curve.** Plot the **true-positive rate** (= recall) against the **false-positive rate** (= $1 -$ specificity) for every threshold.
- **AU-ROC.** The area under the ROC curve. It is the chance that a random fake gets a higher score than a random real image. It does **not depend on one threshold**. 1.0 is perfect and 0.5 is chance.
- **EER (equal error rate).** The point where the false-positive rate equals the false-negative rate. Lower is better. Ours is **4.07%**.
- **$\tau^\star$.** The accuracy-optimal threshold found by a sweep over **1,000 thresholds**. Ours is $\tau^\star = 0.680$ on the probability of the **real** class. It is chosen on the same split it is evaluated on, so it is **optimistic**.

The default $\tau = 0.5$ is the primary operating point. The tuned $\tau^\star$ is reported separately so it cannot flatter the main number.

## 7.5 In-loop versus re-evaluated accuracy

Validation accuracy logged **inside** the training loop is computed under float16 autocast. The saved checkpoints are **re-evaluated in full precision**. The two differ by up to **0.21 points** (best SWA: 97.17% in-loop at epoch 18, 97.04% re-evaluated). The paper uses **re-evaluated** values for every comparison. The trajectory figures must use the in-loop values.

## 7.6 Cost metrics

- **Parameters.** The number of learned weights. Ours: 304.0 M. CAE-Net: 117.4 M.
- **MACs (multiply-accumulates).** One multiplication plus one addition. **GMACs** = billions of them per image. A rough measure of compute. Ours: 81.0. CAE-Net: 24.8. (FLOPs are about twice the MACs.) The formula is on [[notes/pairclip-swa/12-cost-limits-future|page 12]].
- **Latency.** Milliseconds per image. Ours: 28.1 ms (2× T4 GPUs). CAE-Net: 10.4 ms (P100, from its reported throughput). Different hardware, so only a rough comparison.

## 7.7 Words used on this page

- **Positive class.** The class we call "the thing to detect". Here, fake.
- **Operating point.** One chosen threshold and the metrics it gives.
- **Threshold sweep.** Trying many thresholds and recording the metrics for each.
- **Sensitivity / specificity.** Recall on the positive class / recall on the negative class.
- **Confusion matrix.** The 2 × 2 table of TP, FP, FN, TN.
- **Wilson interval.** A confidence interval for a proportion that stays inside 0–100%.
- **Autocast.** PyTorch's automatic use of float16 where safe.

## 7.8 Check yourself

- Which class is positive in the paper's metrics, and why does it matter?
- Why is $\tau^\star$ "optimistic"?
- Why does MCC need all four cells?

Next: [[notes/pairclip-swa/8-results|8. Results]]
