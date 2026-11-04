#!/usr/bin/env python3
"""
Quartz dissolution deck (quartz paper: Hyman et al. 2024 G-cubed,
rtm_dfn_qtz.in) in the rate-controlled single-stage framework, so the same
runner, frozen-state snapshots and analysis apply.

Kept from rtm_dfn_qtz.in: primary species Tracer / SiO2(aq) / H2O, Quartz
kinetics (k = 1e-12 mol m^-2 s^-1, SURFACE_AREA_VOL_FRAC_POWER 2/3,
AFFINITY_THRESHOLD 1e6), UPDATE_POROSITY / UPDATE_PERMEABILITY,
surface area updated with mineral volume fraction (UPDATE_MINERAL_SURFACE_AREA
is now SURFACE_AREA_FUNCTION VOLUME_FRACTION_RATIO in current PFLOTRAN), LOG_FORMULATION, diffusion 1e-12 m^2/s,
tortuosity 0.5, quartz VF 0.90 with SSA 0.0225 m^2/g, initial water at
quartz equilibrium, inlet water 1e-3 M tracer and 1e-20 SiO2(aq), injection
rate = initial network volume per year.
Changed: hanford.dat (the paper's hanford_Liz.dat is not available; same
Quartz log K), injection through the inlet manifold (SOURCE_SINK) with a
seepage outflow and gravity, as in deck_gypsum_calcite.py, instead of
perm-scaled injection/extraction on the boundary cells plus a pinned node;
run to target fractions of quartz dissolved instead of 5 My.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "physics_upscaling"))
from deck_staged_reactive_base import P_SEEPAGE, inert_graph_boundary_cells  # noqa: E402
from write_corrected_bigrafv_inputs import read_uge  # noqa: E402

DATABASE = "/Users/collin/src/pflotran/database/hanford.dat"
QUARTZ_VF0 = 0.90
MATERIAL_POROSITY = 0.25    # UPDATE_PERMEABILITY scales k by phi / this (paper text: phi0 = 0.01 -> set both)
QUARTZ_MOLAR_VOLUME = 22.688e-6   # m^3/mol, hanford.dat
C_CAP = 0.1                       # mol/m^3: quartz solubility (log K -4.0 at 25 C)


def deck(rate, box, t_end, vtk_times, chk_times, dt, k_mult=1.0, direct=False, ramp=False, bc="seepage", dt_cap=None):
    (lo, hi) = box
    solver = "  LINEAR_SOLVER\n    SOLVER DIRECT\n  /\n" if direct else ""
    # rtm_dfn_qtz.in schedule (0.5 y -> 1 -> 10 -> 100 -> 1000 y), or one cap
    sched = [(t, d if dt_cap is None else min(d, dt_cap)) for t, d in ((0, 0.5), (1e3, 1.0), (1e4, 10.0), (1e5, 100.0), (1e6, 1000.0))]
    dt_lines = ("\n".join(f"  MAXIMUM_TIMESTEP_SIZE {d:g} y at {t:g} y" for t, d in sched)
                if ramp else f"  MAXIMUM_TIMESTEP_SIZE {dt:.6e} y")
    text = f"""# quartz dissolution (rtm_dfn_qtz.in chemistry), rate-controlled single stage
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
  CHECKPOINT
    TIMES y {" ".join(f"{t:.6e}" for t in chk_times)}
    FORMAT HDF5
  /
END
SUBSURFACE

CHEMISTRY
  PRIMARY_SPECIES
    Tracer
    SiO2(aq)
    H2O
  /
  UPDATE_POROSITY
  UPDATE_PERMEABILITY
  MINERALS
    Quartz
  /
  MINERAL_KINETICS
    Quartz
      SURFACE_AREA_FUNCTION VOLUME_FRACTION_RATIO
      RATE_CONSTANT {1.0e-12 * k_mult:.6e} mol/m^2-sec
      SURFACE_AREA_VOL_FRAC_POWER 0.66666667
      AFFINITY_THRESHOLD 1E6
    /
  /
  DATABASE {DATABASE}
  LOG_FORMULATION
  ACTIVITY_COEFFICIENTS TIMESTEP
  OUTPUT
    ALL
    TOTAL
    MINERALS
    MINERAL_VOLUME_FRACTION
    MINERAL_SURFACE_AREA
    MINERAL_SATURATION_INDEX
  /
END

GRID
  TYPE unstructured_explicit full_mesh_vol_area.uge
END

FLUID_PROPERTY
  DIFFUSION_COEFFICIENT 1.d-12
END

DATASET Permeability
  FILENAME dfn_properties.h5
END

