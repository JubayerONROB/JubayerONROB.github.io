---
title: "17. Interview deep dive: generation metrics and statistics"
date: 2026-11-14
tags:
  - notes
  - math
  - interview
  - statistics
---

`math` `statistics` `interview` · Part of the [[notes/proactive-assistant/index|Proactive Assistant study guide]]

Part A covers the three text-scoring metrics. Part B covers the statistics behind every "significant", "tie" and "level" in the paper. Definitions are standard **background**; numbers marked *(paper)* are from the paper; toy examples are made up.

# Part A. Generation metrics

## 17.1 Exact match

**Meaning.** The hint counts as right only if it equals the reference hint exactly.

**Formula.** $m_i = \mathbf{1}[\,h_i = h_i^*\,]$. Exact match over a set $S$ of markers is $\frac1{|S|}\sum_{i\in S} m_i$.

**Worked example.** Reference "dance performance". Hint "dance performance": $m=1$. Hint "dance show": $m = 0$ (a near-synonym counts as wrong). Hint "the dance performance": $m = 0$.

**Why it matters here.** It is the primary automatic metric because it is the only one with a defensible **end-to-end form**: a suppressed trigger has no string to score, and "no hint" is unambiguously not an exact match. A BERTScore of zero would be an invented convention *(paper)*. It is a **strict lower bound** on usefulness.

**Interview question.** *Why keep a metric you call a lower bound?* **Answer.** Because only EM extends cleanly to Equation (2). The paper then shows graded metrics and LlamaPIE's native judge track human uptake more closely (section 17.10), so EM is the end-to-end tool and the others are the stage-wise tools.

## 17.2 BERTScore

**Meaning.** Compare **meaning**, not letters. Each word is turned into a context-aware vector by a language model (the paper uses roberta-large). Each word of one text is matched to its most similar word of the other.

**Formula.** For candidate tokens $c_a$ and reference tokens $r_b$ with unit-length vectors, using cosine similarity $\cos(c_a, r_b) = c_a\cdot r_b$:

$$
P = \frac{1}{|c|}\sum_{a}\max_{b}\ c_a\cdot r_b, \qquad
R = \frac{1}{|r|}\sum_{b}\max_{a}\ c_a\cdot r_b, \qquad
F = \frac{2PR}{P+R}
$$

The paper uses `idf=False` (no extra weight for rare words) and reports the **raw** score and a **rescaled** one. Rescaling uses a baseline $b$ (the typical score of unrelated text): $s_{resc} = \dfrac{s - b}{1 - b}$. *(Standard form, background.)*

**Worked example** *(toy 2-D unit vectors)*. dance $= (1,0)$, show $= (0.8,0.6)$, performance $= (0.6,0.8)$. Candidate "dance show", reference "dance performance".

- $\cos(\text{dance},\text{dance}) = 1$; $\cos(\text{dance},\text{performance}) = 0.6$; $\cos(\text{show},\text{dance}) = 0.8$; $\cos(\text{show},\text{performance}) = 0.48 + 0.48 = 0.96$.
- $P$: dance $\to \max(1, 0.6) = 1$; show $\to \max(0.8, 0.96) = 0.96$. $P = (1 + 0.96)/2 = 0.98$.
- $R$: dance $\to 1$; performance $\to \max(0.6, 0.96) = 0.96$. $R = 0.98$. $F = 0.98$.
- Illustrative rescale with $b = 0.70$: $(0.98 - 0.70)/0.30 = 0.933$.

So a near-synonym scores high on BERTScore but zero on exact match.

**Why rescale** *(paper)*. Among the memory-only baselines the raw scores span only 0.012, but rescaling moves every score by about 0.70, which is 57 times that spread. Hence rescaled values are reported beside the raw ones. With the profile the rescaled BERTScore is 0.57 and without it 0.35 *(paper)*.

**Interview question.** *What does BERTScore miss?* **Answer.** It rewards topical similarity, so a plausible but wrong word can score high. In the paper the "hallucination" class exists for exactly that. It also depends on the embedding model and a baseline, which is why the scale is rescaled.

