# Project Rules — Autonomous Indoor Delivery Robot

## Source of Truth
- `TODO.md` — phase status and task checklist. Update at the start and end of every phase.
- `README.md` — always accurate enough for a stranger to run the project. Update whenever a new launch file, command, or parameter is added.
- `ONBOARDING.md` — teammate onboarding guide. Keep Team Tips and Skills sections current.
- `docs/project_plan.md` — reference only. **Never modify.**

## Commit Rules
1. Write a brief, descriptive commit message covering what was included, changed, created, or improved. Format: `phase-N: short description`.
2. Always run `colcon build --symlink-install` on all affected packages before committing. Never commit a broken build.
3. One concern per commit. If a prior-phase bug is found and fixed, it gets its own commit — do not bundle it with current phase work.

## Phase Completion Rules
4. Before marking a phase done, run rigorous tests:
   - Verify the current phase deliverable works as specified in `project_plan.md`.
   - Verify nothing is broken from all previous phases (topics publishing, TF tree intact, EKF running, builds clean).
   - Run `colcon build --symlink-install` from workspace root.
5. After a phase is complete, provide the user with:
   - The exact commands to run (with terminal labels if multi-terminal).
   - The expected output / behavior to observe at each step.
   - Any WSL2-specific pre-flight steps (`export DISPLAY`, `ros2 daemon start`).
   The user verifies independently before the phase is considered merged.

## WSL2 Pre-flight (every test session)
6. Before any test that involves Gazebo, RViz, or `ros2` CLI commands:
   - Confirm `echo $DISPLAY` returns a value (e.g. `:0`). If not, set it.
   - Run `ros2 daemon start` (or confirm it's already running).
   - Include these steps in every verification command block given to the user.

## Map Files
7. `maps/*.pgm` is git-ignored (binary). After the user saves and verifies a map, remind them to explicitly commit both `maps/office_map.yaml` and `maps/office_map.pgm` together.

## Docs Hygiene
8. Time-to-time (at minimum: at phase start, at phase end, and after any breaking change), review and update:
   - `README.md` — launch commands, topic tables, known issues
   - `TODO.md` — current phase, checked-off tasks, known issues
   - `ONBOARDING.md` — team tips, skills list
