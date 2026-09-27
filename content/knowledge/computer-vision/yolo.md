---
title: YOLO
date: 2024-12-01
tags:
  - notes
  - computer-vision
  - robotics
---

`yolo` `object-detection`

YOLO (You Only Look Once) frames object detection as a single regression problem: one forward pass over the full image predicts bounding boxes and class probabilities directly, rather than the propose-then-classify pipeline older two-stage detectors used. That single-pass design is what makes it fast enough for real-time use on constrained hardware like a drone's onboard computer.

In the [[work/projects/autonomous-rescue-drone|Autonomous Rescue Drone]], YOLOv8 handles real-time human detection from the onboard RGB camera feed.

Related:

→ [[knowledge/computer-vision/optical-flow|Optical Flow]]
→ [[knowledge/robotics/slam|SLAM]]
→ [[work/projects/autonomous-rescue-drone|Autonomous Rescue Drone]]
