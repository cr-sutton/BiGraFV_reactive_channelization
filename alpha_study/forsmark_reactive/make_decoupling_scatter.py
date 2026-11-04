#!/usr/bin/env python3
"""
Per-fracture flow share against open-pore-volume share at the four stages (P32 x6, sigma 1, seed 1): the decoupling of
flow and pore space as data.  Points on the 1:1 line carry flow in proportion to their open space; above it, flow crosses
fractures with little open space (still mineral-filled); below, open space carries little flow.  Colour = position along
the flow direction.  Reads paraview/<net>__<run>__mech/fractures_KKK.vtu (prep_mechanism_vtu.py).

  python3 forsmark_reactive/make_decoupling_scatter.py -> phase1/figures/decoupling_scatter_<mode>.png
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import vtk
from vtk.util.numpy_support import vtk_to_numpy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
NET = "L2_r15_p6.0_sg1.0_seed1"
STAGES = [(0.05, "1 · pore space opens"), (0.2, "2 · front runs the paths"), (0.45, "3 · breakthrough"), (1.0, "4 · widening")]
INK2, GRID = "#52514e", "#e6e5e1"

for mode, run, lab in (("gyponly", "gypsum", "gypsum only"), ("gypcal", "gypsum_calcite", "gypsum → calcite")):
    d = ROOT / "paraview" / f"{NET}__{run}__uncorrected_graph__phase1__mech"
    st = pd.read_csv(d / "states.csv")
    st = st[st.t_cap > 0]
    fig, axs = plt.subplots(1, 4, figsize=(14, 3.9), sharex=True, sharey=True)
    for ax, (tc, title) in zip(axs, STAGES):
        r = st.iloc[(np.log(st.t_cap) - np.log(tc)).abs().argmin()]
        rd = vtk.vtkXMLUnstructuredGridReader(); rd.SetFileName(str(d / f"fractures_{int(r.k):03d}.vtu")); rd.Update()
        cd = rd.GetOutput().GetCellData()
        g = lambda n: vtk_to_numpy(cd.GetArray(n)).astype(float)
        q, p, x = 10 ** g("log10_Q"), 10 ** g("log10_pore"), g("x_center")
        ok = (q > 1e-7) & (p > 1e-7)
        sc = ax.scatter(p[ok], q[ok], c=x[ok], cmap="cividis", vmin=-500, vmax=500, s=7, lw=0, alpha=0.75)
        ax.plot([1e-7, 1], [1e-7, 1], color="#0b0b0b", lw=1)
        ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(1e-6, 0.3); ax.set_ylim(1e-6, 0.3)
        ax.grid(color=GRID, lw=0.8)
        ax.set_title(f"{title}\ncapacity time {r.t_cap:.2g}", fontsize=9.5)
        ax.set_xlabel("share of open pore volume", fontsize=9, color=INK2)
        ax.tick_params(labelsize=8, colors=INK2)
        ax.text(2e-6, 0.12, "more flow\nthan space", fontsize=8, color=INK2, va="top")
        ax.text(0.2, 2e-6, "space without\nflow", fontsize=8, color=INK2, ha="right")
    axs[0].set_ylabel("share of injected flow", fontsize=9, color=INK2)
    cb = fig.colorbar(sc, ax=axs, fraction=0.015, pad=0.01)
    cb.set_label("x (m): inlet −500 → outlet +500", fontsize=8); cb.ax.tick_params(labelsize=7)
    fig.suptitle(f"{lab}: each dot is one fracture (P32 ×6, σ = 1, seed 1); the line is flow in proportion to open space", fontsize=10.5, y=1.07)
    fig.savefig(HERE / "phase1" / "figures" / f"decoupling_scatter_{mode}.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
print("ok")
