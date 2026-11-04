#!/usr/bin/env python3
"""
Build the hybrid channelized network and its three model directories.

  model_dfn/        fully meshed DFN (mesh_network -> lagrit2pflotran)
  model_graph_raw/  BiGraFV graph (create_graph -> graph_to_pflotran)
  model_graph_geo/  copy of the raw graph with the geometric correction

Each directory gets a steady flow solve with the pressure deck of the reactive
case (same boundary pressures as gyp_and_calc.in) and is kept on disk,
including all VTK output, for later tracer/reactive stages and inspection.

  python3 build_network_dfn_and_graphs.py --seed 3010 --out reactive_hybrid_network_staged/seed3010 --ncpu 6
"""
from __future__ import annotations

import argparse
import importlib
import json
import os
import shutil
from pathlib import Path
from time import perf_counter

from pydfnworks import *

from bigrafv_geometric_correction import GRAPH_INPUTS, apply_geometric_correction

HERE = Path(__file__).resolve().parent
P_IN, P_OUT = 1.1e6, 1.0e6


def pressure_deck(out_dir):
    """The repository pressure deck with gyp_and_calc.in's boundary pressures."""
    s = (HERE / "pflotran_graph_pressure.in").read_text()
    s = s.replace("LIQUID_PRESSURE 2.0d6", "LIQUID_PRESSURE 1.1d6").replace("LIQUID_PRESSURE 1.2d6", "LIQUID_PRESSURE 1.05d6")
    p = Path(out_dir) / "pflotran_hybrid_pressure.in"
    p.write_text(s)
    return p


def eff_Q(DFN):
    return float(DFN.effective_perm(inflow_pressure=P_IN, outflow_pressure=P_OUT, boundary_file="boundary_left_w.ex",
                                    direction="x", darcy_vel_file="darcyvel_001.dat"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--ncpu", type=int, default=6)
    ap.add_argument("--network", choices=["hybrid", "tpl", "tpl_large", "tpl_dense", "qtz"], default="hybrid")
    a = ap.parse_args()
    net = importlib.import_module({"hybrid": "network_hybrid_channelized", "tpl": "network_tpl_6x4x4m", "tpl_large": "network_tpl_16x8x8m", "tpl_dense": "network_tpl_dense", "qtz": "network_quartz_paper"}[a.network])
    configure, DOMAIN = net.configure, net.DOMAIN
    out = a.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    deck = pressure_deck(out)
    summary, t0 = {}, perf_counter()

    def new(name):
        os.chdir(HERE)
        D = DFNWORKS(str(out / name), dfnFlow_file=str(deck), ncpu=a.ncpu)
        configure(D, a.seed)
        D.make_working_directory(delete=True)
        D.check_input()
        D.create_network()
        return D

    D = new("model_dfn")
    D.mesh_network()
    D.lagrit2pflotran()
    D.pflotran()
    D.parse_pflotran_vtk_python()
    D.pflotran_cleanup()
    summary["Q_dfn"] = eff_Q(D)
    summary["dfn_cells"] = sum(1 for _ in open(out / "model_dfn" / "materialid.dat")) - 3
    summary["dfn_flow_seconds"] = perf_counter() - t0

    t1 = perf_counter()
    Gd = new("model_graph_raw")
    Gd.mesh_network()
    G = Gd.create_graph("bipartite", inflow="left", outflow="right")
    Gd.graph_to_pflotran(G, uge_filename="full_mesh_vol_area.uge")
    Gd.ncpu = 1
    Gd.pflotran()
    Gd.pflotran_cleanup()
    summary["Q_graph_raw"] = eff_Q(Gd)

    geo = out / "model_graph_geo"
    geo.mkdir(exist_ok=True)
    for f in GRAPH_INPUTS:
        shutil.copy(out / "model_graph_raw" / f, geo / f)
    shutil.copytree(out / "model_graph_raw" / "dfnGen_output", geo / "dfnGen_output", dirs_exist_ok=True)
    summary["geometric"] = apply_geometric_correction(geo, Gd.perm, Gd.aperture, DOMAIN)
    os.chdir(geo)
    Gd.pflotran()
    Gd.pflotran_cleanup()
    summary["Q_graph_geo"] = eff_Q(Gd)
    summary["graph_seconds"] = perf_counter() - t1
    summary["geo_Q_error_pct"] = 100 * (summary["Q_graph_geo"] / summary["Q_dfn"] - 1)
    summary["raw_Q_error_pct"] = 100 * (summary["Q_graph_raw"] / summary["Q_dfn"] - 1)
    (out / "flow_summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
