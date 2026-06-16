# Project TODO

## Current Phase: Phase 6 — Navigation 🔧

---

## Project Status

- [x] **Phase 0**: Project bootstrap — workspace, git, README, TODO
- [x] **Phase 1**: Robot Description — URDF/Xacro, Gazebo spawn, RViz display ✅
- [x] **Phase 2**: Odometry — verify `/odom`, TF tree, teleop drift ✅
- [x] **Phase 3**: Sensor Fusion — EKF fuses `/odom`+`/imu` → `/odometry/filtered` ✅
- [x] **Phase 4**: SLAM — SLAM Toolbox mapping → `office_map.yaml` ✅
- [x] **Phase 5**: Localization — AMCL on saved map, particle convergence ✅
- [ ] **Phase 6**: Nav2 Navigation — planner + controller + costmaps, click-to-navigate
- [ ] **Phase 7**: Dynamic Obstacles — Gazebo actor, Nav2 replanning
- [ ] **Phase 8**: Multi-Goal Mission — 5-waypoint autonomous mission loop
- [ ] **Phase 9**: Docking — AprilTag detection + PID approach controller

---

## Phase Details

### Phase 1 — Robot Description
**Branch**: `phase-1/robot-description`
- [x] Create `robot_description` package (URDF/Xacro)
  - [x] Chassis, wheels, caster
  - [x] LiDAR link + Gazebo plugin
  - [x] IMU link + Gazebo plugin
  - [x] Camera link + Gazebo plugin (for Phase 9)
  - [x] Differential drive plugin
- [x] Create `robot_gazebo` package
  - [x] Office world SDF
  - [x] Spawn launch file
- [x] RViz config + display launch
- [x] `colcon build` — both packages build clean
- [x] URDF parses correctly (10 links, 9 joints — added rear caster for stability)
- [x] **Verified**: robot visible in RViz ✅
- [x] **Verified**: robot spawns in Gazebo, stable, all sensor topics active ✅
  - `/odom`, `/scan`, `/imu`, `/camera/image_raw`, `/cmd_vel` all confirmed
  - Diff drive, camera, LiDAR, IMU plugins all running

### Phase 2 — Odometry
**Branch**: `phase-2/odometry`
- [x] Fix single-launch spawn — Python rclpy spawner, no ros2 CLI daemon needed
- [x] Fix ros2 topic/service CLI hang — daemon auto-started in launch
- [x] `sim.rviz` config (Fixed Frame = odom, shows TF + LaserScan + Odometry arrow)
- [x] `sim_display.launch.py` — RViz for use alongside running simulation
- [ ] **Verify**: `/odom` topic publishing `nav_msgs/Odometry` with correct data
- [ ] **Verify**: TF tree complete (`odom → base_footprint → base_link → all sensors`)
- [ ] **Verify**: Robot moves in RViz as you teleoperate
- [ ] **Verify**: Drift accumulates over time (expected — no fusion yet)
- [ ] Save TF tree diagram → `docs/tf_tree_phase2.pdf` (run while sim is active)

### Phase 3 — Sensor Fusion
**Branch**: `phase-3/sensor-fusion`
- [x] Install `ros-humble-robot-localization`
- [x] Create `robot_localization_cfg` package
- [x] Configure EKF — fuse `/odom` (10 Hz, abs x/y/yaw + vx) + `/imu` (100 Hz, angular vel + accel)
- [x] `ekf.launch.py` — starts EKF node with sim time
- [x] `publish_odom_tf: false` in URDF — EKF owns `odom → base_footprint` TF
- [x] `sim.rviz` updated — shows raw `/odom` (orange) vs `/odometry/filtered` (green)
- [x] **Verified**: `/odometry/filtered` publishing (WSL2 sim runs below real-time; actual rates: /odom ~50 Hz, /imu ~50 Hz, /filtered ~5 Hz — all functional)
- [x] **Verified**: EKF TF visible in RViz (`odom → base_footprint` from EKF)
- [x] **Verified**: Green (filtered) trail smoother than orange (raw) during teleop ✅

