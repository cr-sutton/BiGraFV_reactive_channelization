#!/usr/bin/env python3
"""
Single-stage, rate-controlled acid injection into calcite-filled fractures
(mode "acid"): dilute HCl dissolves calcite, CaCO3 + 2H+ -> Ca++ + CO2(aq) + H2O.

Built from the gypsum-only single-stage deck (deck_gypsum_calcite.py, same
grid, flow, boundaries, output, inlet manifold and inert graph boundary
cells) by replacing the chemistry block and the four constraints, so the two
chemistries differ only in the reaction.

Chemistry (sources in docs/weekend_literature_log.md):
  calcite kinetics   TST with two parallel mechanisms (Palandri & Kharaka
                     2004 compilation, after Plummer, Wigley & Parkhurst 1978):
                       acid     k = 10^-0.30 mol/m^2/s x a(H+)^1.0
                       neutral  k = 10^-5.81 mol/m^2/s
                     area: 100 m^2/kg (order of BET areas of crushed calcite),
                     scaled by (VF/VF0)^(2/3) as for gypsum
  fill               calcite VF0 = 0.77 (same initial porosity 0.23 as the
                     gypsum runs, so permeability evolves on the same law)
  resident water     pH 8, 2 mM carbonate, calcite-saturated, Na+ by charge
  injected water     HCl at pH 1.5 (Cl- by charge balance, ~38 mM), 1 mM Na+
  capacity c_cap     22.9 mmol/kg = 22.88 mol/m^3 calcite per m^3 injected
                     (PFLOTRAN batch: injected water + calcite to equilibrium,
                     closed to CO2; scratch acid_batch/b_1.5.in)
  acid capacity      gamma = c_HCl / (nu c_sol) = 37.6 / (2 x 27076) = 7e-4 << 1,
  number             the quasi-steady regime assumed by Szymczak & Ladd 2012 and
                     Szawello et al. 2026

Mode "co2cal" (same deck, different injection water): water equilibrated with
CO2(g) at 1 bar (PFLOTRAN constraint CO3-- 1.0 G CO2(g), H+ by charge balance;
pH 3.91, total carbonate 34.1 mM), 1 mM NaCl, no calcium.  A third Palandri &
Kharaka (2004) calcite mechanism is added, the carbonate (CO2) mechanism
log k = -3.48 with n(P_CO2) = 1.0, written on CO2(aq) activity through Henry's
law (a_CO2(aq) = K_H P_CO2, log K_H = -1.47 at 25 C): k = 10^(-3.48 + 1.47) =
9.77e-3 mol/m^2/s.  Capacity 8.40 mol calcite per m^3 injected (PFLOTRAN batch,
closed system, scratch co2_batch/batch.in: pH 3.91 -> 6.07, Ca 8.40 mM).
Mode "acid" keeps the HCl water and the two mechanisms exactly as before.

--k-mult scales the rate constants (Da sweep), as --k-gypsum-mult does for
gypsum.  All other arguments are those of deck_gypsum_calcite.py.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CALCITE_VF0 = 0.77
CALCITE_MOLAR_VOLUME = 36.934e-6          # m^3/mol, hanford.dat
GYPSUM_VF0, GYPSUM_MOLAR_VOLUME = 0.77, 74.69e-6
C_CAP_ACID = 22.88                        # mol calcite / m^3 injected (batch equilibrium)
K_ACID, K_NEUTRAL = 0.5012, 1.549e-6      # mol/m^2/s
K_CARB = 9.772372e-3                      # mol/m^2/s per unit a(CO2(aq)): P&K carbonate mechanism via Henry's law
C_CAP_CO2 = 8.40                          # mol calcite / m^3 injected (batch, pCO2 1 bar, closed)
SSA = 100.0                               # m^2/kg

CHEMISTRY = """CHEMISTRY
  PRIMARY_SPECIES
    H+
    CO3--
    Ca++
    Na+
    Cl-
  /
  SECONDARY_SPECIES
    OH-
    HCO3-
    CO2(aq)
    CaCO3(aq)
    CaHCO3+
    CaOH+
    CaCl+
    CaCl2(aq)
    HCl(aq)
    NaCl(aq)
    NaCO3-
    NaHCO3(aq)
    NaOH(aq)
  /
  PASSIVE_GAS_SPECIES
    CO2(g)
  /
  MINERALS
    Calcite
  /
  MINERAL_KINETICS
    Calcite
      SURFACE_AREA_FUNCTION VOLUME_FRACTION_RATIO
      SURFACE_AREA_VOL_FRAC_POWER 0.6667
      PREFACTOR
        RATE_CONSTANT {ka:.6e} mol/m^2-sec
        PREFACTOR_SPECIES H+
          ALPHA 1.0
        /
      /
      PREFACTOR
        RATE_CONSTANT {kn:.6e} mol/m^2-sec
      /
{carb}    /
  /
  DATABASE /Users/collin/src/pflotran/database/hanford.dat
  LOG_FORMULATION
  ACTIVITY_COEFFICIENTS TIMESTEP
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
RESIDENT = ("    H+     8.d0   pH\n    CO3--  2.d-3  T\n    Ca++   1.d-3  M Calcite\n"
            "    Na+    1.d-3  Z\n    Cl-    1.d-3  T\n")
