#!/usr/bin/env python3
"""
Hyman-style transport metrics from the frozen-state tracer probes of the Phase 1 runs (RUN/snap_k: a steady flow solve on
the reacted permeability and porosity of checkpoint k, then a conservative tracer pulse; probe_frozen_state_tracer.py).
Definitions follow Hyman et al. 2024 G-cubed and Hyman, Szawełło, Kang & Szymczak 2026 JGR (forsmark_reactive/lit/
hyman_transport_metrics.md), adapted from particles to an Eulerian pulse:

  f(t)    breakthrough curve = outflow tracer flux / injected tracer, t from the pulse start (J26 Eq. 32 as a flux)
  F(t)    cumulative (normalised by the recovered tracer); t16, t50, t84 from F
  t_peak  time of max f
  D_L     (1/8) [(L0 - v t16)/sqrt(t16) - (L0 - v t84)/sqrt(t84)]^2, v = L0 / t50, L0 = 1000 m (J26 Eq. B1)
  gamma   tail exponent, f ~ t^-gamma, least squares in log-log on the PDF over t in [2 t_peak, t at f = 1e-2 f_peak]
          (fit window ours; J26 does not state theirs)
  Times are normalised by the unreacted state of the same run (Hyman: by the tau = 0 values).
  The probes hold the flow rate fixed while dissolution grows the pore volume (up to x10), so raw arrival times stretch with
  the volume (J26 reports the same: peak arrival doubles as the volume doubles).  Volume-free measures of channelization:
  t_peak/tau_res and t50/tau_res (tau_res = current pore volume / rate: mean residence time) and the dispersivity
  alpha_L = D_L / v (m).
Eulerian pulses carry numerical dispersion and a finite pulse (0.1 residence times) and the probe window is 10 current
residence times, so early arrival and the tail fit are smeared and truncated; compare states with each other, not with
particle results.

State coordinate: capacity-normalised time t_cap = t_y x c_cap / C_inv (16.6 mol/m3 gyponly, 516.6 gypcal; C_inv for
porosity 0.1).

  python3 forsmark_reactive/analyze_phase1_tracer.py   -> phase1/phase1_tracer.csv, phase1/figures/tracer_*.png
"""
from __future__ import annotations

import glob
import json
import re
from pathlib import Path

import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from time_axes import clocks  # noqa: E402
P1 = HERE / "phase1"
OUT = P1 / "figures"
L0 = 1000.0
C_INV = 0.9 / (0.1 * 74.69e-6)
C_CAP = {"gyponly": 16.6, "gypcal": 516.6}
SIG = {0.0: "#86b6ef", 0.5: "#2a78d6", 1.0: "#104281"}
INK2, GRID = "#52514e", "#e6e5e1"


def read_probe(snap: Path):
    meta = json.loads((snap / "snap.json").read_text())
    hdr = [c.strip().strip('"') for c in (snap / "snap-mas.dat").open().readline().split('",')]
    d = np.genfromtxt(snap / "snap-mas.dat", skip_header=1, invalid_raise=False)
    col = lambda name: hdr.index(name)
    t = d[:, 0] - meta["t_pulse_y"]
    q = np.abs(d[:, col("outflow Tracer [mol/y]")])
    m_in = np.nanmax(np.abs(d[:, col("inflow Tracer [mol]")]))
    keep = t >= 0
    return meta, t[keep], q[keep] / m_in


def metrics(t, f):
    cum = np.concatenate([[0], np.cumsum(0.5 * (f[1:] + f[:-1]) * np.diff(t))])
    rec = cum[-1]
    F = cum / rec
    q = lambda p: float(np.interp(p, F, t))
    t16, t50, t84 = q(0.16), q(0.5), q(0.84)
    v = L0 / t50
    dl = 0.125 * ((L0 - v * t16) / np.sqrt(t16) - (L0 - v * t84) / np.sqrt(t84)) ** 2
    ip = int(np.argmax(f))
    tp, fp = t[ip], f[ip]
    after = np.where((t > 2 * tp) & (f > 1e-2 * fp))[0]
    gamma = np.nan
    if len(after) >= 5:
        sl = np.polyfit(np.log(t[after]), np.log(f[after]), 1)[0]
        gamma = -sl
    return dict(recovery=rec, t_first=q(0.01), t_peak=tp, t16=t16, t50=t50, t84=t84, D_L=dl, gamma=gamma)


