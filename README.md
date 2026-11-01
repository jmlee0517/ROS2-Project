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

## Installation & Usage

### 1. My setup

- Ubuntu 26.04
- ROS 2 Lyrical
- Python 3
- RViz2
- Colcon

### 2. Clone the Repository

```bash
git clone https://github.com/jmlee0517/ROS2-Project.git
cd ROS2-Project
```

### 3. Build the Workspace

Source the ROS 2 environment:

```bash
source /opt/ros/lyrical/setup.bash
```

Build the workspace:

```bash
colcon build --symlink-install
```

Source the workspace:

```bash
source install/setup.bash
```

### 4. Launch the Robot Description

Open **Terminal 1**.

Navigate to the workspace and source the environment:

```bash
cd ~/ROS2-Project
source /opt/ros/lyrical/setup.bash
source install/setup.bash
```

Launch the 4-DOF robot model:

```bash
ros2 launch robot_arm_description display.launch.py
```

This launches the `robot_state_publisher` node using:

```text
robot_arm_description/urdf/robot_arm_4dof.urdf
```

The `robot_state_publisher` calculates and publishes TF transformations based on the incoming joint states.

### 5. Launch RViz2

Open **Terminal 2**:

```bash
rviz2
```

Configure RViz:

1. Set the Fixed Frame to `base_link`.
2. Add a `RobotModel` display.
3. Set the Robot Description parameter to `robot_description` if required.

The 4-DOF robot arm should now appear in RViz.

### 6. Launch the Joint State Bridge

Open **Terminal 3**:

Run the bridge node:

```bash
ros2 run my_py_pkg joint_state_bridge
```

The `joint_state_bridge` node:

- Subscribes to `/joint_commands` to receive joint angles calculated by the inverse kinematics node.
- Stores the received joint angles in `joint_positions`.
- Publishes the complete joint state to `/joint_states` at 30 Hz.

The published joint states are then used by `robot_state_publisher` to update the robot's TF transformations.

**Note:** Do not run `joint_state_publisher` simultaneously with this bridge, because both would publish to `/joint_states`.

### 7. Launch the Inverse Kinematics Node

Open **Terminal 4**:

Run the inverse kinematics node:

```bash
ros2 run my_py_pkg inverse_kinematics
```

The node subscribes to `/target_position` and calculates the required joint angles.

It publishes the calculated joint commands to `/joint_commands`.

The target end-effector pitch is currently configured as 180 degrees (pointing downward).

### 8. Send a Target Position

Open **Terminal 5** and source the ROS 2 environment:

Publish a target position using `geometry_msgs/msg/Point`:

```bash
ros2 topic pub --once /target_position geometry_msgs/msg/Point "{x: 0.12, y: 0.0, z: 0.15}"
```

The inverse kinematics node calculates the joint angles and publishes them to `/joint_commands`.

The joint state bridge receives these commands and updates `/joint_states`.

Finally, `robot_state_publisher` updates the TF transformations, and RViz visualizes the resulting robot configuration.

### 9. ROS 2 Communication Architecture

```text
/target_position
       |
       v
inverse_kinematics
       |
       v
/joint_commands
       |
       v
joint_state_bridge
       |
       v
/joint_states
       |
       v
robot_state_publisher
       |
       v
      RViz
```

### 10. Verify ROS 2 Topics

Check active nodes:

```bash
ros2 node list
```

Check available topics:

```bash
ros2 topic list
```

Inspect joint commands:

```bash
ros2 topic echo /joint_commands
```

Inspect joint states:

```bash
ros2 topic echo /joint_states
```

Check topic information:

```bash
ros2 topic info /joint_commands
ros2 topic info /joint_states
```

---

## Current Implementation

| Component | Status |
|---|---|
| 2-DOF Robot Arm URDF | Completed |
| Forward Kinematics | Completed |
| 4-DOF Robot Arm URDF | Completed |
| Inverse Kinematics | Completed |
| Joint State Bridge | Completed |
| RViz Visualization | Completed |
| Camera-based Object Detection | Planned |
| PyTorch Integration | Planned |
| ESP32 Hardware Control | Planned |
