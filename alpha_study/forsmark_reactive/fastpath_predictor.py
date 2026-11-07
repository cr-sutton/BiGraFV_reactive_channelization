#!/usr/bin/env python3
"""
Fastest-path breakthrough predictor (7 Nov 2026; story item D).

Idea.  At local equilibrium (Da_f >> 1) a well-mixed fracture cell sends saturated water downstream until its gypsum is
gone, so the dissolution front crosses fracture i in a time proportional to its inventory over its flow, V_i / q_i.
Before breakthrough every injected volume leaves saturated, so the gypsum dissolved at time t is Q t c_cap / inventory.
If the front reached the outlet first along the path that minimises sum(V_i / q_i) and the flow did not change, the
fraction dissolved at breakthrough would be

    d_pred = Q * min_path sum_{i in path} V_i / q_i  /  sum_i V_i            (no fitted constant)

i.e. the fastest inlet-to-outlet "inventory travel time" in units of the network fill time.  It needs only the initial
steady flow (one flow solve), nothing from the reactive run.  Flow focusing during the run speeds the channel up, so the
measured d_bt is expected to be below d_pred, by an amount that grows with the permeability ceiling.

Graph: all UGE cells (fractures, intersection cells, boundary helpers); directed edges along the initial flux; node
weight V_j / inflow_j for fracture cells, 0 for the rest; Dijkstra from the inlet manifold cell to the outflow cells of
boundary_right_e.ex.  Flow from analyze_km_dissolution_patterns.solve on the k of the first saved state.

Networks: 1 km Phase 1 (P32 x4/x6/x8/x16, 60) and 2 km (45).  Events: scale2km/scale_runs.csv (1 and 2 km, x4-x8,
capacity time <= 2); x16 from phase1/stage_events_clocks.csv.  Ceiling sweep networks reuse the 1 km value.
Outputs: phase1/fastpath_predictor.csv (per network), fastpath_predictor_fit.csv.
  python3 forsmark_reactive/fastpath_predictor.py
"""
from __future__ import annotations

import json
import re
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT), str(ROOT / "physics_upscaling")]
from analyze_km_dissolution_patterns import read_polygons, read_scalar_from_vtk, read_uge, solve, read_ex  # noqa: E402


def one(run):
    run = Path(run)
    sched = json.loads((run / "single_stage.in.schedule.json").read_text())
    rate = sched["rate_m3y"] / 3.15576e7
    nf = len(read_polygons(run / "polygons.dat"))
    cells, conns = read_uge(run / "full_mesh_vol_area.uge")
    N = len(cells)
    kk = np.asarray(read_scalar_from_vtk(str(run / "single_stage-000.vtk"), "Permeability"), float)
    if len(kk) < N:
        kk = np.r_[kk, np.full(N - len(kk), kk.max())]
    _, flux, ci, cj = solve(run, cells, conns, kk[:N], rate)
    i, j = ci - 1, cj - 1
    src = np.where(flux > 0, i, j)
    dst = np.where(flux > 0, j, i)
    q = np.abs(flux)
    inflow = np.bincount(dst, q, N)
    V = cells[:, 4]
    w = np.zeros(N)
    w[:nf] = V[:nf] / np.maximum(inflow[:nf], 1e-30)
    keep = q > 1e-12 * rate
    G = coo_matrix((w[dst[keep]] + 1e-30, (src[keep], dst[keep])), shape=(N, N)).tocsr()
    man = json.loads((run / "inlet_manifold.json").read_text())["manifold_cell"] - 1
    out = np.array([int(r[0]) - 1 for r in read_ex(run / "boundary_right_e.ex")])
    dist = dijkstra(G, directed=True, indices=man)
    T = float(np.min(dist[out]))
    # also: flow-weighted mean over outlet cells of the shortest time (less sensitive to one path)
    return dict(run=str(run), d_pred=rate * T / V[:nf].sum(), n_fractures=nf)


