---
title: "5. Training and progressive unfreezing"
date: 2026-11-10
tags:
  - notes
  - deep-learning
---

`deep-learning` · Part of the [[notes/pairclip-swa/index|PairCLIP-SWA study guide]]

## 5.1 Fine-tuning a pre-trained model

We do not train from nothing. We start from the **pre-trained OpenCLIP tower** and a **random linear head**, and then **fine-tune**. Before any adaptation the model scores **45.80%** on the validation set. That is chance level, because the head is random.

The question is how much of the tower to change. This is a trade-off:

- change **too little** (a near-linear probe): the model under-fits the fine forensic evidence;
- change **too much** (full fine-tuning): the model can destroy the pre-trained features and over-fit the training set. Fine-tuning can distort pre-trained features and hurt robustness outside the training distribution.

## 5.2 Progressive unfreezing

We change the tower **gradually**. At epoch $e$ the head and the **last $k(e)$ blocks** are trainable:

$$
k(e) = \min\!\left(2 + \lfloor e/2 \rfloor,\ K_{max}\right), \qquad K_{max} = 14 \tag{10}
$$

Everything else (the patch embedding, the positional embedding, $W_{proj}$ and the early blocks) stays **frozen**. The symbol $\lfloor\cdot\rfloor$ means "round down". So $k$ goes 2, 2, 3, 3, 4, 4, ... one more block every two epochs.

![Progressive unfreezing](/attachments/notes/pairclip-swa/pc7-unfreezing.png)
*Figure 9. Trainable blocks (red) grow while the prefix stays frozen. The design cap of 14 was not reached. [PDF](/attachments/notes/pairclip-swa/pc7-unfreezing.pdf)*

At $e = 0$ the model is a **linear probe plus two blocks**, so early gradient updates act on an almost intact CLIP space. Newly unfrozen tensors join the optimizer as **fresh parameter groups with zero moment estimates**.

| Stage | Trainable parameters | Share |
|---|---|---|
| $k = 2$ (epoch 0) | 25,193,986 | 8.29% |
| $k = 8$ (epochs 12–13) | 100,771,330 | 33.15% |
| $k = 11$ (epochs 18–19, **reported run**) | 138,560,002 | 45.58% |
| $k = 14$ (design cap, not reached) | 176,348,674 | 58.02% |
| Frozen in the reported run | 165,407,744 | 54.42% |
| Frozen by design (guaranteed) | 127,619,072 | 41.98% |

The 20-epoch budget ended at $k = 11$, so the cap of 14 was never used. At least **41.98%** of the tower can never move by design.

## 5.3 The loss: plain cross-entropy

Training minimizes the **unweighted two-way cross-entropy** (see [[notes/proactive-assistant/4-training|the earlier guide]] for the formula $-\log p_t$). We do not need class weights or focal loss here, because **every batch is already balanced** (16 real + 16 fake).

## 5.4 The optimizer

An **optimizer** decides how to change the weights from the gradient. We use **AdamW**:

- learning rate $\eta_0 = 10^{-4}$;
- **weight decay** $\lambda = 0$. With $\lambda = 0$, AdamW is exactly plain **Adam**.

**Why no weight decay?** Weight decay pulls the weights toward zero. For a fine-tuned pre-trained model, it would pull the trainable suffix **away from its pre-trained values**, the distortion that harms robustness. Regularization here is **structural** instead:

1. 54.42% of the tower never moves;
2. batches are exactly balanced;
3. weight averaging smooths the path ([[notes/pairclip-swa/6-weight-averaging|page 6]]).

The paper admits that the non-averaged suffix does overfit (see the loss curve), so a sweep over $\lambda$ remains worth running.

## 5.5 Mixed precision

Training uses **float16 automatic mixed precision (AMP)** with **dynamic loss scaling**.

- float16 uses 16 bits per number, so memory and time drop. But very small gradients can round to zero (**underflow**).
- **Loss scaling** multiplies the loss by a large factor before backpropagation so gradients stay representable, and divides it out before the update. "Dynamic" means the factor adjusts itself during training.

## 5.6 Early stopping

**Early stopping** ends training when validation accuracy stops improving. We watch the **non-averaged** validation accuracy with **patience 8**: if it does not improve for 8 epochs in a row, stop. The reported run used epochs 0–19.

## 5.7 Reported configuration (Table IV)

| Setting | Value |
|---|---|
| Backbone | OpenCLIP ViT-L/14, OpenAI weights |
| Initialization | pre-trained tower, random linear head |
| Training corpus | 85,380-image 1:1 subsample |
| Batch size | 32 (16 + 16), 2× T4 GPUs, DataParallel |
| Optimizer | AdamW, $\eta_0 = 10^{-4}$, $\lambda = 0$ |
| Precision | AMP float16, dynamic loss scaling |
| Epochs | 0–19 |
| Unfreezing | $k(e) = \min(2 + \lfloor e/2 \rfloor, 14)$; reached $k = 11$ |
| SWA | starts at epoch 12; SWALR to $10^{-5}$, cosine, 10 epochs |
| Early stopping | patience 8 on non-averaged validation accuracy |
| Stage-1 encoder | CLIP ViT-L/14 (HuggingFace), frozen, block size $B = 1000$ |

## 5.8 Words used on this page

- **Gradient.** The direction that changes the weights to lower the loss.
- **Optimizer (Adam, AdamW).** The rule that turns gradients into weight updates.
- **Learning rate.** The size of each update step.
- **Weight decay.** A penalty that pulls weights toward zero.
- **Moment estimates.** Running averages of the gradient that Adam keeps for each weight.
- **Parameter group.** A set of weights updated with the same settings.
- **Mixed precision / AMP.** Using 16-bit numbers where safe to save memory and time.
- **Loss scaling.** Multiplying the loss so tiny gradients do not vanish in float16.
- **Epoch.** One full pass over the training data.
- **Early stopping / patience.** Stop when validation stops improving for a set number of epochs.
- **Linear probe.** Training only a new linear head on frozen features.
- **Overfitting.** Doing well on training data but not on new data.

## 5.9 Check yourself

- How many blocks are trainable at epoch 0, and at the end of the reported run?
- Why is plain cross-entropy enough here?
- Why is weight decay set to zero?

Next: [[notes/pairclip-swa/6-weight-averaging|6. Stochastic weight averaging]]
