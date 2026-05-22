# Problem 1 — Classical PDDL (IMV)

Interplanetary Museum Vault (IMV), single robotic curator, capacity 1. Minimal model for the assignment’s Problem 2.1.1.

## What’s done

- **Domain:** `domain.pddl` (domain name `imv`)
  - **Types:** `location`, `artifact`, `robot`
  - **Predicates:** `robot_at`, `artifact_at`, `robot_carrying`, `empty`, `connected`
  - **Actions:** `move`, `load`, `unload` (naming aligned with Problem 2)
  - **Requirements:** `:strips :typing` (no conditional effects, no sealing)
- **Problem:** `problem.pddl` (problem name `imv-p01`)
  - **Locations:** entrance, tunnel, hallA, hallB, cryo, pod1, pod2, stasis (tunnel as hub; connectivity matches the map)
  - **Artifacts:** a1, a2 (Hall A → cryo), b1, b2 (Hall B → pods), cs1, cs2 (cryo → stasis)
  - **Robot:** one curator `r1`, capacity 1 (must be `empty` to load)
  - **Goal:** a1,a2 in cryo; b1 in pod1, b2 in pod2; cs1,cs2 in stasis

## Design choices (minimal P1)

- No sealing in the maintenance tunnel (deferred to later problems).
- No tunnel segments; single `tunnel` location.
- No explicit cooling; Cryo-Chamber preserves artifacts by location.
- Hall B artifacts: goal is “in pod” (not “in stasis after pod” for P1).

## Running planners

From the project root (e.g. inside planutils Docker):

```bash
ff problem1/domain.pddl problem1/problem.pddl
downward --alias lama-first problem1/domain.pddl problem1/problem.pddl
```

Plan output can be saved in `problem1/results/` (e.g. `ff.plan`, `lama.plan`).

## Files

| File            | Description                    |
|-----------------|--------------------------------|
| `domain.pddl`   | PDDL domain                    |
| `problem.pddl`  | PDDL problem (single curator)  |
| `results/`      | Planner output plans (optional)|