def key(run, scale):
    m = re.search(r"p([\d.]+)_sg([\d.]+)_seed(\d+)", run)
    return dict(scale=scale, p32=float(m[1]), sigma=float(m[2]), seed=int(m[3]))


def loo_r2(h, x, y="d_bt"):
    pr = np.empty(len(h))
    for p in h.p32.unique():
        tr = (h.p32 != p).values
        a, b = np.polyfit(h[x][tr], h[y][tr], 1)
        pr[~tr] = a * h[x][~tr] + b
    return 1 - ((h[y] - pr) ** 2).sum() / ((h[y] - h[y].mean()) ** 2).sum()


def main():
    jobs = [(str(r), "1km") for r in sorted((HERE / "phase1").glob("L2_r15_p*_sg*_seed*/gypsum__uncorrected_graph__phase1"))]
    jobs += [(str(r), "2km") for r in sorted((HERE / "scale2km").glob("L2_r15_p*_sg*_seed*/gypsum__uncorrected_graph__phase1"))]
    with Pool(4) as p:
        res = p.map(one, [r for r, _ in jobs])
    P = pd.DataFrame([{**key(r, s), **x} for (r, s), x in zip(jobs, res)])
    ev = pd.read_csv(HERE / "scale2km" / "scale_runs.csv").rename(columns={"domain": "scale"})
    ev = ev[["scale", "mode", "p32", "sigma", "seed", "breakthrough"]]
    e16 = pd.read_csv(HERE / "phase1" / "stage_events_clocks.csv")
    e16 = e16[(e16.tag == "phase1") & (e16.event == "breakthrough") & (e16.p32 == 16.0)].drop_duplicates(["mode", "p32", "sigma", "seed"])
    e16 = e16.assign(scale="1km").rename(columns={"dissolved": "breakthrough"})[["scale", "mode", "p32", "sigma", "seed", "breakthrough"]]
    ev = pd.concat([ev, e16]).rename(columns={"breakthrough": "d_bt"})
    bp = pd.read_csv(HERE / "phase1" / "breakthrough_predictor.csv")[["p32", "sigma", "seed", "top1_share"]].drop_duplicates(["p32", "sigma", "seed"])
    D = ev.merge(P, on=["scale", "p32", "sigma", "seed"]).merge(bp.assign(scale="1km"), on=["scale", "p32", "sigma", "seed"], how="left")
    D.to_csv(HERE / "phase1" / "fastpath_predictor.csv", index=False)
    rows = []
    for mo, h in D.groupby("mode"):
        a = h[h.scale == "1km"].reset_index(drop=True)
        b = h[h.scale == "2km"].reset_index(drop=True)
        r = dict(mode=mo, n_1km=len(a), n_2km=len(b),
                 rho_dpred_1km=spearmanr(a.d_pred, a.d_bt).statistic, loo_r2_dpred_1km=loo_r2(a, "d_pred"),
                 rho_top1_1km=spearmanr(a.top1_share, a.d_bt).statistic, loo_r2_top1_1km=loo_r2(a.dropna(subset=["top1_share"]).reset_index(drop=True), "top1_share"),
                 ratio_median_1km=float((a.d_bt / a.d_pred).median()), ratio_median_2km=float((b.d_bt / b.d_pred).median()))
        s, c = np.polyfit(a.d_pred, a.d_bt, 1)
        pb = s * b.d_pred + c
        r.update(fit_slope=s, fit_icpt=c, r2_2km_from_1km_fit=1 - ((b.d_bt - pb) ** 2).sum() / ((b.d_bt - b.d_bt.mean()) ** 2).sum(),
                 rho_dpred_2km=spearmanr(b.d_pred, b.d_bt).statistic)
        rows.append(r)
    F = pd.DataFrame(rows)
    F.to_csv(HERE / "phase1" / "fastpath_predictor_fit.csv", index=False)
    pd.set_option("display.width", 250)
    print(F.round(3).T.to_string())


if __name__ == "__main__":
    main()
