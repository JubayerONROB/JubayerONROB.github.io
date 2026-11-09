---
title: "0. The whole story, in order"
date: 2026-11-09
tags:
  - notes
  - nlp
  - llm
  - edge-ai
---

`nlp` `llm` `edge-ai` · Part of the [[notes/proactive-assistant/index|Proactive Assistant study guide]]

This page tells the **whole paper in one line of thought**, from zero knowledge to the final result. Each step says what we need, what we do, and why. Links go to the detailed pages.

## Step 1. The problem

Imagine smart glasses that listen to your talk. You get stuck: "that performance I went to… the one in the spring…". A small hint appears: **dance performance**. This is a **proactive assistant**. It is never called. It must decide **when** to speak and **what** to say. See [[notes/proactive-assistant/1-the-task-and-the-gate|page 1]].

![One decision at every silence](/attachments/notes/proactive-assistant/fig1-decision-points.png)

## Step 2. Cut the conversation into decision points

After each utterance there is a short silence. Each silence is a **marker**. At every marker the assistant makes a **yes/no choice**. In our test data there are **28,058 markers**, and only **3,356 (11.96%)** need a hint.

## Step 3. The first decision: the gate

A **gate** model reads the dialogue so far, $D_{\le i}$, and gives a score $p_i$ in $[0,1]$. A **threshold** $t$ turns it into a decision:

$$g_i(t) = \mathbf{1}\left[\,p_i \ge t\,\right]$$

A **false alarm** interrupts for nothing. A **miss** leaves the user alone. Raising $t$ reduces false alarms and raises misses. So the paper treats the threshold as a **choice**, tied to a false-alarm budget.

## Step 4. What a language model is

Text is cut into **tokens**. Each token becomes a vector. A stack of $L$ **layers** changes these vectors. The vector after $k$ layers is the **hidden state** $h_k$. A small **head** (a matrix) turns a hidden state into scores, for example two scores for "no hint / hint". Reading the prompt in one go is **prefill**. Writing the answer token by token is **decoding**. Our cost is mostly **prefill**. See [[notes/proactive-assistant/2-language-model-basics|page 2]].

## Step 5. The second decision: the hint, and the memory profile

If the gate fires, a **generator** writes a hint $h_i$ of 1 to 3 words. To do that it needs facts about the user. These come from a **memory profile** $M_w$, written in plain prose, collected before the conversation. The profile adds **306 tokens** to every prompt. For about half the triggers the answer is **not** a copy from the profile, so the model must combine profile and dialogue. See [[notes/proactive-assistant/3-memory-and-prompt|page 3]].

![What the model reads](/attachments/notes/proactive-assistant/fig4-prompt.png)

## Step 6. How the models are trained

We start from a pre-trained model and **fine-tune** it. To save memory we use **LoRA**: freeze the big matrix $W$ and train two thin matrices $A$ and $B$:

$$y = Wx + \frac{\alpha}{r}BAx$$

Weights are stored in **4 bits (NF4)**. The gate learns with a loss that handles the rare trigger class (class weights, **focal loss**). The hint is learned with **cross-entropy**. See [[notes/proactive-assistant/4-training|page 4]].

## Step 7. The common design and its cost

The usual design is a **cascade** of two models: a small gate, and an 8B generator that runs only when the gate fires. It saves generator calls (**7.62× fewer**). But the gate still reads **all** 28,058 markers, and the generator must **reread the whole prompt**, now with the profile.

## Step 8. The key idea: one model, early exit

Use **one** 1B model. Run layers $1 \ldots k$. A classifier head $W_c \in \mathbb{R}^{2\times d}$ reads the hidden state $h_k$ and gives $p_i$.

- If $p_i < t$: stop. Layers $k{+}1 \ldots L$ never run.
- If $p_i \ge t$: **continue the same forward pass** and write the hint.

![Cascade and unified decoder](/attachments/notes/proactive-assistant/fig6-architectures.png)

The cost per marker (in full passes) becomes

$$c_i^{\text{unified}} = \frac{k}{L} + g_i\left(1-\frac{k}{L}\right), \qquad c_i^{\text{cascade}} = 1 + g_i\,c_{\text{gen}}$$

