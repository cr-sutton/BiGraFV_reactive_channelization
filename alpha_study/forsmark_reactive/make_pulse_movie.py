#!/usr/bin/env python3
"""
Paused-pulse stage movie (network P32 x6, sigma 1, seed 1; both chemistries).  A NEW movie beside the decoupling movie
(make_decoupling_movie.py, whose frames it reuses unchanged): the reaction plays; at each of the four stage stills the
reaction clock is frozen, a conservative tracer pulse is sent through the frozen state, and its plume and breakthrough
curve are shown; then the reaction resumes.  Earlier stages' curves stay on as faded lines.

Inputs : phase1/figures/anim2/<mode>/frame_*.png      reaction frames (run make_decoupling_movie.py first)
         <run>/snapanim_k/   plume probes at k = 0 and the stage stills (run_anim_probes.sh; extra VTK every 0.05 tau_res)
         <run>/snapseq_k/    breakthrough-only probes at every movie frame (run_anim_probes.sh)
         paraview/<net>__<run>__mech/fractures_000.vtu   fracture polygons for the slices
Outputs: phase1/figures/anim3/pulse_<mode>.mp4, pulse_stages_<mode>.png (contact sheet of the four plume peaks),
         phase1/figures/anim3/transport_trace_<mode>.csv (t50/tau_res, gamma, tau_res per frame state)

Right-hand panels: (1) breakthrough curve against t / tau_res (shape: flow focusing), (2) the same against years (shift:
pore volume added at the same flow), (3) t50/tau_res against the fraction of the gypsum dissolved (the report's main clock)
for every frame state, current state marked.
Plume maps: Total_Tracer / pulse concentration (1e-3 M) on the fracture traces of the slices z = 0 and z = +60 m, log colour.

  python3 forsmark_reactive/make_pulse_movie.py
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import cm, colors
from matplotlib.collections import LineCollection

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT)]
import make_decoupling_movie as M  # noqa: E402
from analyze_phase1_tracer import metrics, read_probe  # noqa: E402
from bipartite_pressure_solutions_functions import read_scalar_from_vtk  # noqa: E402

P1 = HERE / "phase1"
OUT = P1 / "figures" / "anim3"
C_PULSE = 1e-3
STAGE_COL = ["#86b6ef", "#2a78d6", "#d9822b", "#7a3d9a"]          # stage 1..4 curves; k = 0 in grey
INK, INK2, GRID = "#2b2b29", "#52514e", "#d9d8d3"
T_REACT, T_PULSE, T_HOLD = 1 / 3, 0.1, 1.2                       # seconds per reaction frame / plume frame / hold


def stills(mode):
    """k of the four stage stills, exactly as make_decoupling_movie.py chooses them, and the frame table."""
    m = pd.read_csv(P1 / "phase1_mechanism.csv")
    m = m[(m["mode"] == mode) & (m.p32 == 6.0) & (m.sigma == 1.0) & (m.seed == 1) & (m.tag == "phase1")].sort_values("k").reset_index(drop=True)
    win = m[m.t_cap <= M.TMAX]
    m["stage"] = M.stage_of(m, int(win.k.values[np.argmin(win.pr_frac.values)]))
    fr = m[m.t_cap <= M.TMAX].reset_index(drop=True)
    lt = np.log(np.maximum(fr.t_cap.values, 1e-6))
    ks = []
    for tc in (0.08, 0.2, None, 1.2):
        if tc is None:
            idx = np.where(fr.stage.values == 3)[0]
            j = idx[len(idx) // 2] if len(idx) else int(np.argmin(abs(lt - np.log(0.45))))
        else:
            j = int(np.argmin(abs(lt - np.log(tc))))
        ks.append(j)
    return fr, ks


def plume_frames(snap):
    """[(t since pulse start in tau_res, c/c_pulse per cell)] from snap-001.. (snap-000 is the initial output)."""
    times = [float(v) for line in (snap / "snap.in").read_text().splitlines() if line.strip().startswith("TIMES y")
             for v in line.split()[2:]]
    meta = read_probe(snap)[0]
    out = []
    for j, t in enumerate(times, 1):
        f = snap / f"snap-{j:03d}.vtk"
        if f.exists():
            out.append(((t - meta["t_pulse_y"]) / meta["tau_res_y"], np.asarray(read_scalar_from_vtk(str(f), "Total_Tracer"), float) / C_PULSE))
    return out


def btc(snap):
    meta, t, f = read_probe(snap)
    return meta, t, f, metrics(t, f)


def run_mode(mode, label):
    run = "gypsum" if mode == "gyponly" else "gypsum_calcite"
    rd = P1 / M.NET / f"{run}__uncorrected_graph__phase1"
    fr, ks = stills(mode)
    frames = sorted((P1 / "figures" / "anim2" / mode).glob("frame_*.png"))
    assert len(frames) == len(fr), f"{mode}: {len(frames)} reaction frames vs {len(fr)} states; rerun make_decoupling_movie.py"
    g0 = M.read(ROOT / "paraview" / f"{M.NET}__{run}__uncorrected_graph__phase1__mech" / "fractures_000.vtu")
    segs = [M.slice_segments(g0, z) for z in M.ZS]
    # continuous transport trace from the breakthrough-only probes
    trace = []
    for k in fr.k:
        s = rd / f"snapseq_{int(k)}"
        if (s / "snap-mas.dat").exists():
            meta, t, f, mt = btc(s)
            trace.append(dict(k=int(k), t_cap=float(fr.t_cap[fr.k == k].iloc[0]), diss=float(fr.dissolved[fr.k == k].iloc[0]), tau_res_y=meta["tau_res_y"],
                              t50_res=mt["t50"] / meta["tau_res_y"], gamma=mt["gamma"], recovery=mt["recovery"]))
    trace = pd.DataFrame(trace)
    OUT.mkdir(parents=True, exist_ok=True)
    trace.to_csv(OUT / f"transport_trace_{mode}.csv", index=False)
    # pulses: k = 0 reference plus the four stills
    pulses = {}
    for name, k in [("start", 0)] + [(f"stage {i + 1}", int(fr.k[j])) for i, j in enumerate(ks)]:
        s = rd / f"snapanim_{k}"
        meta, t, f, mt = btc(s)
        pulses[name] = dict(k=k, tau=meta["tau_res_y"], t=t, f=f, m=mt, plume=plume_frames(s))
    work = OUT / mode
    work.mkdir(exist_ok=True)
    for p in work.glob("*.png"):
        p.unlink()
    seq, sheet = [], []                                                # (png, seconds)
    cmap, norm = cm.get_cmap("magma_r"), colors.LogNorm(1e-3, 1)

    def panels(fig, gs, done, cur=None, upto=None, k_now=None):
        """Right-hand column: BTC (t/tau_res), BTC (years), t50/tau_res trace.  done = pulse names already shown."""
        a1, a2, a3 = (fig.add_subplot(gs[i]) for i in range(3))
        for name in done + ([cur] if cur else []):
            p = pulses[name]
            col = "#9a9a94" if name == "start" else STAGE_COL[int(name[-1]) - 1]
            sel = slice(None) if name != cur else p["t"] / p["tau"] <= upto
            alpha, lw = (1.0, 3) if name == cur else (0.55, 2)
            tn, fn = p["t"][sel] / p["tau"], p["f"][sel] * p["tau"]
            a1.plot(tn, fn, color=col, lw=lw, alpha=alpha, label=f"{name}: t50/τ_res {p['m']['t50'] / p['tau']:.2f}")
            a2.plot(p["t"][sel], p["f"][sel], color=col, lw=lw, alpha=alpha, label=f"{name}: τ_res {p['tau']:.2f} y")
        a1.set_xlim(0, 3); a1.set_ylim(0, None); a1.set_xlabel("time since pulse / residence time", fontsize=11)
        a1.set_ylabel("outlet flux × τ_res\n(shape)", fontsize=11)
        a2.set_xlim(0, 3 * max(p["tau"] for p in pulses.values())); a2.set_ylim(0, None)
        a2.set_xlabel("time since pulse (years)", fontsize=11); a2.set_ylabel("outlet flux (1/y)\n(timing)", fontsize=11)
        for a in (a1, a2):
            a.legend(frameon=False, fontsize=9, loc="upper right")
        if len(trace):
            w = trace[(trace.diss > 0) & (trace.diss < 1)]
            a3.plot(w.diss, w.t50_res, color=INK2, lw=2)
            for i, j in enumerate(ks):
                a3.axvline(float(fr.dissolved[j]), color=STAGE_COL[i], lw=1.2, ls=":")
            if k_now is not None and (trace.k == k_now).any():
                r = trace[trace.k == k_now].iloc[0]
                a3.plot(min(max(r.diss, 1e-3), 0.99), r.t50_res, "o", ms=10, color=INK)
        a3.axhline(float(trace.t50_res.iloc[0]) if len(trace) else np.nan, color="#9a9a94", lw=1, ls="--")
        a3.set_xscale("logit"); a3.set_xlim(1e-3, 0.99); a3.minorticks_off()
        a3.set_xticks([1e-3, 0.01, 0.1, 0.5, 0.9, 0.99]); a3.set_xticklabels(["0.001", "0.01", "0.1", "0.5", "0.9", "0.99"])
        a3.set_xlabel("fraction of the gypsum dissolved (main clock)", fontsize=11); a3.set_ylabel("t50 / τ_res", fontsize=11)
        for a in (a1, a2, a3):
            a.grid(color=GRID, lw=0.8); a.tick_params(labelsize=10)
            for s_ in ("top", "right"):
                a.spines[s_].set_visible(False)

    def save(fig, n, dur):
        p = work / f"f{n:04d}.png"
        fig.savefig(p, dpi=90); plt.close(fig)
        seq.append((p, dur))

    n, done = 0, []
    for i in range(len(fr)):
        k = int(fr.k[i])
        fig = plt.figure(figsize=(24, 14), facecolor="white")
        gs = fig.add_gridspec(3, 2, width_ratios=[1.6, 1], hspace=0.38, wspace=0.12, left=0.01, right=0.98, top=0.95, bottom=0.06)
        ax = fig.add_subplot(gs[:, 0]); ax.imshow(plt.imread(frames[i])); ax.axis("off")
        panels(fig, [gs[r, 1] for r in range(3)], done, k_now=k)
        fig.text(0.63, 0.975, "reaction running", fontsize=16, weight="bold", color=INK, va="top")
        save(fig, n, T_REACT); n += 1
        if i not in ks:
            continue
        s = ks.index(i)
        name = f"stage {s + 1}"
        r = fr.iloc[i]
        for pname in (["start"] if s == 0 else []) + [name]:
            p = pulses[pname]
            peak = max(range(len(p["plume"])), key=lambda j: np.nanmedian(p["plume"][j][1][p["plume"][j][1] > 1e-6]) if (p["plume"][j][1] > 1e-6).any() else 0)
            for j, (tn, c) in enumerate(p["plume"]):
                fig = plt.figure(figsize=(24, 14), facecolor="white")
                gs = fig.add_gridspec(3, 2, width_ratios=[1.6, 1], hspace=0.38, wspace=0.12, left=0.04, right=0.98, top=0.86, bottom=0.14)
                sub = gs[:, 0].subgridspec(2, 1, hspace=0.18)
                for row, (z, (sg, ids)) in enumerate(zip(M.ZS, segs)):
                    ax = fig.add_subplot(sub[row]); ax.set_facecolor(M.BG)
                    ax.add_collection(LineCollection(sg, colors="#cfcfca", linewidths=1.5))
                    cc = c[ids]; on = cc > 1e-3
                    ax.add_collection(LineCollection(sg[on], colors=cmap(norm(np.clip(cc[on], 1e-3, 1))), linewidths=5, capstyle="round"))
                    ax.set_xlim(-500, 500); ax.set_ylim(-125, 125); ax.set_yticks([])
                    ax.set_xticks([-500, -250, 0, 250, 500] if row == 1 else [])
                    ax.text(0.005, 0.96, f"slice z = {z:+.0f} m", transform=ax.transAxes, va="top", fontsize=12, color=INK)
                    if row == 0:
                        ax.text(0.0, 1.03, "INLET  x = -500 m", transform=ax.transAxes, fontsize=12, weight="bold", color=INK)
                        ax.text(1.0, 1.03, "OUTLET  x = +500 m", transform=ax.transAxes, ha="right", fontsize=12, weight="bold", color=INK)
                    for s_ in ax.spines.values():
                        s_.set_color(GRID)
                cax = fig.add_axes([0.06, 0.055, 0.3, 0.015])
                cb = fig.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax, orientation="horizontal")
                cb.set_label("tracer concentration / pulse concentration", fontsize=11)
                panels(fig, [gs[r_, 1] for r_ in range(3)], done, cur=pname, upto=tn, k_now=k)
                head = "before any reaction (reference)" if pname == "start" else f"stage {M.STAGE[s]}"
                fig.text(0.04, 0.975, f"{label}  -  REACTION PAUSED  -  tracer pulse, {head}", fontsize=19, weight="bold", va="top", color=INK)
                fig.text(0.04, 0.935, f"frozen state: {0 if pname == 'start' else 100 * r.dissolved:.0f} % of the gypsum dissolved  |  "
                         f"{0 if pname == 'start' else r.pv:,.0f} pore volumes  |  τ_res {p['tau']:.2f} y  |  "
                         f"time since pulse {tn:.2f} τ_res", fontsize=14, va="top", color=INK)
                fig.text(0.04, 0.9, "flow and pore space are frozen; the tracer does not react.  Grey traces: no tracer (< 0.1 % of the pulse).",
                         fontsize=12, va="top", color=INK2)
                hold = T_HOLD if j in (0, len(p["plume"]) - 1) else T_PULSE
                save(fig, n, hold); n += 1
                if j == peak and pname != "start":
                    sheet.append(seq[-1][0])
            done.append(pname)
    lst = work / "concat.txt"
    lst.write_text("".join(f"file '{p.name}'\nduration {d:.3f}\n" for p, d in seq) + f"file '{seq[-1][0].name}'\n")
    mp4 = OUT / f"pulse_{mode}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-vf",
                    "scale=trunc(iw/2)*2:trunc(ih/2)*2,fps=12", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", str(mp4)], check=True)
    fig, axs = plt.subplots(2, 2, figsize=(24, 14))
    for a, p in zip(axs.ravel(), sheet):
        a.imshow(plt.imread(p)); a.axis("off")
    fig.subplots_adjust(0, 0, 1, 1, 0.01, 0.01)
    fig.savefig(OUT / f"pulse_stages_{mode}.png", dpi=70); plt.close(fig)
    print(mode, len(seq), "frames", f"{sum(d for _, d in seq):.0f} s", mp4)
    print(pd.DataFrame([dict(pulse=k_, k=v["k"], tau_res_y=round(v["tau"], 3), t50_res=round(v["m"]["t50"] / v["tau"], 3),
                             gamma=round(v["m"]["gamma"], 2)) for k_, v in pulses.items()]).to_string(index=False))


if __name__ == "__main__":
    modes = sys.argv[1:] or ["gyponly", "gypcal"]
    for mode in modes:
        run_mode(mode, "gypsum only" if mode == "gyponly" else "gypsum → calcite")
