---
title: "18. Deep dive: optimization"
date: 2026-11-15
tags:
  - notes
  - math
  - optimization
---

`math` `optimization` · Part of the [[notes/proactive-assistant/index|Proactive Assistant study guide]]

**Builds on:** [[notes/proactive-assistant/4-training|4. Training: LoRA, 4-bit, losses]]; [[notes/proactive-assistant/5-early-exit-and-unified-decoder|5. Early exit and the unified decoder]]. **Previous:** [[notes/proactive-assistant/17-deep-dive-generation-metrics-and-statistics|17. Generation metrics and statistics]].

**Where the facts come from.** The paper says only that the unified model trained for **2 epochs (53,772 steps)** with one shared LoRA adapter, and that the two-stage gate trained for 4 epochs *(paper)*. It does **not** list the optimizer settings. The settings below (AdamW, learning rate $2\times10^{-5}$, weight decay 0.01, batch 2 × 4, float16, clipping at 1.0) come from the **defaults in your code**, `experiments/train_joint.py`, and are marked *(repo)*. Check them against the exact run before you quote them. Other statements are **background** (standard facts), **derived** (my arithmetic) or **toy** (made-up numbers to show the idea).

This page explains **how the model learns**, one idea at a time, starting from the simplest picture. Each section has: **In one sentence**, **The picture**, **The symbols**, **A worked example**, **Why it matters here**, and **Likely question**.

## 18.0 The whole training loop in plain words

Training is a loop. Every pass through the loop is one **step**:

1. **Forward.** Show the model a few examples. It makes predictions.
2. **Loss.** Measure how wrong the predictions are with one number, the **loss**.
3. **Backward.** Work out, for every trainable weight, "if I nudged this weight up a little, would the loss go up or down, and by how much?" That list of numbers is the **gradient**.
4. **Clip.** If the gradient is huge, shrink it (so one bad batch cannot ruin the model).
5. **Update.** The **optimizer** (AdamW) moves each weight a small step in the direction that lowers the loss. The size of the step is set by the **learning rate**.
6. **Schedule.** The learning rate is changed a little for the next step (small at the start, biggest early, then smaller and smaller).

In the code the order is exactly this *(repo)*: forward under float16, scaled backward, (after 4 small batches) unscale, clip to norm 1.0, optimizer step, update the loss scale, then step the schedule. The sections below explain each word.

**What is trained.** The big model (about 1.2 billion weights, stored in 4-bit) is **frozen**. Only a small add-on is trained: the **LoRA adapter** (about 11 million weights, my estimate on [[notes/proactive-assistant/16-deep-dive-model-lora-quantization|page 16]]) and the small **gate head** $W_c$.

## 18.1 Two jobs, two losses: who learns from what

**In one sentence.** The model has two jobs (decide "speak or not", and write the hint), so it has two losses, and different layers receive different ones.

**The formula** *(repo)*:

$$
\mathcal{L} = \lambda_{\text{cls}}\ \text{FL}\big(\text{gate output},\, y\big) \;+\; \lambda_{\text{gen}}\ \text{CE}\big(\text{hint tokens}\big), \qquad \lambda_{\text{cls}} = \lambda_{\text{gen}} = 1
$$

- $\mathcal{L}$ is the total loss, a single number.
- FL is the **focal loss** on the gate (page 15). $y\in\{0,1\}$ says whether the marker is a trigger.
- CE is the **cross-entropy** on the hint words.
- $\lambda_{\text{cls}}$ and $\lambda_{\text{gen}}$ are weights that say how much each job counts. Both are 1.

The code also stops before training if the two terms differ by more than 20 times at the start, because then one would drown out the other *(repo)*.

**The picture.**

![Which layers learn from which loss](/attachments/notes/proactive-assistant/o8-gradient-flow.png)
*Figure 30. The gate head reads layer $k$. Red layers (1 to $k$) feel both losses. Black layers ($k{+}1$ to 16) feel only the hint loss. [PDF](/attachments/notes/proactive-assistant/o8-gradient-flow.pdf)*

