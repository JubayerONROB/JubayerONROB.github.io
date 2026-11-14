---
title: "18. Interview deep dive: optimization"
date: 2026-11-14
tags:
  - notes
  - math
  - interview
  - optimization
---

`math` `optimization` `interview` · Part of the [[notes/proactive-assistant/index|Proactive Assistant study guide]]

**Builds on:** [[notes/proactive-assistant/4-training|4. Training: LoRA, 4-bit, losses]]; [[notes/proactive-assistant/5-early-exit-and-unified-decoder|5. Early exit and the unified decoder]]. **Previous:** [[notes/proactive-assistant/17-deep-dive-generation-metrics-and-statistics|17. Generation metrics and statistics]].

**Read this first.** The paper says only that the unified model trained for **2 epochs (53,772 steps)** on marker-level rows with one shared LoRA adapter, and that the two-stage gate trained for 4 epochs *(paper)*. It does **not** list the optimizer settings. Everything below about AdamW, the schedule, the batch size, mixed precision and clipping comes from **your code repository** (`experiments/train_joint.py`) and is marked *(repo)*. The repo values are **defaults of the script**. Confirm them against the exact configuration of the run before you quote them in the interview. Other statements are **background** or **derived**.

## 18.1 What is being optimized, and which layers receive which gradient

**Meaning.** The unified model has one set of weights and **two jobs**, so it has two losses added together: the gate loss (a focal cross-entropy on the 2-way head at layer $k$) and the hint loss (cross-entropy on the hint tokens).

**Formula** *(repo)*:

$$
\mathcal{L} = \lambda_{\text{cls}}\,\text{FL}\!\big(\text{softmax}(W_c h_k),\,y\big) \;+\; \lambda_{\text{gen}}\,\text{CE}\big(\text{hint tokens}\big), \qquad \lambda_{\text{cls}} = \lambda_{\text{gen}} = 1
$$

Here $h_k$ is the hidden state after $k$ layers, $y\in\{0,1\}$ is the trigger label, FL is the focal loss ([[notes/proactive-assistant/15-deep-dive-metrics-calibration-losses|page 15]]). The repo also stops before training if the two loss terms differ by more than 20 times at initialization, so one cannot swamp the other *(repo)*.

**Derivation: which parameters get which gradient.** Let $\theta_\ell$ be the parameters (LoRA adapters) of layer $\ell$. By the chain rule

$$
\frac{\partial\mathcal{L}}{\partial\theta_\ell} = \lambda_{\text{cls}}\frac{\partial \text{FL}}{\partial\theta_\ell} + \lambda_{\text{gen}}\frac{\partial \text{CE}}{\partial\theta_\ell}.
$$

The gate loss depends on the input only through $h_k$, which is computed by layers $1..k$. So $\partial\text{FL}/\partial\theta_\ell = 0$ for every $\ell > k$. The hint loss depends on the last layer, hence on all layers. Therefore:

| parameters | receive gate gradient | receive hint gradient |
|---|---|---|
| head $W_c$ | yes | no |
| layers $1..k$ | yes | yes |
| layers $k{+}1..L$ | **no** | yes |

**Worked example.** $L = 16$, $k = 6$. Layers 1–6 are pulled by two objectives. Layers 7–16 learn only to write hints. At $k=10$, layers 1–10 are shared by both objectives and layers 11–16 are hint-only.

**Why it matters here.** This is why training runs **full depth** even for markers that will be silent at inference: only then can the hint loss shape layers $k{+}1..L$ *(repo)*. It also explains why the exit depth is a real design choice: a deeper $k$ makes more layers serve both objectives.

**Interview question.** *Do the two losses interfere?* **Answer.** They can: layers $1..k$ receive both gradients, so the gate objective constrains what those layers represent, and the hint objective does the same. The paper shows the cost is small at the final checkpoint: the gate F1 is 0.8022 ($k=6$) and 0.8164 ($k=10$) against 0.8002 for the separate gate, and generation exact match is 0.3299 and 0.3218 against 0.2971 for the 1B generator alone *(paper, Table 4)*. A caution from the repo itself: the hint loss is supervised only on trigger markers, so many batches have **no** hint supervision at all.

