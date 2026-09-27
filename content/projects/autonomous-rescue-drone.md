---
title: Autonomous Rescue Drone for Locating Survivors
date: 2024-09-01
tags:
  - projects
  - computer-vision
  - ai
  - uav
  - robotics
status: complete
---

`computer-vision` `ai` `uav` · Sep – Dec 2024 · **Status: Complete**

[GitHub →](https://github.com/JubayerONROB/autonomous-rescue-drone)

## Description

An AI-powered drone for search and rescue, built to locate survivors in disaster areas where manual search is slow or dangerous.

## Technical stack

- Python, YOLOv8, OpenCV
- DroneKit, ArduPilot
- GPS-based flight control

## Architecture

```mermaid
flowchart TD
    A[RGB Camera] --> B[YOLOv8 Human Detection]
    B --> C[GPS-tagged Detection Coordinates]
    C --> D[ArduPilot Flight Controller / DroneKit]
    D --> E[Autonomous Area-Coverage Flight Plan]
```

## Key contributions

- Real-time human detection using RGB cameras and OpenCV.
- GPS-based autonomous flight control for structured area coverage, so the drone systematically sweeps a search zone rather than flying ad hoc.

## Related

[[projects/ultrasonic-obstacle-mapping-bot|Ultrasonic Obstacle Mapping Bot]] — another autonomous-navigation project, ground-based instead of aerial.
