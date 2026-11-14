---
title: "Proactive Assistant: Study Guide"
date: 2026-11-09
tags:
  - notes
  - nlp
  - llm
  - edge-ai
---

`nlp` `llm` `edge-ai` · A from-scratch guide to my paper, [arXiv:2610.40611](https://arxiv.org/abs/2610.40611)

> **When to Assist and What to Suggest: Joint Gating and Memory-Grounded Hint Generation in One Compact Decoder.**
> A. J. A. Jubayer Talukder and M. A. Haque. Paper summary: [[work/research/proactive-conversation-assistant|research page]] · Code: [GitHub](https://github.com/JubayerONROB/proactive-conversation-assistant)

This guide is for a reader who knows **nothing** about the topic. Each page explains one group of ideas with plain words, small formulas, and figures. Every number comes from the paper. Small made-up examples are marked **toy example**.

## Start here

If you want everything in one straight line, read the first page. If you only need one topic, jump to it.

| # | Page | You will learn |
|---|---|---|
| 0 | [[notes/proactive-assistant/0-the-whole-story\|The whole story, in order]] | The full paper from zero, step by step |
| 1 | [[notes/proactive-assistant/1-the-task-and-the-gate\|The task and the gate]] | What a proactive assistant does, decision points, threshold, false alarms |
| 2 | [[notes/proactive-assistant/2-language-model-basics\|Language model basics]] | Tokens, layers, hidden states, attention, prefill and decoding |
| 3 | [[notes/proactive-assistant/3-memory-and-prompt\|Memory profile and prompt]] | What the assistant knows about the user and how it is fed to the model |
| 4 | [[notes/proactive-assistant/4-training\|Training: LoRA, 4-bit, losses]] | Fine-tuning a small part of a big model, cross-entropy, focal loss |
| 5 | [[notes/proactive-assistant/5-early-exit-and-unified-decoder\|Early exit and the unified decoder]] | The main idea: one model that gates from a middle layer |
| 6 | [[notes/proactive-assistant/6-evaluation-metrics\|Evaluation metrics]] | Precision, recall, F1, AUROC, exact match, BERTScore, end-to-end scores |
| 7 | [[notes/proactive-assistant/7-experiments-and-findings\|Experiments and findings]] | What we tested and what we found |
| 8 | [[notes/proactive-assistant/8-statistics\|Statistics behind the claims]] | Noise floor, confidence intervals, McNemar, Holm, non-inferiority |
| 9 | [[notes/proactive-assistant/9-human-evaluation\|Human evaluation]] | How people rated the hints and which scores match them |
| 10 | [[notes/proactive-assistant/10-deployment-and-limits\|Deployment and limits]] | Calibration, CPU cost, memory, ethics, what we did not do |
| 11 | [[notes/proactive-assistant/11-glossary\|Glossary]] | Every symbol and term on one page |
| 12 | [[notes/proactive-assistant/12-math-foundations\|Deep dive: math foundations]] | Sum, set, indicator, probability, Bayes, expectation, softmax, from zero |
| 13 | [[notes/proactive-assistant/13-deep-dive-gate-and-end-to-end\|Deep dive: gate and end-to-end score]] | Eq. (1)–(3), threshold sweep, factorization proof, monotonicity proof, oracle ceiling |
| 14 | [[notes/proactive-assistant/14-deep-dive-cost-model\|Deep dive: the cost model]] | Eq. (4), ideal $L/k$, expected cost at 12% triggers, measured vs ideal, why a gate saves less with a small generator |
| 15 | [[notes/proactive-assistant/15-deep-dive-metrics-calibration-losses\|Deep dive: metrics, calibration, losses]] | Confusion matrix, F1 proof, AUROC, AUPRC, ECE/MCE/Brier, cross-entropy, weighted CE, focal loss |
| 16 | [[notes/proactive-assistant/16-deep-dive-model-lora-quantization\|Deep dive: model, LoRA, quantization]] | Attention, layer-$k$ head, prefill vs decoding, LoRA parameter count, NF4, why 4-bit saves memory not time |
| 17 | [[notes/proactive-assistant/17-deep-dive-generation-metrics-and-statistics\|Deep dive: generation metrics and statistics]] | EM, BERTScore, ROUGE, McNemar, Holm, bootstrap, noise floor, Pearson, kappa, non-inferiority |
| 18 | [[notes/proactive-assistant/18-deep-dive-optimization\|Deep dive: optimization]] | Gradient flow through the shared trunk, Adam and AdamW, OneCycle, accumulation, mixed precision, clipping, LoRA's zero start |

**Interview preparation (pages 12–18).** These pages re-derive every formula, with five parts per concept: meaning, formula, worked example, why it matters here, and a likely interview question with a model answer. Numbers are from the paper unless marked *background*, *derived* or *toy*.

## Concept map: where each idea is explained

| Idea | First explained | Derived in the deep dive |
|---|---|---|
| Gate $g_i(t)$, threshold | [[notes/proactive-assistant/1-the-task-and-the-gate\|1]] | [[notes/proactive-assistant/13-deep-dive-gate-and-end-to-end\|13]] |
| End-to-end EM and precision, ceiling | [[notes/proactive-assistant/6-evaluation-metrics\|6]], [[notes/proactive-assistant/7-experiments-and-findings\|7]] | [[notes/proactive-assistant/13-deep-dive-gate-and-end-to-end\|13]] |
| Cost model, early exit | [[notes/proactive-assistant/5-early-exit-and-unified-decoder\|5]] | [[notes/proactive-assistant/14-deep-dive-cost-model\|14]], [[notes/proactive-assistant/16-deep-dive-model-lora-quantization\|16]] |
| Precision, recall, F1, AUROC, AUPRC, calibration | [[notes/proactive-assistant/6-evaluation-metrics\|6]] | [[notes/proactive-assistant/15-deep-dive-metrics-calibration-losses\|15]] |
| Cross-entropy, focal loss, weights | [[notes/proactive-assistant/4-training\|4]] | [[notes/proactive-assistant/15-deep-dive-metrics-calibration-losses\|15]] |
| Transformer, attention, prefill/decode | [[notes/proactive-assistant/2-language-model-basics\|2]] | [[notes/proactive-assistant/16-deep-dive-model-lora-quantization\|16]] |
| LoRA, 4-bit quantization | [[notes/proactive-assistant/4-training\|4]] | [[notes/proactive-assistant/16-deep-dive-model-lora-quantization\|16]], [[notes/proactive-assistant/18-deep-dive-optimization\|18]] |
| Optimizer, schedule, clipping | not in 0–11 | [[notes/proactive-assistant/18-deep-dive-optimization\|18]] |
| EM, BERTScore, ROUGE | [[notes/proactive-assistant/6-evaluation-metrics\|6]] | [[notes/proactive-assistant/17-deep-dive-generation-metrics-and-statistics\|17]] |
| McNemar, Holm, bootstrap, noise floor | [[notes/proactive-assistant/8-statistics\|8]] | [[notes/proactive-assistant/17-deep-dive-generation-metrics-and-statistics\|17]] |
| Human study, kappa, non-inferiority | [[notes/proactive-assistant/9-human-evaluation\|9]] | [[notes/proactive-assistant/17-deep-dive-generation-metrics-and-statistics\|17]] |
| Deployment: calibration, CPU, memory | [[notes/proactive-assistant/10-deployment-and-limits\|10]] | [[notes/proactive-assistant/13-deep-dive-gate-and-end-to-end\|13]], [[notes/proactive-assistant/14-deep-dive-cost-model\|14]], [[notes/proactive-assistant/16-deep-dive-model-lora-quantization\|16]] |

## The paper in five lines

1. A proactive assistant must decide **when** to speak and **what** to say.
2. Scoring each part alone looks better than it is. Behind a real gate, end-to-end exact match falls from 0.2971 to 0.2619.
3. The **memory profile** drives hint quality. Removing it costs 24.7 exact-match points.
4. One 1B model can do both jobs. It decides from layer $k$ and, if needed, **continues the same pass** to write the hint.
5. People rate it level with the matched 1B pipeline and below the 8B one.

## Figures

All figures here are made with Python and matplotlib as vector PDF (fonts embedded) plus a PNG. Each figure has a PDF link under it. Black is normal, red is the important path.
