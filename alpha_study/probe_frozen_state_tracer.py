#!/usr/bin/env python3
"""
Frozen-state flow + tracer snapshots of a single-stage reactive run
(quartz-dissolution protocol: freeze the reacted porosity/permeability at
each checkpoint, then probe it with a separate steady flow solve and a
conservative tracer pulse; the chemistry does not evolve during the probe).

For checkpoint k of <run_dir> (single_stage.in.schedule.json; k = 0 is the
unreacted state) writes <run_dir>/snap_k/:
  snap_properties.h5   Cell Ids, Permeability, Porosity from single_stage-<idx>.vtk
  snap.in              same rate-controlled flow (SOURCE_SINK on the inlet
                       manifold, seepage outflow, gravity) and one Tracer;
                       pulse after 0.2 residence times of flow spin-up,
                       observed for 20 residence times
The VTK and darcyvel output of each snapshot are kept for inspection.

  python3 probe_frozen_state_tracer.py setup reactive_TPL_6x4x4m/seed4221/gypsum__geometric_graph__template_rate
  python3 probe_frozen_state_tracer.py run   reactive_TPL_6x4x4m/seed4221/gypsum__geometric_graph__template_rate [--np 3]
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import h5py
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "physics_upscaling"))
from bipartite_pressure_solutions_functions import read_scalar_from_vtk  # noqa: E402
from deck_staged_reactive_base import P_SEEPAGE  # noqa: E402
from write_corrected_bigrafv_inputs import read_uge  # noqa: E402

DATABASE = "/Users/collin/src/pflotran/database/hanford.dat"
SPINUP, PULSE, WINDOW, DT = 0.2, 0.02, 20.0, 0.01     # in residence times
# dense km graphs: coarser probes via PROBE_PULSE / PROBE_WINDOW / PROBE_DT (residence times)
PULSE = float(os.environ.get("PROBE_PULSE", PULSE))
WINDOW = float(os.environ.get("PROBE_WINDOW", WINDOW))
DT = float(os.environ.get("PROBE_DT", DT))
# finer early output (the mass-balance file is written every step): steps of PROBE_DT_FINE residence times until
# PROBE_FINE_UNTIL residence times after the pulse starts, then PROBE_DT.  PROBE_DIR names the snapshot folders
# (default snap_k), so a finer re-probe can sit beside the original.
DT_FINE = float(os.environ.get("PROBE_DT_FINE", 0) or 0)
FINE_UNTIL = float(os.environ.get("PROBE_FINE_UNTIL", 3.0))
PREFIX = os.environ.get("PROBE_DIR", "snap")
# opt-in plume frames for animations: extra VTK outputs every PROBE_VTK_DT residence times until PROBE_VTK_UNTIL
# residence times after the pulse starts (default off: only the original outputs are written)
VTK_DT = float(os.environ.get("PROBE_VTK_DT", 0) or 0)
VTK_UNTIL = float(os.environ.get("PROBE_VTK_UNTIL", 3.0))


def vtk_times_lines(t_s, tau_y):
    if VTK_DT <= 0:
        return f"  TIMES y {t_s:.6e}\n"
    ts = [t_s + i * VTK_DT * tau_y for i in range(int(round(VTK_UNTIL / VTK_DT)) + 1)]
    return "".join("  TIMES y " + " ".join(f"{t:.6e}" for t in ts[i:i + 8]) + "\n" for i in range(0, len(ts), 8))


def max_dt_lines(tau_y):
    if DT_FINE > 0:
        return (f"  MAXIMUM_TIMESTEP_SIZE {DT_FINE * tau_y:.6e} y\n"
                f"  MAXIMUM_TIMESTEP_SIZE {DT * tau_y:.6e} y at {(SPINUP + FINE_UNTIL) * tau_y:.6e} y\n")
    return f"  MAXIMUM_TIMESTEP_SIZE {DT * tau_y:.6e} y\n"


def deck(rate_m3y, well_box, tau_y):
    t_s, t_p, t_end = SPINUP * tau_y, (SPINUP + PULSE) * tau_y, (SPINUP + WINDOW) * tau_y
    (lo, hi) = well_box
    return f"""# frozen-state snapshot: steady rate-controlled flow + conservative tracer pulse
SIMULATION
  SIMULATION_TYPE SUBSURFACE
  PROCESS_MODELS
    SUBSURFACE_FLOW flow
      MODE RICHARDS
    /
    SUBSURFACE_TRANSPORT transport
      MODE GIRT
    /
  /
END
SUBSURFACE

CHEMISTRY
  PRIMARY_SPECIES
    Tracer
  /
  DATABASE {DATABASE}
  OUTPUT
    TOTAL
    ALL
  /
END

GRID
  TYPE unstructured_explicit full_mesh_vol_area.uge
END

FLUID_PROPERTY
  DIFFUSION_COEFFICIENT 1e-9
END

DATASET Permeability
  FILENAME snap_properties.h5
END

