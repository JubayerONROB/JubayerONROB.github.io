---
title: LLM Routing
date: 2026-07-01
tags:
  - notes
  - llm
  - llm-routing
---

`llm-routing` `nlp`

LLM routing sends a query to the cheapest model capable of handling it, rather than always calling the largest available model. A common pattern is a two-stage pipeline: a small, fast classifier makes a first pass over the query, and only queries it judges "hard" get escalated to a larger, more expensive model.

The efficiency gain comes from the fact that most real-world queries are easy — routing wastes little accuracy but saves most of the API cost or compute.

Related:

→ [[projects/hybrid-router-vinci-monsoon|Hybrid Router: Two-Stage Local-First LLM Agent]]
→ [[research/proactive-conversation-assistant|Proactive Conversation Assistant]]
→ [[notes/model-optimization|Model Optimization]]
