#!/usr/bin/env python3
"""
Repair NaN Voronoi volumes / areas that LaGriT writes for a few degenerate cells of an rFram mesh (5 Nov 2026: 2 of 758,183
cells and the 1 connection between them on rf_p4.0_sg1.0_seed1).  A NaN cell volume is replaced by the median volume of its
mesh neighbours; a NaN connection area is set to 0 (no flux across that face).  Originals are kept as *.uge.orig and every
change is listed in uge_repair.json.  Applied to full_mesh_vol_area.uge (PFLOTRAN grid) and full_mesh.uge.

  python3 forsmark_reactive/dfn_validation/repair_uge_nan.py MODEL_DFN_DIR
"""
import json
import shutil
import sys
from pathlib import Path

import numpy as np


def repair(f):
    lines = f.read_text().splitlines()
    nc = int(lines[0].split()[1])
    cells = lines[1:1 + nc]
    hdr = 1 + nc
    ncon = int(lines[hdr].split()[1])
    cons = lines[hdr + 1:hdr + 1 + ncon]
    vol = np.array([float(l.split()[4]) for l in cells])
    bad_c = np.where(~np.isfinite(vol))[0]
    ij = np.array([[int(t) for t in l.split()[:2]] for l in cons]) - 1
    area = np.array([float(l.split()[5]) for l in cons])
    bad_e = np.where(~np.isfinite(area))[0]
    log = dict(file=f.name, cells=[], connections=[])
    for c in bad_c:
        nb = np.concatenate([ij[ij[:, 0] == c, 1], ij[ij[:, 1] == c, 0]])
        v = np.nanmedian(vol[nb][np.isfinite(vol[nb])])
        t = cells[c].split()
        log["cells"].append(dict(id=int(t[0]), new_volume=float(v), n_neighbours=int(len(nb))))
        cells[c] = "\t".join(t[:4] + [f"{v:.12e}"])
    for e in bad_e:
        t = cons[e].split()
        log["connections"].append(dict(i=int(t[0]), j=int(t[1]), new_area=0.0))
        cons[e] = "\t".join(t[:5] + ["0.0"])
    if len(bad_c) or len(bad_e):
        shutil.copy(f, f.with_suffix(".uge.orig"))
        f.write_text("\n".join([lines[0]] + cells + [lines[hdr]] + cons + lines[hdr + 1 + ncon:]) + "\n")
    log["total_volume"] = float(np.nansum(vol))
    return log


if __name__ == "__main__":
    d = Path(sys.argv[1])
    out = [repair(d / n) for n in ("full_mesh_vol_area.uge", "full_mesh.uge") if (d / n).exists()]
    (d / "uge_repair.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))
