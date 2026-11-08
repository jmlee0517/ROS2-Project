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
| End-Effector Pose Tracking (TF) | Completed |
| IK Computation-Time Measurement | Completed |
| Automated Gazebo Experiment Runner | Completed |
| Analytical IK Performance Evaluation (40 trials) | Completed |
| PyTorch Neural Network for Inverse Kinematics | Planned |
| Analytical vs. PyTorch Comparative Evaluation | Planned |

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

The analytical IK node also measures its own solver execution time using
`time.perf_counter()` and publishes the result to `/ik_computation_time`
as a `std_msgs/msg/Float64` value in seconds. This measures the IK
calculation itself, not the robot's movement time.


---

## Automated Gazebo Experiments

The project includes an automated experiment pipeline for evaluating the
analytical inverse kinematics implementation in Gazebo.

### 16. Experiment Pipeline

The experiment uses the same Gazebo robot, `ros2_control` controller, and
analytical IK node as the manual workflow. The end-effector pose is tracked
through TF, and the experiment runner evaluates a sequence of target positions.

Open the following terminals after launching Gazebo and confirming that both
controllers are active.

**Terminal 1 — Gazebo**

```bash
ros2 launch robot_arm_description gazebo.launch.py
```

**Terminal 2 — Joint target-to-trajectory adapter**

```bash
ros2 run my_py_pkg joint_target_to_trajectory
```

**Terminal 3 — Analytical inverse kinematics**

```bash
ros2 run my_py_pkg inverse_kinematics
```

**Terminal 4 — End-effector pose tracker**

```bash
ros2 run my_py_pkg end_effector_tracker --ros-args -p use_sim_time:=true
```

The tracker looks up the transform from `world` to `end_effector` and
publishes the measured pose to `/end_effector_pose` as a
`geometry_msgs/msg/PoseStamped` message.

**Terminal 5 — Experiment runner**

```bash
ros2 run my_py_pkg experiment_runner --ros-args -p use_sim_time:=true
```

The experiment runner publishes the predefined target positions sequentially,
monitors the end-effector pose, and records the result of each trial.

### 17. Experiment Measurements

The experiment runner records the following metrics for each target:

| Metric | Description | Unit |
|---|---|---|
| Positioning error | Euclidean distance between the target and measured end-effector position | m |
| Target execution time | Time from target publication until the end effector reaches and remains within the position tolerance | s |
| IK computation time | Time spent calculating the analytical IK solution, measured with `time.perf_counter()` | ms |
| Trial status | Whether the target satisfied the experiment's success criteria | — |

The current experiment settings are:

- Number of target positions: 40
- Position tolerance: 0.002 m (2 mm)
- Required stable duration: 0.5 s
- Target trajectory duration: 3 s
- Experiment timeout: 15 s (simulation time)

**Timing clarification:** The trajectory sent to the joint trajectory controller
has a configured duration of 3 seconds. The recorded target execution time is
not fixed to 3 seconds: it is measured by the experiment runner and also
includes communication/controller overhead and the stability-check interval.
It should therefore be interpreted as end-to-end target execution time rather
than isolated physical motion time.

IK computation time is measured separately inside the analytical IK node.
It represents solver computation time and does not include Gazebo movement.

### 18. Experiment Output

The experiment results are saved to:

```text
~/ROS2-Project/experiments/analytical_results.csv
```

The CSV contains one row per trial, followed by an automatically generated
experiment summary containing aggregate statistics such as:

- Total, successful, and failed trials
- Success rate
- Mean, median, and maximum positioning error
- Positioning error RMSE
- Mean, minimum, and maximum target execution time
- Mean, minimum, and maximum IK computation time

The experiment runner uses ROS simulation time. Make sure the Gazebo clock
bridge is running and `/clock` is advancing before starting the experiment.

### 19. Analytical IK Baseline

The automated experiment pipeline establishes the analytical IK baseline
that will be used for comparison with the planned PyTorch-based approach.
The two approaches will be evaluated under consistent conditions, using the
same robot model, target set, Gazebo controller, and measurement criteria.

The PyTorch implementation and comparative evaluation are still planned;
they are not part of the current completed implementation.

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

## Learning-Based Inverse Kinematics

In addition to the analytical inverse kinematics solver, this project introduces a learning-based approach using PyTorch. A Multi-Layer Perceptron (MLP) is trained to predict the four joint angles required to reach a desired end-effector position.

### Dataset Generation

A dataset of 50,000 samples is generated using the robot's forward kinematics model.

- **Input:** End-effector position (x, y, z)
- **Output:** Joint angles (base rotation, shoulder, elbow, wrist)
- **Sampling:** Uniform random sampling in joint space
- **Random seed:** 42
- **Elbow configuration:** Positive-elbow branch
- **End-effector pitch:** Fixed at π radians

Each generated sample is validated against the robot's joint limits and forward kinematics model to ensure consistency.

Dataset location: `datasets/ik_dataset.csv`

### Neural Network Architecture

The inverse kinematics model is implemented as a Multi-Layer Perceptron (MLP).

| Layer | Configuration |
|---|---|
| Input | 3 neurons (x, y, z) |
| Hidden layer 1 | 128 neurons, ReLU |
| Hidden layer 2 | 128 neurons, ReLU |
| Hidden layer 3 | 64 neurons, ReLU |
| Output | 4 neurons (joint angles) |

**Training configuration:**
- Train / validation / test split: 70% / 15% / 15%
- Optimizer: Adam
- Learning rate: 0.001
- Batch size: 128
- Loss function: Mean Squared Error (MSE)
- Maximum epochs: 200
- Early stopping patience: 20 epochs
- Input normalization using training-set statistics

The best-performing model is saved to `models/pytorch_ik_model.pth`.

### PyTorch Model Evaluation

The trained model was evaluated on 7,500 previously unseen test samples.

**Joint-angle prediction errors**

| Joint | Mean Absolute Error |
|---|---:|
| Base rotation | 0.003528 rad |
| Shoulder | 0.002886 rad |
| Elbow | 0.003772 rad |
| Wrist | 0.002578 rad |

**Cartesian positioning accuracy**

| Metric | Result |
|---|---:|
| Mean positioning error | 0.918 mm |
| Median positioning error | 0.867 mm |
| Maximum positioning error | 4.056 mm |
| RMSE | 1.004 mm |
| 95th percentile error | 1.657 mm |
| Success rate (within 2 mm) | 98.68% |

**Inference performance**

| Metric | Result |
|---|---:|
| Average single-sample inference time | 0.191 ms |

The 2 mm positioning threshold corresponds to the tolerance used in the Gazebo experiment runner.

*Note: These results are from an offline randomly held-out test set. They do not yet represent a direct comparison against the analytical solver in Gazebo.*