## 17.3 ROUGE-1

**Meaning.** Count shared **single words** between hint and reference.

**Formula.** With overlap count $o$ (words in common, counting multiplicity at most as often as in both), candidate length $|c|$ and reference length $|r|$:

$$
P_1 = \frac{o}{|c|}, \quad R_1 = \frac{o}{|r|}, \quad F_1 = \frac{2P_1R_1}{P_1+R_1}
$$

**Worked example.** "dance show" vs "dance performance": $o = 1$, $P_1 = R_1 = F_1 = 0.5$. "the dance performance" vs "dance performance": $o = 2$, $P_1 = 2/3$, $R_1 = 1$, $F_1 = 0.8$.

**Why it matters here.** It rewards partial overlap that exact match gives zero for. With the profile ROUGE-1 is 0.48 and without it 0.13 *(paper)*. (The paper does not say whether this is the F, P or R form; the standard $F_1$ is shown here.)

**Interview question.** *Why can ROUGE-1 and EM disagree?* **Answer.** "the dance performance" has EM 0 but ROUGE-1 F 0.8. Any extra or missing word kills EM and only dents ROUGE-1.

# Part B. Statistics

## 17.4 Paired versus unpaired tests

**Meaning.** A **paired** comparison tests two systems on the **same items** and uses the item-by-item differences. An **unpaired** one treats the two sets of scores as independent samples. Pairing removes the variation that comes from some items being harder than others.

**Worked example** *(toy)*. System A is right on 80 of 100 items and B on 70 of 100. Unpaired: standard error of the difference $= \sqrt{0.8\cdot0.2/100 + 0.7\cdot0.3/100} = 0.0608$; $z = 0.10/0.0608 = 1.64$, two-sided $p = 0.10$ (not significant). Paired: suppose both right on 65, only A right on 15, only B right on 5, both wrong on 15 (same 80 and 70). Only the 20 discordant items matter: McNemar $\chi^2 = (15 - 5)^2/20 = 5.0$, $p = 0.025$ (significant). Same data totals, a different conclusion.

**Why it matters here.** The paper says a single judge scoring the same items twice agrees with itself at $r = 0.672$ and "does not resolve a 6.3-point exact-match gap between two systems that a **paired test** resolves at $p < 0.001$" *(paper)*.

**Interview question.** *When is paired not applicable?* **Answer.** When the two systems were not run on the same items, or when you only have aggregate scores. The paper cannot test against LlamaPIE's reported numbers because its per-marker predictions are unavailable *(paper)*.

## 17.5 McNemar's test

**Meaning.** Compare two classifiers on the same items using only the items where they **disagree**.

**Formula.** Make the 2×2 table. $b$ is the count where only A is right and $c$ the count where only B is right.

| | B right | B wrong |
|---|---|---|
| **A right** | $a$ (both right) | $b$ |
| **A wrong** | $c$ | $d$ (both wrong) |

Under "no difference" every disagreement is equally likely to favour A or B, so $b \sim \text{Binomial}(b+c,\ \tfrac12)$. The **exact two-sided $p$-value** is

$$
p = 2\sum_{j=0}^{\min(b,c)}\binom{b+c}{j}\left(\tfrac12\right)^{b+c} \quad(\text{capped at }1)
$$

For large $b+c$ the Binomial is close to a normal with mean $(b+c)/2$ and variance $(b+c)/4$, so $z = \dfrac{b - c}{\sqrt{b+c}}$ and $z^2 = \chi^2 = \dfrac{(b-c)^2}{b+c}$, with one degree of freedom. Items where both are right or both wrong carry **no** information about which is better.

**Worked example** *(toy: 100 items, $a = 70$, $b = 12$, $c = 4$, $d = 14$)*.

