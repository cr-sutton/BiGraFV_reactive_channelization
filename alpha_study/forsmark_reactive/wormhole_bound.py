#!/usr/bin/env python3
"""
Check 2 of WORMHOLE_CHECKS.md: wormhole-limit bound on breakthrough.  Post-processing only; this is a bound, not a simulation.

Per Phase 1 run (P32 x4/x6/x8, plus x16 as a separate group when its VTUs exist), both chemistries:
  k_bt    first saved state with outlet_diss >= 0.5 (phase1_mechanism.csv; for x16, which has no rows there, computed the same way
          as analyze_phase1_mechanism.py: flow-weighted fraction_dissolved of fractures with x_center > 400, from the VTUs)
  D_bt    network dissolved fraction at k_bt (patterns.csv 'dissolved', fracture-cell inventory definition)
  channel the 90 %-flow set (s90 of analyze_channelization.py, on Q_frac) at the state where channelization.csv n90 is smallest
  D_ch, D_off  sum(fraction_dissolved x inventory) over channel / other fractures, divided by the total inventory,
          inventory = fracture volume (first n_fractures cells of the UGE, column 4) x vf0.  D_ch + D_off = D_bt (asserted).
  If only a fraction f of each channel fracture had to dissolve before the front passes:
      lower  D_lo(f) = f D_bt              (all dissolution before breakthrough scales)
      upper  D_hi(f) = f D_ch + D_off      (off-channel dissolution unchanged)
  D -> time by inverting the run's own dissolved-vs-time curve (patterns.csv t_y, dissolved; made monotone with a running maximum,
  linear interpolation), then t_cap and pore volumes from time_axes.clocks.  f = 1 reproduces t_cap at k_bt (asserted).

Outputs: phase1/wormhole_bound.csv, phase1/figures/wormhole_bound.png (+ printed medians [IQR]).
  python3 forsmark_reactive/wormhole_bound.py      (run from src/alpha_study)
"""
from __future__ import annotations

import glob
import re
import sys
from multiprocessing import Pool
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT), str(ROOT / "physics_upscaling")]
from analyze_phase1_mechanism import read_vtu  # noqa: E402
from time_axes import clocks  # noqa: E402
from write_corrected_bigrafv_inputs import read_uge  # noqa: E402
import json  # noqa: E402

P1 = HERE / "phase1"
PV = ROOT / "paraview"
FS = [0.1, 0.2, 0.3, 0.5, 0.75, 1.0]
COL = {4.0: "#86b6ef", 6.0: "#2a78d6", 8.0: "#104281", 16.0: "#e08a1e"}


def s90(Q, frac=0.9):
    o = np.argsort(Q)[::-1]
    n = int(np.searchsorted(np.cumsum(Q[o]) / Q.sum(), frac) + 1)
    return o[:n]


def outlet_diss(a):
    q = np.abs(a["Q_frac"]).astype(float)
    out = a["x_center"] > 400
    return float((q[out] * a["fraction_dissolved"][out]).sum() / q[out].sum()) if q[out].sum() > 0 else np.nan


def one(args):
    run, kbt_csv = args
    run = Path(run)
    m = re.search(r"p([\d.]+)_sg([\d.]+)_seed(\d)", str(run))
    p32, sigma, seed = float(m[1]), float(m[2]), int(m[3])
    mode = "gypcal" if "calcite" in run.name else "gyponly"
    pvdir = PV / f"{run.parent.name}__{run.name}"
    pat = pd.read_csv(run / "patterns.csv").dropna(subset=["t_y"]).sort_values("k").set_index("k", drop=False)
    ch = pd.read_csv(run / "channelization.csv")
    key = dict(p32=p32, sigma=sigma, seed=seed, mode=mode)
    files = {int(f.stem.split("_")[1]): f for f in pvdir.glob("fractures_*.vtu")}
    if not files:
        return [], dict(key, why="no VTUs")
    kbt = kbt_csv
    if kbt is None:       # same definition as analyze_phase1_mechanism.py
        for k in sorted(files):
            if k in pat.index and outlet_diss(read_vtu(files[k])) >= 0.5:
                kbt = k
                break
    if kbt is None or kbt not in files:
        return [], dict(key, why="no breakthrough state")
    # channel set at the n90 minimum (first state of the minimum; states without a VTU are not candidates)
    cc = ch[ch.k.isin(list(files))]
    kn = int(cc.k[cc.n90.idxmin()])
    a_n = read_vtu(files[kn])
    chan = s90(np.abs(a_n["Q_frac"]).astype(float))
    a = read_vtu(files[kbt])
    nf = len(a["Q_frac"])
    cells, _ = read_uge(run / "full_mesh_vol_area.uge")
    clk = clocks(run)
    inv = cells[:nf, 4] * clk.vf0
    inv = inv / inv.sum()
    d = a["fraction_dissolved"].astype(float)
    is_ch = np.zeros(nf, bool)
    is_ch[chan] = True
    D_ch, D_off = float((d * inv)[is_ch].sum()), float((d * inv)[~is_ch].sum())
    D_bt = float(pat.loc[kbt, "dissolved"])
    assert abs(D_ch + D_off - D_bt) <= 1e-6 * D_bt, (run, D_ch + D_off, D_bt)
    t, D = pat.t_y.to_numpy(float), np.maximum.accumulate(pat.dissolved.to_numpy(float))

    def t_of(x):          # invert the monotone dissolved-vs-time curve (first time D reaches x)
        return float(np.interp(x, D, t))

    tbt = float(clk.t_cap(pat.loc[kbt, "t_y"]))
    rows = []
    for f in FS:
        lo, hi = f * D_bt, f * D_ch + D_off
        tl, th = t_of(lo), t_of(hi)
        r = dict(key, f=f, D_bt=D_bt, D_ch=D_ch, D_off=D_off, D_lo=lo, D_hi=hi, tcap_bt=tbt,
                 tcap_lo=float(clk.t_cap(tl)), tcap_hi=float(clk.t_cap(th)), pv_lo=float(clk.pv(tl)), pv_hi=float(clk.pv(th)),
                 k_bt=kbt, k_n90=kn)
        if f == 1.0:
            assert abs(r["tcap_lo"] - tbt) <= 1e-6 * tbt, (run, r["tcap_lo"], tbt)
        rows.append(r)
    return rows, None


