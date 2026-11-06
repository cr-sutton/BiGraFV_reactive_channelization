#!/usr/bin/env python3
"""
k-phi shape pilot E0 (6 Nov 2026, KPHI_WORKPLAN.md): one network (P32 x6, sigma 1, seed 1), gypsum-only, to capacity time 2.
Same ceiling x10 with four shapes (n = 0.5 / 1 / 2 / 8, phi_c from the ceiling), plus n = 3 (ceiling x1000) for reference.

Outputs (forsmark_reactive/phase1/kphi_e0/):
  kphi_e0_summary.csv   per law: depth, d at deepest focusing, breakthrough, n90 min / start, inheritance, k_eff gain,
                        median and 95th-percentile open and hydraulic aperture before and after
  kphi_e0_curves.png    law shape (with realized cells), PR_V / start and network k_eff against the dissolved fraction
  kphi_e0_apertures.png histograms over the network's fractures, before vs after (capacity time 2):
                        open (physical) aperture = porosity x b_h; hydraulic aperture b_T = (12 k b_h)^(1/3) = b_h (k/k0)^(1/3)
b_h = the fracture's dfnWorks hydraulic aperture = slab thickness of its cell (k0 = b_h^2 / 12).

  python3 forsmark_reactive/kphi_e0_report.py
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(HERE / "scale2km"), str(ROOT), str(ROOT / "physics_upscaling")]
from compare_scale import TCAP_MAX, chan, events, mech_2km  # noqa: E402
from analyze_km_dissolution_patterns import read_scalar_from_vtk  # noqa: E402
from time_axes import clocks  # noqa: E402

NET = HERE / "phase1" / "L2_r15_p6.0_sg1.0_seed1"
OUT = HERE / "phase1" / "kphi_e0"
OUT.mkdir(exist_ok=True)
P0 = 0.1
LAWS = [  # label, tag, n, phi_c, colour
    ("n = 0.5 (concave)", "kphiC10n05", 0.5, 0.09090909091, "#2a9d8f"),
    ("n = 1 (current)", "phase1", 1.0, 0.0, "#1f5f8b"),
    ("n = 2 (convex)", "kphiC10n2", 2.0, -0.316227766, "#e9a23b"),
    ("n = 8 (near-exponential)", "kphiC10n8", 8.0, -2.598477259, "#c4472d"),
    ("n = 3, ceiling ×1000", "kphi_n3", 3.0, 0.0, "#6b4fbb"),
]
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
b_h = np.loadtxt(NET / "model_graph_raw" / "aperture.dat")
nf = len(b_h)


def law(d, n, pc):
    phi = P0 + (1 - P0) * d
    return ((phi - pc) / (P0 - pc)) ** n


def state_at(run, tcap):
    """vtk file of the last saved state with capacity time <= tcap."""
    pat = pd.read_csv(run / "patterns.csv")
    c = clocks(run)
    pat["tc"] = [float(c.t_cap(t)) for t in pat.t_y]
    k = int(pat[pat.tc <= tcap].k.max())
    return run / f"single_stage-{k:03d}.vtk", k


def cells(vtk):
    gyp = np.asarray(read_scalar_from_vtk(str(vtk), "Gypsum_VF"), float)[:nf]
    kk = np.asarray(read_scalar_from_vtk(str(vtk), "Permeability"), float)[:nf]
    return np.clip(1 - gyp, 0, 1), kk


rows, curves, aps = [], {}, {}
for lab, tag, n, pc, col in LAWS:
    run = NET / f"gypsum__uncorrected_graph__{tag}"
    if not (run / "channelization.csv").exists():
        print("not finished:", tag)
        continue
    g = mech_2km(run, xout=400.0, use_cache=(tag != "phase1"))
    g = g[g.t_cap <= TCAP_MAX].sort_values("k")
    ch = pd.read_csv(run / "channelization.csv")
    ch = ch[ch.k.isin(g.k)].sort_values("k")
    v0, _ = state_at(run, 0.0)
    v1, k1 = state_at(run, TCAP_MAX)
    phi0, k0 = cells(v0)
    phi1, kk1 = cells(v1)
    assert np.allclose(k0, b_h ** 2 / 12, rtol=1e-3), "cell order does not match aperture.dat"
    ap = dict(open0=phi0 * b_h, open1=phi1 * b_h, hyd0=b_h * (k0 / k0) ** (1 / 3), hyd1=b_h * (kk1 / k0) ** (1 / 3),
              d1=(phi1 - P0) / (1 - P0), g1=kk1 / k0)
    aps[lab] = ap
    curves[lab] = (g, ch)
    rows.append(dict(law=lab, n=n, phi_c=pc, ceiling=law(1.0, n, pc), gain_at_half=law(0.5, n, pc), **events(g), **chan(run, g),
                     keff_gain_max=float(ch.k_eff_ratio.max()), final_state_k=k1, final_dissolved=float(g.dissolved.iloc[-1]),
                     law_max_rel_err=float(np.nanmax(np.abs(ap["g1"] / law(np.clip(ap["d1"], 0, 1), n, pc) - 1))),
                     open_med0_um=1e6 * np.median(ap["open0"]), open_med1_um=1e6 * np.median(ap["open1"]),
                     open_p95_1_um=1e6 * np.percentile(ap["open1"], 95),
                     hyd_med0_um=1e6 * np.median(ap["hyd0"]), hyd_med1_um=1e6 * np.median(ap["hyd1"]),
                     hyd_p95_1_um=1e6 * np.percentile(ap["hyd1"], 95), hyd_max_ratio=float(np.max(ap["hyd1"] / ap["hyd0"]))))
S = pd.DataFrame(rows)
S.to_csv(OUT / "kphi_e0_summary.csv", index=False)
pd.set_option("display.width", 250)
print(S.round(3).to_string(index=False))

# Figure 1: law, PR_V, k_eff
fig, axs = plt.subplots(1, 3, figsize=(14, 4.3), constrained_layout=True)
d = np.linspace(0, 1, 201)
for lab, tag, n, pc, col in LAWS:
    lw = 2.6 if tag == "phase1" else 1.8
    axs[0].plot(d, law(d, n, pc), color=col, lw=lw, label=lab)
    if lab in aps:
        ap = aps[lab]
        m = ap["d1"] > 0.01
        axs[0].scatter(ap["d1"][m][::7], ap["g1"][m][::7], s=5, color=col, alpha=0.35, lw=0)
    if lab in curves:
        g, ch = curves[lab]
        axs[1].plot(g.dissolved, g.pr_frac / g.pr_frac.iloc[0], color=col, lw=lw)
        axs[2].plot(ch.dissolved, ch.k_eff_ratio, color=col, lw=lw)
axs[0].set_yscale("log")
axs[0].set_ylim(0.8, 1500)
axs[0].set_xlabel("fraction of a fracture's gypsum dissolved")
axs[0].set_ylabel("k / k$_0$ of that fracture")
axs[0].set_title("A. The laws (lines) and the cells at the end (dots)", fontsize=10, loc="left")
axs[0].legend(frameon=False, fontsize=8.5, loc="upper left")
axs[1].axhline(1, color="0.85", lw=0.8)
axs[1].set_xlabel("fraction of the network's gypsum dissolved")
axs[1].set_ylabel("PR$_V$ / its start  (lower = more channelized)")
axs[1].set_title("B. Flow focusing", fontsize=10, loc="left")
axs[2].set_yscale("log")
axs[2].set_xlabel("fraction of the network's gypsum dissolved")
axs[2].set_ylabel("network k$_{eff}$ / start")
axs[2].set_title("C. Network permeability", fontsize=10, loc="left")
fig.suptitle("Same ×10 ceiling, different paths to it (P32 ×6, σ 1, seed 1, gypsum-only, to capacity time 2); "
             "purple: n = 3 with a ×1000 ceiling", fontsize=10.5)
fig.savefig(OUT / "kphi_e0_curves.png", dpi=150)
plt.close(fig)

# Figure 2: aperture histograms before / after
labs = [l for l, *_ in LAWS if l in aps]
fig, axs = plt.subplots(2, len(labs), figsize=(3.1 * len(labs), 5.6), sharey="row", constrained_layout=True)
bins = np.logspace(np.log10(2e-6), np.log10(3e-3), 45)
for j, lab in enumerate(labs):
    col = [c for l, _, _, _, c in LAWS if l == lab][0]
    ap = aps[lab]
    for i, (a0, a1, name) in enumerate((("open0", "open1", "open (physical) aperture"), ("hyd0", "hyd1", "hydraulic aperture"))):
        ax = axs[i, j]
        ax.hist(ap[a0], bins=bins, color="0.6", alpha=0.55, label="before")
        ax.hist(ap[a1], bins=bins, histtype="step", color=col, lw=1.8, label="after")
        ax.set_xscale("log")
        ax.axvline(np.median(ap[a0]), color="0.45", ls=":", lw=1)
        ax.axvline(np.median(ap[a1]), color=col, ls=":", lw=1.2)
        if j == 0:
            ax.set_ylabel(f"fractures\n{name}")
        if i == 0:
            ax.set_title(lab, fontsize=9.5)
        if i == 1:
            ax.set_xlabel("aperture (m)")
        ax.text(0.98, 0.95, f"median {1e6*np.median(ap[a0]):.0f} → {1e6*np.median(ap[a1]):.0f} µm\n"
                f"95th pct → {1e6*np.percentile(ap[a1],95):.0f} µm", transform=ax.transAxes, ha="right", va="top", fontsize=7.5)
axs[0, 0].legend(frameon=False, fontsize=8, loc="upper left")
fig.suptitle("Aperture of every fracture before reaction and at capacity time 2. Open aperture = porosity × slab thickness b$_h$; "
             "hydraulic aperture = b$_h$ (k/k$_0$)$^{1/3}$ (cubic law)", fontsize=10)
fig.savefig(OUT / "kphi_e0_apertures.png", dpi=150)
plt.close(fig)
print("wrote", OUT)
