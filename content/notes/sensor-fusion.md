---
title: Sensor Fusion
date: 2025-08-01
tags:
  - notes
  - robotics
  - control-systems
---

`sensor-fusion` `estimation`

Sensor fusion combines measurements from multiple noisy sensors into a single, more reliable estimate — exploiting the fact that different sensors tend to fail or drift in different ways. A barometer drifts slowly but is absolute; an optical-flow sensor is precise short-term but accumulates drift. Fusing them (typically with a [[notes/kalman-filter|Kalman filter]]) gives an estimate better than either sensor alone.

Related:

→ [[notes/kalman-filter|Kalman Filter]]
→ [[notes/optical-flow|Optical Flow]]
→ [[notes/slam|What is SLAM?]]
