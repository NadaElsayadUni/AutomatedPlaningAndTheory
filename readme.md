# Automated Planning Project Report Draft

## 1. Project Overview

This project models the Interplanetary Museum Vault (IMV) scenario across five planning problems, starting from a simple classical PDDL formulation and progressing to HTN, temporal planning, and finally PlanSys2 execution.

My understanding of the scenario is:

- the environment contains symbolic locations: `entrance`, `tunnel`, `hallA`, `hallB`, `cryo`, `pod1`, `pod2`, and `stasis`
- the robot must move artifacts between these locations according to the museum constraints
- `a1` and `a2` must end in `cryo`
- `b1` and `b2` come from Hall Beta and must be moved to anti-vibration pods
- `cs1` and `cs2` start in `cryo` and must end in `stasis`
- later problems add capacity, multiple agents, HTN decomposition, durative actions, tunnel sealing, seismic access constraints, and PlanSys2 execution

The assignment in `main.pdf` asks for a step-by-step development of the same overall museum scenario using different planning paradigms. My work follows that progression:

1. Problem 1: classical baseline
2. Problem 2: capacity and multi-agent extension
3. Problem 3: HTN/HDDL version of the same scenario
4. Problem 4: temporal / durative version
5. Problem 5: PlanSys2 implementation using fake actions

---

## 2. General Modeling Assumptions

Some assumptions were used to keep the models solvable and easy to explain:

- the museum map is abstracted into symbolic connected locations instead of geometric coordinates
- artifacts are indivisible objects; only their location matters
- robot carrying capacity is modeled with slots
- only constraints that materially affect planning are modeled explicitly
- more detailed realism is introduced gradually across problems instead of all at once in Problem 1

### Shared initial state and mission goal

Across the project, the core scenario remains the same even when the modeling formalism changes.

The common initial situation is:

- the robot starts at the `entrance`
- the environment contains the locations `entrance`, `tunnel`, `hallA`, `hallB`, `cryo`, `pod1`, `pod2`, and `stasis`
- artifacts are initially distributed as:
  - `a1`, `a2` in `hallA`
  - `b1`, `b2` in `hallB`
  - `cs1`, `cs2` in `cryo`
- the map connectivity is centered around the tunnel, which links the entrance and all main rooms

The common mission goal is:

- move `a1` and `a2` to `cryo`
- move `b1` and `b2` to `pod1` and `pod2`
- move `cs1` and `cs2` to `stasis`

What changes from one problem to another is not the mission itself, but the modeling depth:

- Problem 1 uses a simple classical abstraction
- Problem 2 adds capacity and additional agents
- Problem 3 keeps the same mission but expresses it hierarchically
- Problem 4 adds durative actions and temporal constraints
- Problem 5 deploys the temporal/seismic version inside PlanSys2

### Why these predicates were used

The main predicates were chosen because they directly represent the planning state:

- `robot_at` / `at`: robot location
- `artifact_at`: artifact location
- `robot_carrying`, `empty`: single-carry abstraction in Problem 1
- `slot_free`, `in_slot`, `robot_slot`: explicit capacity representation in Problems 2–5
- `connected`: map connectivity
- `manip_free`: prevents impossible overlap between actions in temporal domains
- `tunnel`, `non_tunnel`: distinguish tunnel logic from normal rooms
- `sealing_on`, `sealing_off`: represent vault sealing state for safe tunnel traversal
- `hall_b_safe`: represent seismic accessibility of Hall Beta in the seismic domain

These predicates were kept only when they were needed by the corresponding problem. For example, `manip_free` and sealing predicates were not introduced until the temporal model, because they are not necessary in the simpler classical versions.

---

## 3. Problem 1 — Classical PDDL Baseline

Problem 1 asks for a classical PDDL model of the IMV scenario with one robotic curator that can carry one artifact at a time. This problem acts as the baseline classical formulation. The goal here was to first capture the core transport logic before adding more realism in the later problems. For that reason, the model is intentionally simple and focuses on reachability, carrying, and final artifact placement.

### Structure and implementation

The baseline is structured around:

- one robot `r1`
- one-artifact carrying capacity using `empty` and `robot_carrying`
- actions:
  - `move`
  - `load`
  - `unload`
- artifact goal structure:
  - `a1`, `a2` to `cryo`
  - `b1`, `b2` to `pod1`, `pod2`
  - `cs1`, `cs2` to `stasis`

### Files and what each one does

