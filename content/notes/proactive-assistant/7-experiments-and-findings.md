---
title: "7. Experiments and findings"
date: 2026-11-09
tags:
  - notes
  - nlp
---

`nlp` · Part of the [[notes/proactive-assistant/index|Proactive Assistant study guide]]

## 7.1 The data

All systems are tested on **one canonical set** of $N = 28{,}058$ test markers (24,702 silence, 3,356 trigger, 11.96% triggers) over **866 dialogues**. It is built without using any tokenizer, so every model sees the same markers. The dialogues come from three source corpora in LlamaPIE's release: **perl**, **soda** and **synthetic**, with 292, 268 and 306 test dialogues.

For each marker, the window is the dialogue up to that point, cut from the front at 1,300 characters.

**Splits.** The training data fits the weights. The **validation** split (26,410 markers, 12.81% triggers) is used to choose settings such as the threshold. The **test** split is touched only to report results. Validation and test do not share dialogues.

**Threshold selection.** For each gate we try $t = 0.01, 0.02, \ldots, 0.99$ on validation, pick the one with the best F1, and report on test. Choosing on validation instead of test costs a mean of only 0.0016 F1 (at most 0.0041, across 21 systems). No ranking changes.

**A limit to keep in mind.** Dialogues and trigger labels were made by a language model. The labels mark moments a model judged a hint would help, not moments a real wearer needed one. On a natural meeting corpus, a fine-tuned gate was on par with a metadata-only baseline (AUROC 0.8349 vs 0.8291).

## 7.2 Experiment 1: which model is the best gate?

| Gate | PA-F1 | FAR | AUPRC |
|---|---|---|---|
| RoBERTa-large, ASL recipe | 0.8113 | 0.0304 | 0.8902 |
| **Llama-3.2-1B** | **0.8002** | 0.0351 | 0.8883 |
| Qwen2.5-0.5B | 0.7849 | 0.0386 | 0.8642 |
| SmolLM2-360M | 0.7800 | 0.0382 | 0.8596 |
| Gemma-3-1B | 0.7600 | 0.0359 | 0.8415 |
| Gemma-3-270M | 0.7212 | 0.0417 | 0.7784 |
| RoBERTa-large, matched LoRA | 0.7483 | 0.0536 | 0.8132 |
| Logistic regression (21 surface features) | 0.3456 | 0.3108 | 0.2368 |
| Prompted LLM, zero-shot | 0.1381 | 0.0710 | 0.1543 |
| Prompted LLM, few-shot ($k=4$) | 0.1914 | 0.1164 | 0.1545 |

**What it shows.**

- The best decoder gate is **Llama-3.2-1B** (0.8002), the one the two-stage baseline uses.
- An **encoder** (RoBERTa-large) with its own recipe is 1.11 points higher. But the same encoder under the decoders' LoRA recipe falls to 0.7483. The **training recipe** explains about +0.0650 F1; context length only +0.0020.
- Surface features cannot do the job (0.3456). Just asking a general LLM does not work either (0.1381 and 0.1914). The fine-tuned gates learn something **specific to this corpus**.

## 7.3 Experiment 2: what does the generator need?

![Memory profile effect](/attachments/notes/proactive-assistant/fig9-memory.png)
*Figure 9. Exact match on the 3,356 true triggers for different memory conditions. [PDF](/attachments/notes/proactive-assistant/fig9-memory.pdf)*

**The memory profile is the key.** Same adapter, same triggers:

- With the full profile: EM 0.2947.
- With **no profile at inference**: EM 0.0474. That is **−24.73 points** (McNemar $p < 0.001$). Rescaled BERTScore falls from 0.57 to 0.35 and ROUGE-1 from 0.48 to 0.13.

**Controls** (to be sure it is the *content*, not just extra tokens):

1. **Mismatched profile** from another sample: EM 0.0441. Same as no profile ($p = 0.343$).
2. **Length vs content split:** the length share of the gain is $-1.33\%$.
3. **Trained without any profile:** EM 0.0584, close to the no-profile arm. Against that model the effect is 23.63 points.
4. **Span-selection oracle** (the best any copy-from-profile method could do): 0.9371 when the target is in the profile, and 0 otherwise. The fine-tuned model scores below that even when copying would work. So it is **not just copying**.

