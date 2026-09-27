---
title: CLIP
date: 2025-10-01
tags:
  - notes
  - ai-ml
  - computer-vision
---

`clip` `openclip` `computer-vision`

CLIP (Contrastive Language-Image Pretraining) trains an image encoder and a text encoder jointly, so that matching image-text pairs land close together in a shared embedding space. The image encoder is typically a ViT. Once trained, CLIP's embeddings transfer well to downstream tasks — including ones it was never explicitly trained for, like deepfake detection, by fine-tuning a small classification head on top of frozen or lightly-tuned CLIP features.

Related:

→ [[notes/vision-transformers|Vision Transformers]]
→ [[work/projects/deepfake-detection-clip-vit|Deepfake Detection using CLIP-ViT]]
