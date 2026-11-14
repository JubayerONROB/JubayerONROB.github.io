---
title: "16. Interview deep dive: the model, LoRA and quantization"
date: 2026-11-14
tags:
  - notes
  - math
  - interview
---

`math` `interview` · Part of the [[notes/proactive-assistant/index|Proactive Assistant study guide]]

**What is from where.** From the paper: $L = 16$ layers, the head $W_c\in\mathbb{R}^{2\times d}$, exit depths $k\in\{6,10\}$, one shared LoRA adapter, 42 MB vs 957 MB, 4.99 GB vs 1.65 GB. **Background** (public model configuration of Llama-3.2-1B, not in the paper): $d = 2048$, 32 attention heads of width 64, 8 key/value heads, feed-forward width 8192, vocabulary 128,256. **Code** (your repository): LoRA rank $r = 16$, scale $\alpha = 32$, adapters on the seven projections `q,k,v,o,gate,up,down`. Parameter counts below are **my estimates** from those numbers.

## 16.1 Tokens and embeddings

**Meaning.** The tokenizer cuts text into **tokens**, each with an integer ID. The **embedding matrix** $E \in \mathbb{R}^{V\times d}$ has one row per vocabulary entry. Looking up the row for a token gives its **embedding**, a vector of $d$ numbers.

**Formula.** For token ID $c$, $x = E_{c,:}\in\mathbb{R}^{d}$. Number of parameters $= V\cdot d$.

**Worked example.** $V = 128{,}256$ and $d = 2048$ give $128256\times2048 = 262{,}668{,}288$ parameters, about 21% of the model *(my estimate, background config)*. A prompt of 676 tokens (test split, with the profile *(paper)*) becomes a $676\times2048$ matrix.

**Why it matters here.** The embedding table is large and stays in higher precision when the rest is quantized (section 16.8).

**Interview question.** *What is the sequence the transformer actually sees?* **Answer.** A matrix with one $d$-dimensional row per token, plus position information. Each layer maps that matrix to a new matrix of the same shape.

## 16.2 A transformer layer, and attention

**Meaning.** Each layer has two parts joined by **residual connections** (the input is added back). **Attention** lets each token read from the earlier tokens. The **MLP** transforms each token on its own.

**Formula.** For one head, with queries $Q$, keys $K$, values $V$ (all linear maps of the layer input) and key width $d_k$:

$$
\text{Attention}(Q,K,V) = \text{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right)V
$$

The division by $\sqrt{d_k}$ keeps the dot products from growing with $d_k$, which would push softmax into a flat-gradient region. *(Background.)* In a **decoder** model a **causal mask** sets scores for later tokens to $-\infty$, so token $j$ reads only tokens $\le j$. This is what makes the "left context only" rule in the paper true by construction.

**Worked example** *(toy numbers)*. One query $q = (1, 0)$, two keys $k_1 = (1,0)$, $k_2 = (0,1)$, values $v_1 = (2,0)$, $v_2 = (0,4)$, $d_k = 2$.

1. Scores: $q\cdot k_1/\sqrt2 = 0.7071$ and $q\cdot k_2/\sqrt2 = 0$.
2. Softmax: $e^{0.7071} = 2.028$, $e^0 = 1$. Weights $= (2.028/3.028,\ 1/3.028) = (0.670,\ 0.330)$.
3. Output $= 0.670\,(2,0) + 0.330\,(0,4) = (1.340,\ 1.321)$.

The query is closest to $k_1$, so most of the output comes from $v_1$.

**Why it matters here.** The 16 layers of Llama-3.2-1B are stacks of these. The gate reads the result after $k$ of them.

**Interview question.** *Is the cost really proportional to the number of layers?* **Answer.** For a fixed prompt, yes: every layer does the same work, so $k$ layers cost $k/L$ of $L$. Per layer the work has a part linear in the prompt length $n$ (projections and MLP, about $12nd^2$ multiply-adds) and a part quadratic in $n$ (attention scores, about $2n^2d$). Their ratio is $n/(6d)$. For $n = 676$ and $d = 2048$ that is $676/12288 = 0.055$, so attention's quadratic part is only about 5% of a layer at this prompt length. *(Rough background estimate; it ignores the key/value head sharing and the exact MLP shape.)* That is why Equation (4) can ignore it.

## 16.3 Hidden state and the classifier head at layer $k$

**Meaning.** The **hidden state** $h_\ell$ is the vector for a token after $\ell$ layers. The **classifier head** $W_c$ is a small matrix that reads the hidden state and produces two **logits**.

**Formula.**

$$
z = W_c\, h_k + b_c \in \mathbb{R}^{2}, \qquad p_i = \text{softmax}(z)_{\text{trigger}} = \sigma(z_{1} - z_{0}), \qquad W_c\in\mathbb{R}^{2\times d}
$$