1. Exact: $n = 16$, $\min = 4$. $P(X\le4) = (1 + 16 + 120 + 560 + 1820)/65536 = 2517/65536 = 0.0384$. Two-sided: $2\times0.0384 = 0.0768$.
2. Chi-square: $(12-4)^2/16 = 4.0$, $p = 0.0455$.
3. With a continuity correction (a standard fix for small counts): $(|b-c|-1)^2/(b+c) = 49/16 = 3.06$, $p = 0.080$.

At 5%, the chi-square form says "significant" and the exact test says "not". With only 16 discordant pairs the exact test is the honest one. A second example: $b = 9$, $c = 7$ gives exact $p = 0.80$, chi-square $0.25$ with $p = 0.62$. Clear tie.

**Why it matters here** *(paper)*. 1B-gate-plus-1B-generator against 1B-gate-plus-8B-generator end to end: $p = 0.338$ (a tie on exact match). At the oracle-gate stage: $p = 0.79$. Removing the memory profile: $p<0.001$. A mismatched profile against no profile: $p = 0.343$ (indistinguishable). The RoBERTa-large versus Llama-3.2-1B gate comparison: $p_{holm} = 0.0060$ (McNemar, corrected).

**Interview question.** *Why can't I use a chi-square test of independence on the 2×2 table?* **Answer.** The two classifiers are evaluated on the same items, so the rows and columns are dependent by construction. McNemar's test conditions on that pairing and only looks at the discordant cells.

## 17.6 Multiple comparisons: Bonferroni and Holm

**Meaning.** If you run $m$ tests at level $\alpha = 0.05$, the chance of at least one false positive is far above 5%. A **correction** controls the **family-wise error rate (FWER)**, the chance of any false positive.

**Bonferroni.** Test each at $\alpha/m$ (or multiply each $p$ by $m$). *Proof* (union bound): $P(\text{any false rejection}) \le \sum_{\text{true nulls}} P(p_i\le\alpha/m) \le m_0\cdot\alpha/m \le \alpha$. $\blacksquare$

**Holm (step-down).** Sort $p_{(1)}\le\dots\le p_{(m)}$. For $j = 1,2,\dots$ reject $H_{(j)}$ if $p_{(j)} \le \dfrac{\alpha}{m - j + 1}$, and stop at the first failure. *Proof sketch:* let $m_0$ be the number of true nulls. A false rejection requires the smallest true-null $p$-value to be rejected. Its rank $j$ is at most $m - m_0 + 1$, so its threshold $\alpha/(m-j+1)\le\alpha/m_0$. Then $P(\text{error})\le m_0\cdot\alpha/m_0 = \alpha$ by the union bound. $\blacksquare$ Holm controls FWER at least as well as Bonferroni and is never less powerful.

**Worked example** *(toy: $m=4$, $\alpha = 0.05$, raw $p = 0.001, 0.012, 0.016, 0.040$)*.

| rank | raw $p$ | Holm threshold $\alpha/(m-j+1)$ | Holm decision | Bonferroni adj. $= 4p$ | Holm adj. |
|---|---|---|---|---|---|
| 1 | 0.001 | 0.0125 | reject | 0.004 | 0.004 |
| 2 | 0.012 | 0.0167 | reject | 0.048 | 0.036 |
| 3 | 0.016 | 0.0250 | reject | 0.064 | 0.036 |
| 4 | 0.040 | 0.0500 | reject | 0.160 | 0.040 |

Holm rejects all four; Bonferroni (adjusted $p \le 0.05$) rejects only two. *(Holm adjusted $p$ is the running maximum of $(m-j+1)p_{(j)}$.)*

**Why it matters here** *(paper)*. Holm is applied "across all pairwise comparisons in the table" for the gate comparison, and across the 45 retrieval configurations (none beats the full profile). Bonferroni is used for the four non-inferiority tests of the human study, which makes their intervals **98.75%** wide: $\alpha = 0.05/4 = 0.0125$, confidence $1 - 0.0125 = 98.75\%$, critical value $z = 2.498$ instead of 1.96.

