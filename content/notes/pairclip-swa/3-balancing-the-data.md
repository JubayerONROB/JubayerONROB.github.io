---
title: "3. Balancing the data (Stage 1)"
date: 2026-11-10
tags:
  - notes
  - deepfake
  - data
---

`deepfake` `data` · Part of the [[notes/pairclip-swa/index|PairCLIP-SWA study guide]]

## 3.1 The problem: 5 fakes for every real image

The DF-Wild-Cup training set has 42,690 real and 219,470 fake images. A lazy model that says "fake" every time would be right about 84% of the time. We must balance the classes.

## 3.2 Common ways to balance, and why we did not use them

| Method | Idea | Problem here |
|---|---|---|
| **Oversampling** | Repeat the real images | The detector sees the same reals many times and can memorize them |
| **Loss reweighting** | Give real images a bigger weight | The majority class still dominates the batches |
| **SMOTE** | Invent new minority samples by mixing neighbours | A synthetic "real" is not a valid authentic image |
| **Partitioning** (CAE-Net) | Split the fakes into five subsets and train five times | Five training stages; visits all 262,160 images five times |
| **Random undersampling** | Keep a random fifth of the fakes | Ignores what the fakes look like |

**Count-based balancing** (all but the last two rows) fixes the numbers but leaves **content differences** untouched. This is a problem because of shortcuts.

## 3.3 The shortcut problem

Think of an image as a mix of two factors:

- **content $c$**: identity, pose, illumination, background, capture pipeline;
- **manipulation $m$**: the actual forgery traces.

If the content differs between the classes, that is $p(c \mid y{=}1) \neq p(c \mid y{=}0)$, then a classifier can lower its loss using content alone. For example, it may learn "this person appears mostly in fake videos". That shortcut does **not transfer** to new data.

So when we must throw away most of the fakes anyway, it is better to keep the fakes that **most resemble the reals** than a random fifth of them. Then the content looks alike in both classes, and the model has to look at the manipulation.

## 3.4 Stage 1: CLIP-similarity-guided subsampling

We measure "resembles" with a **frozen CLIP ViT-L/14 image encoder** $\phi$.

![Stage 1](/attachments/notes/pairclip-swa/pc4-stage1.png)
*Figure 6. Stage 1 builds a 1:1 corpus of 85,380 images. [PDF](/attachments/notes/pairclip-swa/pc4-stage1.pdf)*

**Step 1: embed.** Run every real and fake image through $\phi$ to get a vector in $\mathbb{R}^{768}$. Normalize each vector to length 1 (row-normalization). Call the matrices $\hat U \in \mathbb{R}^{n_r \times 768}$ (reals) and $\hat V \in \mathbb{R}^{n_f \times 768}$ (fakes).

**Step 2: similarity.** For unit vectors, the dot product is the **cosine similarity**. One matrix product gives all of them:

$$
S = \hat U \hat V^{\top}, \qquad S_{ij} = \text{similarity of real } i \text{ with fake } j
$$

**Step 3: assign.** Give every real image one partner fake, with no fake used twice, to make the total similarity as large as possible:

$$
\pi^\star = \arg\max_{\pi\ \text{injective}} \sum_{i=1}^{n_r} S_{i,\pi(i)} \tag{4}
$$

This is a **linear assignment problem**. The exact answer costs $O(n^3)$, which is too slow for these sizes. So we solve it **greedily**: process the reals in order and give each one the most similar fake that is not yet used:

$$
\pi(i) = \arg\max_{j \notin \mathcal{U}_{i-1}} S_{ij}, \qquad \mathcal{U}_i = \mathcal{U}_{i-1} \cup \{\pi(i)\}, \quad \mathcal{U}_0 = \emptyset \tag{5}
$$

The **no-reuse rule** stops a few generic fakes from becoming the partner of many reals.

![Greedy toy example](/attachments/notes/pairclip-swa/pc5-greedy-toy.png)
*Figure 7. The greedy rule on a toy matrix with made-up numbers. [PDF](/attachments/notes/pairclip-swa/pc5-greedy-toy.pdf)*

**Memory trick.** The full $S$ has $42{,}690 \times 219{,}470 = 9.37 \times 10^9$ numbers. It never exists in memory at once. Rows are processed in **blocks of $B = 1000$**. One block is $1000 \times 219{,}470$ numbers, which is **837 MB** in float32. Peak memory is $O(B\,n_f)$. Total work is $O(n_r n_f d)$ with $d = 768$.

## 3.5 Algorithm 1 in words

1. Compute $\hat U$ and $\hat V$.
2. Start with no used fakes and an empty corpus.
3. For each block of 1000 reals: compute the block of similarities.
4. For each real in the block: pick its most similar unused fake, mark it used, and add the pair to the corpus.
5. Free the block and continue.
6. Return the balanced corpus $\mathcal{D}_{pair}$.

## 3.6 What it gives

- **42,690 pairs**, a 1:1 corpus of **85,380 images**.
- That is **32.6%** of the 262,160 training images.
- It keeps **19.5%** of the fakes and discards **176,780**.
- For comparison, **one stage** of CAE-Net already uses 86,584 images, and its full schedule visits all 262,160 images **five times**.

It is a **data-efficiency choice**, with a cost: most of the generator diversity in the fake pool never reaches the detector.

## 3.7 What this stage can and cannot be credited with

Two honest caveats from the paper:

1. **No controlled comparison.** There is no run with a *random* one-to-one subsample under an *identical* schedule. The one comparison available is random undersampling at **93.36%** against similarity-guided at **95.67%** (both non-averaged). But those runs also differ in unfreezing depth (**5 vs 11 blocks**), so the 2.31-point gap **cannot be credited to the sampling alone**. It is consistent with a benefit, but does not prove one.
2. **Double rescaling.** The code that built the reported corpus loaded CLIP through HuggingFace transformers. It used `ToTensor` (which already maps pixel values to $[0,1]$) and then `CLIPProcessor`, whose default `do_rescale` divides by 255 **again**. The normalized inputs became

$$
(v_c/255^2 - \mu_c)/\sigma_c \in [-1.792,\, -1.466] \quad \text{instead of roughly } [-1.8,\, 2.1].
$$

   Each channel's range shrank 255-fold. A random-noise image and a flat grey image map to nearly the same tensor. So the similarities that picked the pairs were computed on **near-black inputs**, not on the real appearance. Passing PIL images, or setting `do_rescale=False`, fixes it.

For the reported run, Stage 1 should therefore be read as a **deterministic, similarity-guided one-to-one subsample whose content alignment has not been established.** The paper lists re-running Stage 1 with the fix, plus a random-subsample control, as the first future experiment.

## 3.8 Words used on this page

- **Cosine similarity.** How close in direction two vectors are (1 = same direction).
- **Linear assignment problem.** Match items from two lists, one-to-one, to maximize total score.
- **Greedy algorithm.** Make the best local choice at each step, without looking ahead.
- **Injective.** No two items share a partner.
- **Undersampling / oversampling.** Dropping majority examples / repeating minority examples.
- **SMOTE.** Inventing new minority examples by interpolating between neighbours.
- **Shortcut.** A cue that predicts the label in training but does not reflect the real task.
- **Float32.** A 32-bit number format (4 bytes per value).

## 3.9 Check yourself

- Why is greedy matching only an approximation?
- Why can count-based balancing still leave a shortcut?
- What does the double-rescaling bug do to the CLIP inputs?

Next: [[notes/pairclip-swa/4-preprocessing|4. Preprocessing]]
