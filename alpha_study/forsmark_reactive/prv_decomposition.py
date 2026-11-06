#!/usr/bin/env python3
"""
Two checks after the front-occupancy test failed (6 Nov 2026, report 8.13).

A. Spanning bins (robustness of "each stretch focuses as the front passes, then relaxes", 8.9).
   8.9 puts each fracture in the 100 m bin of its centre.  Here a fracture counts in EVERY 100 m bin its polygon spans
   in x, with its full throughflow q and the share of its volume that lies in that bin (V * overlap length / x-extent).
   Same per-bin measures as xbin_bin_minima.py: PR_V / start minimum, dissolved fraction at it, end value / start.
   Passes if, for both chemistries, the median end value / start is within 0.05 of 1 in every bin AND the d at the bin
   minimum rises from the inlet bin to the outlet bin (Spearman rho over bins >= 0.8).  1 km Phase 1, 120 runs.

B. What sets the timing of the network PR_V minimum?  PR_V = (sum q)^2 / (V_tot * S), S = sum q^2 / V.
   Groups of fractures, fixed before running:
     chan0   the initial channel: fewest fractures carrying 90 % of the summed throughflow at the start
     long    fractures whose x-extent is >= 200 m (two bins or more)
     outlet  fractures with centre in the last 100 m before the outlet
   (a) share of the change in S from the start to the network minimum carried by each group (and by its complement);
   (b) timing test as 8.13: d at the minimum of the group's own PR_V against d at the network minimum, Spearman rho and
       share within 0.05; a group "sets the timing" if rho >= 0.6 and share >= 0.6 at both scales (both chemistries).
   1 km Phase 1 (120 runs) and the finished 2 km runs with per-fracture files.  States with capacity time <= 2.

Outputs (phase1/): xbin_spanning.csv (per run, state, bin), xbin_spanning_minima.csv, prv_decomposition_runs.csv,
prv_decomposition_tests.csv.
  DYLD_LIBRARY_PATH=/opt/homebrew/Cellar/freetype/2.14.1_1/lib python3 forsmark_reactive/prv_decomposition.py
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
GROUPS = ("chan0", "long", "outlet")


def prv(q, V):
    s = (q ** 2 / V).sum()
    return float(q.sum() ** 2 / (V.sum() * s)) if s > 0 else np.nan


def one(arg):
    run, scale = arg
    run = Path(run)
    L = 1000.0 if scale == "1km" else 2000.0
    pv = PV / (f"{run.parent.name}__{run.name}" if scale == "1km" else f"S2KM__{run.parent.name}__{run.name}")
    m = re.search(r"p([\d.]+)_sg([\d.]+)_seed(\d)", str(run))
    key = dict(scale=scale, mode="gypcal" if "calcite" in run.name else "gyponly", p32=float(m[1]), sigma=float(m[2]), seed=int(m[3]))
    pat = pd.read_csv(run / "patterns.csv").set_index("k")
    c = clocks(run)
    polys = read_polygons(run / "polygons.dat")
    nf = len(polys)
    V = read_uge(run / "full_mesh_vol_area.uge")[0][:nf, 4]
    xlo = np.array([P[:, 0].min() for P in polys]) + L / 2
    xhi = np.array([P[:, 0].max() for P in polys]) + L / 2
    ext = np.maximum(xhi - xlo, 1e-9)
    xc = np.array([P[:, 0].mean() for P in polys]) + L / 2
    E = np.arange(0.0, L + 1, 100.0)
    ov = np.clip(np.minimum(xhi[:, None], E[None, 1:]) - np.maximum(xlo[:, None], E[None, :-1]), 0, None) / ext[:, None]
    grp = {"long": ext >= 200.0, "outlet": xc > L - 100.0}
    states, bins = [], []
    for f in sorted(pv.glob("fractures_*.vtu"), key=lambda p: int(p.stem.split("_")[1])):
        k = int(f.stem.split("_")[1])
        if k not in pat.index:
            continue
        tc = float(c.t_cap(pat.loc[k, "t_y"]))
        if tc > TCAP_MAX:
            continue
        q = np.abs(read_vtu(f)["Q_frac"]).astype(float)[:nf]
        if "chan0" not in grp:
            o = np.argsort(q)[::-1]
            n90 = int(np.searchsorted(np.cumsum(q[o]), 0.9 * q.sum()) + 1)
            g0 = np.zeros(nf, bool); g0[o[:n90]] = True
            grp["chan0"] = g0
        d = float(pat.loc[k, "dissolved"])
        r = dict(key, k=k, t_cap=tc, dissolved=d, prv=prv(q, V), sumq=float(q.sum()), S=float((q ** 2 / V).sum()))
        for g in GROUPS:
            s = grp[g]
            r[f"prv_{g}"] = prv(q[s], V[s]) if s.sum() > 1 else np.nan
            r[f"S_{g}"] = float((q[s] ** 2 / V[s]).sum())
            r[f"n_{g}"] = int(s.sum())
        states.append(r)
        if scale == "1km":
            for i in range(len(E) - 1):
                w = ov[:, i]
                s = w > 0
                if s.sum() >= 2:
                    bins.append(dict(key, k=k, dissolved=d, bin=i, n_frac=int(s.sum()), prv=prv(q[s], V[s] * w[s])))
    return states, bins


def spanning_minima(B):
    r = []
    for (sc, mo, p, sg, s, b), h in B.groupby(["scale", "mode", "p32", "sigma", "seed", "bin"]):
        h = h.sort_values("k")
        y = h.prv / h.prv.iloc[0]
        r.append(dict(mode=mo, p32=p, sigma=sg, seed=s, bin=b, min_rel=y.min(), d_at_min=h.dissolved[y.idxmin()], end_rel=y.iloc[-1]))
    r = pd.DataFrame(r)
    out = r.groupby(["mode", "bin"])[["min_rel", "d_at_min", "end_rel"]].median().reset_index()
    out["n_runs"] = r.groupby(["mode", "bin"]).size().values
    return out


def decomposition(S):
    runs = []
    for key, h in S.groupby(["scale", "mode", "p32", "sigma", "seed"]):
        h = h.sort_values("k").reset_index(drop=True)
        h["d"] = np.maximum.accumulate(h.dissolved.values)
        i = h.prv.idxmin()
        r = dict(zip(["scale", "mode", "p32", "sigma", "seed"], key), d_net_min=h.d[i], depth=h.prv[i] / h.prv[0],
                 dS_rel=(h.S[i] - h.S[0]) / h.S[0], dsumq_rel=(h.sumq[i] - h.sumq[0]) / h.sumq[0])
        for g in GROUPS:
            r[f"dS_share_{g}"] = (h[f"S_{g}"][i] - h[f"S_{g}"][0]) / (h.S[i] - h.S[0]) if h.S[i] != h.S[0] else np.nan
            r[f"S0_share_{g}"] = h[f"S_{g}"][0] / h.S[0]
            r[f"n_{g}"] = int(h[f"n_{g}"][0])
            j = h[f"prv_{g}"].idxmin()
            r[f"d_min_{g}"] = h.d[j]
            r[f"depth_{g}"] = h[f"prv_{g}"][j] / h[f"prv_{g}"][0]
        runs.append(r)
    R = pd.DataFrame(runs)
    T = []
    for (sc, mo), h in R.groupby(["scale", "mode"]):
        for g in GROUPS:
            dd = h[f"d_min_{g}"] - h.d_net_min
            T.append(dict(scale=sc, mode=mo, group=g, n=len(h), rho=spearmanr(h[f"d_min_{g}"], h.d_net_min).statistic,
                          share_within_005=float((dd.abs() <= 0.05).mean()), median_diff=float(dd.median()),
                          dS_share_median=float(h[f"dS_share_{g}"].median()), S0_share_median=float(h[f"S0_share_{g}"].median()),
                          n_frac_median=float(h[f"n_{g}"].median()), group_depth_median=float(h[f"depth_{g}"].median())))
    return R, pd.DataFrame(T)


def main():
    jobs = [(str(r), "1km") for r in sorted(P1.glob("L2_r15_p*_sg*_seed*/gyp*__phase1")) if (r / "patterns.csv").exists()]
    jobs += [(str(r), "2km") for r in sorted((HERE / "scale2km").glob("L2_r15_p*_sg*_seed*/gyp*__phase1"))
             if (r / "patterns.csv").exists() and (PV / f"S2KM__{r.parent.name}__{r.name}").exists()]
    with Pool(3) as p:
        res = p.map(one, jobs)
    S = pd.DataFrame([r for s, _ in res for r in s])
    B = pd.DataFrame([r for _, b in res for r in b])
    B.to_csv(P1 / "xbin_spanning.csv", index=False)
    M = spanning_minima(B)
    M.to_csv(P1 / "xbin_spanning_minima.csv", index=False)
    R, T = decomposition(S)
    R.to_csv(P1 / "prv_decomposition_runs.csv", index=False)
    T.to_csv(P1 / "prv_decomposition_tests.csv", index=False)
    pd.set_option("display.width", 250)
    print(len(jobs), "runs")
    print(M.round(3).to_string(index=False))
    for mo, h in M.groupby("mode"):
        print(mo, "A pass:", bool((h.end_rel - 1).abs().max() <= 0.05), "| rho(bin, d_at_min) =", round(spearmanr(h.bin, h.d_at_min).statistic, 3),
              "| max |end-1| =", round((h.end_rel - 1).abs().max(), 3))
    print(T.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
