# skidsteer-ros-2
Skidsteer | ROS 2 Humble | Ubuntu 22.04

## How to run?
```bash
micro-ros -> kinematic -> joy_node -> ps3
```
---
## 1. Project Overview

This repository contains software components for developing and operating
a skid-steer mobile robot using ROS 2.

The intended workflow connects joystick teleoperation, robot control,
kinematics, and communication with the robot's embedded controller.

The current workflow is organized around:

- micro-ROS communication
- Robot kinematics
- PS3 controller teleoperation
- Navigation2 with controllers: RPP, MPPI

The exact nodes, topics, launch files, and hardware interfaces depend on
the implementation in this repository.

## 2. Who Should Use This Repository?

This repository is intended for:

- Lab members developing and testing the skid-steer robot.
- Members integrating embedded hardware with ROS 2 through micro-ROS.
- Students learning mobile robot teleoperation and software integration.
- Contributors maintaining and extending the robot's software packages.

Basic familiarity with Linux, Git, and ROS 2 is recommended.

## 3. Supported Operating System and Platform

### Software environment

| Component | Target environment |
|---|---|
| Operating system | Ubuntu 22.04 LTS |
| Robot middleware | ROS 2 Humble |
| Package management | apt and rosdep |
| Embedded communication | micro-ROS |
| Teleoperation input | ROS 2 joystick interface / PS3 controller |

### Hardware platform

The software is designed for a skid-steer mobile robot.
