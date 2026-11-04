#!/usr/bin/env python3
"""
Input-only fixes for strongly channelized graph runs (diagnosed on the cubic
k-phi runs, 25 Oct): graph_to_pflotran's boundary helper cells are ~1e-8 m^3,
about a million times smaller than the fractures they drain.  When a channel
routes a large share of the injected flow through one of them, the pressure
solve's small mass imbalance (Newton stops on the step tolerance) is divided
by that tiny volume and conservative solute piles up (Na+ 548 mol/kg in a cell
fed 0.001 mol/kg), until the chemistry returns NaN.

  --min-boundary-volume-frac f   raise every boundary helper cell's volume to
                                 f x the median fracture-cell volume (UGE copy in
                                 the run folder; flow is unchanged, storage changes)
  --tight-flow                   pressure Newton must reduce the residual
                                 (RTOL 1e-12, ATOL 1e-14, STOL off) and the linear
                                 solve is tightened (RTOL 1e-12)

  python3 stabilize_graph_run.py RUN_DIR [--min-boundary-volume-frac 0.01] [--tight-flow]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np


def raise_boundary_volumes(run, frac):
    uge = run / "full_mesh_vol_area.uge"
    lines = uge.read_text().splitlines()
    n = int(lines[0].split()[1])
    rows = [l.split() for l in lines[1:1 + n]]
    kind = {}
    for l in (run / "altered_cells_df.dat").read_text().splitlines()[1:]:
        p = l.split()
        if len(p) > 5:
            kind[int(p[0])] = p[5]
    vol = np.array([float(r[4]) for r in rows])
    frac_cells = np.array([kind.get(i + 1) == "internal" for i in range(n)])
    vmin = frac * float(np.median(vol[frac_cells]))
    changed = 0
    for i, r in enumerate(rows):
        if kind.get(i + 1) == "boundary" and vol[i] < vmin:
            r[4] = f"{vmin:.10e}"
            changed += 1
    lines[1:1 + n] = ["\t".join(r) for r in rows]
    uge.write_text("\n".join(lines) + "\n")
    return changed, vmin


def tighten_flow(run):
    deck = run / "single_stage.in"
    s = deck.read_text()
    block = ("NUMERICAL_METHODS FLOW\n  NEWTON_SOLVER\n    RTOL 1.d-12\n    ATOL 1.d-14\n    STOL 1.d-60\n    MAXIMUM_NUMBER_OF_ITERATIONS 50\n  /\n"
             "  LINEAR_SOLVER\n    RTOL 1.d-12\n  /\nEND\n\n")
    assert "NUMERICAL_METHODS FLOW" not in s
    deck.write_text(s.replace("END_SUBSURFACE", block + "END_SUBSURFACE", 1))


MARK = "# outflow: Dirichlet faces, gravity off (stabilize_graph_run.py --dirichlet-outflow)\n"


def dirichlet_outflow_text(s, p0):
    """Gravity off, uniform initial pressure p0, outflow faces at fixed pressure p0
    (replaces the hydrostatic SEEPAGE outlet).  With injection, every interior
    pressure stays above p0, so every outlet face discharges; no face can flip
    between outflow and no-flow at a tiny pressure margin."""
    import re
    s, n = re.subn(r"^\s*#?\s*GRAVITY 0\.d0 0\.d0 0\.d0[^\n]*\n", "  GRAVITY 0.d0 0.d0 0.d0\n", s, count=1, flags=re.M)
    if n == 0:
        s, n = re.subn(r"^(GRID\n)", "\\1  GRAVITY 0.d0 0.d0 0.d0\n", s, count=1, flags=re.M)
    assert n == 1, "GRID/GRAVITY not found"
    s, n = re.subn(r"^FLOW_CONDITION initial\n.*?^END\n",
                   f"FLOW_CONDITION initial\n  TYPE\n    LIQUID_PRESSURE DIRICHLET\n  /\n  LIQUID_PRESSURE {p0:.6e}\nEND\n", s, count=1, flags=re.S | re.M)
    assert n == 1, "FLOW_CONDITION initial not found"
    s, n = re.subn(r"^FLOW_CONDITION boundaries\n.*?^END\n",
                   f"FLOW_CONDITION boundaries\n  TYPE\n    LIQUID_PRESSURE DIRICHLET\n  /\n  LIQUID_PRESSURE {p0:.6e}\nEND\n", s, count=1, flags=re.S | re.M)
    assert n == 1, "FLOW_CONDITION boundaries not found"
    return MARK + s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir", type=Path)
    ap.add_argument("--min-boundary-volume-frac", type=float, default=None)
    ap.add_argument("--tight-flow", action="store_true")
    ap.add_argument("--dirichlet-outflow", type=float, default=None, metavar="P0",
                    help="gravity off, Dirichlet outflow faces and uniform initial pressure at P0 (Pa)")
    a = ap.parse_args()
    if a.min_boundary_volume_frac:
        n, v = raise_boundary_volumes(a.run_dir, a.min_boundary_volume_frac)
        print(f"{a.run_dir.name}: {n} boundary cells raised to {v:.3g} m^3")
    if a.dirichlet_outflow:
        deck = a.run_dir / "single_stage.in"
        deck.write_text(dirichlet_outflow_text(deck.read_text(), a.dirichlet_outflow))
        print(f"{a.run_dir.name}: Dirichlet outflow at {a.dirichlet_outflow:g} Pa, gravity off")
    if a.tight_flow:
        tighten_flow(a.run_dir)
        print(f"{a.run_dir.name}: tight flow solver")


if __name__ == "__main__":
    main()