$h_k$ is the hidden state **after $k$ layers** at the marker's position (the last position of the window). $\sigma$ is the sigmoid (page 12). In the code the state is taken **un-normalized**, with no final norm, exactly as a full-depth pass would produce at that point.

**Worked example.** $d = 2048$, so $W_c$ has $2\times2048 = 4096$ weights plus 2 biases $= 4098$ parameters *(my estimate)*. Take a toy $d=3$: $W_c = \begin{pmatrix}0.5 & -1 & 0\\ -0.5 & 1 & 0.2\end{pmatrix}$, $h = (1, 0.5, 2)$, $b = 0$. Then $z = (0.5 - 0.5 + 0,\ -0.5 + 0.5 + 0.4) = (0,\ 0.4)$. $p = \sigma(0.4 - 0) = 0.599$.

**Why it matters here.** The head sits at layer $k$. It does not approximate the final output; it decides whether the layers $k{+}1..L$ should run at all *(paper)*. The shared trunk is trained on **two** losses, the gate loss and the hint loss, with full-depth passes in training.

**Interview question.** *Why can a gate read a middle layer at all?* **Answer.** Hidden states of a pre-trained decoder already carry task-relevant information well before the last layer, and fine-tuning with the gate loss on the layer-$k$ readout shapes layers $1..k$ to make the trigger decision linearly readable. The paper measures the price: at the final checkpoint the gate F1 is 0.8022 at $k=6$ and 0.8164 at $k=10$, against 0.8002 for the separate gate; over three seeds $k=10$ ties it and $k=6$ is 0.0156 below *(paper)*.

## 16.4 Prefill, decoding and the KV cache

**Meaning.** **Prefill** runs the whole prompt through all layers in one parallel pass. **Decoding** then produces one token per pass, reusing stored keys and values (the **KV cache**) of earlier tokens.

**Formula.** Per layer, prefill computes keys and values for all $n$ prompt tokens: $O(n)$ rows of work per projection. Each decoded token adds one row of work and reads the cache.

**Worked example.** Prompt $n = 676$, hint of 3 tokens. Prefill does the work of 676 token-rows through every layer. Decoding does 3 more token-rows (plus attention over the cache). So prefill is about $676/3 \approx 225$ times the token-rows of decoding. *(My arithmetic; the paper says decoding is cheap and counts only prefill in Equation (4).)*

**Why it matters here.** Early exit saves prefill work: a silent marker never goes past layer $k$, and never starts decoding.

**Interview question.** *Why does a triggered marker not pay prefill twice?* **Answer.** In the unified model the cache of layers $1..k$ from the gate readout is the same cache the continuation uses. The cascade must encode a different prompt (with the memory profile) from scratch for the separate generator.

## 16.5 Early exit

**Meaning.** Stop the forward pass at an intermediate layer when the result is enough to decide. Here the "decision" is whether to continue.

**Formula.** The rule is $g_i = \mathbf{1}[\,\sigma(W_c h_k + b_c)\ge t\,]$; if $g_i = 0$ stop, else continue with layers $k{+}1..L$ and decode.

**Why it differs from confidence-based exit** *(paper)*. In ordinary early exit an intermediate classifier **approximates** the deep output and exits when confident. Here the readout decides **whether the deep computation should run at all**. The router and the expert are the **same weights**.

**Interview question.** *Is there a train/inference mismatch?* **Answer.** Yes, by design: training always runs full depth so the hint loss can shape layers $k{+}1..L$ even for examples that will be silent; only inference short-circuits. This is standard early-exit practice. *(Repo code.)*

## 16.6 LoRA: $W + BA$

**Meaning.** **LoRA** (low-rank adaptation) freezes a big weight matrix $W$ and trains a small low-rank update.

**Formula.** For a frozen $W\in\mathbb{R}^{d_{out}\times d_{in}}$, trainable $B\in\mathbb{R}^{d_{out}\times r}$ and $A\in\mathbb{R}^{r\times d_{in}}$ with **rank** $r\ll\min(d_{in},d_{out})$:

$$
W' = W + \frac{\alpha}{r}\,BA, \qquad y = W'x = Wx + \frac{\alpha}{r}B(Ax)
$$

$\alpha$ is a scale (so the effective update is $\frac{\alpha}{r}BA$). $B$ starts at zero so $W' = W$ at the start. A full update would need $d_{out}d_{in}$ numbers; LoRA needs $r\,(d_{in}+d_{out})$.

**Why a low-rank update can be enough** *(background)*. The needed change for a new task is assumed to lie in a low-dimensional subspace. A matrix of rank $r$ is a sum of $r$ outer products, so $BA$ has far fewer free numbers than a full $d\times d$ matrix.

