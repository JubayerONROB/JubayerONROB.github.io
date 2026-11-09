---
title: "4. Training: LoRA, 4-bit, losses"
date: 2026-11-09
tags:
  - notes
  - llm
---

`llm` · Part of the [[notes/proactive-assistant/index|Proactive Assistant study guide]]

## 4.1 Fine-tuning

We do not train a language model from nothing. We start from a **base model** that already knows language (Llama-3.2-1B) and **fine-tune** it on our task. Fine-tuning means we show many examples and nudge the weights so the model gets them right.

Our examples are **markers**. Each one has a label (trigger or silence) and, for triggers, the target hint.

## 4.2 Why LoRA?

A full model has billions of numbers. Changing all of them needs a lot of memory. **LoRA** (low-rank adaptation, Hu et al., 2022) changes only a tiny add-on.

Take one big weight matrix $W$ of size $d \times d$. Freeze it. Add a small update that is the product of two thin matrices:

$$y = W x + \frac{\alpha}{r}\, B A x$$

- $A$ has size $r \times d$ and $B$ has size $d \times r$.
- $r$ is the **rank**, and it is much smaller than $d$.
- $\alpha$ is a scale.
- Only $A$ and $B$ are trained.

**Why it is cheap.** $W$ has $d^2$ numbers. $A$ and $B$ have only $2dr$. If $r \ll d$, that is far fewer.

In our code: rank $r = 16$, scale $\alpha = 32$, dropout 0.05, applied to every attention projection (`q`, `k`, `v`, `o`) and every MLP projection (`gate`, `up`, `down`).

![LoRA](/attachments/notes/proactive-assistant/fig5-lora.png)
*Figure 5. The frozen path is black. The trained path is red. [PDF](/attachments/notes/proactive-assistant/fig5-lora.pdf)*

**The adapter is small.** One adapter is about **42 MB**. A second full 1B base model would be about **957 MB**. That is the core of the memory saving in [[notes/proactive-assistant/10-deployment-and-limits|page 10]].

## 4.3 4-bit weights (NF4)

Normally each weight takes 16 or 32 bits. **Quantization** stores each weight with only 4 bits. **NF4** is a 4-bit format designed for weights that follow a bell-shaped curve. The result is a model about 4 times smaller in memory.

In our tests, 4-bit weights **save memory, not time** at batch size one. The 16-layer decoder is **1.65 GB** in NF4 against **4.99 GB** in fp32.

## 4.4 Cross-entropy loss

Training needs a number that says "how wrong is the model?". That number is the **loss**. The model changes its weights to make the loss smaller.

For a classifier, the usual loss is **cross-entropy**. If the model gives the true class probability $p_t$, then

$$\text{CE} = -\log p_t$$

If $p_t = 1$ the loss is 0 (perfect). If $p_t$ is near 0 the loss is very large.

> **Toy example.** True class gets probability 0.9: loss $= -\ln 0.9 \approx 0.105$. True class gets 0.1: loss $\approx 2.30$.

The hint tokens use the same loss, token by token: the model should give high probability to each correct token.

## 4.5 Class imbalance and focal loss

Only about 12% of markers are triggers. A lazy model that always says "silence" would be right 88% of the time. We need to push it to care about the rare class.

**Class weights** make mistakes on the rare class cost more. In our code the weights are 1.0 for silence and 2.5 for trigger.

**Focal loss** goes further. It shrinks the loss on easy examples so the model focuses on hard ones:

$$\text{FL} = (1 - p_t)^{\gamma}\,\text{CE}$$

When $p_t$ is near 1 (easy), $(1-p_t)^\gamma$ is near 0 and the loss almost disappears. When $p_t$ is small (hard), the factor is near 1. In our code $\gamma = 1.5$.

**What the paper found.** No alternative to plain cross-entropy was significantly better. Strong settings hurt: $\gamma = 2$ cost $-0.0310$ F1 and raising the trigger weight from 1 to 4 cost $-0.0278$ F1. Mild reweighting is harmless.

## 4.6 The joint loss of the unified model

The unified model learns two jobs with one set of weights, so it has **two losses** added together:

$$\mathcal{L} = \lambda_{\text{cls}}\,\text{FL}(\text{gate}) + \lambda_{\text{gen}}\,\text{CE}(\text{hint tokens})$$

In our code both $\lambda$ values are 1.

**An important detail.** During **training**, every example runs through all $L$ layers, even examples that will be silent at test time. This lets the hint loss shape layers $k{+}1 \ldots L$. Only at **inference** does the model stop early for silent markers. This is normal for early-exit models.

## 4.7 Training size

The unified model trained for **2 epochs (53,772 steps)** over marker-level rows. The two-stage gate trained for **4 epochs** over dialogue-level samples. So the budgets differ and comparisons are between systems *as trained*. An **epoch** is one full pass over the training data.

## 4.8 Check yourself

- Why does LoRA train fewer numbers than full fine-tuning?
- If the model says "hint needed" with probability 0.2 and the truth is "hint needed", what is the cross-entropy?  (*Answer: $-\ln 0.2 \approx 1.61$.*)
- Why do we use class weights?

Next: [[notes/proactive-assistant/5-early-exit-and-unified-decoder|5. Early exit and the unified decoder]]
