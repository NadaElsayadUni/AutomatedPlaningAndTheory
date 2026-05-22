# Problem 5 — PlanSys2 (ROS 2)

## After `colcon build` succeeds — run **IMV** (your domain)

This package follows the same runtime pattern as the lab example:

- **`pddl/domain.pddl`** is loaded by PlanSys2 at launch time
- **`launch/imv_commands.txt`** provides the problem instances, predicates, and goal at runtime in `plansys2_terminal`

1. Put this package in your workspace as **`imv_plansys2`**: e.g. `cp -r problem5 /plansys2_ws/src/imv_plansys2`, or symlink it there.
2. Build the package and its workspace dependencies: `cd /plansys2_ws && colcon build --packages-up-to imv_plansys2`
3. **Every new shell:**  
   `source /opt/ros/humble/setup.bash`  
   `source /plansys2_ws/install/setup.bash`
4. **Terminal 1:**  
   `ros2 launch imv_plansys2 imv_plansys2_launch.py`
5. **Terminal 2:**  
   `ros2 run plansys2_terminal plansys2_terminal`
6. In `plansys2_terminal`, type **one line, Enter, wait for `>`**. For this setup, first load the runtime problem using **`launch/imv_commands.txt`**.

PlanSys2 loads **`pddl/domain.pddl`** from the package. In `plansys2_terminal`, enter the lines from **`launch/imv_commands.txt`** one by one to create the runtime problem and then run the tested cumulative seismic sequence already included at the bottom of that same file.

This staged sequence in **`launch/imv_commands.txt`** is the reliable way to complete the full seismic mission in PlanSys2. After editing on the host:  
`cp -r /workspace/problem5 /plansys2_ws/src/imv_plansys2`, then `colcon build --packages-up-to imv_plansys2`.

The seismic PlanSys2 package runs executors for:

- `move`
- `move_into_tunnel_from_site`
- `move_into_tunnel_from_beta`
- `move_out_of_tunnel_to_site`
- `move_out_of_tunnel_to_beta`
- `activate_sealing_site`
- `activate_sealing_beta`
- `deactivate_sealing_site`
- `deactivate_sealing_beta`
- `load_site`
- `load_beta`
- `unload_site`
- `unload_beta`

These names match the split Hall beta / other-site actions from the seismic temporal domain.

---

You do **not** “download ROS 2 and PlanSys2” as a single installer. You install **ROS 2** for your OS, then build **PlanSys2** from source on top of it.

## If you are on **macOS** (typical for your machine)

ROS 2 + PlanSys2 are **maintained for Linux**. On Mac, the practical options are:

1. **Ubuntu VM** (recommended): e.g. **Ubuntu 22.04** in **UTM**, **Parallels**, or **VMware**, then follow the **Ubuntu** steps below inside the VM.
2. **Docker**: run a ROS 2 container with GUI/network setup (more work for `plansys2_terminal` and multi-node launch). VM is usually simpler for coursework.
3. **Native macOS**: possible for some ROS 2 releases but **not** officially tier‑1; PlanSys2 may not have macOS binaries. Prefer a VM.

## Docker Desktop (Mac or Windows)

Your **`AP_PROJECT_NADA/Dockerfile`** (`myplanutils`) is for **planutils** (VAL, OPTIC, …) — it does **not** include ROS 2. For PlanSys2 you run a **ROS 2 image**, then build PlanSys2 inside the container (first time ~10–20+ minutes).

### 1. One-off container (two terminals: launch + `plansys2_terminal`)

Use a **named** container (no `--rm`) so a second terminal can `docker exec` into it.

**Terminal A — start container** (from the folder you want mounted, e.g. `AP_PROJECT_NADA`). **Apple Silicon:** add `--platform linux/amd64` to both `docker pull` and `docker run` (see **§2** below).

```bash
docker pull osrf/ros:humble-desktop-full-jammy

docker run -it \
  --name ros2plansys \
  -e ROS_LOCALHOST_ONLY=1 \
  -v "$(pwd):/workspace" \
  osrf/ros:humble-desktop-full-jammy \
  bash
```

Run that `docker run` after `cd` to `AP_PROJECT_NADA` so `/workspace/problem5` is your package.

Inside the container, once per “fresh” container:

```bash
source /opt/ros/humble/setup.bash
apt update && apt install -y python3-colcon-common-extensions python3-rosdep git wget
rosdep init 2>/dev/null || true
rosdep update

mkdir -p /plansys2_ws/src
cd /plansys2_ws/src
git clone -b humble-devel https://github.com/PlanSys2/ros2_planning_system.git
# optional: symlink your package
# ln -s /workspace/problem5 /plansys2_ws/src/imv_plansys2

cd /plansys2_ws
rosdep install --from-paths src --ignore-src -r -y
apt install -y ros-humble-behaviortree-cpp-v3
colcon build --symlink-install
source /plansys2_ws/install/setup.bash
```

Leave this shell open, or **detach** with `Ctrl+p Ctrl+q` (if you used `-dit`) so the container keeps running.

**Terminal B — second shell in the same container**

```bash
docker exec -it ros2plansys bash
source /opt/ros/humble/setup.bash
source /plansys2_ws/install/setup.bash
ros2 pkg list | grep plansys2
```