**Why this is true (the chain rule, in words).** A weight can only receive a gradient from a loss if the loss **depends** on that weight. The gate loss is computed from the layer-$k$ readout, which only layers $1..k$ produced. Layers after $k$ do not affect the gate loss, so their gradient from it is exactly zero. The hint loss comes out of the last layer, so every layer affects it. In symbols, for a layer $\ell$ with parameters $\theta_\ell$:

$$
\frac{\partial\mathcal{L}}{\partial\theta_\ell} = \lambda_{\text{cls}}\frac{\partial \text{FL}}{\partial\theta_\ell} + \lambda_{\text{gen}}\frac{\partial \text{CE}}{\partial\theta_\ell}, \qquad \frac{\partial \text{FL}}{\partial\theta_\ell} = 0 \ \text{ for } \ell > k
$$

**A worked example.** $k = 6$: layers 1–6 get two gradients added together. Layers 7–16 get one. At $k=10$, layers 1–10 get two and layers 11–16 get one. The head $W_c$ gets only the gate gradient.

**Why it matters here.** This is why training runs the **full depth** even for markers that will be silent at test time: only then can the hint loss reach layers $k{+}1..16$ *(repo)*. It also explains the exit depth trade-off: a larger $k$ makes more layers serve both jobs.

**Likely question.** *Do the two losses fight each other?* **Answer.** They can: layers $1..k$ must satisfy both. The paper shows the cost is small at the final checkpoint. The gate F1 is 0.8022 ($k=6$) and 0.8164 ($k=10$) against 0.8002 for the separate gate, and generation exact match is 0.3299 and 0.3218 against 0.2971 for the 1B generator alone *(paper, Table 4)*. Many batches also carry no hint supervision at all, because only trigger markers have a hint *(repo)*.

## 18.2 The gradient and walking downhill

**In one sentence.** The loss is a hilly landscape over the weights; the **gradient** is the slope; learning means taking small steps downhill.

**The picture.**

![Gradient descent](/attachments/notes/proactive-assistant/o1-descent.png)
*Figure 31. (a) A toy bowl-shaped loss $f(x)=x^2$. Each red dot is one step downhill. (b) The learning rate $\eta$ decides whether the walk is slow, good, zig-zag or explosive. These are toy numbers. [PDF](/attachments/notes/proactive-assistant/o1-descent.pdf)*

**The symbols.**

- $x$ is one weight. $f(x)$ is the loss when the weight has value $x$.
- $f'(x)$ is the **slope** of the loss at $x$ (the derivative). If $f'(x)>0$ the loss rises to the right, so we should move left.
- $\eta$ (eta) is the **learning rate**: how big a step we take.
- The rule is **gradient descent**: $x \leftarrow x - \eta\,f'(x)$. "$\leftarrow$" means "replace the old value by".

For many weights, the slope for each weight together is the **gradient** vector $g = \nabla\mathcal{L}$, and the same rule is applied to every weight: $\theta \leftarrow \theta - \eta\,g$.

**A worked example** *(toy)*. $f(x) = x^2$, so $f'(x) = 2x$. Start at $x=4$ with $\eta = 0.1$:

| step | $x$ | slope $2x$ | new $x = x - 0.1\cdot2x$ |
|---|---|---|---|
| 0 | 4.00 | 8.00 | 3.20 |
| 1 | 3.20 | 6.40 | 2.56 |
| 2 | 2.56 | 5.12 | 2.05 |
| 3 | 2.05 | 4.10 | 1.64 |
| 4 | 1.64 | 3.28 | 1.31 |

Each step multiplies $x$ by $1 - 2\eta = 0.8$, so $x$ shrinks toward 0, the bottom of the bowl. Now compare learning rates (panel b), same start $x = 4$:

- $\eta = 0.05$: factor $0.9$. Slow: 4, 3.6, 3.24, 2.92, 2.62.
- $\eta = 0.4$: factor $0.2$. Fast and smooth: 4, 0.8, 0.16, 0.03.
- $\eta = 0.95$: factor $-0.9$. It jumps to the other side every step (zig-zag): 4, −3.6, 3.24, −2.92.
- $\eta = 1.1$: factor $-1.2$. Each jump is **bigger** than the last: 4, −4.8, 5.76, −6.91. It blows up.

