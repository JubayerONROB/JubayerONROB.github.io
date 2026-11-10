---
title: "6. Stochastic weight averaging"
date: 2026-11-10
tags:
  - notes
  - deep-learning
---

`deep-learning` · Part of the [[notes/pairclip-swa/index|PairCLIP-SWA study guide]]

## 6.1 The problem: the last epoch is noisy

Training with random batches and a big learning rate makes the weights **jump around** from epoch to epoch. Each epoch's weights are a slightly different model. If you pick one of them by its validation score, you pick a **noisy maximum**.

## 6.2 The idea: average the weights

**Stochastic weight averaging (SWA)** keeps a **running mean of the weights** along the end of the training path, instead of only the latest weights. The average sits in the **middle** of the region the weights were wandering through. Such middle points tend to lie in **flatter** regions of the loss, which generalize better when the data shifts. They also cost **nothing extra at inference**: the average is just one set of weights.

![SWA concept](/attachments/notes/pairclip-swa/pc8-swa-concept.png)
*Figure 10. Epoch weights are averaged into one model. Three checkpoints are kept. [PDF](/attachments/notes/pairclip-swa/pc8-swa-concept.pdf)*

## 6.3 How we do it

From epoch $e_{swa} = 12$ we maintain the running mean

$$
\theta_{SWA}^{(t)} = \theta_{SWA}^{(t-1)} + \frac{\theta_t - \theta_{SWA}^{(t-1)}}{n_t + 1} \tag{11}
$$

This is the **online** form of $\frac{1}{n}\sum_t \theta_t$: the new average moves a fraction $1/(n_t+1)$ of the way toward the new weights.

> **Toy example.** Suppose one weight has values 4, 6, 8 at three epochs. The running mean is 4, then $4 + (6-4)/2 = 5$, then $5 + (8-5)/3 = 6$. That equals $(4+6+8)/3 = 6$. ✓.

**Details of our setup.**

- The learning rate is lowered toward $\eta_{swa} = 0.1\,\eta_0 = 10^{-5}$ with the **ten-epoch cosine schedule** of `SWALR`, stepped once per epoch.
- PyTorch's `AveragedModel` **copies** the weights on its first update instead of averaging. So the final average is made of the **seven iterates of epochs 13–19**.
- A **normalization-statistics pass** is applied to the final average. It does nothing for a layer-normalized tower like ours. It is needed for backbones with batch normalization.

## 6.4 Three deployable checkpoints

Every epoch we evaluate and save **both** the running average and the non-averaged weights. That gives three models you could deploy:

| Name | What it is |
|---|---|
| **Best regular** | the non-averaged weights of the epoch with the highest validation accuracy |
| **Best SWA** | the running average, cut at its best validation epoch |
| **Final SWA** | the average over the whole averaged part of the path (epochs 13–19) |

Algorithm 2 of the paper in words: unfreeze the last $k(e)$ blocks; train one epoch with the class-exact batches; compute validation accuracy; if $e \ge e_{swa}$ update the average and evaluate it; track the best regular and best SWA; stop if the regular model has not improved for 8 epochs; finish with the normalization pass and save the final average.

## 6.5 The training log

Here is the full log over the averaged epochs (Table VI, in-loop values).

| Epoch | Blocks | Train loss | Train acc | Non-avg val loss | Non-avg val acc | SWA val loss | SWA val acc | Gap |
|---|---|---|---|---|---|---|---|---|
| 12 | 8 | 0.1628 | 93.58 | 0.1677 | 95.70 | 0.1677 | 95.70 | – |
| 13 | 8 | 0.0802 | 97.01 | 0.1684 | 95.61 | 0.1684 | 95.61 | – |
| 14 | 9 | 0.1060 | 95.93 | 0.2552 | 91.05 | 0.1383 | 95.61 | +4.56 |
| 15 | 9 | 0.0669 | 97.44 | 0.2005 | 93.88 | 0.1426 | 95.31 | +1.43 |
| 16 | 10 | 0.0885 | 96.65 | 0.2344 | 92.22 | 0.1386 | 95.80 | +3.58 |
| 17 | 10 | 0.0538 | 97.89 | 0.3603 | 90.36 | 0.1334 | 96.35 | **+5.99** |
| 18 | 11 | 0.0697 | 97.29 | 0.2307 | 93.49 | 0.1178 | 97.17 | +3.68 |
| 19 | 11 | 0.0351 | 98.48 | 0.2226 | 95.67 | 0.1227 | 97.04 | +1.37 |

"Gap" is SWA minus non-averaged validation accuracy. The two are equal at epochs 12–13 because the first SWA update copies the weights.

![Training dynamics](/attachments/notes/pairclip-swa/pc9-training-dynamics.png)
*Figure 11. (a) Accuracy. (b) Loss. The non-averaged weights swing and overfit; the average does not. [PDF](/attachments/notes/pairclip-swa/pc9-training-dynamics.pdf)*

## 6.6 What the log shows

1. **The selected checkpoint is a noisy maximum.** From one epoch to the next, non-averaged validation accuracy moves **2.33 points on average**. Over eight epochs it spans **5.34 points**, from 95.70 to 90.36 (standard deviation 2.13). The average spans 1.86 points (standard deviation 0.70) and changes by only 0.34 points between epochs. Any rule that picks one of the noisy iterates is picking from a spread almost **three times wider** than the 1.87-point margin that separates the three best systems in the CAE-Net paper.
2. **The iterate overfits; the average does not.** Training loss falls from 0.1628 to 0.0351 (**−78%**) and training accuracy reaches 98.48%. The non-averaged validation loss climbs to 0.3603 at epoch 17, **2.15 times** its epoch-12 value, with a train-validation accuracy gap of 7.53 points (at epoch 17). The averaged model's validation loss **falls 30%** to 0.1178. The first big jump in non-averaged loss (epoch 14, +0.087) coincides with the first unfreezing step inside the averaged window.
3. **Averaging wins at every epoch.** From epoch 14, where the average first differs from the iterate, the average is better at every epoch, by **1.37 to 5.99 points (3.44 on average)**. Whatever epoch early stopping might have landed on, the average was the better model to deploy.

## 6.7 Averaging weights vs averaging predictions

An **ensemble** averages the *predictions* of several models. It needs several forward passes. SWA averages the *weights* of one model's path and needs **one** pass. [[notes/pairclip-swa/10-ablations-and-design-space|Page 10]] compares the two directly.

## 6.8 Words used on this page

- **Iterate.** The weights at one point on the training path.
- **Running mean.** An average that is updated one value at a time.
- **Flat minimum.** A low-loss region where small changes to the weights barely change the loss.
- **Cosine schedule.** A learning rate that follows a half cosine wave down to a small value.
- **Batch normalization.** A normalization that uses batch statistics (not in our tower).
- **In-loop value.** A number computed during training, in float16 autocast.
- **Checkpoint.** A saved copy of the model weights.

## 6.9 Check yourself

- Why is the average of the weights usually better than the last weights?
- Which seven epochs make up the final average, and why not eight?
- At which epoch is the gap between the average and the iterate largest?

Next: [[notes/pairclip-swa/7-evaluation-metrics|7. Evaluation metrics]]
