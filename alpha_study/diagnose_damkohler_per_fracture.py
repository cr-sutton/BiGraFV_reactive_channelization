#!/usr/bin/env python3
"""
A-priori per-fracture Damkohler diagnostic from a flow-only graph solve
(no reactive run, no DFN needed).

For each fracture f (graph cell f), with throughflow Q_f scaled to the
injection rate and volume V_f (aperture x area):

  Da_gyp,f = k_gyp * a_gyp * V_f / (Q_f * c_sat)
             a_gyp = SSA * rho_gyp * VF0   (reactive area per bulk volume)
  Da_cal,f = k_cal * a_cal * V_f / (Q_f * c_CO3,inj)
  t_clear,f = n_gyp,f / (Q_f * c_cap)     time to empty f if fed fresh water;
                                          a lower bound (upstream fractures
                                          saturate the water first)

Da_f is the ratio of fracture length to reaction penetration length
(regimes paper, Eq. 14: c = c0 exp(-2 k_eff x / q)).  Da_f >> 1 means the
reaction is at local equilibrium inside the fracture, so a dissolution
front sits inside it and one well-mixed cell per fracture smears that front.
The well-mixed/plug-flow conversion ratio (e^Da - 1)/Da (a candidate
surface-area correction) is only meaningful for Da_f <~ 3.

Optional --dfn: DFN fracture throughflow from cross-fracture faces (dfnWorks
assigns intersection nodes to one fracture, so this is approximate) for a
check of the graph Q_f.

  python3 diagnose_damkohler_per_fracture.py reactive_TPL_6x4x4m/seed4221 --rate 3.2195 --dfn
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "physics_upscaling"))
from write_corrected_bigrafv_inputs import read_uge  # noqa: E402

SEC_PER_Y = 365.25 * 86400
K_GYP, K_CAL = 7.382575853955734e-05, 2.287975768343148e-05   # mol/m^2/s, template deck
SSA_GYP, A_CAL = 750.0, 200.0           # m^2/kg gypsum; m^2/m^3 bulk calcite (template)
RHO_GYP = 0.17217 / 74.69e-6            # kg/m^3 from hanford.dat molar mass / volume
VF0, VM_GYP = 0.77, 74.69e-6
C_SAT, C_CO3 = 16.5, 100.0              # mol/m^3: measured dilute-water capacity; injected CO3


def face_fluxes(darcyvel):
    d = np.loadtxt(darcyvel)
    return d[:, 0].astype(int), d[:, 1].astype(int), d[:, 2] * d[:, 4]   # i, j, Q_ij (m^3/s, i->j)


def throughflow(i, j, q, owner):
    """Per-group throughflow max(inflow, outflow) over faces that cross groups."""
    oi, oj = owner[i - 1], owner[j - 1]
    m = oi != oj
    inflow, outflow = {}, {}
    for a, b, f in zip(oi[m], oj[m], q[m]):
        src, dst = (a, b) if f > 0 else (b, a)
        outflow[src] = outflow.get(src, 0.0) + abs(f)
        inflow[dst] = inflow.get(dst, 0.0) + abs(f)
    keys = set(inflow) | set(outflow)
    return {k: max(inflow.get(k, 0.0), outflow.get(k, 0.0)) for k in keys}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("seed_dir", type=Path)
    ap.add_argument("--model", default="graph_geo")
    ap.add_argument("--rate", type=float, required=True, help="injection rate (m^3/y)")
    ap.add_argument("--dfn", action="store_true")
    ap.add_argument("--k-gypsum-mult", type=float, default=1.0, help="deck --k-gypsum-mult")
    ap.add_argument("--k-calcite-mult", type=float, default=1.0, help="deck --k-calcite-mult")
    ap.add_argument("--inj-co3", type=float, default=C_CO3 / 1000, help="deck --inj-co3 (mol/L), sets c_CO3 of Da_cal")
    ap.add_argument("--out-dir", type=Path, default=None, help="default SEED_DIR/analysis_single_stage")
    a = ap.parse_args()
    k_gyp, k_cal, c_co3 = K_GYP * a.k_gypsum_mult, K_CAL * a.k_calcite_mult, 1000 * a.inj_co3
    a_gyp = SSA_GYP * RHO_GYP * VF0                 # m^2/m^3 bulk, initial (VOLUME_FRACTION_RATIO = 1 at t = 0)
    fo_net = k_cal * A_CAL / (k_gyp * a_gyp)        # Fogler number with areas: (k a)_calcite / (k a)_gypsum
    sd = a.seed_dir.resolve()
    fs = json.loads((sd / "flow_summary.json").read_text())
    nf = fs["geometric"]["n_fractures"]
    md = sd / f"model_{a.model}"
    cells, _ = read_uge(md / "full_mesh_vol_area.uge")
    owner = np.arange(1, len(cells) + 1)          # graph: one cell per fracture, helpers after
    i, j, q = face_fluxes(md / "darcyvel.dat")
    q_in = {"graph_geo": fs["Q_graph_geo"], "graph_raw": fs["Q_graph_raw"]}[a.model]
    scale = a.rate / SEC_PER_Y / q_in
    Qf = throughflow(i, j, q * scale, owner)
    area = np.loadtxt(sd / "model_dfn" / "dfnGen_output" / "surface_area_Final.dat", skiprows=1)[:nf]
    rows = []
    for f in range(1, nf + 1):
        V, Q = cells[f - 1, 4], Qf.get(f, 0.0)
        n_gyp = V * VF0 / VM_GYP
        rows.append(dict(fracture=f, area_m2=area[f - 1], volume_m3=V, Q_m3s=Q, Q_frac=Q * SEC_PER_Y / a.rate,
                         tau_res_s=V * (1 - VF0) / Q if Q > 0 else np.inf,
                         Da_gyp=k_gyp * SSA_GYP * RHO_GYP * VF0 * V / (Q * C_SAT) if Q > 0 else np.inf,
                         Da_cal=k_cal * A_CAL * V / (Q * c_co3) if Q > 0 else np.inf,
                         t_clear_y=n_gyp / (Q * C_SAT) / SEC_PER_Y if Q > 0 else np.inf))
    df = pd.DataFrame(rows)
    if a.dfn:
        dd = sd / "model_dfn"
        mat = np.array([int(l.split()[0]) for l in (dd / "materialid.dat").read_text().splitlines()[3:] if l.strip()])
        i2, j2, q2 = face_fluxes(dd / "darcyvel.dat")
        Qd = throughflow(i2, j2, q2 * a.rate / SEC_PER_Y / fs["Q_dfn"], mat)
        df["Q_dfn_m3s_approx"] = [Qd.get(f, 0.0) for f in df.fracture]
    out = a.out_dir or sd / "analysis_single_stage"
    out.mkdir(exist_ok=True)
    df.to_csv(out / f"damkohler_{a.model}.csv", index=False)
    flowing = df[df.Q_frac > 1e-3]
    w = flowing.Q_m3s / flowing.Q_m3s.sum()
    summ = dict(model=a.model, n_fractures=nf, n_flowing=len(flowing),
                Da_gyp_min=float(flowing.Da_gyp.min()), Da_gyp_median=float(flowing.Da_gyp.median()),
                Da_cal_min=float(flowing.Da_cal.min()), Da_cal_median=float(flowing.Da_cal.median()),
                frac_flow_Da_cal_lt_3=float(w[flowing.Da_cal < 3].sum()),
                t_clear_y_quantiles=dict(zip(("p10", "p50", "p90"), np.quantile(flowing.t_clear_y, [0.1, 0.5, 0.9]).tolist())))
    if (a.k_gypsum_mult, a.k_calcite_mult, a.inj_co3) != (1.0, 1.0, C_CO3 / 1000):   # default summaries unchanged
        summ.update(k_gypsum_mult=a.k_gypsum_mult, k_calcite_mult=a.k_calcite_mult, inj_co3_M=a.inj_co3)
    summ["fo_net"] = fo_net
    (out / f"damkohler_{a.model}_summary.json").write_text(json.dumps(summ, indent=1))
    fig, axs = plt.subplots(1, 3, figsize=(14, 4))
    axs[0].loglog(flowing.Q_frac, flowing.Da_gyp, "o", label="gypsum"); axs[0].loglog(flowing.Q_frac, flowing.Da_cal, "s", label="calcite")
    axs[0].axhline(1, color="k", lw=0.8); axs[0].set_xlabel("Q_f / Q_in"); axs[0].set_ylabel("Da_f"); axs[0].legend()
    axs[1].loglog(flowing.Q_frac, flowing.t_clear_y, "o"); axs[1].set_xlabel("Q_f / Q_in"); axs[1].set_ylabel("t_clear,f (y, fresh feed)")
    if a.dfn:
        axs[2].loglog(df.Q_m3s, df.Q_dfn_m3s_approx, "o"); lim = [df.Q_m3s[df.Q_m3s > 0].min(), df.Q_m3s.max()]
        axs[2].plot(lim, lim, "k-", lw=0.8); axs[2].set_xlabel(f"Q_f {a.model} (m$^3$/s)"); axs[2].set_ylabel("Q_f DFN (approx)")
    fig.tight_layout(); fig.savefig(out / f"damkohler_{a.model}.png", dpi=110)
    print(json.dumps(summ, indent=1))
    print(f"fo_net {fo_net:.4e}  = k_cal a_cal / (k_gyp a_gyp) = {k_cal:.4e} x {A_CAL:g} / ({k_gyp:.4e} x {a_gyp:.4e})")


if __name__ == "__main__":
    main()
