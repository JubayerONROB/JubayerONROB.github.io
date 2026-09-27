---
title: Model Optimization
date: 2025-02-01
tags:
  - notes
  - llm
  - edge-ai
---

`edge-ai` `model-optimization`

Model optimization for edge/wearable deployment usually trades a small amount of accuracy for a large reduction in resident memory and compute. Two techniques come up repeatedly in my work:

- **Adapter sharing** — instead of two separate fine-tuned models for two related tasks, share one base decoder and one adapter across both tasks. This cuts resident weights roughly in half without retraining from scratch.
- **Quantization** — reducing weight precision (e.g. GGUF Q4_K_M) so a model that would otherwise need a GPU can run on a CPU-only device within a fixed memory budget.

Related:

→ [[work/research/proactive-conversation-assistant|Proactive Conversation Assistant]] — shared-adapter 1B decoder, 1.05 GB resident weights
→ [[work/projects/hybrid-router-vinci-monsoon|Hybrid Router]] — Q4_K_M quantized local classifier
→ [[knowledge/ai-ml/llm-routing|LLM Routing]]
→ [[knowledge/ai-ml/lora|LoRA]] — a different lever (training-time cost) on the same optimization problem
