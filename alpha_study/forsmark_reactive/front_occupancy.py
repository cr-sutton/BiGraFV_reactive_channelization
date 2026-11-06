#!/usr/bin/env python3
"""
Front-occupancy test and Hyman-style flow-focusing profile (6 Nov 2026; external assessment + Hyman et al. 2026 Fig. 11).

Question: does the network-wide PR_V minimum come when the moving focused zone covers the largest part of the domain?

Rules fixed before running (do not tune after seeing results):
  bins        100 m along x at both scales (10 at 1 km, 20 at 2 km); fracture assigned to the bin of its centre (as 8.9)
  focused     a bin is focused at a state when its PR_V / its own start <= 0.8   (0.7 and 0.9 reported as sensitivity)
  occupancy   O(state) = share of bins that are focused (= share of domain length)
  window      states with capacity time <= 2 (TCAP_MAX, as every stage event)
  T1 timing   d at max O against d at the network PR_V minimum: Spearman rho per scale and chemistry, and the share of runs
              with |difference| <= 0.05.  Supports the hypothesis if rho >= 0.6 and the share >= 0.6 at 1 km and at 2 km.
  T2 depth    max O against network depth (PR_V min / start): Spearman; supports if rho <= -0.5 (wider zone, deeper).
  T3 scale    median d at max O minus d at breakthrough, 1 km against 2 km (descriptive).
  Unit        each sigma is its own ensemble; runs on the same geometry are not counted as independent in any test of
              significance (T1/T2 are descriptive correlations over runs, stated with n).
Network PR_V is computed from the same per-fracture flows (sum Q)^2 / (sum V * sum Q^2 / V) over all fractures.

Hyman-style profile (Hyman et al. 2026 Eq. 42, Jang et al. 2011): at planes x every 20 m, f50 = (n/2 - n50) / (n/2), n the
fractures whose polygon spans the plane and n50 the fewest of them whose throughflow sums to half of theirs.  Theirs counts
graph connections crossing the plane; one cell per fracture has only throughflow, so this is our analogue.  1 km Phase 1.

Inputs: paraview/<net>__<run>/fractures_KKK.vtu (Q_frac, x_center), paraview/S2KM__... for 2 km, polygons.dat, the UGE,
patterns.csv, time_axes.clocks.
Outputs (phase1/): front_occupancy.csv (per run and state), front_occupancy_runs.csv (per run), f50_profile.csv,
front_occupancy_tests.csv.
  python3 forsmark_reactive/front_occupancy.py
"""
from __future__ import annotations

import re
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT), str(ROOT / "physics_upscaling")]
from analyze_km_dissolution_patterns import read_polygons  # noqa: E402
from analyze_phase1_mechanism import read_vtu  # noqa: E402
from write_corrected_bigrafv_inputs import read_uge  # noqa: E402
from time_axes import clocks  # noqa: E402

P1 = HERE / "phase1"
PV = ROOT / "paraview"
TCAP_MAX = 2.0
THR = (0.7, 0.8, 0.9)
MAIN = 0.8


def prv(q, V):
    return float(q.sum() ** 2 / (V.sum() * (q ** 2 / V).sum())) if q.sum() > 0 else np.nan


def f50(q):
    n = len(q)
    if n < 2 or q.sum() <= 0:
        return np.nan
    c = np.cumsum(np.sort(q)[::-1])
    n50 = int(np.searchsorted(c, 0.5 * c[-1]) + 1)
    return (n / 2 - n50) / (n / 2)


