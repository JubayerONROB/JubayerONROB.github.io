---
title: "5. Early exit and the unified decoder"
date: 2026-11-09
tags:
  - notes
  - llm
  - edge-ai
---

`llm` `edge-ai` · Part of the [[notes/proactive-assistant/index|Proactive Assistant study guide]]

This is the main idea of the paper.

## 5.1 The usual design: a cascade

The existing way (LlamaPIE, Chen et al., 2025) uses **two models**:

1. A small **gate** (1B) reads the dialogue at every silence.
2. Only if the gate says yes, a bigger **generator** (8B) writes the hint.

This is called a **cascade**. It saves work because the big model runs rarely. We reimplemented it as the baseline.

**The problem.** The gate still reads **every** marker. Our tests show it takes **82%** of the runtime of the gated 1B pipeline. And when a marker fires, the generator must read the whole prompt **again from scratch**, now with the profile. Two models also need two sets of weights in memory.

## 5.2 The idea: gate from a middle layer

Use **one** 1B model for both jobs.

- Run the prompt through layers $1 \ldots k$.
- At layer $k$, a small **classifier head** $W_c \in \mathbb{R}^{2 \times d}$ reads the hidden state $h_k$ and gives the gate score $p_i$.
- If $p_i < t$: **stop**. Layers $k{+}1 \ldots L$ never run. Output nothing.
- If $p_i \ge t$: **keep going** in the **same forward pass** through layers $k{+}1 \ldots L$ and write the hint.

![Cascade and unified decoder](/attachments/notes/proactive-assistant/fig6-architectures.png)
*Figure 6. (a) The cascade. (b) The unified decoder. The red path is the one that runs only when the gate fires. [PDF](/attachments/notes/proactive-assistant/fig6-architectures.pdf)*

We tried exit depths $k = 6$ and $k = 10$ (out of $L = 16$). One base model and **one shared LoRA adapter** serve both objectives.

## 5.3 How this differs from normal early exit

In normal **confidence-based early exit**, an intermediate classifier tries to **approximate** the final answer, and the model stops when it is sure.

Ours is different. The middle readout does not approximate the deep output. It decides **whether the deep computation should run at all**. The router and the expert are the **same weights**, and the routing decision is a **prefix of the computation it authorizes**. Early exit is the mechanism, but it is not our claim. The claim is the shared gate-and-generator design.

## 5.4 The cost formula

Count cost in **full passes over the prompt**, before decoding any hint token. Let $L = 16$.

- **Unified:** $\;c_i^{\text{unified}} = \dfrac{k}{L} + g_i\left(1 - \dfrac{k}{L}\right)$
- **Cascade:** $\;c_i^{\text{cascade}} = 1 + g_i\, c_{\text{gen}}$

Here $c_{\text{gen}}$ is the cost of one prefill of the separate generator in the same units.

Read them case by case:

| Marker | Unified cost | Cascade cost |
|---|---|---|
| silent ($g_i = 0$) | $k/L$ | 1 |
| triggered ($g_i = 1$) | $k/L + (1 - k/L) = 1$ | $1 + c_{\text{gen}}$ |

So a silent marker costs only $k/L$ of a pass. That gives an **ideal saving of $L/k$**: $16/6 = 2.67\times$ at $k = 6$ and $16/10 = 1.60\times$ at $k = 10$. A triggered marker costs **exactly one pass** in the unified model, not one plus the generator.

![Cost per marker](/attachments/notes/proactive-assistant/fig7-cost.png)
*Figure 7. Cost of one marker in full passes of the 1B model. The dashed box $c_{\text{gen}}$ is a symbol, not a measured size. [PDF](/attachments/notes/proactive-assistant/fig7-cost.pdf)*

## 5.5 The price of the idea

Reading layer $k$ instead of the last layer may give a **worse** gate. That was the central risk we measured. Results (see [[notes/proactive-assistant/7-experiments-and-findings|page 7]]):

- At the final checkpoint the gate F1 is 0.8022 ($k=6$) and 0.8164 ($k=10$), against 0.8002 for the cascade gate.
- Over three seeds the $k = 10$ gate **ties** the separate gate ($0.8022 \pm 0.0029$ mean and SD, +0.0020). The $k = 6$ gate is below it ($0.7846 \pm 0.0033$, −0.0156).
- Deeper is better for the gate: $k = 10$ leads $k = 6$ by about 0.013 F1. But $k = 6$ is cheaper. So exit depth is mainly a **cost** decision.

## 5.6 Memory saving

The unified model needs one base and one adapter. A probe with one 4-bit 1B base, two adapters and the head used **1.05 GB**. The second adapter costs 42 MB where a second base would cost 957 MB. That saves **915 MB**. The unified model has one adapter only, so 1.05 GB is an **upper bound** for it.

## 5.7 Check yourself

- Why does a silent marker cost $k/L$?
- What does "same forward pass" mean, and why does it save work?
- At $k = 10$, what is the ideal saving?  (*Answer: $16/10 = 1.60\times$.*)

Next: [[notes/proactive-assistant/6-evaluation-metrics|6. Evaluation metrics]]
