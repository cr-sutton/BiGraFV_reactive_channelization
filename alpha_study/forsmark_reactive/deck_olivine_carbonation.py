#!/usr/bin/env python3
"""
Exploratory olivine-carbonation deck (one run, 4 Nov 2026): CO2-charged water injected at a fixed volumetric rate (one
network pore volume per year) into forsterite-filled fractures, Mg2SiO4 + 2 CO2 -> 2 MgCO3 + SiO2.  Unlike gypsum ->
calcite (solids shrink to 0.49), the products occupy more volume than the forsterite they replace (hanford.dat molar
volumes: +80 % with chalcedony), so a well-mixed BiGraFV cell can lose porosity and clog.  Question: does clogging re-route
the flow in the one-cell model?

Built by text edits of an existing Forsmark coupled deck of the same network (regions, helper cells, Dirichlet outflow,
outflow-face fix, inlet manifold and rate are kept); only the chemistry, constraints, temperature and output times change.
Parameters and sources: forsmark_reactive/lit/lit_olivine_carbonation.md.
  - 185 C (Kelemen & Matter 2008 optimum), REFERENCE_TEMPERATURE; hanford.dat log K interpolated (grid 150/200 C).
  - injected water: 1.0 mol/kg total carbonate (about 1.03-1.09 mol/kg CO2 at 150 bar, Duan & Sun 2003 port, UNVERIFIED
    +-5 %), pH 3.5 (estimate from the CO2(aq) log K at 185 C).
  - forsterite: Palandri & Kharaka 2004 Table 23, acid log k25 -6.85, E 67.2 kJ/mol, n(H+) 0.47; neutral -10.64, 79.0.
  - magnesite: P&K Table 33 neutral log k25 -9.34, E 23.5 (dissolution constants used both ways; gives 1.2e-8 mol/m2/s
    at 185 C, close to Steefel & Hu 2022's 1e-8).  Saldi et al. growth rates are slower (UNVERIFIED at 185 C).
  - chalcedony: P&K SiO2-polymorph precipitation log k25 -9.42, E 49.8.
  - surface areas: forsterite 1000 m2/m3 (Steefel & Hu 2022) scaled by volume fraction; magnesite and chalcedony fixed
    100 m2/m3 seed (Steefel & Hu magnesite; no silica seed value found).
  - fill: forsterite VF 0.9, porosity 0.1 (as the gypsum runs), k-phi n = 1, MINIMUM_POROSITY 1e-3,
    PERMEABILITY_MIN_SCALE_FACTOR 1e-6.
Not modelled: pressure (Richards, single-phase liquid at the run's pressure), CO2 as a separate phase, reaction-driven
cracking, serpentinisation.

  python3 forsmark_reactive/deck_olivine_carbonation.py SRC_RUN_DIR OUT_RUN_DIR [--t-end 300] [--dt 0.05] [--n-vtk 60]
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

import numpy as np

V_FO = 43.79e-6                  # m3/mol forsterite, hanford.dat
VF0, PHI0 = 0.9, 0.1
CO2_INJ = 1.0                    # mol/L total carbonate injected
C_CAP = 1000.0 * CO2_INJ / 2.0   # mol forsterite one m3 of injected water can carbonate (2 CO2 per Mg2SiO4)

CHEMISTRY = """CHEMISTRY
  PRIMARY_SPECIES
    H+
    HCO3-
    Mg++
    SiO2(aq)
  /
  SECONDARY_SPECIES
    OH-
    CO2(aq)
    CO3--
    MgCO3(aq)
    MgHCO3+
    MgOH+
    H3SiO4-
    H2SiO4--
  /
  PASSIVE_GAS_SPECIES
    CO2(g)
  /
  MINERALS
    Forsterite
    Magnesite
    Chalcedony
  /
  MINERAL_KINETICS
    Forsterite
      SURFACE_AREA_FUNCTION VOLUME_FRACTION_RATIO
      SURFACE_AREA_VOL_FRAC_POWER 0.6667
      PREFACTOR
        RATE_CONSTANT 1.4125d-7 mol/m^2-sec
        ACTIVATION_ENERGY 67.2d0 kJ/mol
        PREFACTOR_SPECIES H+
          ALPHA 0.47d0
        /
      /
      PREFACTOR
        RATE_CONSTANT 2.2909d-11 mol/m^2-sec
        ACTIVATION_ENERGY 79.0d0 kJ/mol
      /
    /
    Magnesite
      RATE_CONSTANT 4.5709d-10 mol/m^2-sec
      ACTIVATION_ENERGY 23.5d0 kJ/mol
    /
    Chalcedony
      RATE_CONSTANT 3.8019d-10 mol/m^2-sec
      ACTIVATION_ENERGY 49.8d0 kJ/mol
    /
  /
  DATABASE /Users/collin/src/pflotran/database/hanford.dat
  LOG_FORMULATION
  ACTIVITY_COEFFICIENTS TIMESTEP
  MINIMUM_POROSITY 1.0e-03
  UPDATE_POROSITY
  UPDATE_PERMEABILITY
  UPDATE_TORTUOSITY
  MOLAL
  OUTPUT
    PH
    TOTAL
    ALL
    MINERALS
    MINERAL_VOLUME_FRACTION
    MINERAL_SURFACE_AREA
    MINERAL_SATURATION_INDEX
  /
