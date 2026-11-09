---
title: "6. Evaluation metrics"
date: 2026-11-09
tags:
  - notes
  - nlp
---

`nlp` · Part of the [[notes/proactive-assistant/index|Proactive Assistant study guide]]

A metric is a way to turn "how good is it?" into a number. This page explains every metric in the paper, from the basics.

## 6.1 The four outcomes

(See Figure 3 on [[notes/proactive-assistant/1-the-task-and-the-gate|page 1]].) For each marker, compare the gate to the reference label:

| | Reference: trigger | Reference: no trigger |
|---|---|---|
| **Gate fires** | TP (right call) | FP (false alarm) |
| **Gate silent** | FN (miss) | TN (right quiet) |

On our test set, $TP + FN = 3{,}356$ and $TN + FP = 24{,}702$.

## 6.2 Gate metrics

**Precision.** Of everything the gate fired on, how much was right?

$$\text{precision} = \frac{TP}{TP + FP}$$

**Recall.** Of all real triggers, how many did the gate catch?

$$\text{recall} = \frac{TP}{TP + FN}$$

**F1.** One number that balances the two. It is their **harmonic mean**, which is low if either one is low:

$$F_1 = \frac{2 \cdot \text{precision} \cdot \text{recall}}{\text{precision} + \text{recall}}$$