def one(arg):
    run, scale = arg
    run = Path(run)
    L = 1000.0 if scale == "1km" else 2000.0
    pv = PV / (f"{run.parent.name}__{run.name}" if scale == "1km" else f"S2KM__{run.parent.name}__{run.name}")
    m = re.search(r"p([\d.]+)_sg([\d.]+)_seed(\d)", str(run))
    mode = "gypcal" if "calcite" in run.name else "gyponly"
    pat = pd.read_csv(run / "patterns.csv").set_index("k")
    c = clocks(run)
    polys = read_polygons(run / "polygons.dat")
    nf = len(polys)
    V = read_uge(run / "full_mesh_vol_area.uge")[0][:nf, 4]
    xlo = np.array([P[:, 0].min() for P in polys]) + L / 2
    xhi = np.array([P[:, 0].max() for P in polys]) + L / 2
    E = np.arange(0.0, L + 1, 100.0)
    planes = np.arange(10.0, L, 20.0)
    span = [(xlo < x) & (xhi > x) for x in planes]
    base, rows, prof = None, [], []
    for f in sorted(pv.glob("fractures_*.vtu"), key=lambda p: int(p.stem.split("_")[1])):
        k = int(f.stem.split("_")[1])
        if k not in pat.index:
            continue
        tc = float(c.t_cap(pat.loc[k, "t_y"]))
        if tc > TCAP_MAX:
            continue
        a = read_vtu(f)
        q = np.abs(a["Q_frac"]).astype(float)[:nf]
        b = np.clip(np.digitize(a["x_center"].astype(float)[:nf] + L / 2, E) - 1, 0, len(E) - 2)
        pb = np.array([prv(q[b == i], V[b == i]) if (b == i).sum() >= 2 else np.nan for i in range(len(E) - 1)])
        if base is None:
            base = pb
        rel = pb / base
        ok = np.isfinite(rel)
        row = dict(scale=scale, mode=mode, p32=float(m[1]), sigma=float(m[2]), seed=int(m[3]), k=k, t_cap=tc,
                   dissolved=float(pat.loc[k, "dissolved"]), prv_net=prv(q, V), n_bins=int(ok.sum()))
        for t in THR:
            row[f"occ_{t}"] = float((rel[ok] <= t).mean())
        row["front_x"] = float(E[:-1][ok][rel[ok] <= MAIN].max() + 50) if (rel[ok] <= MAIN).any() else np.nan
        rows.append(row)
        if scale == "1km":
            for x, s in zip(planes, span):
                prof.append(dict(mode=mode, p32=row["p32"], sigma=row["sigma"], seed=row["seed"], k=k,
                                 dissolved=row["dissolved"], x=x, n=int(s.sum()), f50=f50(q[s])))
    return rows, prof


def per_run(df):
    out = []
    for key, h in df.groupby(["scale", "mode", "p32", "sigma", "seed"]):
        h = h.sort_values("k")
        h = h.assign(d=np.maximum.accumulate(h.dissolved.values), rel=h.prv_net / h.prv_net.iloc[0])
        i = h.rel.idxmin()
        r = dict(zip(["scale", "mode", "p32", "sigma", "seed"], key), d_prv_min=h.d[i], depth=h.rel[i], n_states=len(h))
        for t in THR:
            j = h[f"occ_{t}"].idxmax()
            r[f"occ_max_{t}"] = h[f"occ_{t}"][j]
            r[f"d_occ_max_{t}"] = h.d[j]
        out.append(r)
    return pd.DataFrame(out)


def tests(R):
    ev = pd.read_csv(HERE / "scale2km" / "scale_runs.csv")[["domain", "mode", "p32", "sigma", "seed", "breakthrough", "PRV_min"]]
    ev = ev.rename(columns={"domain": "scale"})
    R = R.merge(ev, on=["scale", "mode", "p32", "sigma", "seed"], how="left")
    out = []
    for (sc, mo), h in R.groupby(["scale", "mode"]):
        for t in THR:
            dd = h[f"d_occ_max_{t}"] - h.d_prv_min
            rt = spearmanr(h[f"d_occ_max_{t}"], h.d_prv_min)
            rd = spearmanr(h[f"occ_max_{t}"], h.depth)
            out.append(dict(scale=sc, mode=mo, threshold=t, n=len(h), T1_rho=rt.statistic, T1_share_within_005=float((dd.abs() <= 0.05).mean()),
                            T1_median_diff=float(dd.median()), T2_rho=rd.statistic, occ_max_median=float(h[f"occ_max_{t}"].median()),
                            T3_d_occmax_minus_bt=float((h[f"d_occ_max_{t}"] - h.breakthrough).median()),
                            check_prvmin_vs_events=float((h.d_prv_min - h.PRV_min).abs().median())))
    return pd.DataFrame(out), R


def main():
    jobs = [(str(r), "1km") for r in sorted(P1.glob("L2_r15_p*_sg*_seed*/gyp*__phase1")) if (r / "patterns.csv").exists()]
    jobs += [(str(r), "2km") for r in sorted((HERE / "scale2km").glob("L2_r15_p*_sg*_seed*/gyp*__phase1"))
             if (r / "patterns.csv").exists() and (PV / f"S2KM__{r.parent.name}__{r.name}").exists()]
    with Pool(3) as p:
        res = p.map(one, jobs)
    df = pd.DataFrame([r for rs, _ in res for r in rs])
    prof = pd.DataFrame([r for _, ps in res for r in ps])
    df.to_csv(P1 / "front_occupancy.csv", index=False)
    prof.to_csv(P1 / "f50_profile.csv", index=False)
    R = per_run(df)
    T, R = tests(R)
    R.to_csv(P1 / "front_occupancy_runs.csv", index=False)
    T.to_csv(P1 / "front_occupancy_tests.csv", index=False)
    pd.set_option("display.width", 250)
    print(len(jobs), "runs")
    print(T.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
