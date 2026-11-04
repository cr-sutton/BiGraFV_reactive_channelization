#!/usr/bin/env python3
"""
WORMHOLE_CHECKS Check 1: regime map of the flowing fractures of the Phase 1 networks (initial state) on the
Li et al. 2026 (GRL 53, e2026GL123899) pattern diagram. Formulas as in forsmark_reactive/lit/lit_wormhole_regime.md.

Inputs per network: lit.state0 (S, b, Q at the build rate), Q rescaled to the run rate (one pore volume per
year, as forsmark_damkohler.py), L = w = sqrt(S), gypsum k_lin, D = 1e-9, Sh = 8, n_s = 2.
Flowing fractures = the 90 %-flow set of the initial state (s90 of analyze_channelization.py).
Per fracture, with q0 = Q/w:
    Pe          = q0 / D
    keff        = k / (1 + 2 k b / (D Sh)),  k = k_lin * R  (deck, R = SSA rho vf0 b / 2)  or  k = k_lin  (R = 1)
    Da_eff,L    = n_s keff L / q0           (uniform if 1/Da_eff,L >= 0.278)
    Lambda^-1   = q0 / sqrt(n_s keff D b)   (compact if Lambda^-1 <= 0.237)
    wormhole otherwise; the corner 1/Da_eff,L >= 0.278 and Lambda^-1 <= 0.237 is flagged "overlap", not resolved.
Flags: in_valid = L in 0.1-30 m and Pe in 1.4-1000 (Li); in_da = Da_eff,L <= 4e3 (largest published Da_eff).

  python3 forsmark_reactive/wormhole_regime_map.py   (run from src/alpha_study)
Outputs: phase1/wormhole_regime.csv, phase1/wormhole_regime_summary.csv, phase1/figures/wormhole_regime.png
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent), str(HERE.parent / "physics_upscaling")]
import compute_literature_damkohler as lit  # noqa: E402
from analyze_channelization import s90  # noqa: E402
from write_corrected_bigrafv_inputs import read_uge  # noqa: E402

P1 = HERE / "phase1"
VF0, NS = 0.9, 2
D, SH = lit.D_MOL, lit.SH
GYP = lit.CHEM["gypsum"]
UNI, COMP = 0.278, 0.237
L_RNG, PE_RNG, DA_MAX = (0.1, 30.0), (1.4, 1000.0), 4e3
REGS = ["uniform", "wormhole", "compact", "overlap"]


def regime(da_inv, lam_inv):
    uni, comp = da_inv >= UNI, lam_inv <= COMP
    return np.where(uni & comp, "overlap", np.where(uni, "uniform", np.where(comp, "compact", "wormhole")))


def network_fractures(net: Path):
    s = lit.state0(net)
    cells, _ = read_uge(net / "model_graph_raw" / "full_mesh_vol_area.uge")
    q_run = cells[:, 4].sum() * (1 - VF0) / (365.25 * 86400)
    S, b, Q = s["S"], s["b"], s["Q"] * q_run / s["rate"]
    w = L = np.sqrt(S)
    idx = s90(Q)
    R = GYP["ssa"] * GYP["rho"] * VF0 * b / 2
    rows = []
    for tag, kk in (("R", GYP["k_lin"] * R), ("R1", GYP["k_lin"] * np.ones_like(b))):
        keff = kk / (1 + 2 * kk * b / (D * SH))
        q0 = Q / w
        pe = q0 / D
        da = NS * keff * L / q0
        lam = q0 / np.sqrt(NS * keff * D * b)
        reg = regime(1 / da, lam)
        df = pd.DataFrame(dict(network=net.name, k_choice=tag, fracture=idx, Q_m3s=Q[idx], flow_share=Q[idx] / Q[idx].sum(),
                               L_m=L[idx], b_m=b[idx], Pe=pe[idx], Da_effL=da[idx], Da_effL_inv=1 / da[idx], Lambda_inv=lam[idx],
                               regime=reg[idx]))
        df["in_validated"] = (df.L_m.between(*L_RNG)) & (df.Pe.between(*PE_RNG))
        df["in_Da_range"] = df.Da_effL <= DA_MAX
        rows.append(df)
    return pd.concat(rows)


def wmed(x, w):
    o = np.argsort(x.values); c = np.cumsum(w.values[o]) / w.sum()
    return float(x.values[o][np.searchsorted(c, 0.5)])


def summarize(df, keys):
    out = []
    for key, g in df.groupby(keys):
        r = dict(zip(keys, key if isinstance(key, tuple) else (key,)))
        r["n_fractures"] = len(g)
        for rg in REGS:
            m = g.regime == rg
            r[f"frac_{rg}"] = m.mean()
            r[f"flow_{rg}"] = g.flow_share[m].sum() / g.flow_share.sum()
        r["frac_in_validated"] = g.in_validated.mean()
        r["flow_in_validated"] = g.flow_share[g.in_validated].sum() / g.flow_share.sum()
        r["frac_in_Da_range"] = g.in_Da_range.mean()
        r["flow_in_Da_range"] = g.flow_share[g.in_Da_range].sum() / g.flow_share.sum()
        for c in ("Pe", "Da_effL", "Lambda_inv", "L_m"):
            r[f"{c}_p50"] = g[c].median()
            r[f"{c}_p25"], r[f"{c}_p75"] = g[c].quantile([0.25, 0.75])
            r[f"{c}_flowp50"] = wmed(g[c], g.flow_share)
        out.append(r)
    return pd.DataFrame(out)


def figure(df, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LogNorm
    fig, axs = plt.subplots(1, 2, figsize=(13, 5.6), sharex=True, sharey=True)
    xl, yl = (1e-10, 1e2), (1e-3, 1e3)
    for ax, (tag, title) in zip(axs, (("R", "k as in the deck (with area factor R)"), ("R1", "k per flat wall area (R = 1)"))):
        g = df[(df.k_choice == tag) & (df.P32 != 16)]
        ax.axvspan(1 / DA_MAX, xl[1], color="tab:green", alpha=0.12, label="inside largest published Da_eff,L (<= 4e3)")
        nb = 60
        xb = np.logspace(*np.log10(xl), nb); yb = np.logspace(*np.log10(yl), nb)
        H, _, _ = np.histogram2d(g.Da_effL_inv, g.Lambda_inv, bins=[xb, yb], weights=g.flow_share / g.network.nunique())
        H = np.ma.masked_where(H <= 0, H)
        pc = ax.pcolormesh(xb, yb, H.T, norm=LogNorm(vmin=1e-5, vmax=max(H.max(), 1e-4)), cmap="viridis")
        ax.axvline(UNI, color="k", ls="--"); ax.axhline(COMP, color="r", ls="--")
        ax.text(UNI * 1.3, 2e-3, "uniform", rotation=90, va="bottom"); ax.text(1.5e-10, 1.5, "wormhole", color="k")
        ax.text(1.5e-10, 0.05, "compact", color="k")
        ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(xl); ax.set_ylim(yl)
        ax.set_xlabel(r"$Da_{eff,L}^{-1} = l_p/L$"); ax.set_title(title, fontsize=10)
        ax.text(0.02, 0.97, f"flow inside Li's validated range (L 0.1-30 m, Pe 1.4-1000): {100*g.flow_share[g.in_validated].sum()/g.flow_share.sum():.1f} %\n"
                f"flow inside Da_eff,L <= 4e3: {100*g.flow_share[g.in_Da_range].sum()/g.flow_share.sum():.2g} %",
                transform=ax.transAxes, va="top", fontsize=8, bbox=dict(fc="w", alpha=0.85))
    axs[0].set_ylabel(r"$\Lambda^{-1} = l_p/l_t$")
    axs[0].legend(loc="lower right", fontsize=8)
    fig.colorbar(pc, ax=axs, label="flow share per network (mean over 45 networks, P32 x4/x6/x8)")
    fig.suptitle("Li et al. 2026 regime map: 90 %-flow fractures, initial state. Boundaries: 1/Da_eff,L = 0.278 (dashed black), Lambda^-1 = 0.237 (dashed red). "
                 "Points lie outside the validated range; regime labels are extrapolations.", fontsize=9)
    fig.savefig(path, dpi=150, bbox_inches="tight")


def main():
    nets = sorted(p for p in P1.glob("L2_r15_p*_sg*_seed*") if p.is_dir())
    parts = []
    for i, net in enumerate(nets):
        print(f"[{i+1}/{len(nets)}] {net.name}", flush=True)
        d = network_fractures(net)
        d.insert(1, "P32", int(float(net.name.split("_p")[1].split("_")[0])))
        parts.append(d)
    df = pd.concat(parts, ignore_index=True)
    df.to_csv(P1 / "wormhole_regime.csv", index=False)
    summ = pd.concat([summarize(df, ["P32", "k_choice", "network"]).assign(level="network"),
                      summarize(df, ["P32", "k_choice"]).assign(level="P32")], ignore_index=True)
    summ.to_csv(P1 / "wormhole_regime_summary.csv", index=False)
    (P1 / "figures").mkdir(exist_ok=True)
    figure(df, P1 / "figures" / "wormhole_regime.png")
    # printed table: pooled fractures per P32 (medians [IQR]; flow shares of pooled flow, per-network flow normalised)
    p = summarize(df.assign(flow_share=df.flow_share), ["k_choice", "P32"])
    fm = lambda r, c, f="{:.2g}": f"{f.format(r[c+'_p50'])} [{f.format(r[c+'_p25'])}-{f.format(r[c+'_p75'])}]"
    for kc in ("R", "R1"):
        print(f"\nk choice {kc}")
        for _, r in p[p.k_choice == kc].iterrows():
            print(f"P32 x{int(r.P32)} n={int(r.n_fractures)}  Pe {fm(r,'Pe')}  Da_effL {fm(r,'Da_effL')}  Lam^-1 {fm(r,'Lambda_inv')}  L {fm(r,'L_m')}")
            print("   flow share: " + " ".join(f"{g} {100*r['flow_'+g]:.1f}%" for g in REGS)
                  + f" | flow in validated range {100*r.flow_in_validated:.1f}% (frac {100*r.frac_in_validated:.1f}%), flow Da_eff,L<=4e3 {100*r.flow_in_Da_range:.2g}%")
            print("   fracture share: " + " ".join(f"{g} {100*r['frac_'+g]:.1f}%" for g in REGS))


if __name__ == "__main__":
    main()
