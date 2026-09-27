---
title: ICML 2026 Agent Reproducibility Challenge
date: 2026-02-01
tags:
  - projects
  - research
  - machine-learning
  - reproducibility
  - ai-safety
status: complete
---

`machine-learning` `reproducibility` `ai-safety` `llm-evaluation` · **Status: Complete**

[GitHub →](https://github.com/JubayerONROB/icml2026-agent-repro)

## Description

Eight end-to-end reproductions of ICML 2026 papers, run as an autonomous agent pipeline (Claude Code / Opus 5) that read each paper, designed tests, wrote code, ran audits, generated figures and posters, and published logbooks to Hugging Face.

## Methodology

The pipeline enforces "controls that must FAIL" — deliberately broken variants included alongside each test to validate that the tests themselves are actually discriminating, not just passing by default. All results flow through a single `results/*.json` file so figures and prose stay synchronized with the underlying measurements.

## Featured reproductions

**Paper #8565 — "A Coin Flip for Safety: LLM Judges Fail to Reliably Measure Adversarial Robustness"**
5 verified claims, 1 partial. The paper's central claim survives with the released data; Figure 3 reproduced exactly, matching to the integer.

**Paper #15191 — "Who Said Neural Networks Aren't Linear?"**
5 verified claims — plus a bug found in the authors' released code: a nesting error in the Runge-Kutta branch silently demoted it to first-order accuracy. Fixing it restored agreement between one-step and multi-step methods to 80 dB PSNR.

The remaining six reproductions span pure theory papers (audited mathematically), GPU-heavy papers, survey papers (data recovered from PDF figures), and semidefinite-programming tightness verification.

## Related

[[research/proactive-conversation-assistant|Proactive Conversation Assistant]] — shares an evaluation-rigor mindset: verify claims against real measurements rather than assuming them.
