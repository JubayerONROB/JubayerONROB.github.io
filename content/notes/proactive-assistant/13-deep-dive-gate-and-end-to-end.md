---
title: "13. Interview deep dive: gate and end-to-end score"
date: 2026-11-14
tags:
  - notes
  - math
  - interview
---

`math` `interview` · Part of the [[notes/proactive-assistant/index|Proactive Assistant study guide]]

**Builds on:** [[notes/proactive-assistant/1-the-task-and-the-gate|1. The task and the gate]]; [[notes/proactive-assistant/5-early-exit-and-unified-decoder|5. Early exit and the unified decoder]]; [[notes/proactive-assistant/6-evaluation-metrics|6. Evaluation metrics]]; [[notes/proactive-assistant/7-experiments-and-findings|7. Experiments and findings]]; [[notes/proactive-assistant/10-deployment-and-limits|10. Deployment and limits]]. **Previous:** [[notes/proactive-assistant/12-math-foundations|12. Math foundations]].

Symbols: see [[notes/proactive-assistant/12-math-foundations|page 12]]. This page derives Equations (1), (2), (3) and the monotonicity result.

## 13.1 Equation (1): the gate

**Meaning.** The gate model gives each silence marker $i$ a score $p_i \in [0,1]$. We speak only if the score reaches a threshold $t$.

**Formula.**

$$
g_i(t) = \mathbf{1}[\,p_i \ge t\,] \tag{1}
$$

$i$ is the marker index. $p_i$ is the gate score. $t$ is the threshold. $g_i \in \{0,1\}$, with 1 meaning "fire".

**Worked example.** Scores $p = (0.62, 0.91, 0.10)$ and $t = 0.60$ give $g = (1, 1, 0)$. With $t = 0.95$ they give $g = (0,0,0)$.

**Why it matters here.** It is the only place where a number becomes an action. A false alarm interrupts, and a miss leaves the wearer alone *(paper)*.

**Interview question.** *Why a threshold and not argmax of the two softmax outputs?* **Answer.** The argmax is the special case $t = 0.5$. Triggers are only 11.96% of markers and a false alarm costs more than a miss, so the best operating point is rarely 0.5. A threshold lets you pick the point on the false-alarm budget. The paper's selected thresholds range from 0.13 to 0.60 *(paper, Table 2)*.

### The threshold sweep

**Meaning.** We try every $t \in \{0.01, 0.02, \ldots, 0.99\}$ (99 values) on the **validation** split, keep the $t$ with the highest F1, and **report on test** with the same trained weights *(paper)*.

**Formula.** $t^\star = \arg\max_{t \in \{0.01,\ldots,0.99\}} F_1^{\text{val}}(t)$.

**Worked example** *(toy)*. If validation F1 is 0.70, 0.78, 0.80, 0.79 at $t = 0.4, 0.5, 0.6, 0.7$, then $t^\star = 0.6$ (the largest). Test F1 is then computed once at 0.6.

**Why it matters here.** Selecting on validation instead of test costs a mean of 0.0016 F1 (at most 0.0041) over 21 systems *(paper)*. Validation has 26,410 markers at 12.81% trigger rate, disjoint from test by dialogue *(paper)*. The cascade's Llama-3.2-1B gate gets $t = 0.60$ and F1 0.8002 *(paper)*.

**Interview question.** *Why not tune $t$ on test?* **Answer.** Then the test score would be optimistically biased: you would have picked the best of 99 noisy numbers on the data you report on. The paper audits this for RoBERTa: the optimism of its selected threshold is 0.0033 F1 on average and 0.0079 at the 95th percentile *(paper)*.

### Why $t$ is recalibrated per model

**Meaning.** A threshold is not a property of the task. It is a property of **how one model spreads its scores**.

**Formula.** The false-alarm rate at threshold $t$ is the share of **negative** examples that score at least $t$:

$$
\mathrm{FAR}(t) = \frac{1}{|\mathcal{N}|}\sum_{i\in\mathcal{N}} \mathbf{1}[\,p_i \ge t\,]
$$

$\mathcal{N}$ is the set of silence markers. Hence the threshold for a budget $\beta$ is a **quantile** of the negative scores: $t_\beta = $ the $(1-\beta)$-quantile of $\{p_i : i\in\mathcal{N}\}$.