In the paper this is called **PA-F1** (the F1 of the gate's binary per-marker decision against the reference label).

**FAR (false-alarm rate).** Of all quiet moments, how many did the gate interrupt?

$$\text{FAR} = \frac{FP}{TN + FP}$$

> **Toy example.** 10 triggers, gate catches 8 and also fires 4 times wrongly. Precision $= 8/12 = 0.67$. Recall $= 8/10 = 0.80$. $F_1 = 2(0.67)(0.80)/(0.67+0.80) \approx 0.73$.

**Paper example.** At the deployed point, gate precision is 0.7648 and recall is 0.8391. It emits 3,682 hints, and 23.5% of them fall where the corpus says to stay silent.

## 6.3 Threshold-free metrics

F1 depends on $t$. Two metrics look at the score ranking only.

**AUROC.** Take a random trigger and a random silence marker. AUROC is the chance that the gate gives the trigger the higher score. 0.5 is a coin flip, 1.0 is perfect.

**AUPRC.** The area under the precision-recall curve. It is better than AUROC when the positive class is rare, as here.

## 6.4 Calibration

A gate that is good at **ranking** may still give bad **probabilities**. If it says "0.8" on 100 markers, about 80 should be true triggers. That is **calibration**.

**ECE (expected calibration error).** Cut the scores into bins. In each bin compare the average predicted probability to the real fraction of triggers. Average the gaps, weighted by bin size:

$$\text{ECE} = \sum_{b} \frac{n_b}{N}\,\bigl|\,\text{acc}_b - \text{conf}_b\,\bigr|$$

Result: the best-ranking gate (RoBERTa-large ASL, AUPRC 0.8902) is the **worst calibrated** (ECE 0.3036). The best-calibrated model (Gemma-3-1B, ECE 0.0425) ranks lower. ECE is 7.1 times bigger. This matters if you adapt the threshold from user feedback ([[notes/proactive-assistant/10-deployment-and-limits|page 10]]).

![Ranking vs calibration](/attachments/notes/proactive-assistant/fig15-ranking-vs-calibration.png)
*Figure 11. Left: how well each gate ranks (AUPRC). Right: how well its probabilities match reality (ECE, lower is better). Red marks the worst and the best calibrated gate. [PDF](/attachments/notes/proactive-assistant/fig15-ranking-vs-calibration.pdf)*

## 6.5 Generation metrics: is the hint right?

**Exact match (EM).** The hint is correct only if it equals the reference hint exactly. Strict, but simple:

$$m_i = \mathbf{1}\,[\,h_i = h_i^{*}\,]$$

A near-synonym counts as wrong. So we treat EM as a **strict lower bound** on usefulness.

Why keep EM? It is the only metric with a clean **end-to-end** form. A suppressed trigger has no text to score, and "no hint" is clearly not an exact match. A score like BERTScore would need an invented value for "no hint".

**BERTScore.** Compares the **meaning** of two texts. Each word is turned into a vector with a model (we use roberta-large). Each word in one text is matched to its most similar word in the other by cosine similarity. We then average. Precision, recall and F1 versions exist. We use no idf weighting. We also report a **rescaled** version, because raw scores sit in a narrow band and rescaling shifts every score by about 0.70, which is 57 times the spread between the memory-only baselines.

**ROUGE-1.** Counts the overlap of single words between hint and reference.

**LLM judges.** A strong model rates the hint. LlamaPIE's **native judge** uses its own rubric. The paper tests which judges match people ([[notes/proactive-assistant/9-human-evaluation|page 9]]).

**Error types.** Wrong hints are split into: **partial overlap**, **grounded but incorrect** (uses real profile facts), and **hallucination** (made up). For the 1B generator, of the 3,356 true triggers: 29.7% exact, 17.8% partial, 35.9% grounded other, 16.6% hallucinated.

![Error types](/attachments/notes/proactive-assistant/fig19-error-types.png)
*Figure 12. What the generators produce at the 3,356 true triggers, in percent (Table 6). The 'exact' share equals the oracle-gate exact match. [PDF](/attachments/notes/proactive-assistant/fig19-error-types.pdf)*

**More words used above.**

- **Cosine similarity.** How close in direction two vectors are. 1 means the same direction, 0 means unrelated. BERTScore uses it between word vectors.
- **idf (inverse document frequency).** A weight that makes rare words count more. We turn it **off** (`idf=False`).
- **Rescaling with a baseline.** Moving scores so that a random pair of texts scores near 0. The raw BERTScores sit in a narrow band, so a rescaled value is easier to read.
- **Reference-free.** A judge that sees only the hint and the conversation, not the correct answer.
- **Rubric.** A written list of rules a judge follows to give a score.
- **Operating point.** One chosen threshold $t$ and the precision, recall and false-alarm rate it gives. "Deployed operating point" means the one we would actually use.
- **Prevalence.** The share of positive cases in the data. Our trigger prevalence is 11.96% on test and 12.81% on validation.

## 6.6 Scoring both decisions together

This is the paper's first contribution. Let $\mathcal{T}$ be the set of reference triggers. At each marker $g_i$ is the gate decision and $m_i$ says if the hint matched.

$$
\text{EM}_{\text{e2e}} = \frac{1}{|\mathcal{T}|}\sum_{i \in \mathcal{T}} g_i\, m_i, \qquad P_{\text{e2e}} = \frac{\sum_{i \in \mathcal{T}} g_i\, m_i}{\sum_i g_i} \tag{2}
$$

- **End-to-end exact match** divides by the number of real triggers. It is **recall-type**: a trigger the gate suppressed scores 0, and false alarms do not enter.
- **End-to-end precision** divides by **every emitted hint**, false alarms included.

The first one splits into two parts:

$$
\text{EM}_{\text{e2e}} = R \cdot \text{EM}_{\text{fwd}}, \quad R = \frac{1}{|\mathcal{T}|}\sum_{i\in\mathcal{T}} g_i, \quad \text{EM}_{\text{fwd}} = \frac{\sum_{i\in\mathcal{T}} g_i m_i}{\sum_{i\in\mathcal{T}} g_i} \tag{3}
$$

$R$ is the gate's **recall**. $\text{EM}_{\text{fwd}}$ is the exact match on the triggers it **forwards**.

**Oracle gate.** A *stage-wise* generation score is Equation (2) with $g_i = 1$ for every trigger. That is a **ceiling**. No real system has a perfect gate.

**A built-in property.** Raising $t$ can only switch gates **off**. So $\text{EM}_{\text{e2e}}$ **cannot rise** as $t$ rises. That is why we never read it alone. We pair it with end-to-end precision, which can rise.

**Worked numbers.** Deployed point, 1B generator: $R = 0.8391$ (the gate's recall). From Equation (3), $\text{EM}_{\text{fwd}} = 0.2619 / 0.8391 \approx 0.312$ (our arithmetic). That is **above** the 0.2971 ceiling. It suggests that the triggers the gate catches are a bit easier than average.

![Ceiling vs deployed](/attachments/notes/proactive-assistant/fig8-end-to-end.png)
*Figure 13. (a) Ceilings (open) against scores behind a real gate (red). (b) Tightening to a 1% false-alarm budget gives more precision and less recall. [PDF](/attachments/notes/proactive-assistant/fig8-end-to-end.pdf)*

## 6.7 Cost metrics

**Wall-clock time.** Total seconds or hours. We report it on an **early-exit-only basis**, the one optimization measured for both architectures.

**Generator-call reduction.** The gate cuts generator calls by **7.62×**. That is worth **4.39×** in wall-clock time against an 8B generator, but only **1.38×** against a 1B one. Why? Because the gate itself is **82%** of the gated 1B pipeline's runtime on our per-marker setup.

**Resident weights.** Memory held for model weights (GB).

## 6.8 Check yourself

- Why does $\text{EM}_{\text{e2e}}$ never go up when $t$ goes up?
- What does end-to-end precision charge that end-to-end exact match does not?
- Why is exact match "a strict lower bound"?

Next: [[notes/proactive-assistant/7-experiments-and-findings|7. Experiments and findings]]
