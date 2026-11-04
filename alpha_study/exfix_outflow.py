#!/usr/bin/env python3
"""Track H2 (1 Nov 2026): outflow-face conductance fix, applied to the COPY of boundary_right_e.ex inside a run folder
(never to a model_* folder).  Track H found the seed 4221 DFN outflow faces (10 m^2 at 1e-4 m from the cell centre)
quantise the outflow at the Hyman rate; face area 1e-6 m^2 fixes it (findings 2026-11-01_1015_trackH_hyman_fix.md).
  --area A            every outflow face gets area A (m^2); the DFN fix is --area 1e-6
  --area-per-dist R   face area = R x (distance from the cell centre to the face, m): the same face conductance
                      per unit permeability, A/d, for every face.  R = 1e-2 m reproduces the DFN fix (1e-6 m^2 at 1e-4 m)
                      on graph meshes whose outflow cells sit 2e-4 ... 0.29 m from the face.
Writes RUN/boundary_right_e.ex in place (same format as hyfix: id x y z area, tab separated) and RUN/exfix.json.
usage: exfix_outflow.py RUN_DIR (--area A | --area-per-dist R)"""
import argparse, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent / "physics_upscaling"))
from write_corrected_bigrafv_inputs import read_uge  # noqa: E402

ap = argparse.ArgumentParser(); ap.add_argument("run")
g = ap.add_mutually_exclusive_group(required=True); g.add_argument("--area", type=float); g.add_argument("--area-per-dist", type=float)
a = ap.parse_args()
rd = Path(a.run); p = rd / "boundary_right_e.ex"
if rd.resolve().name.startswith("model_"):
    sys.exit("refusing to edit a model_* folder")
c, _ = read_uge(rd / "full_mesh_vol_area.uge"); xyz = {int(r[0]): r[1:4] for r in c}
L = [l for l in p.read_text().splitlines() if l.strip()]
out, rows = [L[0]], []
for l in L[1:]:
    s = l.split(); i = int(s[0]); f = np.array([float(v) for v in s[1:4]])
    d = float(np.linalg.norm(f - xyz[i])); new = a.area if a.area is not None else a.area_per_dist * d
    out.append("\t".join(s[:4] + ["%.12e" % new])); rows.append(dict(cell=i, dist_m=d, area_old=float(s[4]), area_new=new))
p.write_text("\n".join(out) + "\n")
json.dump(dict(rule=("area %g" % a.area) if a.area is not None else ("area_per_dist %g" % a.area_per_dist), faces=rows),
          open(rd / "exfix.json", "w"), indent=1)
print(f"{p}: {len(rows)} faces, area {min(r['area_new'] for r in rows):.3g} ... {max(r['area_new'] for r in rows):.3g} m2")
