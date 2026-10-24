# skidsteer-ros-2
Skidsteer | ROS 2 Humble | Ubuntu 22.04

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

The exact nodes, topics, launch files, and hardware interfaces depend on
the implementation in this repository.


## 2. Tutorial: Build, Run and Launch

This tutorial explains how to prepare the ROS 2 environment, build the
workspace, inspect ROS 2 nodes and topics, and launch the robot software.

### 2.1. Build the project
First step, gitclone or download this reposity:
```bash
git clone https://github.com/HaIBotLab/skidsteer-ros-2
```
Aftêr that, build all workspace.

Copy and run the following commands:
```bash
cd ~/skid_robot_v2
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install --parallel-workers 1
```
### 2.2 Launch the project
Remember to supply power to the devices and sensors, such as the IMU, Lidar, ESP32, and the two motor drivers. Crucially, the robot must have its wheels locked (i.e., velocity at zero) before the entire system is started. 

***Important Note: Power the driver first and the ESP32 second; the robot's wheels will then lock.***

After successfully building the workspace, run the commands below to start the system:
```bash
cd ~/skid_robot_v2
source install/setup.bash
ros2 launch bringup bringup_2.py
```