**Why it matters here.** Real models have millions of weights and a bumpy loss, but the lesson is the same: too small a learning rate wastes time and too large destroys training. The repo records exactly such a failure (section 18.12).

**Likely question.** *Is the training problem convex?* **Answer.** No. A transformer's loss has many valleys, so training finds a good valley, not a proven best one. (Background.) The low-rank LoRA update searches a much smaller space, which helps stability but does not make the problem convex.

## 18.3 Adam: a different step size for every weight

**In one sentence.** Adam remembers the recent slope of each weight (its *direction*) and how big the slopes have been (its *scale*), and uses both so that every weight takes a sensible step.

**The picture.**

![Adam](/attachments/notes/proactive-assistant/o2-adam.png)
*Figure 32. (a) Plain descent takes a step proportional to the gradient. Adam's very first step is always about $\eta$, whatever the gradient size. (b) Three Adam steps on a toy weight. [PDF](/attachments/notes/proactive-assistant/o2-adam.pdf)*

**The symbols** *(standard defaults, background)*.

- $g_t$: the gradient at step $t$.
- $m_t$: a running average of the gradients (the **momentum**). It points in the recent average direction. $\beta_1 = 0.9$ means 90% old, 10% new.
- $v_t$: a running average of the **squared** gradients (the typical size). $\beta_2 = 0.999$.
- $\hat m_t$ and $\hat v_t$: the same, **bias corrected**. $m$ and $v$ start at 0, so early on they are too small. Dividing by $1-\beta^t$ fixes that.
- $\epsilon = 10^{-8}$: a tiny number that stops division by zero.

$$
m_t = \beta_1 m_{t-1} + (1-\beta_1)g_t, \qquad v_t = \beta_2 v_{t-1} + (1-\beta_2)g_t^{2}
$$

$$
\hat m_t = \frac{m_t}{1-\beta_1^{\,t}}, \qquad \hat v_t = \frac{v_t}{1-\beta_2^{\,t}}, \qquad \theta_t = \theta_{t-1} - \eta\,\frac{\hat m_t}{\sqrt{\hat v_t} + \epsilon}
$$

**In plain words:** the step is "average direction ÷ typical size". A weight whose slopes are always large gets divided by a large number, so it takes a **small** step. A weight whose slopes are tiny gets a **larger** step. Every weight moves at a similar speed.

**A worked example** *(toy: one weight $\theta_0 = 1$, $\eta = 0.1$, gradients 0.5, 0.25, −0.1)*.

| step $t$ | $g_t$ | $m_t$ | $v_t$ | $\hat m_t$ | $\hat v_t$ | step | $\theta_t$ |
|---|---|---|---|---|---|---|---|
| 1 | 0.50 | 0.0500 | 0.000250 | 0.5000 | 0.2500 | 0.1000 | 0.9000 |
| 2 | 0.25 | 0.0700 | 0.000312 | 0.3684 | 0.1562 | 0.0932 | 0.8068 |
| 3 | −0.10 | 0.0530 | 0.000322 | 0.1956 | 0.1074 | 0.0597 | 0.7471 |

Check step 1: $m_1 = 0.9\cdot0 + 0.1\cdot0.5 = 0.05$; $\hat m_1 = 0.05/(1-0.9) = 0.5$. $v_1 = 0.001\cdot0.25 = 0.00025$; $\hat v_1 = 0.00025/0.001 = 0.25$, so $\sqrt{\hat v_1} = 0.5$. The step is $0.1\times0.5/0.5 = 0.1$.

**The surprise.** At step 1, $\hat m/\sqrt{\hat v} = g/|g| = \pm1$ always, so the first step has size exactly $\eta$ for gradients of 0.5, 5 or 50 (panel a). Adam's step size is set by $\eta$, not by how big the gradient happens to be.

**Why it matters here** *(repo)*. Joint training uses AdamW with $\eta = 2\times10^{-5}$ on the adapter and head weights.

**Likely question.** *Why Adam and not plain gradient descent for a transformer?* **Answer.** Different weights have very different gradient sizes (embeddings, attention, a fresh head). Adam scales each step by that weight's own gradient history, so one learning rate works for all. Plain descent would need a different learning rate for each part. This is common practice, not a theorem. (Background.)