MATERIAL_PROPERTY soil1
  ID 1
  POROSITY {MATERIAL_POROSITY:.4f}d0
  TORTUOSITY 0.5d0
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
  TIMES y {" ".join(f"{t:.6e}" for t in vtk_times)}
  PRINT_PRIMAL_GRID
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
    LIQUID_SATURATION
    PERMEABILITY
    POROSITY
  /
END

TIME
{dt_lines}
  FINAL_TIME {t_end:.6e} y
END

NUMERICAL_METHODS FLOW
{solver}END

NUMERICAL_METHODS TRANSPORT
  NEWTON_SOLVER
    ITOL 1.d-8
    ATOL 1.d-15
  /
{solver}END

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

CONSTRAINT initial
  CONCENTRATIONS
    H2O       55.      T
    Tracer    1.d-20   T
    SiO2(aq)  1.d-7    M Quartz
  /
  MINERALS
    Quartz  {QUARTZ_VF0:.2f} 0.0225 m^2/g
  /
END

CONSTRAINT well_initial
  CONCENTRATIONS
    H2O       55.      T
    Tracer    1.d-20   T
    SiO2(aq)  1.d-7    M Quartz
  /
  MINERALS
    Quartz  0.d0 0.0225 m^2/g
  /
  ACKNOWLEDGE_ZERO_SURFACE_AREA
END

CONSTRAINT inlet
  CONCENTRATIONS
    H2O       55.      T
    Tracer    1.d-3    T
    SiO2(aq)  1.d-20   T
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
  RATE {rate:.6e} m^3/y
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
    0.d0 initial
  /
END

TRANSPORT_CONDITION well_initial
  TYPE dirichlet
  CONSTRAINT_LIST
    0.d0 well_initial
  /
END

TRANSPORT_CONDITION seepage_face
  TYPE ZERO_GRADIENT
  CONSTRAINT_LIST
    0.d0 initial
  /
END

TRANSPORT_CONDITION inflow_conc
  TYPE ZERO_GRADIENT
  CONSTRAINT_LIST
    0.d0 inlet
  /
END

INITIAL_CONDITION
  FLOW_CONDITION initial
  TRANSPORT_CONDITION initial
  REGION All
/

INITIAL_CONDITION
  FLOW_CONDITION initial
  TRANSPORT_CONDITION well_initial
  REGION well
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
  MATERIAL soil1
END

END_SUBSURFACE
"""
    if bc == "paper":
        text = paper_bc(text, rate)
    return text


def paper_bc(s, rate):
    """rtm_dfn_qtz.in boundaries: no gravity, uniform initial pressure,
    perm-scaled extraction from the outflow cells, one pinned pressure node
    (pinned.ex, written by main).  Avoids the hydrostatic seepage outlet,
    whose cell/face elevation mismatches swamp the ~100 Pa dynamic pressure
    drop at the paper's rate (outlet DFN cells accumulated mass)."""
    def sub(a, b):
        nonlocal s
        assert a in s, a[:50]
        s = s.replace(a, b, 1)
    sub("GRID\n  TYPE unstructured_explicit full_mesh_vol_area.uge\nEND",
        "GRID\n  TYPE unstructured_explicit full_mesh_vol_area.uge\n  GRAVITY 0.d0 0.d0 0.d0\nEND")
    sub(f"""FLOW_CONDITION initial
  TYPE
    LIQUID_PRESSURE HYDROSTATIC
  /
  DATUM 0.d0 0.d0 0.d0
  LIQUID_PRESSURE {P_SEEPAGE:.6e}
END""", f"""FLOW_CONDITION initial
  TYPE
    LIQUID_PRESSURE DIRICHLET
  /
  LIQUID_PRESSURE {P_SEEPAGE:.6e}
END

FLOW_CONDITION extraction
  TYPE
    RATE SCALED_VOLUMETRIC_RATE PERM
  /
  RATE {-rate:.6e} m^3/y
END""")
    sub(f"""FLOW_CONDITION boundaries
  TYPE
    LIQUID_PRESSURE SEEPAGE
  /
  DATUM 0.d0 0.d0 0.d0
  LIQUID_PRESSURE {P_SEEPAGE:.6e}
END""", f"""FLOW_CONDITION pinned
  TYPE
    LIQUID_PRESSURE DIRICHLET
  /
  LIQUID_PRESSURE {P_SEEPAGE:.6e}
END""")
    sub("""BOUNDARY_CONDITION outflow
  FLOW_CONDITION boundaries
  TRANSPORT_CONDITION seepage_face
  REGION outflow
/""", """SOURCE_SINK outflow
  FLOW_CONDITION extraction
  TRANSPORT_CONDITION seepage_face
  REGION outflow
END

BOUNDARY_CONDITION pinned
  FLOW_CONDITION pinned
  TRANSPORT_CONDITION initial
  REGION pinned
/""")
    sub("REGION outflow\n  FILE boundary_right_e.ex\nEND", "REGION outflow\n  FILE boundary_right_e.ex\nEND\n\nREGION pinned\n  FILE pinned.ex\nEND")
    return s