def main():
    mech = pd.read_csv(P1 / "phase1_mechanism.csv")
    mech = mech[mech.tag == "phase1"]
    bt = {}
    for key, g in mech.groupby(["p32", "sigma", "seed", "mode"]):
        r = g[g.outlet_diss >= 0.5]
        bt[key] = int(r.k.min()) if len(r) else None
    jobs = []
    for r in sorted(glob.glob(str(P1 / "L2_r15_p*_sg*_seed*/gyp*__uncorrected_graph__phase1"))):
        if not (Path(r) / "patterns.csv").exists():
            continue
        m = re.search(r"p([\d.]+)_sg([\d.]+)_seed(\d)", r)
        key = (float(m[1]), float(m[2]), int(m[3]), "gypcal" if "calcite" in Path(r).name else "gyponly")
        if key[0] == 16.0:
            jobs.append((r, None))
        elif key in bt:
            jobs.append((r, bt[key]))
    with Pool(4) as p:
        res = p.map(one, jobs)
    rows = [x for rs, _ in res for x in rs]
    skipped = [s for _, s in res if s]
    df = pd.DataFrame(rows)
    df.to_csv(P1 / "wormhole_bound.csv", index=False)
    print(f"{len(jobs)} runs, {len(df) // len(FS)} with a breakthrough state; skipped: {skipped}")

    # table: medians [IQR]
    def mq(x):
        q = np.nanpercentile(x, [25, 50, 75])
        return f"{q[1]:.3g} [{q[0]:.3g}-{q[2]:.3g}]"
    base = df[df.f == 1.0].assign(ch_share=lambda d: d.D_ch / d.D_bt)
    for (p32, mode), g in base.groupby(["p32", "mode"]):
        print(f"\nx{p32:g} {mode} (n={len(g)})  D_bt {mq(g.D_bt)}  D_ch/D_bt {mq(g.ch_share)}  tcap_bt {mq(g.tcap_bt)}")
        for f in (0.1, 0.3, 0.5):
            h = df[(df.p32 == p32) & (df["mode"] == mode) & (df.f == f)]
            print(f"   f={f}: D_lo {mq(h.D_lo)}  D_hi {mq(h.D_hi)}  tcap_lo {mq(h.tcap_lo)}  tcap_hi {mq(h.tcap_hi)}")

    # figure
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
    for ax, mode, ttl in zip(axs, ["gyponly", "gypcal"], ["gypsum only", "coupled gypsum-calcite"]):
        for p32 in sorted(df.p32.unique()):
            g = df[(df.p32 == p32) & (df["mode"] == mode)].groupby("f")
            med = g[["D_lo", "D_hi", "D_bt"]].median()
            ax.fill_between(med.index, med.D_lo, med.D_hi, color=COL[p32], alpha=0.3, lw=0)
            ax.plot(med.index, med.D_lo, color=COL[p32], lw=1.5, label=f"P32 x{p32:g}")
            ax.plot(med.index, med.D_hi, color=COL[p32], lw=1.5, ls=":")
            ax.axhline(med.D_bt.iloc[0], color=COL[p32], ls="--", lw=0.8)
        ax.set_title(ttl)
        ax.set_xlabel("f (fraction of a channel fracture dissolved at passage)")
    axs[0].set_ylabel("dissolved fraction at breakthrough")
    axs[0].legend(title="solid: lower, dotted: upper\ndashed: model", fontsize=8)
    fig.tight_layout()
    (P1 / "figures").mkdir(exist_ok=True)
    fig.savefig(P1 / "figures" / "wormhole_bound.png", dpi=150)


if __name__ == "__main__":
    main()