### Phase 4 — SLAM
**Branch**: `phase-4/slam`
- [x] Create `robot_slam` package
- [x] Configure SLAM Toolbox (async online, `mapper_params_online_async.yaml`)
- [x] Switch TF ownership: EKF now publishes `odom→base_footprint` (URDF `publish_odom_tf: false`)
- [x] `slam.launch.py` — standalone SLAM Toolbox node
- [x] `slam_bringup.launch.py` — full stack (Gazebo + EKF + SLAM + RViz)
- [x] `slam.rviz` — fixed frame `map`, shows /map occupancy grid + LaserScan
- [x] Install `ros-humble-slam-toolbox`
- [x] Build and verify: all 4 packages clean
- [x] Map the simulated environment via teleop
- [x] Save map: `ros2 run nav2_map_server map_saver_cli -f ~/amr_ws/maps/office_map`
- [x] **Verified**: `map→odom` at 10 Hz (SLAM Toolbox), `odom→base_footprint` at 10 Hz (EKF) ✅
- [x] **Verified**: Full TF chain `map→odom→base_footprint→base_link→sensors` confirmed ✅
- [x] TF tree saved to `docs/tf_tree_phase4.gv`

### Phase 5 — Localization
**Branch**: `phase-5/localization`
- [x] Add `amcl_params.yaml` — likelihood_field model, 500–2000 particles, diff drive motion model
- [x] Add `localization.launch.py` — map_server + amcl + lifecycle_manager
- [x] Add `localization_bringup.launch.py` — full stack (Gazebo + EKF + localization + RViz)
- [x] Add `localization.rviz` — map, particle cloud (/particle_cloud), AMCL pose, laser, 2D Pose Estimate tool
- [x] Install dependencies: `ros-humble-nav2-amcl`, `ros-humble-nav2-lifecycle-manager`, `ros-humble-nav2-rviz-plugins`
- [x] Build clean, set initial pose, particle cloud converges, delocalization recovery verified ✅
- [x] **Verified**: `nav2_rviz_plugins/ParticleCloud` fix — `nav2_msgs/ParticleCloud` type mismatch resolved ✅

### Phase 6 — Nav2 Navigation
**Branch**: `phase-6/navigation`
- [x] Create `robot_nav2` package
- [x] `nav2_params.yaml` — NavfnPlanner, DWBLocalPlanner, global/local costmaps tuned for 0.3×0.25 m robot
- [x] `navigation.launch.py` — map_server + AMCL + bt_navigator + planner + controller + behaviors + velocity_smoother + waypoint_follower + lifecycle_manager
- [x] `navigation_bringup.launch.py` — full stack (Gazebo + EKF + navigation.launch.py + RViz)
- [x] `navigation.rviz` — map, global/local costmaps, global path, local plan, footprint, 2D Nav Goal tool
- [ ] Install: `sudo apt install ros-humble-navigation2 ros-humble-nav2-bringup`
- [ ] Build: `colcon build --symlink-install`
- [ ] Launch and send `2D Nav Goal` → robot plans and drives to goal
- [ ] Verify global path (blue) and local plan (green) appear in RViz
- [ ] Verify robot stops cleanly at goal
- [ ] **Verified**: click goal → robot reaches it autonomously ✅

### Phase 7 — Dynamic Obstacles
**Branch**: `phase-7/dynamic-obstacles`
- [ ] Add Gazebo animated actor to world
- [ ] Verify Nav2 replans when actor blocks path
- [ ] Tune recovery behaviors if needed

### Phase 8 — Multi-Goal Mission
**Branch**: `phase-8/missions`
- [ ] Create `robot_missions` package
- [ ] Define 5 waypoints (Dock, Room A, Room B, Room C, Home)
- [ ] Implement `mission_executor.py` with `nav2_simple_commander`
- [ ] Verify full mission loop completes

### Phase 9 — Docking
**Branch**: `phase-9/docking`
- [ ] Create `robot_docking` package
- [ ] Add AprilTag to Gazebo charging station model
- [ ] Configure `apriltag_ros` detection
- [ ] Implement PID docking controller
- [ ] Integrate with mission (final waypoint triggers dock)
- [ ] Verify autonomous docking

---

## Known Issues

- **WSL2 / Gazebo spawn timing**: On WSL2, gzserver takes longer to register `/spawn_entity`
  than the default 30s timeout. The launch file uses a polling loop to handle this.
  If auto-spawn still fails, run manually in a second terminal:
  ```bash
  source /opt/ros/humble/setup.bash && source ~/amr_ws/install/setup.bash
  ros2 run gazebo_ros spawn_entity.py -topic robot_description -entity amr_robot -x 0 -y 0 -z 0.05 -Y 0
  ```

## Notes

- Map files (`*.pgm`) are git-ignored; commit `office_map.yaml` + the pgm manually when finalized
- WSL2: always set `export DISPLAY=:0` before launching Gazebo or RViz
- Each phase merged to `main` only after deliverable is verified by the user