**Worked example** *(toy)*. 20 negative scores of model A. A 15% budget allows 3 of 20 false alarms, so $t_A$ is the 3rd-largest score: 0.30. Model B is a monotone transform of A, $p' = \sqrt{p}$. It has the **same ranking and the same AUROC**, but its 3rd-largest score is $\sqrt{0.30} = 0.55$. So $t_B = 0.55 \ne t_A$.

![Threshold is a quantile](/attachments/notes/proactive-assistant/pa8-threshold-quantile.png)
*Figure 22. Toy data. The threshold that gives a false-alarm budget is a quantile of the negative scores, so two models with the same ranking need different thresholds. [PDF](/attachments/notes/proactive-assistant/pa8-threshold-quantile.pdf)*

**Why it matters here** *(paper)*. At a 2% false-alarm budget the threshold ranges over $0.205$–$0.725$ across six candidates (3.5×). Gemma-3-270M needs $t = 0.205$ and loses 28.0 F1 points if run at another model's operating point. Gemma-3-1B has selected $t = 0.24$ while Llama-3.2-1B has $0.60$.

**Interview question.** *If two models have equal AUROC, why can their thresholds differ?* **Answer.** AUROC only uses the **ranking** of scores. Any increasing transform of the scores keeps the ranking and the AUROC but moves every threshold. So thresholds must be re-chosen per model on held-out data.

**Decision-theory extra** *(background)*. If a false alarm costs $c_{FP}$ and a miss costs $c_{FN}$, the cost-minimizing rule on a **calibrated** probability is to fire when $p \ge c_{FP}/(c_{FP}+c_{FN})$. With equal costs that is 0.5. With a miss costing 3 times a false alarm: $1/(1+3) = 0.25$. With a false alarm costing 3 times a miss: $3/4 = 0.75$. This is why the paper calls the budget "a deployment decision".

## 13.2 Equation (2): end-to-end exact match and precision

**Meaning.** Score the **two decisions together**. A trigger that the gate suppresses scores zero. A hint emitted at a silent moment counts against precision.

**Formula.** Let $\mathcal{T}$ be the reference triggers. Let $m_i = \mathbf{1}[h_i = h_i^*]$ be 1 if the generated hint $h_i$ equals the reference hint $h_i^*$ exactly.

$$
EM_{e2e} = \frac{1}{|\mathcal{T}|}\sum_{i\in\mathcal{T}} g_i\, m_i, \qquad
P_{e2e} = \frac{\sum_{i\in\mathcal{T}} g_i\, m_i}{\sum_{i} g_i} \tag{2}
$$

The sum $\sum_i g_i$ in the denominator runs over **all** markers, so it counts every emitted hint, false alarms included.

**Worked example** *(toy: 10 markers, made-up scores)*. $t = 0.5$. Reference triggers $\mathcal{T} = \{2, 5, 7, 9\}$. Suppose the generator, if called, would be exact at markers 2, 5 and 9 but not at 7.

![Toy 10 markers](/attachments/notes/proactive-assistant/pa1-toy-markers.png)
*Figure 23. Toy example with ten markers. Marker 1 is a false alarm, marker 5 is a miss, markers 2 and 9 are correct hints, and marker 7 is a wrong hint. [PDF](/attachments/notes/proactive-assistant/pa1-toy-markers.pdf)*

Step by step:

1. Gate: $g = 1$ where $p_i \ge 0.5$: markers 1, 2, 7, 9. So $\sum_i g_i = 4$.
2. Marker 5 is a trigger with $p = 0.45 < 0.5$, so $g_5 = 0$. A **miss**: it contributes $g_5 m_5 = 0$.
3. Marker 1 has $g_1 = 1$ but is not a trigger. A **false alarm**: it is in the denominator of $P_{e2e}$ but not in the numerator.
4. Marker 7: $g_7 = 1$, trigger, but the hint is wrong, $m_7 = 0$.
5. Numerator: $g_2m_2 + g_5m_5 + g_7m_7 + g_9m_9 = 1 + 0 + 0 + 1 = 2$.
6. $EM_{e2e} = 2/4 = 0.50$. $P_{e2e} = 2/4 = 0.50$.

