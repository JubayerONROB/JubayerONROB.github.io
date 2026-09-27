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

## Description

A complete, 135-page preparation handbook for VLSI physical design — covering theory, tool flows, and a worked problem bank. Built for interview prep, coursework, sign-off/ECO problem-solving, and hackathon reference, with derivations from first principles rather than bare assertions.

## Technical stack

- Cadence Innovus and OpenLane/OpenROAD flows, with annotated Tcl scripts
- Licensed CC BY 4.0

## Structure

```
Part I   — Foundations (CMOS, standard cells, .lib/.lef/.def/.sdc/.spef, STA)
Part II  — The Flow (floorplan → power plan → placement → CTS → routing → sign-off)
Part III — The Optimization Sweep (area, timing, power, congestion, signal integrity)
Part IV  — Algorithms Inside the Tools (partitioning, placement, buffer insertion)
Part V   — Practice (32 worked problems, 63 rapid-fire questions, checklists, study plan)
```

## Key contributions

- 32 fully worked problems across three difficulty tiers, with solutions.
- Real timing/power/congestion report examples rather than synthetic ones.
- Covers both a commercial flow (Cadence Innovus) and the open-source flow (OpenLane/OpenROAD) side by side.

## Related

[[projects/vlsi-16bit-square-rooter|16-bit Binary Square Rooter]] — an applied RTL-to-GDS project using the same flow this handbook documents.
