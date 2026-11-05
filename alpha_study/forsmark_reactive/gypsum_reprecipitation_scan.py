#!/usr/bin/env python3
"""
Gypsum re-precipitation check (5 Nov 2026): per run, over every saved fracture state (paraview/<net>__<run>/fractures_KKK.vtu),
  max_gyp_vf        largest gypsum volume fraction in any fracture cell (initial fill vf0 = 1 - material porosity)
  n_gyp_up          most fracture cells at once with gypsum VF > vf0 + 0.001 (net gypsum gain)
  n_floor           most fracture cells at once with solids (gypsum + calcite) >= 0.999 (porosity at the 1e-3 floor)
  n_floor_ever      fracture cells that reach the floor at any saved state
  q_floor_max       largest share of the injected flow through floor cells at any saved state
  n_vf_gt1          most fracture cells at once with solids > 1 (more solid than cell volume: not physical)
  -> phase1/gypsum_reprecipitation.csv      python3 forsmark_reactive/gypsum_reprecipitation_scan.py
"""
import re, sys
from multiprocessing import Pool
from pathlib import Path
import numpy as np, pandas as pd
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent), str(HERE.parent / "physics_upscaling")]
from analyze_phase1_mechanism import read_vtu, PV  # noqa: E402
PHI = {"phase1": 0.1, "phase2_phi005": 0.05, "phase2_co3lo": 0.1, "phase3_phi0182": 0.182, "phase3_rate01": 0.1, "phase3_rate10": 0.1}

def one(d):
    m = re.match(r"L2_r15_p([\d.]+)_sg([\d.]+)_seed(\d+)__(gypsum(?:_calcite)?)__uncorrected_graph__(\w+)", d.name)
    if not m or m[5] not in PHI: return None
    vf0 = 1 - PHI[m[5]]; r = dict(p32=float(m[1]), sigma=float(m[2]), seed=int(m[3]), mode=m[4], tag=m[5], max_gyp_vf=0.0,
          n_gyp_up=0, n_floor=0, q_floor_max=0.0, n_vf_gt1=0, n_states=0)
    ever = None
    for f in sorted(d.glob("fractures_*.vtu")):
        a = read_vtu(f); g = a["Gypsum_VF"].astype(float); c = a["Calcite_VF"].astype(float) if "Calcite_VF" in a else 0 * g
        q = np.abs(a["Q_frac"]).astype(float); s = g + c; fl = s >= 0.999
        ever = fl if ever is None else ever | fl
        r["max_gyp_vf"] = max(r["max_gyp_vf"], float(g.max())); r["n_gyp_up"] = max(r["n_gyp_up"], int((g > vf0 + 1e-3).sum()))
        r["n_floor"] = max(r["n_floor"], int(fl.sum())); r["n_vf_gt1"] = max(r["n_vf_gt1"], int((s > 1.0 + 1e-6).sum()))
        r["q_floor_max"] = max(r["q_floor_max"], float(q[fl].sum() / q.sum()) if q.sum() > 0 else 0.0); r["n_states"] += 1
    r["n_floor_ever"] = int(ever.sum()) if ever is not None else 0; r["n_frac"] = int(len(ever)) if ever is not None else 0
    return r

if __name__ == "__main__":
    ds = sorted(p for p in PV.glob("L2_r15_*__gyp*") if p.is_dir())
    with Pool(6) as p: rows = [r for r in p.map(one, ds) if r]
    D = pd.DataFrame(rows).sort_values(["tag", "mode", "p32", "sigma", "seed"]); D.to_csv(HERE / "phase1/gypsum_reprecipitation.csv", index=False)
    g = D.groupby(["tag", "mode"]).agg(n=("seed", "size"), runs_gyp_up=("n_gyp_up", lambda x: (x > 0).sum()), runs_floor=("n_floor", lambda x: (x > 0).sum()),
        runs_vf_gt1=("n_vf_gt1", lambda x: (x > 0).sum()), max_gyp_vf=("max_gyp_vf", "max"), med_n_gyp_up=("n_gyp_up", "median"),
        max_n_floor=("n_floor_ever", "max"), max_q_floor=("q_floor_max", "max"))
    print(g.to_string())