- `problem1/domain.pddl`
  - defines the classical domain `imv`
  - introduces the base predicates `robot_at`, `artifact_at`, `robot_carrying`, `empty`, and `connected`
  - keeps the action set intentionally minimal with only `move`, `load`, and `unload`
- `problem1/problem.pddl`
  - defines the initial museum map and objects
  - places the robot at `entrance`
  - places each artifact in its starting room
  - encodes the final placement goals for all six artifacts
- `problem1/results/`
  - stores planner outputs used as evidence that the model is solvable

### Assumptions and simplifications

At this stage I intentionally did **not** model:

- explicit seismic timing for Hall Beta
- explicit tunnel sealing
- cooling or temperature thresholds
- a more detailed tunnel structure

The tunnel is treated as a single hub location. This is a conscious abstraction, because Problem 1 is meant to establish the classical transport baseline first.

### What was already done

The problem was fully modeled and solved with more than one classical planner. The generated plans confirm that the baseline domain is valid and that the target goal configuration is reachable.

### Results

Files:

- `problem1/results/ff.plan`
- `problem1/results/lama.plan`
- `problem1/results/lama_first.plan`
- `problem1/results/optic.plan`
- `problem1/results/problem.pddl.plan`

Observed result:

- FF, LAMA, and LAMA-first all produced the same basic plan structure with **32 actions**
- the classical planners start with Hall Alpha and Cryo / Stasis work, then finish Hall Beta
- `problem.pddl.plan` follows the same structure again
- OPTIC also solved the problem and produced a **32-action** plan, but with a different ordering
- OPTIC starts from Hall Beta first, then continues with Hall Alpha and Cryo / Stasis

Interpretation:

- despite the different order, the solution quality is essentially the same because the model is still classical and unit-cost
- OPTIC is not worse, but it does not give a meaningful advantage on this non-temporal model

---

## 4. Problem 2 — Capacity and Multi-Agent Extension

Problem 2 extends the same museum scenario by adding explicit carrying capacity and, optionally, a second transport agent. The purpose of this step was to move from a simple single-item courier model to a richer formulation where planner quality can improve by using multiple slots or a second robot.

### Structure and implementation

This problem is structured around:

- slot-based carrying capacity instead of a single `empty` flag
- optional multiple robots
- the same overall museum map and artifact goals as Problem 1
- a second variant with fixed division of labour

### Files and what each one does

- `problem2/domain.pddl`
  - main classical domain with capacity and multi-agent support
  - introduces `slot_free`, `in_slot`, and `robot_slot`
  - `move`, `load`, and `unload` now take robot and slot parameters
- `problem2/problem.pddl`
  - single-curator version of Problem 2
  - `r1` has two slots (`slot1`, `slot2`)
  - same museum layout and same final artifact goals as Problem 1
- `problem2/problem-curator-drone.pddl`
  - adds a second robot `d1`
  - curator and drone both operate on the same map
  - used to test whether the planner can benefit from multi-agent transport
- `problem2/domain-assigned.pddl`
  - extends the main domain with predicate `handles`
  - forces artifacts to be associated with specific robots
- `problem2/problem-curator-drone-assigned.pddl`
  - uses `domain-assigned.pddl`
  - fixes the division of labour between `r1` and `d1`
- `problem2/results/`
  - contains saved plans for single-curator, curator–drone, and assigned variants

### Assumptions and simplifications

Problem 2 still keeps some early abstractions:

- no explicit sealing
- no explicit seismic time windows
- no explicit temperature or cooling constraints

The focus here is specifically on **capacity** and **agent structure**, not yet on temporal realism.

### How it was adjusted from Problem 1

The key adjustment was replacing the binary “carrying or empty” model with a structural slot model. This makes the domain more expressive and lets the planner carry two artifacts at once when useful. I also added a multi-agent version to explore whether cooperation improves the solution.

### What was already done

All main variants were modeled and solved:

- single curator with two slots
- curator + drone without fixed roles
- curator + drone with forced assignment

### Results

Files:

- `problem2/results/ff.plan`
- `problem2/results/lama.plan`
- `problem2/results/lama_first.plan`
- `problem2/results/problem-curator-drone.pddl.plan`
- `problem2/results/ff-problem-curator-drone.pddl.plan`
- `problem2/results/problem-curator-drone-assigned.pddl.plan`
- `problem2/results/ff-problem-curator-drone-assigned.pddl.plan`
- `problem2/results/lama-curator-drone-plan1.plan`
- `problem2/results/lama-curator-drone-plan2.plan`
- `problem2/results/lama-curator-drone-plan3.plan`

