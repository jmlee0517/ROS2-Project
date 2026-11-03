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

- **ROS 2 Lyrical** – Robot communication and control
- **Python** – Algorithm implementation
- **PyTorch** – Neural network development
- **Gazebo Sim** – Physics-based robot simulation
- **ros2_control** – Robot hardware abstraction and controller management
- **URDF** – Robot description and modeling
- **RViz2** – Robot visualization

## Current Implementation

| Component | Status |
|---|---|
| 2-DOF Robot Arm URDF | Completed |
| 4-DOF Robot Arm URDF | Completed |
| Forward Kinematics | Completed |
| Analytical Inverse Kinematics | Completed |
| Joint State Bridge (RViz) | Completed |
| Python Trajectory Controller (RViz) | Completed |
| RViz Visualization | Completed |
| Gazebo Simulation Integration | Completed |
| ros2_control Integration | Completed |
| Joint Trajectory Controller (Gazebo) | Completed |
| IK-to-Gazebo Command Integration | Completed |
| PyTorch Neural Network for Inverse Kinematics | Planned |
| Comparative Performance Evaluation | Planned |

## Installation & Usage

### 1. System Requirements

- Ubuntu 26.04
- ROS 2 Lyrical
- Python 3
- Gazebo Sim 10
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

---

## RViz Visualization

The RViz workflow uses a custom joint-state bridge and Python trajectory controller to visualize the robot's movement.

### 4. Launch the Robot Description

Open **Terminal 1**:

```bash
ros2 launch robot_arm_description display.launch.py
```

This launches the `robot_state_publisher` node using:

```text
robot_arm_description/urdf/robot_arm_4dof.urdf
```

The `robot_state_publisher` calculates and publishes TF transformations based on incoming joint states.

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

```bash
ros2 run my_py_pkg joint_state_bridge
```

The `joint_state_bridge` node:

- Subscribes to `/joint_commands`.
- Stores the received joint angles in `joint_positions`.
- Publishes the complete joint state to `/joint_states` at 30 Hz.

The published joint states are used by `robot_state_publisher` to update the robot's TF transformations.

**Note:** Do not run `joint_state_publisher` simultaneously with this bridge, because both would publish to `/joint_states`.

### 7. Launch the Python Trajectory Controller

Open **Terminal 4**:

```bash
ros2 run my_py_pkg trajectory_controller
```

The trajectory controller receives joint targets and generates time-based joint commands.

### 8. Launch the Inverse Kinematics Node

Open **Terminal 5**:

```bash
ros2 run my_py_pkg inverse_kinematics
```

The node subscribes to `/target_position` and calculates the required joint angles.

It publishes the calculated joint positions to `/joint_targets`. The trajectory controller receives these targets and publishes interpolated joint commands to `/joint_commands`.

The target end-effector pitch is currently configured as 180 degrees (pointing downward).

### 9. Send a Target Position

Open **Terminal 6**:

```bash
ros2 topic pub --once /target_position geometry_msgs/msg/Point "{x: 0.12, y: 0.0, z: 0.15}"
```

The inverse kinematics node calculates the joint angles, and the trajectory controller generates the corresponding joint commands.

The joint state bridge updates `/joint_states`, allowing `robot_state_publisher` to update the TF transformations and RViz to visualize the resulting configuration.

---

## Gazebo Simulation

The Gazebo workflow uses Gazebo Sim together with `gz_ros2_control` and a ROS 2 joint trajectory controller.

Unlike the RViz workflow, Gazebo directly simulates the robot's joints and physics.

### 10. Launch Gazebo and Spawn the Robot

Open **Terminal 1**:

```bash
ros2 launch robot_arm_description gazebo.launch.py
```

This launch file:

- Starts Gazebo Sim.
- Loads the Gazebo-specific 4-DOF robot description.
- Spawns the robot into the simulation world.
- Initializes the `gz_ros2_control` plugin.
- Starts the ROS 2 controller manager.

The Gazebo-specific robot description is:

```text
robot_arm_description/urdf/robot_arm_4dof_gazebo.urdf
```

The robot uses the `gz_ros2_control/GazeboSimSystem` hardware interface to communicate with Gazebo's physics simulation.

### 11. Verify the Controllers

Once Gazebo has started, open **Terminal 2**:

```bash
ros2 control list_controllers
```

Both controllers should be active:

```text
arm_controller          joint_trajectory_controller/JointTrajectoryController  active
joint_state_broadcaster joint_state_broadcaster/JointStateBroadcaster          active
```

The `joint_state_broadcaster` publishes the simulated joint states, while the `arm_controller` executes joint trajectories.

### 12. Launch the Joint Target-to-Trajectory Adapter

Open **Terminal 3**:

```bash
ros2 run my_py_pkg joint_target_to_trajectory
```

The `joint_target_to_trajectory` node:

- Subscribes to `/joint_targets`.
- Maps the joint positions using their joint names.
- Converts the received positions into a `JointTrajectory` message.
- Publishes the trajectory to `/arm_controller/joint_trajectory`.

Each trajectory currently uses a 3-second execution duration.

### 13. Launch the Inverse Kinematics Node

Open **Terminal 4**:

```bash
ros2 run my_py_pkg inverse_kinematics
```

The node subscribes to `/target_position` and calculates the required joint angles.

It publishes the resulting joint positions to `/joint_targets`, which are then converted into trajectories by the adapter node.

### 14. Control the Robot in Gazebo

Open **Terminal 5** and publish a target position:

```bash
ros2 topic pub --once /target_position geometry_msgs/msg/Point "{x: 0.12, y: 0.0, z: 0.15}"
```

The robot should move toward the specified end-effector position in Gazebo.

You can send additional target positions while the nodes are running:

```bash
ros2 topic pub --once /target_position geometry_msgs/msg/Point "{x: 0.15, y: 0.0, z: 0.20}"
```

### 15. Gazebo ROS 2 Communication Architecture

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
joint_target_to_trajectory
       |
       v
/arm_controller/joint_trajectory
       |
       v
joint_trajectory_controller
       |
       v
gz_ros2_control
       |
       v
Gazebo Sim
       |
       v
Robot Movement
```

The joint states are published separately through:

```text
Gazebo Sim
       |
       v
gz_ros2_control
       |
       v
joint_state_broadcaster
       |
       v
/joint_states
```

---

## Example Target Positions

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