## 18.2 Gradient descent, Adam and AdamW

**Meaning.** The **gradient** $g = \nabla_\theta\mathcal{L}$ points in the direction of steepest increase of the loss. **Gradient descent** moves the opposite way. **Adam** keeps running averages of the gradient and of its square so that every parameter gets its own step size. **AdamW** adds weight decay in a way that does not interact with those running averages.

**Formulas.** Plain gradient descent with learning rate $\eta$: $\theta \leftarrow \theta - \eta\,g$.

Adam at step $t$, with $\beta_1 = 0.9$, $\beta_2 = 0.999$, $\epsilon = 10^{-8}$ *(standard defaults, background)*:

$$
m_t = \beta_1 m_{t-1} + (1-\beta_1)\,g_t, \qquad v_t = \beta_2 v_{t-1} + (1-\beta_2)\,g_t^2
$$

$$
\hat m_t = \frac{m_t}{1-\beta_1^{\,t}}, \qquad \hat v_t = \frac{v_t}{1-\beta_2^{\,t}}, \qquad
\theta_t = \theta_{t-1} - \eta\,\frac{\hat m_t}{\sqrt{\hat v_t} + \epsilon}
$$

$m$ is the average gradient (momentum), $v$ the average squared gradient. The hats are **bias corrections**: $m$ and $v$ start at 0, so early values are too small; dividing by $1-\beta^t$ fixes that.

**AdamW** *(repo: weight decay 0.01)* adds a decay term applied directly to the weights:

$$
\theta_t = \theta_{t-1} - \eta\left(\frac{\hat m_t}{\sqrt{\hat v_t}+\epsilon} + \lambda\,\theta_{t-1}\right)
$$

Applying decay **outside** the adaptive scaling is the point of AdamW: with ordinary L2 regularization inside the gradient, the decay would be divided by $\sqrt{\hat v}$ and would act unevenly. *(Background.)*

**Worked example** *(toy: one weight, $\theta_0 = 1$, $\eta = 0.1$, gradients $0.5, 0.25, -0.1$)*.

| step $t$ | $g_t$ | $m_t$ | $v_t$ | $\hat m_t$ | $\hat v_t$ | step $\eta\hat m/\sqrt{\hat v}$ | $\theta_t$ |
|---|---|---|---|---|---|---|---|
| 1 | 0.50 | 0.0500 | 0.000250 | 0.5000 | 0.2500 | 0.1000 | 0.9000 |
| 2 | 0.25 | 0.0700 | 0.000312 | 0.3684 | 0.1562 | 0.0932 | 0.8068 |
| 3 | −0.10 | 0.0530 | 0.000322 | 0.1956 | 0.1074 | 0.0597 | 0.7471 |

Observation: the **first step is exactly $\eta$** whatever the size of the gradient ($\hat m/\sqrt{\hat v} = g/|g| = 1$). Gradients of 0.5, 5 and 50 all give a first step of 0.1. Adam's step size is controlled by $\eta$, not by the gradient scale.

**Why it matters here** *(repo)*. The joint training uses AdamW with $\eta = 2\times10^{-5}$ and weight decay 0.01, over the LoRA parameters and the classifier head only (the 4-bit base is frozen).

**Interview question.** *Why Adam and not SGD for a transformer?* **Answer.** The gradients of different parameters have very different scales (embeddings, attention, MLP, a freshly initialized head). Adam normalizes each parameter's step by its own gradient history, so one learning rate works for all of them. SGD would need per-layer learning rates. This is common practice for transformers, though not a theorem. *(Background.)*

## 18.3 The learning-rate schedule: OneCycle

**Meaning.** The learning rate is not constant. It **warms up** from a small value to a peak, then **anneals** (decreases) to nearly zero.

