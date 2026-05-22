# How To Run `problem5`

This guide is split into:

1. first-time setup
2. normal reopen
3. rebuild after code edits
4. seismic execution order

In this Docker setup, `/workspace` inside the container is the `problem5` folder itself.

## 1. First-time setup

From the `problem5` folder on your Mac:

```bash
docker rm -f ros2plansys 2>/dev/null || true

docker run -it --platform linux/amd64 \
  --name ros2plansys \
  -e ROS_LOCALHOST_ONLY=1 \
  -v "$(pwd):/workspace" \
  osrf/ros:humble-desktop-full-jammy \
  bash
```

Inside the container, run this only the first time for that container:

```bash
source /opt/ros/humble/setup.bash
apt update
apt install -y python3-colcon-common-extensions python3-rosdep git wget
rosdep init 2>/dev/null || true
rosdep update

mkdir -p /plansys2_ws/src
cd /plansys2_ws/src

if [ ! -d ros2_planning_system/.git ]; then
  rm -rf ros2_planning_system
  git clone -b humble-devel https://github.com/PlanSys2/ros2_planning_system.git
fi

rm -rf /plansys2_ws/src/imv_plansys2
cp -r /workspace /plansys2_ws/src/imv_plansys2

cd /plansys2_ws
rosdep install --from-paths src --ignore-src -r -y
apt install -y ros-humble-behaviortree-cpp-v3
colcon build --symlink-install --packages-up-to imv_plansys2
source /plansys2_ws/install/setup.bash
ros2 pkg list | grep imv_plansys2
```

If the last command prints `imv_plansys2`, the package is ready.

## 2. Normal reopen later

If the container still exists, you do not need to repeat `apt install`, `rosdep init`, or `rosdep update`.

Start the old container again:

```bash
docker start -ai ros2plansys
```

Then inside the container:

```bash
source /opt/ros/humble/setup.bash
source /plansys2_ws/install/setup.bash
ros2 launch imv_plansys2 imv_plansys2_launch.py
```

Leave that terminal open.

Open a second terminal on your Mac:

```bash
docker exec -it ros2plansys bash
```

Then inside:

```bash
source /opt/ros/humble/setup.bash
source /plansys2_ws/install/setup.bash
ros2 run plansys2_terminal plansys2_terminal
```

## 3. Rebuild after code edits

Only do this if you changed files in `problem5`.

```bash
docker exec -it ros2plansys bash
```

Then inside:

```bash
rm -rf /plansys2_ws/src/imv_plansys2
cp -r /workspace /plansys2_ws/src/imv_plansys2
cd /plansys2_ws
rm -rf build install log
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-up-to imv_plansys2
source /plansys2_ws/install/setup.bash
```

## 4. Load the runtime problem

In `plansys2_terminal`, type the lines from `launch/imv_commands.txt` one by one.

## 5. Seismic execution order

`launch/imv_commands.txt` now contains:

- the initial problem setup
- Phase 1
- Phase 2
- Phase 3a
- Phase 3b
- Phase 3c
- Phase 3d (full final goal)

Run that file top to bottom in the same `plansys2_terminal` session. The staged cumulative goals at the end of the file are the reliable way to complete the seismic mission.

Use the same running `plansys2_terminal` session for all phases. If `plansys2_terminal` crashes but the launch terminal is still alive, open a new `plansys2_terminal` and continue from the current state.

## 6. Notes

- `get plan` should print a valid plan
- after `run`, `plansys2_terminal` may look idle while execution continues
- the action logs usually appear in the launch terminal
- the full tested workflow is already written inside `launch/imv_commands.txt`

## 7. Stop the container

```bash
docker stop ros2plansys
```

