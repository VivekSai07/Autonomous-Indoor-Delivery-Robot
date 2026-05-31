# Autonomous Indoor Delivery Robot

A fully autonomous indoor delivery robot built with ROS2 Humble, Gazebo Classic 11, Nav2, SLAM Toolbox, and EKF sensor fusion. Implements mapping, localization, path planning, obstacle avoidance, multi-goal mission execution, and AprilTag-based docking in simulation.

---

## Overview

This project builds an AMR (Autonomous Mobile Robot) step-by-step across 9 phases, covering every core autonomy component used in real warehouse/delivery robotics:

| Phase | Skill |
|-------|-------|
| 1 | Robot URDF model (differential drive, LiDAR, IMU, Camera) |
| 2 | Wheel odometry + TF tree |
| 3 | EKF sensor fusion (wheel odom + IMU) |
| 4 | SLAM mapping with SLAM Toolbox |
| 5 | Localization with AMCL |
| 6 | Autonomous navigation with Nav2 |
| 7 | Dynamic obstacle avoidance |
| 8 | Multi-goal mission execution |
| 9 | AprilTag-based docking |

---

## Prerequisites

- Ubuntu 22.04 (or WSL2 on Windows)
- [ROS2 Humble](https://docs.ros.org/en/humble/Installation.html) (full desktop install)
- Gazebo Classic 11 (`ros-humble-gazebo-ros-pkgs`)
- Git

### Install Dependencies

```bash
sudo apt update && sudo apt install \
  ros-humble-gazebo-ros-pkgs \
  ros-humble-robot-localization \
  ros-humble-slam-toolbox \
  ros-humble-nav2-bringup \
  ros-humble-nav2-simple-commander \
  ros-humble-apriltag-ros \
  ros-humble-teleop-twist-keyboard \
  ros-humble-tf2-tools \
  ros-humble-joint-state-publisher-gui
```

### WSL2 Setup Note

Before launching any GUI tool (Gazebo, RViz), ensure your display server is running:

```bash
export DISPLAY=:0       # or the value shown by 'echo $DISPLAY'
```

---

## Workspace Setup

```bash
# Clone the repo
git clone <repo-url> ~/amr_ws
cd ~/amr_ws

# Source ROS2
source /opt/ros/humble/setup.bash

# Build
colcon build --symlink-install

# Source the workspace
source install/setup.bash
```

---

## Launch Commands

> Commands are added here as each phase is completed.

### Phase 1 — View Robot Model

```bash
# RViz only (no simulation)
ros2 launch robot_description display.launch.py

# Gazebo simulation
ros2 launch robot_gazebo gazebo.launch.py
```

### Phase 2 — Teleoperate

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

### Phase 3 — EKF Sensor Fusion

```bash
ros2 launch robot_localization_cfg ekf.launch.py
```

### Phase 4 — SLAM Mapping

```bash
ros2 launch robot_slam slam.launch.py
# Save map when done:
ros2 run nav2_map_server map_saver_cli -f ~/amr_ws/maps/office_map
```

### Phase 5 — Localization (AMCL)

```bash
ros2 launch robot_slam localization.launch.py
```

### Phase 6 — Nav2 Navigation

```bash
ros2 launch robot_nav2 navigation.launch.py
# Then use "2D Nav Goal" in RViz
```

### Phase 8 — Autonomous Mission

```bash
ros2 launch robot_missions mission.launch.py
```

---

## Architecture

> Architecture diagram will be added in docs/ after Phase 6.

## TF Tree

> TF tree diagram will be added in docs/ after Phase 2.

---

## Repository Structure

```
amr_ws/
├── src/
│   ├── robot_description/       # URDF/Xacro, meshes, RViz config
│   ├── robot_gazebo/            # Gazebo worlds, spawn launch
│   ├── robot_bringup/           # Top-level launch files
│   ├── robot_localization_cfg/  # EKF configuration
│   ├── robot_slam/              # SLAM Toolbox + AMCL config
│   ├── robot_nav2/              # Nav2 params and costmap config
│   ├── robot_missions/          # Multi-goal mission executor
│   └── robot_docking/           # AprilTag docking controller
├── maps/                        # Saved maps (generated)
├── docs/                        # Diagrams and videos
├── TODO.md
└── README.md
```

---

## License

MIT