**Formula** *(repo: `OneCycleLR`, peak $2\times10^{-5}$, `pct_start` = 0.1; PyTorch defaults in the rest, background)*. Start rate $\eta_{\text{init}} = \eta_{\max}/25$, final rate $\eta_{\text{fin}} = \eta_{\text{init}}/10^{4}$. A cosine interpolation $\text{cos}(a\to b, p) = b + \tfrac{a-b}{2}(1+\cos\pi p)$ for progress $p\in[0,1]$. Warm-up from $\eta_{\text{init}}$ to $\eta_{\max}$ over the first 10% of steps, then anneal from $\eta_{\max}$ to $\eta_{\text{fin}}$.

**Worked example** *(total steps $T = 53{,}772$ from the paper; the schedule shape is from the repo)*. Warm-up lasts about 5,376 steps. Computed rates:

| step | learning rate |
|---|---|
| 0 | $8.0\times10^{-7}$ |
| 1,000 | $2.4\times10^{-6}$ |
| 5,376 (peak) | $2.0\times10^{-5}$ |
| 15,000 | $1.8\times10^{-5}$ |
| 26,886 (middle) | $1.2\times10^{-5}$ |
| 40,000 | $3.7\times10^{-6}$ |
| 53,771 (end) | $8.0\times10^{-11}$ |

**Why warm-up.** At the start the adapters and the head are untrained and Adam's second-moment estimate $\hat v$ is based on a few samples. A small initial rate avoids large damaging steps before the statistics settle. *(Background.)*

**Why it matters here** *(repo comments)*. The schedule is defined over the **whole run**. The script has two options for short debugging runs: `--max-steps` also shortens the schedule, while `--stop-after-steps` stops early but keeps the full schedule. A short run with the first option "never sat at peak learning rate". See section 18.9.

**Interview question.** *What would happen with a constant learning rate?* **Answer.** The weights would keep jumping by roughly $\eta$ per step at the end of training, so the final model would be a noisy point. Annealing lets the weights settle into a minimum. (The deepfake paper handles the same noise with weight averaging; here annealing does the job.) *(Background.)*

## 18.4 Batch size, gradient accumulation and steps

**Meaning.** A **micro-batch** is the number of examples in one forward/backward pass. **Gradient accumulation** adds the gradients of several micro-batches before one optimizer step, which simulates a larger batch with less memory.

**Formula** *(repo defaults: micro-batch 2, accumulation 4)*: effective batch $B = 2\times4 = 8$ rows per optimizer step. If each micro-batch loss is divided by the number of accumulation steps $a$, then

$$
\frac1a\sum_{j=1}^{a}\nabla\mathcal{L}_j = \nabla\!\left(\frac1a\sum_{j=1}^{a}\mathcal{L}_j\right),
$$

which is the gradient of the loss over the combined batch. (This works because the gradient of a sum is the sum of the gradients.)

**Worked example.** The paper reports 53,772 steps for 2 epochs, so 26,886 steps per epoch. *If* the run used the repo defaults (effective batch 8) that would mean about $26{,}886\times8 \approx 215{,}000$ marker rows per epoch. This is an **inference from the defaults**, not a number in the paper.

**Interview question.** *Is accumulation identical to a bigger batch?* **Answer.** For the gradient, yes if the loss is normalized the same way. It differs for layers that use batch statistics (batch normalization), which a transformer with layer normalization does not, so here it is equivalent. *(Background.)*

## 18.5 Mixed precision and loss scaling

**Meaning.** Run the forward and backward passes in 16-bit floating point to save memory and time, but keep the master weights in higher precision. **Loss scaling** multiplies the loss by a large factor $S$ so that small gradients do not round to zero.

**Facts** *(background)*. In float16 the smallest normal number is $2^{-14} \approx 6.1\times10^{-5}$ and the smallest subnormal is $2^{-24}\approx6.0\times10^{-8}$. Smaller values become 0 (**underflow**).

**Formula.** Backpropagate $S\cdot\mathcal{L}$. Every gradient is multiplied by $S$ (linearity of the derivative). Before the optimizer step, divide by $S$ again (and skip the step if any value is infinite). *Dynamic* scaling raises $S$ when steps succeed and lowers it when an overflow occurs.

