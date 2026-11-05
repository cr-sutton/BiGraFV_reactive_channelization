#!/usr/bin/env python3
"""
Mechanism checks on the Phase 1 runs, from the per-fracture state files (paraview/<net>__<run>/fractures_KKK.vtu written by
analyze_km_dissolution_patterns.py: Q_frac = share of the injected flow through the fracture, Gypsum_VF, Calcite_VF,
x_center) and the fracture volumes (UGE, first n_fractures cells).

Per run and saved state -> phase1/phase1_mechanism.csv:
  pr_frac   (sum Q)^2 / sum(Q^2 / w), w = fracture volume share: flow focusing measured against the FRACTURE volume
            (same as pr_fracture_vol in channelization.csv)
  pr_pore   the same with w = open pore volume share (fracture volume x porosity, porosity = 1 - gypsum VF - calcite VF):
            flow focusing measured against where the open space is
  outlet_diss  flow-weighted dissolved fraction of the fractures whose centres lie in the last 100 m before the outlet
            (x > 400 m): the dissolution front reaching the outlet along the flowing paths
  front_x   flow-weighted mean x of the dissolution front: sum_f Q_f d_f x_f / sum_f Q_f d_f (d = fraction dissolved)

  python3 forsmark_reactive/analyze_phase1_mechanism.py   (multiprocessing, 4 workers)
"""
from __future__ import annotations

import glob
import re
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
import vtk
from vtk.util.numpy_support import vtk_to_numpy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT), str(ROOT / "physics_upscaling")]
from time_axes import clocks  # noqa: E402
from write_corrected_bigrafv_inputs import read_uge  # noqa: E402

P1 = HERE / "phase1"
PV = ROOT / "paraview"


def read_vtu(f):
    r = vtk.vtkXMLUnstructuredGridReader()
    r.SetFileName(str(f))
    r.Update()
    cd = r.GetOutput().GetCellData()
    return {cd.GetArrayName(i): vtk_to_numpy(cd.GetArray(i)) for i in range(cd.GetNumberOfArrays())}


def prw(q, w):
    w = w / w.sum()
    m = w > 0
    return float(q[m].sum() ** 2 / (q[m] ** 2 / w[m]).sum())


def one(run):
    run = Path(run)
    m = re.search(r"p([\d.]+)_sg([\d.]+)_seed(\d)", str(run))
    tag = run.name.split("__")[-1]
    mode = "gypcal" if "calcite" in run.name else "gyponly"
    pvdir = PV / f"{run.parent.name}__{run.name}"
    files = sorted(pvdir.glob("fractures_*.vtu"))
    if not files:
        return []
    pat = pd.read_csv(run / "patterns.csv").set_index("k")
    c = clocks(run)
    cells, _ = read_uge(run / "full_mesh_vol_area.uge")
    rows = []
    for f in files:
        k = int(f.stem.split("_")[1])
        if k not in pat.index:
            continue
        a = read_vtu(f)
        q = np.abs(a["Q_frac"]).astype(float)
        nf = len(q)
        vol = cells[:nf, 4]
        vf = a["Gypsum_VF"].astype(float) + (a["Calcite_VF"].astype(float) if "Calcite_VF" in a else 0.0)
        phi = np.clip(1 - vf, 1e-6, 1)
        d = a["fraction_dissolved"].astype(float)
        x = a["x_center"].astype(float)
        out = x > 400
        qd = q * d
        t = pat.loc[k, "t_y"]
        rows.append(dict(p32=float(m[1]), sigma=float(m[2]), seed=int(m[3]), mode=mode, tag=tag, k=k, t_y=t, pv=float(c.pv(t)),
                         t_cap=float(c.t_cap(t)), tau_H=float(c.tau_H(t)), pr_frac=prw(q, vol), pr_pore=prw(q, vol * phi),
                         outlet_diss=float((q[out] * d[out]).sum() / q[out].sum()) if q[out].sum() > 0 else np.nan,
                         front_x=float((qd * x).sum() / qd.sum()) if qd.sum() > 0 else np.nan, dissolved=pat.loc[k, "dissolved"]))
    return rows


def main():
    runs = sorted(r for t in ("phase1", "phase2_phi005", "phase2_co3lo", "phase3_phi0182", "phase3_rate01", "phase3_rate10") for r in glob.glob(str(P1 / f"L2_r15_p*_sg*_seed*/gyp*__{t}"))
                  if (Path(r) / "patterns.csv").exists())   # x16 included since 4 Nov; figures and tables filter p32
    with Pool(4) as p:
        rows = [r for rs in p.map(one, runs) for r in rs]
    df = pd.DataFrame(rows).sort_values(["tag", "mode", "p32", "sigma", "seed", "k"])
    df.to_csv(P1 / "phase1_mechanism.csv", index=False)
    # per run: when the fracture-volume and pore-volume focusing bottom out, and when the front reaches the outlet
    s = []
    for key, d in df.groupby(["tag", "mode", "p32", "sigma", "seed"]):
        d = d.reset_index(drop=True)
        i = d.pr_frac.idxmin()
        reach = d[d.outlet_diss >= 0.5]
        s.append(dict(zip(["tag", "mode", "p32", "sigma", "seed"], key), dissolved_at_outlet50=reach.dissolved.min() if len(reach) else np.nan, pr_frac_min_rel=d.pr_frac[i] / d.pr_frac[0],
                      pr_pore_at_that_rel=d.pr_pore[i] / d.pr_pore[0], pr_pore_min_rel=d.pr_pore.min() / d.pr_pore[0],
                      tcap_prmin=d.t_cap[i], tcap_outlet50=reach.t_cap.min() if len(reach) else np.nan,
                      outlet_diss_at_prmin=d.outlet_diss[i]))
    s = pd.DataFrame(s)
    s.to_csv(P1 / "phase1_mechanism_summary.csv", index=False)
    pd.set_option("display.width", 200)
    print(s[s.sigma == 1.0].groupby(["tag", "mode", "p32"])[["pr_frac_min_rel", "pr_pore_at_that_rel", "pr_pore_min_rel", "tcap_prmin",
                                     "tcap_outlet50", "dissolved_at_outlet50"]].median().round(3).to_string())


if __name__ == "__main__":
    main()
