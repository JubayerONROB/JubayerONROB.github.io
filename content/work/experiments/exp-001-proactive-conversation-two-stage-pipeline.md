---
title: "EXP-001: Two-Stage Pipeline for Proactive Interruption"
date: 2025-02-01
tags:
  - experiments
  - llm
  - nlp
status: ongoing
---

`EXP-001` · [[work/research/proactive-conversation-assistant|Proactive Conversation Assistant]]

**TITLE**
Two-stage interruption detection + hint generation vs. a single always-on generator

**DATE**
2025.02 – present

**OBJECTIVE**
Determine whether splitting "should the assistant speak now?" from "what should it say?" into two stages — a cheap always-on detector gating an expensive generator — reduces generator calls and latency without a hint-quality regression.

**METHOD**
Two-stage LLM pipeline evaluated on 28,058 decision points with an 8B generator; ablation removing persistent user-memory context; a compact 1B-parameter decoder sharing one adapter between both stages.

**INPUTS**
Conversation audio/text stream, persistent user-memory context

**OUTPUT**
Interruption decision + generated hint

**RESULT**

| Metric | Result |
|---|---|
| Generator call reduction | 7.62× |
| Wall-clock speedup | up to 4.39× |
| Exact-match drop when user-memory context removed | 24.7 points |
| Resident weights, shared-adapter 1B decoder | 1.05 GB |
| Compute reduction vs. two-model pipeline | 1.3–1.8× |

**STATUS**
ONGOING

Related:

→ [[work/research/proactive-conversation-assistant|Proactive Conversation Assistant]]
→ [[knowledge/ai-ml/model-optimization|Model Optimization]]
