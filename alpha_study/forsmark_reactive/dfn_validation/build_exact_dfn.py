#!/usr/bin/env python3
"""
Exact-network DFN (6 Nov 2026, targeted weekend DFN plan): feed the Phase 1 network's own polygons (polygons.dat, after
truncation and cluster removal) and its per-fracture transmissivities to dfnGen as user-defined polygons, with relaxed
FRAM (rFram) on at h = 1 m so that LaGriT can mesh it.  No stochastic families.  If rFram accepts every polygon the DFN
and a BiGraFV graph rebuilt from the same dfnGen output are the same fractures as the Phase 1 run (1:1 by fracture).

  --stage gen    dfnGen only: how many polygons survive, are they unchanged (coordinates), fracture-id mapping
  --stage graph  one-cell graph from the same dfnGen output (model_graph_raw), steady flow
  --stage dfn    mesh_network + lagrit2pflotran + steady flow (model_dfn)

  python3 forsmark_reactive/dfn_validation/build_exact_dfn.py --net L2_r15_p6.0_sg1.0_seed1 --stage gen \
      --out forsmark_reactive/dfn_validation/ex_p6.0_sg1.0_seed1
"""
from __future__ import annotations

import argparse
import json
import os
import types
import sys
from pathlib import Path
from time import perf_counter

import numpy as np
from scipy.spatial import cKDTree

HERE = Path(__file__).resolve().parent
FR = HERE.parent
ROOT = FR.parent
sys.path[:0] = [str(ROOT), str(ROOT / "physics_upscaling")]
os.chdir(ROOT)

from pydfnworks import *  # noqa: E402,F401,F403