## 18.4 AdamW: shrinking the weights a little

**In one sentence.** **Weight decay** pulls every weight slightly toward zero each step, which keeps the weights from growing too large; **AdamW** applies it separately from the Adam step.

**The formula** *(repo: weight decay $\lambda = 0.01$)*:

$$
\theta_t = \theta_{t-1} - \eta\left(\frac{\hat m_t}{\sqrt{\hat v_t}+\epsilon} + \lambda\,\theta_{t-1}\right)
$$

The first term is the Adam step. The second, $\lambda\theta_{t-1}$, is the decay.

**A worked example** *(derived)*. At the peak learning rate, $\eta\lambda = 2\times10^{-5}\times0.01 = 2\times10^{-7}$. Each step, the weights are multiplied by about $1 - 2\times10^{-7}$. That is a tiny pull, so the decay is gentle.

**Why "W"?** In the older way, the decay is added into the gradient, so Adam divides it by $\sqrt{\hat v}$ and it acts unevenly across weights. AdamW applies it **outside** that division. (Background.)

**Likely question.** *Is weight decay on or off here?* **Answer.** On, at 0.01 *(repo)*. (In the deepfake guide it was off, $\lambda = 0$; these are different papers.)

## 18.5 The learning-rate schedule

**In one sentence.** The learning rate is not constant: it starts small (**warm-up**), reaches its peak early, then gets smaller and smaller (**anneal**), so the model first moves boldly and then settles.

**The picture.**

![Learning-rate schedule](/attachments/notes/proactive-assistant/o3-schedule.png)
*Figure 33. The OneCycle schedule over the paper's 53,772 steps. The shape and the 10% warm-up are from the code; the peak is $2\times10^{-5}$. [PDF](/attachments/notes/proactive-assistant/o3-schedule.pdf)*

**The recipe** *(repo: `OneCycleLR`, peak $2\times10^{-5}$, warm-up 10% of steps; the rest are PyTorch defaults, background)*.

- Start at $\eta_{\text{init}} = \eta_{\max}/25 = 8\times10^{-7}$.
- Rise to $\eta_{\max} = 2\times10^{-5}$ over the first 10% of steps (about 5,376 steps).
- Then fall along a **cosine** curve (a smooth half-wave) to $\eta_{\text{fin}} = \eta_{\text{init}}/10^4 = 8\times10^{-11}$.

**Worked values** *(derived, $T = 53{,}772$)*:

| step | learning rate | what is happening |
|---|---|---|
| 0 | $8.0\times10^{-7}$ | very small start |
| 1,000 | $2.4\times10^{-6}$ | warming up |
| 5,376 | $2.0\times10^{-5}$ | peak |
| 15,000 | $1.8\times10^{-5}$ | still high |
| 26,886 (middle) | $1.2\times10^{-5}$ | falling |
| 40,000 | $3.7\times10^{-6}$ | settling |
| 53,771 (end) | $8.0\times10^{-11}$ | almost zero |

**Why warm up?** At the start the adapter is untrained and Adam's averages $m$ and $v$ are built from only a few steps, so they are unreliable. A small first step avoids a damaging jump. **Why anneal?** With a large constant rate the weights keep bouncing around the bottom of a valley. Lowering the rate lets them settle. (Background.)

**Why it matters here** *(repo)*. The schedule is defined over the **whole** run. A short debugging run can either shorten the schedule (`--max-steps`) or just stop early (`--stop-after-steps`). Only the second one tests the same learning-rate regime as the long run. See section 18.12.

**Likely question.** *What if the learning rate were constant?* **Answer.** The weights would keep jumping by about $\eta$ per step at the end of training, so the final model would be a noisy point instead of a settled one.

## 18.6 Batch size and gradient accumulation

**In one sentence.** A **batch** is the group of examples used for one update; when a big batch does not fit in memory, you split it into small **micro-batches** and add their gradients before updating.

**The picture.**