**Why it matters here.** Stage-wise generation scores assume a perfect gate, so they overstate. Behind the real gate at its deployed point, $EM_{e2e} = 0.2619$ and $P_{e2e} = 0.2387$ *(paper)*. Check with counts: $P_{e2e}\times 3682 = 879$ correct hints, and $EM_{e2e}\times 3356 = 879$. Same numerator, as Equation (2) requires. ✓

**Interview question.** *Why is $P_{e2e}$ so low (0.2387) when gate precision is 0.7648?* **Answer.** $P_{e2e}$ needs **two** things to hold at once: the gate fired at a true trigger (probability about 0.76) and the generator got the hint exactly right (about 0.31 of forwarded triggers). Roughly $0.7648\times 0.312 = 0.2387$. ✓ *(My arithmetic.)* The generator's exact-match rate is the bottleneck, not the gate.

## 13.3 Equation (3): the factorization $EM_{e2e} = R\cdot EM_{fwd}$

**Meaning.** End-to-end exact match is the gate's recall times the exact-match rate on the triggers the gate forwards.

**Formula.** Define

$$
R = \frac{1}{|\mathcal{T}|}\sum_{i\in\mathcal{T}} g_i, \qquad
EM_{fwd} = \frac{\sum_{i\in\mathcal{T}} g_i m_i}{\sum_{i\in\mathcal{T}} g_i} \tag{3}
$$

$R$ is the **recall of the gate**: the share of triggers it lets through. $EM_{fwd}$ is the exact-match rate **among the triggers it let through**.

**Proof.** Assume $\sum_{i\in\mathcal{T}} g_i > 0$ (at least one trigger is forwarded). Then

$$
R \cdot EM_{fwd}
= \frac{\sum_{i\in\mathcal{T}} g_i}{|\mathcal{T}|}\cdot\frac{\sum_{i\in\mathcal{T}} g_i m_i}{\sum_{i\in\mathcal{T}} g_i}
= \frac{\sum_{i\in\mathcal{T}} g_i m_i}{|\mathcal{T}|}
= EM_{e2e}. \qquad\blacksquare
$$

The factor $\sum_{i\in\mathcal{T}} g_i$ cancels top and bottom. If it is 0, then every $g_im_i = 0$ and $EM_{e2e} = 0$ too, so the identity holds with the convention $EM_{fwd}=0$.

**Worked example** *(toy, Figure 23)*. $R = 3/4 = 0.75$ (markers 2, 7, 9 forwarded out of 4). $EM_{fwd} = 2/3 \approx 0.667$. Product: $0.75 \times 0.667 = 0.50 = EM_{e2e}$. ✓

**Worked example** *(paper numbers)*. Deployed gate recall $R = 0.8391$ and $EM_{e2e} = 0.2619$. So $EM_{fwd} = 0.2619/0.8391 = 0.3121$. This is **above** the oracle ceiling 0.2971. *(My derived number.)* One reading: the triggers the gate lets through are, on average, a little easier for the generator than the ones it suppresses. The paper does not state this, so treat it as an interpretation.

**Why it matters here.** It separates the two failure sources: how many triggers the gate loses ($R$) and how good the generator is on what it receives ($EM_{fwd}$).

**Interview question.** *Is $EM_{fwd}$ the same as the oracle-gate score?* **Answer.** No. The oracle forwards **every** trigger. $EM_{fwd}$ averages only over the triggers the real gate forwards. They coincide only if the gate's forwarded set is a random sample of the triggers, or if $R = 1$.

## 13.4 Monotonicity: $EM_{e2e}$ cannot rise when $t$ rises

**Claim.** If $t_1 \le t_2$ then $EM_{e2e}(t_2) \le EM_{e2e}(t_1)$.

**Proof.**

