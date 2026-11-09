---
title: "1. The task and the gate"
date: 2026-11-09
tags:
  - notes
  - nlp
---

`nlp` · Part of the [[notes/proactive-assistant/index|Proactive Assistant study guide]]

## 1.1 What is a proactive assistant?

Most assistants are **reactive**. You ask, they answer.

A **proactive** assistant listens to a conversation you are already having. It is never called. Sometimes it shows a very short **hint**. For example, you are stuck on a name or a date, and the hint gives it to you.

So it must solve two problems:

1. **When** to help. Most moments do not need a hint. Interrupting at the wrong time is annoying.
2. **What** to say. The hint must be short and correct.

In our data, only **11.96%** of the pauses need a hint. The assistant must stay quiet the other 88%.

![One decision at every silence](/attachments/notes/proactive-assistant/fig1-decision-points.png)
*Figure 1. At each silence the assistant asks "should I speak?". Only the third silence says yes. [PDF](/attachments/notes/proactive-assistant/fig1-decision-points.pdf)*

## 1.2 Decision points (markers)

A conversation is a list of utterances (things people say). After each utterance there can be a short **silence**. We call each silence a **marker** or **decision point**.

Write the conversation seen so far as

$$D = \langle u_1, u_2, \ldots, u_T \rangle$$

and the part up to silence $i$ as $D_{\le i}$. This is the **left context**: only what was said before, never the future.

Our test set has $N = 28{,}058$ markers from 866 dialogues. Of these, **3,356 are triggers** (a hint is needed) and **24,702 are silence markers** (no hint needed). That is 11.96% triggers.

## 1.3 The two decisions

At marker $i$ the system makes two decisions.

**Decision 1: the gate.** A model reads $D_{\le i}$ and gives a score $p_i$ between 0 and 1. Think of it as "how sure am I that a hint is needed?". Then we compare it to a **threshold** $t$:

$$
g_i(t) = \mathbf{1}\left[\,p_i \ge t\,\right] \tag{1}
$$

The symbol $\mathbf{1}[\cdot]$ is the **indicator**. It is 1 if the statement inside is true and 0 if false. So $g_i = 1$ means "speak" and $g_i = 0$ means "stay quiet".

**Decision 2: the hint.** Only if $g_i = 1$, the system writes a hint $h_i$ of **one to three words** using $D_{\le i}$ and the user's memory $M_w$ (see [[notes/proactive-assistant/3-memory-and-prompt|page 3]]).

## 1.4 Why the threshold matters

![Threshold and four outcomes](/attachments/notes/proactive-assistant/fig2-threshold.png)
*Figure 2. (a) The threshold $t$ splits scores into "silent" and "fire". (b) Every marker lands in one of four boxes. [PDF](/attachments/notes/proactive-assistant/fig2-threshold.pdf)*

A gate can make two kinds of mistakes, and they cost different things:

- **False alarm (FP).** The assistant speaks when it should not. It interrupts a conversation that did not need help. Other people in the room also pay for this.
- **Miss (FN).** The assistant stays quiet when a hint was needed. The user is left as they would be without the assistant.

Raising $t$ gives fewer false alarms but more misses. Lowering $t$ does the opposite. There is no free lunch. So the paper does not use one fixed $t$. It reports gate quality **against a false-alarm budget**. Choosing that budget is a **deployment decision**, not a science decision.

## 1.5 Why "when" and "what" depend on each other

A hint is useful only at a moment that needs one. And a moment deserves an interruption only if a useful hint exists. This is why the paper **scores both decisions together** and does not treat them as separate problems. That idea is the topic of [[notes/proactive-assistant/6-evaluation-metrics|page 6]].

## 1.6 Check yourself

- What does $g_i = 0$ mean?
- If you raise $t$ from 0.5 to 0.8, do false alarms go up or down? Do misses go up or down?
- Why is a false alarm worse than it first looks?

*Answers: stay quiet; false alarms go down, misses go up; because it interrupts everyone in the conversation, not only the user.*

Next: [[notes/proactive-assistant/2-language-model-basics|2. Language model basics]]
