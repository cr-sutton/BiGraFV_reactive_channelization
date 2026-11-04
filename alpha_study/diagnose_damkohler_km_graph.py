#!/usr/bin/env python3
"""
Per-fracture Damkohler numbers of a graph-only reactive run directory, from a
direct TPFA flow solve on its initial permeability (analyze_km_dissolution_patterns.solve):
Da_f = k a V_f / (Q_f c_ref), constants of diagnose_damkohler_per_fracture.py for
gypsum and of deck_acid_calcite.py for calcite (acid, linearised at the
injected H+ activity of pH 1.5).

  python3 diagnose_damkohler_km_graph.py RUN_DIR [RUN_DIR ...]
"""
import json
import sys
from pathlib import Path

import h5py
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE / "physics_upscaling")]
from diagnose_damkohler_per_fracture import K_GYP, RHO_GYP, SSA_GYP, throughflow  # noqa: E402
from analyze_km_dissolution_patterns import read_polygons, solve  # noqa: E402
from compute_keff_tpfa import read_uge  # noqa: E402

C_GYP = 16.6
K_ACID_PH15 = 0.5012 * 10 ** -1.5          # far-from-equilibrium acid mechanism at a(H+) = 10^-1.5
A_CAL = 100.0 * 2710.0 * 0.77              # m^2/m^3 bulk: 100 m^2/kg x rho_calcite x VF0
C_ACID = 22.88


def main():
    for run in map(Path, sys.argv[1:]):
        sched = json.loads((run / "single_stage.in.schedule.json").read_text())
        nf = len(read_polygons(run / "polygons.dat"))
        cells, conns = read_uge(run / "full_mesh_vol_area.uge")
        with h5py.File(run / "dfn_properties.h5") as h:
            ids = np.asarray(h["Cell Ids"]).astype(int)
            k = np.full(len(cells), np.nan)
            k[ids - 1] = np.asarray(h["Permeability"], float)
        k[np.isnan(k)] = np.nanmax(k)
        rate = sched["rate_m3y"] / 3.15576e7
        _, flux, ci, cj = solve(run, cells, conns, k, rate)
        own = np.zeros(len(cells), int)
        own[:nf] = np.arange(1, nf + 1)
        own[nf:] = -np.arange(1, len(cells) - nf + 1)
        Qf = throughflow(ci, cj, flux, own)
        Q = np.array([Qf.get(f, 0.0) for f in range(1, nf + 1)])
        V = cells[:nf, 4]
        mult = sched.get("k_gypsum_mult", 1.0) if sched.get("mineral", "Gypsum") == "Gypsum" else sched.get("k_mult", 1.0)
        mineral = sched.get("mineral", "Gypsum")
        if mineral == "Gypsum":
            Da = K_GYP * mult * SSA_GYP * RHO_GYP * 0.77 * V / (Q * C_GYP)
        elif mineral == "Quartz":                   # quartz paper: k 1e-12, 0.0225 m^2/g, rho 2.65e6 g/m^3, c_ref 0.1 mol/m^3
            Da = 1e-12 * mult * 0.0225 * 2.65e6 * sched.get("vf0", 0.99) * V / (Q * 0.1)
        else:
            Da = K_ACID_PH15 * mult * A_CAL * V / (Q * C_ACID)
        fl = Q > 1e-3 * rate
        p = np.percentile(Da[fl], [10, 50, 90])
        out = dict(run=str(run), n_flowing=int(fl.sum()), Da_p10=p[0], Da_median=p[1], Da_p90=p[2])
        (run / "damkohler.json").write_text(json.dumps(out, indent=1))
        print(json.dumps(out))


if __name__ == "__main__":
    main()