**Worked example.** A gradient value of $10^{-8}$ would underflow to 0 in float16. With $S = 65{,}536$, it is stored as $6.6\times10^{-4}$, which is representable. It is divided by $S$ before the update.

**Why it matters here** *(repo)*. The script uses `autocast` in float16 with a `GradScaler`. (A repo comment mentions a 14.56 GB T4 GPU, which has no native bfloat16 support, so float16 is the natural choice there.) The base weights are 4-bit NF4 ([[notes/proactive-assistant/16-deep-dive-model-lora-quantization|page 16]]).

**Interview question.** *Why must clipping come after unscaling?* **Answer.** The clip threshold refers to the true gradient norm. If you clipped before dividing by $S$, you would compare an inflated norm with the threshold and clip almost always. The repo unscales first (`scaler.unscale_`) and then clips *(repo)*.

## 18.6 Gradient clipping

**Meaning.** Limit the size of one update by rescaling the gradient if its norm is too large.

**Formula** *(repo: max norm 1.0)*: $g \leftarrow g\cdot\min\!\left(1,\ \dfrac{c}{\lVert g\rVert_2}\right)$ with $c = 1$, where $\lVert g\rVert_2 = \sqrt{\sum_j g_j^2}$ is computed over all trainable parameters together.

**Worked example.** $\lVert g\rVert = 0.4$: factor $\min(1, 2.5) = 1$ (unchanged). $\lVert g\rVert = 3$: factor $1/3$. $\lVert g\rVert = 10$: factor $0.1$. The direction is kept; only the length is capped.

**Why it matters here.** A few noisy batches (for instance, ones where only a few markers carry hint supervision) can produce large gradients; clipping prevents one batch from throwing the adapters far off.

**Interview question.** *With Adam, does clipping still matter, since Adam normalizes the step?* **Answer.** It matters through the moment estimates: one huge gradient inflates $v$ for many steps and shrinks the later steps, or inflates $m$ and causes a jump. Clipping limits that. *(Background.)*

## 18.7 LoRA and its optimization: why $B$ starts at zero

**Meaning.** With $y = Wx + \frac{\alpha}{r}BAx$ ([[notes/proactive-assistant/16-deep-dive-model-lora-quantization|page 16]]), only $A$ and $B$ are trained. Initially $B = 0$ so the model equals the pre-trained one.

**Derivation.** Let $u = Ax\in\mathbb{R}^r$ and let $\delta = \partial\mathcal{L}/\partial y$ be the gradient arriving at the layer output. With $s = \alpha/r$:

$$
\frac{\partial\mathcal{L}}{\partial B} = s\,\delta\,u^{\top}, \qquad
\frac{\partial\mathcal{L}}{\partial A} = s\,B^{\top}\delta\,x^{\top}
$$

At $B = 0$ the second gradient is **zero**: $A$ does not move at the first step, while $B$ does. After $B$ becomes non-zero, $A$ starts to learn.

**Worked example** *(toy, $r=1$, $d=2$)*. $A = (1,1)$, $x = (2,1)$, so $u = Ax = 3$. $\delta = (1,-1)$, $s = 2$.

- $\partial\mathcal{L}/\partial B = 2\cdot(1,-1)\cdot3 = (6, -6)$: large, so $B$ moves first.
- $\partial\mathcal{L}/\partial A$ at $B=0$: $2\cdot(0\cdot1+0\cdot(-1))\cdot(2,1) = (0,0)$.
- After $B = (0.1, -0.2)$: $B^\top\delta = 0.1 + 0.2 = 0.3$; $\partial\mathcal{L}/\partial A = 2\cdot0.3\cdot(2,1) = (1.2, 0.6)$.

**Why it matters here.** The zero start guarantees that fine-tuning begins from the pre-trained function, which keeps early training stable.

**Interview question.** *Why not initialize both $A$ and $B$ at zero?* **Answer.** Then both gradients are zero (the gradient of each factor is proportional to the other), so nothing would ever train. One factor is random, the other zero. *(Background.)*

