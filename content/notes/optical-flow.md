---
title: Optical Flow
date: 2025-08-01
tags:
  - notes
  - computer-vision
  - robotics
---

`optical-flow` `sensor-fusion`

Optical flow estimates the apparent motion of brightness patterns between consecutive video frames — effectively a per-pixel velocity field. On a robot, a downward-facing optical-flow sensor gives a cheap estimate of horizontal displacement without GPS, and can be fused with other sensors (barometer, IMU) for altitude or position estimation.

Related:

→ [[notes/sensor-fusion|Sensor Fusion]]
→ [[notes/kalman-filter|Kalman Filter]]
