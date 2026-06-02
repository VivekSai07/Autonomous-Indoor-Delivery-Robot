# Project TODO

## Current Phase: Phase 2 — Odometry 🔧

---

## Project Status

- [x] **Phase 0**: Project bootstrap — workspace, git, README, TODO
- [x] **Phase 1**: Robot Description — URDF/Xacro, Gazebo spawn, RViz display ✅
- [ ] **Phase 2**: Odometry — verify `/odom`, TF tree, teleop drift
- [ ] **Phase 3**: Sensor Fusion — EKF (wheel odom + IMU) → `/odometry/filtered`
- [ ] **Phase 4**: SLAM — SLAM Toolbox mapping → `office_map.yaml`
- [ ] **Phase 5**: Localization — AMCL on saved map, particle convergence
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
- [ ] Create `robot_localization_cfg` package
- [ ] Configure EKF: fuse `/odom` + `/imu`
- [ ] Verify `/odometry/filtered` is smoother
- [ ] Update README with `ekf.launch.py` command

### Phase 4 — SLAM
**Branch**: `phase-4/slam`
- [ ] Create `robot_slam` package
- [ ] Configure SLAM Toolbox (async online)
- [ ] Map the simulated environment via teleop
- [ ] Save map to `maps/office_map.yaml` + `maps/office_map.pgm`

### Phase 5 — Localization
**Branch**: `phase-5/localization`
- [ ] Add `localization.launch.py` to `robot_slam`
- [ ] Configure AMCL params
- [ ] Verify particle convergence in RViz
- [ ] Test recovery from delocalization

### Phase 6 — Nav2 Navigation
**Branch**: `phase-6/navigation`
- [ ] Create `robot_nav2` package
- [ ] Configure Nav2 params (planner, controller, costmaps, BT)
- [ ] `navigation.launch.py` (nav2 + amcl + map server)
- [ ] Verify: click `2D Nav Goal` → robot reaches goal
- [ ] Add architecture diagram to `docs/`

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
