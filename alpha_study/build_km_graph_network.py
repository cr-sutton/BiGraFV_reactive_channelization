#!/usr/bin/env python3
"""
Graph-only (no DFN mesh) build for the kilometre-scale scoping networks:
dfnGen -> bipartite graph -> graph_to_pflotran -> steady flow, then the
geometric correction on a copy (dfnGen polygons only; no mesh needed).

  python3 build_km_graph_network.py --domain km250 --seed 11 --out km_scale_graph_only/km250_s11
  python3 build_km_graph_network.py --domain-size 200 50 50 ...   (quick test)

Writes model_graph_raw/, model_graph_geo/ and flow_summary.json (Q of both
graphs at the pressure deck's boundary pressures; no DFN reference exists).
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path
from time import perf_counter

from pydfnworks import *  # noqa: F401,F403

from bigrafv_geometric_correction import GRAPH_INPUTS, apply_geometric_correction
from build_network_dfn_and_graphs import P_IN, P_OUT, pressure_deck
import network_forsmark as forsmark
import network_km_scale as net

HERE = Path(__file__).resolve().parent


def eff_Q(D):
    return float(D.effective_perm(inflow_pressure=P_IN, outflow_pressure=P_OUT, boundary_file="boundary_left_w.ex",
                                  direction="x", darcy_vel_file="darcyvel_001.dat"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", choices=sorted(net.DOMAINS), default=None)
    ap.add_argument("--domain-size", type=float, nargs=3, default=None)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--p32", type=float, default=net.P32_FAMILY)
    ap.add_argument("--sigma", type=float, default=0.0, help="semi-correlated aperture spread (variance of ln b); 0 = correlated")
    ap.add_argument("--forsmark", action="store_true", help="Forsmark FFM01 sets (network_forsmark.py) instead of the orthogonal ones")
    ap.add_argument("--layer", type=int, choices=(1, 2, 3), default=2, help="--forsmark: FFM01 depth layer")
    ap.add_argument("--rmin", type=float, default=5.0, help="--forsmark: minimum fracture radius (m)")
    ap.add_argument("--rmax", type=float, default=forsmark.RMAX_TABLE, help="--forsmark: maximum fracture radius (m)")
    ap.add_argument("--p32-scale", type=float, default=1.0, help="--forsmark: multiplier on the SKB P32 of every set")
    ap.add_argument("--no-geo", action="store_true")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    domain = a.domain_size or {**net.DOMAINS, **forsmark.DOMAINS}[a.domain]
    out = a.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    deck = pressure_deck(out)
    summary = dict(domain=domain, seed=a.seed, p32_family=a.p32, aperture_sigma=a.sigma)
    if a.forsmark:
        summary = dict(domain=domain, seed=a.seed, network="forsmark_ffm01", layer=a.layer, rmin=a.rmin, rmax=a.rmax,
                       p32_scale=a.p32_scale, transmissivity_sigma=a.sigma)
    t0 = perf_counter()
    os.chdir(HERE)
    D = DFNWORKS(str(out / "model_graph_raw"), dfnFlow_file=str(deck), ncpu=1)
    if a.forsmark:
        forsmark.configure(D, a.seed, domain, a.p32_scale, a.sigma, a.rmin, a.rmax, a.layer)
    else:
        net.configure(D, a.seed, domain, a.p32, a.sigma)
    D.make_working_directory(delete=True)
    D.check_input()
    D.create_network()
    summary["gen_seconds"] = perf_counter() - t0
    G = D.create_graph("bipartite", inflow="left", outflow="right")
    D.graph_to_pflotran(G, uge_filename="full_mesh_vol_area.uge")
    D.pflotran()
    D.pflotran_cleanup()
    summary["Q_graph_raw"] = eff_Q(D)
    summary["n_fractures"] = int(len(D.aperture))
    summary["graph_nodes"] = G.number_of_nodes()
    summary["graph_edges"] = G.number_of_edges()
    summary["raw_seconds"] = perf_counter() - t0
    (out / "flow_summary.json").write_text(json.dumps(summary, indent=2, default=str))
    if not a.no_geo:
        t1 = perf_counter()
        geo = out / "model_graph_geo"
        geo.mkdir(exist_ok=True)
        for f in GRAPH_INPUTS:
            shutil.copy(out / "model_graph_raw" / f, geo / f)
        shutil.copytree(out / "model_graph_raw" / "dfnGen_output", geo / "dfnGen_output", dirs_exist_ok=True)
        summary["geometric"] = apply_geometric_correction(geo, D.perm, D.aperture, domain)
        os.chdir(geo)
        D.pflotran()
        D.pflotran_cleanup()
        summary["Q_graph_geo"] = eff_Q(D)
        summary["geo_seconds"] = perf_counter() - t1
    (out / "flow_summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print(json.dumps({k: v for k, v in summary.items() if k != "geometric"}, indent=2, default=str))


if __name__ == "__main__":
    main()
