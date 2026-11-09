---
title: "9. Human evaluation"
date: 2026-11-09
tags:
  - notes
  - nlp
---

`nlp` · Part of the [[notes/proactive-assistant/index|Proactive Assistant study guide]]

Automatic scores are only a proxy. This page explains how real people rated the hints.

## 9.1 Design

- We sampled **100 test dialogues** with **433 hints**.
- Each hint was rendered in **7 versions**. They include the 8B generator with and without memory, the 1B generator, and the unified model at both exit depths.
- Each hint was assigned to **5 annotators**.
- Annotators rated each hint on LlamaPIE's **5-point uptake scale**, with the following turns visible. Uptake means "did this hint help the conversation?".
- Every version puts its hints at the **same gold trigger markers**. So the study compares **what each system says**, not **when it speaks**.
- The study followed a **pre-registered plan**, time-stamped and hash-pinned before any rating existed.

## 9.2 What really happened (deviations)

Honesty about the study matters:

1. One annotator's ratings were scored, unblinded, during annotation.
2. Annotation was then stopped early, after that interim look.
3. Missing ratings were excluded per item rather than per hint. This was a scoring change made after seeing data.

The analysed data are **1,144 uptake ratings over 32 of the 100 dialogues**: 829 of one annotator's 833 assigned hints, 313 from a second annotator on 10 conversations, and 2 from a third. It rests mostly on **one rater**.

## 9.3 Result 1: memory helps people too

With the profile, the 8B generator's hints average **4.01** uptake. Without it: **3.18**. The difference is **+0.83** with 95% CI $[+0.48, +1.23]$ (clustered by dialogue). This agrees with the automatic metrics.

## 9.4 Result 2: the unified model

| Comparison (A vs B) | A | B | A − B | 98.75% CI | Reading |
|---|---|---|---|---|---|
| Unified $k=6$ vs 1B | 3.64 | 3.60 | +0.04 | $[-0.31, +0.41]$ | level; non-inferiority not shown |
| Unified $k=10$ vs 1B | 3.58 | 3.60 | −0.02 | $[-0.35, +0.30]$ | level; non-inferiority not shown |
| Unified $k=6$ vs 8B (memory) | 3.64 | 4.01 | −0.38 | $[-0.69, -0.04]$ | lower |
| Unified $k=10$ vs 8B (memory) | 3.58 | 4.01 | −0.44 | $[-0.83, -0.07]$ | lower |

So people rate the unified model **level with the matched 1B pipeline** and **below the 8B one**, although it is higher on end-to-end exact match. An exploratory (unplanned) look: the 8B generator rates +0.42 above the 1B one (4.01 vs 3.60), while the two tie on exact match.

## 9.5 Result 3: which automatic score matches people?

![Correlation with human uptake](/attachments/notes/proactive-assistant/fig10-human-correlation.png)
*Figure 10. Pearson $r$ between human uptake and each automatic signal, over 136 hints. [PDF](/attachments/notes/proactive-assistant/fig10-human-correlation.pdf)*

| Rendering | EM | BERTScore | ROUGE-1 | native judge |
|---|---|---|---|---|
| 8B, memory | 0.31 | 0.47 | 0.51 | 0.55 |
| 1B | 0.43 | 0.61 | 0.62 | 0.67 |

**Order, best first:** LlamaPIE's **native judge**, then ROUGE-1, then BERTScore, then **exact match**. So we recommend the native judge for this task, a choice made **after** this comparison. We keep exact match as the primary metric only because it alone has an end-to-end form.

**Caution.** The ranking rests on two renderings. The native judge scored only the 8B and 1B ones. Our own reconstruction of LlamaPIE's rubric agrees poorly with the native judge, so we do not use it for any claim.

## 9.6 Why test the judges at all?

Rating open-ended text with a strong model, without a reference, is standard (Zheng et al., 2023). Reported agreement with human preference is high enough that many people use it as a proxy. But it must be **checked on each task**. That is what this study does for ours.

## 9.7 Check yourself

- Why does every version place hints at the same trigger markers?
- What does "non-inferiority not shown" mean?
- Which automatic score is the best match to people, and which is the worst?

Next: [[notes/proactive-assistant/10-deployment-and-limits|10. Deployment and limits]]
