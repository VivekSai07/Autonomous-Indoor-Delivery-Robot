# Plan: Autonomous Indoor Delivery Robot

## Context

This is a greenfield ROS2 Humble project to build a fully autonomous indoor delivery robot in simulation. It covers every core autonomy component: URDF modeling, wheel odometry, EKF sensor fusion, SLAM mapping, AMCL localization, Nav2 navigation, dynamic obstacle avoidance, multi-goal mission execution, and AprilTag-based docking. The project runs on WSL2 with Gazebo Classic 11.

**Choices locked in:**
- Simulator: Gazebo Classic 11
- SLAM: SLAM Toolbox
- Docking: AprilTag-based (camera + apriltag_ros)
- Workspace: `~/amr_ws`

---

## Working Rules (Between Us)

1. **TODO.md is truth**: I update TODO.md at the start and end of every phase. Neither of us starts a new phase without the previous one being checked off.
2. **README.md stays live**: Updated after every phase with new setup steps, launch commands, and usage. Must always be accurate enough for a stranger to run the project.
3. **Git after every deliverable**: Commit after each verified sub-deliverable, not just phase completions. Commit messages follow `phase-N: short description` format.
4. **Phase branches**: Each phase lives on `phase-N/description`, merged to `main` when the deliverable is verified.
5. **No skipping**: I will not start Phase N+1 code until the Phase N deliverable is verified by you (robot appears in RViz/Gazebo, goal reached, etc.).
6. **WSL2 hygiene**: Always check `DISPLAY` env var and `ROS_DOMAIN_ID` at launch. Remind you to run `export DISPLAY=:0` (or whatever is set) before Gazebo launches.
7. **Dependency checks before code**: Before writing a package that depends on a new library, I'll verify it's installed or tell you the exact `apt install` command.
8. **Docs update trigger**: Any change that adds a new launch file, parameter, or command → README.md gets updated in the same commit.

---

## Project Structure

```
~/amr_ws/
├── src/
│   ├── robot_description/       # URDF/Xacro, meshes, RViz config
│   ├── robot_gazebo/            # Gazebo worlds, spawn launch, Gazebo plugins config
│   ├── robot_bringup/           # Top-level launch files (sim, nav, full stack)
│   ├── robot_odometry/          # Wheel odometry node (if needed beyond Gazebo plugin)
│   ├── robot_localization_cfg/  # EKF config (wraps robot_localization pkg)
│   ├── robot_slam/              # SLAM Toolbox config + launch
│   ├── robot_nav2/              # Nav2 params, costmap configs, BT XMLs
│   ├── robot_missions/          # Action client mission executor
│   └── robot_docking/           # AprilTag detection + docking controller
├── maps/                        # office_map.yaml + office_map.pgm (generated)
├── docs/                        # Architecture diagram, TF tree, videos
├── TODO.md
└── README.md
```

---

## Phase 0: Project Bootstrap (session 1)

**Goal**: Scaffolding, git, docs skeleton.

Steps:
1. Create workspace at `~/amr_ws/src`
2. `git init` in `~/amr_ws`, add `.gitignore` (ROS2 build artifacts, install/, build/, log/)
3. Write `README.md` skeleton: project overview, prerequisites, workspace setup, per-phase command table (fills in as phases complete)
4. Write `TODO.md` with all phases listed as `[ ]` pending
5. First commit: `phase-0: project bootstrap`

**Deliverable**: Clean git repo with README.md and TODO.md. Build system verified with `colcon build` (no packages yet — just scaffold).

---

## Phase 1: Robot Description

**Package**: `robot_description`

Steps:
1. Create ROS2 ament_cmake package with URDF/Xacro
2. Robot geometry:
   - Differential drive base: 0.3m × 0.25m × 0.15m box chassis
   - 2 drive wheels (r=0.05m), 1 caster ball
   - LiDAR: Hokuyo-style, 270° FOV, mounted on top
   - IMU: fixed to base_link
   - Camera: front-facing (for AprilTag docking in Phase 9)
3. Gazebo plugins in URDF:
   - `libgazebo_ros_diff_drive.so` → publishes `/cmd_vel` control, `/odom`, `/joint_states`
   - `libgazebo_ros_ray_sensor.so` → publishes `/scan`
   - `libgazebo_ros_imu_sensor.so` → publishes `/imu`
   - `libgazebo_ros_camera.so` → publishes `/camera/image_raw`
4. RViz config: display robot model + TF tree
5. Launch files:
   - `display.launch.py` → RViz only (robot_state_publisher + joint_state_publisher_gui)
   - `gazebo.launch.py` → Gazebo + spawn robot

**Deliverable**: `ros2 launch robot_description display.launch.py` shows robot in RViz; `ros2 launch robot_gazebo gazebo.launch.py` spawns robot in Gazebo with sensor topics active.

**Critical files**: `robot_description/urdf/robot.urdf.xacro`, `robot_description/launch/display.launch.py`, `robot_gazebo/launch/gazebo.launch.py`

---

## Phase 2: Odometry

**Source**: Gazebo diff drive plugin (already publishes `/odom` and TF `odom→base_link` from Phase 1).

Steps:
1. Verify `/odom` topic publishing correct geometry_msgs/Odometry
2. Verify TF tree: `odom → base_footprint → base_link → ... → sensors`
3. Drive robot with `teleop_twist_keyboard` and watch pose drift in RViz
4. Document drift behavior in README.md

**Deliverable**: Robot position updates correctly in RViz as you teleoperate. TF tree complete with `ros2 run tf2_tools view_frames`.

---

## Phase 3: Sensor Fusion (EKF)

**Package**: `robot_localization_cfg`
**Dependency**: `robot_localization` (ROS2 pkg, EKF node)

