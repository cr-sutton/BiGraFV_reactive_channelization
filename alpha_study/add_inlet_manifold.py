#!/usr/bin/env python3
"""
Inlet manifold for rate-controlled injection (SOURCE_SINK) into DFN and graph.

PFLOTRAN's VOLUMETRIC_RATE applies the stated rate to every cell of the
source region, and region files define face connections, not cell lists.
Pointing a SOURCE_SINK at the inlet face would therefore inject different
totals into a DFN (many inlet nodes) and a graph (few inlet cells).

Instead one small manifold ("well") cell is added to the UGE, 5 cm outside
the inlet face.  It is connected to every inlet boundary cell listed in
boundary_left_w.ex through a connection 100x stronger than that cell's
strongest existing connection (negligible added resistance, well-conditioned), and its permeability is
large, so its side of each connection is negligible.  The manifold is one
cell selected by a coordinate box (REGION well), injection is a single
VOLUMETRIC_RATE, and the split among inlet fractures is set by their
conductance at a common (floating) manifold pressure, evolving as minerals
dissolve or precipitate.  Applied identically to DFN and graphs.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import h5py
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "physics_upscaling"))
from write_corrected_bigrafv_inputs import read_uge, write_uge  # noqa: E402

OFFSET = 0.05          # m outside the inlet face
K_MANIFOLD = 1.0e-3    # m^2, makes the manifold side of each connection negligible
V_MANIFOLD = 1.0e-6    # m^3
STRENGTH = 100.0      # manifold connection / strongest inlet-cell connection


def read_ex(path):
    lines = Path(path).read_text().splitlines()
    n = int(lines[0].split()[1])
    return np.array([[float(v) for v in l.split()[:5]] for l in lines[1:1 + n]])


def add_inlet_manifold(run_dir, inflow_ex="boundary_left_w.ex"):
    run_dir = Path(run_dir)
    cells, cons = read_uge(run_dir / "full_mesh_vol_area.uge")
    ex = read_ex(run_dir / inflow_ex)
    mid = int(cells[:, 0].max()) + 1
    x_face = float(np.median(ex[:, 1]))
    xm = np.array([x_face - OFFSET, float(np.mean(ex[:, 2])), float(np.mean(ex[:, 3]))])
    cells = np.vstack([cells, [mid, *xm, V_MANIFOLD]])
    # PFLOTRAN needs each face centroid on the segment between the two cell
    # centres: keep the inlet cell's distance to its original boundary face
    # (so its half of the conductance is unchanged) along the cell->manifold line
    # Each manifold connection gets STRENGTH x the area/distance of the inlet
    # cell's strongest existing connection: negligible resistance (<1%) without
    # the ~1e9 coefficients that copying placeholder boundary-face areas
    # (1e3 m^2 at ~0 distance) put into the transport matrix.
    xyz = {int(c[0]): c[1:4] for c in cells}
    a_over_d = {}
    for c in cons:
        i, j = int(c[0]), int(c[1])
        d = float(np.linalg.norm(xyz[i] - xyz[j]))
        for k in (i, j):
            a_over_d[k] = max(a_over_d.get(k, 0.0), c[5] / max(d, 1e-12))
    new = []
    for r in ex:
        b = int(r[0])
        xb = xyz[b]
        seg = xm - xb
        L = float(np.linalg.norm(seg))
        face = xb + 0.5 * seg
        new.append([b, mid, *face, STRENGTH * a_over_d[b] * 0.5 * L])
    cons = np.vstack([cons, np.array(new, float)])
    write_uge(run_dir / "full_mesh_vol_area.uge", cells, cons)
    with h5py.File(run_dir / "dfn_properties.h5", "r+") as h:
        ids, perm = h["Cell Ids"][...], h["Permeability"][...]
        del h["Cell Ids"], h["Permeability"]
        h["Cell Ids"] = np.r_[ids, np.array([mid], ids.dtype)]
        h["Permeability"] = np.r_[perm, [K_MANIFOLD]]
    info = dict(manifold_cell=mid, manifold_xyz=xm.tolist(), n_inlet_connections=len(new),
                region_box=[(xm - 0.01).tolist(), (xm + 0.01).tolist()])
    (run_dir / "inlet_manifold.json").write_text(json.dumps(info, indent=1))
    return info


if __name__ == "__main__":
    print(json.dumps(add_inlet_manifold(sys.argv[1])))