def main():
    global QUARTZ_VF0, MATERIAL_POROSITY
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="qtz")
    ap.add_argument("--uge", type=Path, required=True, help="reference-model UGE (inventory; same for all models)")
    ap.add_argument("--rate", type=float, default=None, help="m^3/y; default = reference network volume per year")
    ap.add_argument("--manifold-json", type=Path, required=True)
    ap.add_argument("--dissolved-fractions", type=float, nargs="+", default=[0.05, 0.15, 0.30, 0.45])
    ap.add_argument("--c-cap", type=float, default=C_CAP)
    ap.add_argument("--checkpoint-times", type=float, nargs="+", default=None,
                    help="checkpoint times (y) instead of dissolved fractions (reaction-limited quartz)")
    ap.add_argument("--dt", type=float, default=None, help="max time step (y); default 1e-3 x final time")
    ap.add_argument("--n-extra-vtk", type=int, default=8)
    ap.add_argument("--k-gypsum-mult", "--k-mult", dest="k_mult", type=float, default=1.0)
    ap.add_argument("--inert-boundary-x", type=float, nargs=2, default=None)
    ap.add_argument("--direct-transport", action="store_true")
    ap.add_argument("--dt-ramp", action="store_true", help="the paper's time-step schedule instead of one cap")
    ap.add_argument("--dt-cap", type=float, default=None, help="cap the ramp's maximum step (y)")
    ap.add_argument("--bc", choices=("seepage", "paper"), default="seepage",
                    help="paper: no gravity, perm-scaled extraction on the outflow cells, one pinned node")
    ap.add_argument("--quartz-vf0", type=float, default=QUARTZ_VF0, help="initial quartz volume fraction (porosity = 1 - this)")
    ap.add_argument("--material-porosity", type=float, default=MATERIAL_POROSITY,
                    help="reference porosity for UPDATE_PERMEABILITY; 1 - quartz-vf0 keeps k0 = dataset permeability")
    ap.add_argument("--perm-power", type=float, default=1.0, help="PERMEABILITY_POWER n, k ~ phi^n (3 = cubic law)")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    QUARTZ_VF0, MATERIAL_POROSITY = a.quartz_vf0, a.material_porosity
    cells, _ = read_uge(a.uge)
    V = float(cells[:, 4].sum())
    rate = a.rate or V
    inv = V * QUARTZ_VF0 / QUARTZ_MOLAR_VOLUME
    if a.checkpoint_times:
        t_chk = list(a.checkpoint_times)
        a.dissolved_fractions = [t * rate * a.c_cap / inv for t in t_chk]
    else:
        t_chk = [f * inv / (rate * a.c_cap) for f in a.dissolved_fractions]
    t_end = t_chk[-1]
    dt = a.dt or 1e-3 * t_end
    vtk_times = sorted(set(np.round(np.r_[t_chk, np.linspace(0, t_end, a.n_extra_vtk + 2)[1:-1]], 6)))
    box = json.loads(a.manifold_json.read_text())["region_box"]
    s = deck(rate, box, t_end, vtk_times, t_chk, dt, a.k_mult, a.direct_transport, a.dt_ramp, a.bc, a.dt_cap)
    if a.bc == "paper":                    # pin the pressure at the first outflow face
        lines = (a.out.parent / "boundary_right_e.ex").read_text().splitlines()
        (a.out.parent / "pinned.ex").write_text("CONNECTIONS\t1\n" + lines[1] + "\n")
    if a.inert_boundary_x is not None:
        s = inert_graph_boundary_cells(s, *a.inert_boundary_x)
    from deck_heterogeneity import set_material
    s = set_material(s, None, a.perm_power)
    a.out.write_text(s)
    pv0 = V * (1 - QUARTZ_VF0)
    sched = dict(mode="qtz", mineral="Quartz", vf0=QUARTZ_VF0, rate_m3y=rate, mineral_inventory_mol=inv, c_cap=a.c_cap,
                 pore_volume0_m3=pv0, material_porosity=MATERIAL_POROSITY, k_mult=a.k_mult, dt_max_y=dt, final_time_y=t_end,
                 checkpoints=[dict(tau_d=f, t_y=t, tau_pv=t * rate / pv0, vtk_index=1 + vtk_times.index(round(t, 6)))
                              for f, t in zip(a.dissolved_fractions, t_chk)],
                 vtk_times_y=vtk_times)
    Path(str(a.out) + ".schedule.json").write_text(json.dumps(sched, indent=1))
    print(json.dumps({k: v for k, v in sched.items() if k != "vtk_times_y"}, indent=1))


if __name__ == "__main__":
    main()
