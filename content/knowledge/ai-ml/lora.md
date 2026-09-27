---
title: LoRA
date: 2025-10-01
tags:
  - notes
  - ai-ml
  - llm
---

`lora` `unsloth` `fine-tuning`

LoRA (Low-Rank Adaptation) freezes a pretrained model's weights and injects small trainable low-rank matrices into each layer instead of updating the full weight matrix. This cuts the number of trainable parameters by orders of magnitude, which is what makes fine-tuning large models feasible on a single consumer GPU — the use case tools like Unsloth are built around.

It's a different lever from the shared-adapter approach in the [[work/research/proactive-conversation-assistant|Proactive Conversation Assistant]]: LoRA reduces *training* cost on a fixed architecture, while adapter-sharing there reduces *inference-time resident weights* by having two tasks share one decoder.

Related:

→ [[knowledge/ai-ml/model-optimization|Model Optimization]]
→ [[work/research/proactive-conversation-assistant|Proactive Conversation Assistant]]
