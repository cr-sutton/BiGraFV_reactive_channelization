#!/usr/bin/env python3
"""
Ceiling sweep analysis (6 Nov 2026; rules R1-R3 of CEILING_SWEEP.md, fixed before the runs).
Per run on the 9 Phase 3 networks: depth, inheritance (channelization.csv) and breakthrough (flow re-solved at every
saved state, compare_scale.mech_2km with the 1 km outlet window x > 400 m), all within capacity time <= 2, plus the
network k_eff gain at the last state.  Ceiling C = (phi_end / phi0)^n, phi_end = 1 (gypsum-only) or 1 - vf0 * 0.494
(coupled, full replacement by calcite).
  DYLD_LIBRARY_PATH=/opt/homebrew/Cellar/freetype/2.14.1_1/lib python3 forsmark_reactive/ceilsweep/analyze_ceilsweep.py
  -> ceilsweep_runs.csv, ceilsweep_tests.csv, ceilsweep_depth.png
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402

HERE = Path(__file__).resolve().parent
FR = HERE.parent
sys.path[:0] = [str(FR / "scale2km"), str(FR), str(FR.parent), str(FR.parent / "physics_upscaling")]
from compare_scale import TCAP_MAX, chan, events, mech_2km  # noqa: E402

GAMMA = 0.494
NETS = [(p, s) for p in (4.0, 6.0, 8.0) for s in (1, 2, 3)]
LAWS = [("phase3_phi0182", 1.0, 0.182), ("phase1", 1.0, 0.1), ("ceilN148", 1.4771, 0.1), ("ceilN2", 2.0, 0.1),
        ("ceilN3", 3.0, 0.1), ("kphi_n3", 3.0, 0.1)]
COL = {"gyponly": "#1f5f8b", "gypcal": "#c4472d"}


def ceiling(mode, n, phi0):
    phi_end = 1.0 if mode == "gyponly" else 1 - (1 - phi0) * GAMMA
    return (phi_end / phi0) ** n


def collect():
    rows = []
    for p, s in NETS:
        net = FR / "phase1" / f"L2_r15_p{p}_sg1.0_seed{s}"
        for tag, n, phi0 in LAWS:
            for mode, mdir in (("gyponly", "gypsum"), ("gypcal", "gypsum_calcite")):
                run = net / f"{mdir}__uncorrected_graph__{tag}"
                if not ((run / "channelization.csv").exists() and (run / "patterns.csv").exists()):
                    continue
                g = mech_2km(run, xout=400.0)
                g = g[g.t_cap <= TCAP_MAX].sort_values("k").reset_index(drop=True)
                c = pd.read_csv(run / "channelization.csv")
                c = c[c.k.isin(g.k)].sort_values("k")
                rows.append(dict(p32=p, seed=s, mode=mode, tag=tag, n=n, phi0=phi0, C=ceiling(mode, n, phi0), **events(g),
                                 **chan(run, g), keff_gain_end=float(c.k_eff_ratio.iloc[-1]) if len(c) else np.nan,
                                 t_cap_end=float(g.t_cap.max())))
    return pd.DataFrame(rows)


def tests(R):
    out, res = {}, []
    rho = []
    for (p, s), h in R[R["mode"] == "gyponly"].groupby(["p32", "seed"]):
        if len(h) >= 3:
            rho.append(spearmanr(np.log10(h.C), h.depth).statistic)
    out["R1_networks"] = len(rho)
    out["R1_rho_minus1"] = int(sum(np.isclose(r, -1) for r in rho))
    out["R1_pass"] = bool(len(rho) == 9 and out["R1_rho_minus1"] >= 7)
    for (p, s), h in R.groupby(["p32", "seed"]):
        gy = h[h["mode"] == "gyponly"].sort_values("C")
        for _, r in h[h["mode"] == "gypcal"].iterrows():
            if len(gy) >= 2 and gy.C.min() <= r.C <= gy.C.max():
                ref = np.interp(np.log10(r.C), np.log10(gy.C), gy.depth)
                res.append(dict(p32=p, seed=s, tag=r.tag, C=r.C, depth_cal=r.depth, depth_gyp_interp=ref, residual=r.depth - ref))
    res = pd.DataFrame(res)
    if len(res):
        out["R2_n"] = len(res)
        out["R2_median_abs"] = float(res.residual.abs().median())
        out["R2_median"] = float(res.residual.median())
        out["R2_pass_005"] = bool(out["R2_median_abs"] <= 0.05 and abs(out["R2_median"]) <= 0.05)
        out["R2_pass_003"] = bool(out["R2_median_abs"] <= 0.03 and abs(out["R2_median"]) <= 0.03)
    sl, q = [], []
    for (p, s), h in R[R["mode"] == "gyponly"].groupby(["p32", "seed"]):
        if len(h) >= 4:
            x = np.log10(h.C)
            sl.append(np.polyfit(x, h.depth, 1)[0])
            q.append(np.polyfit(x, h.depth, 2)[0])
    out["R3_slope_median_per_decade"] = float(np.median(sl)) if sl else np.nan
    out["R3_quadratic_median"] = float(np.median(q)) if q else np.nan
    out["R3_quadratic_positive"] = int(sum(np.array(q) > 0)) if q else 0
    return out, res


def figure(R, res):
    fig, axs = plt.subplots(1, 2, figsize=(12.5, 4.6), constrained_layout=True, gridspec_kw=dict(width_ratios=[1.6, 1]))
    ax = axs[0]
    for (p, s), h in R.groupby(["p32", "seed"]):
        gy = h[h["mode"] == "gyponly"].sort_values("C")
        ax.plot(gy.C, gy.depth, "-o", color=COL["gyponly"], lw=1, ms=4, alpha=0.6)
        cp = h[h["mode"] == "gypcal"].sort_values("C")
        ax.plot(cp.C, cp.depth, "s", color=COL["gypcal"], ms=5, alpha=0.75, mfc="white", mew=1.4)
    e0 = FR / "phase1" / "kphi_e0" / "kphi_e0_summary.csv"
    if e0.exists():
        e = pd.read_csv(e0)
        e = e[np.isclose(e.ceiling, 10, rtol=0.02)]
        ax.errorbar([10], [e.depth.median()], yerr=[[e.depth.median() - e.depth.min()], [e.depth.max() - e.depth.median()]],
                    fmt="none", ecolor="0.3", capsize=5, lw=1.6)
        ax.annotate("law shape at ×10\n(E0, one network)", (10, e.depth.max()), xytext=(14, e.depth.max() + 0.06), fontsize=8,
                    color="0.3")
    ax.set_xscale("log")
    ax.set_xlabel("attainable permeability gain of a fully reacted fracture, C (k / k$_0$)")
    ax.set_ylabel("channel depth: PR$_V$ minimum / start\n(lower = more focused)")
    ax.plot([], [], "-o", color=COL["gyponly"], label="gypsum-only (one line per network)")
    ax.plot([], [], "s", color=COL["gypcal"], mfc="white", mew=1.4, label="coupled gypsum–calcite")
    ax.legend(frameon=False, fontsize=8.5, loc="lower left")
    ax.set_title("A. Depth against the attainable gain, 9 networks", fontsize=10, loc="left")
    ax = axs[1]
    if len(res):
        ax.axhspan(-0.05, 0.05, color="0.92")
        ax.axhline(0, color="0.6", lw=0.8)
        ax.scatter(res.C, res.residual, color=COL["gypcal"], s=22)
        ax.set_xscale("log")
    ax.set_xlabel("coupled ceiling C")
    ax.set_ylabel("coupled depth − gypsum-only depth\nat the same C (same network)")
    ax.set_title("B. Do the chemistries collapse?", fontsize=10, loc="left")
    for a in axs:
        a.spines[["top", "right"]].set_visible(False)
    fig.savefig(HERE / "ceilsweep_depth.png", dpi=150)
    plt.close(fig)


def main():
    R = collect()
    R.to_csv(HERE / "ceilsweep_runs.csv", index=False)
    T, res = tests(R)
    res.to_csv(HERE / "ceilsweep_residuals.csv", index=False)
    pd.Series(T).to_csv(HERE / "ceilsweep_tests.csv", header=["value"])
    figure(R, res)
    pd.set_option("display.width", 250)
    print(R.groupby(["mode", "tag"]).agg(n=("depth", "size"), C=("C", "median"), depth=("depth", "median"),
                                         bt=("breakthrough", "median"), inh=("inheritance", "median")).round(3))
    print(pd.Series(T).to_string())


if __name__ == "__main__":
    main()