**Interview question.** *Why Holm and not Bonferroni?* **Answer.** Both control the family-wise error. Holm is uniformly more powerful because it uses the ordering of the $p$-values, and it needs no extra assumptions about dependence between tests.

## 17.7 The bootstrap and the dialogue (cluster) bootstrap

**Meaning.** The **bootstrap** estimates the uncertainty of a statistic by **resampling the data with replacement** and recomputing the statistic many times. The **percentile 95% CI** is the 2.5th to 97.5th percentile of those recomputed values.

**Why cluster.** Markers from one dialogue share a topic, a speaker and a memory profile, so they are **not independent**. Resampling single markers would give intervals that are too narrow. The **cluster bootstrap** resamples **whole dialogues**. *(Background: with $m$ items per cluster and within-cluster correlation $\rho$, the variance is inflated by the design effect $1 + (m-1)\rho$; for $m=10$, $\rho = 0.3$ that is 3.7.)*

**Worked example** *(toy)*. Five dialogues with (correct, total) hints: A (3,10), B (5,10), C (1,10), D (4,10), E (2,10). Overall: $15/50 = 0.30$. Draw 5 dialogues with replacement:

| resample | correct | total | rate |
|---|---|---|---|
| A, A, B, D, E | 17 | 50 | 0.34 |
| B, C, C, D, E | 13 | 50 | 0.26 |
| A, B, D, D, D | 20 | 50 | 0.40 |
| C, C, C, E, A | 8 | 50 | 0.16 |
| B, B, D, E, E | 18 | 50 | 0.36 |

The spread of these rates (SD $\approx 0.095$) is the bootstrap's estimate of the standard error. In practice you draw 1,000 or more resamples and take the percentiles.

**Why it matters here** *(paper)*. All intervals are "clustered by dialogue". Examples: profile effect $+0.0055\ [-0.0010,\ +0.0125]$ (includes zero); 8B with memory vs without: $+0.83\ [+0.48,\ +1.23]$ uptake; the unified $k=10$ gate over the memory-aware two-stage gate $+0.0183\ [+0.0106,\ +0.0259]$.

**Interview question.** *Why does clustering widen the interval?* **Answer.** Because 100 markers from 10 dialogues are less than 100 independent observations: markers in a dialogue are correlated, so the effective sample size is smaller. Resampling dialogues keeps that correlation inside each resample, so the estimate of variance is honest.

## 17.8 Noise floor

**Meaning.** The **noise floor** is the score difference you get between two trainings of the **same** configuration. A gap smaller than it cannot be told from luck.

**Value** *(paper)*: **0.0070 F1**, "the difference between two trainings of a nominally identical gate configuration. It comes from a single pair of runs." The other estimate is the three-seed SD of the unified gate: $0.0033$ at $k=6$ and $0.0029$ at $k=10$.

**Worked example.** The unified $k=6$ gate beats the separate gate by $0.8022 - 0.8002 = +0.0020$, less than 0.0070, so it is a **tie**. The $k=10$ gate leads by $0.8164 - 0.8002 = +0.0162$, more than 0.0070, so it **exceeds** the noise floor *(paper)*. Consistency check *(my arithmetic)*: if two runs each have SD $\sigma\approx0.003$, their difference has SD $\sigma\sqrt2\approx0.0044$, so 0.0070 is a plausible single draw, about 1.6 SD.

**Interview question.** *Is 0.0070 a reliable threshold?* **Answer.** Not strongly: it comes from one pair of runs, which the paper states. It is a reference band, not a confidence interval, and the paper backs it with the three-seed SDs.

## 17.9 Multiple seeds

**Meaning.** A **seed** fixes the random choices (initial values, data order). Different seeds give slightly different trained models. Several seeds estimate how much of a result is luck.

**Formula.** With $S$ seeds, mean $\bar x$ and sample SD $s$, the standard error of the mean is $s/\sqrt S$, and for the difference of two means $\sqrt{s_1^2/S + s_2^2/S}$.

