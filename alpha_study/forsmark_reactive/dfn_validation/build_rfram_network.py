#!/usr/bin/env python3
"""
DFN-validation network (5 Nov 2026, DFN_VALIDATION_SCOPE.md stage 0/1): a Forsmark FFM01 network built exactly as the Phase 1
networks (network_forsmark.configure, layer 2, r_min 15 m, 1000 x 250 x 250 m) except that relaxed FRAM is ON
(framOn = True, disableFram = False, rFram = True, h = 1 m), so that the same dfnGen output can be meshed.

  model_graph_raw/  one-cell BiGraFV graph (create_graph -> graph_to_pflotran), as build_km_graph_network.py
  model_dfn/        meshed DFN (mesh_network -> lagrit2pflotran), same seed -> same dfnGen output (checked on polygons.dat)

  python3 forsmark_reactive/dfn_validation/build_rfram_network.py --p32-scale 4 --sigma 1 --seed 1 \
      --out forsmark_reactive/dfn_validation/rf_p4.0_sg1.0_seed1 [--stage graph|dfn|both] [--ncpu 6]

The Phase 1 builder (build_km_graph_network.py) is not modified.
"""
from __future__ import annotations

import argparse
import filecmp
import json
import os
import sys
from pathlib import Path
from time import perf_counter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT)]
os.chdir(ROOT)

from pydfnworks import *  # noqa: E402,F401,F403

from build_km_graph_network import eff_Q  # noqa: E402
from build_network_dfn_and_graphs import pressure_deck  # noqa: E402
import network_forsmark as forsmark  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--p32-scale", type=float, default=4.0)
    ap.add_argument("--sigma", type=float, default=1.0)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--h", type=float, default=1.0)
    ap.add_argument("--ncpu", type=int, default=6)
    ap.add_argument("--stage", choices=("graph", "dfn", "both"), default="both")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    domain = forsmark.DOMAINS["km250"]
    out = a.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    deck = pressure_deck(out)
    sf = out / "build_summary.json"
    summary = json.loads(sf.read_text()) if sf.exists() else {}
    summary.update(domain=domain, seed=a.seed, network="forsmark_ffm01_rfram", layer=2, rmin=15.0, rmax=forsmark.RMAX_TABLE,
                   p32_scale=a.p32_scale, transmissivity_sigma=a.sigma, h=a.h, framOn=True, rFram=True)

    def new(name, ncpu):
        os.chdir(ROOT)
        D = DFNWORKS(str(out / name), dfnFlow_file=str(deck), ncpu=ncpu)
        forsmark.configure(D, a.seed, domain, a.p32_scale, a.sigma, 15.0, forsmark.RMAX_TABLE, 2)
        D.params["h"]["value"] = a.h
        D.params["disableFram"]["value"] = False
        D.params["framOn"]["value"] = True
        D.params["rFram"]["value"] = True
        D.make_working_directory(delete=True)
        D.check_input()
        D.create_network()
        return D

    if a.stage in ("graph", "both"):
        t0 = perf_counter()
        G_D = new("model_graph_raw", 1)
        G = G_D.create_graph("bipartite", inflow="left", outflow="right")
        G_D.graph_to_pflotran(G, uge_filename="full_mesh_vol_area.uge")
        G_D.pflotran()
        G_D.pflotran_cleanup()
        summary.update(Q_graph_raw=eff_Q(G_D), n_fractures=int(len(G_D.aperture)), graph_nodes=G.number_of_nodes(),
                       graph_edges=G.number_of_edges(), graph_seconds=perf_counter() - t0)
        sf.write_text(json.dumps(summary, indent=2, default=str))
    if a.stage in ("dfn", "both"):
        t0 = perf_counter()
        D = new("model_dfn", a.ncpu)
        g = out / "model_graph_raw" / "dfnGen_output" / "polygons.dat"
        summary["same_dfnGen_as_graph"] = bool(g.exists() and filecmp.cmp(g, out / "model_dfn" / "dfnGen_output" / "polygons.dat", shallow=False))
        t1 = perf_counter()
        D.mesh_network()
        summary["mesh_seconds"] = perf_counter() - t1
        D.lagrit2pflotran()
        t2 = perf_counter()
        D.pflotran()
        D.pflotran_cleanup()
        summary["dfn_flow_seconds"] = perf_counter() - t2
        summary["Q_dfn"] = eff_Q(D)
        summary["dfn_cells"] = sum(1 for _ in open(out / "model_dfn" / "materialid.dat")) - 3
        summary["dfn_seconds"] = perf_counter() - t0
        sf.write_text(json.dumps(summary, indent=2, default=str))
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