def main():
    rows, curves = [], {}
    for run in sorted(glob.glob(str(P1 / "L2_r15_p*_sg*_seed*/gyp*__phase1"))):
        m = re.search(r"p([\d.]+)_sg([\d.]+)_seed(\d)", run)
        mode = "gypcal" if "calcite" in run else "gyponly"   # x16 included since 5 Nov (fine probes run for it)
        fine = sorted(Path(run).glob("snapfine_*"), key=lambda p: int(p.name.split("_")[1]))   # finer early output if probed
        if not (fine and all((f / "snap-mas.dat").exists() for f in fine)):
            continue                      # fine probes only (steps of 0.005 tau_res for the first 3); runs without them are skipped
        snaps = fine
        clk = clocks(Path(run))
        for s in snaps:
            if not (s / "snap-mas.dat").exists():
                continue
            meta, t, f = read_probe(s)
            r = dict(p32=float(m[1]), sigma=float(m[2]), seed=int(m[3]), mode=mode, k=meta["k"], t_y=meta["t_y"],
                     pv=float(clk.pv(meta["t_y"])), t_cap=float(clk.t_cap(meta["t_y"])), tau_H=float(clk.tau_H(meta["t_y"])), diss=float(clk.diss(meta["t_y"])),
                     probe=snaps[0].name.split("_")[0], tau_res_y=meta["tau_res_y"], **metrics(t, f))
            rows.append(r)
            curves[(r["p32"], r["sigma"], r["seed"], mode, r["k"])] = (t, f)
    df = pd.DataFrame(rows).sort_values(["mode", "p32", "sigma", "seed", "t_y"])
    base = df[df.k == 0].set_index(["mode", "p32", "sigma", "seed"])
    df["t_peak_res"] = df.t_peak / df.tau_res_y
    df["t50_res"] = df.t50 / df.tau_res_y
    df["alpha_L"] = df.D_L * df.t50 / L0
    base = df[df.k == 0].set_index(["mode", "p32", "sigma", "seed"])
    for c in ("t_first", "t_peak", "t50", "D_L", "gamma", "alpha_L"):
        df[c + "_rel"] = [r[c] / base.loc[(r["mode"], r["p32"], r["sigma"], r["seed"]), c] for _, r in df.iterrows()]
    df.to_csv(P1 / "phase1_tracer.csv", index=False)
    OUT.mkdir(exist_ok=True)

    # 1. breakthrough curves of one network, every probed state
    fig, axs = plt.subplots(1, 2, figsize=(10.5, 3.8), sharey=True)
    key = (6.0, 1.0, 1)
    for ax, mode, lab in zip(axs, ("gyponly", "gypcal"), ("gypsum only", "gypsum → calcite")):
        ks = sorted(k for (p, s, sd, mo, k) in curves if (p, s, sd) == key and mo == mode)
        t0 = base.loc[(mode,) + key, "t_first"]
        cmap = plt.get_cmap("viridis")
        for i, k in enumerate(ks):
            t, f = curves[key + (mode, k)]
            tc = df[(df["mode"] == mode) & (df.p32 == key[0]) & (df.sigma == key[1]) & (df.seed == key[2]) & (df.k == k)].t_cap.iloc[0]
            ok = (t > 0) & (f > 0)
            ax.loglog(t[ok] / t0, f[ok] * t0, color=cmap(i / max(1, len(ks) - 1)), lw=1.6, label=f"t_cap {tc:.3g}")
        ax.set_title(f"{lab}: P32 ×6, σ = 1, seed 1", fontsize=10)
        ax.set_xlabel("t / first arrival of the unreacted state", fontsize=9, color=INK2)
        ax.grid(color=GRID, lw=0.8, which="both")
        ax.set_ylim(1e-4, None)
        ax.set_xlim(0.1, 1e3)
        ax.legend(frameon=False, fontsize=7, ncol=2)
    axs[0].set_ylabel("breakthrough f(t) (normalised)", fontsize=9, color=INK2)
    fig.tight_layout(); fig.savefig(OUT / "tracer_btc_example.png", dpi=160); plt.close(fig)

    # 1b. annotated curves on residence-time-scaled time: unreacted, channel peak, after widening
    for mode, lab in (("gyponly", "gypsum only"), ("gypcal", "gypsum → calcite")):
        sub = df[(df["mode"] == mode) & (df.p32 == key[0]) & (df.sigma == key[1]) & (df.seed == key[2])].sort_values("t_cap")
        if sub.empty:
            continue
        pick = [("unreacted", sub.iloc[0])]
        pos = sub[sub.t_cap > 0]
        for name, tc in (("at the channel peak", 0.45), ("after widening", 2.0)):
            pick.append((name, pos.iloc[(np.log(pos.t_cap) - np.log(tc)).abs().argmin()]))
        fig, ax = plt.subplots(figsize=(7.4, 4.6))
        cols = ["#9a9a95", "#d2572a", "#2a78d6"]
        for (name, r), c in zip(pick, cols):
            t, f = curves[key + (mode, int(r.k))]
            tau = r.tau_res_y
            ok = (t > 0) & (f > 0)
            ax.loglog(t[ok] / tau, f[ok] * tau, color=c, lw=2, label=f"{name} ({100 * r.diss:.0f} % dissolved)")
            ax.axvline(r.t50 / tau, color=c, lw=1, ls=":")
            ax.annotate(f"median {r.t50 / tau:.2f}", (r.t50 / tau, 1.15e-3), color=c, fontsize=8, rotation=90, va="bottom", ha="right")
            if np.isfinite(r.gamma):
                fp = f.max() * tau
                x0 = 2 * r.t_peak / tau
                xs = np.array([x0, x0 * 3])
                ax.loglog(xs, fp * 0.5 * (xs / x0) ** (-r.gamma), color=c, lw=1, ls="--")
                ax.annotate(f"tail γ = {r.gamma:.1f}", (xs[1], fp * 0.5 * 3 ** (-r.gamma)), color=c, fontsize=8, xytext=(4, 0), textcoords="offset points")
        ax.axvline(1.0, color="#0b0b0b", lw=0.8)
        ax.annotate("mean residence time", (1.0, 3e-3), fontsize=8, rotation=90, ha="right", va="bottom")
        ax.set_xlim(0.05, 12); ax.set_ylim(1e-3, 4)
        ax.grid(color=GRID, lw=0.8, which="both")
        ax.set_xlabel("time ÷ current mean residence time (pore volume ÷ flow)", fontsize=9, color=INK2)
        ax.set_ylabel("breakthrough f (× residence time)", fontsize=9, color=INK2)
        ax.set_title(f"{lab}: P32 ×{key[0]:g}, σ = {key[1]:g}, seed {key[2]}", fontsize=10)
        ax.legend(frameon=False, fontsize=8, loc="lower left")
        fig.tight_layout(); fig.savefig(OUT / f"tracer_btc_annotated_{mode}.png", dpi=160); plt.close(fig)

    # 2. metrics against capacity time: rows metrics, columns P32, lines sigma; one figure per chemistry
    mets = [("t50_rel", "median arrival / unreacted"), ("t_peak_res", "peak arrival / mean residence time"),
            ("t50_res", "median arrival / mean residence time"), ("alpha_L", "dispersivity α_L = D_L/v (m)"),
            ("gamma", "tail exponent γ")]
    XL = {"diss": "fraction of the gypsum dissolved (logit axis)", "pv": "pore volumes injected", "t_cap": "capacity-normalised time", "tau_H": "dissolved volume / initial volume (Hyman τ)"}
    XT = {"diss": "diss", "pv": "pv", "t_cap": "tcap", "tau_H": "tauH"}
    for (mode, lab), xc in [(m_, x_) for m_ in (("gyponly", "gypsum only"), ("gypcal", "gypsum → calcite")) for x_ in XL]:
        fig, axs = plt.subplots(len(mets), 4, figsize=(14.5, 12), sharex=True, sharey="row")
        for j, p in enumerate((4.0, 6.0, 8.0, 16.0)):
            for i, (c, yl) in enumerate(mets):
                ax = axs[i, j]
                for s, col in SIG.items():
                    d = df[(df["mode"] == mode) & (df.p32 == p) & (df.sigma == s)]
                    g = d.groupby("k").agg(x=(xc, "median"), med=(c, "median"), lo=(c, lambda v: np.nanpercentile(v, 10)),
                                           hi=(c, lambda v: np.nanpercentile(v, 90))).sort_values("x")
                    g = g[(g.x > 0) & (g.x < 1)] if xc == "diss" else (g[g.x > 0] if xc != "pv" else g)
                    ax.fill_between(g.x, g.lo, g.hi, color=col, alpha=0.15, lw=0)
                    ax.plot(g.x, g.med, "o-", color=col, lw=1.8, ms=4, label=f"σ = {s:g}")
                if xc == "pv":
                    ax.set_xscale("symlog", linthresh=100, linscale=0.6)
                elif xc == "diss":
                    ax.set_xscale("logit"); ax.set_xlim(1e-3, 0.99)
                    ax.set_xticks([1e-3, 0.01, 0.1, 0.5, 0.9, 0.99]); ax.set_xticklabels(["0.001", "0.01", "0.1", "0.5", "0.9", "0.99"]); ax.minorticks_off()
                else:
                    ax.set_xscale("log")
                if c in ("t50_rel", "alpha_L"):
                    ax.set_yscale("log")
                ax.grid(color=GRID, lw=0.8, which="both")
                ax.tick_params(labelsize=8, colors=INK2)
                if i == 0:
                    ax.set_title(f"P32 × {p:g}", fontsize=10)
                if j == 0:
                    ax.set_ylabel(yl, fontsize=9, color=INK2)
                if i == len(mets) - 1:
                    ax.set_xlabel(XL[xc], fontsize=9, color=INK2)
        axs[0, 0].legend(frameon=False, fontsize=8, title="5 seeds each", title_fontsize=8)
        fig.suptitle(f"{lab}: transport of the frozen reacted states", fontsize=11)
        fig.tight_layout(); fig.savefig(OUT / f"tracer_metrics_{mode}_{XT[xc]}.png", dpi=160); plt.close(fig)
    pd.set_option("display.width", 220)
    print(df.groupby(["mode", "p32"]).recovery.describe()[["min", "50%"]].round(3))
    print(df.groupby(["mode", "p32", "k"])[["t_cap", "t50_rel", "t_peak_res", "t50_res", "alpha_L", "gamma"]].median().round(3).to_string())


if __name__ == "__main__":
    main()