Observed result:

- the single-curator two-slot model gives **24 actions**, which is better than Problem 1’s **32 actions**
- this happens because two artifacts can be transported in one trip
- in the unassigned curator–drone model, some planners use only `d1`, so adding another agent does **not** automatically improve the plan
- saved LAMA curator–drone plans vary between **28**, **27**, and **24** actions
- the assigned curator–drone plans use both robots, but are about **30 actions**

Interpretation:

- the main gain in Problem 2 comes from **capacity**
- multi-agent planning is only clearly beneficial when the role structure encourages or forces cooperation
- the assigned domain is not the shortest in action count, but it is the clearest demonstration of division of labour

---

## 5. Problem 3 — HTN / HDDL Model

Problem 3 keeps the same basic museum scenario but changes the modeling paradigm from classical planning to HTN/HDDL. The goal is no longer expressed only as a final state to satisfy; instead, it is decomposed through tasks and methods into an explicit hierarchy of deliveries.

### Structure and implementation

This problem is structured around:

- the same primitive transport actions as the Problem 2 baseline
- one top-level compound task
- one delivery subtask per artifact objective
- methods that decompose high-level tasks into primitive steps

### Files and what each one does

- `problem3/domain.hddl`
  - main HTN domain
  - keeps the same primitive actions as the Problem 2 baseline
  - adds compound tasks such as `relocate_all`, `deliver_a1_to_cryo`, and similar named deliveries
  - defines methods that decompose those tasks into action sequences
- `problem3/problem.hddl`
  - HTN problem file
  - keeps the same museum objects and initial state as the single-curator Problem 2 baseline
  - encodes the mission through the top-level task `(relocate_all)`
- `problem3/domain-pair.hddl`
  - alternative HTN domain
  - groups some work into paired/batched decompositions
  - aims to use capacity more efficiently
- `problem3/panda.txt`
  - solver output for the main HTN domain
- `problem3/panda-pair.txt`
  - solver output for the paired HTN variant

### Modeling decisions

I used explicit named delivery tasks instead of a very generic parameterized HTN formulation. This decision was made because PANDA/HDDL is more stable and easier to debug when the task hierarchy is explicit. It also makes the logic of the report easier to explain.

The paired HTN variant was introduced to test whether a better decomposition design can reduce unnecessary travel compared with the more direct one-delivery-at-a-time decomposition.

### How it was adjusted from Problem 2

Problem 3 does not change the primitive transport logic very much. The major adjustment is representational:

- Problem 2: planner decides directly from predicates and actions
- Problem 3: planner must follow a task hierarchy and method decomposition

This makes Problem 3 useful for comparing not just plan quality, but also the effect of decomposition design.

### What was already done

- the main HTN model was solved with PANDA
- the paired HTN model was also solved
- the repository contains solver outputs for both versions

### Results

Files:

- `problem3/panda.txt`
- `problem3/panda-pair.txt`

Observed result:

- `panda.txt` gives a long decomposition with about **46 primitive actions**
- `panda-pair.txt` gives a much shorter decomposition with about **30 primitive actions**

Interpretation:

- the quality of the HTN solution depends strongly on the method design
- the paired HTN version is better because it groups work and uses the slot structure more effectively
- this shows that in HTN planning, the decomposition itself is part of the solution quality

---

## 6. Problem 4 — Temporal / Durative Planning

Problem 4 converts the same museum mission into a temporal model. This is where the project starts to represent action duration, temporal constraints, realistic sequencing, and tunnel safety requirements more explicitly.

### Structure and implementation

This problem is structured around:

- durative actions instead of instantaneous actions
- explicit sealing logic for tunnel traversal
- resource-style control through `manip_free`
- optional multi-agent parallelism
- a seismic variant with timed Hall Beta constraints

### Files and what each one does

- `problem4/domain.pddl`
  - main temporal domain
  - introduces durative versions of movement, loading, unloading, and sealing
  - distinguishes tunnel vs non-tunnel locations
- `problem4/problem.pddl`
  - main single-robot temporal problem
  - includes sealing state and tunnel typing in the initial state
  - uses `(:metric minimize (total-time))`
- `problem4/problem-curator-drone.pddl`
  - adds a second robot for temporal parallelism tests
- `problem4/domain-seismic.pddl`
  - seismic temporal domain
  - adds `hall_b_safe`
  - uses Hall Beta-specific actions to make the seismic logic explicit
