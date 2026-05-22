# Problem 2 — Capacity and Multi-Agent (IMV)

Extends the IMV scenario with robot capacity (slots) and optional second agent (drone). Aligns with the assignment’s Problem 2.1.2.

## What’s done

### Domain (capacity and multi-agent)

- **`domain.pddl`** (domain name `imv`)
  - **Types:** `location`, `artifact`, `robot`, `slot`
  - **Predicates:** `at ?r ?l`, `artifact_at`, `slot_free ?r ?s`, `in_slot ?a ?r ?s`, `robot_slot ?r ?s`, `connected`
  - **Actions:** `move(?r ?from ?to)`, `load(?r ?a ?l ?s)`, `unload(?r ?a ?l ?s)` — slot-based load/unload; each robot has its own slots via `robot_slot`
  - One robot can have multiple slots (e.g. curator: 2, drone: 1); capacity is fixed in the problem by how many slots each robot has.

### Problem files

| File | Description |
|------|-------------|
| **`problem.pddl`** | Single curator `r1`, capacity 2 (slot1, slot2). Same goal as P1. Uses `domain.pddl`. |
| **`problem-curator-drone.pddl`** | Curator `r1` (2 slots: slot1, slot2) and drone `d1` (1 slot: slot_d). Both can move/load/unload any artifact. Uses `domain.pddl`. |
| **`problem-curator-drone-assigned.pddl`** | Same two agents; **fixed assignment:** r1 handles a1, a2, b1, b2; d1 handles cs1, cs2. Uses `domain-assigned.pddl`. |

### Assigned domain (fixed division of labour)

- **`domain-assigned.pddl`** (domain name `imv-assigned`)
  - Same as `domain.pddl` plus predicate **`(handles ?r ?a)`**.
  - **load** and **unload** require `(handles ?r ?a)` so only the assigned robot can move that artifact.
  - Used only by `problem-curator-drone-assigned.pddl`.

## Design choices

- Sealing in the tunnel is not modelled (can be added later).
- Connectivity: same as P1 (entrance ↔ tunnel ↔ cryo, pod1, pod2, hallA, hallB, stasis).
- In the unassigned curator–drone problem, the planner may use only one agent if that yields a shorter plan; the assigned problem forces both r1 and d1 to be used.

## Running planners

From the project root (e.g. inside planutils Docker):

```bash
# Single curator (capacity 2)
ff problem2/domain.pddl problem2/problem.pddl

# Curator + drone (any agent can handle any artifact)
ff problem2/domain.pddl problem2/problem-curator-drone.pddl

# Curator + drone with fixed assignment (r1 → a1,a2,b1,b2; d1 → cs1,cs2)
ff problem2/domain-assigned.pddl problem2/problem-curator-drone-assigned.pddl
```

Replace `ff` with `downward --alias lama-first` (or other planner) as needed. Save plans in `problem2/results/` if desired.

## Files overview

| File | Purpose |
|------|--------|
| `domain.pddl` | Main domain (capacity + multi-agent, no assignment) |
| `domain-assigned.pddl` | Domain with `handles` for fixed artifact–robot assignment |
| `problem.pddl` | One curator, two slots |
| `problem-curator-drone.pddl` | Curator + drone, no assignment |
| `problem-curator-drone-assigned.pddl` | Curator + drone, r1 = a1,a2,b1,b2; d1 = cs1,cs2 |
| `results/` | Planner output plans (e.g. `ff.plan`, `lama.plan`, `*curator-drone*.plan`) |