**Worked example** *(parameter count, my estimate)*. $r=16$, $d = 2048$, key/value width $8\times64 = 512$, feed-forward width 8192.

| projection | shape $d_{in}\to d_{out}$ | $r(d_{in}+d_{out})$ |
|---|---|---|
| q | 2048 → 2048 | 65,536 |
| k | 2048 → 512 | 40,960 |
| v | 2048 → 512 | 40,960 |
| o | 2048 → 2048 | 65,536 |
| gate | 2048 → 8192 | 163,840 |
| up | 2048 → 8192 | 163,840 |
| down | 8192 → 2048 | 163,840 |
| **per layer** | | **704,512** |

Over 16 layers: $704{,}512\times16 = 11{,}272{,}192$ trainable parameters. A full $2048\times2048$ matrix has 4,194,304 weights, and its LoRA update has $16\times4096 = 65{,}536$: **64 times fewer**.

**Why it matters here.** One base model plus **one shared adapter** serves both objectives (gate and hint) *(paper)*.

**Interview question.** *What does $\alpha/r$ do?* **Answer.** It scales the update so that changing the rank $r$ does not change the update's overall size. With $\alpha = 32$ and $r = 16$ the factor is 2. *(Background.)*

## 16.7 Why a second adapter is 42 MB and a second base is 957 MB

**Facts from the paper.** A second adapter costs **42 MB**. A second 4-bit base would cost **957 MB**. The saving is $957 - 42 = 915$ MB, and 957/42 = 22.8 times. A probe with one 4-bit base, two adapters and the head used **1.05 GB**: $957 + 2\times42 = 1041$ MB $\approx 1.05$ GB. ✓

![Memory figures](/attachments/notes/proactive-assistant/pa7-memory.png)
*Figure 29. (a) 4-bit weights shrink the 16-layer decoder from 4.99 GB to 1.65 GB. (b) A second adapter is 42 MB where a second base would be 957 MB. All numbers are from the paper. [PDF](/attachments/notes/proactive-assistant/pa7-memory.pdf)*

**Derivation of why the two sizes differ so much** *(my estimate from the public config)*.

1. **Count.** The base has about $973$ M weights in the linear layers of the 16 blocks plus $263$ M in the embedding table $\approx 1.24$ B. The adapter has $11.27$ M. Ratio $\approx 110\times$ in count.
2. **Bytes per parameter.** The base is stored in about $4.13$ bits ($\approx0.516$ byte) per linear weight (section 16.8); the adapter is kept in 32-bit ($4$ bytes). That is $8\times$ more bytes per parameter for the adapter.
3. **Net.** Base: $973\,\text{M}\times0.516 \approx 502$ MB, plus the embedding table in 16-bit ($263\,\text{M}\times2 = 525$ MB): $\approx1{,}027$ MB. Adapter: $11.27\,\text{M}\times4 = 45$ MB. Ratio $1027/45 = 22.8$, **the same ratio as the paper's 957/42**.

**How good is the estimate?** My adapter size is 45 MB (43.0 MiB) against the paper's 42 MB, and my base is 1,027 MB (980 MiB) against the paper's 957 MB. They agree within about 7%. **I cannot reproduce the paper's exact 42 and 957**: the exact figures depend on the storage dtype, what is saved and rounding, which the paper does not state. Present the derivation as an order-of-magnitude explanation, not an exact match.

**Interview question.** *Why is the adapter ~23 times smaller than the second base if the parameter count ratio is ~110?* **Answer.** Because the base is stored in 4-bit while the adapter is in 32-bit: that is about 8 times more bytes per adapter parameter, so $110/8\approx14$; the remaining factor comes from the large embedding table kept in 16-bit, which my estimate gives as the 525 MB term. The point for the paper is that the second model's **weights** are the cost, and a shared trunk removes them.

## 16.8 Quantization: 4-bit and NF4

**Meaning.** **Quantization** stores weights with fewer bits. **NF4** (NormalFloat 4) uses 16 representable values placed at the quantiles of a normal distribution, because pre-trained weights are roughly bell-shaped.

**Formula** *(background)*. Cut the weights into blocks of 64. For a block $w$, store the largest magnitude $s = \max|w_j|$ and for each weight the 4-bit index of the nearest codebook value $c_m$:

$$
\hat w_j = s\cdot c_{\,\text{idx}_j},\quad \text{idx}_j = \arg\min_{m}\big|\,w_j/s - c_m\,\big|, \quad c_m\in[-1,1]\ (16\text{ values})
$$

With **double quantization** the 32-bit scales $s$ are themselves stored in 8 bits with their own scale per 256 values.

