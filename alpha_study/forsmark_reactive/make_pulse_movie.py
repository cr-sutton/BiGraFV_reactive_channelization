#!/usr/bin/env python3
"""
Paused-pulse stage movie (network P32 x6, sigma 1, seed 1; both chemistries), redone 5 Nov 2026 at the user's request.  The
reaction frames of the decoupling movie (make_decoupling_movie.py, reused unchanged) play; the movie opens with a pulse through
the unreacted network, and at each of the four stage stills the reaction is paused and the breakthrough curve of a conservative
tracer pulse through that frozen state is drawn in; then the reaction resumes.  No plume maps.  Earlier curves stay on, faded.

Inputs : phase1/figures/anim2/<mode>/frame_*.png      reaction frames (run make_decoupling_movie.py first)
         <run>/snapanim_k/   probes at k = 0 and the stage stills; <run>/snapseq_k/  probes at every movie frame (run_anim_probes.sh)
Outputs: phase1/figures/anim3/pulse_<mode>.mp4, pulse_btc_<mode>.png (last frame), transport_trace_<mode>.csv

Right-hand panels: (1) normalised breakthrough curve E = outlet flux x tau_res = C / (M / V_pore) against theta = t / tau_res,
the pore volumes injected since the pulse counted in the frozen network's pore volume (the same scale for every stage; in years
the curves stretch with the added pore volume, which is not dispersion); (2) median arrival t50 / tau_res against the fraction of
the gypsum dissolved for every frame state, current state marked.

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
T_REACT, T_PULSE, T_HOLD, N_SUB = 1 / 3, 0.1, 1.5, 24              # s per reaction frame / BTC draw frame / hold; BTC draw frames
PAUSE_COL = "#c0392b"
YMAX = {"gyponly": 1.5, "gypcal": 1.5}


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
    # pulses: k = 0 reference plus the four stills (breakthrough curves only; no plume maps since 5 Nov)
    pulses = {}
    for name, k in [("start", 0)] + [(f"stage {i + 1}", int(fr.k[j])) for i, j in enumerate(ks)]:
        meta, t, f, mt = btc(rd / f"snapanim_{k}")
        pulses[name] = dict(k=k, tau=meta["tau_res_y"], th=t / meta["tau_res_y"], E=f * meta["tau_res_y"], m=mt,
                            diss=0.0 if k == 0 else float(fr.dissolved[fr.k == k].iloc[0]))
    work = OUT / mode
    work.mkdir(exist_ok=True)
    for p in work.glob("*.png"):
        p.unlink()
    seq = []                                                           # (png, seconds)

    def panels(fig, gs, done, cur=None, upto=None, k_now=None):
        """Right-hand column: normalised breakthrough curve E(theta) against pore volumes since the pulse (current pore volume),
        and t50/tau_res against the fraction of the gypsum dissolved.  done = pulse names already drawn in full."""
        a1, a2 = fig.add_subplot(gs[0]), fig.add_subplot(gs[1])
        for name in done + ([cur] if cur else []):
            p = pulses[name]
            col = "#9a9a94" if name == "start" else STAGE_COL[int(name[-1]) - 1]
            sel = p["th"] <= (upto if name == cur else np.inf)
            lab = "before reaction" if name == "start" else f"{name}: {100 * p['diss']:.0f} % dissolved"
            a1.plot(p["th"][sel], p["E"][sel], color=col, lw=3.2 if name == cur else 2.2, alpha=1.0 if name == cur else 0.75,
                    label=f"{lab}  (t50 {p['m']['t50'] / p['tau']:.2f})")
        a1.set_xlim(0, 3); a1.set_ylim(0, YMAX[mode])
        a1.set_xlabel("pore volumes injected since the pulse  (current pore volume of the frozen network)", fontsize=12)
        a1.set_ylabel("normalised concentration  C / (M / V_pore)", fontsize=12)
        a1.set_title("tracer breakthrough at the outlet", fontsize=13, color=INK, loc="left")
        a1.legend(frameon=False, fontsize=11, loc="upper right")
        if len(trace):
            w = trace[(trace.diss > 0) & (trace.diss < 1)]
            a2.plot(w.diss, w.t50_res, color=INK2, lw=2)
            for i, j in enumerate(ks):
                a2.axvline(float(fr.dissolved[j]), color=STAGE_COL[i], lw=1.4, ls=":")
            if k_now is not None and (trace.k == k_now).any():
                r = trace[trace.k == k_now].iloc[0]
                a2.plot(min(max(r.diss, 1e-3), 0.99), r.t50_res, "o", ms=11, color=INK)
            a2.axhline(float(trace.t50_res.iloc[0]), color="#9a9a94", lw=1, ls="--")
        a2.set_xscale("logit"); a2.set_xlim(1e-3, 0.99); a2.minorticks_off()
        a2.set_xticks([1e-3, 0.01, 0.1, 0.5, 0.9, 0.99]); a2.set_xticklabels(["0.001", "0.01", "0.1", "0.5", "0.9", "0.99"])
        a2.set_xlabel("fraction of the gypsum dissolved", fontsize=12)
        a2.set_ylabel("median arrival t50\n(pore volumes)", fontsize=12)
        a2.set_title(f"median arrival (movie ends at {100 * trace.diss.max():.0f} % dissolved)", fontsize=12, color=INK, loc="left")
        for a in (a1, a2):
            a.grid(color=GRID, lw=0.8); a.tick_params(labelsize=11)
            for s_ in ("top", "right"):
                a.spines[s_].set_visible(False)

    def frame(i, done, head, sub, cur=None, upto=None, dur=T_REACT, col=INK):
        fig = plt.figure(figsize=(24, 13.5), facecolor="white")
        gs = fig.add_gridspec(2, 2, width_ratios=[1.55, 1], height_ratios=[1.35, 1], hspace=0.32, wspace=0.1, left=0.01, right=0.985, top=0.86, bottom=0.07)
        ax = fig.add_subplot(gs[:, 0]); ax.imshow(plt.imread(frames[i])); ax.axis("off")
        panels(fig, [gs[0, 1], gs[1, 1]], done, cur=cur, upto=upto, k_now=int(fr.k[i]))
        fig.text(0.62, 0.975, head, fontsize=19, weight="bold", color=col, va="top")
        fig.text(0.62, 0.94, sub, fontsize=13, color=INK2, va="top")
        p = work / f"f{len(seq):04d}.png"
        fig.savefig(p, dpi=80); plt.close(fig)
        seq.append((p, dur))

    def pause(i, name, done):
        p = pulses[name]
        what = "before any reaction" if name == "start" else f"{name}, {100 * p['diss']:.0f} % of the gypsum dissolved"
        for u in np.linspace(0.05, 3.0, N_SUB):
            frame(i, done, "REACTION PAUSED - tracer pulse", f"{what}; flow frozen, tracer does not react; residence time {p['tau']:.2f} y",
                  cur=name, upto=u, dur=T_PULSE, col=PAUSE_COL)
        frame(i, done, "REACTION PAUSED - tracer pulse", f"{what}; median arrival {p['m']['t50'] / p['tau']:.2f} pore volumes",
              cur=name, upto=9.9, dur=T_HOLD, col=PAUSE_COL)
        done.append(name)

    done = []
    pause(0, "start", done)
    for i in range(len(fr)):
        r = fr.iloc[i]
        frame(i, done, "reaction running", f"{100 * r.dissolved:.0f} % of the gypsum dissolved   |   {r.pv:,.0f} pore volumes injected")
        if i in ks:
            pause(i, f"stage {ks.index(i) + 1}", done)
    frame(len(fr) - 1, done, "end of the movie", "all pulses: before reaction and the four stages", dur=2.5)
    import shutil
    shutil.copy(seq[-1][0], OUT / f"pulse_btc_{mode}.png")
    fig = plt.figure(figsize=(13, 5.2), facecolor="white")          # standalone curves (deck, manuscript)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.25, 1], wspace=0.28, left=0.07, right=0.98, top=0.9, bottom=0.14)
    panels(fig, [gs[0, 0], gs[0, 1]], list(pulses))
    fig.savefig(OUT / f"pulse_btc_only_{mode}.png", dpi=150); plt.close(fig)
    lst = work / "concat.txt"
    lst.write_text("".join(f"file '{p.name}'\nduration {d:.3f}\n" for p, d in seq) + f"file '{seq[-1][0].name}'\n")
    mp4 = OUT / f"pulse_{mode}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-vf",
                    "scale=trunc(iw/2)*2:trunc(ih/2)*2,fps=12", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "24", str(mp4)], check=True)
    print(mode, len(seq), "frames", f"{sum(d for _, d in seq):.0f} s", mp4)
    print(pd.DataFrame([dict(pulse=k_, k=v["k"], diss=round(v["diss"], 3), tau_res_y=round(v["tau"], 3), t50_PV=round(v["m"]["t50"] / v["tau"], 3),
                             gamma=round(v["m"]["gamma"], 2), E_peak=round(float(v["E"].max()), 2)) for k_, v in pulses.items()]).to_string(index=False))


if __name__ == "__main__":
    modes = sys.argv[1:] or ["gyponly", "gypcal"]
    for mode in modes:
        run_mode(mode, "gypsum only" if mode == "gyponly" else "gypsum → calcite")
