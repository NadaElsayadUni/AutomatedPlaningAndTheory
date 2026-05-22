# Problem 4 — Temporal IMV (durative actions)

Same scenario and goal as Problem 2 (§2.1.2 / §2.1.4): single curator with two slots, or use `problem-curator-drone.pddl` for two robots and possible **parallel** `move` between agents.

## Domain (`domain.pddl`)

- **Requirements:** `:strips :typing :durative-actions :equality`. Durative **conditions** use only **positive** literals so **OPTIC** does not treat the domain as unsupported ADL (`(non_tunnel ?l)` for every location except `tunnel`; `(sealing_off ?u)` / `(sealing_on ?u)` instead of `(not (sealing_on ?u))` in conditions).
- **Maintenance tunnel:** `(tunnel tunnel)` in problems; **`(non_tunnel …)`** for `entrance`, halls, cryo, pods, stasis. Vault object `vs - vunit`; tunnel moves require `(sealing_on vs)`.
- **Moves:**
  - `move` (duration **2**): between two **non-tunnel** locations only.
  - `move_into_tunnel` (duration **3**): `?to` is tunnel, `?from` is not; requires `(sealing_on ?u)` at start.
  - `move_out_of_tunnel` (duration **3**): `?from` is tunnel, `?to` is not; requires `(sealing_on ?u)` at start.
- **Sealing (durative, duration **1**):**
  - `activate_sealing ?r ?l ?u`: same as before; sets `(sealing_on ?u)` at end (`?u` grounds to `vs`).
  - `deactivate_sealing ?r ?l ?u`: clears `(sealing_on ?u)` at end.