**Bits per weight** *(my arithmetic)*: $4 + \dfrac{8}{64} + \dfrac{32}{64\times256} = 4 + 0.125 + 0.002 = 4.127$ bits.

**Worked example** *(toy)*. A block with weights $(0.8, -0.4, 0.1, \ldots)$ and $s=0.8$. Divide by $s$: $(1.0, -0.5, 0.125)$. Round each to the nearest codebook value, for instance $1.0\to1.0$, $-0.5\to-0.4$, $0.125\to0.1$ (toy codebook entries). Dequantized: $(0.8, -0.32, 0.08)$. The storage is 4 bits per weight plus the shared scale. The small rounding errors are why fine-tuning with LoRA on top is used (the adapters correct for them).

**Why memory goes down only 3×, not 8×.** Paper: the 16-layer decoder is **4.99 GB** in fp32 and **1.65 GB** in NF4: $4.99/1.65 = 3.02$. The ideal for 32→4.13 bits is $32/4.127 = 7.75\times$. **My explanation** *(estimate, background config)*: only the linear layers are quantized; the embedding table (263 M weights, 1.05 GB in fp32) stays in high precision. $973\,\text{M}\times0.516 = 0.50$ GB, plus the embedding table in fp32 1.05 GB, gives 1.55 GB against the paper's 1.65 GB. Also the fp32 total, $(973+263)\,\text{M}\times4 = 4.94$ GB, matches the paper's 4.99 GB. So an unquantized embedding table explains most of the gap from 8× to 3×.

**Interview question.** *Does quantization change the model's function?* **Answer.** Slightly: it adds rounding error to the weights. The paper checks the ONNX NF4 variant against the GPU model: gate probabilities correlate at $r=0.998$ ($k=6$) and $0.991$ ($k=10$), decisions agree on 100.0% and 96.7% of sampled markers, and hints are identical on 90% and 95% of 20 triggered markers *(paper)*.

## 16.9 Why 4-bit saves memory but not CPU time

**Paper facts** *(Table S5, 4-core CPU, batch size one)*: ONNX Runtime gate at $k=6$ takes **1,793 ms** in NF4 against **1,611 ms** in fp32. Half precision is slower still: PyTorch's gate takes 22,054 ms in bf16 and 17,683 ms in fp16 against 4,330 ms in fp32, because the CPUs lack the instructions that make half precision fast.

**Derivation: memory-bound or compute-bound** *(background)*. A forward pass multiplies the weights by activations. For $P$ weights and $n$ tokens it does about $2nP$ floating-point operations, and must read $P\,b$ bytes of weights ($b$ = bytes per weight). The ratio, **FLOPs per byte read**, is

$$
\text{intensity} = \frac{2nP}{P\,b} = \frac{2n}{b}.
$$

| situation | $n$ | $b$ | intensity (FLOPs/byte) |
|---|---|---|---|
| decode one token, fp32 | 1 | 4 | 0.5 |
| decode one token, NF4 | 1 | 0.516 | 3.9 |
| prefill 676 tokens, fp32 | 676 | 4 | 338 |
| prefill 676 tokens, NF4 | 676 | 0.516 | 2,637 |

When the intensity is **low** (decoding), the processor waits for memory, so fewer bytes per weight means faster. When it is **high** (our prefill over hundreds of tokens at batch size one), the processor is busy computing, so shrinking the bytes does not help. Moreover 4-bit weights must be **dequantized** to 16- or 32-bit before the multiply, which adds work. So NF4 cuts memory (4.99 GB → 1.65 GB) and does not speed up the compute-bound gate (1,793 vs 1,611 ms) *(paper)*.

**Why it matters here.** Quantization is a **memory** choice, and the paper reports its latency as unchanged or slightly worse. The speed-up comes from early exit instead (2.86× at $k=6$).

**Interview question.** *When would 4-bit weights speed up inference?* **Answer.** When the workload is memory-bound, for instance decoding a long sequence token by token at small batch, where each step must read all the weights. In this paper the gate is a prefill over several hundred tokens, which is compute-bound on the CPU, so it does not.

## 16.10 Check yourself

- Compute the LoRA parameters of one $2048\to2048$ projection at $r=8$. *($8\times4096 = 32{,}768$.)*
- For $d = 4$ and $W_c = \begin{pmatrix}1&0&0&0\\0&1&0&0\end{pmatrix}$, what are the logits of $h = (3,1,5,7)$? *($(3, 1)$; $p = \sigma(1-3)=0.119$ for "trigger" if the second row is the trigger class.)*
- Why is 957 MB + 2 × 42 MB ≈ 1.05 GB? *(They add to 1,041 MB; the paper says "up to 1.05 GB".)*

Next: [[notes/proactive-assistant/17-deep-dive-generation-metrics-and-statistics|17. Deep dive: generation metrics and statistics]]