Steps:
1. Create package with `ekf.yaml` config
2. Fuse: `/odom` (wheel) + `/imu` (angular velocity + linear acceleration)
3. EKF publishes `/odometry/filtered` and TF `odom → base_footprint`
4. Launch file: `ekf.launch.py`
5. Verify smoother pose estimate vs raw odometry using PlotJuggler or RViz

**Deliverable**: `/odometry/filtered` shows measurably less drift/jitter than raw `/odom` during teleop.

---

## Phase 4: SLAM

**Package**: `robot_slam`
**Dependency**: `slam_toolbox`

Steps:
1. Config: `slam_toolbox/config/mapper_params_online_async.yaml`
2. Input: `/scan` (LiDAR), `/odometry/filtered` (EKF pose)
3. Launch: `slam.launch.py` (async online mode)
4. Teleoperate robot around simulated office environment to build map
5. Save map: `ros2 run nav2_map_server map_saver_cli -f ~/amr_ws/maps/office_map`
6. Outputs: `maps/office_map.yaml` + `maps/office_map.pgm`

**Deliverable**: Robot maps simulated environment. Map image shows walls/obstacles clearly.

---

## Phase 5: Localization (AMCL)

**Package**: `robot_slam` (add localization launch)
**Dependency**: `nav2_amcl`, `nav2_map_server`

Steps:
1. `map_server` launch: serves `office_map.yaml`
2. AMCL config: `amcl_params.yaml` (particle count, laser model params)
3. Launch: `localization.launch.py`
4. Set initial pose in RViz (`2D Pose Estimate`)
5. Drive robot → verify particle cloud converges
6. Test pose recovery: manually delocalize, verify recovery

**Deliverable**: AMCL particle cloud visible in RViz, converges to correct pose. Robot stays localized during teleop.

---

## Phase 6: Nav2 Navigation

**Package**: `robot_nav2`
**Dependency**: `nav2_bringup`, `nav2_planner`, `nav2_controller`, `nav2_bt_navigator`

Steps:
1. Nav2 params file: `nav2_params.yaml`
   - Planner: `NavfnPlanner` (fallback to `SmacPlanner`)
   - Controller: `DWBLocalPlanner`
   - BT Navigator: default `navigate_to_pose_w_replanning_and_recovery.xml`
2. Global costmap: static layer (map) + obstacle layer (LiDAR)
3. Local costmap: inflation layer + obstacle layer (LiDAR)
4. Launch: `navigation.launch.py` (includes map server + AMCL + Nav2 stack)
5. In RViz: send `2D Nav Goal` → robot plans and drives to goal

**Deliverable**: Click goal in RViz → robot reaches it autonomously, stopping cleanly.

---

## Phase 7: Dynamic Obstacles

**Package**: `robot_gazebo` (add dynamic actor world)

Steps:
1. Create Gazebo world with walking actor (animated human) using `<actor>` SDF
2. Spawn actor walking on a loop that crosses the robot's typical path
3. Verify: Nav2 replans when actor blocks path
4. Tune recovery behaviors in `nav2_params.yaml` if needed

**Deliverable**: Robot navigates to goal even when moving actor blocks initial path. No collision, successful arrival.

---

## Phase 8: Multi-Goal Mission

**Package**: `robot_missions`

Steps:
1. Create ROS2 node `mission_executor.py` using `nav2_simple_commander` Python API (or raw Action Client to `NavigateToPose`)
2. Define 5 waypoints in code: Dock, Room A, Room B, Room C, Home (as `PoseStamped` in map frame)
3. Sequential mission loop with status logging
4. Launch: `mission.launch.py`

**Deliverable**: `ros2 launch robot_missions mission.launch.py` → robot visits all 5 waypoints in sequence, returns home.

---

## Phase 9: Docking (AprilTag)

**Package**: `robot_docking`
**Dependencies**: `apriltag_ros`, `image_geometry`

Steps:
1. Add AprilTag marker to Gazebo charging station model (36h11 family, tag ID 0)
2. URDF camera already set up from Phase 1 (`/camera/image_raw`)
3. `apriltag_ros` continuous detection node: publishes tag pose in camera frame
4. Docking controller node:
   - Subscribe to `/tag_detections`
   - Transform tag pose to base_link frame using TF
   - PID-based approach: align heading → drive forward → stop at dock distance
5. Mission integration: final waypoint triggers docking

**Deliverable**: Robot detects AprilTag on dock, approaches, and stops accurately at docking position.

---

## Verification Strategy (Per Phase)

| Phase | Verification Command |
|-------|---------------------|
| 0 | `colcon build --symlink-install` succeeds |
| 1 | `ros2 launch robot_description display.launch.py` → robot in RViz |
| 2 | `ros2 topic echo /odom` shows pose updating during teleop |
| 3 | Compare `/odom` vs `/odometry/filtered` noise in RViz |
| 4 | Map image shows walls; `maps/office_map.pgm` saved |
| 5 | Particle cloud converges after `2D Pose Estimate` in RViz |
| 6 | `2D Nav Goal` in RViz → robot reaches goal |
| 7 | Robot navigates around moving actor |
| 8 | Mission node completes 5-waypoint loop |
| 9 | Robot docks to AprilTag station autonomously |

---

## README.md Structure

```
# Autonomous Indoor Delivery Robot
## Overview
## Prerequisites (ROS2 Humble, Gazebo Classic 11, WSL2 setup)
## Workspace Setup
## Per-Phase Launch Commands
## Architecture Diagram
## TF Tree
## Videos
```

## TODO.md Structure

```
## Project Status
- [x] Phase 0: Bootstrap
- [ ] Phase 1: Robot Description
...
## Current Phase: X
## Known Issues
## Next Steps
```

---

## Dependency Install Commands (Ready to Run)

```bash
sudo apt install \
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