**Worked example** *(paper numbers, treated as independent samples; my arithmetic)*. At step 21,703: $k=6$ mean $0.7846$ (SD 0.0033), $k=10$ mean $0.8022$ (SD 0.0029), 3 seeds each. Difference $= 0.0176$. Standard error $= \sqrt{0.0033^2/3 + 0.0029^2/3} = 0.00254$. So $t = 0.0176/0.00254 = 6.9$: the depth gap is far outside seed noise. Compared with a **single** run, $0.8002$ for the separate gate, the $k=10$ mean differs by $+0.0020$, which is within one SD, so a tie.

**Why it matters here.** Seed dispersion is measured at step 21,703 only, "since pooling it with a point estimate from another step would misstate it" *(paper)*. At the final checkpoint only one seed per depth exists, and the paper says so.

**Interview question.** *Why three seeds and not more?* **Answer.** The paper lists "most configurations were trained once" and no second-family or further-seed run as limitations. Three seeds give a rough SD, not a precise one, so conclusions rest on gaps being large against that SD.

## 17.10 Pearson correlation

**Meaning.** Pearson $r$ measures how closely two lists of numbers follow a straight line, from $-1$ to $+1$.

**Formula.** For paired values $(x_i, y_i)$ with means $\bar x, \bar y$:

$$
r = \frac{\sum_i (x_i-\bar x)(y_i-\bar y)}{\sqrt{\sum_i (x_i-\bar x)^2}\ \sqrt{\sum_i (y_i-\bar y)^2}}
$$

Geometrically, $r$ is the **cosine of the angle** between the two centered vectors. $r^2$ is the share of the variance of $y$ explained by a straight-line fit to $x$.

**Worked example** *(toy)*. $x = (1,2,3,4,5)$, $y = (2,1,4,3,5)$. $\bar x = 3$, $\bar y = 3$. Products of deviations: $(-2)(-1) + (-1)(-2) + 0\cdot1 + 1\cdot0 + 2\cdot2 = 2 + 2 + 0 + 0 + 4 = 8$. $\sum(x-\bar x)^2 = 10$ and $\sum(y-\bar y)^2 = 10$. $r = 8/\sqrt{10\cdot10} = 0.8$, $r^2 = 0.64$.

**Numbers from the paper** *(S7, Qwen2.5-7B, $n = 199$)*:

| comparison | $r$ | $r^2$ | reading |
|---|---|---|---|
| Rubric B vs Rubric C (two different reference-free judges), Qwen2.5-7B | 0.127 | 0.016 | share only 1.6% of variance |
| same on the 8B generator | 0.185 | 0.034 | |
| same on the 1B generator | 0.264 | 0.070 | |
| one judge scoring the same items twice | 0.672 | 0.452 | **self-agreement ceiling** |

So two LLM judges barely agree with each other ($r = 0.127$), while one judge agrees with itself at $0.672$. A **derived significance check** *(my arithmetic)*: $t = r\sqrt{n-2}/\sqrt{1-r^2} = 0.127\times14.04/0.992 = 1.80$, two-sided $p\approx0.07$, so even that small $r$ is borderline.

**Human correlation** *(Table 7b, 136 hints)*: native judge $r = 0.55$ (8B) and $0.67$ (1B); ROUGE-1 0.51 and 0.62; BERTScore 0.47 and 0.61; exact match 0.31 and 0.43. Only the orders matter: the native judge tracks people best, exact match worst. Some entries have $n<60$ and are marked with an asterisk in the paper.

**Interview question.** *What does a correlation of 0.31 between exact match and human uptake tell you?* **Answer.** $r^2 = 0.096$, so EM explains about 10% of the variance of human uptake. It carries signal but is a weak proxy, which is why EM is called a strict lower bound and the native judge is recommended.

## 17.11 Cohen's kappa (and Krippendorff's alpha)

**Meaning.** **Agreement beyond chance** between two raters labelling the same items.

