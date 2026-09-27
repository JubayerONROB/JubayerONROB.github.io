---
title: Kalman Filtering
date: 2025-08-01
tags:
  - notes
  - control-systems
  - robotics
---

`kalman-filter` `estimation`

A Kalman filter estimates the hidden state of a system (e.g. true altitude) from a sequence of noisy measurements, by alternating between a *predict* step (propagate the previous estimate forward using a motion model) and an *update* step (correct that prediction using a new noisy measurement, weighted by each source's known uncertainty). It's the standard tool for fusing measurements like barometer and optical-flow readings into one estimate that's better than either alone.

Related:

→ [[notes/sensor-fusion|Sensor Fusion]]
→ [[notes/optical-flow|Optical Flow]]
→ [[notes/slam|What is SLAM?]]
