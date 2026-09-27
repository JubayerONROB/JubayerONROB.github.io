---
title: What is SLAM?
date: 2025-08-01
tags:
  - notes
  - robotics
---

`slam` `localization` `mapping`

SLAM (Simultaneous Localization and Mapping) is the problem of building a map of an unknown environment while simultaneously tracking a robot's position within that map — neither can be solved cleanly without the other, since a map needs a known pose to build and a pose estimate needs a map to localize against. Most practical solutions solve them jointly using probabilistic estimation (e.g. Kalman-filter-based EKF-SLAM, or newer graph-based/visual SLAM methods).

The [[work/projects/ultrasonic-obstacle-mapping-bot|Ultrasonic Obstacle Mapping Bot]] is a simplified, single-sensor relative of this: it maps its surroundings from a fixed known position rather than solving full SLAM, since it doesn't need to localize itself while mapping.

Related:

→ [[knowledge/robotics/sensor-fusion|Sensor Fusion]]
→ [[knowledge/control-systems/kalman-filter|Kalman Filter]]
→ [[work/projects/ultrasonic-obstacle-mapping-bot|Ultrasonic Obstacle Mapping Bot]]
