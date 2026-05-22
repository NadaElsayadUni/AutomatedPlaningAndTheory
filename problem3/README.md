# Problem 3 — HTN (Hierarchical Task Networks)

Same scenario as Problem 2 encoded as an HTN/HDDL model: same primitive actions plus **:task** and **:method** definitions (assignment 2.1.3).

## What’s done

- **HDDL (HTN):**
  - `**domain.hddl`** (domain name `imv-htn`)
    - Same **predicates** and **actions** as the Problem 2 baseline: `move`, `load`, `unload` (slot-based).
    - **Compound tasks:** `relocate_all` plus nullary tasks `deliver_a1_to_cryo`, `deliver_a2_to_cryo`, `deliver_b1_to_pod1`, `deliver_b2_to_pod2`, `deliver_cs1_to_stasis`, `deliver_cs2_to_stasis` (PANDA does not allow constants in a method’s `:task` head, e.g. not `(deliver_to_cryo a1)`).
    - **Methods:** decompose these into sequences of primitive actions; each delivery method returns r1 to entrance so the next can assume the same start.
  - **`problem.hddl`** (problem name `imv-p03`)
    - Same **objects** and **:init** as the single-curator Problem 2 baseline (entrance, tunnel, hallA, hallB, cryo, pod1, pod2, stasis; a1,a2,b1,b2,cs1,cs2; r1; slot1, slot2).
    - **:htn** top-level task: `(relocate_all)`.
  - **`domain-pair.hddl`**
    - Alternative HTN encoding that groups deliveries in pairs / batches while keeping the same primitive action layer.

## Task hierarchy

- **relocate_all** → `deliver_a1_to_cryo`, `deliver_a2_to_cryo`, `deliver_b1_to_pod1`, `deliver_b2_to_pod2`, `deliver_cs1_to_stasis`, `deliver_cs2_to_stasis` (ordered).
- Each leaf task decomposes to ground `move` / `load` / `unload` (same as P2).

## Running PANDA (HTN / HDDL)

**PANDA** is a Java JAR (see `../PANDA.jar` or `labs/3:11/PANDA.jar`). **FF does not parse HDDL.**

**Inside Docker:** the image must include Java. Rebuild after the Dockerfile adds `default-jre-headless`:

```bash
docker build --rm --tag myplanutils /path/to/AP_PROJECT_NADA
docker run -v "/path/to/AP_PROJECT_NADA:/computer" -it --privileged --rm myplanutils bash
cd /computer/problem3
java -Dfile.encoding=UTF-8 -jar ../PANDA.jar -parser hddl domain.hddl problem.hddl
```

If you see `java: command not found`, rebuild the image (Java was added to `AP_PROJECT_NADA/Dockerfile`).

**On macOS (host):** if Java is installed (`java -version`):

```bash
cd "/path/to/AP_PROJECT_NADA/problem3"
java -Dfile.encoding=UTF-8 -jar ../PANDA.jar -parser hddl domain.hddl problem.hddl
```

**`MalformedInputException`:** try `-Dfile.encoding=UTF-8` as above; if it persists, run `xattr -c domain.hddl problem.hddl` on the host.

**PANDA format:** files match `labs/3:11`: `:hierachie`, every `:task` must list **`:parameters (...)`** before `:precondition` (use **`:parameters ()`** if there are no parameters — required for `relocate_all`), then `:effect ()`; methods with named `:subtasks` and `:ordering`; problem `:htn` with `(task0 (relocate_all))`. Section order in the domain: predicates → tasks → methods → actions.

## Files

| File               | Description                                                            |
| ------------------ | ---------------------------------------------------------------------- |
| `domain.hddl`      | Main HTN domain (same primitive actions as Problem 2 + tasks/methods)  |
| `problem.hddl`     | Main HTN problem (same init as Problem 2, goal via `(relocate_all)`)   |
| `domain-pair.hddl` | Alternative HTN domain with paired/grouped decompositions              |
| `panda.txt`        | Example PANDA output for the main HTN model                            |
| `panda-pair.txt`   | Example PANDA output for the paired HTN variant                        |

The classical baseline referenced here is the Problem 2 model in `../problem2/`, not extra `domain.pddl` / `problem.pddl` files inside `problem3/`.


