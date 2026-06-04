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

Before launching any GUI tool (Gazebo, RViz), run these two setup steps:

```bash
# 1. Display server (required for Gazebo and RViz)
export DISPLAY=:0       # or the value shown by 'echo $DISPLAY'

# 2. ROS2 CLI daemon — REQUIRED on WSL2 before ros2 topic list / ros2 service list
#    Without this, all ros2 CLI commands hang indefinitely on WSL2.
ros2 daemon start
```

> **Why the daemon?** On WSL2, the ROS2 CLI daemon is not started automatically.
> Without it, `ros2 topic list`, `ros2 topic echo`, `ros2 service list` all hang.
> Run `ros2 daemon start` once per WSL2 session. The launch file also starts it
> automatically, but it's good practice to run it manually first.

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

### Phase 1 — Robot Model

> **Prerequisite (Gazebo only):**
> ```bash
> sudo apt install ros-humble-gazebo-ros-pkgs
> ```

```bash
# WSL2: ensure display is set
export DISPLAY=:0

# Source workspace (required every new terminal)
source /opt/ros/humble/setup.bash && source ~/amr_ws/install/setup.bash

# View robot in RViz only (no Gazebo needed)
ros2 launch robot_description display.launch.py

# Launch Gazebo simulation (auto-spawns robot when ready)
ros2 launch robot_gazebo gazebo.launch.py
```

**Topics published (Gazebo):**

| Topic | Type | Source |
|-------|------|--------|
| `/odom` | `nav_msgs/Odometry` | diff drive plugin |
| `/scan` | `sensor_msgs/LaserScan` | LiDAR plugin |
| `/imu` | `sensor_msgs/Imu` | IMU plugin |
| `/camera/image_raw` | `sensor_msgs/Image` | Camera plugin |
| `/cmd_vel` | `geometry_msgs/Twist` | subscribed (teleop) |

**Verify all topics are live:**
```bash
ros2 topic list | grep -E "odom|scan|imu|camera|cmd_vel"
ros2 topic hz /scan        # should report ~10 Hz
ros2 topic hz /odom        # should report ~10 Hz
```

**Kill Gazebo cleanly between runs:**
```bash
pkill -f gzserver; pkill -f gzclient
```

---

## WSL2 Known Issues & Fixes (Phase 1)

These issues were encountered and resolved on WSL2 + Gazebo Classic 11 + ROS2 Humble.
Documented here so they don't need to be debugged again in future phases.

### 1. `robot_description` parameter YAML parse error

**Error:** `Unable to parse the value of parameter robot_description as yaml`

**Cause:** ROS2 Humble's `robot_state_publisher` tries to parse every parameter as YAML. A raw URDF string is not valid YAML.

**Fix:** Wrap the xacro command with `ParameterValue`:
```python
from launch_ros.parameter_descriptions import ParameterValue
robot_description = ParameterValue(Command(['xacro ', urdf_file]), value_type=str)
```

### 2. Gazebo model database empty — robot falls through the floor

**Error:** Robot spawns but immediately falls through the floor with no ground.

**Cause:** `<include><uri>model://ground_plane</uri></include>` silently fails when
`~/.gazebo/models/` is empty (default on fresh WSL2 installs).

**Fix:** Inline the ground plane and sun light directly in the SDF world file instead
of relying on the model database. See `src/robot_gazebo/worlds/office.world`.

### 3. Robot tips backward in Gazebo

**Cause:** With drive wheels at `x=0` (chassis center) and only a front caster, the
centre of gravity sits exactly on the wheel axle line — unstable equilibrium.

**Fix:** Added a rear caster (`caster_wheel_rear`) mirroring the front one. This creates
a stable rectangular support base:
```
rear caster (-0.125, 0) ←→ front caster (+0.125, 0)
left wheel  (0, +0.145) ←→ right wheel  (0, -0.145)
CG ≈ (0, 0) — dead centre of rectangle
```

### 4. `ros2 topic list` / `ros2 service list` hang indefinitely

**Symptom:** Running `ros2 topic list`, `ros2 service list`, or `ros2 topic echo <topic>` in a terminal just hangs with no output.

**Cause:** The ROS2 CLI daemon (`ros2daemon`) is not running. All `ros2` CLI commands
that do DDS discovery silently wait for the daemon socket, which never responds.

**Fix:** Start the daemon once per WSL2 session:
```bash
ros2 daemon start
```
The `ros2 launch robot_gazebo gazebo.launch.py` command also starts the daemon automatically.
After starting the daemon, all `ros2` CLI commands work normally.

### 5. `/spawn_entity` service not available — robot never spawns

**Error:** `Service /spawn_entity unavailable. Was Gazebo started with GazeboRosFactory?`

**Root cause (A):** `ExecuteProcess(['gazebo', ...])` does not inherit `GAZEBO_PLUGIN_PATH`,
so `libgazebo_ros_factory.so` is invisible to Gazebo even when passed via `-s`.

