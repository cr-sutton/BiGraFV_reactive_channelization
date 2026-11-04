"""
The three clocks used for the Forsmark runs, for any run directory (gyponly or gypcal, any porosity or carbonate):

  diss   fraction of the fracture cells' gypsum dissolved (patterns.csv, VTK states): the MAIN clock of the report, i.e. capacity
         time with the measured instead of the theoretical cap (diss = t_cap x c_measured / c_cap)
  pv     pore volumes injected = t x rate / initial pore volume (= years at one pore volume per year)
  t_cap  capacity-normalised time = pv x c_cap / C_inv: the gypsum the injected water could have carried away if it left
         saturated, as a multiple of the inventory.  c_cap = 16.6 mol/m3 (gypsum solubility) + 1000 x injected carbonate
         (mol/L; each carbonate can take one Ca out as calcite).  C_inv = vf0 / ((1 - vf0) x V_gypsum), mol per m3 of pore.
  tau_H  dissolved volume / initial volume (Hyman, Szawełło, Kang & Szymczak 2026, Eq. 26: tau = Delta V / V0):
         the change in open pore volume over the initial pore volume, from PFLOTRAN's mineral totals,
         Delta V = (gypsum dissolved) V_gypsum - (calcite formed) V_calcite.

  from time_axes import clocks;  c = clocks(run_dir);  c.pv(t_y), c.t_cap(t_y), c.tau_H(t_y)
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

V_GYP, V_CAL = 74.69e-6, 36.934e-6          # m3/mol, hanford.dat
C_SAT = 16.6                               # mol/m3, gypsum in dilute water


class clocks:
    def __init__(self, run: Path):
        run = Path(run)
        s = json.loads((run / "single_stage.in.schedule.json").read_text())
        self.vf0 = float(s["vf0"])
        self.pv0 = float(s["pore_volume0_m3"])
        self.rate = float(s["rate_m3y"])
        co3 = float(s.get("inj_co3_M", 0.1)) if "calcite" in run.name else 0.0     # 0.1 M = template brine if unset
        self.c_cap = C_SAT + 1000.0 * co3
        self.c_inv = self.vf0 / ((1 - self.vf0) * V_GYP)
        hdr = [c.strip().strip('"') for c in (run / "single_stage-mas.dat").open().readline().split('",')]
        d = np.genfromtxt(run / "single_stage-mas.dat", skip_header=1, invalid_raise=False)
        gi = hdr.index("Region All Gypsum Total Mass [mol]")
        ci = hdr.index("Region All Calcite Total Mass [mol]") if "Region All Calcite Total Mass [mol]" in hdr else None
        self._t = d[:, 0]
        dv = (d[0, gi] - d[:, gi]) * V_GYP - (d[:, ci] * V_CAL if ci is not None else 0.0)
        self._tau = dv / self.pv0
        # fraction of the FRACTURE-cell gypsum dissolved (patterns.csv, from the VTK states; the same definition as
        # 'dissolved' in phase1_mechanism.csv).  The mass-balance region also holds ~1 % of the gypsum in inert boundary
        # helper cells that never reacts, so (g0 - g)/g0 would be ~1 % low; fall back to it only without patterns.csv.
        pat = run / "patterns.csv"
        if pat.exists():
            import pandas as pd
            pp = pd.read_csv(pat).dropna(subset=["t_y"]).sort_values("t_y")
            self._dt, self._dd = pp.t_y.to_numpy(float), pp.dissolved.to_numpy(float)
        else:
            self._dt, self._dd = self._t, (d[0, gi] - d[:, gi]) / d[0, gi]

    def pv(self, t_y):
        return np.asarray(t_y, float) * self.rate / self.pv0

    def t_cap(self, t_y):
        return self.pv(t_y) * self.c_cap / self.c_inv

    def diss(self, t_y):
        return np.interp(np.asarray(t_y, float), self._dt, self._dd)

    def tau_H(self, t_y):
        return np.interp(np.asarray(t_y, float), self._t, self._tau)
