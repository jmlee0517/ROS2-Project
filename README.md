# ROS 2 4-DOF Robotic Manipulator: Analytical vs. Learning-Based Inverse Kinematics

## About

This project focuses on the development of a 4-DOF robotic manipulator using ROS 2, with the goal of comparing conventional analytical inverse kinematics against a neural network-based approach implemented using PyTorch.

The project explores two methods of solving inverse kinematics and evaluates their performance in a Gazebo simulation environment. Key evaluation criteria include end-effector positioning accuracy, computational efficiency, and generalization to unseen target positions.

By combining mechanical modeling, robot kinematics, and machine learning, this project aims to investigate the potential of learning-based approaches in robotic motion control.

## Objectives

- Develop a 4-DOF robotic manipulator model using URDF.
- Implement analytical inverse kinematics.
- Develop a neural network for inverse kinematics using PyTorch.
- Integrate both approaches with ROS 2 and Gazebo.
- Compare their performance under consistent simulation conditions.

## Technologies

- **ROS 2** – Robot communication and control
- **Python** – Algorithm implementation
- **PyTorch** – Neural network development
- **Gazebo** – Physics-based robot simulation
- **URDF** – Robot description and modeling
- **RViz** – Robot visualization

## Current Implementation

| Component | Status |
|---|---|
| 2-DOF Robot Arm URDF | Completed |
| 4-DOF Robot Arm URDF | Completed |
| Forward Kinematics | Completed |
| Analytical Inverse Kinematics | Completed |
| Joint State Bridge | Completed |
| Trajectory Controller | Completed |
| RViz Visualization | Completed |
| Gazebo Simulation Integration | Planned |
| PyTorch Neural Network for Inverse Kinematics | Planned |
| Comparative Performance Evaluation | Planned |

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

### 7. Launch the Trajectory Controller

Open **Terminal 4**:

Run the trajectory controller node:

```bash
ros2 run my_py_pkg trajectory_controller
```

### 8. Launch the Inverse Kinematics Node

Open **Terminal 5**:

Run the inverse kinematics node:

```bash
ros2 run my_py_pkg inverse_kinematics
```

The node subscribes to `/target_position` and calculates the required joint angles.

It publishes the calculated target joint positions to `/joint_targets`. The trajectory controller receives these targets and generates time-based joint trajectories, publishing interpolated joint commands to `/joint_commands`.

The target end-effector pitch is currently configured as 180 degrees (pointing downward).

### 9. Send a Target Position

Open **Terminal 6** and source the ROS 2 environment:

Publish a target position using `geometry_msgs/msg/Point`:

```bash
ros2 topic pub --once /target_position geometry_msgs/msg/Point "{x: 0.12, y: 0.0, z: 0.15}"
```

The inverse kinematics node calculates the joint angles and publishes them to `/joint_commands`.

The joint state bridge receives these commands and updates `/joint_states`.

Finally, `robot_state_publisher` updates the TF transformations, and RViz visualizes the resulting robot configuration.

### 10. ROS 2 Communication Architecture

```text
/target_position
       |
       v
inverse_kinematics
       |
       v
/joint_targets
       |
       v
trajectory_controller
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

### 11. Example Target Positions

The following target positions have been verified against the analytical inverse kinematics model and its joint limits.

All coordinates are specified in meters.

| Test | X (m) | Y (m) | Z (m) | Description |
|---|---:|---:|---:|---|
| A | 0.12 | 0.00 | 0.15 | Reference position |
| B | 0.14 | 0.00 | 0.14 | Forward movement |
| C | 0.16 | 0.00 | 0.12 | Extended forward position |
| D | 0.10 | 0.00 | 0.16 | Upper position |
| E | 0.12 | 0.05 | 0.15 | Positive base rotation |
| F | 0.12 | -0.05 | 0.15 | Negative base rotation |
| G | 0.15 | 0.05 | 0.14 | Forward diagonal (+Y) |
| H | 0.15 | -0.05 | 0.14 | Forward diagonal (-Y) |
| I | 0.10 | 0.05 | 0.16 | Upper diagonal (+Y) |

Example command:

```bash
ros2 topic pub --once /target_position geometry_msgs/msg/Point "{x: 0.14, y: 0.0, z: 0.14}"
```

**Note:** These positions are valid for the current robot geometry, joint limits, and fixed end-effector pitch of 180 degrees. Physical collisions and hardware reachability have not yet been evaluated.
