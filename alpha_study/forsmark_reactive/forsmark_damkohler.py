#!/usr/bin/env python3
"""
Network Damköhler number of the Forsmark networks at the rate the runs actually use, one network pore
volume per year (gypsum vf0 0.9, porosity 0.1), with the published definition of Hyman, Szawełło, Kang &
Szymczak (2026, JGR Solid Earth) Eqs. 24-25 as implemented in compute_literature_damkohler.py:
    Da_net = (2 k w0 L0 / Q0) / (1 + G),   G = 2 k b0 / (D Sh)
compute_literature_damkohler.py solves flow at the build rate (0.1 MPa) with vf0 0.77; here the fluxes are
rescaled to the run rate (flow is linear in the rate) and the PFLOTRAN area factor R uses vf0 0.9. Nothing
is written to km_scale_graph_only/literature_damkohler.csv.

  python3 forsmark_reactive/forsmark_damkohler.py NET_DIR [NET_DIR ...]   -> forsmark_reactive/forsmark_damkohler.csv
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent), str(HERE.parent / "physics_upscaling")]
import compute_literature_damkohler as lit  # noqa: E402
from write_corrected_bigrafv_inputs import read_uge  # noqa: E402

VF0 = 0.9
GYP = lit.CHEM["gypsum"]


def network_da(net: Path, k_mult: float = 1.0):
    s = lit.state0(net)
    cells, _ = read_uge(net / "model_graph_raw" / "full_mesh_vol_area.uge")
    q_run = cells[:, 4].sum() * (1 - VF0) / (365.25 * 86400)       # m^3/s, one pore volume per year
    scale = q_run / s["rate"]
    S, b, Q = s["S"], s["b"], s["Q"] * scale
    w = L = np.sqrt(S)
    flowing = Q > 1e-3 * q_run
    b0, w0, L0 = b.mean(), w.mean(), L.sum()
    R = GYP["ssa"] * GYP["rho"] * VF0 * b / 2
    Rm = float(np.average(R, weights=S))
    out = dict(network=net.name, Q0_m3s=q_run, build_to_run=1 / scale, b0_m=b0, w0_m=w0, L0_m=L0, R_model_mean=Rm)
    for tag, kk in (("", GYP["k_lin"] * k_mult), ("_model", GYP["k_lin"] * k_mult * Rm)):
        G = 2 * kk * b0 / (lit.D_MOL * lit.SH)
        out[f"G{tag}"] = G
        out[f"Da_net{tag}"] = (2 * kk * w0 * L0 / q_run) / (1 + G)
    keff = GYP["k_lin"] * k_mult * R
    keff = keff / (1 + 2 * keff * b / (lit.D_MOL * lit.SH))
    da_f = 2 * keff * w * L / np.maximum(Q, 1e-300)
    out["Da_f_model_p50"] = float(np.median(da_f[flowing]))
    return out


if __name__ == "__main__":
    rows = [network_da(Path(a).resolve()) for a in sys.argv[1:]]
    df = pd.DataFrame(rows)
    df.to_csv(HERE / "forsmark_damkohler.csv", index=False)
    pd.set_option("display.width", 200)
    print(df[["network", "Da_net", "G", "Da_net_model", "G_model", "Da_f_model_p50", "build_to_run"]].to_string(float_format="%.3g"))
