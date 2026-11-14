---
title: "12. Interview deep dive: math foundations"
date: 2026-11-14
tags:
  - notes
  - math
  - interview
---

`math` `interview` · Part of the [[notes/proactive-assistant/index|Proactive Assistant study guide]]

**How the deep-dive pages 12–17 work.** Every concept has five parts: **Meaning** (plain English), **Formula** (every symbol defined), **Worked example** (real numbers, step by step), **Why it matters here** (my paper), and **Interview question** (with a model answer). Numbers from the paper are marked *(paper)*. Toy examples use made-up numbers and say so. Anything the paper does not contain is marked **background**. I checked every calculation by computer.

This first page defines the small symbols that everything else uses. Skip nothing: a professor can start from any of them.

## 12.1 Sum: $\sum$

**Meaning.** "Add up a list of numbers."

**Formula.** $\displaystyle\sum_{i=1}^{n} a_i = a_1 + a_2 + \cdots + a_n$. The letter $i$ is a counter. The small numbers say where it starts (1) and ends ($n$). $a_i$ is the $i$-th number in the list.

**Worked example.** $a = (3, 5, 2)$, so $n = 3$. $\sum_{i=1}^{3} a_i = 3 + 5 + 2 = 10$. The *average* is the sum divided by the count: $10/3 \approx 3.33$.

**Why it matters here.** Every metric in the paper is a sum over markers, for example $\sum_{i \in \mathcal{T}} g_i m_i$ in Equation (2).

**Interview question.** *What does $\sum_{i\in\mathcal{T}}$ mean, with a set and not a range?* **Answer.** Add the term only for the $i$ that belong to the set $\mathcal{T}$ (the reference triggers). It is the same as summing over all $i$ and multiplying each term by $\mathbf{1}[i \in \mathcal{T}]$.

## 12.2 Set, element and size $|\cdot|$

**Meaning.** A **set** is a collection of different things, written in braces. $i \in \mathcal{T}$ means "$i$ is a member of $\mathcal{T}$". $|\mathcal{T}|$ is the **number of members** (the *cardinality*).

**Formula.** $|\mathcal{T}| = \sum_{i} \mathbf{1}[i \in \mathcal{T}]$.

**Worked example.** $\mathcal{T} = \{2, 5, 7, 9\}$. Then $|\mathcal{T}| = 4$, and $5 \in \mathcal{T}$ but $3 \notin \mathcal{T}$.

**Why it matters here.** $\mathcal{T}$ is the set of reference triggers, $|\mathcal{T}| = 3{,}356$ *(paper)* out of $N = 28{,}058$ markers. The trigger rate is $3356/28058 = 0.1196$, so 11.96% *(paper)*.

**Interview question.** *Why divide by $|\mathcal{T}|$ in $EM_{e2e}$ and not by the number of emitted hints?* **Answer.** Dividing by $|\mathcal{T}|$ asks "of all the moments that needed a hint, what fraction did we serve correctly?" (recall type). Dividing by emitted hints asks "of what we showed, what fraction was right?" (precision type). The paper reports both, as $EM_{e2e}$ and $P_{e2e}$.

## 12.3 The indicator $\mathbf{1}[\cdot]$

**Meaning.** A switch. It is **1 if the statement inside is true, 0 if false.**

**Formula.** $\mathbf{1}[A] = 1$ if $A$ is true, else $0$.

**Worked example.** $\mathbf{1}[0.62 \ge 0.50] = 1$. $\mathbf{1}[0.45 \ge 0.50] = 0$. $\mathbf{1}[\text{hint} = \text{reference}]$ is 1 only for an exact match.

**Why it matters here.** Equation (1), $g_i(t) = \mathbf{1}[p_i \ge t]$, is the gate. And $m_i = \mathbf{1}[h_i = h_i^*]$ is exact match.

**Interview question.** *Is $\mathbf{1}[p \ge t]$ differentiable in $p$?* **Answer.** No. It is a step: flat everywhere and jumps at $t$, so its gradient is zero or undefined. That is why we **train** with a smooth loss on the score $p_i$ (cross-entropy) and only apply the step **after** training, at inference. *(Background reasoning.)*