![Gradient accumulation](/attachments/notes/proactive-assistant/o4-accumulation.png)
*Figure 34. Four micro-batches of 2 rows give four gradients. They are averaged and used for one update on 8 rows (the code's defaults). [PDF](/attachments/notes/proactive-assistant/o4-accumulation.pdf)*

**The numbers** *(repo defaults)*: micro-batch 2, accumulation 4, so the **effective batch** is $2\times4 = 8$ rows per update.

**Why adding gradients is allowed.** The gradient of a sum is the sum of the gradients. So the average of the four micro-batch gradients equals the gradient of the average loss over all 8 rows:

$$
\frac14\sum_{j=1}^{4}\nabla\mathcal{L}_j = \nabla\Big(\frac14\sum_{j=1}^{4}\mathcal{L}_j\Big)
$$

**A worked example** *(toy)*. Four micro-batch gradients for one weight: 0.2, 0.6, −0.1, 0.3. Average $= (0.2+0.6-0.1+0.3)/4 = 0.25$. One update uses 0.25.

**Counting steps.** The paper reports 53,772 steps for 2 epochs, so 26,886 steps per epoch. *If* the run used effective batch 8, that is about $26{,}886\times8\approx215{,}000$ training rows per epoch. This is an inference from the defaults, not a number in the paper.

**Likely question.** *Is accumulation identical to a really big batch?* **Answer.** For the gradient, yes. It would differ only for layers that use batch statistics (batch normalization), and a transformer uses layer normalization, so here it is equivalent. (Background.)

## 18.7 Mixed precision and loss scaling

**In one sentence.** Doing the math in 16-bit numbers is faster and uses less memory, but very small numbers become zero in 16 bits; **loss scaling** multiplies the loss by a big number so the small gradients survive, and divides it back before the update.

**The picture.**

![Loss scaling](/attachments/notes/proactive-assistant/o5-fp16-scaling.png)
*Figure 35. Gradients below about $6\times10^{-8}$ become exactly 0 in float16 (the hatched zone). Multiplying by 65,536 lifts a gradient of $10^{-8}$ to $6.6\times10^{-4}$. [PDF](/attachments/notes/proactive-assistant/o5-fp16-scaling.pdf)*

**Facts** *(background)*. float16 has the smallest normal number $2^{-14}\approx6.1\times10^{-5}$ and the smallest subnormal $2^{-24}\approx6.0\times10^{-8}$. Anything smaller is rounded to 0 (**underflow**).

**The steps.**

1. Multiply the loss by a scale $S$. By the rule that a derivative is linear, **every gradient is also multiplied by $S$**.
2. Backpropagate. The gradients are now large enough to be stored.
3. Divide the gradients by $S$ again (**unscale**).
4. If any number overflowed to infinity, skip this update and lower $S$. If many steps succeed, raise $S$. This is **dynamic** scaling.

**A worked example.** A true gradient of $10^{-8}$ would become 0. With $S = 65{,}536$ it is stored as $10^{-8}\times65536 = 6.6\times10^{-4}$, which float16 can hold. After unscaling it is $10^{-8}$ again.

**Why it matters here** *(repo)*. The script uses float16 autocast with a gradient scaler. (A repo comment mentions a 14.56 GB T4 GPU, which has no native bfloat16, so float16 is the natural choice.)

**Likely question.** *Why must unscaling happen before clipping?* **Answer.** The clip threshold is about the **true** gradient size. If you clipped first, you would compare the inflated size (true × $S$) with the threshold and clip almost every time. The code unscales, then clips *(repo)*.

## 18.8 Gradient clipping

**In one sentence.** If the gradient is too long, shrink it to a maximum length, keeping its direction.

**The picture.**

![Gradient clipping](/attachments/notes/proactive-assistant/o6-clipping.png)
*Figure 36. (a) A short gradient is kept; a long one is scaled down to the circle. (b) The length used in the update never exceeds 1. [PDF](/attachments/notes/proactive-assistant/o6-clipping.pdf)*

**The formula** *(repo: maximum norm $c = 1.0$)*:

$$
g \leftarrow g\cdot\min\!\left(1,\ \frac{c}{\lVert g\rVert_2}\right), \qquad \lVert g\rVert_2 = \sqrt{\textstyle\sum_j g_j^{2}}
$$

$\lVert g\rVert_2$ is the **norm**: the length of the whole gradient, computed over all trainable weights together.

**A worked example.** If $\lVert g\rVert = 0.4$ the factor is $\min(1, 2.5) = 1$ (unchanged). If $\lVert g\rVert = 3$ the factor is $1/3$. If $\lVert g\rVert = 10$ the factor is $0.1$.

**Why it matters here.** A few noisy batches (for example, ones with almost no hint supervision) can give a very large gradient. Clipping stops one batch from throwing the adapter far away.

**Likely question.** *Adam already normalizes the step. Is clipping still useful?* **Answer.** Yes. One huge gradient raises Adam's stored averages $m$ and $v$ and keeps affecting the next steps. Clipping limits that. (Background.)

## 18.9 LoRA: why one factor starts at zero

**In one sentence.** LoRA adds a small update $\frac{\alpha}{r}BA$ to the frozen weights; $B$ starts at zero so training begins exactly at the pre-trained model, and the zero start also decides who learns first.

**The picture.**

![LoRA zero start](/attachments/notes/proactive-assistant/o7-lora-zero.png)
*Figure 37. With $B = 0$ the gradient on $B$ is large and the gradient on $A$ is zero, so $B$ moves first. After that $A$ can learn too. All numbers are a toy. [PDF](/attachments/notes/proactive-assistant/o7-lora-zero.pdf)*

**The symbols** (see [[notes/proactive-assistant/16-deep-dive-model-lora-quantization|page 16]] for LoRA itself).

- $x$: the input to the layer. $A$ and $B$: the two small trainable matrices. $s = \alpha/r$: a scale (here $32/16 = 2$, from the code).
- $u = Ax$: the input squeezed to $r$ numbers.
- $\delta = \partial\mathcal{L}/\partial y$: the gradient coming back from the loss to the layer output $y$.

**The derivation.** The layer output is $y = Wx + s\,B u$. By the chain rule:

$$
\frac{\partial\mathcal{L}}{\partial B} = s\,\delta\,u^{\top}, \qquad
\frac{\partial\mathcal{L}}{\partial A} = s\,B^{\top}\delta\,x^{\top}
$$

The gradient on $A$ contains the factor $B^{\top}$. When $B = 0$ it is **zero**. The gradient on $B$ contains $u = Ax$, which is not zero, so $B$ learns first.

**A worked example** *(toy: $r=1$, $d=2$)*. $A = (1,1)$, $x = (2,1)$, so $u = 3$. $\delta = (1,-1)$, $s = 2$.

- Gradient on $B$: $2\cdot(1,-1)\cdot3 = (6,-6)$. Large: $B$ moves.
- Gradient on $A$ at $B = 0$: $2\cdot(0\cdot1 + 0\cdot(-1))\cdot(2,1) = (0,0)$.
- After $B$ becomes $(0.1,-0.2)$: $B^{\top}\delta = 0.1 + 0.2 = 0.3$. Gradient on $A$ $= 2\cdot0.3\cdot(2,1) = (1.2,\ 0.6)$. Now $A$ learns too.

**Why it matters here.** At step 0 the model is exactly the pre-trained one (the update $s\,Bu = 0$), so early training is stable.

**Likely question.** *Why not start both $A$ and $B$ at zero?* **Answer.** Each gradient contains the other factor, so both would be zero forever and nothing would train. One is random and the other zero. (Background.)

## 18.10 Training through a 4-bit base

**In one sentence.** The big model's weights are frozen and stored in 4 bits; during the forward pass they are expanded on the fly to 16 bits for the multiplication, and the gradient flows back **through** them to the adapter without changing them. (Background: the standard QLoRA recipe.)

**Why it matters here.** The trainable part is only about 11.27 million weights (my estimate, page 16) out of about 1.2 billion. Adam keeps two extra numbers per trainable weight ($m$ and $v$), so the training state is small: $11.27\times10^6\times(4+4+4)$ bytes (weights, $m$, $v$ in 32-bit) $\approx135$ MB *(my arithmetic)*.

**Likely question.** *Where does the 4-bit rounding error go?* **Answer.** The base is frozen with its rounding error built in. The adapter is trained **on top of** that rounded model, so it can learn to compensate. (Background.)

## 18.11 One training step, put together

Here is the loop of section 18.0 with every number from this page. All settings are the code's defaults *(repo)* unless noted.

| order | what happens | setting |
|---|---|---|
| 1 | forward on a micro-batch in float16 | micro-batch 2 rows |
| 2 | total loss $\mathcal{L}$ = gate loss + hint loss | $\lambda_{\text{cls}}=\lambda_{\text{gen}}=1$ |
| 3 | backward on the **scaled** loss | dynamic scale $S$ |
| 4 | repeat 1–3 four times, adding gradients | accumulation 4, effective batch 8 |
| 5 | divide gradients by $S$ (unscale) | |
| 6 | clip to maximum norm 1.0 | $c = 1.0$ |
| 7 | AdamW update of adapter and head | $\eta$ from the schedule, weight decay 0.01 |
| 8 | adjust the loss scale; skip the step if infinite | |
| 9 | move the learning rate along the OneCycle curve | peak $2\times10^{-5}$ |

The paper's 53,772 steps (2 epochs) are most likely counts of the **updates in row 7**, because the code counts optimizer steps and not micro-batches. (My reading of the code; the paper does not define a step.)

## 18.12 A failure recorded in the code (not in the paper)

**What the code comments say** *(repo, `train_joint.py`)*:

- The first full run used a learning rate of $2\times10^{-4}$, the rate used for the hint-writing stage, "carried over without checking".
- The **gate collapsed to chance** (AUROC 0.4995 at $k=6$ after 28,547 steps) while **writing hints was unharmed**.
- The fix was $2\times10^{-5}$, the learning rate of the published gate.
- A quick 200-step test did not catch it, because the schedule **finished inside** the 200 steps, so the model never sat at the peak rate. That is why there are two flags, `--max-steps` (compresses the schedule) and `--stop-after-steps` (stops early but keeps the full schedule), and a periodic gate score during training (`--eval-every`).

**What this teaches** *(my reading)*:

1. **A short test must keep the schedule's shape.** A compressed schedule tests a different regime.
2. **Measure during training, not only at the end.** A final number cannot say when a collapse happened.
3. **Different jobs may need different learning rates.** A rate that suits writing text can destroy a classifier head. (A hypothesis consistent with the comments, not tested in the paper.)

**Likely question.** *Tell me about something that went wrong in training.* **Answer.** State the symptom (gate at chance, AUROC 0.4995, hints fine), the cause (a learning rate ten times too high for the gate, inherited from another stage), why a quick test missed it (the schedule had annealed within the test), and the fix (the published gate rate, tests that keep the full schedule, and scoring during training).

## 18.13 Quick answers

- **Why does Adam's first step have size $\eta$?** Because $\hat m/\sqrt{\hat v} = g/|g| = \pm1$ at $t=1$ (section 18.3).
- **What does weight decay do in AdamW?** It shrinks each weight by a factor $1-\eta\lambda$ per step, separately from the gradient statistics (about $1-2\times10^{-7}$ at peak rate here).
- **Why is the gate loss only on layers up to $k$?** The head reads layer $k$, so later layers cannot affect that loss (section 18.1).
- **What does the cross-entropy gradient look like?** At the output score it is just "prediction minus truth", $p - y$ ([[notes/proactive-assistant/15-deep-dive-metrics-calibration-losses|page 15]]).
- **What limits LoRA?** The update has rank at most $r$ (here 16), so it cannot express a change that needs a higher rank. (Background.)

## 18.14 Check yourself

- At step 1 of Adam, what is the update for gradient 3 and $\eta = 0.01$? *(0.01.)*
- What is the clip factor if the gradient norm is 4 and the maximum is 1? *(0.25.)*
- Why is $\partial\mathcal{L}/\partial A = 0$ when $B=0$? *(It contains the factor $B^{\top}$.)*
- With $x_0 = 4$, $f(x) = x^2$ and $\eta = 0.3$, what is $x_1$? *($4 - 0.3\cdot8 = 1.6$.)*
- Which layers get the hint loss only when $k = 10$? *(Layers 11 to 16.)*

Back to the [[notes/proactive-assistant/index|study guide index]].
