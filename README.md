# ROS2-Project

A vision-guided robotic arm project built with ROS 2 and Python, with plans to integrate PyTorch-based imitation learning.

## Overview

The goal of this project is to develop a low-cost robotic arm simulation that can detect objects, estimate their positions, and learn manipulation behaviors from demonstrations.

The project combines robotics fundamentals, computer vision, inverse kinematics, and deep learning.

## Current Features

- **Robot Description:** A two-joint robotic arm modeled using URDF.
- **Forward Kinematics:** Calculates the end-effector position from joint angles.
- **Inverse Kinematics:** Calculates joint angles for a specified target position.
- **ROS 2 Communication:** Uses ROS 2 topics to exchange target positions, joint commands, and joint states.
- **RViz Visualization:** Visualizes the robot model and simulates joint movements.

## Planned Features

- **Camera Integration:** Use the laptop's built-in camera with OpenCV to detect colored objects.
- **Coordinate Calibration:** Map image coordinates to the robot's workspace.
- **Demonstration Dataset:** Record observations and actions from manipulation tasks.
- **PyTorch Imitation Learning:** Train a neural network using behavior cloning to predict robot actions from demonstrations.
- **ROS 2 Integration:** Connect the trained model to the robot simulation.
- **Evaluation:** Compare learned behavior with the conventional inverse-kinematics baseline.

## Tech Stack

- Ubuntu Linux
- ROS 2
- Python
- URDF
- RViz
- OpenCV (planned)
- PyTorch (planned)

## Project Goal

Build a modular robotic manipulation pipeline that combines classical robotics with learning-based control, providing a foundation for exploring imitation learning and more advanced vision-based robotic policies.

## Status

Currently developing the ROS 2 robot arm simulation and kinematics pipeline. Camera integration and PyTorch-based learning are planned next.

