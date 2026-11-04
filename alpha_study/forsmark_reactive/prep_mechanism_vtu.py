#!/usr/bin/env python3
"""
Per-fracture fields for the flow / pore-space visualisations: reads paraview/<net>__<run>/fractures_KKK.vtu and writes
paraview/<net>__<run>__mech/fractures_KKK.vtu with extra cell data
  porosity        1 - gypsum VF - calcite VF
  log10_Q         log10 of the fracture's share of the injected flow (floored at 1e-8)
  log10_pore      log10 of the fracture's share of the open pore volume (fracture volume x porosity)
  mismatch        log10(flow share / pore share): > 0 the fracture carries more flow than its share of open space
                  (water crossing undissolved rock), < 0 open space that carries little flow
and a states.csv (k, t_y, pv, t_cap, tau_H) for labelling frames.

  python3 forsmark_reactive/prep_mechanism_vtu.py RUN_DIR [RUN_DIR ...]
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import vtk
from vtk.util.numpy_support import numpy_to_vtk, vtk_to_numpy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT / "physics_upscaling")]
from time_axes import clocks  # noqa: E402
from write_corrected_bigrafv_inputs import read_uge  # noqa: E402


def add(grid, name, arr):
    a = numpy_to_vtk(np.ascontiguousarray(arr, dtype=np.float64), deep=True)
    a.SetName(name)
    grid.GetCellData().AddArray(a)


def main(run):
    run = Path(run).resolve()
    src = ROOT / "paraview" / f"{run.parent.name}__{run.name}"
    dst = ROOT / "paraview" / f"{run.parent.name}__{run.name}__mech"
    dst.mkdir(exist_ok=True)
    pat = pd.read_csv(run / "patterns.csv").set_index("k")
    c = clocks(run)
    cells, _ = read_uge(run / "full_mesh_vol_area.uge")
    rows = []
    for f in sorted(src.glob("fractures_*.vtu")):
        k = int(f.stem.split("_")[1])
        if k not in pat.index:
            continue
        r = vtk.vtkXMLUnstructuredGridReader(); r.SetFileName(str(f)); r.Update()
        g = r.GetOutput()
        cd = g.GetCellData()
        get = lambda n: vtk_to_numpy(cd.GetArray(n)).astype(float) if cd.HasArray(n) else None
        q = np.abs(get("Q_frac"))
        nf = len(q)
        vf = get("Gypsum_VF") + (get("Calcite_VF") if get("Calcite_VF") is not None else 0.0)
        phi = np.clip(1 - vf, 1e-6, 1)
        pore = cells[:nf, 4] * phi
        qs, ps = q / q.sum(), pore / pore.sum()
        add(g, "porosity", phi)
        add(g, "log10_Q", np.log10(np.maximum(qs, 1e-8)))
        add(g, "log10_pore", np.log10(np.maximum(ps, 1e-8)))
        add(g, "mismatch", np.log10(np.maximum(qs, 1e-10) / np.maximum(ps, 1e-10)))
        w = vtk.vtkXMLUnstructuredGridWriter(); w.SetFileName(str(dst / f.name)); w.SetInputData(g); w.Write()
        t = pat.loc[k, "t_y"]
        rows.append(dict(k=k, t_y=t, pv=float(c.pv(t)), t_cap=float(c.t_cap(t)), tau_H=float(c.tau_H(t)), dissolved=pat.loc[k, "dissolved"]))
    pd.DataFrame(rows).to_csv(dst / "states.csv", index=False)
    print(dst, len(rows))


if __name__ == "__main__":
    for a in sys.argv[1:]:
        main(a)
