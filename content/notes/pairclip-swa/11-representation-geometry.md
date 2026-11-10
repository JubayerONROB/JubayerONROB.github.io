---
title: "11. Representation geometry"
date: 2026-11-10
tags:
  - notes
  - deep-learning
  - deepfake
---

`deep-learning` · Part of the [[notes/pairclip-swa/index|PairCLIP-SWA study guide]]

A model turns each image into a vector $g(x) \in \mathbb{R}^{768}$ (Equation 8, [[notes/pairclip-swa/2-vision-transformers-and-clip|page 2]]). This page asks: **do real and fake images form separate clusters in that space, and does that predict how good the classifier is?** The paper's answer: **not reliably.**

## 11.1 The tools

**t-SNE.** A method that squeezes high-dimensional vectors into 2 dimensions so you can plot them, while keeping neighbours close. In the picture, each dot is an image. Axes have no direct meaning. Distances between far-apart clusters are not reliable.

**Separation score $S$.** Let $\mu_f, \mu_r$ be the centres (centroids) of the fake and real clouds, and $\sigma_f, \sigma_r$ the root-mean-square spread of each cloud around its centre. Then

$$
\Delta = \lVert \mu_f - \mu_r \rVert_2, \qquad S = \frac{\Delta}{\sigma_f + \sigma_r} \tag{12}
$$

This is a **two-cluster Fisher-type ratio**. Bigger $S$ means the clouds are far apart compared with how wide they are. It has no units.

**k-NN probe.** For each image, look at its $k$ nearest neighbours in the embedding and vote. The accuracy shows how much class information survives in the projected space.

**DBSCAN.** An algorithm that finds clusters **without being told how many** and without a 2-D projection. We run it on the **full 768 numbers**. Two scores measure the result:

- **Silhouette coefficient.** For each point: how much closer it is to its own cluster than to the next one. Runs from −1 to +1. Higher is better.
- **Davies–Bouldin index.** The average similarity between each cluster and its most similar other cluster. **Lower** is better.

## 11.2 Results (Table X)

Subsets: DF-Wild-Cup, 1,000 validation images (493 fake, 507 real); OpenForensics, 1,000 held-out images (513 fake, 487 real). "Head" is the classifier accuracy on the **full** split.

| Corpus | Checkpoint | $\Delta$ | $\sigma_f$ | $\sigma_r$ | $S$ | k-NN probe | Head |
|---|---|---|---|---|---|---|---|
| DF-Wild-Cup | Best regular | 43.90 | 10.70 | 10.90 | 2.033 | 96.00 | 95.67 |
| | Best SWA | 40.73 | 10.41 | 10.72 | 1.927 | 97.20 | 97.04 |
| | Final SWA | 39.08 | 10.32 | 10.07 | 1.917 | 97.20 | 97.04 |
| OpenForensics | Best regular | 40.42 | 8.42 | 9.72 | 2.228 | 97.80 | 88.85 (test) |
| | Best SWA | 40.42 | 8.42 | 9.72 | 2.228 | 97.80 | 88.85 (test) |
| | Final SWA | 43.02 | 8.97 | 10.09 | 2.257 | 97.80 | 94.76 (test) |

**Check one score by hand:** best regular on DF-Wild-Cup: $43.90/(10.70 + 10.90) = 43.90/21.60 = 2.03$. ✓

![t-SNE](/attachments/notes/pairclip-swa/paper-figure7-tsne.png)
*Figure 20 (Figure 7 of the paper). t-SNE embeddings of 1,000 DF-Wild-Cup validation images (493 fake, 507 real) for the three checkpoints. Green is real, red is fake, crosses are centroids. [PDF](/attachments/notes/pairclip-swa/paper-figure7-tsne.pdf)*

## 11.3 What it shows

![Geometry vs accuracy](/attachments/notes/pairclip-swa/pc17-geometry-vs-accuracy.png)
*Figure 21. Separation score against accuracy for the three checkpoints on both corpora. [PDF](/attachments/notes/pairclip-swa/pc17-geometry-vs-accuracy.pdf)*

**On DF-Wild-Cup, separation and accuracy move in opposite directions.** The best-regular checkpoint has the **highest** separation (2.033) and the **lowest** accuracy. Averaging shrinks the centre distance $\Delta$ by 11.0%, but the pooled spread by only 5.6%, so $S$ falls to 1.917. Yet the k-NN probe **removes 14 of its 35 fake-side errors** (fake recall 92.90 → 95.74%, MCC 0.922 → 0.944), and the classifier head gains 1.37 points.

**On OpenForensics, almost the same geometry hides a six-point gap.** The checkpoints differ by at most 0.03 in $S$ and **not at all** in probe accuracy (97.80%). Yet they differ by **5.91 points** on the held-out test. What averaging changes is **not the arrangement of the embedding but the decision boundary laid over it**, which is exactly what a separability index does not measure.

**Without projection, cluster structure is weak.** DBSCAN on the 768-dimensional OpenCLIP features gives silhouette coefficients of **0.109** and **0.315** (two parameter settings) and Davies–Bouldin indices of **0.911** and **0.700**. That is moderate unsupervised structure at best, in a feature family where a linear head exceeds 97%.

## 11.4 The lesson

**Cluster indices, projected or not, are not proxies for classifier quality.** Papers that show a pretty t-SNE as evidence of a good representation, as is common, should be read with this caveat. Two cautions from the paper itself:

- the DF-Wild-Cup probe agrees with the head to within 0.16 points, but it is fit on a **single 1,000-image subsample**;
- the differences in $S$ are small enough that **subsample variance cannot be excluded**.

## 11.5 Words used on this page

- **Embedding / feature.** The vector $g(x)$ the model builds for an image.
- **Centroid.** The average point of a cloud of vectors.
- **Fisher ratio.** Distance between class centres divided by within-class spread.
- **Nearest neighbours.** The closest points to a given point.
- **Unsupervised.** Without using labels.
- **Projection.** Mapping vectors to fewer dimensions.

## 11.6 Check yourself

- On which corpus did a higher separation score go with a *lower* accuracy?
- Why can two checkpoints have the same $S$ and the same probe accuracy but different test accuracy?
- Is a good-looking t-SNE enough to claim a good classifier?

Next: [[notes/pairclip-swa/12-cost-limits-future|12. Cost, limits and future work]]