A silent marker costs only $k/L$. A triggered marker costs exactly 1. See [[notes/proactive-assistant/5-early-exit-and-unified-decoder|page 5]].

![Cost per marker](/attachments/notes/proactive-assistant/fig7-cost.png)

## Step 9. How to score a system that has two decisions

Scoring each part alone is misleading. So we define two **end-to-end** scores over the 3,356 true triggers:

$$\text{EM}_{\text{e2e}} = \frac{1}{|\mathcal{T}|}\sum_{i\in\mathcal{T}} g_i m_i, \qquad P_{\text{e2e}} = \frac{\sum_{i\in\mathcal{T}} g_i m_i}{\sum_i g_i}$$

Here $m_i = 1$ if the hint **exactly** equals the reference. The first is recall-type. The second charges every false alarm. A score that assumes a perfect gate is a **ceiling**. And $\text{EM}_{\text{e2e}}$ can never rise when $t$ rises. We also use gate metrics (precision, recall, F1, FAR, AUROC, AUPRC, calibration) and text metrics (BERTScore, ROUGE, judges). See [[notes/proactive-assistant/6-evaluation-metrics|page 6]].

## Step 10. What we found

1. **Ceilings overstate.** Behind a real gate, exact match is **0.2619**, against a ceiling of **0.2971**. End-to-end precision is **0.2387**.
2. **A gate pays off through precision and compute.** The saving is **4.39×** with an 8B generator but only **1.38×** with a 1B one, because the gate itself takes 82% of the gated 1B pipeline's time.
3. **Memory drives quality.** Removing the profile costs **24.7 points** (BERTScore 0.57 to 0.35). A larger generator and retrieval add nothing on exact match.
4. **One model can do both.** The unified decoder reaches end-to-end exact match **0.2929** ($k=6$) and **0.2908** ($k=10$), with **1.31–1.76× less time** than the matched 1B pipeline.

![Memory effect](/attachments/notes/proactive-assistant/fig9-memory.png)

See [[notes/proactive-assistant/7-experiments-and-findings|page 7]].

## Step 11. Are the differences real?

We compare against a **noise floor** (0.0070 F1). We use **cluster bootstrap** intervals (resampling dialogues), **McNemar** tests with **Holm** correction, and a **non-inferiority** margin of 0.25 for the human study. See [[notes/proactive-assistant/8-statistics|page 8]].

## Step 12. What do people think?

**1,144 ratings** over 32 dialogues. Memory helps: **4.01 vs 3.18**. The unified model is **level** with the matched 1B pipeline and **below** the 8B one. LlamaPIE's native judge tracks people best (r = 0.55 and 0.67); exact match tracks them least (0.31 and 0.43). So exact match is a strict **lower bound**. See [[notes/proactive-assistant/9-human-evaluation|page 9]].

![Which score tracks people](/attachments/notes/proactive-assistant/fig10-human-correlation.png)

## Step 13. Before you deploy

Recalibrate the threshold for every new gate. Pick the false-alarm budget on purpose. Expect **one adapter of 42 MB** instead of a second base of 957 MB (up to **1.05 GB** resident). On a 4-core CPU the early exit gives **2.86×** ($k=6$) and **1.51×** ($k=10$) in ONNX Runtime. And remember the limits: a model-made corpus, mostly one rater, no phone or glasses tested, no speech-recognition errors, and serious privacy duties for people nearby. See [[notes/proactive-assistant/10-deployment-and-limits|page 10]].

## One-paragraph summary

A proactive assistant must choose **when** to speak and **what** to say. Judged together, a perfect-gate score overstates the real result, and a gate pays off through precision and compute. Hint quality comes from the **user's memory profile**, not from a bigger model or retrieval. One compact 1B decoder can read its gate from a middle layer and **continue the same pass** to write the hint. It matches the two-model pipeline on automatic scores, runs faster, and people rate it level with the matched 1B pipeline.

Symbols and terms: [[notes/proactive-assistant/11-glossary|Glossary]]
