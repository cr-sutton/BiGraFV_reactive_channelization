#!/usr/bin/env python3
"""
Staged reactive deck for the hybrid channelized network.

Built from constant_chemistry_small_kbias/gyp_and_calc.in by text edits only;
chemistry, kinetics, database, characteristic curves and flow boundary
pressures are unchanged.  Added:
  * primary species Tracer1-3 (one per stage, from hanford.dat)
  * stage waters and a timed inlet CONSTRAINT_LIST:
      stage 0  gypsum-saturated water (no net reaction), Tracer1 pulse
      stage A  dilute water: gypsum dissolution only, Tracer2 pulse at the end
      stage B  the original Na2CO3 injection water: gypsum dissolution +
               calcite precipitation, Tracer3 pulse at the end
  * initial pore water equilibrated with gypsum (stage 0 is reaction-free)
  * time-varying MAXIMUM_TIMESTEP_SIZE (fine inside tracer windows; 1e-3 y broke Ca/SO4 balance)
  * VTK output at stage boundaries plus evenly spaced snapshots, for visual inspection

  python3 deck_staged_reactive_base.py --t0 9e-4 --tA 0.06 --tB 0.12 --pulse 1.1e-5 --window 9e-4 \\
      --dt-tracer 2e-6 --dt-react 1e-5 --out deck.in
"""
from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parent / "constant_chemistry_small_kbias" / "gyp_and_calc.in"
TRACERS = ("Tracer1", "Tracer2", "Tracer3")


def water(name, ph, na, co3, ca, so4, tracer=None):
    tr = "\n".join(f"    {t:7s} {'1.d-3' if t == tracer else '1.d-20'}  T" for t in TRACERS)
    return (f"CONSTRAINT {name}\n  CONCENTRATIONS\n    H+     {ph}  pH\n    Na+    {na}  T\n"
            f"    CO3--  {co3}  T\n    Ca++   {ca}\n    SO4--  {so4}  T\n{tr}\n  /\nEND\n")


