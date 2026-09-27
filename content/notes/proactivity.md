---
title: Proactivity in Conversational AI
date: 2025-02-01
tags:
  - notes
  - nlp
  - llm
---

`nlp` `llm` `edge-ai`

Most conversational AI is reactive: it only produces a response once the user has finished speaking and explicitly asked for something. A *proactive* assistant instead has to solve a harder, prior problem — deciding **when** to speak at all, before deciding **what** to say. Getting the timing wrong in either direction breaks the interaction: interrupting too often is intrusive, interrupting too rarely means the assistance arrives too late to be useful.

This is the core problem behind my thesis, [[work/research/proactive-conversation-assistant|Proactive Conversation Assistant]] — treating interruption detection as a distinct, cheaper first stage that gates a more expensive generation stage, rather than running a single model that tries to do both at once.

Related:

→ [[work/research/proactive-conversation-assistant|Proactive Conversation Assistant]]
