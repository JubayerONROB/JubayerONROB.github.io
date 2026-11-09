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
