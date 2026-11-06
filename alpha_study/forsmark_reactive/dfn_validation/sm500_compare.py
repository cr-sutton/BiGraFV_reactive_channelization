#!/usr/bin/env python3
"""
1:1 DFN vs BiGraFV on the 500 x 125 x 125 m trial network (sm500_r282_p6_s1).  Written 6 Nov 2026, BEFORE any reactive
DFN state exists; the pass criteria below are fixed now and must not be changed after the DFN runs.

Both models come from the same dfnGen output (same 381 fractures and apertures).  For every saved state of each model,
the same post-processing:
  per fracture  volume-weighted gypsum and porosity over its cells (graph: one cell; DFN: materialid), dissolved fraction
                d_f = 1 - gypsum / initial gypsum, throughflow q_f from flow re-solved on the frozen permeability
                (analyze_km_dissolution_patterns.solve; throughflow = max(in, out) over faces crossing fractures),
                divided by the injected rate
  network       d (gypsum-weighted), PR_V = prw(q, V_f), PR_pore = prw(q, V_f phi_f), outlet_diss (flow-weighted d_f of
                fractures with centre in the last 100 m, x > 150 m), k_eff / start = manifold pressure at start / now,
                n90 and its overlap with the initial n90 set
  along x       PR_V per 50 m bin by fracture centre (10 bins), relative to its start
Events within capacity time <= 2, as compare_scale.events (PRpore_min, outlet5, PRV_min, breakthrough), on d.

PASS CRITERIA (gypsum-only is the primary comparison; coupled is reported with the same numbers):
  C1 stage order    DFN keeps PRpore_min <= PRV_min <= breakthrough
  C2 event timing   |d_DFN - d_graph| <= 0.10 for each of the four events
  C3 depth          |depth_DFN - depth_graph| <= 0.10 (depth = PR_V min / start)
  C4 inheritance    DFN inheritance >= 0.8, and Jaccard of the n90 sets at each model's PR_V minimum >= 0.5
  C5 moving front   in the DFN the d at each bin's PR_V minimum rises from inlet to outlet (Spearman over bins >= 0.8)
  C6 relaxation     in the DFN every bin's last value / start is >= 0.9 (focusing has relaxed behind the front), at the
                    last state with capacity time <= 2; the graph is held to the same rule
  C7 per fracture   at d = 0.25 and 0.40 (nearest saved state), Spearman of d_f DFN vs graph >= 0.6
  Verdict: "agrees" if C1-C7 all pass; "agrees on mechanism, differs on magnitude" if C1, C4, C5, C6 pass and any of
  C2, C3, C7 fail; otherwise "differs".  The steady-flow difference (Q_dfn / Q_graph = 1.69 at the start) is reported,
  not tested.

  python3 forsmark_reactive/dfn_validation/sm500_compare.py [--graph-only]
  -> sm500_r282_p6_s1/compare/{states.csv, bins.csv, fractures.csv, summary.csv, verdict.json}
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
FR = HERE.parent
ROOT = FR.parent
sys.path[:0] = [str(FR), str(ROOT), str(ROOT / "physics_upscaling")]
from analyze_km_dissolution_patterns import read_polygons, read_scalar_from_vtk, read_uge, solve  # noqa: E402
from diagnose_damkohler_per_fracture import throughflow  # noqa: E402
from time_axes import clocks  # noqa: E402

NET = HERE / "sm500_r282_p6_s1"
L = 500.0
TCAP_MAX = 2.0
XOUT = L / 2 - 100.0
EDGES = np.arange(0.0, L + 1, 50.0)
MODES = (("gyponly", "gypsum"), ("gypcal", "gypsum_calcite"))


def prw(q, w):
    w = w / w.sum()
    m = w > 0
    return float(q[m].sum() ** 2 / (q[m] ** 2 / w[m]).sum())


def n90set(q):
    o = np.argsort(q)[::-1]
    n = int(np.searchsorted(np.cumsum(q[o]), 0.9 * q.sum()) + 1)
    return set(o[:n].tolist())


def owner_map(run, ncells, nf, dfn):
    own = -np.arange(1, ncells + 1)
    if dfn:
        mid = np.loadtxt(run / "materialid.dat", skiprows=3, dtype=int)
        own[: len(mid)] = mid
    else:
        own[:nf] = np.arange(1, nf + 1)
    return own


def model_states(run, nf, xc, dfn):
    sched = json.loads((run / "single_stage.in.schedule.json").read_text())
    times = [0.0] + list(sched["vtk_times_y"])
    c = clocks(run)
    cells, conns = read_uge(run / "full_mesh_vol_area.uge")
    V = cells[:, 4]
    own = owner_map(run, len(cells), nf, dfn)
    fr = own > 0
    idx = own[fr] - 1
    Vf = np.bincount(idx, V[fr], nf)
    rate = sched["rate_m3y"] / 3.15576e7
    rows, perfrac, g0f, g0, p0, base0 = [], [], None, None, None, None
    for vk in sorted(run.glob("single_stage-*.vtk"), key=lambda p: int(p.stem.split("-")[1])):
        k = int(vk.stem.split("-")[1])
        if k >= len(times):
            continue
        t = times[k]
        tc = float(c.t_cap(t))
        if tc > TCAP_MAX:
            break
        gyp = np.asarray(read_scalar_from_vtk(str(vk), "Gypsum_VF"), float)
        phi = np.asarray(read_scalar_from_vtk(str(vk), "Porosity"), float)
        kk = np.asarray(read_scalar_from_vtk(str(vk), "Permeability"), float)
        if len(kk) < len(cells):
            kk = np.r_[kk, np.full(len(cells) - len(kk), kk.max())]
            gyp = np.r_[gyp, np.zeros(len(cells) - len(gyp))]
            phi = np.r_[phi, np.ones(len(cells) - len(phi))]
        gf = np.bincount(idx, (V * gyp)[fr], nf)
        phif = np.bincount(idx, (V * phi)[fr], nf) / Vf
        if g0f is None:
            g0f, g0 = np.maximum(gf, 1e-30), gf.sum()
        df = 1 - np.clip(gf / g0f, 0, 1)
        d = float(1 - gf.sum() / g0)
        pman, flux, ci, cj = solve(run, cells, conns, kk[: len(cells)], rate)
        Q = throughflow(ci, cj, flux, own)
        q = np.abs(np.array([Q.get(f, 0.0) for f in range(1, nf + 1)])) / rate
        if p0 is None:
            p0, base0 = pman, n90set(q)
        s90 = n90set(q)
        out = xc > XOUT
        b = np.clip(np.digitize(xc + L / 2, EDGES) - 1, 0, len(EDGES) - 2)
        rows.append(dict(k=k, t_y=t, t_cap=tc, d=d, pr_frac=prw(q, Vf), pr_pore=prw(q, Vf * phif),
                         outlet_diss=float((q[out] * df[out]).sum() / q[out].sum()) if q[out].sum() > 0 else np.nan,
                         keff_ratio=p0 / pman, n90=len(s90), overlap0=len(s90 & base0) / len(s90), qsum=float(q.sum()),
                         **{f"bin{i}": prw(q[b == i], Vf[b == i]) if (b == i).sum() >= 2 else np.nan for i in range(len(EDGES) - 1)}))
        perfrac.append((k, d, df, q, s90))
        print(f"  {run.name} k={k} tcap={tc:.3f} d={d:.3f} PRV={rows[-1]['pr_frac']:.3f}", flush=True)
    return pd.DataFrame(rows), perfrac


def events(g):
    g = g.reset_index(drop=True)
    ev = {"PRpore_min": g.pr_pore.idxmin(), "PRV_min": g.pr_frac.idxmin()}
    o = g.index[g.outlet_diss > 0.05]; ev["outlet5"] = o[0] if len(o) else None
    o = g.index[g.outlet_diss >= 0.5]; ev["breakthrough"] = o[0] if len(o) else None
    return {e: (float(g.d[i]) if i is not None else np.nan) for e, i in ev.items()}


def summarise(g, pf):
    ev = events(g)
    i = g.pr_frac.idxmin()
    j = g.n90.idxmin()
    bins = [c for c in g.columns if c.startswith("bin")]
    rel = g[bins] / g[bins].iloc[0]
    dmin = [g.d[rel[c].idxmin()] if rel[c].notna().any() else np.nan for c in bins]
    ok = np.isfinite(dmin)
    return dict(**ev, depth=float(g.pr_frac[i] / g.pr_frac[0]), inheritance=float(g.overlap0[j]),
                keff_gain_end=float(g.keff_ratio.iloc[-1]), d_end=float(g.d.iloc[-1]),
                front_rho=float(spearmanr(np.arange(len(bins))[ok], np.array(dmin)[ok]).statistic),
                bin_end_min=float(rel.iloc[-1].min()), bin_end=rel.iloc[-1].round(3).tolist(), bin_dmin=np.round(dmin, 3).tolist(),
                set_at_prvmin=pf[i][4])


def nearest(pf, dt):
    return min(pf, key=lambda x: abs(x[1] - dt))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph-only", action="store_true")
    a = ap.parse_args()
    polys = read_polygons(NET / "gypsum__uncorrected_graph__sm" / "polygons.dat")
    nf = len(polys)
    xc = np.array([P[:, 0].mean() for P in polys])
    out = NET / "compare"
    out.mkdir(exist_ok=True)
    S, Bsum, F, verdict = [], [], [], {}
    for mode, mdir in MODES:
        res = {}
        for model, dfn in (("graph", False), ("dfn", True)):
            run = NET / f"{mdir}__{'dfn' if dfn else 'uncorrected_graph'}__sm"
            if dfn and (a.graph_only or not (run / "single_stage-001.vtk").exists()):
                continue
            g, pf = model_states(run, nf, xc, dfn)
            S.append(g.assign(mode=mode, model=model))
            res[model] = (g, pf, summarise(g, pf))
        for model, (_, _, s) in res.items():
            Bsum.append(dict(mode=mode, model=model, **{k: v for k, v in s.items() if k != "set_at_prvmin"}))
        if "dfn" not in res:
            continue
        sg, sd = res["graph"][2], res["dfn"][2]
        jac = len(sg["set_at_prvmin"] & sd["set_at_prvmin"]) / len(sg["set_at_prvmin"] | sd["set_at_prvmin"])
        rho = {}
        for dt in (0.25, 0.40):
            kg, dg, dfg, qg, _ = nearest(res["graph"][1], dt)
            kd, dd, dfd, qd, _ = nearest(res["dfn"][1], dt)
            rho[dt] = float(spearmanr(dfg, dfd).statistic)
            F += [dict(mode=mode, d_target=dt, fracture=i + 1, d_graph=dfg[i], d_dfn=dfd[i], q_graph=qg[i], q_dfn=qd[i],
                       d_state_graph=dg, d_state_dfn=dd) for i in range(nf)]
        evs = ["PRpore_min", "outlet5", "PRV_min", "breakthrough"]
        C = {"C1": bool(sd["PRpore_min"] <= sd["PRV_min"] <= sd["breakthrough"]),
             "C2": bool(all(abs(sd[e] - sg[e]) <= 0.10 for e in evs)),
             "C3": bool(abs(sd["depth"] - sg["depth"]) <= 0.10),
             "C4": bool(sd["inheritance"] >= 0.8 and jac >= 0.5),
             "C5": bool(sd["front_rho"] >= 0.8),
             "C6": bool(sd["bin_end_min"] >= 0.9),
             "C7": bool(min(rho.values()) >= 0.6)}
        if all(C.values()):
            v = "agrees"
        elif all(C[c] for c in ("C1", "C4", "C5", "C6")):
            v = "agrees on mechanism, differs on magnitude"
        else:
            v = "differs"
        verdict[mode] = dict(criteria=C, verdict=v, jaccard=jac, rho_df=rho, graph_C6=bool(sg["bin_end_min"] >= 0.9),
                             graph_C5=bool(sg["front_rho"] >= 0.8), **{f"{e}_diff": sd[e] - sg[e] for e in evs},
                             depth_diff=sd["depth"] - sg["depth"])
    pd.concat(S).to_csv(out / "states.csv", index=False)
    pd.DataFrame(Bsum).to_csv(out / "summary.csv", index=False)
    if F:
        pd.DataFrame(F).to_csv(out / "fractures.csv", index=False)
    (out / "verdict.json").write_text(json.dumps(verdict, indent=2, default=str))
    pd.set_option("display.width", 250)
    print(pd.DataFrame(Bsum).drop(columns=["bin_end", "bin_dmin"]).round(3).to_string(index=False))
    print(json.dumps(verdict, indent=2, default=str))


if __name__ == "__main__":
    main()