**Fix (A):** Use `IncludeLaunchDescription` pointing to `gazebo_ros/launch/gazebo.launch.py`.
That launch file sets `GAZEBO_PLUGIN_PATH` via `GazeboRosPaths.get_paths()` before starting
gzserver.

**Root cause (B):** On WSL2, gzserver takes longer than 30 seconds to register the
`/spawn_entity` service. `spawn_entity.py` has a hardcoded 30 s timeout.

**Fix (B):** Replace the `TimerAction` with a polling bash loop:
```bash
until ros2 service list | grep -q /spawn_entity; do sleep 2; done && ros2 run gazebo_ros spawn_entity.py ...
```

**Manual fallback** (always works): while Gazebo is running, in a second terminal:
```bash
source /opt/ros/humble/setup.bash && source ~/amr_ws/install/setup.bash
ros2 run gazebo_ros spawn_entity.py -topic robot_description -entity amr_robot -x 0 -y 0 -z 0.05 -Y 0
```

### Phase 2 — Odometry Verification

Run these in **three separate terminals** (all with ROS2 + workspace sourced and daemon started).

**Terminal 1 — Gazebo simulation (if not already running):**
```bash
ros2 launch robot_gazebo gazebo.launch.py
```

**Terminal 2 — RViz connected to simulation:**
```bash
ros2 launch robot_description sim_display.launch.py
```
RViz will show:
- Robot model in the `odom` frame
- TF tree (all frames: odom → base_footprint → base_link → sensors)
- Red dots: LiDAR scan (`/scan`)
- Purple arrow trail: wheel odometry path (`/odom`)

**Terminal 3 — Teleop:**
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```
Drive the robot and watch the purple odometry arrows accumulate in RViz.
Over time the path will drift from the robot's true position — this is
expected and motivates Phase 3 (EKF sensor fusion).

**Verify topics are publishing (after spawn):**
```bash
ros2 topic list | grep -E "odom|scan|imu|cmd_vel|camera"
ros2 topic hz /odom      # expect ~10 Hz
ros2 topic hz /scan      # expect ~10 Hz
```

**Verify TF tree is complete:**
```bash
cd ~/amr_ws
ros2 run tf2_tools view_frames
# Saves frames_TIMESTAMP.pdf (and .gv) in the current directory
cp $(ls -t frames_*.pdf | head -1) docs/tf_tree_phase2.pdf
rm -f frames_*.pdf frames_*.gv   # clean up timestamped files
```

**Expected TF chain:**
```
odom
  └── base_footprint        ← published by diff_drive plugin
        └── base_link       ← published by robot_state_publisher
              ├── left_wheel
              ├── right_wheel
              ├── caster_wheel
              ├── caster_wheel_rear
              ├── lidar_link
              ├── imu_link
              ├── camera_link
              └── camera_optical_link
```

### Phase 3 — EKF Sensor Fusion

**Install dependency (once):**
```bash
sudo apt install ros-humble-robot-localization
```

**Run order — four terminals** (all sourced + daemon started):

**Terminal 1 — Gazebo:**
```bash
ros2 launch robot_gazebo gazebo.launch.py
```
Wait for: `[python3-4] Spawn result: SpawnEntity: Successfully spawned entity [amr_robot]`

**Terminal 2 — EKF node:**
```bash
ros2 launch robot_localization_cfg ekf.launch.py
```
Wait for: `[ekf_filter_node]: Estimator initialized`  
The EKF reads `/odom` (10 Hz) + `/imu` (100 Hz) and publishes `/odometry/filtered` at 30 Hz.

**Terminal 3 — RViz:**
```bash
ros2 launch robot_description sim_display.launch.py
```
You will see:
- **Orange arrows** = raw `/odom` (noisy, 10 Hz)
- **Green arrows** = `/odometry/filtered` (smooth, 30 Hz, EKF fused)

**Terminal 4 — Teleop:**
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

**Verify topics and rates:**
```bash
ros2 topic list | grep -E "odom|imu"
ros2 topic hz /odom                  # nominal 10 Hz (WSL2 sim may show ~50 Hz wall-clock)
ros2 topic hz /imu                   # nominal 100 Hz (WSL2 may show ~50 Hz)
ros2 topic hz /odometry/filtered     # nominal 15 Hz (WSL2 may show ~5 Hz — EKF uses sim time)
```
> **WSL2 note:** Gazebo Classic runs below real-time on WSL2, so wall-clock rates
> differ from sim-time rates. The EKF uses `/clock` (sim time) so `/odometry/filtered`
> appears slower in wall time but is correct in simulation time.

**What to observe:**
1. Drive the robot in a straight line — green trail is smoother than orange
2. Spin the robot in place — green (IMU at 100 Hz) tracks rotation more tightly
3. Drive in a loop — green trail has less angular drift than orange

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
