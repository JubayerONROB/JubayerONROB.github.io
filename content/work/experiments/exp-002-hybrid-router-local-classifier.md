---
title: "EXP-002: Local Classifier for LLM Query Routing"
date: 2026-07-01
tags:
  - experiments
  - llm
  - llm-routing
status: complete
---

`EXP-002` · [[work/projects/hybrid-router-vinci-monsoon|Hybrid Router]]

**TITLE**
Grammar-constrained local classifier for zero-cost query resolution

**DATE**
2026.07

**OBJECTIVE**
Test whether a small, grammar-constrained local classifier can resolve most incoming queries without calling a remote LLM, cutting API cost with no correctness regression on the harder queries still escalated.

**METHOD**
Qwen2.5-3B (GGUF, Q4_K_M) local classifier routing across 8 intent categories, escalating high-difficulty queries to a Fireworks remote backend; offline pytest harness enforcing zero hardcoded values; deployed on a CPU-only grading VM (4 GB RAM, no GPU, linux/amd64) with a 25s per-request timeout.

**INPUTS**
Incoming query text

**OUTPUT**
Local resolution or escalation decision + response

**RESULT**
The classifier reliably separated shallow from high-difficulty queries under the offline harness, escalating only the latter to the Fireworks backend and holding to the CPU/memory/timeout budget of the grading VM throughout.

**STATUS**
COMPLETE (AMD Hackathon ACT II, Track 1)

Related:

→ [[work/projects/hybrid-router-vinci-monsoon|Hybrid Router]]
→ [[knowledge/ai-ml/llm-routing|LLM Routing]]
