---
title: "12. Cost, limits and future work"
date: 2026-11-10
tags:
  - notes
  - deepfake
---

`deepfake` · Part of the [[notes/pairclip-swa/index|PairCLIP-SWA study guide]]

## 12.1 Where the compute goes

The forward cost is dominated by the 24 blocks. Let $N = N_p + 1$ be the number of tokens and $d_m$ the width. One block does three kinds of work:

- the **projections** for queries, keys, values and output: $4 N d_m^2$ MACs;
- the **attention** itself ($QK^\top$ and the weighted sum with $V$): $2 N^2 d_m$ MACs;
- the **MLP** (two matrices, $d_m \to 4d_m \to d_m$): $8 N d_m^2$ MACs.

The patch embedding adds $N_p \cdot 3 \cdot 14^2 \cdot d_m$. In total

$$
\text{MACs} = L\left(12 N d_m^2 + 2 N^2 d_m\right) + N_p \cdot 3 \cdot 14^2 \cdot d_m \tag{14}
$$

With $L = 24$, $N = 257$, $d_m = 1024$:

- one block: $12 \cdot 257 \cdot 1024^2 \approx 3.23 \times 10^9$ for projections and MLP, plus $2 \cdot 257^2 \cdot 1024 \approx 1.35 \times 10^8$ for attention;
- 24 blocks plus the patch embedding give **81.0 GMACs** (**162.0 GFLOPs**) per image;
- the quadratic attention term is only **4.0%** of this.

**Memory.** Parameters take **1,160 MB** in float32 and **580 MB** in float16, against 448 MB for CAE-Net. Measured latency is **28.1 ms per image** on 2× T4.

**Training is cheaper than these numbers suggest.** Between **8.3% and 45.6%** of the parameters receive gradients in the reported run. And one stage on 85,380 images replaces five stages of 86,584 images each. **Stage 1** costs $n_r + n_f$ frozen forward passes plus $9.37 \times 10^9$ similarities, **once**.

> **MACs and FLOPs.** One MAC is one multiplication and one addition, which is 2 FLOPs. That is why 81.0 GMACs equals 162.0 GFLOPs.

## 12.2 Limitations (as the paper states them)

1. **Single seed.** The reported runs are single trajectories. CAE-Net reports five-seed means. Our 2.58-point margin is 4.4 times its seed deviation, but our own spread is unknown.
2. **Stage 1 is not isolated, and it double-rescaled its inputs.** No random one-to-one control exists, and the similarities used were computed on attenuated inputs.
3. **Selection on the evaluation split.** DF-Wild-Cup numbers (CAE-Net's too) are selection-split numbers. $\tau^\star$ is tuned there as well.
4. **Uncontrolled design-space runs.** Apart from block E of Table XI, comparisons in the survey confound schedule, epochs and sometimes data and hardware.
5. **Metric coverage.** Threshold-free metrics exist only for the DF-Wild-Cup best-SWA checkpoint. The OpenForensics analysis is at $\tau = 0.5$.
6. **Geometry from one subsample.** t-SNE, separation scores and probes use one 1,000-image subsample per corpus.
7. **No adversarial evaluation**, unlike CAE-Net.
8. **Cost.** 304 M parameters and 81 GMACs rule out edge deployment without **distillation**.

## 12.3 Future work

1. **Re-run Stage 1** with corrected preprocessing, and train a **random-subsample control** under an identical schedule, to measure what similarity-guided balancing contributes.
2. **More seeds** for the main run. Re-run the threshold sweep on the OpenForensics splits, so selection effects carry dispersion and threshold-free metrics.
3. **Adversarial robustness**: evaluate against **FGSM** and **PGD** attacks.
4. **Class-symmetric corruption augmentation**: apply the same noise, blur and compression to both classes, to test against the "degradation means fake" shortcut.
5. **Distillation**: teach a smaller student model to copy the averaged tower, and measure how much accuracy and selection robustness survive.
6. A **weight-decay sweep** (suggested in the paper's discussion of weight decay).

## 12.4 Words used on this page

- **GMACs / GFLOPs.** Billions of multiply-accumulates / floating-point operations.
- **Latency.** Time per image.
- **Distillation.** Training a small model to imitate a big one.
- **FGSM / PGD.** Standard attacks that nudge an image slightly to fool a classifier. **Adversarial robustness** means resisting them.
- **Edge deployment.** Running on a small device such as a phone, not a data centre.

## 12.5 Check yourself

- Which term of Equation (14) is largest?
- Why does the paper say its own 97.04% is an upper bound on deployment accuracy?
- What is the first experiment on the future-work list?

Next: [[notes/pairclip-swa/13-glossary|13. Glossary]]
