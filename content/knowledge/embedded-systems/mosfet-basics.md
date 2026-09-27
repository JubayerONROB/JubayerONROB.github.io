---
title: MOSFET Basics
date: 2025-08-01
tags:
  - notes
  - embedded-systems
---

`mosfet` `electronics`

A MOSFET is a voltage-controlled switch: applying a voltage at the gate creates a conductive channel between drain and source, with (ideally) no gate current required to hold it open. That makes MOSFETs the standard choice for switching higher-current loads like motors from a microcontroller's low-current GPIO pin — usually via a driver IC (like the L298N) rather than driving the gate directly, since motor stall/inrush current would otherwise blow past what a microcontroller pin can source.

Related:

→ [[knowledge/embedded-systems/bjt-basics|BJT Basics]]
→ [[work/projects/ultrasonic-obstacle-mapping-bot|Ultrasonic Obstacle Mapping Bot]]
