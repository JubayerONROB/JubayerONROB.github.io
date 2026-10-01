---
title: Physical Design Optimization Handbook
date: 2025-01-01
tags:
  - projects
  - vlsi
  - eda
  - physical-design
status: ongoing
---

`asic` `eda` `vlsi` `physical-design` `openroad` `openlane` · **Status: Ongoing**

[GitHub →](https://github.com/JubayerONROB/physical-design-optimization-handbook)

## Overview

A complete, 135-page preparation handbook for VLSI physical design — covering theory, tool flows, and a worked problem bank. Built for interview prep, coursework, sign-off/ECO problem-solving, and hackathon reference, with derivations from first principles rather than bare assertions.

## Problem

Most physical-design reference material is either scattered across vendor documentation and academic papers, or reduced to interview flashcards with no derivation behind them. There wasn't a single reference that covered the theory, the tool flow, and a worked problem bank together.

## Approach

Write the handbook in five parts moving from foundations to practice, covering both a commercial flow (Cadence Innovus) and the open-source flow (OpenLane/OpenROAD) side by side, with real timing/power/congestion report examples rather than synthetic ones.

## System architecture

```mermaid
flowchart TD
    A[Part I: Foundations<br/>CMOS, standard cells, .lib/.lef/.def/.sdc/.spef, STA] --> B[Part II: The Flow<br/>floorplan to power plan to placement to CTS to routing to sign-off]
    B --> C[Part III: Optimization Sweep<br/>area, timing, power, congestion, signal integrity]
    C --> D[Part IV: Algorithms Inside the Tools<br/>partitioning, placement, buffer insertion]
    D --> E[Part V: Practice<br/>32 worked problems, 63 rapid-fire questions, study plan]
```

## Tech stack

- Cadence Innovus and OpenLane/OpenROAD flows, with annotated Tcl scripts
- Licensed CC BY 4.0

## Results

- 32 fully worked problems across three difficulty tiers, with solutions.
- Real timing/power/congestion report examples rather than synthetic ones.
- Covers both a commercial flow (Cadence Innovus) and the open-source flow (OpenLane/OpenROAD) side by side.

## Media

![Physical Design Optimization Handbook cover](/attachments/projects/vlsi-pd-handbook/cover.jpg)
*Edition 1, open-source release: theory, algorithms, tool flows and worked problems from floorplan to sign-off. [Download the handbook (PDF) →](/attachments/projects/vlsi-pd-handbook/Physical-Design-Optimization-Handbook.pdf)*

## Challenges

Not documented yet.

## What I learned

Not documented yet.

## Future work

Not documented yet.

## Related

[[work/projects/vlsi-16bit-square-rooter|16-bit Binary Square Rooter]] — an applied RTL-to-GDS project using the same flow this handbook documents.