- `problem4/problem-seismic.pddl`
  - single-robot seismic temporal problem
  - uses timed initial literals for Hall Beta safe/unsafe windows
- `problem4/problem-curator-drone-seismic.pddl`
  - multi-agent seismic temporal problem
- `problem4/results/`
  - stores OPTIC-based seismic plans
- `problem4/scripts/respace_plan_val.py`
  - post-processing utility used to make temporal plans easier for VAL to validate

### Durations used

The temporal domains use:

- `move` = 2
- `move_into_tunnel` / `move_out_of_tunnel` = 3
- `activate_sealing` / `deactivate_sealing` = 1
- `load` / `unload` = 1

### Why these durations were chosen

The durations express relative effort rather than physical seconds:

- normal room-to-room movement is cheaper than tunnel traversal
- tunnel traversal is longer because it needs controlled sealing
- sealing and manipulation are short support actions

This was enough to create meaningful temporal trade-offs without overcomplicating the model.

### Why `at start`, `over all`, and `at end` were used

The temporal models use standard PDDL2.1 semantics:

- `at start` for preconditions that must hold before the action begins
- `over all` for safety conditions that must remain true for the entire action
- `at end` for facts that only become true after completion

This is especially important for:

- `manip_free`
- tunnel sealing
- Hall Beta safety in the seismic domain

### How it was adjusted from earlier problems

Problem 4 extends the earlier abstraction by explicitly representing:

- the maintenance tunnel as a constrained transition
- sealing as its own durative process
- concurrency only where it is realistic
- seismic safety windows for Hall Beta in the seismic variant

### What was already done

- the base temporal domain was modeled
- a seismic extension was added
- saved OPTIC plans were generated
- validation support was added with `respace_plan_val.py`

### Results

Files:

- `problem4/results/optic-seismic-raw.plan`
- `problem4/results/optic-seismic-val.plan`
- `problem4/results/optic-seismic-drone.plan`
- `problem4/results/optic-seismic-drone-val.plan`

Observed result:

- `optic-seismic-raw.plan` and `optic-seismic-val.plan` are the same logical plan, but the second has slightly shifted timestamps for easier VAL validation
- the single-robot seismic plan contains about **50 durative actions**
- the curator–drone temporal plan shows overlap between robots, but the schedule is not automatically shorter

Interpretation:

- OPTIC is the most useful practical planner for the seismic temporal domain
- the `-val` files are not “better” plans, but validation-friendly versions of the same plan
- the multi-agent temporal plan is useful as evidence of concurrency, even when it is not the shortest one

---

## 7. Problem 5 — PlanSys2 Deployment

Problem 5 takes the planning model into execution by deploying it inside PlanSys2 with fake actions. This step is different from the previous ones because success is not only “a planner found a plan”, but also “the ROS 2 planning system executed the plan successfully.”

### Structure and implementation

This problem is structured around:

- a PlanSys2 package
- one fake action executor node per planning action
- a temporal seismic domain adapted for PlanSys2
- a runtime command file that loads the problem and executes the mission

### Files and what each one does

- `problem5/pddl/domain.pddl`
  - the deployed temporal/seismic domain used by PlanSys2
  - contains split actions for Hall Beta and other sites
- `problem5/launch/imv_plansys2_launch.py`
  - launches PlanSys2 and all fake action executors
- `problem5/launch/imv_commands.txt`
  - contains the full tested command sequence:
    - initial problem setup
    - cumulative goal phases
    - final full goal
- `problem5/src/*.cpp`
  - fake action executor nodes
  - each node subclasses `ActionExecutorClient` and simulates progress for one domain action
- `problem5/README.md`
  - package-level explanation and usage
- `problem5/RUNNING.md`
  - step-by-step runtime guide
- `problem5/result-seismic.txt`
  - saved successful PlanSys2 run evidence

### Important implementation adjustment

During development, Hall Beta entry was initially modeled in a way that caused execution instability in PlanSys2. This was fixed by changing the domain so the beta destination is passed as a parameter rather than being hardcoded. After that adjustment, Hall Beta transitions executed correctly.

### Why cumulative staged execution was used

The most reliable workflow inside PlanSys2 was not one long monolithic final run. Instead, I used cumulative goal stages written directly into `launch/imv_commands.txt`.

This made the execution sequence:

- easier to debug
- more stable in practice
- still equivalent to reaching the full final mission goal

### How it was adjusted from Problem 4

