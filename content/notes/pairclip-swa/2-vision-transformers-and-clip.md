---
title: "2. Vision transformers and CLIP"
date: 2026-11-10
tags:
  - notes
  - computer-vision
  - deep-learning
---

`computer-vision` · Part of the [[notes/pairclip-swa/index|PairCLIP-SWA study guide]]

This page explains the model: how a picture becomes numbers, how a **vision transformer** reads them, and what **CLIP** is. It uses the same ideas as the language-model page of the [[notes/proactive-assistant/2-language-model-basics|earlier guide]], with pictures instead of words.

## 2.1 Images as numbers

A colour image is a grid of pixels. Each pixel has three numbers: red, green and blue, from 0 to 255. A 224 × 224 image is therefore $224 \times 224 \times 3$ numbers.

## 2.2 From image to tokens: patches

A **vision transformer (ViT)** cuts the image into small squares called **patches**. Each patch is treated like a word.

For our model, **ViT-L/14**:

- patch size is **14 × 14 pixels** ("/14");
- a 224 × 224 image gives $16 \times 16 = 256$ patches ($N_p = 256$);
- each patch is flattened to $3 \times 14 \times 14 = 588$ numbers and mapped by a **linear layer** to a vector of width $d_m = 1024$;
- a special **class token** (CLS) is added at the front, so there are $N = 257$ tokens;
- a **positional embedding** is added so the model knows where each patch came from.

So the input to the first layer is

$$
Z_0 = [\,z_{cls};\ E x_1;\ \ldots;\ E x_{N_p}\,] + E_{pos}
$$

where $E$ is the patch-embedding matrix and $x_j$ is patch $j$.

![ViT-L/14 from image to score](/attachments/notes/pairclip-swa/pc2-vit.png)
*Figure 4. From an image to a score. The grid is drawn 4 × 4 for clarity; the real grid is 16 × 16. [PDF](/attachments/notes/pairclip-swa/pc2-vit.pdf)*

## 2.3 The transformer block

The model has $L = 24$ identical **blocks**. Each block has two parts, joined by **residual connections** (the input is added back to the output, so information can flow through easily):

$$
Z'_\ell = Z_{\ell-1} + \text{MHSA}\!\left(\text{LN}(Z_{\ell-1})\right) \tag{6}
$$

$$
Z_\ell = Z'_\ell + \text{MLP}\!\left(\text{LN}(Z'_\ell)\right) \tag{7}
$$

- **LN (layer normalization).** Rescales each token's vector to have mean 0 and variance 1 (then a learned scale and shift). It works **per sample**, so the batch does not change the result. This matters for class-exact batching in [[notes/pairclip-swa/4-preprocessing|page 4]].
- **MHSA (multi-head self-attention).** Every token looks at every other token and mixes in the ones that matter. Here there are **16 heads**, each of width 64 ($16 \times 64 = 1024$). Attention is $\text{softmax}(QK^\top/\sqrt{d_k})\,V$, explained in the [[notes/proactive-assistant/2-language-model-basics|earlier guide]].
- **MLP.** A small network applied to each token. Its hidden layer is 4 times wider (**expansion 4**) with a **GELU** activation (a smooth version of "keep positive values, squash negative ones"). "Pre-norm" means LN comes *before* each part.

## 2.4 From the class token to a decision

After 24 blocks, the class token has gathered information from the whole image. We take it, apply a layer norm, and project it:

$$
g(x) = \text{LN}\!\left(Z_L^{(0)}\right) W_{proj} \in \mathbb{R}^{768} \tag{8}
$$

Then a **linear head** maps this 768-number vector to two scores and **softmax** turns them into probabilities:

$$
f_\theta(x) = \text{softmax}\!\left(W_c\, g(x) + b_c\right) \tag{9}
$$

We keep $W_{proj}$ because the projected space is where CLIP's contrastive geometry was learned, and where frozen-feature transfer has been shown to work.

## 2.5 What is CLIP?

**CLIP** (Contrastive Language-Image Pre-training) was trained on web-scale collections of image-caption pairs. It has two networks:

- an **image tower** that turns an image into a vector $u$;
- a **text tower** that turns a caption into a vector $v$.

Training makes the vector of an image **close to its own caption** and **far from other captions**. "Closeness" is a dot product (or cosine similarity). That pulls the matching pairs on the diagonal of the similarity matrix together and pushes the others apart.

![CLIP idea](/attachments/notes/pairclip-swa/pc3-clip.png)
*Figure 5. CLIP learns by matching images with captions. We keep only the image tower. The layout is schematic. [PDF](/attachments/notes/pairclip-swa/pc3-clip.pdf)*

**OpenCLIP** is an open re-implementation and training of this idea. We use the **visual tower of OpenCLIP ViT-L/14 with the original OpenAI weights**, followed by a linear head. **The text tower is discarded.**

**Why CLIP for forensics?** Earlier work found that frozen CLIP features, even with a simple classifier, transfer to new generators much better than fine-tuned CNNs. But a frozen tower under-fits fine-grained forensic evidence. Fully fine-tuning it can distort the pre-trained geometry. Our **progressive unfreezing** ([[notes/pairclip-swa/5-training-and-unfreezing|page 5]]) sits between the two extremes.

## 2.6 Parameter budget

| Component | Parameters | Share |
|---|---|---|
| Patch embedding (3×14×14 → 1024) | 602,112 | 0.20% |
| Class token and positional embedding | 264,192 | 0.09% |
| Pre-/post-layer normalization | 4,096 | < 0.01% |
| Transformer blocks (24 × 12.60 M) | 302,309,376 | 99.45% |
| Output projection (1024 → 768) | 786,432 | 0.26% |
| Linear head (768 → 2) | 1,538 | < 0.01% |
| **Total** | **303,967,746** | 100% |

Almost all parameters are in the 24 blocks. This is why *which blocks are trainable* is the key design choice.

## 2.7 A detail to know: QuickGELU

Loading ViT-L-14 in `open_clip` with the `openai` tag pairs weights trained with **QuickGELU** (a cheaper approximation of GELU) with a configuration that uses standard GELU. Fine-tuning absorbs the mismatch. But anyone reproducing **frozen-feature** results should be aware of it.

## 2.8 Words used on this page

- **Patch.** A small square piece of the image treated as one token.
- **Token.** One element of the sequence the transformer reads.
- **Embedding.** A vector that represents a token.
- **Class token (CLS).** An extra token that collects a summary of the whole image.
- **Residual connection.** Adding a layer's input to its output.
- **Layer normalization.** Rescaling each vector to a standard range.
- **Head (attention head / classifier head).** A parallel attention computation, or a final small matrix.
- **Contrastive learning.** Learning by pulling matching pairs together and pushing others apart.
- **Tower.** One of the two networks inside CLIP.
- **Frozen.** Not updated by training.

## 2.9 Check yourself

- How many patches does a 224 × 224 image give with 14 × 14 patches?
- Which part of CLIP do we throw away?
- Where are 99.45% of the parameters?

Next: [[notes/pairclip-swa/3-balancing-the-data|3. Balancing the data (Stage 1)]]
