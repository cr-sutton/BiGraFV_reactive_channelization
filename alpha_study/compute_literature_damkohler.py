#!/usr/bin/env python3
"""
Network- and fracture-scale Damköhler numbers from published definitions only,
for the graph-only networks (state 0: unreacted, flow-only TPFA solve at the run rate).

Network scale (one number per network and chemistry)
  Hyman, Szawełło, Kang & Szymczak (2026, JGR Solid Earth, 10.1029/2025JB033004), Eqs. 24-25:
      Da_net = (2 k w0 L0 / Q0) / (1 + G),   G = 2 k b0 / (D Sh),   Sh = 8
      b0, w0 mean initial aperture and fracture width, L0 total network length, Q0 total flow.
      Regimes reported there: 2e-4 mild, 2e-3 strong channelization, 2e-2 wormholing (G = 0.1-5).

Fracture scale (a distribution over flowing fractures)
  (a) the same framework per fracture (Szymczak & Ladd 2012; Hyman et al. 2026 Eqs. 14, 23): the
      penetration exponent of one fracture, Da_f = 2 k_eff w_f L_f / Q_f, k_eff = k / (1 + 2 k b_f/(D Sh))
  (b) Pachalieva, Hyman, O'Malley, Srinivasan & Viswanathan (2024, Front. Environ. Sci.,
      10.3389/fenvs.2024.1454295), Sec. 2.2.1.3: Q_f = 1/2 sum_j |Q_fj|,
      Da_I,f = k' S_f / Q_f,  Da_II,f = k' r_f / D,  k' = k_mol V_m  (mol m-2 s-1 x m3 mol-1 -> m s-1)

Geometry inputs are fracture-plane proxies for the paper's edge-graph quantities (Karen review,
28 Oct): the paper's b0, w0 are the mean initial aperture and fracture-plane width of its graph
edges and L0 is the total edge length; here w_f = L_f = sqrt(S_f) for square fractures, so
w0 = mean(sqrt S), L0 = sum(sqrt S), b0 = mean(sqrt(12 k)).  Because w0 L0 != sum(S) unless all
fractures are the same size, Da_net is ~20-25% below the value using the total fracture area;
column Da_net_area uses 2 k sum(S)/Q0 /(1+G) instead.  Report Da_net as "Eq. 24 with
fracture-plane proxies for w0, L0".

Rate constant k (m/s) in (a) and the network Da: the linear law J = k C with C the reactant
concentration. For dissolution by undersaturated water C = c_s - c (Szymczak & Ladd 2009,
Eqs. 6-8), so k = k_mol / c_s; for acid, C = [H+] and k = k_H (mol m-2 s-1 per mol/L) / 1000.
These rates are per unit fracture-wall area (the literature models react on the two walls).

PFLOTRAN reacts on the mineral surface SSA x mass, R = A_min / (2 S_f) times the wall area.
Columns *_model use k x R (the rate the simulation actually applies per wall area); columns
without the suffix use the intrinsic k on the walls, as written in the papers.

  python3 compute_literature_damkohler.py [NET_DIR ...]   (default: all 500 m and km networks)
  -> km_scale_graph_only/literature_damkohler.csv
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

import h5py
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE / "physics_upscaling")]
from add_inlet_manifold import add_inlet_manifold  # noqa: E402
from analyze_km_dissolution_patterns import poly_area, read_polygons, solve  # noqa: E402
from compute_keff_tpfa import read_uge  # noqa: E402

KM = HERE / "km_scale_graph_only"
D_MOL, SH = 1.0e-9, 8.0                 # deck diffusion coefficient (m2/s); Sherwood number (Hyman et al. 2026)
# chemistry as run: k_mol (mol m-2 s-1), c_s (mol m-3), V_m (m3/mol), SSA (m2/kg), rho (kg/m3), fill VF
CHEM = {
    "gypsum": dict(k_lin=7.382575853955734e-05 * 21.95 / 16.6, k_mol=7.382575853955734e-05 * 21.95,
                   V_m=74.69e-6, ssa=750.0, rho=2305.0, vf=0.77,
                   note="Palandri & Kharaka log k -2.79; c_s 16.6 mol/m3 (batch, dilute water)"),
    "quartz": dict(k_lin=1.0e-12 / 0.1, k_mol=1.0e-12, V_m=22.688e-6, ssa=22.5, rho=2648.0, vf=0.99,
                   note="k 1e-12 mol/m2/s (quartz paper); c_s 0.1 mol/m3"),
    "acid_calcite": dict(k_lin=10 ** -0.30 / 1000.0, k_mol=10 ** -0.30 * 10 ** -1.5, V_m=36.934e-6, ssa=100.0,
                         rho=2710.0, vf=0.77,
                         note="acid mechanism log k -0.30 per unit a(H+), reactant = [H+] (pH 1.5 -> k_mol at inlet)"),
    # CO2-charged water (pCO2 1 bar, pH 3.91): undersaturation-driven, so k = k_mol / c_s with k_mol the sum of the
    # three Palandri & Kharaka mechanisms at the inlet (acid 0.5012 a_H, neutral 1.549e-6, carbonate 9.772e-3 a_CO2(aq));
    # an upper bound, since all three fall as the water reacts.  c_s = 8.40 mol/m3 (batch capacity)
    "co2_calcite": dict(k_lin=(0.5012 * 10 ** -3.906 + 1.549e-6 + 9.772e-3 * 0.0340) / 8.40,
                        k_mol=0.5012 * 10 ** -3.906 + 1.549e-6 + 9.772e-3 * 0.0340, V_m=36.934e-6, ssa=100.0,
                        rho=2710.0, vf=0.77, note="pCO2 1 bar water; inlet rate, three P&K mechanisms; c_s 8.40 mol/m3"),
}


def state0(net):
    src = net / "model_graph_raw"
    fs = json.loads((net / "flow_summary.json").read_text())
    rate, nf = fs["Q_graph_raw"], fs["n_fractures"]
    polys = read_polygons(src / "dfnGen_output" / "polygons.dat")
    S = np.array([poly_area(P) for P in polys])[:nf]
    radii = np.loadtxt(src / "dfnGen_output" / "radii_Final.dat", skiprows=2)[:nf, 0]
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        for f in ("full_mesh_vol_area.uge", "dfn_properties.h5", "boundary_left_w.ex", "boundary_right_e.ex"):
            shutil.copy(src / f, d / f)
        add_inlet_manifold(d)
        cells, conns = read_uge(d / "full_mesh_vol_area.uge")
        with h5py.File(d / "dfn_properties.h5") as h:
            ids = np.asarray(h["Cell Ids"]).astype(int)
            k = np.empty(len(cells))
            k[ids - 1] = np.asarray(h["Permeability"], float)
        own = np.zeros(len(cells), int)
        own[:nf] = np.arange(1, nf + 1)
        own[nf:] = -np.arange(1, len(cells) - nf + 1)
        _, flux, ci, cj = solve(d, cells, conns, k, rate)
    oi, oj = own[ci - 1], own[cj - 1]
    m = oi != oj
    Q = np.zeros(nf)                                       # Q_f = 1/2 sum |Q_fj| (Pachalieva et al. 2024; Hyman 2020)
    for a, b, q in zip(oi[m], oj[m], np.abs(flux[m])):
        if a > 0:
            Q[a - 1] += q
        if b > 0:
            Q[b - 1] += q
    Q *= 0.5
    b = np.sqrt(12 * k[:nf])
    return dict(rate=rate, nf=nf, S=S, r=radii, b=b, Q=Q)


def damkohler(net):
    s = state0(net)
    S, b, Q, r, Q0 = s["S"], s["b"], s["Q"], s["r"], s["rate"]
    w = L = np.sqrt(S)                                     # square fractures (aspect 1): width = length = sqrt(area)
    flowing = Q > 1e-3 * Q0
    b0, w0, L0 = b.mean(), w.mean(), L.sum()
    rows = []
    for chem, c in CHEM.items():
        R = c["ssa"] * c["rho"] * c["vf"] * b / 2         # mineral surface / wall area, per fracture
        Rm = float(np.average(R, weights=S))
        out = dict(network=net.name, chemistry=chem, n_fractures=s["nf"], Q0_m3s=Q0, b0_m=b0, w0_m=w0, L0_m=L0,
                   R_model_mean=Rm, flowing_share=float(flowing.mean()))
        for tag, kk in (("", c["k_lin"]), ("_model", c["k_lin"] * Rm)):
            G = 2 * kk * b0 / (D_MOL * SH)
            out[f"G{tag}"] = G
            out[f"Da_net{tag}"] = (2 * kk * w0 * L0 / Q0) / (1 + G)
            out[f"Da_net_area{tag}"] = (2 * kk * S.sum() / Q0) / (1 + G)      # total fracture area instead of w0 L0
        for tag, kk in (("", c["k_lin"]), ("_model", c["k_lin"] * R)):
            keff = kk / (1 + 2 * kk * b / (D_MOL * SH))
            da = 2 * keff * w * L / np.maximum(Q, 1e-300)
            for p in (10, 50, 90):
                out[f"Da_f{tag}_p{p}"] = float(np.percentile(da[flowing], p))
        kp = c["k_mol"] * c["V_m"]
        daI, daII = kp * S / np.maximum(Q, 1e-300), kp * r / D_MOL
        for p in (10, 50, 90):
            out[f"DaI_f_p{p}"] = float(np.percentile(daI[flowing], p))
            out[f"DaII_f_p{p}"] = float(np.percentile(daII[flowing], p))
        rows.append(out)
    return rows


def main():
    nets = [Path(a).resolve() for a in sys.argv[1:]] or [
        p for p in sorted((KM / "ensemble_500x200x200m").glob("500x*")) + sorted(KM.glob("1000x*_fractures"))
        if (p / "flow_summary.json").exists()]
    f = KM / "literature_damkohler.csv"
    old = pd.read_csv(f) if f.exists() else pd.DataFrame()
    rows = []
    for n in nets:
        rows += damkohler(n)
        print(n.name, "done", flush=True)
    new = pd.DataFrame(rows)
    out = pd.concat([old[~old.network.isin(new.network)] if len(old) else old, new])
    out.to_csv(f, index=False)
    print(new[["network", "chemistry", "Da_net", "Da_net_area", "G", "Da_net_model", "G_model", "Da_f_p50", "Da_f_model_p50",
               "DaI_f_p50"]].to_string())


if __name__ == "__main__":
    main()