def build(t0, tA, tB, pulse, window, dt_tracer, dt_react, n_vtk):
    """Stage schedule (y):
       [0, pulse)             w0_T1   Tracer1 pulse, no net reaction
       [pulse, t0)            w0      Tracer1 observed until t0 (>= window)
       [t0, tA - window)      wA      gypsum dissolution
       [tA - window, +pulse)  wA_T2   Tracer2 pulse, observed until tA
       [tA, tB - window)      wB      gypsum dissolution + calcite precipitation
       [tB - window, +pulse)  wB_T3   Tracer3 pulse, observed until tB (final time)
    Max time step dt_tracer inside tracer windows, dt_react elsewhere.
    """
    s = TEMPLATE.read_text()
    s = s.replace("    SO4--\n  /\n  SECONDARY_SPECIES", "    SO4--\n" + "".join(f"    {t}\n" for t in TRACERS) + "  /\n  SECONDARY_SPECIES", 1)
    assert all(t in s for t in TRACERS), "tracer species not inserted"
    s = re.sub(r"CONSTRAINT initial\n  CONCENTRATIONS\n.*?  /\n",
               "CONSTRAINT initial\n  CONCENTRATIONS\n    H+     7.d0  pH\n    Na+    1.d-3  T\n    CO3--  1.d-10  T\n"
               "    Ca++   1.d-3  M Gypsum\n    SO4--  1.5d-2  T\n"
               + "".join(f"    {t:7s} 1.d-20  T\n" for t in TRACERS) + "  /\n", s, count=1, flags=re.S)
    s = re.sub(r"CONSTRAINT injection_constraint\n.*?END\n",
               water("w0", "7.d0", "1.d-3", "1.d-10", "1.d-3  M Gypsum", "1.5d-2")
               + water("w0_T1", "7.d0", "1.d-3", "1.d-10", "1.d-3  M Gypsum", "1.5d-2", "Tracer1")
               + water("wA", "7.d0", "1.d-3", "1.d-10", "1.d-10  T", "1.d-10")
               + water("wA_T2", "7.d0", "1.d-3", "1.d-10", "1.d-10  T", "1.d-10", "Tracer2")
               + water("wB", "11.11d0", "0.2d0", "0.1d0", "1.d-10  M Calcite", "1.d-10")
               + water("wB_T3", "11.11d0", "0.2d0", "0.1d0", "1.d-10  M Calcite", "1.d-10", "Tracer3"),
               s, count=1, flags=re.S)
    wA0, wB0 = tA - window, tB - window
    assert pulse < t0 < wA0 < tA < wB0 < tB, "stage times out of order"
    sched = [(0.0, "w0_T1"), (pulse, "w0"), (t0, "wA"), (wA0, "wA_T2"), (wA0 + pulse, "wA"),
             (tA, "wB"), (wB0, "wB_T3"), (wB0 + pulse, "wB")]
    lst = "\n".join(f"    {t:.6e} {c}" for t, c in sched)
    s = re.sub(r"TRANSPORT_CONDITION inflow_conc\n  TYPE ZERO_GRADIENT\n  CONSTRAINT_LIST\n.*?  /\nEND",
               f"TRANSPORT_CONDITION inflow_conc\n  TYPE ZERO_GRADIENT\n  TIME_UNITS y\n  CONSTRAINT_LIST\n{lst}\n  /\nEND",
               s, count=1, flags=re.S)
    dts = [(0.0, dt_tracer), (t0, dt_react), (wA0, dt_tracer), (tA, dt_react), (wB0, dt_tracer)]
    dt_lines = "\n".join(f"    MAXIMUM_TIMESTEP_SIZE {d:.1e} y at {t:.6e} y" for t, d in dts)
    s = re.sub(r"TIME\n.*?END\n", f"TIME\n{dt_lines}\n    FINAL_TIME {tB:.6e} y\nEND\n", s, count=1, flags=re.S)
    import numpy as np
    times = sorted(set(np.round(np.r_[np.linspace(0, tB, n_vtk + 1)[1:], [t0, wA0, tA, wB0, tB]], 10)))
    # top-level OUTPUT block (column 0; the CHEMISTRY OUTPUT block is indented)
    s = re.sub(r"^OUTPUT\n", "OUTPUT\n  TIMES y " + " ".join(f"{t:.6e}" for t in times) + "\n", s, count=1, flags=re.M)
    for needle in ("w0_T1", "wA_T2", "wB_T3", "TIMES y", f"FINAL_TIME {tB:.6e}", " at "):
        assert needle in s, f"edit failed: {needle}"
    return s


P_SEEPAGE = float(os.environ.get("P_SEEPAGE", 1.01325e6))   # km-scale domains: raise (env) so the top stays saturated