**Formula.** Let $p_o$ be the observed agreement and $p_e$ the agreement expected by chance from the raters' own label frequencies:

$$
\kappa = \frac{p_o - p_e}{1 - p_e}
$$

$\kappa = 1$ is perfect, $0$ is chance level.

**Worked example** *(toy 100 items)*. Both say yes on 45, both no on 35, A yes/B no on 5, A no/B yes on 15. $p_o = (45+35)/100 = 0.80$. Rater A says yes on 50%, B says yes on 60%. $p_e = 0.5\times0.6 + 0.5\times0.4 = 0.30 + 0.20 = 0.50$. $\kappa = (0.80 - 0.50)/(1 - 0.50) = 0.60$.

**Numbers from the paper** *(S8, meeting corpus)*: a blind annotator relabelling the same cards agrees with their own earlier labels at $\kappa = 0.694$ (a **ceiling**); the behavioural proxy label agrees with that annotator at $\kappa = 0.361$, "about half of that ceiling" ($0.361/0.694 = 0.52$ ✓). *(The paper writes the symbol $\kappa$; for two raters and binary labels this is Cohen's $\kappa$, which is background.)*

**For the main human study** the paper uses **Krippendorff's ordinal $\alpha = 0.72$** on the 196 hints both annotators rated, because the rating scale is ordered 1 to 5. Its general form is $\alpha = 1 - D_o/D_e$, the observed disagreement over the disagreement expected by chance. *(Background.)*

**Interview question.** *Why kappa and not plain percent agreement?* **Answer.** If 90% of items are "no", two raters who always say "no" agree 90% of the time with no skill. Kappa subtracts that chance agreement.

## 17.12 Non-inferiority

**Meaning.** Sometimes you want to show a new system is **not worse than the old by more than a small margin $\delta$**, not that it is better.

**Rule.** Compute a confidence interval for (new − old). The new system is **non-inferior** if the whole interval lies above $-\delta$. In the paper $\delta = 0.25$ uptake points, with the interval at 98.75% (Bonferroni over four tests).

**Worked example** *(paper, Table 7a)*. Unified $k=6$ minus the 1B pipeline: $+0.04\ [-0.31,\ +0.41]$. The lower end $-0.31 < -0.25$, so non-inferiority is **not shown**. Unified $k=10$ minus 1B: $-0.02\ [-0.35,\ +0.30]$, lower end $-0.35 < -0.25$, also **not shown**. Against the 8B pipeline: $-0.38\ [-0.69,\ -0.04]$ and $-0.44\ [-0.83,\ -0.07]$ lie entirely below 0, so "lower". A *(toy)* that would pass: $-0.05\ [-0.20,\ +0.10]$, lower end $-0.20 > -0.25$.

**Why it matters here.** The correct statement is "level, but non-inferiority at the planned margin is not shown": the intervals are too wide (1,144 ratings over 32 dialogues, mostly one rater).

**Interview question.** *The point estimate is +0.04. Why not claim non-inferiority?* **Answer.** Non-inferiority is a claim about the **interval**, not the point estimate. The interval reaches $-0.31$, so a true difference worse than $-0.25$ cannot be ruled out.

## 17.13 Reading "level", "tie" and "lower"

- **Level / tie:** a difference smaller than the noise floor, or an interval that contains zero.
- **Exceeds:** larger than the noise floor, or an interval that excludes zero.
- **Lower:** the interval lies entirely below zero.
- **Not shown:** the data cannot rule out a difference. This is not the same as "shown to be equal".

## 17.14 Check yourself

- Compute McNemar $\chi^2$ for $b = 20$, $c = 10$. *($100/30 = 3.33$, $p = 0.068$.)*
- Is the chance of at least one false positive at 5% with 4 independent tests larger or smaller than 5%? *(Larger: $1-0.95^4 = 0.185$.)*
- If $r = 0.55$, what share of variance is shared? *($0.3025$, about 30%.)*

Back to the [[notes/proactive-assistant/index|study guide index]].
