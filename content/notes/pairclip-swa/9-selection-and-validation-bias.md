---
title: "9. Selection and validation bias"
date: 2026-11-10
tags:
  - notes
  - statistics
  - deepfake
---

`statistics` `deepfake` · Part of the [[notes/pairclip-swa/index|PairCLIP-SWA study guide]]

This page explains the paper's most transferable lesson: **how you choose the checkpoint matters as much as the model.**

## 9.1 What "selecting a checkpoint" means

Training produces a new set of weights every epoch. You must choose **one** to deploy. The standard protocol is:

1. After every epoch, measure accuracy on a **validation split**.
2. Keep the epoch with the **highest validation accuracy** (this is also what early stopping uses).
3. Report and deploy that one.

It sounds harmless. But validation data is a **finite sample**, and the choice is made *using that same sample*.

## 9.2 Why the best score is optimistic (the winner's curse)

Every validation score is **true quality plus luck**. The luck comes from which images happened to be in the validation set, and from random wobble in the weights. If you compare many candidates and keep the highest score, you tend to keep the one with the **best luck**, not only the best quality. Its reported score then **overstates** its true quality. The more variable the candidates, the bigger the overstatement.

![Selection bias](/attachments/notes/pairclip-swa/pc18-selection-bias.png)
*Figure 19. A schematic with no data: the highest validation score includes luck that disappears on new data. [PDF](/attachments/notes/pairclip-swa/pc18-selection-bias.pdf)*

The paper cites three earlier observations that fit this:

- selection on a finite validation set is itself a source of **optimistic bias**, growing with the number of candidates compared;
- accuracy can drop on a **freshly drawn sample** of nominally the same distribution;
- in domain generalization, the **selection protocol** can matter as much as the method.

## 9.3 What our data show

In our run, the non-averaged weights are very noisy: their validation accuracy has a standard deviation of **2.13 points** across the last eight epochs ([[notes/pairclip-swa/6-weight-averaging|page 6]]). So the "best epoch" is a maximum over noise.

Now read Table V again ([[notes/pairclip-swa/8-results|page 8]]):

| Where | Averaging vs the selected iterate |
|---|---|
| DF-Wild-Cup validation (selection split) | average **wins** by 1.37 |
| OpenForensics validation (selection split) | average **loses** by 0.76 |
| OpenForensics test (nothing selected on it) | average **wins** by 5.91 |

**One mechanism explains all three rows.**

- The non-averaged iterate is a **high-variance** object.
- When its noise happens to **line up with the selection split** (OpenForensics validation), the selected iterate beats the average by a small margin.
- When it does not (throughout the DF-Wild-Cup trajectory), the average wins at every epoch.
- On data used for neither training nor selection, the iterate's advantage is not just lost but **reversed**.

This is the pattern selection bias predicts. Averaging the weights **reduces the variance** at zero inference cost. The flat-minimum account of SWA explains why the averaged solution degrades less under shift.

## 9.4 Why scalar accuracy missed it

On OpenForensics, the loss was **confined to one class**. The model rejected too many real photographs (specificity fell from 97.83% to 78.88%) while still catching almost every fake (recall 98.67%). On a **balanced** split, accuracy is the mean of the two recalls. A collapse of one recall by 19 points moves accuracy by about 9.6 points, and that was invisible to the selection split because the validation split showed **no** collapse at all. The collapse only appeared on the new sample.

> **Toy example.** Two systems have the same 90% accuracy on a balanced set. System A has recall 90% on both classes. System B has fake recall 100% and real recall 80%. Accuracy cannot tell them apart. Per-class recall can. If real photographs matter (for example, falsely accusing people of forgery), B is much worse.

## 9.5 The paper's recommendations

Forensic detectors should be:

1. **selected on balanced accuracy or MCC**, not raw accuracy;
2. selected on a **partition disjoint from the one used for early stopping**;
3. **reported with per-class recall** next to accuracy;
4. built with **weight averaging** preferred to a single selected iterate.

## 9.6 A warning that applies to the paper itself

Every DF-Wild-Cup number in the comparison table, **including CAE-Net's and ours**, is measured on the split its system was selected or tuned on. Treat them as **upper bounds on deployment accuracy**. The held-out OpenForensics test is the only truly untouched number, and it shows how large the optimism can be (9.58 points for the selected checkpoint).

## 9.7 Words used on this page

- **Selection bias / optimistic bias.** A reported score that is too high because it was chosen as the best of many.
- **Winner's curse.** The best of many noisy estimates tends to be one with a lucky error.
- **Variance.** How much a quantity wobbles from run to run.
- **Disjoint.** Sharing no items.
- **Balanced accuracy.** The average of the recall on each class.
- **Domain generalization.** Doing well on data from distributions not seen in training.
- **Held-out.** Kept aside and not used in any decision.

## 9.8 Check yourself

- Why is the highest validation score an optimistic estimate?
- Why did a balanced-split accuracy not show the collapse on validation?
- Which of the four recommendations would have prevented the wrong choice on OpenForensics?

Next: [[notes/pairclip-swa/10-ablations-and-design-space|10. Ablations and design space]]