/
"""

RESIDENT = "    H+       8.d0     pH\n    HCO3-    1.d-4    T\n    Mg++     1.d-4    T\n    SiO2(aq) 1.d-4    T\n"
INJECTION = f"    H+       3.5d0    pH\n    HCO3-    {CO2_INJ:.4f}d0  T\n    Mg++     1.d-10   T\n    SiO2(aq) 1.d-10   T\n"
MINERALS_FRACTURE = (f"    Forsterite  {VF0:.2f}d0  1000.d0 m^2/m^3\n    Magnesite   0.d0  100.d0 m^2/m^3\n"
                     "    Chalcedony  0.d0  100.d0 m^2/m^3\n")
MINERALS_INERT = "    Forsterite  0.d0  0.d0 m^2/m^3\n    Magnesite   0.d0  0.d0 m^2/m^3\n    Chalcedony  0.d0  0.d0 m^2/m^3\n"


def constraint(name, conc, minerals=None, extra=""):
    s = f"CONSTRAINT {name}\n  CONCENTRATIONS\n{conc}  /\n"
    if minerals:
        s += f"  MINERALS\n{minerals}  /\n"
    return s + extra + "END\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", type=Path, help="existing Forsmark run dir of the same network (gypsum_calcite deck)")
    ap.add_argument("out", type=Path)
    ap.add_argument("--t-end", type=float, default=300.0, help="years (= network pore volumes at 1 PV/yr)")
    ap.add_argument("--dt", type=float, default=0.05, help="max time step (y)")
    ap.add_argument("--n-vtk", type=int, default=60)
    ap.add_argument("--temperature", type=float, default=185.0)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    for f in ("full_mesh_vol_area.uge", "boundary_left_w.ex", "boundary_right_e.ex", "dfn_properties.h5", "initial_pressure.h5",
              "inlet_manifold.json", "polygons.dat", "materialid.dat"):
        if (a.src / f).exists():
            shutil.copy(a.src / f, a.out / f)
    s = (a.src / "single_stage.in").read_text()
    src_sched = json.loads((a.src / "single_stage.in.schedule.json").read_text())

    def sub(pat, rep, flags=re.S | re.M):
        nonlocal s
        s, n = re.subn(pat, lambda m: rep, s, count=1, flags=flags)
        assert n == 1, f"edit failed: {pat[:60]}"

    sub(r"^CHEMISTRY\n.*?^/\n", CHEMISTRY)
    sub(r"^SUBSURFACE\n", f"SUBSURFACE\n\nREFERENCE_TEMPERATURE {a.temperature:.1f}d0\n")
    eq = " EQUILIBRATE_AT_EACH_CELL\n"
    sub(r"^CONSTRAINT initial\n.*?^END\n", constraint("initial", RESIDENT, MINERALS_FRACTURE, eq))
    sub(r"^CONSTRAINT well_initial\n.*?^END\n", constraint("well_initial", RESIDENT, MINERALS_INERT, "  ACKNOWLEDGE_ZERO_SURFACE_AREA\n"))
    if re.search(r"^CONSTRAINT well_fill\n", s, re.M):
        sub(r"^CONSTRAINT well_fill\n.*?^END\n", constraint("well_fill", INJECTION, MINERALS_INERT, "  ACKNOWLEDGE_ZERO_SURFACE_AREA\n"))
    sub(r"^CONSTRAINT w0\n.*?^END\n", constraint("w0", RESIDENT))
    sub(r"^CONSTRAINT injection\n.*?^END\n", constraint("injection", INJECTION))
    # output, checkpoint and time
    vtk = sorted(set(np.round(np.geomspace(a.t_end * 1e-4, a.t_end, a.n_vtk), 6)))
    chk = [t for t in (1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0) if t <= a.t_end]
    vtk = sorted(set(vtk) | set(chk))
    tt = [f"{t:.6e}" for t in vtk]
    times = " \\\n    ".join(" ".join(tt[i:i + 8]) for i in range(0, len(tt), 8))
    sub(r"^OUTPUT\n  TIMES y .*?(?=\n  [A-Z])", f"OUTPUT\n  TIMES y {times}")
    sub(r"^  CHECKPOINT\n    TIMES y [^\n]*\n", "  CHECKPOINT\n    TIMES y " + " ".join(f"{t:.6e}" for t in chk) + "\n")
    sub(r"^TIME\n.*?^END\n", f"TIME\n    INITIAL_TIMESTEP_SIZE 1.0e-8 y\n    MAXIMUM_TIMESTEP_SIZE {a.dt:.2e} y\n    FINAL_TIME {a.t_end:.6e} y\nEND\n")
    assert "Gypsum" not in s and "Calcite" not in s and "Ca++" not in s, "gypsum chemistry left in the deck"
    (a.out / "single_stage.in").write_text(s)
    inv = float(src_sched["gypsum_inventory_mol"]) * 74.69e-6 / V_FO       # same fill volume, forsterite moles
    sched = dict(mode="olivine", rate_m3y=src_sched["rate_m3y"], forsterite_inventory_mol=inv, gypsum_inventory_mol=inv,
                 c_cap=C_CAP, pore_volume0_m3=src_sched["pore_volume0_m3"], dt_max_y=a.dt, final_time_y=a.t_end,
                 mineral="Forsterite", vf0=VF0, material_porosity=PHI0, perm_power=1.0, fill_sigma=0.0, fill_seed=1,
                 temperature_C=a.temperature, inj_co2_M=CO2_INJ,
                 checkpoints=[dict(tau_d=float("nan"), t_y=t, tau_pv=t * src_sched["rate_m3y"] / src_sched["pore_volume0_m3"],
                                   vtk_index=1 + vtk.index(t)) for t in chk],
                 vtk_times_y=vtk, source_run=str(a.src))
    (a.out / "single_stage.in.schedule.json").write_text(json.dumps(sched, indent=1))
    print(json.dumps({k: v for k, v in sched.items() if k != "vtk_times_y"}, indent=1))


if __name__ == "__main__":
    main()