Use **Terminal A** for `ros2 launch …` and **Terminal B** for `ros2 run plansys2_terminal plansys2_terminal` (or both in one terminal with `tmux`).

**Stop / remove when done**

```bash
docker stop ros2plansys
docker rm ros2plansys
```

### 2. Apple Silicon (M1 / M2 / M3) — `no matching manifest for linux/arm64`

Official `osrf/ros:…` images are often **amd64-only**. On ARM Macs, **pull and run with x86_64 emulation**:

```bash
docker pull --platform linux/amd64 osrf/ros:humble-desktop-full-jammy

docker run -it --platform linux/amd64 \
  --name ros2plansys \
  -e ROS_LOCALHOST_ONLY=1 \
  -v "$(pwd):/workspace" \
  osrf/ros:humble-desktop-full-jammy \
  bash
```

Docker Desktop → **Settings → General**: enable **Rosetta** / **x86/amd64 emulation** if Docker suggests it. Builds will be **slower** than on native Linux.

### 3. Docker Desktop settings

- **Resources**: give the VM enough **RAM** (e.g. 8 GB+) for `colcon build`.
- **File sharing**: the path in `-v "HOST:CONTAINER"` must be under a directory Docker Desktop allows (usually your home folder is fine).

### 4. Limitations on Mac

- All ROS nodes run **inside Linux** in the VM; that’s fine for coursework.
- **`ROS_LOCALHOST_ONLY=1`** avoids many DDS discovery issues when everything is in **one** container.
- **GUI tools** (RViz, etc.) need extra setup on Mac (XQuartz + `DISPLAY`, or skip GUI and use terminal only).

### 5. Not the same as `myplanutils`

| Image            | Use                                      |
| ---------------- | ---------------------------------------- |
| `myplanutils`    | PDDL planners (VAL, OPTIC, FF, …)        |
| `osrf/ros:…`     | ROS 2 + then PlanSys2 built inside       |

You can keep **both**: one container for planning assignments, another for Problem 5.

---

## 1. Install ROS 2 (Ubuntu)

Pick a **pair** that matches PlanSys2 docs (check [ros2_planning_system](https://github.com/PlanSys2/ros2_planning_system) README for supported distros). Common choice:


| Ubuntu | ROS 2      |
| ------ | ---------- |
| 22.04  | **Humble** |
| 24.04  | **Jazzy**  |


Official install (binary): **[https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debians.html](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debians.html)** (replace `humble` with your distro in the URL if you use Jazzy).

After install, every new terminal:

```bash
source /opt/ros/humble/setup.bash   # or jazzy
```

Install build tools:

```bash
sudo apt update
sudo apt install python3-colcon-common-extensions python3-rosdep git
sudo rosdep init   # once, if never done
rosdep update
```

## 2. Install PlanSys2 (from source)

Create a workspace and clone PlanSys2:

```bash
mkdir -p ~/plansys2_ws/src
cd ~/plansys2_ws/src
# Branch must match ROS 2: Humble → humble-devel, Jazzy → jazzy-devel (default branch ≠ Humble)
git clone -b humble-devel https://github.com/PlanSys2/ros2_planning_system.git
```

Install dependencies and build:

```bash
cd ~/plansys2_ws
rosdep install --from-paths src --ignore-src -r -y
sudo apt install -y ros-humble-behaviortree-cpp-v3
source /opt/ros/humble/setup.bash
colcon build --symlink-install
```

**Build error `rclcpp::experimental::executors` / `EventsExecutor`:** you cloned the wrong branch for Humble. Fix:

```bash
cd ~/plansys2_ws/src/ros2_planning_system && git fetch origin && git checkout humble-devel
cd ~/plansys2_ws && rm -rf build install log
source /opt/ros/humble/setup.bash && colcon build --symlink-install
```

**Build error `Could not find behaviortree_cpp_v3`:** `rosdep` pulled **BT4** (`ros-humble-behaviortree-cpp`). **PlanSys2 `humble-devel`** still needs **BT3**:

```bash
apt-get update && apt-get install -y ros-humble-behaviortree-cpp-v3
cd ~/plansys2_ws && rm -rf build install log
source /opt/ros/humble/setup.bash && colcon build --symlink-install
```

If `ros-humble-behaviortree-cpp-v3` is not found, run `apt-cache search behaviortree | grep humble` on your system.

If `rosdep` misses packages, see the PlanSys2 repo README for extra `apt` lines.

Source the overlay:

```bash
source ~/plansys2_ws/install/setup.bash
```

## 3. Add this package (`problem5`)

Put this folder under the **same** workspace `src/` (or a second overlay workspace):

```bash
# example: you keep AP_PROJECT_NADA on the VM’s disk
ln -s /path/to/AP_PROJECT_NADA/problem5 ~/plansys2_ws/src/imv_plansys2
# or copy the folder into src/ with that name
```

Then:

```bash
cd ~/plansys2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash   # if PlanSys2 already built
rosdep install --from-paths src --ignore-src -r -y
colcon build --packages-up-to imv_plansys2
source install/setup.bash
```

## 4. References

- PlanSys2 tutorials: **[https://plansys2.github.io/tutorials/](https://plansys2.github.io/tutorials/)**

## 5. Quick check

With PlanSys2 built and sourced:

```bash
ros2 pkg list | grep plansys2
```

You should see packages like `plansys2_bringup`, `plansys2_terminal`, etc.