1. For a fixed marker, $g_i(t) = \mathbf{1}[p_i \ge t]$. If $t_1 \le t_2$ and $p_i \ge t_2$ then $p_i \ge t_1$. So $g_i(t_2) = 1 \Rightarrow g_i(t_1) = 1$, that is $g_i(t_2) \le g_i(t_1)$.
2. The hint exactness $m_i$ does **not depend on $t$**. The generator reads the same dialogue and profile whatever $t$ is. (In the unified model the hint comes from the same pass, independent of $t$ as well.)
3. Each term $g_i(t)m_i$ is therefore non-increasing in $t$, because $m_i \ge 0$.
4. A sum of non-increasing terms, divided by the constant $|\mathcal{T}|$, is non-increasing. $\blacksquare$

**Same argument for recall.** $R(t)$ is also non-increasing. **It does not hold for $P_{e2e}$**: the denominator $\sum_i g_i$ also falls. If false alarms drop faster than correct hints, precision rises.

**Worked example** *(toy sweep)*. Using the ten markers of Figure 23:

| $t$ | markers fired | numerator | $EM_{e2e}$ | $P_{e2e}$ |
|---|---|---|---|---|
| 0.40 | 1, 2, 5, 7, 9 | 3 | 0.75 | 0.60 |
| 0.50 | 1, 2, 7, 9 | 2 | 0.50 | 0.50 |
| 0.80 | 2, 9 | 2 | 0.50 | 1.00 |
| 0.90 | 2 | 1 | 0.25 | 1.00 |
| 0.95 | none | 0 | 0.00 | undefined |

![Toy threshold sweep](/attachments/notes/proactive-assistant/pa2-toy-sweep.png)
*Figure 24. The same toy markers swept over $t$. $EM_{e2e}$ (red) only steps down, while $P_{e2e}$ can step up. The dotted red line is the oracle ceiling. [PDF](/attachments/notes/proactive-assistant/pa2-toy-sweep.pdf)*

### Why stage-wise scores are an "oracle-gate ceiling"

**Claim.** For any gate, $EM_{e2e} \le EM_{oracle}$, where $EM_{oracle} = \frac{1}{|\mathcal{T}|}\sum_{i\in\mathcal{T}} m_i$ (Equation (2) with $g_i = 1$ at every trigger).

**Proof.** Since $g_i \le 1$ and $m_i \ge 0$, we get $g_im_i \le m_i$ for each $i$. Sum over $\mathcal{T}$ and divide by $|\mathcal{T}|$. $\blacksquare$

**Worked example** *(toy)*: oracle $= (1+1+0+1)/4 = 0.75$. Real gate at $t=0.5$: $0.50$. *(paper)*: 1B generator, ceiling **0.2971**, behind the real gate **0.2619**. The gap, $0.2971 - 0.2619 = 0.0352$, is the cost of an imperfect gate. For the 8B generator it is $0.2947 \to 0.2548$; for Qwen2.5-7B $0.3579 \to 0.3084$.

**Why it matters here.** This is the first contribution. A generator paper that reports 0.2971 is quoting a number no deployment can reach. And because $EM_{e2e}$ can only fall as $t$ rises, a gate cannot "earn" exact match. It is justified only by **precision** (fewer false alarms: at a 1% false-alarm budget, $P_{e2e}$ rises to 0.3011 while $EM_{e2e}$ falls to 0.2122) and **compute** *(paper)*.

**Interview question.** *If $EM_{e2e}$ always falls with $t$, why use a gate at all?* **Answer.** Because the objective is not "serve every trigger". A false alarm interrupts the wearer and bystanders. The gate trades some recall for fewer false alarms and, more importantly, **cuts generator calls by 7.62×** ($28058/3682$) *(paper)*. EM alone would say "always fire", which is why the paper reports $P_{e2e}$ beside it and never reads $EM_{e2e}$ alone.

## 13.5 Check yourself

- Prove $EM_{e2e} \le R$. *(Since $m_i\le 1$, each $g_im_i \le g_i$, so $EM_{e2e}\le \frac1{|\mathcal{T}|}\sum g_i = R$.)*
- In the toy example, what is the false-alarm rate at $t=0.5$? *(One false alarm, marker 1, among 6 silence markers: $1/6 = 0.167$.)*
- Which of $R$, $EM_{e2e}$, $P_{e2e}$ can go **up** when $t$ goes up? *(Only $P_{e2e}$.)*

Next: [[notes/proactive-assistant/14-deep-dive-cost-model|14. Deep dive: the cost model]]
