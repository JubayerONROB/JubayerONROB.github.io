---
title: PID Control
date: 2025-08-01
tags:
  - notes
  - control-systems
  - robotics
---

`pid` `control-systems`

A PID controller drives a system's error (setpoint minus measured value) toward zero using three terms: **P**roportional (react to current error), **I**ntegral (eliminate steady-state error by accumulating past error), and **D**erivative (dampen oscillation by reacting to the rate of change of error). It's the workhorse controller in flight controllers, motor drivers, and most closed-loop embedded systems — the standard approach for the kind of encoder-feedback motor control used in the [[work/projects/ultrasonic-obstacle-mapping-bot|Ultrasonic Obstacle Mapping Bot]].

Related:

→ [[work/projects/ultrasonic-obstacle-mapping-bot|Ultrasonic Obstacle Mapping Bot]]
→ [[notes/kalman-filter|Kalman Filtering]]