from analyze_km_dissolution_patterns import read_polygons  # noqa: E402
from build_km_graph_network import eff_Q  # noqa: E402
from build_network_dfn_and_graphs import pressure_deck  # noqa: E402
import network_forsmark as forsmark  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--net", default="L2_r15_p6.0_sg1.0_seed1")
    ap.add_argument("--h", type=float, default=1.0)
    ap.add_argument("--ncpu", type=int, default=4)
    ap.add_argument("--stage", choices=("gen", "graph", "dfn"), default="gen")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    src = FR / "phase1" / a.net
    out = a.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    poly_file = src / "gypsum__uncorrected_graph__phase1" / "polygons.dat"
    B = np.loadtxt(src / "model_graph_raw" / "aperture.dat")
    P0 = read_polygons(poly_file)
    assert len(P0) == len(B), (len(P0), len(B))
    C0 = np.array([p.mean(0) for p in P0])
    deck = pressure_deck(out)
    sf = out / "build_summary.json"
    summary = json.loads(sf.read_text()) if sf.exists() else {}
    summary.update(source_network=str(src), n_input_polygons=len(P0), h=a.h, rFram=True)

    def new(name, ncpu):
        os.chdir(ROOT)
        D = DFNWORKS(str(out / name), dfnFlow_file=str(deck), ncpu=ncpu)
        # The Phase 1 polygons are already cut exactly at the domain faces, so dfnGen does not see them as touching a face
        # (all truncated = 0, no inflow-outflow cluster). Shrinking the domain by 1 cm per face makes dfnGen re-cut them.
        D.params["domainSize"]["value"] = [s - 0.02 for s in forsmark.DOMAINS["km250"]]
        D.params["h"]["value"] = a.h
        D.params["boundaryFaces"]["value"] = [1, 1, 0, 0, 0, 0]
        D.params["keepOnlyLargestCluster"]["value"] = True
        D.params["domainSizeIncrease"]["value"] = [0, 0, 0]
        D.params["disableFram"]["value"] = False
        D.params["framOn"]["value"] = True
        D.params["rFram"]["value"] = True
        D.params["seed"]["value"] = 1
        D.params["stopCondition"]["value"] = 0   # no stochastic families (dfnGen ignores userPolygonByCoord when stopCondition = 1)
        D.params["nPoly"]["value"] = len(P0)
        D.add_user_fract_from_file(str(poly_file), shape="poly", nPolygons=len(P0), by_coord=True, aperture=list(B))

        def assign_by_match(self):
            """pydfnworks maps user-polygon values by input order minus rFram rejections, but not minus the isolated fractures
            removed afterwards (and overruns the array). Assign each final fracture the Phase 1 aperture (k = b^2/12, as Phase 1)
            of the input polygon with the same centroid instead."""
            P1 = read_polygons(Path("dfnGen_output") / "polygons.dat")
            c1 = np.array([p.mean(0) for p in P1])
            dist, j = cKDTree(C0).query(c1)
            # dfnGen drops a near-duplicate vertex on a few polygons, which moves the vertex mean by up to a few m; require a
            # one-to-one match and matching bounding boxes instead of a tight centroid tolerance
            assert len(set(j)) == len(j), "two final fractures matched the same Phase 1 polygon"
            bb = max(np.abs(P1[i].min(0) - P0[k].min(0)).max() + np.abs(P1[i].max(0) - P0[k].max(0)).max() for i, k in enumerate(j))
            assert bb < 0.5, f"bounding boxes differ by {bb:.3f} m"
            np.savetxt("phase1_fracture_id.txt", j + 1, fmt="%d")   # final fracture i (1-based line) -> Phase 1 fracture id
            self.set_fracture_hydraulic_values("aperture", np.arange(1, len(P1) + 1), B[j])
            self.print_log(f"--> exact-network apertures assigned by centroid match ({len(P1)} fractures, max offset {dist.max():.4f} m)")
        D.assign_hydraulic_properties = types.MethodType(assign_by_match, D)
        D.make_working_directory(delete=True)
        D.check_input()
        D.create_network()
        return D

    if a.stage == "gen":
        t0 = perf_counter()
        D = new("model_gen", 1)
        P1 = read_polygons(out / "model_gen" / "dfnGen_output" / "polygons.dat")
        c0 = np.array([p.mean(0) for p in P0])
        c1 = np.array([p.mean(0) for p in P1])
        d, idx = cKDTree(c0).query(c1)
        same_shape = [bool(len(P1[i]) == len(P0[j]) and np.allclose(P1[i], P0[j], atol=1e-3)) for i, j in enumerate(idx)]
        summary.update(gen_seconds=perf_counter() - t0, n_output_polygons=len(P1), n_matched_centre_1mm=int((d < 1e-3).sum()),
                       n_identical_polygons=int(sum(same_shape)), n_missing=len(P0) - int((d < 1e-3).sum()))
        missing = sorted(set(range(len(P0))) - set(int(j) for j, dd in zip(idx, d) if dd < 1e-3))
        (out / "missing_phase1_fractures.txt").write_text("\n".join(str(i + 1) for i in missing) + "\n")
    elif a.stage == "graph":
        t0 = perf_counter()
        G_D = new("model_graph_raw", 1)
        G = G_D.create_graph("bipartite", inflow="left", outflow="right")
        G_D.graph_to_pflotran(G, uge_filename="full_mesh_vol_area.uge")
        G_D.pflotran()
        G_D.pflotran_cleanup()
        summary.update(Q_graph_raw=eff_Q(G_D), graph_nodes=G.number_of_nodes(), graph_edges=G.number_of_edges(),
                       graph_seconds=perf_counter() - t0)
    else:
        t0 = perf_counter()
        D = new("model_dfn", a.ncpu)
        D.mesh_network(min_dist=0.5, max_dist=10.0)
        summary["mesh_seconds"] = perf_counter() - t0
        D.lagrit2pflotran()
        D.pflotran()
        D.pflotran_cleanup()
        summary.update(Q_dfn=eff_Q(D), dfn_cells=sum(1 for _ in open(out / "model_dfn" / "materialid.dat")) - 3,
                       dfn_seconds=perf_counter() - t0)
    sf.write_text(json.dumps(summary, indent=2, default=str))
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
