#!/usr/bin/env python3
"""Respace plan starts so VAL orders sealing end effects before the next start.

Single-robot (default): sequential line order + gap after sealing actions.

Curator+drone: use --parallel — group same OPTIC timestamps, reorder for VAL,
bump post-activate window for sealing_on, per-robot gaps in file order, then
push sealing_off / activate starts clear of deactivate intervals."""

import re
import sys
from collections import defaultdict

LINE_RE = re.compile(r"^([\d.]+):\s*\(([^)]+)\)\s*\[([\d.]+)\]\s*$")
SEALING_RE = re.compile(r"\b(activate|deactivate)_sealing_(beta|site)\b")
AFTER_SEALING = 0.02


def is_activate_sealing(act: str) -> bool:
    return act.startswith("activate_sealing_")


def is_deactivate_sealing(act: str) -> bool:
    return act.startswith("deactivate_sealing_")


def cluster_sort_key(act: str, orig_idx: int) -> tuple:
    if "move_into_tunnel" in act or "move_out_of_tunnel" in act:
        tier = 0
    elif "unload" in act or "load" in act:
        tier = 1
    elif is_deactivate_sealing(act):
        tier = 2
    elif is_activate_sealing(act):
        tier = 3
    else:
        tier = 4
    return (tier, orig_idx)


def needs_sealing_off_at_start(act: str) -> bool:
    return (
        is_activate_sealing(act)
        or "load_beta" in act
        or "load_site" in act
        or "unload_beta" in act
        or "unload_site" in act
    )


def needs_sealing_on_at_start(act: str) -> bool:
    return (
        "move_into_tunnel" in act
        or "move_out_of_tunnel" in act
        or is_deactivate_sealing(act)
    )


def activate_sealing_end_times(rows):
    return [t + d for t, a, d, _ in rows if is_activate_sealing(a)]


def bump_activate_starts_after_deactivate(rows, eps: float):
    deacts = [(t, t + d) for t, a, d, _ in rows if is_deactivate_sealing(a)]
    out = []
    for t, act, dur, idx in rows:
        nt = t
        if is_activate_sealing(act):
            for ds, de in deacts:
                if ds <= nt < de - 1e-12:
                    nt = max(nt, de + eps)
        out.append((nt, act, dur, idx))
    return out


def bump_after_deactivate_interval(rows, eps: float):
    deacts = [(t, t + d) for t, a, d, _ in rows if is_deactivate_sealing(a)]
    out = []
    for t, act, dur, idx in rows:
        nt = t
        if needs_sealing_off_at_start(act):
            for ds, de in deacts:
                if ds <= nt < de - 1e-12:
                    nt = max(nt, de + eps)
        out.append((nt, act, dur, idx))
    return out


def bump_post_activate_window(rows, after: float):
    ends = activate_sealing_end_times(rows)
    out = []
    for t, act, dur, idx in rows:
        nt = t
        if needs_sealing_on_at_start(act):
            for ae in ends:
                if ae <= nt < ae + after:
                    nt = max(nt, ae + after)
        out.append((nt, act, dur, idx))
    return out


def robot_token(act: str) -> str:
    parts = act.split()
    return parts[1] if len(parts) > 1 else ""


def enforce_robot_file_order(rows, eps: float):
    rows = sorted(rows, key=lambda r: r[3])
    last_end = {}
    out = []
    for t, act, dur, idx in rows:
        rob = robot_token(act)
        lo = last_end.get(rob, -1e9)
        nt = max(t, lo + eps)
        out.append((nt, act, dur, idx))
        last_end[rob] = nt + dur
    return out


def group_parallel(rows, intra_eps: float):
    by_t = defaultdict(list)
    for t, act, dur, idx in rows:
        key = round(t + 1e-9, 3)
        by_t[key].append((t, act, dur, idx))
    out = []
    for key in sorted(by_t.keys()):
        chunk = by_t[key]
        chunk.sort(key=lambda r: cluster_sort_key(r[1], r[3]))
        for i, (_t, act, dur, idx) in enumerate(chunk):
            start = key + i * intra_eps
            out.append((start, act, dur, idx))
    out.sort(key=lambda r: (r[0], r[3]))
    return out


def parallel_respace(rows_raw, intra_eps: float):
    indexed = [(t, a, d, i) for i, (t, a, d) in enumerate(rows_raw)]
    rows = group_parallel(indexed, intra_eps)
    rows = bump_post_activate_window(rows, AFTER_SEALING)
    gap = max(intra_eps, 0.02)
    rows = enforce_robot_file_order(rows, gap)
    rows = bump_after_deactivate_interval(rows, intra_eps)
    rows = bump_activate_starts_after_deactivate(rows, intra_eps)
    rows = enforce_robot_file_order(rows, gap)
    rows = sorted(rows, key=lambda r: r[3])
    return [(t, a, d) for t, a, d, _ in rows]


def apply_sealing_gaps(rows, eps: float):
    prev_end = 0.0
    prev_act = ""
    out_lines = []
    for i, (t, act, dur) in enumerate(rows):
        if i == 0:
            start = t
        else:
            min_gap = eps
            if SEALING_RE.search(prev_act):
                min_gap = max(eps, AFTER_SEALING)
            start = max(t, prev_end + min_gap)
        out_lines.append(f"{start:.3f}: ({act})  [{dur:.3f}]")
        prev_end = start + dur
        prev_act = act
    return out_lines


def main():
    eps = 0.01
    parallel = False
    intra_eps = 0.005
    argv = sys.argv[1:]
    while argv and argv[0].startswith("--"):
        if argv[0] == "--parallel":
            parallel = True
            argv = argv[1:]
        elif argv[0] == "--eps" and len(argv) >= 2:
            eps = float(argv[1])
            argv = argv[2:]
        elif argv[0] == "--intra-eps" and len(argv) >= 2:
            intra_eps = float(argv[1])
            argv = argv[2:]
        else:
            print("unknown flag:", argv[0], file=sys.stderr)
            sys.exit(1)
    if len(argv) != 2:
        print(
            "usage: respace_plan_val.py [--parallel] [--eps 0.01] [--intra-eps 0.005] input.plan output.plan",
            file=sys.stderr,
        )
        sys.exit(1)
    inp, outp = argv
    rows_raw = []
    with open(inp) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith(";"):
                continue
            m = LINE_RE.match(line)
            if not m:
                print("skip:", line, file=sys.stderr)
                continue
            t, act, dur = float(m.group(1)), m.group(2).strip(), float(m.group(3))
            rows_raw.append((t, act, dur))
    if parallel:
        rows = parallel_respace(rows_raw, intra_eps)
        out_lines = [f"{t:.3f}: ({act})  [{dur:.3f}]" for t, act, dur in rows]
    else:
        rows = [(t, a, d) for t, a, d in rows_raw]
        out_lines = apply_sealing_gaps(rows, eps)
    with open(outp, "w") as f:
        f.write("\n".join(out_lines) + "\n")


if __name__ == "__main__":
    main()
