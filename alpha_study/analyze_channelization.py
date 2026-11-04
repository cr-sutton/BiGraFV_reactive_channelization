#!/usr/bin/env python3
"""
Channelization metrics and network descriptors for the large graph-only
gypsum runs (uncorrected BiGraFV, 500 m ensemble + km networks).

Per run (every saved state; flow re-solved on the frozen permeability with the
same TPFA as analyze_km_dissolution_patterns.py) -> RUN_DIR/channelization.csv:
  dissolved, k_eff_ratio, dQ_P32   as in patterns.csv
  n90, n90_share                   fractures carrying 90% of throughflow (count, share of all fractures)
  n50                              fractures carrying 50%
  flow_gini                        Gini of throughflow over fractures
  top1_share                       share of throughflow in the top 1% of fractures
  backbone_share                   share of fractures carrying > 1e-3 of the injected rate
  dry_area                         share of fracture area carrying < 1e-5 of the injected rate (near-stagnant;
                                   every cell stays saturated)
  overlap0                         |S90(k) & S90(0)| / |S90(k)|: share of the current 90%-set
                                   that was already in the initial 90%-set (channel inheritance)
  n_exchange                       fracture pairs that exchange flow (intersections)
  pr_exchange, pr_exchange_share   participation ratio of the volumetric flow exchanged between
                                   fractures, (sum q_e)^2 / sum q_e^2: effective number of
                                   intersections carrying the flow, and that over n_exchange
  pr_fracture, pr_fracture_share   the same over fracture throughflow (area-free dQ/P32)
  pr_fracture_vol                  volume-weighted participation ratio (sum Q)^2 / sum(Q^2 / w), w = cell volume
                                   share (UGE): the effective fraction of the fracture volume carrying the
                                   flow (1 if every fracture carries flow in proportion to its volume)
  pr_fracture_area                 the same with polygon-area weights
  n90_vol_share, n90_area_share    volume / area share of the fractures carrying 90% of the flow
  t_pv                             t / tau, tau = total fracture volume (UGE) / injection rate

Per network (state 0 of the linear run) -> km_scale_graph_only/channelization_networks.csv:
  n_fractures, sigma, p32_family, mean_degree, n_inlet, n_outlet,
  backbone_share0, dead_share0 (fractures with < 1e-5 of the rate),
  n90_share0, dQ_P32_0, flow_gini0, lnT_sd_backbone (s.d. of ln transmissivity on
  the backbone), corr_lnQ_lnT (backbone), corr_lnQ_area (backbone)

Per fracture (state 0 + peak channelization of each run) -> RUN_DIR/channel_fractures.csv:
  Q0 share, rank0, in S90 at start / at peak, time-to-half-dissolved

  python3 analyze_channelization.py [RUN_DIR ...]      (default: all *_dirichlet gypsum runs)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import h5py
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE / "physics_upscaling")]
from analyze_km_dissolution_patterns import gini, poly_area, read_polygons, solve  # noqa: E402
from bipartite_pressure_solutions_functions import read_scalar_from_vtk  # noqa: E402
from compute_keff_tpfa import read_ex, read_uge  # noqa: E402
from diagnose_damkohler_per_fracture import throughflow  # noqa: E402

KM = HERE / "km_scale_graph_only"
LEVERS = ("linear_dirichlet", "cubic_dirichlet", "cubic_fill_dirichlet")


def all_runs():
    out = []
    for net in sorted((KM / "ensemble_500x200x200m").glob("500x*")) + sorted(KM.glob("1000x*_fractures")):
        if not net.is_dir():
            continue
        for lev in LEVERS:
            r = net / f"gypsum__uncorrected_graph__{lev}"
            if (r / "patterns.csv").exists():
                out.append(r)
    return out


def exchange_flows(flux, ci, cj, nf):
    """Volumetric flow exchanged between each pair of intersecting fractures:
    |net flux| summed over all UGE connections joining the two fracture cells
    (boundary helper and manifold cells excluded)."""
    m = (ci <= nf) & (cj <= nf) & (ci != cj)
    a, b, f = ci[m], cj[m], flux[m]
    sgn = np.where(a < b, 1.0, -1.0)                      # orient every pair low -> high id
    lo, hi = np.minimum(a, b), np.maximum(a, b)
    key = lo.astype(np.int64) * (nf + 1) + hi
    u, inv = np.unique(key, return_inverse=True)
    return np.abs(np.bincount(inv, weights=sgn * f, minlength=len(u)))


def pr(x):
    """Participation ratio (sum x)^2 / sum x^2: the effective number of
    members carrying the flow (= N if all equal, 1 if one carries all)."""
    x = np.asarray(x, float)
    return float(x.sum() ** 2 / (x ** 2).sum()) if (x ** 2).sum() > 0 else 0.0


def pr_w(x, w):
    """Weighted participation ratio (sum x)^2 / sum(x^2 / w) with sum w = 1: the effective share of
    the weight (volume, area) carrying the flow; 1 when x is proportional to w."""
    x = np.asarray(x, float); w = np.asarray(w, float); w = w / w.sum()
    m = w > 0
    return float(x[m].sum() ** 2 / (x[m] ** 2 / w[m]).sum()) if (x[m] ** 2).sum() > 0 else 0.0


def s90(Q, frac=0.9):
    o = np.argsort(Q)[::-1]
    n = int(np.searchsorted(np.cumsum(Q[o]) / Q.sum(), frac) + 1)
    return o[:n]


def analyze(run):
    sched = json.loads((run / "single_stage.in.schedule.json").read_text())
    vf0 = sched.get("vf0", 0.77)
    mineral = sched.get("mineral", "Gypsum")
    times = [0.0] + list(sched["vtk_times_y"])
    polys = read_polygons(run / "polygons.dat")
    nf = len(polys)
    area = np.array([poly_area(P) for P in polys])
    cells, conns = read_uge(run / "full_mesh_vol_area.uge")
    vol = cells[:nf, 4]
    own = np.zeros(len(cells), int)
    own[:nf] = np.arange(1, nf + 1)
    own[nf:] = -np.arange(1, len(cells) - nf + 1)
    rate = sched["rate_m3y"] / 3.15576e7
    tau_pv = float(vol.sum()) / sched["rate_m3y"]                          # network volumes injected per year
    pat = pd.read_csv(run / "patterns.csv").set_index("k")
    vtks = sorted(run.glob("single_stage-*.vtk"), key=lambda p: int(p.stem.split("-")[1]))
    rows, Qs, diss_all, vf_init, S0 = [], {}, {}, None, None
    for vk in vtks:
        k = int(vk.stem.split("-")[1])
        if k not in pat.index:
            continue
        vf = np.asarray(read_scalar_from_vtk(str(vk), f"{mineral}_VF"), float)
        kk = np.asarray(read_scalar_from_vtk(str(vk), "Permeability"), float)
        if len(kk) < len(cells):
            kk = np.r_[kk, np.full(len(cells) - len(kk), kk.max())]
        _, flux, ci, cj = solve(run, cells, conns, kk[: len(cells)], rate)
        Qf = throughflow(ci, cj, flux, own)
        Q = np.array([Qf.get(f, 0.0) for f in range(1, nf + 1)]) / rate
        ex = exchange_flows(flux, ci, cj, nf) / rate
        if vf_init is None:
            vf_init = np.where(vf[:nf] > 0, vf[:nf], vf0)
        diss_all[k] = 1 - np.clip(vf[:nf] / vf_init, 0, 1)
        S = s90(Q)
        S0 = S if S0 is None else S0
        Qs[k] = Q
        o = np.sort(Q)[::-1]
        t_y = times[k] if k < len(times) else np.nan
        rows.append(dict(k=k, t_y=t_y, t_pv=t_y / tau_pv, dissolved=pat.loc[k, "dissolved"],
                         k_eff_ratio=pat.loc[k, "k_eff_ratio"], dQ_P32=pat.loc[k, "dQ_P32"],
                         n90=len(S), n90_share=len(S) / nf, n50=len(s90(Q, 0.5)), flow_gini=gini(Q),
                         top1_share=float(o[: max(1, nf // 100)].sum() / Q.sum()),
                         backbone_share=float((Q > 1e-3).mean()),
                         dry_area=float(area[Q < 1e-5].sum() / area.sum()),
                         overlap0=len(np.intersect1d(S, S0)) / len(S),
                         n_exchange=len(ex), pr_exchange=pr(ex), pr_exchange_share=pr(ex) / len(ex),
                         pr_fracture=pr(Q), pr_fracture_share=pr(Q) / nf,
                         pr_fracture_vol=pr_w(Q, vol), pr_fracture_area=pr_w(Q, area),
                         n90_vol_share=float(vol[S].sum() / vol.sum()), n90_area_share=float(area[S].sum() / area.sum())))
    d = pd.DataFrame(rows)
    d.to_csv(run / "channelization.csv", index=False)
    kpk = int(d.k[d.n90.idxmin()])
    Q0 = Qs[min(Qs)]
    rank0 = np.empty(nf, int)
    rank0[np.argsort(Q0)[::-1]] = np.arange(1, nf + 1)
    ks = sorted(diss_all)
    t_half = np.full(nf, np.nan)
    for k in ks[::-1]:
        t_half[diss_all[k] > 0.5] = times[k] if k < len(times) else np.nan
    fr = pd.DataFrame(dict(fracture=np.arange(1, nf + 1), area=area, Q0=Q0, rank0=rank0,
                           in_s90_start=np.isin(np.arange(nf), S0), in_s90_peak=np.isin(np.arange(nf), s90(Qs[kpk])),
                           Q_peak=Qs[kpk], t_half_dissolved_y=t_half))
    fr.to_csv(run / "channel_fractures.csv", index=False)
    return d, fr, dict(nf=nf, area=area, Q0=Q0, cells=cells, conns=conns, kpk=kpk)


def descriptors(run, info):
    net = run.parent
    nf, Q0, area, conns = info["nf"], info["Q0"], info["area"], info["conns"]
    with h5py.File(run / "dfn_properties.h5") as h:
        k = np.asarray(h["Permeability"], float)[:nf]
    T = k * np.sqrt(12 * k)                                   # k b with b = sqrt(12 k)
    i, j = conns[:, 0].astype(int), conns[:, 1].astype(int)
    m = (i <= nf) & (j <= nf)
    pairs = np.unique(np.sort(np.c_[i[m], j[m]], axis=1), axis=0)          # distinct intersecting neighbours
    deg = np.bincount(pairs.ravel() - 1, minlength=nf)
    fs = json.loads((net / "flow_summary.json").read_text()) if (net / "flow_summary.json").exists() else {}
    bb = Q0 > 1e-3
    lnQ, lnT, lnA = np.log(Q0[bb]), np.log(T[bb]), np.log(area[bb])
    n_in = len(read_ex(run / "boundary_left_w.ex"))
    n_out = len(read_ex(run / "boundary_right_e.ex"))
    o = np.sort(Q0)[::-1]
    return dict(network=net.name, n_fractures=nf, sigma=fs.get("aperture_sigma", 0.0), p32_family=fs.get("p32_family", np.nan),
                domain=" x ".join(f"{v:g}" for v in fs.get("domain", [])), mean_degree=float(deg.mean()),
                n_inlet=n_in, n_outlet=n_out, backbone_share0=float(bb.mean()), dead_share0=float((Q0 < 1e-5).mean()),
                n90_share0=float(np.searchsorted(np.cumsum(o) / o.sum(), 0.9) + 1) / nf,
                flow_gini0=gini(Q0), lnT_sd_backbone=float(lnT.std()), corr_lnQ_lnT=float(np.corrcoef(lnQ, lnT)[0, 1]),
                corr_lnQ_area=float(np.corrcoef(lnQ, lnA)[0, 1]))


def main():
    runs = [Path(a).resolve() for a in sys.argv[1:]] or all_runs()
    desc = {}
    for r in runs:
        d, fr, info = analyze(r)
        print(f"{r.parent.name}/{r.name}: {len(d)} states, n90 {d.n90.iloc[0]} -> min {d.n90.min()}", flush=True)
        if r.name.endswith("linear_dirichlet"):
            desc[r.parent.name] = descriptors(r, info)
    if desc:
        f = KM / "channelization_networks.csv"
        old = pd.read_csv(f) if f.exists() else pd.DataFrame()
        new = pd.DataFrame(desc.values())
        out = pd.concat([old[~old.network.isin(new.network)] if len(old) else old, new])
        out.to_csv(f, index=False)


if __name__ == "__main__":
    main()
