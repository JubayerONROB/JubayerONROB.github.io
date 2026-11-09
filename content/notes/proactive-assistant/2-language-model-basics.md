---
title: "2. Language model basics"
date: 2026-11-09
tags:
  - notes
  - llm
---

`llm` · Part of the [[notes/proactive-assistant/index|Proactive Assistant study guide]]

This page gives the minimum you need about language models to understand the paper. No earlier knowledge is assumed.

## 2.1 Tokens

A computer cannot read letters directly. A **tokenizer** cuts text into small pieces called **tokens**. A token can be a word, part of a word, or a symbol. Each token gets an integer ID.

> **Toy example.** "dance performance" might become two tokens. The real split depends on the tokenizer.

Our hints are **one to three tokens** long. This limit comes from the training data, not from the model design.

## 2.2 Embeddings and hidden states

Each token ID is turned into a list of numbers (a **vector**) called an **embedding**. Its length is $d$, the **hidden size**.

The model then changes these vectors again and again. After each stage, every token has a new vector. We call this vector the **hidden state** and write it $h$. Early hidden states are close to the raw word. Later ones carry meaning from the whole context.

## 2.3 Layers

A modern language model is a **stack of identical layers**. One layer takes the hidden states in and gives new hidden states out. We write the number of layers as $L$.

- **Llama-3.2-1B** has $L = 16$ layers. It has about 1 billion parameters ("1B").
- **Llama-3.1-8B** is a bigger model of the same family with about 8 billion parameters.

A **parameter** is one learned number. More parameters usually means more memory and more time.

The hidden state **after $k$ layers** is written $h_k$. This is the key object in our paper: the gate reads $h_k$ at a middle layer $k$.

![Prefill and decoding](/attachments/notes/proactive-assistant/fig3-transformer.png)
*Figure 3. (a) Prefill reads the whole prompt in one pass. (b) Decoding writes one token at a time. [PDF](/attachments/notes/proactive-assistant/fig3-transformer.pdf)*

## 2.4 What happens inside a layer (short version)

Each layer has two main parts.

**Attention.** Each token looks at the other tokens and decides which ones matter. For one head the formula is

$$\text{Attention}(Q,K,V) = \text{softmax}\!\left(\frac{QK^{\top}}{\sqrt{d_k}}\right)V$$

Read it like this. $Q$ (queries) say "what am I looking for?". $K$ (keys) say "what do I contain?". $V$ (values) say "what do I give if you pick me?". The product $QK^{\top}$ scores how well each token matches each other token. **Softmax** turns scores into weights that add up to 1. The result is a weighted mix of the values.

**MLP (feed-forward network).** A small network that changes each token's vector on its own. It stores much of the model's "knowledge".

Both parts have learned weight matrices. In the code, these are called `q_proj`, `k_proj`, `v_proj`, `o_proj` (attention) and `gate_proj`, `up_proj`, `down_proj` (MLP). We will meet them again in [[notes/proactive-assistant/4-training|page 4]].

## 2.5 Two phases of running a model

**Prefill.** The model reads the whole prompt in **one forward pass** through all $L$ layers. All tokens are processed together. This is where most of our cost is, because our prompt is several hundred tokens.

**Decoding.** The model then writes the answer **one token at a time**. Each new token needs another pass, but old tokens' keys and values are saved (the **KV cache**), so only the new token is computed.

For us, decoding is cheap (1 to 3 tokens). The expensive part is **prefill**. This is why the paper counts cost in **full passes over the prompt before any hint token is decoded**.

## 2.6 From a hidden state to a word: logits and softmax

To pick the next token, the model uses a **language-model head**. It multiplies the last hidden state by a matrix and gives one number for every word in the vocabulary. These numbers are **logits**. Softmax turns logits $z_1, \ldots, z_V$ into probabilities:

$$P(\text{token } c) = \frac{e^{z_c}}{\sum_{j} e^{z_j}}$$

All probabilities are positive and add up to 1. The model picks the likely token.

## 2.7 A classifier head

A **classifier head** is a small matrix that turns a hidden state into logits for a few classes instead of a whole vocabulary. In our paper:

$$W_c \in \mathbb{R}^{2 \times d}$$

It maps a hidden state of size $d$ to **two numbers**: one for "no hint needed" and one for "hint needed". Softmax on these two gives $p_i$, the gate score.

The special part of our work is **where** the head is attached. A normal classifier reads the last layer. Ours reads layer $k$, in the middle. See [[notes/proactive-assistant/5-early-exit-and-unified-decoder|page 5]].

## 2.8 Check yourself

- What is the difference between prefill and decoding?
- What does $h_k$ mean?
- Why is the cost in our paper measured in "full passes" and not in seconds only?

Next: [[notes/proactive-assistant/3-memory-and-prompt|3. Memory profile and prompt]]
