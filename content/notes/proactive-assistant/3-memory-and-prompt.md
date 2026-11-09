---
title: "3. Memory profile and prompt"
date: 2026-11-09
tags:
  - notes
  - llm
---

`llm` · Part of the [[notes/proactive-assistant/index|Proactive Assistant study guide]]

## 3.1 What is the memory profile?

The assistant helps the user with things only the user knows. For that it needs a **memory profile**, written $M_w$ for wearer $w$. It is the system's knowledge base about one person. It was collected **before** the conversation began.

From the paper's example (not a real corpus item): *the user is a graduate student in Boston who attended a dance performance last spring, is learning Portuguese, and plans a trip to Lisbon.*

The profile has two parts, both written as normal prose (not fixed slots):

- a **profile field**: general facts about the person;
- an **events map**: separate episodes, like `event0`, `event1`.

The profile comes with LlamaPIE's released dataset, one file per sample. We use it exactly as given. How it was built is outside our pipeline.

## 3.2 Facts

For some tests (see [[notes/proactive-assistant/7-experiments-and-findings|page 7]]) the profile is cut into **facts**. One fact is one sentence of the profile field or of one event. Very short pieces are joined to the one before. A profile has **11.99 facts on average** across the 3,356 test triggers.

## 3.3 Where the hint comes from

How much of the answer is in the profile?

- The target hint is among the retrievable facts for **51.19%** of triggers.
- It is a **verbatim string** in the profile for **50.95%**.

So for about **half** of the triggers, the model cannot just copy from the profile. It must make the hint from the dialogue. This is why the model must understand and not only look up.

## 3.4 The prompt

The model sees one long text, the **prompt**, with these parts in order:

1. a **system prompt** (instructions);
2. the **memory profile** (flattened: profile field first, then events in key order);
3. the **dialogue** so far.

The dialogue is cut to the last **1,300 characters**. About 60.4% of training rows reach this limit, so the character cap, not the model's token limit, is what binds.

![Prompt anatomy](/attachments/notes/proactive-assistant/fig4-prompt.png)
*Figure 6. The unified model and the generator read the profile. The gate of the cascade does not. [PDF](/attachments/notes/proactive-assistant/fig4-prompt.pdf)*

The profile adds **306 tokens** to every prompt. On the test split a prompt has 676 tokens with the profile and 370 without. This matters because prefill cost grows with prompt length, and the profile is not small.

## 3.5 Does the gate need the profile?

In the two-model cascade, the gate reads the dialogue **without** the profile. In our unified model, the gate reads a prompt that **includes** the profile.

That gives the unified model extra information. Is that the reason it does well? We tested it. We retrained the cascade's 1B gate with the profile added to its input:

- F1 moves from 0.7926 to 0.7981. That is **+0.0055** with a 95% interval of $[-0.0010, +0.0125]$. The interval includes zero.
- The unified gate at $k = 10$ is still ahead by **+0.0183** F1.

So the profile explains only about **23%** of the gap (with a wide range, $[-5, +49]\%$). At $k = 10$ the rest is credited to the architecture.

## 3.6 Why not retrieve only the best facts?

A common idea is **retrieval**: pick only the most relevant facts and drop the rest. This saves tokens. We tested it. It did **not** help, because the whole profile already fits in the context. Retrieval only removed information. See [[notes/proactive-assistant/7-experiments-and-findings|page 7]].

## 3.7 Check yourself

- What two parts does a memory profile have?
- Why does the prompt cost matter more than the hint length?
- Does the cascade gate see the profile?

Next: [[notes/proactive-assistant/4-training|4. Training: LoRA, 4-bit, losses]]
