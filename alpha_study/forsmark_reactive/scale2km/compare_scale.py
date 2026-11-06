#!/usr/bin/env python3
"""
2 km scale test vs 1 km Phase 1 (5 Nov 2026; design fixed in SCALE_TEST.md).

Per finished 2 km run, at EVERY saved state (the pattern script keeps only every 4th per-fracture file on networks with
>= 10,000 fractures, so the state files are not used): flow re-solved on the frozen permeability exactly as
analyze_km_dissolution_patterns.py, then the analyze_phase1_mechanism.py measures:
  pr_frac (= PR_V), pr_pore, outlet_diss (flow-weighted dissolved fraction of the fractures in the last 100 m before the
  outlet: x > 900 m here, x > 400 m at 1 km), dissolved (patterns.csv), clocks from time_axes.py.
Stage events as stage_events_clocks.py / dfn_validation/gate_check.py, but within capacity time <= 2 for BOTH domains
(the 2 km runs end at 2); depth = min PR_V / start and inheritance = overlap0 at the n90 minimum (channelization.csv),
also within capacity time <= 2.

  python3 forsmark_reactive/scale2km/compare_scale.py   -> scale2km/scale_mechanism.csv, scale_runs.csv, scale_compare.csv
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
FR = HERE.parent
ROOT = FR.parent
sys.path[:0] = [str(FR), str(ROOT), str(ROOT / "physics_upscaling")]
from analyze_km_dissolution_patterns import read_polygons, solve, read_uge, read_scalar_from_vtk, throughflow  # noqa: E402
from time_axes import clocks  # noqa: E402
import json  # noqa: E402

TCAP_MAX = 2.0
P1 = FR / "phase1"
EVENTS = ["PRpore_min", "outlet5", "PRV_min", "breakthrough"]


def prw(q, w):
    w = w / w.sum()
    m = w > 0
    return float(q[m].sum() ** 2 / (q[m] ** 2 / w[m]).sum())


def mech_2km(run, xout=900.0, use_cache=True):
    cache = run / "scale_mechanism_run.csv"
    if use_cache and cache.exists() and cache.stat().st_mtime > (run / "patterns.csv").stat().st_mtime:
        return pd.read_csv(cache)
    m = re.search(r"p([\d.]+)_sg([\d.]+)_seed(\d)", str(run))
    sched = json.loads((run / "single_stage.in.schedule.json").read_text())
    vf0 = sched.get("vf0", 0.9)
    pat = pd.read_csv(run / "patterns.csv").set_index("k")
    c = clocks(run)
    polys = read_polygons(run / "polygons.dat")
    nf = len(polys)
    xc = np.array([P[:, 0].mean() for P in polys])
    out = xc > xout
    cells, conns = read_uge(run / "full_mesh_vol_area.uge")
    vol = cells[:nf, 4]
    own = np.zeros(len(cells), int)
    own[:nf] = np.arange(1, nf + 1)
    own[nf:] = -np.arange(1, len(cells) - nf + 1)
    rate = sched["rate_m3y"] / 3.15576e7
    mode = "gypcal" if "calcite" in run.name else "gyponly"
    rows, vf_init = [], None
    for vk in sorted(run.glob("single_stage-*.vtk"), key=lambda p: int(p.stem.split("-")[1])):
        k = int(vk.stem.split("-")[1])
        if k not in pat.index:
            continue
        gyp = np.asarray(read_scalar_from_vtk(str(vk), "Gypsum_VF"), float)
        cal = np.asarray(read_scalar_from_vtk(str(vk), "Calcite_VF"), float)[:nf] if mode == "gypcal" else 0.0
        kk = np.asarray(read_scalar_from_vtk(str(vk), "Permeability"), float)
        if len(kk) < len(cells):
            kk = np.r_[kk, np.full(len(cells) - len(kk), kk.max())]
        _, flux, ci, cj = solve(run, cells, conns, kk[: len(cells)], rate)
        Qf = throughflow(ci, cj, flux, own)
        q = np.abs(np.array([Qf.get(f, 0.0) for f in range(1, nf + 1)])) / rate
        if vf_init is None:
            vf_init = np.where(gyp[:nf] > 0, gyp[:nf], vf0)
        d = 1 - np.clip(gyp[:nf] / vf_init, 0, 1)
        phi = np.clip(1 - gyp[:nf] - cal, 1e-6, 1)
        t = pat.loc[k, "t_y"]
        rows.append(dict(p32=float(m[1]), sigma=float(m[2]), seed=int(m[3]), mode=mode, k=k, t_y=t, pv=float(c.pv(t)),
                         t_cap=float(c.t_cap(t)), pr_frac=prw(q, vol), pr_pore=prw(q, vol * phi),
                         outlet_diss=float((q[out] * d[out]).sum() / q[out].sum()) if q[out].sum() > 0 else np.nan,
                         dissolved=pat.loc[k, "dissolved"]))
    df = pd.DataFrame(rows)
    if use_cache:
        df.to_csv(cache, index=False)
    return df


def events(g):
    g = g.sort_values("k").reset_index(drop=True)
    g = g[g.t_cap <= TCAP_MAX].reset_index(drop=True)
    ev = {"PRpore_min": g.pr_pore.idxmin(), "PRV_min": g.pr_frac.idxmin()}
    o = g.index[g.outlet_diss > 0.05]; ev["outlet5"] = o[0] if len(o) else None
    o = g.index[g.outlet_diss >= 0.5]; ev["breakthrough"] = o[0] if len(o) else None
    return {e: (float(g.dissolved[i]) if i is not None else np.nan) for e, i in ev.items()}


def chan(run, g):
    d = pd.read_csv(run / "channelization.csv").sort_values("k")
    d = d[d.k.isin(g.k[g.t_cap <= TCAP_MAX])].reset_index(drop=True)
    return dict(depth=float(d.pr_fracture_vol.min() / d.pr_fracture_vol.iloc[0]), inheritance=float(d.overlap0[d.n90.idxmin()]),
                n90_min_rel=float(d.n90.min() / d.n90.iloc[0]))


def main():
    rows, mech = [], []
    for run in sorted(HERE.glob("L2_r15_p*_sg*_seed*/gyp*__phase1")):
        if not ((run / "patterns.csv").exists() and (run / "channelization.csv").exists()):
            continue
        g = mech_2km(run)
        mech.append(g)
        r = g.iloc[0]
        rows.append(dict(domain="2km", mode=r["mode"], p32=r.p32, sigma=r.sigma, seed=int(r.seed), t_cap_end=float(g.t_cap.max()),
                         **events(g), **chan(run, g)))
    if not rows:
        print("no finished 2 km runs yet")
        return
    pd.concat(mech).to_csv(HERE / "scale_mechanism.csv", index=False)
    done = pd.DataFrame(rows)
    p1 = pd.read_csv(P1 / "phase1_mechanism.csv")
    p1 = p1[(p1.tag == "phase1") & p1.p32.isin([4.0, 6.0, 8.0])]
    ref = []
    for (mode, p, sg, seed), g in p1.groupby(["mode", "p32", "sigma", "seed"]):
        mdir = "gypsum" if mode == "gyponly" else "gypsum_calcite"
        run = P1 / f"L2_r15_p{p}_sg{sg}_seed{seed}" / f"{mdir}__uncorrected_graph__phase1"
        ref.append(dict(domain="1km", mode=mode, p32=p, sigma=sg, seed=int(seed), t_cap_end=float(g.t_cap.max()), **events(g), **chan(run, g)))
    runs = pd.concat([pd.DataFrame(ref), done], ignore_index=True)
    for a, b in (("PRpore_min", "PRV_min"), ("outlet5", "PRV_min"), ("PRV_min", "breakthrough"), ("outlet5", "breakthrough")):
        runs[f"{a}<={b}"] = runs[a] <= runs[b]
    runs.to_csv(HERE / "scale_runs.csv", index=False)
    # compare only the (mode, p32, sigma) cells that have 2 km runs; 1 km uses all 5 seeds of that cell
    cmp = []
    meas = EVENTS + ["depth", "inheritance", "n90_min_rel"]
    for (mode, p, sg), g2 in done.groupby(["mode", "p32", "sigma"]):
        g1 = runs[(runs.domain == "1km") & (runs["mode"] == mode) & (runs.p32 == p) & (runs.sigma == sg)]
        for k in meas:
            q1 = g1[k].quantile([0.25, 0.5, 0.75]).values
            cmp.append(dict(mode=mode, p32=p, sigma=sg, measure=k, n_1km=int(g1[k].notna().sum()), km1_q25=q1[0], km1_median=q1[1],
                            km1_q75=q1[2], n_2km=int(g2[k].notna().sum()), km2_median=g2[k].median(), km2_min=g2[k].min(),
                            km2_max=g2[k].max(), inside_1km_iqr=bool(q1[0] <= g2[k].median() <= q1[2])))
    cmp = pd.DataFrame(cmp)
    cmp.to_csv(HERE / "scale_compare.csv", index=False)
    pd.set_option("display.width", 220)
    print(cmp.round(3).to_string(index=False))
    order = [c for c in runs.columns if "<=" in c]
    print("\nstage order holds (share of runs, t_cap <= 2):")
    print(runs[runs.p32.isin(done.p32.unique())].groupby(["domain", "mode"])[order].mean().round(2).to_string())


if __name__ == "__main__":
    main()