**A bigger generator does not help on exact match.** Llama-3.1-8B and Llama-3.2-1B tie at the oracle-gate stage ($p = 0.79$) and end to end ($p = 0.338$). Qwen2.5-7B scores 35.79% at the oracle stage, but it is an Instruct model compared with a base one, so family and instruction tuning change together.

**Retrieval does not help.** We ranked profile units by several rankers (bm25, tfidf, embed, hybrid) and kept $k$ units. Exact match falls as $k$ shrinks (0.2935 at 20 units, 0.2864 at 10, 0.2810 at 5). The values at $k=10$ and $k=5$ are significantly below the full profile (Holm-corrected $p = 0.0022$ and $0.0013$). Across **45 configurations**, none beats the full profile. The full profile already fits, so retrieval only removes information.

## 7.4 Experiment 3: from ceiling to deployment

| System | Ceiling (oracle gate) | Behind the real gate |
|---|---|---|
| 1B gate + 1B generator | 0.2971 | **0.2619** |
| 1B gate + 8B generator | 0.2947 | 0.2548 |
| 1B gate + Qwen2.5-7B | 0.3579 | 0.3084 |

End-to-end precision at the deployed point is **0.2387**. Tightening to a 1% false-alarm budget raises it to **0.3011** while end-to-end exact match falls to **0.2122**. So a gate pays off through **precision and compute**, not through more correct hints.

Cost: the gate cuts generator calls by **7.62×**, which is worth **4.39×** against an 8B generator and **1.38×** against a 1B one.

## 7.5 Experiment 4: the unified decoder

At the final checkpoint (step 53,772, one seed per depth):

| System | Gate F1 | FAR | Gen. EM | E2E EM | E2E prec. | Wall (h) | Models |
|---|---|---|---|---|---|---|---|
| Unified, $k=6$ | 0.8022 | 0.0359 | 0.3299 | **0.2929** | 0.2665 | **0.748** | 1 |
| Unified, $k=10$ | 0.8164 | 0.0292 | 0.3218 | 0.2908 | 0.2761 | 1.005 | 1 |
| Two-model, 1B + 1B | 0.8002 | 0.0351 | 0.2971 | 0.2619 | 0.2387 | 1.318 | 2 |
| Two-model, 1B + 8B | 0.8002 | 0.0351 | 0.2947 | 0.2548 | 0.2322 | 2.551 | 2 |

Read the speed-ups from the Wall column: $1.318 / 0.748 = 1.76\times$ and $1.318 / 1.005 = 1.31\times$ against the matched 1B pipeline; $2.551 / 0.748 = 3.41\times$ against the 8B one.

**Careful reading.**

- This is a result on **automatic measures at one checkpoint**.
- Over three seeds only $k=10$ ties the separate gate.
- The unified gate at $k=10$ leads a cascade gate that **also reads the profile**, by +0.0183 F1 [+0.0106, +0.0259]. Under a rule fixed before validation results, this is credited to the **architecture**.
- Exit depth: $k=10$ beats $k=6$ in gate F1 by about 0.013, but end-to-end the two are inside the noise floor. So depth is mainly a **cost** decision.

## 7.6 What the generator gets wrong

From Table 6 of the paper, as a share of the 3,356 true triggers:

| Generator | Exact | Partial overlap | Grounded, other | Hallucinated |
|---|---|---|---|---|
| Llama-3.2-1B | 29.7 | 17.8 | 35.9 | 16.6 |
| Llama-3.1-8B | 29.5 | 27.9 | 23.5 | 19.1 |
| Qwen2.5-7B | 35.8 | 18.5 | 27.3 | 18.4 |

Non-matching hints split across the three error types in similar shares for every generator.

## 7.7 Check yourself

- Which one change cost the most exact-match points?
- Why was the "mismatched profile" test useful?
- Why is the cascade gate's F1 not the whole story of its cost?

Next: [[notes/proactive-assistant/8-statistics|8. Statistics behind the claims]]
