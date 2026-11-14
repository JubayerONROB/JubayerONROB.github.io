---
title: "14. Interview deep dive: the cost model"
date: 2026-11-14
tags:
  - notes
  - math
  - interview
---

`math` `interview` · Part of the [[notes/proactive-assistant/index|Proactive Assistant study guide]]

**Builds on:** [[notes/proactive-assistant/5-early-exit-and-unified-decoder|5. Early exit and the unified decoder]]; [[notes/proactive-assistant/10-deployment-and-limits|10. Deployment and limits]]; [[notes/proactive-assistant/3-memory-and-prompt|3. Memory profile and prompt]]. **Previous:** [[notes/proactive-assistant/13-deep-dive-gate-and-end-to-end|13. Gate and end-to-end score]].

This page derives Equation (4), the ideal $L/k$ saving, the expected cost at the real trigger rate, and why the measured numbers differ from the ideal. Basic symbols: [[notes/proactive-assistant/12-math-foundations|page 12]].

## 14.1 What is being counted

**Meaning.** Cost is counted in **full passes of the 1B model over one marker's prompt**, before any hint token is decoded. Decoding is only 1 to 3 tokens, so prefill dominates *(paper)*.

**Assumptions** (all three are simplifications, and the paper's formula uses them):

1. Every one of the $L = 16$ layers costs the same.
2. The prompt length is fixed for a marker. The attention term, which grows with the square of the prompt length, is ignored.
3. Cost counts layer computations only (no loading, no tokenization).

*These are modelling assumptions, so the formula is an **ideal**. Section 14.5 shows where reality departs.*

## 14.2 Equation (4): the cost of one marker

**Formula.** For marker $i$ with gate decision $g_i \in \{0,1\}$:

$$
c_i^{\text{unified}} = \frac{k}{L} + g_i\left(1 - \frac{k}{L}\right), \qquad
c_i^{\text{cascade}} = 1 + g_i\, c_{gen} \tag{4}
$$

$k$ is the exit layer (6 or 10). $L = 16$ is the number of layers. $c_{gen}$ is the cost of one prefill of the separate generator, in the same units (one full pass of the 1B gate $= 1$).

**Derivation.**

- *Unified, silent* ($g_i = 0$). The model runs layers $1..k$ and stops: cost $k/L$.
- *Unified, triggered* ($g_i = 1$). It runs layers $1..k$, reads the gate, **continues from layer $k$** (the hidden state is reused, not recomputed) through layers $k{+}1..L$. Total layers $= k + (L-k) = L$: cost $= 1$. Written as one formula: $\frac{k}{L} + 1\cdot\left(1-\frac{k}{L}\right) = 1$. ✓
- *Cascade, silent.* The gate is a separate 1B model that always runs all $L$ layers: cost $1$.
- *Cascade, triggered.* Gate (1) **plus** a separate generator that must read a new prompt (with the memory profile) **from scratch**: cost $1 + c_{gen}$.

**Worked example** *(k = 6, L = 16)*.

| Marker | Unified | Cascade ($c_{gen}=1$, assumption) |
|---|---|---|
| silent | $6/16 = 0.375$ | $1$ |
| triggered | $0.375 + 1\times0.625 = 1$ | $1 + 1 = 2$ |

**Why it matters here.** A silent marker costs $k/L$ of a pass, and a triggered one costs exactly one pass instead of $1 + c_{gen}$. Both savings come from the same idea: the router and the expert are the same weights *(paper)*.

**Interview question.** *Why is the triggered cost exactly 1 and not more?* **Answer.** Layers $1..k$ are computed once and their output is the input of layer $k{+}1$. Nothing is recomputed. The only extra work is layers $k{+}1..L$, which together with the first $k$ layers equals one full pass. (During training the model always runs full depth so the generation loss can shape layers $k{+}1..L$. Only inference short-circuits.)

## 14.3 The ideal saving $L/k$

**Meaning.** If every marker were silent, how much cheaper is the unified gate than a full pass?

**Formula.** Saving $= \dfrac{\text{cost of a full pass}}{\text{cost of the early exit}} = \dfrac{1}{k/L} = \dfrac{L}{k}$.

**Worked example.**

- $k = 6$: $16/6 = 2.667$.
- $k = 10$: $16/10 = 1.600$.

*(paper: "2.67× at $k=6$ and 1.60× at $k=10$".)*

**Why it matters here.** It is the upper bound on what early exit can save on silent markers, and about 88% of markers are silent.

**Interview question.** *Why is the ideal saving not a function of the trigger rate?* **Answer.** $L/k$ is the saving on **silent** markers only, which cost $k/L$ against 1. The trigger rate enters when you average over all markers (next section).

## 14.4 Expected cost at the real trigger rate

**Meaning.** Over many markers, the average cost per marker.

**Formula.** Let $\pi = P(g_i = 1)$ be the share of markers where the gate fires. Take the expectation of Equation (4) (see [[notes/proactive-assistant/12-math-foundations|page 12]], section 12.5):

$$
E[c^{\text{unified}}] = \frac{k}{L} + \pi\left(1 - \frac{k}{L}\right), \qquad
E[c^{\text{cascade}}] = 1 + \pi\, c_{gen}
$$

**Worked example.** Use the trigger rate $\pi = 3356/28058 = 0.1196$ *(paper: 11.96%)*, which is about 12%.

- Unified, $k=6$: $0.375 + 0.1196\times0.625 = 0.375 + 0.0748 = 0.4498$.
- Unified, $k=10$: $0.625 + 0.1196\times0.375 = 0.625 + 0.0449 = 0.6699$.
- Cascade with $c_{gen} = 1$ (an **assumption**; the paper does not give $c_{gen}$ in these units): $1 + 0.1196 = 1.1196$.
- Ideal gain over the cascade: $1.1196/0.4498 = 2.49\times$ at $k=6$ and $1.1196/0.6699 = 1.67\times$ at $k=10$.

At the deployed gate the fire rate is $\pi = 3682/28058 = 0.1312$ *(paper: 3,682 hints emitted)*: unified costs $0.457$ and $0.674$; the cascade costs $1.131$ (with $c_{gen}=1$). Ratios: 2.48× and 1.68×.

![Expected cost against fire rate](/attachments/notes/proactive-assistant/pa3-cost-vs-rate.png)
*Figure 25. Expected cost per marker against the fire rate $\pi$. The lines are straight because the cost is linear in $\pi$. The unified lines are far below the cascade. [PDF](/attachments/notes/proactive-assistant/pa3-cost-vs-rate.pdf)*

**Why it matters here.** The expected gain is slightly **below** the silent-only $L/k$ (2.49 against 2.67), because triggered markers cost the full pass.

**Interview question.** *The gain depends on $c_{gen}$. How would you state the result without assuming it?* **Answer.** Write the cascade cost as $1 + \pi c_{gen}$ and say the unified model costs $\frac{k}{L} + \pi(1-\frac kL)$. The unified cost is always lower than the cascade cost as long as $c_{gen} \ge 0$, because $\frac{k}{L} + \pi(1 - \frac kL) < 1 \le 1 + \pi c_{gen}$ whenever $\pi < 1$ and $k < L$. The size of the gap then depends on $c_{gen}$, which the paper measures with wall-clock time.

## 14.5 Compared with what was measured

**What the paper measured** (a 4-core cloud CPU, batch size one, in ONNX Runtime with NF4 weights) *(paper, Table S5)*:

| | $k=6$ | $k=10$ |
|---|---|---|
| Gate, exit at $k$ | 1,793 ms | 2,909 ms |
| Gate, all 16 layers | 5,127 ms | 4,401 ms |
| Measured saving | $5127/1793 = 2.86\times$ | $4401/2909 = 1.51\times$ |
| Ideal $L/k$ | 2.67× | 1.60× |

*(The two "all 16 layers" times differ because they come from nested but different marker sets and different containers.)*

**Why $k=6$ is above ideal and $k=10$ is below.** The paper says the $k=6$ value is slightly above the ceiling because "the two timings use nested but different marker sets" (host and sample variance). For $k=10$ and for PyTorch there is a second effect, **fixed overhead per call** that does not shrink with fewer layers. A simple **background** model: time $= a + b\times(\text{layers run})$, with $a$ the fixed overhead and $b$ the per-layer time. Then

$$
\text{saving} = \frac{a + 16b}{a + k b} < \frac{16}{k} \quad\text{whenever } a > 0.
$$

*Check with PyTorch eager mode* (the paper notes its gate path runs one extra layer, so layers run $= k+1$): measured savings 1.75× ($k=6$) and 1.35× ($k=10$). Fit $a$ from $k=10$: $(a+16b)/(a+11b) = 1.35 \Rightarrow a = 3.29b$. Prediction for $k=6$: $(3.29+16)/(3.29+7) = 1.88$, against 1.75 measured. Roughly consistent, so a fixed overhead of about three layers' worth explains why PyTorch falls short of $16/(k+1)$ = 2.29 and 1.45. *(My reading; the paper says "its per-call overhead does not shrink with depth".)*

**End-to-end wall clock** *(paper, Table 4)*: unified $k=6$ takes 0.748 h and $k=10$ takes 1.005 h against 1.318 h for the matched 1B pipeline: $1.318/0.748 = 1.76\times$ and $1.318/1.005 = 1.31\times$. Against the 8B pipeline (2.551 h): $2.551/0.748 = 3.41\times$.

**Why it is below the ideal 2.49×.** The wall clock includes costs outside the prefill-layer model, such as decoding the 1 to 3 hint tokens and per-marker overheads. The paper does not break these down, so I cannot say how much each contributes.

**Interview question.** *Your formula predicts 2.49× but you report 1.76×. Is the formula wrong?* **Answer.** The formula is an ideal for prefill layer cost only. The measured wall clock also pays for decoding the hint and per-call overhead, and the wall clock is on an early-exit-only basis. The formula correctly predicts the **direction** and the **ordering** ($k=6$ cheaper than $k=10$). The ONNX gate-only measurement, 2.86× and 1.51×, matches the ideal 2.67× and 1.60× to within the noted variance.

## 14.6 Why a gate saves less when the generator is small (Amdahl-style derivation)

This is the paper's statement: "worth 4.39× against an 8B generator and 1.38× against a 1B one, because the gate itself takes 82% of the gated 1B pipeline's runtime." *(paper)* Here is the derivation, **reconstructed by me** and checked against the paper's 82%.

**Setup.** Let $T_{gen}$ be the time to run the generator on one marker and $T_{gate}$ the time for the gate. Without a gate you run the generator on all $N$ markers: $N T_{gen}$. With a gate you run the gate on all $N$ and the generator only on the fraction $\pi$ that fire: $N(T_{gate} + \pi T_{gen})$.

**Formula.** With $r = T_{gate}/T_{gen}$:

$$
S = \frac{N\,T_{gen}}{N(T_{gate} + \pi T_{gen})} = \frac{1}{r + \pi}
$$

Two limits: if the gate is free ($r \to 0$), $S \to 1/\pi = 28058/3682 = 7.62$ (this is the paper's 7.62× cut in generator calls). If the gate is as costly as the generator ($r = 1$), $S \approx 0.88 < 1$: gating **loses**.

**Worked example** *(solve for $r$ from the paper's savings)*, with $\pi = 0.1312$:

- 8B generator, $S = 4.39$: $r = 1/4.39 - 0.1312 = 0.2278 - 0.1312 = 0.0966$. Gate share of gated runtime $= r/(r+\pi) = 0.0966/0.2278 = 42\%$.
- 1B generator, $S = 1.38$: $r = 1/1.38 - 0.1312 = 0.7246 - 0.1312 = 0.5934$. Gate share $= 0.5934/0.7246 = 81.9\%$. **The paper reports 82%.** ✓ (This agreement is the check that the reconstruction is right.)

![Saving against r](/attachments/notes/proactive-assistant/pa4-amdahl-gate.png)
*Figure 26. The saving $S = 1/(r+\pi)$. The two red points are solved from the paper's measured savings. The dashed line is the ceiling $1/\pi$. [PDF](/attachments/notes/proactive-assistant/pa4-amdahl-gate.pdf)*

**A second consistency check** *(derived)*. The two solved values give $T_{gen}^{8B}/T_{gen}^{1B} = 0.5934/0.0966 = 6.1$. Predict the ratio of the two pipelines' runtimes: per-marker cost in units of $T_{gen}^{1B}$ is $0.5934 + 0.1312 = 0.7246$ for the 1B pipeline and $0.5934 + 0.1312\times6.14 = 1.40$ for the 8B pipeline. Ratio $= 1.93$. The paper's wall clocks give $2.551/1.318 = 1.94$. ✓

**Why it matters here.** It explains why the paper motivates one model instead of two: with a 1B generator the gate eats most of the runtime, so the remaining saving comes from making the gate cheaper, which early exit does.

**Interview question.** *When does a gate not pay off?* **Answer.** When $r + \pi \ge 1$, i.e. the gate costs as much as the generator would on the fraction you filter out. With $\pi = 0.13$ that needs $r \ge 0.87$. In the paper's setting $r = 0.59$ for a 1B generator, so gating still wins but only by 1.38×.

## 14.7 Check yourself

- Compute $E[c^{\text{unified}}]$ at $k = 10$ and $\pi = 0.2$. *($0.625 + 0.2\times0.375 = 0.70$.)*
- Which is bigger: $16/6$ or the average-case gain 2.49? Why? *($16/6$; triggered markers pay the full pass.)*
- What is the saving if the gate takes half as long as the generator ($r = 0.5$) and $\pi = 0.13$? *($1/0.63 = 1.59$.)*

Next: [[notes/proactive-assistant/15-deep-dive-metrics-calibration-losses|15. Deep dive: metrics, calibration and losses]]