DATASET Porosity
  FILENAME snap_properties.h5
END

MATERIAL_PROPERTY fractures
  ID 1
  POROSITY DATASET Porosity
  TORTUOSITY 1.0d0
  CHARACTERISTIC_CURVES default
  PERMEABILITY
    DATASET Permeability
  /
END

CHARACTERISTIC_CURVES default
  SATURATION_FUNCTION VAN_GENUCHTEN
    M 0.5d0
    ALPHA  1.d-4
    LIQUID_RESIDUAL_SATURATION 0.1d0
    MAX_CAPILLARY_PRESSURE 1.d8
  /
  PERMEABILITY_FUNCTION MUALEM_VG_LIQ
    M 0.5d0
    LIQUID_RESIDUAL_SATURATION 0.1d0
  /
END

OUTPUT
{vtk_times_lines(t_s, tau_y)}  PRINT_PRIMAL_GRID
  FORMAT VTK
  ACKNOWLEDGE_VTK_FLAW
  MASS_FLOWRATE
  MASS_BALANCE
  MASS_BALANCE_FILE
    TOTAL_MASS_REGIONS
      All
    /
  /
  VARIABLES
    LIQUID_PRESSURE
    PERMEABILITY
    POROSITY
  /
END

TIME
{max_dt_lines(tau_y)}  FINAL_TIME {t_end:.6e} y
END

REGION All
  COORDINATES
    -5.d20 -5.d20 -5.d20
    5.d20 5.d20 5.d20
  /
END

REGION outflow
  FILE boundary_right_e.ex
END

REGION well
  COORDINATES
    {lo[0]:.6e} {lo[1]:.6e} {lo[2]:.6e}
    {hi[0]:.6e} {hi[1]:.6e} {hi[2]:.6e}
  /
END

CONSTRAINT clean
  CONCENTRATIONS
    Tracer 1.d-20 T
  /
END

CONSTRAINT pulse
  CONCENTRATIONS
    Tracer 1.d-3 T
  /
END

FLOW_CONDITION initial
  TYPE
    LIQUID_PRESSURE HYDROSTATIC
  /
  DATUM 0.d0 0.d0 0.d0
  LIQUID_PRESSURE {P_SEEPAGE:.6e}
END

FLOW_CONDITION injection
  TYPE
    RATE VOLUMETRIC_RATE
  /
  RATE {rate_m3y:.6e} m^3/y
END

FLOW_CONDITION boundaries
  TYPE
    LIQUID_PRESSURE SEEPAGE
  /
  DATUM 0.d0 0.d0 0.d0
  LIQUID_PRESSURE {P_SEEPAGE:.6e}
END

TRANSPORT_CONDITION initial
  TYPE dirichlet
  CONSTRAINT_LIST
    0.d0 clean
  /
END

TRANSPORT_CONDITION seepage_face
  TYPE ZERO_GRADIENT
  CONSTRAINT_LIST
    0.d0 clean
  /
END

TRANSPORT_CONDITION inflow_conc
  TYPE ZERO_GRADIENT
  TIME_UNITS y
  CONSTRAINT_LIST
    0.d0 clean
    {t_s:.6e} pulse
    {t_p:.6e} clean
  /
END

INITIAL_CONDITION
  FLOW_CONDITION initial
  TRANSPORT_CONDITION initial
  REGION All
/

SOURCE_SINK inflow
  FLOW_CONDITION injection
  TRANSPORT_CONDITION inflow_conc
  REGION well
END

BOUNDARY_CONDITION outflow
  FLOW_CONDITION boundaries
  TRANSPORT_CONDITION seepage_face
  REGION outflow
/

STRATA
  REGION All
  MATERIAL fractures
END

