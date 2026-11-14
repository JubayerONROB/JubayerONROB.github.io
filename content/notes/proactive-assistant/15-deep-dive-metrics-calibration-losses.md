---
title: "15. Deep dive: metrics, calibration and losses"
date: 2026-11-14
tags:
  - notes
  - math
---

`math` · Part of the [[notes/proactive-assistant/index|Proactive Assistant study guide]]

**Builds on:** [[notes/proactive-assistant/4-training|4. Training: LoRA, 4-bit, losses]]; [[notes/proactive-assistant/6-evaluation-metrics|6. Evaluation metrics]]; [[notes/proactive-assistant/7-experiments-and-findings|7. Experiments and findings]]. **Previous:** [[notes/proactive-assistant/14-deep-dive-cost-model|14. The cost model]].

Basic symbols: [[notes/proactive-assistant/12-math-foundations|page 12]]. Everything marked *(paper)* comes from the paper. Definitions of ECE, MCE, Brier and AP are standard **background**; the paper reports the values but not the bin count.

## 15.1 Confusion matrix and the four counts

**Meaning.** For each marker compare the gate's decision with the reference label. The positive class is "trigger".

**Formula.** TP: fired and a trigger. FP: fired, not a trigger (**false alarm**). FN: quiet, but a trigger (**miss**). TN: quiet, not a trigger. $TP + FN = |\mathcal{T}|$ and $TN + FP = |\mathcal{N}|$ (the silence markers).

**Worked example** *(paper numbers, deployed Llama-3.2-1B gate)*. $|\mathcal{T}| = 3{,}356$, $|\mathcal{N}| = 24{,}702$, recall $0.8391$, hints emitted $3{,}682$.

1. $TP = 0.8391 \times 3356 = 2{,}816$.
2. $FN = 3356 - 2816 = 540$.
3. $FP = 3682 - 2816 = 866$ (emitted minus correct).
4. $TN = 24702 - 866 = 23{,}836$.

*(Derived from the paper's reported recall and emitted count. Check: $866/3682 = 23.5\%$ of hints are false alarms, matching the paper's "23.5%".)*

**Why it matters here.** All gate metrics are functions of these four numbers.

**Likely question.** *Which of the four is most costly in the product?* **Answer.** The paper treats FP and FN as different costs: a false alarm interrupts the conversation for everyone present, a miss leaves the wearer as they would be without the system. Which is worse is a deployment choice, so it reports gate quality against a false-alarm budget.

## 15.2 Precision, recall, false-alarm rate

**Formulas.**

$$
\text{precision} = \frac{TP}{TP + FP}, \qquad
\text{recall} = \frac{TP}{TP + FN}, \qquad
\text{FAR} = \frac{FP}{TN + FP}
$$

Precision asks "of what we fired, how much was right?" Recall asks "of what needed a hint, how much did we catch?" FAR asks "of the quiet moments, how many did we interrupt?"

**Worked example** *(from the counts above)*. Precision $= 2816/3682 = 0.7648$. Recall $= 2816/3356 = 0.8391$. FAR $= 866/24702 = 0.0351$. **These match the paper** (precision 0.7648, recall 0.8391, FAR 0.0351). ✓

