#!/usr/bin/env python3
"""Clogging summary of the olivine run, per saved state -> RUN/clogging.csv: fracture-volume-weighted mean porosity,
min porosity, number of fractures below porosity 0.05 / 0.01 / 1.1e-3 (the floor is 1e-3), magnesite and chalcedony
volume, and (from patterns.csv / channelization.csv) k_eff ratio, n90 and inheritance overlap0.
  python3 forsmark_reactive/explore_olivine/clogging_summary.py RUN_DIR"""
import sys, json
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "physics_upscaling")]
from bipartite_pressure_solutions_functions import read_scalar_from_vtk  # noqa: E402
from write_corrected_bigrafv_inputs import read_uge  # noqa: E402
run = Path(sys.argv[1])
sched = json.loads((run / "single_stage.in.schedule.json").read_text())
nf = sum(1 for _ in open(run / "polygons.dat")) - 1
vol = read_uge(run / "full_mesh_vol_area.uge")[0][:nf, 4]
times = [0.0] + sched["vtk_times_y"]
rows = []
for f in sorted(run.glob("single_stage-*.vtk"), key=lambda p: int(p.stem.split("-")[1])):
    k = int(f.stem.split("-")[1]); g = lambda n: np.asarray(read_scalar_from_vtk(str(f), n), float)[:nf]
    phi = g("Porosity")
    rows.append(dict(k=k, t_y=times[k] if k < len(times) else np.nan, phi_mean=float((phi * vol).sum() / vol.sum()), phi_min=float(phi.min()),
                     n_below_0p05=int((phi < 0.05).sum()), n_below_0p01=int((phi < 0.01).sum()), n_at_floor=int((phi < 1.1e-3).sum()),
                     magnesite_vol=float((g("Magnesite_VF") * vol).sum()), chalcedony_vol=float((g("Chalcedony_VF") * vol).sum())))
d = pd.DataFrame(rows)
for name, cols in (("patterns.csv", ["k", "k_eff_ratio", "dissolved"]), ("channelization.csv", ["k", "n90", "overlap0", "pr_fracture_vol"])):
    if (run / name).exists():
        d = d.merge(pd.read_csv(run / name)[cols], on="k", how="left")
d.to_csv(run / "clogging.csv", index=False)
print(d.iloc[:: max(1, len(d) // 12)].round(4).to_string(index=False))