INJECTION = ("    H+     1.5d0  pH\n    CO3--  1.d-10 T\n    Ca++   1.d-10 T\n"
             "    Na+    1.d-3  T\n    Cl-    3.d-2  Z\n")
INJECTION_CO2 = ("    H+     4.d0   Z\n    CO3--  1.d0   G CO2(g)\n    Ca++   1.d-10 T\n"
                 "    Na+    1.d-3  T\n    Cl-    1.d-3  T\n")
CARB_PREFACTOR = """      PREFACTOR
        RATE_CONSTANT {kc:.6e} mol/m^2-sec
        PREFACTOR_SPECIES CO2(aq)
          ALPHA 1.0
        /
      /
"""
CONSTRAINTS = """CONSTRAINT initial
  CONCENTRATIONS
{RESIDENT}  /
  MINERALS
    Calcite  {VF0}d0  {SSA}  m^2/kg
  /
 EQUILIBRATE_AT_EACH_CELL
END


CONSTRAINT well_initial
  CONCENTRATIONS
{RESIDENT}  /
  MINERALS
    Calcite  0.d0  {SSA}  m^2/kg
  /
  ACKNOWLEDGE_ZERO_SURFACE_AREA
END
CONSTRAINT w0
  CONCENTRATIONS
{RESIDENT}  /
END

CONSTRAINT injection
  CONCENTRATIONS
{INJECTION}  /
END

"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="acid")
    ap.add_argument("--uge", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--c-cap", type=float, default=None)
    ap.add_argument("--k-mult", type=float, default=1.0)
    a, rest = ap.parse_known_args()
    co2 = a.mode == "co2cal"
    if a.c_cap is None:
        a.c_cap = C_CAP_CO2 if co2 else C_CAP_ACID
    # the gypsum deck sets checkpoint times from its own inventory and capacity:
    # rescale the capacity so the same fractions land at calcite's times
    inv_ratio = (GYPSUM_VF0 / GYPSUM_MOLAR_VOLUME) / (CALCITE_VF0 / CALCITE_MOLAR_VOLUME)
    cmd = [sys.executable, str(HERE / "deck_gypsum_calcite.py"), "--mode", "gyponly", "--uge", str(a.uge),
           "--out", str(a.out), "--c-cap", f"{a.c_cap * inv_ratio:.10g}", *rest]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
    s = a.out.read_text()
    s, n = re.subn(r"^CHEMISTRY\n.*?(?=^#=========================== discretization)",
                   CHEMISTRY.format(ka=K_ACID * a.k_mult, kn=K_NEUTRAL * a.k_mult,
                                    carb=CARB_PREFACTOR.format(kc=K_CARB * a.k_mult) if co2 else ""),
                   s, count=1, flags=re.S | re.M)
    assert n == 1, "chemistry block not found"
    cons = CONSTRAINTS.replace("{RESIDENT}", RESIDENT).replace("{INJECTION}", INJECTION_CO2 if co2 else INJECTION)
    cons = cons.replace("{VF0}", str(CALCITE_VF0)).replace("{SSA}", f"{SSA:g}")
    s, n = re.subn(r"^CONSTRAINT initial\n.*?(?=^#=========================== flow conditions)", lambda m: cons, s,
                   count=1, flags=re.S | re.M)
    assert n == 1, "constraints not found"
    assert "Gypsum" not in s and "SO4" not in s, "gypsum left in acid deck"
    a.out.write_text(s)
    sp = Path(str(a.out) + ".schedule.json")
    sched = json.loads(sp.read_text())
    sched.pop("gypsum_inventory_mol", None)
    sched.update(mode=a.mode, mineral="Calcite", vf0=CALCITE_VF0, c_cap=a.c_cap, k_mult=a.k_mult,
                 mineral_inventory_mol=None,
                 injection="CO2-charged water, pCO2 1 bar (pH 3.91)" if co2 else "HCl pH 1.5")
    from write_corrected_bigrafv_inputs import read_uge  # noqa: E402
    cells, _ = read_uge(a.uge)
    sched["mineral_inventory_mol"] = float(cells[:, 4].sum()) * CALCITE_VF0 / CALCITE_MOLAR_VOLUME
    sp.write_text(json.dumps(sched, indent=1))
    print(json.dumps({k: v for k, v in sched.items() if k != "vtk_times_y"}, indent=1))


if __name__ == "__main__":
    sys.path.insert(0, str(HERE / "physics_upscaling"))
    main()