def rate_controlled(s, rate_m3y, well_box):
    """Rate-controlled injection: SOURCE_SINK on a one-cell inlet manifold
    (add_inlet_manifold.py) and a seepage outflow on the opposite face.
    Gravity is switched on (SEEPAGE needs it) with a hydrostatic initial
    pressure at the seepage reference; the manifold cell starts without
    minerals."""
    def sub(pattern, repl):
        nonlocal s
        s, n = re.subn(pattern, repl, s, count=1, flags=re.S | re.M)
        assert n == 1, f"edit failed: {pattern[:40]}"
    # SEEPAGE is evaluated through PFLOTRAN's hydrostatic coupler, which needs
    # gravity (as in J. Hyman's injection deck): gravity on, hydrostatic start
    sub(r"^\s*GRAVITY 0\.d0 0\.d0 0\.d0\n", "  # GRAVITY 0.d0 0.d0 0.d0   (default gravity: SEEPAGE outflow needs it)\n")
    sub(r"^FLOW_CONDITION initial\n.*?^END\n",
        f"FLOW_CONDITION initial\n  TYPE\n     LIQUID_PRESSURE HYDROSTATIC\n  /\n  DATUM 0.d0 0.d0 0.d0\n"
        f"  LIQUID_PRESSURE {P_SEEPAGE:.6e}\nEND\n")
    sub(r"^FLOW_CONDITION inflow \n.*?^END\n",
        f"FLOW_CONDITION injection\n  TYPE\n    RATE VOLUMETRIC_RATE\n  /\n  RATE {rate_m3y:.6e} m^3/y\nEND\n")
    sub(r"^FLOW_CONDITION outflow\n.*?^END\n",
        f"FLOW_CONDITION boundaries\n  TYPE\n    LIQUID_PRESSURE SEEPAGE\n  /\n  DATUM 0.d0 0.d0 0.d0\n  LIQUID_PRESSURE {P_SEEPAGE:.6e}\nEND\n")
    sub(r"^BOUNDARY_CONDITION INFLOW\n.*?^END\n",
        "SOURCE_SINK inflow\n    FLOW_CONDITION injection\n    TRANSPORT_CONDITION inflow_conc\n    REGION well\nEND\n")
    sub(r"^BOUNDARY_CONDITION OUTFLOW\n.*?^/\n",
        "BOUNDARY_CONDITION outflow\n  FLOW_CONDITION boundaries\n  TRANSPORT_CONDITION seepage_face\n  REGION outflow\n/\n")
    # SEEPAGE only allows outflow, so the Dirichlet half of DIRICHLET_ZERO_GRADIENT
    # never applies to advection; its only effect is boundary diffusion, which
    # the graphs' placeholder boundary-face areas (1e3 m^2 at ~0 distance) make
    # enormous and which clogged a 7e-11 m^3 outlet cell with gypsum.
    sub(r"^TRANSPORT_CONDITION seepage_face\n  TYPE DIRICHLET_ZERO_GRADIENT *\n",
        "TRANSPORT_CONDITION seepage_face\n  TYPE ZERO_GRADIENT\n")
    (lo, hi) = well_box
    sub(r"^REGION outflow\n.*?^END\n",
        "REGION outflow\n  FILE boundary_right_e.ex\nEND\n\nREGION well\n  COORDINATES\n"
        f"    {lo[0]:.6e} {lo[1]:.6e} {lo[2]:.6e}\n    {hi[0]:.6e} {hi[1]:.6e} {hi[2]:.6e}\n  /\nEND\n")
    sub(r"^INITIAL_CONDITION\n(.*?)^/\n",
        "INITIAL_CONDITION\n\\1/\n\nINITIAL_CONDITION\n  FLOW_CONDITION initial\n  TRANSPORT_CONDITION well_initial\n  REGION well\n/\n")
    sub(r"^TRANSPORT_CONDITION initial\n",
        "TRANSPORT_CONDITION well_initial\n  TYPE dirichlet\n  CONSTRAINT_LIST\n    0.d0 well_initial\n  /\nEND\n\nTRANSPORT_CONDITION initial\n")
    sub(r"^CONSTRAINT w0\n",
        "CONSTRAINT well_initial\n  CONCENTRATIONS\n    H+     7.d0  pH\n    Na+    1.d-3  T\n    CO3--  1.d-10  T\n"
        "    Ca++   1.d-3  M Gypsum\n    SO4--  1.5d-2  T\n"
        + "".join(f"    {t:7s} 1.d-20  T\n" for t in TRACERS) +
        "  /\n  MINERALS\n    Gypsum  0.d0  750  m^2/kg\n    Calcite 0.d0  200  m^2/m^3\n  /\n  ACKNOWLEDGE_ZERO_SURFACE_AREA\nEND\nCONSTRAINT w0\n")
    return s


