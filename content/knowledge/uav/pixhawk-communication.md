---
title: Pixhawk Communication
date: 2024-12-01
tags:
  - notes
  - uav
  - robotics
---

`pixhawk` `mavlink` `dronekit`

The Pixhawk is a widely-used open-hardware flight controller running ArduPilot or PX4. A companion computer (e.g. a Raspberry Pi running vision code) talks to it over a serial link using the MAVLink protocol — a lightweight, message-based protocol for sending commands (waypoints, mode changes) and reading telemetry (GPS, attitude, battery). DroneKit wraps MAVLink in a Python API, which is the layer the [[work/projects/autonomous-rescue-drone|Autonomous Rescue Drone]] uses to hand detection results off to the flight controller.

Related:

→ [[work/projects/autonomous-rescue-drone|Autonomous Rescue Drone]]
→ [[knowledge/robotics/ros|ROS]]
