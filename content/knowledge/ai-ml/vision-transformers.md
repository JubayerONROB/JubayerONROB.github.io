---
title: Vision Transformers
date: 2025-10-01
tags:
  - notes
  - ai-ml
  - computer-vision
---

`vit` `computer-vision`

A Vision Transformer (ViT) splits an image into fixed-size patches, linearly embeds each patch, and feeds the resulting sequence through a standard transformer encoder — treating an image the same way an NLP transformer treats a sequence of tokens. This drops the convolutional inductive bias of CNNs in favor of global self-attention from the first layer.

CLIP's image encoder is a ViT variant, which is why ViT and CLIP show up together in practice.

Related:

→ [[knowledge/ai-ml/clip|CLIP]]
→ [[work/projects/deepfake-detection-clip-vit|Deepfake Detection using CLIP-ViT]]