## 12.4 Probability, conditional probability, Bayes' rule

**Meaning.** A **probability** $P(A)$ is a number from 0 to 1 for how likely $A$ is. $P(A \mid B)$ is the probability of $A$ **given that** $B$ is true. A **random variable** is a quantity whose value depends on chance.

**Formulas.**

$$
P(A \mid B) = \frac{P(A \text{ and } B)}{P(B)}, \qquad
P(A \mid B) = \frac{P(B \mid A)\,P(A)}{P(B)} \quad \text{(Bayes' rule)}
$$

The second line follows from the first because $P(A \text{ and } B) = P(B \mid A) P(A)$.

**Worked example** *(numbers from the paper)*. The gate at its deployed point has recall $P(\text{fire} \mid \text{trigger}) = 0.8391$, false-alarm rate $P(\text{fire} \mid \text{silence}) = 0.0351$, and prevalence $P(\text{trigger}) = 0.1196$. Then

$$
P(\text{fire}) = 0.8391 \times 0.1196 + 0.0351 \times 0.8804 = 0.1003 + 0.0309 = 0.1312
$$

$$
P(\text{trigger} \mid \text{fire}) = \frac{0.8391 \times 0.1196}{0.1312} = \frac{0.1003}{0.1312} = 0.7646
$$

The paper reports gate precision 0.7648 *(paper)*; the small difference is rounding in the inputs. Also $0.1312 \times 28{,}058 \approx 3{,}682$, the number of hints emitted *(paper)*.

**Why it matters here.** It explains why precision depends on how rare triggers are (Figure 27 on [[notes/proactive-assistant/15-deep-dive-metrics-calibration-losses|page 15]]).

**Interview question.** *Same recall and false-alarm rate, but the corpus had 50% triggers. What is the precision?* **Answer.** $0.8391\cdot0.5 / (0.8391\cdot0.5 + 0.0351\cdot0.5) = 0.8391/0.8742 = 0.96$. Rare positives are the reason precision is only 0.76 here.

## 12.5 Expectation, variance, standard deviation

**Meaning.** The **expectation** $E[X]$ is the long-run average of a random variable. **Variance** $\mathrm{Var}(X) = E[(X - E[X])^2]$ measures spread. The **standard deviation (SD)** is its square root, in the same units as $X$.

**Formulas.** For a list $x_1..x_n$: $\bar x = \frac1n\sum x_i$ and the sample SD $s = \sqrt{\frac{1}{n-1}\sum (x_i-\bar x)^2}$. The $n-1$ (not $n$) corrects a small bias when the mean is itself estimated from the data. *(Background.)*

**Worked example.** Three gate F1 values from three seeds: 0.8000, 0.8044, 0.8022. Mean $= 0.8022$. Deviations: $-0.0022, +0.0022, 0$. Squares sum to $9.68\times10^{-6}$. Divide by 2, take the root: $s = 0.0022$. *(Toy numbers chosen close to the paper's 0.8022 ± 0.0029.)*

**Why it matters here.** The seed SDs 0.0033 ($k=6$) and 0.0029 ($k=10$) *(paper)* measure run-to-run noise.

**Interview question.** *Why can the expected cost per marker be written $k/L + \pi(1-k/L)$?* **Answer.** Cost is a random variable: $k/L$ if silent, $1$ if fired. Its expectation is the sum of value times probability: $(1-\pi)\cdot k/L + \pi\cdot 1 = k/L + \pi(1 - k/L)$.

## 12.6 Vectors, matrices, dot product

**Meaning.** A **vector** is a list of numbers. A **matrix** is a grid of numbers. The **dot product** of two vectors multiplies matching entries and adds. A matrix times a vector is a list of dot products, one per row.

**Formula.** $a\cdot b = \sum_j a_j b_j$. If $W \in \mathbb{R}^{2\times d}$ then $Wh$ has 2 entries, each the dot product of a row of $W$ with $h$.

**Worked example.** $a = (1, 2, 3)$, $b = (4, 0, -1)$. $a\cdot b = 4 + 0 - 3 = 1$. With $W = \begin{pmatrix}1&0&2\\0&1&-1\end{pmatrix}$ and $h = (3,1,2)$: $Wh = (3+0+4,\ 0+1-2) = (7, -1)$.

**Why it matters here.** The classifier head $W_c \in \mathbb{R}^{2\times d}$ turns a hidden state into two scores ("no hint", "hint").

**Interview question.** *What does "$\in \mathbb{R}^{2\times d}$" say?* **Answer.** The matrix has 2 rows and $d$ columns of real numbers. It maps a $d$-number vector to 2 numbers.

## 12.7 $\log$, $\exp$ and the argmax

**Meaning.** $\exp(x) = e^x$ ($e \approx 2.718$) is always positive. $\log$ (natural log) is its inverse: $\log(e^x) = x$. $\log$ turns products into sums: $\log(ab) = \log a + \log b$. $\arg\max_j f(j)$ is the **index** $j$ where $f$ is largest.

**Worked example.** $\log 0.9 = -0.1054$, $\log 0.5 = -0.6931$, $\log 0.1 = -2.3026$. $\arg\max$ of $(0.2, 0.7, 0.1)$ is index 2.

**Why it matters here.** Cross-entropy is $-\log p_t$; softmax uses $\exp$; greedy decoding picks the token with the $\arg\max$ probability.

**Interview question.** *Why do we use $\log$ probabilities in the loss?* **Answer.** The probability of a whole dataset is a product of per-example probabilities. The log turns that product into a sum, which is numerically stable and easy to differentiate. Maximizing the log-likelihood is the same as minimizing cross-entropy. *(Background.)*

## 12.8 Softmax and sigmoid

**Meaning.** **Softmax** turns any list of scores (**logits**) into probabilities that are positive and add to 1. **Sigmoid** does the same for one score, giving a probability between 0 and 1.

**Formulas.**

$$
\text{softmax}(z)_c = \frac{e^{z_c}}{\sum_j e^{z_j}}, \qquad \sigma(z) = \frac{1}{1+e^{-z}}
$$

For two classes, softmax equals a sigmoid of the **difference** of the logits: $\text{softmax}(z_1,z_0)_1 = \sigma(z_1 - z_0)$. Proof: divide top and bottom by $e^{z_0}$ to get $e^{z_1-z_0}/(e^{z_1-z_0}+1) = \sigma(z_1-z_0)$.

**Worked example.** Logits $(z_{hint}, z_{no}) = (1.2, -0.3)$. $e^{1.2} = 3.320$, $e^{-0.3} = 0.741$. $p = 3.320/(3.320+0.741) = 0.8176$. Check: $\sigma(1.5) = 1/(1+e^{-1.5}) = 0.8176$. ✓

**Why it matters here.** The gate head has two outputs, so $p_i$ is a two-class softmax, equal to a sigmoid of the logit difference.

**Interview question.** *Is $p_i$ a calibrated probability?* **Answer.** Not automatically. Softmax guarantees a number in $[0,1]$, not that it matches the true frequency. The paper measures this with ECE and finds the best-ranking gate is the worst calibrated (ECE 0.3036 vs 0.0425) *(paper, Table S4)*.

## 12.9 Check yourself

- Compute $P(\text{trigger}\mid\text{fire})$ if recall is 0.8, FAR is 0.05 and prevalence is 0.1. *(Answer: $0.08/(0.08+0.045) = 0.64$.)*
- What is $|\{2,5,7,9\}|$, and what is $\sum_{i\in\{2,5,7,9\}} 1$? *(4 and 4.)*
- What does softmax do to logits $(0, 0)$? *(Gives $(0.5, 0.5)$.)*

Next: [[notes/proactive-assistant/13-deep-dive-gate-and-end-to-end|13. Deep dive: gate and end-to-end score]]