- **`manip_free`:** the robot may run **only one** durative action at a time: **move**, **move_into_tunnel**, **move_out_of_tunnel**, **load**, **unload**, **activate_sealing**, **deactivate_sealing** all require it at start and release it at end. So you get a serial schedule like: activate sealing → enter tunnel → exit to hall → deactivate sealing → load a1 → load a2 → activate sealing → … (exact order is still up to the planner as long as it’s legal).
- **`load` / `unload`:** duration **1**; require **`(non_tunnel ?l)`** and **`(sealing_off ?u)`** (parameter **`?u`** = `vs`). After **`move_out_of_tunnel`**, sealing is still **on** → the planner must run **`deactivate_sealing`** before any **load**/**unload** at that room. Before **`move_into_tunnel`**, run **`activate_sealing`** again.

## Problems

| File | Description |
|------|-------------|
| `problem.pddl` | `imv-p04` — `vs`, init `(sealing_off vs)`, `(tunnel tunnel)`, `(non_tunnel …)` on all non-tunnel locations. |
| `problem-curator-drone.pddl` | `imv-p04-curator-drone` — `r1` + `d1`; same `vs` (shared vault sealing state). |

Both use `(:metric minimize (total-time))` for makespan.

## Planner (planutils / Docker)

| Case | Use |
|------|-----|
| **`domain.pddl` / `problem.pddl`** (no TIL) | **TFD** or **OPTIC**. **POPF** if it runs; it sometimes **segfaults** on some setups. |
| **`domain-seismic` + TIL** | **OPTIC** (recommended). Seismic domain uses **split Hall β actions** (no **`imply`**) so TILs interact better with the planner. |

**OPTIC** rejects domains it treats as ADL; the base domain uses positive **`non_tunnel`** / **`sealing_off`** in conditions for that reason.

```bash
docker run -v "/path/to/AP_PROJECT_NADA:/computer" -it --privileged --rm myplanutils bash
cd /computer/problem4
planutils run popf domain.pddl problem.pddl
planutils run tfd domain.pddl problem.pddl
planutils run optic domain.pddl problem.pddl
```

### Validation

**1 — Domain + problem (parse / static check)** — no plan file:

```bash
cd /computer/problem4
planutils run val Validate domain.pddl problem.pddl
```

**2 — Domain + problem + temporal plan (execution check)** — checks durative preconditions, effects, mutexes, and **timed initial literals** against the schedule.

1. Save planner output as a **`.plan`** file: keep only lines like  
   `0.000: (action name ...)  [duration]`  
   (remove lines starting with `;`, search banners, and duplicate “second” plans if you only want one schedule).
2. Run:

```bash
cd /computer/problem4
planutils run val Validate domain.pddl problem.pddl results/your.plan
```

Same for seismic: `domain-seismic.pddl`, `problem-seismic.pddl`, and a **fresh** `.plan` from OPTIC (action names changed — old saved logs in `results/` are **not** valid).

**Verbose or `-t` (time tolerance):** `planutils run val Validate …` does not forward extra flags. Inside the container, call VAL directly (path may vary after `planutils install`):

```bash
/root/.planutils/packages/val/bin/Validate -v -t 0.01 domain-seismic.pddl problem-seismic.pddl results/your.plan
```

**`-v`** prints where the plan fails and repair hints (call the **Validate** binary directly; **`planutils run val Validate`** does not pass **`-v`**).

**VAL vs OPTIC timestamps:** At the same clock tick (often **t = 1**), VAL may apply **`move_into_tunnel_*` start** before **`activate_sealing_*` end**, so **`manip_free`** / **`sealing_on`** look false. **`scripts/respace_plan_val.py`** adds a small extra delay (**0.02** by default) after every **`activate_sealing_*` / `deactivate_sealing_*`** so the next step starts after end effects. Keep that delay **small** (do not use **1.0** s per step) or the whole schedule shifts and Hall β can cross a seismic TIL.

```bash
# keep a copy of the raw OPTIC lines first
cp results/my.plan results/my-raw.plan
python3 scripts/respace_plan_val.py results/my-raw.plan results/my-val.plan
```

Naming: **`optic-seismic-raw.plan`** = exact OPTIC lines; **`optic-seismic-val.plan`** = after **`respace_plan_val.py`** (for **Validate**). If you paste OPTIC into **`-val`**, run the script so **Validate** does not fail at **t = 1**.

**Validate** must use the **same** problem as the planner: plans with **`d1`** need **`problem-curator-drone-seismic.pddl`**, not **`problem-seismic.pddl`** (otherwise **`Object with unknown type: d1`**).

**Curator + drone — `*-val.plan`:** Use **`--parallel`** (same-timestamp grouping + post-activate bump + per-robot gaps + deactivate/activate overlap fixes):

```bash
python3 scripts/respace_plan_val.py --parallel results/optic-seismic-drone.plan results/optic-seismic-drone-val.plan
```

**Validate:** `problem-curator-drone-seismic.pddl` + `results/optic-seismic-drone-val.plan`. **Note:** Even after **`--parallel`**, **VAL** may still report **`Plan failed`** on the joint schedule (ordering of simultaneous events vs **end-timed** sealing effects). The **raw** drone OPTIC plan can fail **VAL** too. For the report, treat **OPTIC** as the source of truth for the parallel schedule; use **single-robot** + **`optic-seismic-val.plan`** when you need a **Plan valid** line from **VAL**.

**Seismic + VAL:** Any Hall β action must lie entirely inside a **safe** interval. **`respace_plan_val.py`** reduces false failures from VAL’s timestamp ordering.

**Why OPTIC used to ignore windows:** With **`(imply (= ?x hallB) (hall_b_safe))`**, some OPTIC builds still produced illegal Hall β steps across unsafe times. The seismic domain now uses **`beta-hall`** vs **`other-site`** and **separate durative names** (`move_out_of_tunnel_to_beta`, `load_beta`, …) with **plain `(hall_b_safe)`** preconditions so TILs are harder to ignore.

**cs1 / cs2 “two loads and two unloads”:** The robot has **two slots**. Goals require **both** canister samples in **stasis**, so a good plan loads **cs2** then **cs1** (or the reverse) at cryo, then unloads both at stasis — that is **one** visit pattern, not a mistake.

**`Bad plan file!`:** path missing or not mounted. **`Bad plan description!`:** parser/encoding issue.

## Hall β + seismic (optional — timed initial literals)

Separate files **do not** replace `domain.pddl` / `problem.pddl`.

| File | Role |
|------|------|
| `domain-seismic.pddl` | Types **`beta-hall`** (only **`hallB`**) and **`other-site`** (all other map sites). **`hallB`** is a **constant** of type **`beta-hall`**. Hall β uses **`*_beta`** actions; everywhere else uses **`*_site`** / **`move`**. Hall β actions require **`(hall_b_safe)`** at **start**, **`(over all (hall_b_safe))`**, and (for tunnel exit to β) **`(at end (hall_b_safe))`**. **`move`** is only between **`other-site`** (this map has no direct **hallA↔hallB** edge). |
| `problem-seismic.pddl` | **`imv-p04-seismic`**: locations except **`hallB`** are **`other-site`**. Alternating TILs (example): unsafe **[20,50)**, **[80,110)**; safe **[0,20)**, **[50,80)**, **[110,…)** — edit **`:init`** to change intervals. |
| `problem-curator-drone-seismic.pddl` | Same TIL + two robots. |

**Planner:** **OPTIC** with TIL support. **TFD** may not load this domain (many actions / typing). Re-run OPTIC after changing TIL times; validate schedules with **VAL**.

```bash
planutils run val Validate domain-seismic.pddl problem-seismic.pddl
planutils run optic domain-seismic.pddl problem-seismic.pddl
# optional: validate a saved schedule
planutils run val Validate domain-seismic.pddl problem-seismic.pddl results/your.plan
```

## Files

| File | Role |
|------|------|
| `domain.pddl` | Temporal domain (`imv`) |
| `problem.pddl` | Main temporal problem (1 robot, 2 slots) |
| `problem-curator-drone.pddl` | Two robots, optional parallelism demo |
| `domain-seismic.pddl` | Hall β + TIL variant (`imv-seismic`) |
| `problem-seismic.pddl` | Seismic window deadline (single robot) |
| `problem-curator-drone-seismic.pddl` | Seismic variant, two robots |
| `scripts/respace_plan_val.py` | Optional gap insertion between durative steps for **VAL** |
| `results/optic-seismic-raw.plan` | OPTIC output (no VAL massage) |
| `results/optic-seismic-val.plan` | After **`respace_plan_val.py`** (default) — use with **`Validate`** |
| `results/optic-seismic-drone-val.plan` | After **`respace_plan_val.py --parallel`** on the curator+drone plan |

Save planner output under `results/` for the report (e.g. `popf.plan`).
