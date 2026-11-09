---
title: "8. Statistics behind the claims"
date: 2026-11-09
tags:
  - notes
  - statistics
---

`statistics` · Part of the [[notes/proactive-assistant/index|Proactive Assistant study guide]]

A result like "0.8164 beats 0.8002" can be luck. This page explains the tools the paper uses to separate real effects from noise.

## 8.1 Noise floor

Train the **same** model twice with the same settings. You will not get the same score, because of random starting points and random data order. The difference between two such runs is the **noise floor**. Differences smaller than it cannot be trusted.

In the paper, the noise floor for gate F1 is **0.0070**. It comes from a single pair of runs. The other estimate is the three-seed standard deviation of the unified gate: 0.0033 ($k=6$) and 0.0029 ($k=10$).

> **Rule of thumb in the paper.** If a gap is smaller than 0.0070 F1, call it a tie.

![Noise floor](/attachments/notes/proactive-assistant/fig17-noise-floor.png)
*Figure 17. Three-seed mean and standard deviation for the unified gate at step 21,703, the noise-floor band, the cascade gate, and the single-seed final checkpoints. [PDF](/attachments/notes/proactive-assistant/fig17-noise-floor.pdf)*

> **How to read it.** The $k=10$ mean (0.8022) sits on the cascade line (0.8002): a tie. The $k=6$ mean (0.7846) is more than the noise floor below it. The final-checkpoint diamonds come from one seed each, so they carry no error bar.

## 8.2 Confidence intervals and the bootstrap

A **95% confidence interval (CI)** is a range that, over many repeats of the study, would contain the true value 95% of the time. If the interval for a difference **includes zero**, we cannot say there is a real difference.

The **bootstrap** makes an interval without formulas. Resample the test data with replacement many times, compute the score each time, and take the middle 95%.

**Cluster bootstrap.** Markers from the same dialogue are not independent. So we resample **whole dialogues**, not single markers. This gives honest, wider intervals.

> Example from the paper: giving the cascade gate the profile changes F1 by +0.0055 with CI $[-0.0010, +0.0125]$. It includes zero. So that change is within noise.

## 8.3 McNemar's test (paired)

We often compare two systems on the **same** items. For each item, record who is right.

| | B right | B wrong |
|---|---|---|
| **A right** | both right | only A right ($b$) |
| **A wrong** | only B right ($c$) | both wrong |

Only the **disagreements** ($b$ and $c$) matter. If A and B are equally good, $b$ and $c$ should be about equal. McNemar's test asks how unlikely the observed split is. A small $p$-value means one system is really better on these items.

![Bootstrap and McNemar](/attachments/notes/proactive-assistant/fig21-bootstrap-mcnemar.png)
*Figure 18. (a) The bootstrap, step by step. (b) McNemar's test on a 2 by 2 table. The boxes show symbols only, not data. [PDF](/attachments/notes/proactive-assistant/fig21-bootstrap-mcnemar.pdf)*

### The bootstrap in five steps

1. Start with your test set: here, **866 dialogues**.
2. **Resample**: draw 866 dialogues at random **with replacement**. Some dialogues appear twice or more. Some do not appear at all.
3. Compute your score (for example the F1) on this resample. Call it $s_1$.
4. Repeat many times ($B$ times, often 1,000 or more). You get $s_1, s_2, \ldots, s_B$.
5. **Sort** the scores. The range from the **2.5th** to the **97.5th percentile** is the 95% confidence interval.

*Why it works.* Your test set is a random sample from all possible dialogues. Resampling from it imitates "drawing a new test set" many times, so you can see how much the score moves by luck.

### McNemar's test in four steps

1. Run systems A and B on the **same items**.
2. Fill the 2 by 2 table. Count $b$ (only A is right) and $c$ (only B is right). Ignore items where both are right or both are wrong, because they do not tell A and B apart.
3. If A and B are equally good, $b$ and $c$ should be about equal. The usual form of the statistic is

$$
\chi^2 = \frac{(b - c)^2}{b + c}
$$

4. A large $\chi^2$ gives a small $p$-value. Then the gap between $b$ and $c$ is unlikely to be luck, and one system is really better on these items.

> **Toy example.** A and B are tested on 100 items. $b = 12$ and $c = 4$. Then $\chi^2 = (12-4)^2/(12+4) = 4$. If $b = 9$ and $c = 7$, then $\chi^2 = 0.25$, which is tiny, so we call it a tie. (These numbers are made up to show the arithmetic. This is the textbook form; the paper does not print the formula, and exact variants exist for small counts.)

## 8.4 The $p$-value and the multiple-testing problem

The **$p$-value** is the chance of seeing a difference at least this big if there were really no difference. Small ($< 0.05$) is evidence of a real effect.

But if you run many tests, some will be small by luck. The **Holm correction** adjusts $p$-values for the number of tests. It is stricter than no correction and less strict than Bonferroni. Paper examples: "$p_{\text{holm}} = 0.0060$" and "none of the 45 retrieval configurations beats the full profile after Holm correction".

**Bonferroni** simply multiplies by the number of tests. We use it for the four non-inferiority tests in the human study.

## 8.5 Non-inferiority

Sometimes you do not want to show "better". You want to show "**not worse by more than a small margin**". That is **non-inferiority**. Pick a margin, here **0.25** uptake points. If the lower end of the confidence interval for (new − old) stays above $-0.25$, the new system is non-inferior.

In our human study the unified model's intervals reach below $-0.25$ (for example $[-0.31, +0.41]$). So we say: the average is level, but **non-inferiority at the planned margin is not shown**.

## 8.6 Correlation (Pearson $r$)

$r$ measures how well two lists of numbers move together. $r = 1$: perfect line up. $r = 0$: no link. We use it between **human ratings** and **automatic scores** over 136 hints.

$$r = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum (x_i-\bar{x})^2}\,\sqrt{\sum (y_i-\bar{y})^2}}$$

## 8.7 Inter-annotator agreement (Krippendorff's $\alpha$)

When two people rate the same thing, how much do they agree **beyond chance**? Krippendorff's ordinal $\alpha$ handles ordered scales like 1 to 5. $\alpha = 1$ is perfect and $0$ is chance level. Ours is **0.72** on 196 hints rated by both annotators. Identical texts shown twice under different codes got the same rating on 92.1% and 91.8% of pairs.

## 8.8 Pre-registration

A **pre-registered** study writes the analysis plan, with a time stamp and hash, **before** any data exist. It stops us from picking the nice-looking test after seeing results. Our human study followed a plan fixed in version control before any rating existed. We also list the **three deviations** honestly (see [[notes/proactive-assistant/9-human-evaluation|page 9]]).

## 8.9 Check yourself

- Why do we resample dialogues and not markers?
- A CI for a difference is $[-0.02, +0.30]$. What do you conclude?  (*Answer: no clear difference; it includes zero.*)
- Why do many tests need Holm?

Next: [[notes/proactive-assistant/9-human-evaluation|9. Human evaluation]]
