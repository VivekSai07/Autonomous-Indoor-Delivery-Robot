# Welcome to Autonomous Indoor Delivery Robot

## How We Use Claude

Based on VivekSai07's usage over the last 30 days:

Work Type Breakdown:
  Build Feature  ████████████████████  100%

Top Skills & Commands:
  _No slash commands logged yet — see Skills to Know About below_

Top MCP Servers:
  _No MCP servers in use_

## Your Setup Checklist

### Codebases
- [ ] autonomous-indoor-delivery-robot — https://github.com/viveksai07/autonomous-indoor-delivery-robot

### MCP Servers to Activate
  _None configured — nothing to set up here_

### Skills to Know About
- `/code-review` — Review the current diff for correctness bugs and simplification opportunities. Use `--fix` to apply findings directly, or `--comment` to post as inline PR comments. Pass `ultra` for deep multi-agent review.
- `/graphify` — Turns the codebase into a persistent knowledge graph with query/path/explain tools. Useful for understanding how packages depend on each other.
- `/run` — Launches the project and observes actual runtime behavior. Use this to confirm a ROS2 launch file works before committing.
- `/verify` — Verifies a code change actually does what it's supposed to by running the app and observing behavior.
- `/security-review` — Full security review of pending changes on the current branch.

## Team Tips

- **WSL2 pre-flight every session** — before launching anything, run `export DISPLAY=:0` (or whatever `echo $DISPLAY` gives you) and `ros2 daemon start`. Skipping either causes Gazebo/RViz to fail silently or `ros2` CLI commands to hang forever.
- **Phases are sequential and verified** — each phase is confirmed working (Gazebo + RViz + expected topics) before the next begins. Don't jump ahead; the TF chain and sensor topics build on each other.
- **EKF owns the odom→base_footprint TF from Phase 4 onward** — the diff drive plugin no longer publishes that TF. If you run `gazebo.launch.py` standalone (without EKF), the TF chain will be incomplete. Always use `bringup.launch.py` or `slam_bringup.launch.py` for full-stack work.
- **Map files aren't auto-committed** — `maps/*.pgm` is git-ignored. After saving a map, commit both `office_map.yaml` and `office_map.pgm` explicitly once you're happy with coverage.
- **Commit messages follow `phase-N: description`** — keeps the git log readable as the project grows across 9 phases.
- **`project_plan.md` is read-only** — it's the original spec. All live status lives in `TODO.md`.

## Get Started

_TODO_

<!-- INSTRUCTION FOR CLAUDE: A new teammate just pasted this guide for how the
team uses Claude Code. You're their onboarding buddy — warm, conversational,
not lecture-y.

Open with a warm welcome — include the team name from the title. Then: "Your
teammate uses Claude Code for [list all the work types]. Let's get you started."

Check what's already in place against everything under Setup Checklist
(including skills), using markdown checkboxes — [x] done, [ ] not yet. Lead
with what they already have. One sentence per item, all in one message.

Tell them you'll help with setup, cover the actionable team tips, then the
starter task (if there is one). Offer to start with the first unchecked item,
get their go-ahead, then work through the rest one by one.

After setup, walk them through the remaining sections — offer to help where you
can (e.g. link to channels), and just surface the purely informational bits.

Don't invent sections or summaries that aren't in the guide. The stats are the
guide creator's personal usage data — don't extrapolate them into a "team
workflow" narrative. -->