Problem 5 does not only reuse Problem 4 logic. It also adapts it for execution:

- actions must have fake executors
- the domain must be robust enough to run under PlanSys2
- the practical execution workflow must be stable

That is why the PlanSys2 solution uses a staged cumulative mission instead of relying only on one large run.

### What was already done

- the package builds successfully
- the fake action nodes launch correctly
- the Hall Beta issue was fixed
- the full seismic mission can be completed through the tested command sequence in `imv_commands.txt`
- `result-seismic.txt` records repeated `Plan Succeeded` results

### Results

Files:

- `problem5/result-seismic.txt`

Observed result:

- the mission succeeds in cumulative stages
- each stage ends with `Plan Succeeded`
- the final full mission is achieved through stable staged execution inside PlanSys2

Interpretation:

- the key success in Problem 5 is not only the plan itself, but the fact that the model was actually executed inside a ROS 2 planning system
- the staged workflow is the practical improvement that made the deployment reliable

---

## 8. Planner Comparison and Observed Plan Changes

This section is based on the saved result files inside the repository, not only on theoretical expectations.

### Problem 1 — classical baseline

Compared files:

- `problem1/results/ff.plan`
- `problem1/results/lama.plan`
- `problem1/results/lama_first.plan`
- `problem1/results/optic.plan`
- `problem1/results/problem.pddl.plan`

Observed result:

- FF, LAMA, and LAMA-first all produced the same basic plan structure with **32 actions**
- `problem.pddl.plan` is effectively the same structure again
- OPTIC also solved the problem and produced a **32-action** plan, but with a different ordering

How the plan changed:

- the classical planners start with Hall Alpha and Cryo / Stasis work, then finish Hall Beta
- OPTIC starts from Hall Beta first, then continues with Hall Alpha and Cryo / Stasis
- despite the different order, the solution quality is essentially the same because the model is still classical and unit-cost

Which is better:

- there is no strong winner in Problem 1
- FF and LAMA are the clearest classical baselines because they give the same valid 32-step structure
- OPTIC is not worse, but it does not give a meaningful advantage on this non-temporal model

### Problem 2 — capacity and multi-agent

Compared files:

- `problem2/results/ff.plan`
- `problem2/results/lama.plan`
- `problem2/results/lama_first.plan`
- `problem2/results/problem-curator-drone.pddl.plan`
- `problem2/results/ff-problem-curator-drone.pddl.plan`
- `problem2/results/problem-curator-drone-assigned.pddl.plan`
- `problem2/results/ff-problem-curator-drone-assigned.pddl.plan`
- `problem2/results/lama-curator-drone-plan1.plan`
- `problem2/results/lama-curator-drone-plan2.plan`
- `problem2/results/lama-curator-drone-plan3.plan`

Observed result for the single-curator capacity model:

- FF, LAMA, and LAMA-first all produce a **24-action** plan
- compared with Problem 1’s **32 actions**, this is a clear improvement

Why it improved:

- the robot now has **two slots**
- it can load two artifacts before leaving a room
- this removes repeated travel, especially in Hall Alpha and Cryo / Stasis transport

Observed result for the unassigned curator–drone model:

- the saved FF-style curator–drone plans use only **`d1`** and ignore `r1`, leading to a **32-action** plan
- some saved LAMA variants improve on that:
  - `lama-curator-drone-plan1.plan` -> **28 actions**
  - `lama-curator-drone-plan2.plan` -> **27 actions**
  - `lama-curator-drone-plan3.plan` -> **24 actions**

Interpretation:

- just adding a second agent does **not** automatically produce a better plan
- because curator and drone were modeled with almost the same capabilities, the planner may choose only one robot
- the best saved unassigned LAMA plan is **24 actions**, which is effectively as good as the single-curator two-slot case

Observed result for the assigned model:

- the assigned curator–drone plans use **both** `r1` and `d1`
- they have about **30 actions**

Interpretation:

- this is worse than the best 24-action unassigned plan in pure action count
- however, it demonstrates the intended division of labour more clearly
- in other words, the assigned model is better for showing cooperation, not for minimizing action count

Which is better:

- for **shortest classical plan**, the best Problem 2 result is the **24-action** two-slot solution
- for **showing multi-agent cooperation**, the assigned domain is better, even though it is longer

### Problem 3 — HTN / HDDL

Compared files:

- `problem3/panda.txt`
- `problem3/panda-pair.txt`

Observed result:

