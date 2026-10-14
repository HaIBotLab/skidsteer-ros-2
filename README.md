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

....

## 4. Prerequisites

Before building the workspace, prepare:

- Ubuntu 22.04 LTS
- ROS 2 Humble
- Git
- Python 3 and pip, as required by the packages
- colcon build tools
- rosdep
- Dependencies declared by the ROS 2 packages
- micro-ROS tools and the required embedded firmware environment
- A compatible joystick or PS3 controller, if using teleoperation

Additional dependencies may be required by individual packages.

## 5. Tutorial: Build, Run and Launch

This tutorial explains how to prepare the ROS 2 environment, build the
workspace, inspect ROS 2 nodes and topics, and launch the robot software.

### 5.1. Build the project
First, you should build all workspace. Remember to supply power to the devices and sensors, such as the IMU, Lidar, ESP32, and the two motor drivers. Crucially, the robot must have its wheels locked (i.e., velocity at zero) before the entire system is started. 

***Important Note: Power the driver first and the ESP32 second; the robot's wheels will then lock.***

Copy and run the following commands:
```bash
cd ~/skid_robot_v2
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install --parallel-workers 1
```
### 5.2 Launch the project
After successfully building the workspace, run the commands below to start the system:
```bash
cd ~/skid_robot_v2
ros2 launch bringup bringup_2.py
```