def inert_graph_boundary_cells(s, x_in, x_out, half_width=1.0e-3):
    """graph_to_pflotran adds boundary helper cells with ~1e-10 m^3 volume at
    the inlet/outlet faces.  Water passes them in ~0.01 s, so Newton's
    flux-scaled tolerance leaves ~1e-6 relative concentration error there; the
    resulting ~1e-6 supersaturation precipitated gypsum until a helper cell
    clogged (porosity 0).  They hold no physical rock, so they start
    mineral-free (constraint well_initial).  Fracture cells are unaffected;
    not applied to the DFN, whose boundary nodes are real mesh cells."""
    regions, ics = "", ""
    for name, x in (("graph_inlet_cells", x_in), ("graph_outlet_cells", x_out)):
        regions += (f"REGION {name}\n  COORDINATES\n    {x - half_width:.6e} -1.d3 -1.d3\n"
                    f"    {x + half_width:.6e} 1.d3 1.d3\n  /\nEND\n\n")
        ics += (f"INITIAL_CONDITION\n  FLOW_CONDITION initial\n  TRANSPORT_CONDITION well_initial\n"
                f"  REGION {name}\n/\n\n")
    s, n1 = re.subn(r"^REGION well\n", regions + "REGION well\n", s, count=1, flags=re.M)
    s, n2 = re.subn(r"^SOURCE_SINK inflow\n", ics + "SOURCE_SINK inflow\n", s, count=1, flags=re.M)
    assert n1 == 1 and n2 == 1, "inert boundary edit failed (rate-controlled deck required)"
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--t0", type=float, required=True, help="end of reaction-free stage 0 (y)")
    ap.add_argument("--tA", type=float, required=True, help="end of gypsum-only stage A (y)")
    ap.add_argument("--tB", type=float, required=True, help="end of gypsum+calcite stage B (y)")
    ap.add_argument("--pulse", type=float, required=True, help="tracer pulse duration (y)")
    ap.add_argument("--window", type=float, required=True, help="tracer observation window (y)")
    ap.add_argument("--dt-tracer", type=float, required=True)
    ap.add_argument("--dt-react", type=float, required=True)
    ap.add_argument("--n-vtk", type=int, default=30)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--rate", type=float, default=None, help="injection rate (m^3/y); enables SOURCE_SINK + seepage outflow")
    ap.add_argument("--manifold-json", type=Path, default=None, help="inlet_manifold.json from add_inlet_manifold.py")
    ap.add_argument("--inert-boundary-x", type=float, nargs=2, default=None, metavar=("X_IN", "X_OUT"),
                    help="graph runs: make the zero-volume boundary helper cells at these x faces mineral-free")
    ap.add_argument("--checkpoint-times", type=float, nargs="+", default=None,
                    help="extra PFLOTRAN checkpoint times (y), e.g. the end of stage A for a stage-B restart")
    ap.add_argument("--direct-transport", action="store_true",
                    help="direct linear solver + residual ATOL 1e-15 for transport (BCGS/ILU diverged, and Newton updates oscillated in gypsum-exhausted cells with an already-negligible residual)")
    a = ap.parse_args()
    deck = build(a.t0, a.tA, a.tB, a.pulse, a.window, a.dt_tracer, a.dt_react, a.n_vtk)
    if a.rate is not None:
        import json
        box = json.loads(a.manifold_json.read_text())["region_box"]
        deck = rate_controlled(deck, a.rate, box)
    if a.checkpoint_times:
        times = " ".join(f"{t:.6e}" for t in a.checkpoint_times)
        deck, n = re.subn(r"^  CHECKPOINT\n    FORMAT HDF5\n  /\n",
                          f"  CHECKPOINT\n    TIMES y {times}\n    FORMAT HDF5\n  /\n", deck, count=1, flags=re.M)
        assert n == 1, "CHECKPOINT block not found"
    if a.inert_boundary_x is not None:
        deck = inert_graph_boundary_cells(deck, *a.inert_boundary_x)
    if a.direct_transport:
        deck, n = re.subn(r"^(TIME\n.*?^END\n)",
                          "\\1\nNUMERICAL_METHODS TRANSPORT\n  NEWTON_SOLVER\n    ATOL 1.d-15\n  /\n"
                          "  LINEAR_SOLVER\n    SOLVER DIRECT\n  /\nEND\n",
                          deck, count=1, flags=re.S | re.M)
        assert n == 1, "TIME block not found"
    a.out.write_text(deck)
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
