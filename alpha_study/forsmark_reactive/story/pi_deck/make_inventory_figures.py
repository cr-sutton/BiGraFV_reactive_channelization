#!/usr/bin/env python3
"""
What was run, and the ensemble overview for the PI deck (9 Nov 2026).
  run_inventory.csv          every reactive run folder under phase1/, scale2km/, lenseries/, dfn_validation/ with its campaign,
                             chemistry, P32, sigma, seed and whether it finished (patterns.csv present)
  run_inventory_summary.csv  counts by campaign
  fig_ens_<mode>_p<P32>.png  network PR_V and active surface d_Q/P32 against PVI, gypsum dissolved d and capacity time:
                             1 km (solid) and 2 km (dashed) on the same axes, one colour per sigma, mean of the 5 seeds as the
                             line and the seed range (min-max) as shading; Phase 1 base runs (n = 1, phi0 0.1, 1 PV/yr)
  DYLD_LIBRARY_PATH=/opt/homebrew/Cellar/freetype/2.14.1_1/lib python3 forsmark_reactive/story/pi_deck/make_inventory_figures.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

H = Path(__file__).resolve().parent
FR = H.parent.parent
sys.path[:0] = [str(FR), str(FR.parent)]
from time_axes import clocks  # noqa: E402

CAMPAIGN = {  # tag -> (campaign, what it varies)
    "phase1": ("Base sweep", "P32 ×4–×16, σ 0/0.5/1, 5 seeds; n = 1, φ0 0.1, 1 PV/yr"),
    "phase2_phi005": ("Starting porosity", "φ0 0.05"),
    "phase2_co3lo": ("Low carbonate", "coupled at 2 mM carbonate"),
    "phase3_phi0182": ("Starting porosity", "φ0 0.182 (gain ×5.5 / ×3.3)"),
    "phase3_rate01": ("Injection rate", "0.1 PV/yr"),
    "phase3_rate10": ("Injection rate", "10 PV/yr"),
    "ceilN148": ("Ceiling sweep (+ run C at σ 0)", "n = 1.48 (×30)"),
    "ceilN2": ("Ceiling sweep (+ run C at σ 0)", "n = 2 (×100)"),
    "ceilN3": ("Ceiling sweep (+ run C at σ 0)", "n = 3 (×1000)"),
    "kphi_n3": ("Ceiling sweep (+ run C at σ 0)", "n = 3 on the example network"),
    "kphiC10n05": ("Law shape at fixed ×10", "n = 0.5"),
    "kphiC10n2": ("Law shape at fixed ×10", "n = 2"),
    "kphiC10n8": ("Law shape at fixed ×10", "n = 8"),
    "ceilN2L": ("Late time (run A)", "n = 2 to capacity time 8"),
    "ceilN3L": ("Late time (run A)", "n = 3 to capacity time 8"),
    "ceilN3XL": ("Late time (run A2)", "n = 3 to capacity time 20"),
    "phase1exfix": ("Outflow-face check", "one network"),
}
ORDER = ["Base sweep", "2 km scale test", "Blind predictor networks (run B)", "Starting porosity", "Low carbonate", "Injection rate",
         "Ceiling sweep (+ run C at σ 0)", "Law shape at fixed ×10", "Late time (run A)", "Late time (run A2)", "Outflow-face check",
         "DFN validation: graph runs", "DFN validation: meshed DFN"]


def inventory():
    rows = []
    pat = re.compile(r"p([\d.]+)_sg([\d.]+)_seed(\d+)")
    for root, scale in (("phase1", "1 km"), ("scale2km", "2 km"), ("lenseries", "1 km")):
        for r in sorted((FR / root).glob("L*_r15_p*_sg*_seed*/gyp*__*")):
            m = pat.search(r.parent.name)
            mode = "coupled" if "calcite" in r.name else "gypsum-only"
            tag = r.name.split("__")[-1]
            if root == "scale2km":
                camp, what = "2 km scale test", "P32 ×4/×6/×8, σ 0/0.5/1, 5 seeds"
            elif root == "lenseries":
                camp, what = "Blind predictor networks (run B)", "12 new 1 km networks, P32 ×4/×8, σ 1"
            else:
                camp, what = CAMPAIGN.get(tag, (tag, ""))
            rows.append(dict(campaign=camp, varies=what, scale=scale, mode=mode, tag=tag, p32=float(m[1]), sigma=float(m[2]),
                             seed=int(m[3]), finished=(r / "patterns.csv").exists(), path=str(r.relative_to(FR))))
    for r in sorted((FR / "dfn_validation").glob("*/gyp*__*")):
        dfn = "__dfn__" in r.name
        rows.append(dict(campaign="DFN validation: meshed DFN" if dfn else "DFN validation: graph runs",
                         varies="500 m trial network (sm), 1:1 checks" if r.name.endswith("sm") else r.name.split("__")[-1],
                         scale="0.5–1 km", mode="coupled" if "calcite" in r.name else "gypsum-only", tag=r.name.split("__")[-1],
                         p32=np.nan, sigma=np.nan, seed=np.nan,
                         finished=(r / "patterns.csv").exists() or (r / "smoke.json").exists(), path=str(r.relative_to(FR))))
    D = pd.DataFrame(rows)
    D.to_csv(H / "run_inventory.csv", index=False)
    S = (D.groupby("campaign").agg(runs=("path", "size"), finished=("finished", "sum"),
                                   gypsum_only=("mode", lambda x: int((x == "gypsum-only").sum())),
                                   coupled=("mode", lambda x: int((x == "coupled").sum())),
                                   networks=("path", lambda x: D.loc[x.index].drop_duplicates(["scale", "p32", "sigma", "seed"]).shape[0]),
                                   varies=("varies", lambda x: "; ".join(sorted(set(x))))).reindex(ORDER).dropna(how="all"))
    S.to_csv(H / "run_inventory_summary.csv")
    graph = D[~D.campaign.str.startswith("DFN validation: meshed")]
    forsmark = D[~D.campaign.str.startswith("DFN")]
    nets = forsmark.drop_duplicates(["scale", "p32", "sigma", "seed"]).shape[0]
    out = dict(total_folders=len(D), graph_runs=len(graph), forsmark_graph_runs=len(forsmark),
               forsmark_graph_finished=int(forsmark.finished.sum()), forsmark_networks=nets,
               dfn_runs=int(D.campaign.str.startswith("DFN validation: meshed").sum()))
    print(S.to_string())
    print(out)
    return out


# ------------------------------------------------------------------------------------------------------------ ensembles
SIGC = {"1 km": {0.0: "#8fc1ea", 0.5: "#3a86c8", 1.0: "#0b2c4a"}, "2 km": {0.0: "#f2b49c", 0.5: "#d9693f", 1.0: "#7a2a12"}}
PVI = np.logspace(1, np.log10(4e4), 200)
DG = np.linspace(0, 0.97, 98)
TC = np.linspace(0, 5, 251)


def series(run, PVI):
    c = pd.read_csv(run / "channelization.csv").sort_values("k")
    cl = clocks(run)
    t = c.t_y.to_numpy(float)
    pv, tc = cl.pv(t), cl.t_cap(t)
    d = np.maximum.accumulate(c.dissolved.to_numpy(float))
    out = {}
    for name, y in (("prv", c.pr_fracture_vol.to_numpy(float)), ("dq", c.dQ_P32.to_numpy(float))):
        a = np.interp(PVI, pv, y, left=np.nan, right=np.nan)
        b = np.interp(DG, d, y, left=np.nan, right=np.nan)
        b[DG > d.max()] = np.nan
        e = np.interp(TC, tc, y, left=np.nan, right=np.nan)
        out[name] = (a, b, e)
    return out, float(pv.max())


def fig_ensemble(mode, md, p32):
    PVI = np.logspace(1, np.log10(4e4), 200) if mode == "gyponly" else np.logspace(0, np.log10(1.3e3), 200)
    fig, axs = plt.subplots(2, 3, figsize=(14, 7.6), constrained_layout=True, sharey="row")
    stats = {}
    for root, ls, scale in (("phase1", "-", "1 km"), ("scale2km", "--", "2 km")):
        for sg, colr in SIGC[scale].items():
            runs = sorted((FR / root).glob(f"L2_r15_p{p32}_sg{sg}_seed*/{md}__uncorrected_graph__phase1"))
            runs = [r for r in runs if (r / "channelization.csv").exists()]
            if not runs:
                continue
            S = [series(r, PVI)[0] for r in runs]
            for i, name in enumerate(("prv", "dq")):
                for j, X in enumerate((PVI, DG, TC)):
                    Z = np.array([s[name][j] for s in S])
                    ok = np.isfinite(Z).sum(0) == len(Z)          # all seeds present: no survivorship jumps
                    m = np.where(ok, np.nanmean(Z, 0), np.nan)
                    lo = np.where(ok, np.nanmin(Z, 0), np.nan)
                    hi = np.where(ok, np.nanmax(Z, 0), np.nan)
                    ax = axs[i, j]
                    ax.fill_between(X, lo, hi, color=colr, alpha=0.08, lw=0)
                    ax.plot(X, m, ls, color=colr, lw=2, label=f"{scale}, σ {sg:g} (n = {len(runs)})" if (i, j) == (0, 0) else None)
                    if j == 1:
                        stats[f"{scale}_sg{sg:g}_{name}"] = dict(start=float(m[0]), min=float(np.nanmin(m)),
                                                                d_at_min=float(DG[int(np.nanargmin(m))]), n=len(runs))
    for j, (xl, sc) in enumerate(((f"pore volumes injected (PVI, log; 1 t$_{{cap}}$ = {7259 if mode == 'gyponly' else 233} PVI)", "log"), ("gypsum dissolved d", "linear"),
                                  ("capacity time t$_{cap}$", "linear"))):
        for i in range(2):
            axs[i, j].set_xscale(sc)
            axs[i, j].grid(color="#e6e5e1", lw=0.7, which="both")
            axs[1, j].set_xlabel(xl)
        axs[0, j].set_title(["A. against PVI", "B. against gypsum dissolved", "C. against capacity time"][j], fontsize=10.5, loc="left")
    axs[0, 0].set_ylabel("network PR$_V$ (share of fracture volume carrying flow)")
    axs[1, 0].set_ylabel("active surface d$_Q$/P32 (% of fracture area)")
    axs[0, 0].legend(fontsize=8, frameon=False, loc="lower left", ncol=2)
    lab = "gypsum-only" if mode == "gyponly" else "coupled gypsum–calcite"
    for i in range(2):
        axs[i, 2].set_xlim(0, 3)
    fig.suptitle(f"{lab}, P32 ×{p32:g}: 1 km blue solid" + (", 2 km rust dashed" if p32 != 16 else " (×16 was run at 1 km only)") + "; σ darker = more transmissivity spread; "
                 "line = mean of 5 seeds (where all 5 have data), band = seed range", fontsize=11, x=0.01,
                 ha="left")
    name = f"fig_ens_{mode}_p{p32:g}.png"
    fig.savefig(H / name, dpi=150)
    plt.close(fig)
    print("wrote", name)
    return stats


if __name__ == "__main__":
    out = {"inventory": inventory(), "ensembles": {}}
    if "--inventory-only" not in sys.argv:
        for mode, md in (("gyponly", "gypsum"), ("gypcal", "gypsum_calcite")):
            for p in (4.0, 6.0, 8.0, 16.0):
                out["ensembles"][f"{mode}_p{p:g}"] = fig_ensemble(mode, md, p)
    p = H / "inventory_numbers.json"
    p.write_text(json.dumps(out, indent=1))