**Precision depends on prevalence** (Bayes' rule, page 12): precision $= \dfrac{\text{TPR}\,\pi_+}{\text{TPR}\,\pi_+ + \text{FAR}\,(1-\pi_+)}$ where $\pi_+ = 0.1196$ is the trigger rate. With the same TPR and FAR but 50% triggers, precision would be 0.96, not 0.76.

![Precision against false-alarm rate](/attachments/notes/proactive-assistant/pa5-precision-prevalence.png)
*Figure 27. The same gate (recall 0.8391, FAR 3.51%) has precision 0.7646 on our corpus but would reach 0.96 on a balanced one. The curves are from Bayes' rule. [PDF](/attachments/notes/proactive-assistant/pa5-precision-prevalence.pdf)*

**Likely question.** *Why is FAR of 3.5% a lot, when it sounds small?* **Answer.** FAR divides by the 24,702 silence markers, a big denominator. 3.5% of that is 866 false alarms, compared with 2,816 correct firings. So nearly a quarter of hints are false alarms. The small-looking FAR hides a mid-size precision loss because positives are rare.

## 15.3 F1 and why it is a harmonic mean

**Formula.** $F_1 = \dfrac{2\cdot\text{precision}\cdot\text{recall}}{\text{precision}+\text{recall}}$. It simplifies to $F_1 = \dfrac{2\,TP}{2\,TP + FP + FN}$.

**Proof of the simplification.** With $P = \frac{TP}{TP+FP}$ and $R = \frac{TP}{TP+FN}$:

$$
2PR = \frac{2\,TP^2}{(TP+FP)(TP+FN)}, \qquad
P + R = \frac{TP\,(TP+FN) + TP\,(TP+FP)}{(TP+FP)(TP+FN)} = \frac{TP\,(2TP + FN + FP)}{(TP+FP)(TP+FN)}
$$

Dividing, the common denominator cancels and one $TP$ cancels: $F_1 = \dfrac{2TP}{2TP + FP + FN}$. $\blacksquare$

**Worked example.** $F_1 = 2\times2816 / (2\times2816 + 866 + 540) = 5632/7038 = 0.8002$. **The paper's gate F1 is 0.8002.** ✓

**Why harmonic and not arithmetic.** The harmonic mean is pulled toward the **smaller** of the two. With precision 1.0 and recall 0.1 the average is 0.55 but $F_1 = 0.18$. A gate that fires only once, correctly, cannot score well.

**Why it matters here.** F1 is the criterion used to pick $t$ on validation *(paper)*; it is called PA-F1.

**Likely question.** *Why not pick $t$ by accuracy?* **Answer.** With 88% silence, always saying "quiet" gives about 88% accuracy and 0 recall. F1 ignores TN, so it cannot be inflated by the large silent class.

## 15.4 AUROC: the probability a trigger outranks a silence

**Meaning.** The **ROC curve** plots recall against FAR as $t$ sweeps from 1 to 0. **AUROC** is the area under it.

**Formula and claim.** AUROC equals the probability that a randomly chosen trigger gets a higher score than a randomly chosen silence marker (ties count half):

$$
\text{AUROC} = \frac{1}{|\mathcal{T}||\mathcal{N}|}\sum_{i\in\mathcal{T}}\sum_{j\in\mathcal{N}}\Big(\mathbf{1}[p_i > p_j] + \tfrac12\mathbf{1}[p_i = p_j]\Big)
$$

**Sketch of why.** At threshold $t$ the point on the curve is $(\text{FAR}(t), R(t))$. Sweeping $t$ downward moves the curve right each time a negative is passed and up each time a positive is passed. The area under the curve counts, for each positive, the share of negatives still **below** it. That is the double sum above. *(Background; this is the Mann–Whitney identity.)*

**Worked example** *(toy)*. Trigger scores $\{0.9, 0.8, 0.55, 0.4\}$; silence scores $\{0.7, 0.5, 0.3, 0.2, 0.1, 0.05\}$. Count the pairs where the trigger wins: $0.9$ beats 6, $0.8$ beats 6, $0.55$ beats 5 (all but 0.7), $0.4$ beats 4 (0.3, 0.2, 0.1, 0.05). Total $= 21$ of $4\times6 = 24$ pairs, so AUROC $= 21/24 = 0.875$.

**Why it matters here.** It is threshold-free. It uses only the **ranking**, so it cannot tell you the right $t$, and it does not change under a monotone rescaling of the scores. A prompted LLM gate has AUROC 0.5773 on its 2,000-marker subsample *(paper)*, where 0.5 is chance.

**Likely question.** *Two models have equal AUROC. Are they equally good gates?* **Answer.** No. Equal ranking quality does not give equal calibration or equal operating points: they may need different thresholds, and one may have worse probabilities (page 13).

## 15.5 AUPRC and why it is used under class imbalance

**Meaning.** The **precision–recall curve** plots precision against recall as $t$ sweeps. **AUPRC** (average precision) is the area under it. A standard form:

$$
\text{AP} = \sum_{n} (R_n - R_{n-1})\, P_n
$$

where the sum goes over the thresholds that add a new positive, $R_n$ is the recall and $P_n$ the precision there. **A no-skill model has AUPRC equal to the prevalence** (here 0.1196), while a no-skill model has AUROC 0.5. *(Background.)*

**Worked example** *(same toy scores)*. Rank all 10 scores from high to low and track precision at each trigger:

| score | label | TP | FP | precision | recall |
|---|---|---|---|---|---|
| 0.90 | trigger | 1 | 0 | 1.000 | 0.25 |
| 0.80 | trigger | 2 | 0 | 1.000 | 0.50 |
| 0.70 | silence | 2 | 1 | 0.667 | 0.50 |
| 0.55 | trigger | 3 | 1 | 0.750 | 0.75 |
| 0.50 | silence | 3 | 2 | 0.600 | 0.75 |
| 0.40 | trigger | 4 | 2 | 0.667 | 1.00 |

Each trigger adds 0.25 of recall, so $\text{AP} = 0.25\,(1 + 1 + 0.75 + 0.667) = 0.854$. Prevalence in the toy is $4/10 = 0.4$, the no-skill level.

**Why imbalance matters.** AUROC divides false alarms by the **large** number of silence markers, so a flood of false alarms can look like a small FAR. In our corpus 866 false alarms are only 3.5% of 24,702 silences, yet they are 23.5% of all hints. Precision includes the false alarms in its **numerator-side** count and does not divide by the silences, so AUPRC is sensitive to exactly the cost that matters here. The paper reports AUPRC with every operating point; for the best gate, Llama-3.2-1B, it is 0.8883 *(paper, Table 2)*.

**Likely question.** *Why report AUPRC and not only AUROC?* **Answer.** With 11.96% positives, AUROC can stay high while precision is low, because TN dominates FAR. AUPRC does not use TN at all, so it reflects the rare-class performance that a user feels as false alarms.

## 15.6 Calibration: ECE, MCE, Brier

**Meaning.** A model is **calibrated** if, among the markers it scores about 0.8, about 80% are really triggers. This matters when the threshold is **adapted from user feedback**, because the system then uses the probability itself, not just the ranking *(paper)*.

**Formulas.** Cut $[0,1]$ into $B$ bins. For bin $b$ let $n_b$ be its size, $\text{conf}_b$ the mean predicted probability, and $\text{acc}_b$ the fraction that are true triggers.

$$
\text{ECE} = \sum_{b=1}^{B}\frac{n_b}{N}\,\big|\,\text{acc}_b - \text{conf}_b\,\big|, \quad
\text{MCE} = \max_b\,\big|\,\text{acc}_b - \text{conf}_b\,\big|, \quad
\text{Brier} = \frac1N\sum_{i}(p_i - y_i)^2
$$

$y_i \in \{0,1\}$ is the true label. ECE is the average gap, MCE is the worst gap, and the Brier score is the mean squared error of the probability.

**Worked example** *(toy: 10 predictions, 5 equal-width bins)*. $(p, y)$: (0.95,1) (0.90,1) (0.85,0) (0.80,1) (0.70,1) (0.40,0) (0.30,0) (0.20,1) (0.15,0) (0.05,0).

| bin | members | $\text{conf}_b$ | $\text{acc}_b$ | gap | weight $n_b/10$ |
|---|---|---|---|---|---|
| [0, 0.2) | 0.15, 0.05 | 0.10 | 0/2 = 0.00 | 0.10 | 0.2 |
| [0.2, 0.4) | 0.30, 0.20 | 0.25 | 1/2 = 0.50 | 0.25 | 0.2 |
| [0.4, 0.6) | 0.40 | 0.40 | 0/1 = 0.00 | 0.40 | 0.1 |
| [0.6, 0.8) | 0.70 | 0.70 | 1/1 = 1.00 | 0.30 | 0.1 |
| [0.8, 1.0] | 0.95, 0.90, 0.85, 0.80 | 0.875 | 3/4 = 0.75 | 0.125 | 0.4 |

ECE $= 0.2(0.10) + 0.2(0.25) + 0.1(0.40) + 0.1(0.30) + 0.4(0.125) = 0.02 + 0.05 + 0.04 + 0.03 + 0.05 = 0.19$. MCE $= 0.40$. Brier $= (0.0025 + 0.01 + 0.7225 + 0.04 + 0.09 + 0.16 + 0.09 + 0.64 + 0.0225 + 0.0025)/10 = 1.78/10 = 0.178$.

**What the paper found** *(Table S4)*. RoBERTa-large (ASL recipe): AUPRC 0.8902 (the best), ECE 0.3036, MCE 0.4129, Brier 0.1378. Gemma-3-1B: AUPRC 0.8415, ECE 0.0425, MCE 0.2086, Brier 0.0472. Llama-3.2-1B: ECE 0.0909, Brier 0.0486. So the **best-ranking gate is the worst calibrated**, with ECE $0.3036/0.0425 = 7.1\times$ the best. The paper does not say why. A background hint: its training recipe uses focal loss with full fine-tuning, and losses that re-weight classes change the scale of the output probability (section 15.9), but this was not tested.

![Ranking against calibration](/attachments/notes/proactive-assistant/fig15-ranking-vs-calibration.png)
*The ranking-versus-calibration bars from Table S4 (this is also Figure 11 on [[notes/proactive-assistant/6-evaluation-metrics|page 6]]). [PDF](/attachments/notes/proactive-assistant/fig15-ranking-vs-calibration.pdf)*

**Why it matters here.** Deployment must "select on calibration, or calibrate post hoc and re-measure" *(paper)*.

**Likely question.** *Can a model have perfect AUROC and bad ECE?* **Answer.** Yes. Take any perfect ranking and apply $p \mapsto p^{3}$: the ranking and the AUROC do not change, but the probabilities no longer match the frequencies. This is exactly why the paper separates ranking (AUPRC) from probability quality (ECE, MCE, Brier).

## 15.7 Cross-entropy: derivation and gradient

**Meaning.** Cross-entropy is the **negative log-probability the model gives to the correct answer**. Minimizing it is **maximum likelihood**.

**Formula.** For a true class $y\in\{0,1\}$ and predicted trigger probability $p$, let $p_t = p$ if $y = 1$ and $p_t = 1-p$ if $y=0$ (the probability given to the true class):

$$
\text{CE} = -\log p_t = -\,y\log p - (1-y)\log(1-p)
$$

**Derivation from maximum likelihood.** If examples are independent, the likelihood of the labels is $\prod_i p_{t,i}$. Its log is $\sum_i \log p_{t,i}$. Maximizing that is minimizing its negative, the sum of cross-entropies.

**Gradient.** Let $p = \sigma(z)$ with logit $z$. Using $\sigma'(z) = \sigma(z)(1-\sigma(z))$:

$$
\frac{\partial\,\text{CE}}{\partial z} = -\frac{y}{p}\,p(1-p) + \frac{1-y}{1-p}\,p(1-p) = -y(1-p) + (1-y)p = p - y
$$

**The gradient with respect to the logit is just $p - y$**: prediction minus truth.

**Worked example.** Truth $y = 1$. If $p = 0.9$: $\text{CE} = -\ln 0.9 = 0.1054$ and gradient $0.9 - 1 = -0.1$ (small, nearly right). If $p = 0.1$: $\text{CE} = 2.3026$ and gradient $-0.9$ (large, wrong).

**Why it matters here.** The unified model's hint tokens use CE, and the gate uses a weighted/focal variant *(code in the repo)*.

**Likely question.** *Why does CE with softmax train well compared with squared error?* **Answer.** The logit gradient is $p-y$, which does not vanish when the model is confidently wrong. Squared error through a sigmoid has gradient $(p-y)\,p(1-p)$, which goes to 0 when $p$ saturates near 0 or 1 even if wrong. *(Background.)*

## 15.8 Class-weighted cross-entropy: what the optimum becomes

**Meaning.** Multiply the loss of a trigger by a weight $w$ so errors on the rare class cost more. In the repo, the gate uses weights $(1.0, 2.5)$ for (silence, trigger) *(code)*. The paper's sensitivity study varies the trigger weight $\alpha$ from 1 to 4.

**Formula.** Suppose for an input $x$ the **true** probability of a trigger is $q$. The expected weighted loss for a predicted $p$ is

$$
\mathcal{L}(p) = -\,w\,q\,\log p \;-\; (1-q)\log(1-p)
$$

Set the derivative to zero: $-\dfrac{wq}{p} + \dfrac{1-q}{1-p} = 0 \;\Rightarrow\; wq(1-p) = (1-q)\,p \;\Rightarrow\; p^\star = \dfrac{wq}{wq + 1 - q}$.

**Worked example.** True $q = 0.3$.

- $w = 1$: $p^\star = 0.3/(0.3+0.7) = 0.30$ (calibrated).
- $w = 2.5$: $p^\star = 0.75/(0.75 + 0.7) = 0.517$.
- $w = 4$: $p^\star = 1.2/(1.2 + 0.7) = 0.632$.

A $q = 0.5$ example sits at $p^\star = w/(w+1)$: $0.714$ for $w = 2.5$ and $0.80$ for $w = 4$.

**Meaning of this result.** Weighting **inflates the scores**: the model's output is no longer the true probability. Firing when the truth reaches 0.5 now corresponds to $p \ge 0.714$ (for $w = 2.5$). So a weighted model needs a different threshold, and its probabilities are not calibrated.

![Loss shapes](/attachments/notes/proactive-assistant/pa6-loss-shapes.png)
*Figure 28. (a) The focal factor $(1-p_t)^\gamma$ shrinks the loss on easy examples. (b) A class weight $w$ moves the loss-minimizing score upward. Both are plots of formulas, not measured data. [PDF](/attachments/notes/proactive-assistant/pa6-loss-shapes.pdf)*

**Why it matters here.** The threshold sweep on validation (page 13) can absorb a pure shift like this. The paper's result, that raising the trigger weight from $\alpha = 1$ to $4$ **costs −0.0278 F1** *(paper, Qwen2.5-0.5B, $p_{holm} < 0.001$)*, is therefore not explained by the shift alone. See the next section.

**Likely question.** *If weighting only shifts the scores, why does $\alpha = 4$ hurt F1 after you re-tune $t$?* **Answer.** The paper shows the effect but does not isolate the cause. A reasoned **hypothesis** (not tested in the paper): a larger weight makes the gradient on trigger examples bigger relative to silence examples, so training spends more of its capacity on fitting the (noisy, language-model-generated) trigger labels, and the ranking itself degrades. The shift part is harmless after threshold tuning; any remaining loss must come from changed training dynamics.

## 15.9 Focal loss: derivation and why $\gamma = 2$ hurt

**Formula.**

$$
\text{FL} = (1 - p_t)^{\gamma}\,\text{CE} = -(1-p_t)^{\gamma}\log p_t
$$

with focusing strength $\gamma \ge 0$ ($\gamma=0$ is plain CE). In the repo the gate uses $\gamma = 1.5$ and class weights $(1.0, 2.5)$, with $p_t$ recovered from the weighted CE *(code)*.

**Derivative with respect to $p_t$** (product rule):

$$
\frac{d\,\text{FL}}{d p_t} = \gamma(1-p_t)^{\gamma-1}\log p_t \;-\; \frac{(1-p_t)^{\gamma}}{p_t}
$$

**Worked example.**

| $p_t$ | CE | FL ($\gamma=1.5$) | FL ($\gamma=2$) | $\|dCE/dp_t\|$ | $\|dFL/dp_t\|$, 1.5 | $\|dFL/dp_t\|$, 2 |
|---|---|---|---|---|---|---|
| 0.9 | 0.1054 | 0.0033 | 0.0011 | 1.11 | 0.085 | 0.032 |
| 0.5 | 0.6931 | 0.2451 | 0.1733 | 2.00 | 1.44 | 1.19 |
| 0.1 | 2.3026 | 1.9660 | 1.8651 | 10.00 | 11.81 | 12.24 |

Reading: for an easy example ($p_t = 0.9$) focal loss with $\gamma=1.5$ cuts the loss by $0.1054/0.0033 = 32\times$ and the gradient by 13×. For a very hard example ($p_t = 0.1$), the focal gradient is **larger** than CE's (11.8 against 10), because the derivative of the factor $(1-p_t)^\gamma$ adds to it.

**What the paper found** *(Table S2, Qwen2.5-0.5B, PA-F1)*:

| $\gamma$ | 0 | 1.0 | 1.5 | 2.0 | 3.0 |
|---|---|---|---|---|---|
| F1 | 0.7873 | 0.7856 | 0.7799 | 0.7563 | 0.7737 |
| $p_{holm}$ vs $\gamma=0$ | – | 1.000 | 0.551 | $<0.001$ | 0.036 |

So $\gamma \in \{0, 1, 1.5\}$ are statistically the same, but $\gamma = 2$ costs $-0.0310$ F1 (and $\gamma=3$ costs $-0.0136$, not monotone). Also $\alpha$ from 1 to 4 costs $-0.0278$. On Llama-3.2-1B, focal $\gamma = 1.5$ is 0.7926 against 0.8052 for plain CE ($p_{holm} = 0.117$, not significant) *(paper)*. The paper's conclusion: "moderate reweighting is harmless, aggressive reweighting hurts, and neither explains the ASL recipe's lead."

**Why it hurts: my reading, not tested in the paper** *(background reasoning)*. Focal loss concentrates the gradient on **hard** examples. Here the trigger labels were produced by a language model reading synthetic dialogue, so the hardest examples may be the **noisiest or mislabelled** ones. Raising $\gamma$ (or the trigger weight) pushes training toward fitting them, which can hurt generalization. The table above shows the focal gradient at a hard example growing with $\gamma$ (11.8 at 1.5, 12.2 at 2.0), while the gradient at easy examples shrinks to almost nothing, so the effective training set becomes smaller and noisier.

**Why it matters here.** It justifies using plain or mildly weighted CE and not tuning the loss further: the recipe's lead is not from the loss.

**Likely question.** *Why did you keep $\gamma = 1.5$ if plain CE was as good?* **Answer.** The ablations show no alternative to plain cross-entropy is significantly better (closest $p_{holm} = 0.117$), and the focal setting was inherited unchanged so the exit-depth sweep measures depth and not an incidental hyperparameter change *(code comment, repo)*. The honest summary is that the loss is not the mechanism.

## 15.10 Check yourself

- From $TP = 2816$, $FP = 866$, $FN = 540$ compute F1. *(0.8002.)*
- If scores are cubed, which of AUROC, ECE, the best $t$ change? *(AUROC no; ECE and $t$ yes.)*
- Compute the weighted-CE optimum for $q=0.2$, $w=4$. *($0.8/(0.8+0.8) = 0.50$.)*

Next: [[notes/proactive-assistant/16-deep-dive-model-lora-quantization|16. Deep dive: the model, LoRA and quantization]]
