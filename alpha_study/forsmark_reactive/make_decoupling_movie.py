#!/usr/bin/env python3
"""
Flow / pore-space decoupling movie, one map per frame (network P32 x6, sigma 1, seed 1; both chemistries).

Inputs : paraview/<net>__<run>__mech/fractures_KKK.vtu + states.csv (prep_mechanism_vtu.py),
         phase1/phase1_mechanism.csv (pr_frac = PR_V, pr_pore, outlet_diss, front_x per state).
Outputs: phase1/figures/anim2/movie_<mode>.mp4 (3 fps), stage<i>_<mode>.png, stages_<mode>.png (2x2 contact sheet).

Per state and fracture f (all fractures of the network, not only those cut by the slices):
  share_f = Q_f / sum Q;  flowing = f is in the smallest set of fractures, sorted by share descending, whose shares add to >= 0.9
  open    = porosity_f > 0.5
  category 0 open & flowing (open channel), 1 open & not flowing (open space, little flow),
           2 filled & flowing (flow through filled rock), 3 filled & not flowing (idle)
Gauge = sum of share_f per category (sums to 1).  Maps = traces of the fracture polygons cut by z = 0 and z = +60 m
(vtkCutter, cell data inherited), thick lines coloured by category; dashed line = leading edge: downstream edge of the most downstream 100 m window (2 bins, flow-weighted) with dissolved
fraction >= 0.5, scanning from the outlet; the strip above shows the unsmoothed 50 m bin profile.  A single front is only
approximate in BiGraFV: a fracture dissolves as one cell along its whole length, so there are no in-plane fronts.
x < the edge is shaded.  Frames: states with t_cap <= 3.
Stages from the data: 1 until t_cap 0.1; 2 until outlet_diss > 0.05; 3 until PR_V minimum has passed and outlet_diss > 0.5; 4 after.

  python3 forsmark_reactive/make_decoupling_movie.py
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import vtk
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from vtk.util.numpy_support import numpy_to_vtk, vtk_to_numpy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / "phase1" / "figures" / "anim2"
NET = "L2_r15_p6.0_sg1.0_seed1"
TMAX = 3.0
ZS = [0.0, 60.0]
CATS = [("open channel", "#2a78d6", 5), ("open space, little flow", "#a9cdf2", 5),
        ("flow through filled rock", "#e4572e", 5), ("filled, idle", "#b9b9b2", 2)]
ORDER = [3, 1, 2, 0]                                  # draw order, channel on top
BG, INK, GRID = "#f2f2ef", "#2b2b29", "#d9d8d3"
STAGE = ["1  pore space opens", "2  front runs the paths", "3  breakthrough", "4  widening"]
plt.rcParams.update({"font.size": 12})


def read(f):
    r = vtk.vtkXMLUnstructuredGridReader(); r.SetFileName(str(f)); r.Update()
    return r.GetOutput()


def slice_segments(g, z):
    """Segments (n,2,2) of the slice at z and the index of the fracture cell each came from."""
    g2 = vtk.vtkUnstructuredGrid(); g2.ShallowCopy(g)
    a = numpy_to_vtk(np.arange(g.GetNumberOfCells(), dtype=np.int64)); a.SetName("cid")
    g2.GetCellData().AddArray(a)
    pl = vtk.vtkPlane(); pl.SetOrigin(0, 0, z); pl.SetNormal(0, 0, 1)
    c = vtk.vtkCutter(); c.SetCutFunction(pl); c.SetInputData(g2); c.Update()
    o = c.GetOutput()
    cid = vtk_to_numpy(o.GetCellData().GetArray("cid"))
    pts = vtk_to_numpy(o.GetPoints().GetData())
    seg, ids = [], []
    for i in range(o.GetNumberOfCells()):
        ce = o.GetCell(i)
        p = [pts[ce.GetPointId(j)][:2] for j in range(ce.GetNumberOfPoints())]
        for j in range(len(p) - 1):
            seg.append([p[j], p[j + 1]]); ids.append(cid[i])
    return np.array(seg), np.array(ids)


def categories(q, phi):
    s = q / q.sum()
    o = np.argsort(-s)
    cum = np.cumsum(s[o])
    n = int(np.searchsorted(cum, 0.9 - 1e-12)) + 1
    flowing = np.zeros(len(s), bool); flowing[o[:n]] = True
    opn = phi > 0.5
    return np.where(opn & flowing, 0, np.where(opn, 1, np.where(flowing, 2, 3))), s


def front_profile(q, d, x):
    """Flow-weighted dissolved fraction in 50 m bins of x_center (strip), and the leading edge: 2-bin (100 m) running
    flow-weighted mean (sum Q d / sum Q over bins b, b+1); edge = downstream edge of the most downstream window with
    value >= 0.5, scanning from the outlet (none -> -500)."""
    w = q / q.sum()
    ib = np.clip(((x + 500) // 50).astype(int), 0, 19)
    num = np.bincount(ib, w * d, 20); den = np.bincount(ib, w, 20)
    prof = np.where(den > 0, num / np.maximum(den, 1e-300), np.nan)
    front = -500.0
    for b in range(18, -1, -1):
        dd = den[b] + den[b + 1]
        if dd > 0 and (num[b] + num[b + 1]) / dd >= 0.5:
            front = -500.0 + 50 * (b + 2)
            break
    return prof, front


def stage_of(mech, k_min):
    """Stage 1..4 for every row of mech (sorted by k)."""
    st = np.ones(len(mech), int)
    st[mech.t_cap.values >= 0.1] = 2
    st[mech.outlet_diss.values > 0.05] = 3
    st[(mech.k.values > k_min) & (mech.outlet_diss.values > 0.5)] = 4
    return st


def run_mode(mode, label):
    run = "gypsum" if mode == "gyponly" else "gypsum_calcite"
    d = ROOT / "paraview" / f"{NET}__{run}__uncorrected_graph__phase1__mech"
    stt = pd.read_csv(d / "states.csv").set_index("k")
    m = pd.read_csv(HERE / "phase1" / "phase1_mechanism.csv")
    m = m[(m["mode"] == mode) & (m.p32 == 6.0) & (m.sigma == 1.0) & (m.seed == 1) & (m.tag == "phase1")].sort_values("k").reset_index(drop=True)
    win = m[m.t_cap <= TMAX]
    k_min = int(win.k.values[np.argmin(win.pr_frac.values)])
    m["stage"] = stage_of(m, k_min)
    segs = [slice_segments(read(d / "fractures_000.vtu"), z) for z in ZS]
    fr = m[m.t_cap <= TMAX].reset_index(drop=True)
    out = OUT / mode
    out.mkdir(parents=True, exist_ok=True)
    for f in out.glob("frame_*.png"):
        f.unlink()
    paths, fronts = [], []
    for i, r in fr.iterrows():
        k = int(r.k)
        g = read(d / f"fractures_{k:03d}.vtu")
        cd = g.GetCellData()
        q = np.abs(vtk_to_numpy(cd.GetArray("Q_frac")).astype(float))
        cat, share = categories(q, vtk_to_numpy(cd.GetArray("porosity")).astype(float))
        prof, fx = front_profile(q, vtk_to_numpy(cd.GetArray("fraction_dissolved")).astype(float),
                                 vtk_to_numpy(cd.GetArray("x_center")).astype(float))
        fronts.append(fx)
        gauge = [share[cat == c].sum() for c in range(4)]
        fig = plt.figure(figsize=(16, 14), facecolor="white")
        gs = fig.add_gridspec(5, 1, height_ratios=[0.07, 1, 1, 0.2, 0.85], hspace=0.42, left=0.06, right=0.97, top=0.835, bottom=0.05)
        ax = fig.add_subplot(gs[0])
        ax.imshow(prof[None, :], extent=(-500, 500, 0, 1), aspect="auto", cmap="Blues", vmin=0, vmax=1)
        ax.set_yticks([]); ax.set_xticks([]); ax.set_xlim(-500, 500)
        ax.text(0.0, 1.15, "dissolved fraction per 50 m bin, flow-weighted (white = no flow)", transform=ax.transAxes, ha="left", fontsize=11, color=INK)
        ax.axvline(fx, color=INK, ls="--", lw=2)
        for row, (z, (sg, ids)) in enumerate(zip(ZS, segs)):
            ax = fig.add_subplot(gs[row + 1])
            ax.set_facecolor(BG)
            if True:
                ax.axvspan(-500, fx, color="#ffffff", alpha=0.45, lw=0)
                ax.axvline(fx, color=INK, ls="--", lw=2)
            for c in ORDER:
                sel = cat[ids] == c
                ax.add_collection(LineCollection(sg[sel], colors=CATS[c][1], linewidths=CATS[c][2], capstyle="round"))
            ax.set_xlim(-500, 500); ax.set_ylim(-125, 125); ax.set_aspect("auto")
            ax.set_yticks([]); ax.set_xticks([-500, -250, 0, 250, 500] if row == 1 else [])
            for s in ax.spines.values():
                s.set_color(GRID)
            ax.text(0.005, 0.96, f"slice z = {z:+.0f} m", transform=ax.transAxes, va="top", fontsize=12, color=INK)
            if row == 0:
                ax.text(0.0, 1.14, "INLET  x = -500 m", transform=ax.transAxes, ha="left", fontsize=12, weight="bold", color=INK)
                ax.text(1.0, 1.14, "OUTLET  x = +500 m", transform=ax.transAxes, ha="right", fontsize=12, weight="bold", color=INK)
                if True:
                    ax.text(min(fx + 6, 60), 0.04, "leading edge: flow paths ≥ 50 % dissolved (100 m average)", ha="left", fontsize=12, color=INK, transform=ax.get_xaxis_transform())
            else:  # 100 m scale bar
                ax.plot([380, 480], [-105, -105], color=INK, lw=4, solid_capstyle="butt")
                ax.text(430, -95, "100 m", ha="center", va="bottom", fontsize=12, color=INK)
                ax.set_xlabel("x (m)", fontsize=12)
        ax = fig.add_subplot(gs[3])
        left = 0.0
        for c in range(4):
            ax.barh(0, gauge[c], left=left, color=CATS[c][1], height=0.8)
            if gauge[c] > 0.045:
                ax.text(left + gauge[c] / 2, 0, f"{100 * gauge[c]:.0f} %", ha="center", va="center", fontsize=13,
                        weight="bold", color="white" if c in (0, 2) else INK)
            left += gauge[c]
        ax.set_xlim(0, 1); ax.set_ylim(-0.6, 0.6); ax.set_yticks([]); ax.set_xticks([0, 0.25, 0.5, 0.75, 1])
        ax.set_xticklabels(["0", "25 %", "50 %", "75 %", "100 %"])
        ax.set_title("share of the total flow carried by each kind of fracture", loc="left", fontsize=12, color=INK)
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
        ax = fig.add_subplot(gs[4])
        w = m[(m.t_cap > 0) & (m.t_cap <= TMAX)]
        ax.plot(w.t_cap, w.pr_frac, color="#1b4f9c", lw=3, label="PR_V: flow vs. fracture volume")
        ax.plot(w.t_cap, w.pr_pore, color="#d9822b", lw=3, label="PR_pore: flow vs. open pore volume")
        tm = min(max(r.t_cap, 1e-3), TMAX)
        ax.axvline(tm, color="black", lw=2)
        ax.set_xscale("log"); ax.set_xlim(1e-3, TMAX); ax.set_ylim(0, 0.62)
        ax.set_xticks([1e-3, 1e-2, 0.1, 1]); ax.set_xticklabels(["0.001", "0.01", "0.1", "1"])
        ax.grid(color=GRID, lw=0.8)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.set_xlabel("capacity time  (1 = injected water could dissolve the whole inventory)", fontsize=12)
        ax.set_ylabel("participation ratio", fontsize=12)
        ax.legend(frameon=False, fontsize=12, loc="lower left")
        # legend and title
        hs = [Line2D([0], [0], color=c[1], lw=c[2] + 2) for c in CATS]
        fig.legend(hs, [c[0] for c in CATS], loc="upper center", ncol=4, frameon=False, fontsize=13, bbox_to_anchor=(0.5, 0.905))
        fig.text(0.06, 0.975, f"{label}   -   stage {STAGE[int(r.stage) - 1]}", fontsize=19, weight="bold", va="top", color=INK)
        fig.text(0.06, 0.935, f"capacity time {r.t_cap:.3g}    |    {r.pv:,.0f} pore volumes    |    {100 * stt.loc[k, 'dissolved']:.0f} % dissolved"
                 f"    |    open = porosity > 0.5,  flowing = in the 90 % flow set", fontsize=13, va="top", color=INK)
        p = out / f"frame_{i:03d}.png"
        fig.savefig(p, dpi=100); plt.close(fig)
        paths.append(p)
    mp4 = OUT / f"movie_{mode}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "3", "-i", str(out / "frame_%03d.png"), "-vf",
                    "scale=trunc(iw/2)*2:trunc(ih/2)*2", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", str(mp4)], check=True)
    # stills at fixed representative capacity times; stage 3 = the breakthrough frame
    sheet = []
    lt = np.log(np.maximum(fr.t_cap.values, 1e-6))
    for s_, tc in [(1, 0.08), (2, 0.2), (3, None), (4, 1.2)]:
        if tc is None:
            idx = np.where(fr.stage.values == 3)[0]
            j = idx[len(idx) // 2] if len(idx) else int(np.argmin(abs(lt - np.log(0.45))))
        else:
            j = int(np.argmin(abs(lt - np.log(tc))))
        (OUT / f"stage{s_}_{mode}.png").write_bytes(paths[j].read_bytes())
        sheet.append(plt.imread(paths[j]))
        print(mode, "stage", s_, "k", int(fr.k[j]), "t_cap", round(float(fr.t_cap[j]), 3), "front_x", fronts[j])
    fig, axs = plt.subplots(2, 2, figsize=(20, 14))
    for a, im in zip(axs.ravel(), sheet):
        a.imshow(im); a.axis("off")
    fig.subplots_adjust(0, 0, 1, 1, 0.01, 0.01)
    fig.savefig(OUT / f"stages_{mode}.png", dpi=80); plt.close(fig)
    print(mode, len(paths), "frames", mp4, "k_min", k_min)


if __name__ == "__main__":
    import sys
    OUT.mkdir(parents=True, exist_ok=True)
    for md, lb in [("gyponly", "Gypsum only"), ("gypcal", "Gypsum + calcite (coupled)")]:
        if len(sys.argv) < 2 or sys.argv[1] == md:
            run_mode(md, lb)
