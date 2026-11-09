---
title: "11. Glossary"
date: 2026-11-09
tags:
  - notes
  - nlp
---

`nlp` · Part of the [[notes/proactive-assistant/index|Proactive Assistant study guide]]

## Symbols

| Symbol | Meaning |
|---|---|
| $D = \langle u_1, \ldots, u_T\rangle$ | The conversation so far, as utterances |
| $D_{\le i}$ | The conversation up to silence $i$ (left context) |
| $M_w$ | Memory profile of wearer $w$ |
| $i$ | Index of a decision point (marker) |
| $p_i$ | Gate score in $[0,1]$ at marker $i$ |
| $t$ | Gate threshold |
| $g_i(t) = \mathbf{1}[p_i \ge t]$ | Gate decision: 1 = speak, 0 = stay quiet |
| $h_i$ | Hint written at marker $i$ (1 to 3 words) |
| $h_i^{*}$ | Reference (correct) hint |
| $m_i = \mathbf{1}[h_i = h_i^{*}]$ | 1 if the hint matches exactly |
| $\mathcal{T}$ | Set of reference triggers (3,356) |
| $N$ | Number of test markers (28,058) |
| $L$ | Number of layers (16 in Llama-3.2-1B) |
| $k$ | Layer where the gate reads the hidden state (6 or 10) |
| $d$ | Hidden size of the model |
| $h_k$ | Hidden state after $k$ layers (do not confuse with hint $h_i$) |
| $W_c \in \mathbb{R}^{2\times d}$ | Classifier head: 2 classes |
| $W$, $A$, $B$ | Frozen weight matrix and the two LoRA matrices |
| $r$, $\alpha$ | LoRA rank (16) and scale (32) |
| $\gamma$ | Focal-loss focusing strength (1.5) |
| $c_{\text{gen}}$ | Cost of one prefill of the separate generator |
| $R$ | Gate recall, $\frac{1}{|\mathcal{T}|}\sum_{i\in\mathcal{T}} g_i$ |
| $\text{EM}_{\text{fwd}}$ | Exact match on the triggers the gate forwards |

## Terms

**ASL.** The loss recipe used with the RoBERTa-large gate that gave its best result (pairs focal loss with full fine-tuning).

**AUPRC / AUROC.** Threshold-free ranking scores. See [[notes/proactive-assistant/6-evaluation-metrics|page 6]].

**Base model.** A pre-trained language model before our fine-tuning.

**BERTScore.** A meaning-based text similarity score using contextual word vectors.

**Calibration.** How well predicted probabilities match real frequencies. Measured by ECE.

**Cascade.** A pipeline where a cheap model runs first and a costly one runs only if needed.

**Classifier head.** A small matrix that turns a hidden state into class scores.

**Cluster bootstrap.** Resampling whole dialogues to get honest confidence intervals.

**Decoding.** Writing the output one token at a time.

**Decoder / encoder.** Decoder models (Llama, Qwen) read left to right. Encoder models (RoBERTa) read the whole text both ways.

**Decision point / marker.** A silence between utterances where the assistant decides.

**Early exit.** Stopping the forward pass at an intermediate layer.

**ECE.** Expected calibration error.

**EM (exact match).** The hint equals the reference exactly.

**End-to-end (e2e).** Scoring gate and generator together, using Equation (2).

**FAR.** False-alarm rate, $FP/(TN+FP)$.

**Focal loss.** A loss that down-weights easy examples.

**Gate.** The model part that decides whether to speak.

**Generator.** The model part that writes the hint.

**Hallucination.** A hint that is made up and not grounded in the dialogue or profile.

**Hidden state.** The vector for a token after some layers.

**Holm correction.** A method to correct $p$-values for many tests.

**KV cache.** Saved keys and values so old tokens are not recomputed during decoding.

**Krippendorff's $\alpha$.** Agreement between raters beyond chance.

**LlamaPIE.** The earlier system (Chen et al., 2025) that this paper's baseline follows.

**LoRA.** Low-rank adaptation: train two thin matrices instead of the full weights.

**Logit.** A raw score before softmax.

**McNemar test.** A paired test for two classifiers on the same items.

**Native judge.** LlamaPIE's own LLM-based rating prompt.

**NF4.** A 4-bit number format for model weights.

**Noise floor.** The F1 difference between two runs of the same configuration (0.0070).

**Non-inferiority.** Showing "not worse than by more than a margin".

**Oracle gate.** A perfect gate, used to compute ceilings.

**PA-F1.** F1 of the gate's per-marker decision.

**Prefill.** Reading the whole prompt in one pass.

**Prefix caching.** Reusing the computation of a shared prompt beginning.

**Pre-registration.** Fixing the analysis plan before any data exist.

**Quantization.** Storing weights with fewer bits.

**Softmax.** Turns scores into probabilities that sum to 1.

**Token.** A piece of text that the model reads as one unit.

**Trigger.** A marker where the reference says a hint is needed.

**Unified decoder.** Our model that gates from layer $k$ and continues to write the hint in the same pass.

**Uptake.** LlamaPIE's 5-point human rating of how helpful a hint was.

## More terms

**Ablation.** Removing or changing one part to measure its effect.

**Adapter.** The small trained LoRA matrices that sit on a frozen base model.

**Annotator.** A person who rates items in a study.

**ASR.** Automatic speech recognition: speech audio to text.

**Attention head.** One of several parallel attention computations inside a layer.

**Baseline.** An earlier or simpler system used for comparison.

**Batch size.** How many examples run together. Batch size one is one at a time.

**bf16 / fp16 / fp32.** Number formats with 16, 16 and 32 bits per value.

**Checkpoint.** A saved copy of the model weights at some training step.

**Cosine similarity.** Closeness in direction of two vectors.

**Diarization.** Labelling which speaker is speaking.

**Dropout.** Randomly switching off values in training to avoid overfitting (5% here).

**Epoch.** One full pass over the training data.

**Eager mode.** Running a PyTorch model step by step without compilation.

**Forward pass.** One run of an input through the layers.

**Frozen.** Not changed by training.

**HUD.** Head-up display, the glasses display where the hint appears.

**ICSI.** A corpus of real meeting recordings used for a check on natural data.

**idf.** Inverse document frequency: weights rare words more (turned off in our BERTScore).

**Latency.** Time from input to output for one request.

**Left context.** The conversation before the current silence, never the future.

**MLP.** The feed-forward network inside each layer.

**ONNX Runtime.** A fast inference engine for exported models.

**Operating point.** One chosen threshold and the precision, recall and false-alarm rate it gives.

**Overfitting.** Doing well on training data but badly on new data.

**Parameter.** One learned number in a model.

**Prevalence.** The share of positive cases in the data.

**Reference-free.** Judged without seeing the correct answer.

**Rubric.** Written rules that a judge follows.

**Seed.** A number that fixes the random choices in a run.

**Source corpora (perl, soda, synthetic).** The three dialogue collections the test dialogues come from.

**Step.** One weight update from one batch.

**Subsample.** A smaller part of the data used when a test is costly.

**Utterance.** One thing one person says.

**Vocabulary.** The full list of tokens a model knows.

**Wearer.** The person who uses the assistant and owns the memory profile.

**Zero-shot / few-shot.** Doing a task with no examples, or with a few examples in the prompt.