END_SUBSURFACE
"""


def snapshots(run_dir):
    """Every VTK state (k = VTK index); tau_d is the target where the state is a
    checkpoint, NaN otherwise (the analysis uses the dissolved fraction from
    the mass balance)."""
    sched = json.loads((run_dir / "single_stage.in.schedule.json").read_text())
    chk = {c["vtk_index"]: c["tau_d"] for c in sched["checkpoints"]}
    times = [0.0] + sched["vtk_times_y"]
    return [dict(k=i, tau_d=0.0 if i == 0 else chk.get(i, float("nan")), t_y=t, vtk_index=i,
                 checkpoint=i == 0 or i in chk) for i, t in enumerate(times)], sched


def setup(run_dir, checkpoints_only=False, states=None):
    snaps, sched = snapshots(run_dir)
    if checkpoints_only:                                   # large DFNs: probe the tau_d checkpoints only
        snaps = [s for s in snaps if s["checkpoint"]]
        if len(read_uge(run_dir / "full_mesh_vol_area.uge")[0]) > int(os.environ.get("PROBE_FEW_ABOVE", 50000)) and len(snaps) > 3:
            mid = min(snaps[1:-1], key=lambda s: abs(s["tau_d"] - 1.0))   # ~1 h per probe at 135k cells:
            snaps = [snaps[0], mid, snaps[-1]]                          # initial, tau_d ~ 1, final
    if states:                                             # explicit VTK indices (negative counts from the end)
        n = len(snaps)
        keep = {k % n for k in states}
        snaps = [s for s in snaps if s["k"] in keep]
    cells, _ = read_uge(run_dir / "full_mesh_vol_area.uge")
    man = json.loads((run_dir / "inlet_manifold.json").read_text())
    vol = cells[:, 4].copy()
    vol[man["manifold_cell"] - 1] = 0.0                     # exclude the manifold from the pore volume
    out = []
    for s in snaps:
        vtk = run_dir / f"single_stage-{s['vtk_index']:03d}.vtk"
        if not vtk.exists():
            print(f"missing {vtk.name}; run incomplete")
            break
        phi = np.asarray(read_scalar_from_vtk(str(vtk), "Porosity"), float)[: len(cells)]
        k = np.asarray(read_scalar_from_vtk(str(vtk), "Permeability"), float)[: len(cells)]
        d = run_dir / f"{PREFIX}_{s['k']}"
        d.mkdir(exist_ok=True)
        for f in ("full_mesh_vol_area.uge", "boundary_right_e.ex", "boundary_left_w.ex", "materialid.dat"):
            if (run_dir / f).exists():
                shutil.copy(run_dir / f, d / f)
        with h5py.File(d / "snap_properties.h5", "w") as h:
            h["Cell Ids"] = np.arange(1, len(cells) + 1, dtype=np.int64)
            h["Permeability"] = k
            h["Porosity"] = phi
        pv = float((phi * vol).sum())
        tau_y = pv / sched["rate_m3y"]
        text = deck(sched["rate_m3y"], man["region_box"], tau_y)
        run_deck = (run_dir / "single_stage.in").read_text()
        if run_deck.startswith("# outflow: Dirichlet faces"):         # same boundaries as the reactive run
            import re as _re
            from stabilize_graph_run import dirichlet_outflow_text
            p0 = float(_re.search(r"FLOW_CONDITION boundaries\n.*?LIQUID_PRESSURE ([0-9.eEd+-]+)", run_deck, _re.S).group(1).replace("d", "e"))
            text = dirichlet_outflow_text(text, p0)
        if "SCALED_VOLUMETRIC_RATE" in run_deck:
            # reactive run used the quartz paper's boundaries: probe with the same ones
            from deck_quartz import paper_bc
            text = paper_bc(text.replace("    0.d0 initial\n  /\nEND\n\nTRANSPORT_CONDITION inflow_conc",
                                         "    0.d0 clean\n  /\nEND\n\nTRANSPORT_CONDITION inflow_conc"), sched["rate_m3y"])
            text = text.replace("TRANSPORT_CONDITION initial\n  REGION pinned", "TRANSPORT_CONDITION seepage_face\n  REGION pinned")
            shutil.copy(run_dir / "pinned.ex", d / "pinned.ex")
        (d / "snap.in").write_text(text)
        meta = dict(s, pore_volume_m3=pv, tau_res_y=tau_y, t_pulse_y=SPINUP * tau_y, pulse_y=PULSE * tau_y,
                    rate_m3y=sched["rate_m3y"], vtk_source=vtk.name)
        (d / "snap.json").write_text(json.dumps(meta, indent=1))
        out.append(meta)
    print(json.dumps([{k: m[k] for k in ("k", "tau_d", "pore_volume_m3", "tau_res_y")} for m in out], indent=1))


def run(run_dir, np_):
    cfg = json.loads(Path(os.path.expanduser("~/.dfnworksrc")).read_text())
    exe = cfg["PFLOTRAN_EXE"]
    mpirun = Path(os.environ.get("PETSC_DIR", ""), os.environ.get("PETSC_ARCH", ""), "bin", "mpirun")
    for d in sorted(run_dir.glob(f"{PREFIX}_*"), key=lambda p: int(p.name.split("_")[1])):
        cmd = ([str(mpirun) if mpirun.exists() else "mpirun", "-np", str(np_)] if np_ > 1 else []) + [exe, "-pflotranin", "snap.in"]
        with open(d / "pflotran.stdout", "w") as fh:
            subprocess.run(cmd, cwd=d, stdout=fh, stderr=subprocess.STDOUT)
        ok = (d / "snap-mas.dat").exists()
        print(f"{d.name}: {'ok' if ok else 'FAILED'}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=("setup", "run"))
    ap.add_argument("run_dir", type=Path)
    ap.add_argument("--np", type=int, default=1)
    ap.add_argument("--checkpoints-only", action="store_true")
    ap.add_argument("--states", type=int, nargs="+", default=None, help="VTK indices to probe (e.g. 0 10 -1)")
    a = ap.parse_args()
    if a.action == "setup":
        setup(a.run_dir.resolve(), a.checkpoints_only, a.states)
    else:
        run(a.run_dir.resolve(), a.np)


if __name__ == "__main__":
    main()
