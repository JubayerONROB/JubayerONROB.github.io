---
title: "Proactive Conversation Assistant: LLM Pipeline"
date: 2025-02-01
tags:
  - research
  - nlp
  - edge-ai
  - llm
status: ongoing
---

`nlp` `edge-ai` `llm` · Feb 2025 – Present · **Status: Ongoing (BSc Thesis) · [arXiv:2610.40611](https://arxiv.org/abs/2610.40611)**

[GitHub →](https://github.com/JubayerONROB/proactive-conversation-assistant)

## Abstract

A proactive assistant listens to a conversation and sometimes offers a short, memory-grounded hint, like a name the person is reaching for. It has to decide both *when* to help and *what* to suggest. Current systems use a small gate model plus a larger generator model. This work tests both together on 28,058 decision points, and then asks whether one compact decoder can do both jobs. The result is described in the paper *When to Assist and What to Suggest: Joint Gating and Memory-Grounded Hint Generation in One Compact Decoder* (A. J. A. Jubayer Talukder and M. A. Haque, [arXiv:2610.40611](https://arxiv.org/abs/2610.40611)).

## Methodology

The two-model pipeline follows LlamaPIE (Chen et al., 2025) and was reimplemented for this study. A small gate decides whether a hint is needed, and a larger generator writes it only when the gate fires. The new design is a single 1B decoder with one shared adapter. It reads the gate decision from an intermediate layer, and when the gate fires it continues through the remaining layers in the same pass to write the hint. Both designs read a persistent user memory profile.

```mermaid
flowchart TD
    A[Conversation + user memory profile] --> B{Gate: help now?}
    B -- no --> C[Stay silent]
    B -- yes --> D[Generate a short hint]
```

In the two-model pipeline the gate and the generator are separate models. In the unified decoder the gate reads layer 6 or 10 of the same 16-layer model that then writes the hint.

## Key findings

- Scores for the generator alone are best-case numbers that assume a perfect gate. Behind a real gate, end-to-end exact match is 0.2619 against a ceiling of 0.2971, so there is a lot of room to improve.
- A gate pays off through precision and compute. It cuts generator calls by 7.62×, which saves 4.39× wall-clock time with an 8B generator but only 1.38× with a 1B one, because the gate itself takes most of the time.
- The memory profile drives hint quality. Removing it costs 24.7 exact-match points. A larger generator or retrieval over the profile adds nothing on exact match.
- One 1B decoder can do both jobs. At its final checkpoint it matches or beats the two-model pipelines on automatic end-to-end measures, with 1.31–1.76× less wall-clock time than the matched 1B pipeline.
- In a human evaluation, people rate the single model level with the matched 1B pipeline and below the 8B one. They also confirm the memory effect.

## Results

| Metric | Result |
|---|---|
| Decision points evaluated | 28,058 (3,356 triggers) |
| End-to-end exact match behind a real gate (1B generator) | 0.2619, against a ceiling of 0.2971 |
| End-to-end precision | 0.2387 |
| Reduction in generator calls | 7.62× |
| Wall-clock saving from the gate | 4.39× (8B generator), 1.38× (1B generator) |
| Exact-match drop without the memory profile | 24.7 points (BERTScore 0.57 to 0.35) |
| Unified decoder, end-to-end exact match | 0.2929 (exit at layer 6), 0.2908 (layer 10), against 0.2619 |
| Unified decoder, wall-clock time | 1.31–1.76× less than the matched 1B pipeline, 3.41× less than the 8B pipeline (layer 6) |
| Resident weights, unified decoder | up to 1.05 GB (one base model plus a 42 MB adapter) |

**Human evaluation.** 1,144 ratings over 32 dialogues. With the memory profile, hints from the 8B generator scored 4.01 on the 5-point uptake scale, against 3.18 without it. The unified model was level with the matched 1B pipeline and lower than the 8B pipeline. Of the automatic scores, LlamaPIE's own judge tracked human ratings best, and exact match tracked them least, so the paper reports exact match as a strict lower bound.

## Future work

Extending the shared-adapter decoder to more interruption categories and testing on-device latency on real wearable hardware.

## Related

[[work/projects/hybrid-router-vinci-monsoon|Hybrid Router: Two-Stage Local-First LLM Agent]] — similar two-stage, cost-aware routing philosophy applied to LLM task delegation.
[[notes/proactivity|Proactivity in Conversational AI]]