- `panda.txt` gives a long HTN decomposition with about **46 primitive actions**
- `panda-pair.txt` gives a much shorter decomposition with about **30 primitive actions**

How the plan changed:

- the main HTN model handles each delivery more independently and often returns the robot to a common restart point
- the paired HTN version groups deliveries and uses the two-slot capacity more effectively

Which is better:

- the **paired HTN variant** is better as a plan
- it reduces unnecessary travel and is much closer to the more efficient classical Problem 2 capacity behavior

### Problem 4 — temporal / seismic planning

Compared files:

- `problem4/results/optic-seismic-raw.plan`
- `problem4/results/optic-seismic-val.plan`
- `problem4/results/optic-seismic-drone.plan`
- `problem4/results/optic-seismic-drone-val.plan`

Observed result for the single-robot seismic plan:

- `optic-seismic-raw.plan` and `optic-seismic-val.plan` contain the **same logical plan**
- the `-val` version only shifts timestamps slightly so that VAL accepts the schedule more reliably
- the single-robot temporal plan has about **50 durative actions**

What changed between raw and val:

- the order of actions is the same
- only the timestamps change
- this means `respace_plan_val.py` is a validation fix, not a planning improvement

Observed result for the curator–drone seismic plan:

- the drone plan contains about **58 durative actions**
- it clearly shows temporal overlap between `r1` and `d1`
- however, the total schedule is not automatically shorter than the single-robot version

Interpretation:

- temporal parallelism exists, but shared sealing and Hall Beta timing create overhead
- so the two-agent temporal plan is better for demonstrating concurrency, not necessarily for minimizing makespan in this specific domain

Which is better:

- **OPTIC** is the most useful planner here because it handles the seismic temporal model directly
- the **single-robot seismic plan** is cleaner and easier to validate
- the **drone plan** is better as evidence of parallelism, even if it is not always shorter

### Problem 5 — PlanSys2 execution

Compared file:

- `problem5/result-seismic.txt`

Observed result:

- the full mission was executed through staged cumulative goals
- each stage ends with `Plan Succeeded`
- the stages were:
  - move `b1` to `pod1`
  - move `b2` to `pod2`
  - move `cs1` to `stasis`
  - move `cs2` to `stasis`
  - move `a1` to `cryo`
  - move `a2` to `cryo`

How the execution strategy changed:

- an earlier long final sequence was unreliable in PlanSys2
- splitting the mission into cumulative stages made the execution stable

Which is better:

- for Problem 5, the staged execution is clearly better than one monolithic run
- PlanSys2 is not being compared on action count alone; the important result is successful execution inside a ROS 2 planning framework

### Overall conclusion from the saved results

- **Problem 1:** classical planners are basically equivalent; plan order changes, but quality is similar
- **Problem 2:** adding two-slot capacity gives the first major improvement; adding a second agent helps only if the model forces or meaningfully differentiates roles
- **Problem 3:** HTN quality depends strongly on the decomposition design; the paired HTN is clearly better than the naive sequential decomposition
- **Problem 4:** OPTIC is the most practical planner for the temporal seismic model; validation-friendly timing is sometimes a separate post-processing step
- **Problem 5:** the best improvement is not a different planner, but a better execution workflow inside PlanSys2

---

## 9. Main Adjustments Across Problems

The project evolved through a sequence of deliberate adjustments:

- Problem 1 established the classical transport baseline
- Problem 2 introduced capacity and multi-agent transport
- Problem 3 kept the same operational logic but changed the representation to HTN
- Problem 4 added temporal reasoning, durations, tunnel sealing, and seismic timing
- Problem 5 deployed the temporal/seismic logic inside PlanSys2 using fake action nodes

Some practical adjustments were made during development:

- simplifying the early models to keep them planner-friendly
- introducing richer predicates only when needed
- splitting Hall Beta actions into separate beta/site variants in the seismic domains
- correcting the PlanSys2 Hall Beta modeling so execution succeeds
- replacing a fragile long final run with a reliable cumulative staged sequence

---

## 10. Conclusion

This project shows a full progression from classical symbolic planning to temporal and execution-aware planning in PlanSys2.

The key idea was not to model everything at once, but to gradually increase realism:

- first solve the transport task classically
- then add capacity and multiple agents
- then express the same problem hierarchically
- then add time, sealing, and seismic safety
- finally deploy the model in PlanSys2 with executable fake actions

From my side, the final result is not just a collection of files, but a connected development process where each problem extends the previous one and introduces a new planning concept in a controlled way.