## 18.8 Training through a 4-bit base

**Meaning.** The base weights are stored in NF4 and are **frozen**. During the forward pass they are **dequantized** to 16-bit on the fly, multiplied with the activations, and the result is added to the LoRA branch. Gradients flow **through** the dequantized weights back to the earlier layers' adapters, but no gradient is computed for the base weights themselves. *(Background; the QLoRA recipe.)*

**Why it matters here.** The trainable part is 11.27 million parameters (my estimate, page 16) out of about 1.2 billion; the optimizer state (two numbers per trainable parameter for Adam) is tiny. For 11.27 M parameters in float32 that is $11.27\times10^6\times(4 + 4 + 4)$ bytes (weights, $m$, $v$) $\approx 135$ MB. *(My arithmetic.)*

**Interview question.** *Is the training problem convex?* **Answer.** No. A transformer's loss is non-convex in the weights, so Adam finds a good local solution, not the global minimum. The low-rank constraint restricts the search to a smaller space, which helps stability, but it does not make the problem convex. *(Background.)*

## 18.9 An optimization failure recorded in the repo (not in the paper)

**What the code comments say** *(repo, `train_joint.py`)*. The first full run used a learning rate of $2\times10^{-4}$, the rate of the hint-generation stage, "carried over without checking". The **gate collapsed to chance level** (AUROC 0.4995 at $k=6$ after 28,547 steps) while **generation was unharmed**. The fix was to use $2\times10^{-5}$, the learning rate of the published gate. The collapse was missed by a 200-step smoke test because the OneCycle schedule fully annealed inside 200 steps, so those models never sat at the peak rate. Hence the two flags `--max-steps` (shortens the schedule) and `--stop-after-steps` (keeps the full schedule), and the periodic gate scoring `--eval-every` that turns one number into a curve.

**Lessons** *(my reading)*:

1. **Schedule shape matters in short tests.** A short run with a compressed schedule does not test the regime of the long run.
2. **Measure during training, not only at the end.** An endpoint number cannot tell you when a collapse happened.
3. **Two heads, two learning-rate needs.** A learning rate suited to token generation can destroy a classifier head. *(Hypothesis consistent with the comments, not tested in the paper.)*

**Interview question.** *Tell me about something that went wrong in training.* **Answer.** Use this. State the symptom (gate at chance, AUROC 0.4995, generation fine), the cause (a learning rate 10× too high for the gate, inherited from another stage), why a quick test missed it (the schedule annealed inside the test), and the fix (the published gate rate, a schedule that spans the full run, and mid-training evaluation).

## 18.10 Questions a professor of optimization might ask

- **Why does Adam's first step have size $\eta$?** Bias-corrected $\hat m/\sqrt{\hat v}$ equals $g/|g| = \pm1$ at $t=1$ (table in 18.2).
- **What does weight decay do in AdamW and why is it decoupled?** It shrinks the weights by a factor $(1-\eta\lambda)$ per step independently of the gradient statistics. With $\eta = 2\times10^{-5}$ and $\lambda = 0.01$ that factor is $1 - 2\times10^{-7}$ per step at peak rate. *(Derived from the repo values.)*
- **Why is the gate loss only on layers $\le k$?** Because the head reads layer $k$ (section 18.1).
- **How does the gradient of cross-entropy behave?** It equals $p - y$ at the logit ([[notes/proactive-assistant/15-deep-dive-metrics-calibration-losses|page 15]]).
- **What limits LoRA's expressiveness?** The update has rank at most $r$, so it cannot represent changes that need a higher rank. *(Background.)*

## 18.11 Check yourself

- At step 1 of Adam, what is the update for gradient 3 and $\eta = 0.01$? *(0.01.)*
- What is the clip factor if the gradient norm is 4 and $c = 1$? *(0.25.)*
- Why is $\partial\mathcal{L}/\partial A = 0$ when $B = 0$? *(It is proportional to $B^\top\delta$.)*

Back to the [[notes/proactive-assistant/index|study guide index]].
