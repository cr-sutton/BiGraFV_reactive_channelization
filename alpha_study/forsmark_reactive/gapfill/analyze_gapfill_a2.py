#!/usr/bin/env python3
"""
Run A2 (GAPFILL.md A2, rules locked 8 Nov 2026 09:40 before any run or computation):
  1 completion of the x1000 (n = 3) relaxation by capacity time 20 (ceilN3XL), rule A unchanged;
  2 'paced by the gypsum left': at matched dissolved fraction the n = 3 median network PR_V / start stays within 0.03 of
    the n = 2 median (ceilN2L) from d = 0.5 to the largest d both reach with >= 6 of 9 networks;
  3 bypass: dissolution efficiency E = dd / dt_cap between the common checkpoints (2, 3, 4, 6, 8) and bypass index
    I = flow-weighted / volume-weighted mean remaining gypsum fraction over fractures; supported if n = 3 has lower E and
    lower I than n = 2 on >= 7 of 9 networks (medians over the matched times).
  DYLD_LIBRARY_PATH=/opt/homebrew/Cellar/freetype/2.14.1_1/lib python3 forsmark_reactive/gapfill/analyze_gapfill_a2.py [--bypass-only]
  -> gapA2_bypass_states.csv, gapA2_bypass.csv, gapA2_stretch.csv, gapA2_network.csv, gapA2_paced.csv,
     gapA2_consistency.csv, gapA2_tests.csv
"""
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
FR = HERE.parent
sys.path[:0] = [str(FR / "scale2km"), str(FR), str(FR.parent), str(FR.parent / "physics_upscaling")]
import xbin_channelization as X  # noqa: E402
from analyze_phase1_mechanism import read_vtu  # noqa: E402
from time_axes import clocks  # noqa: E402
from write_corrected_bigrafv_inputs import read_uge  # noqa: E402

NETS = [(p, s) for p in (4.0, 6.0, 8.0) for s in (1, 2, 3)]
TM = [2.0, 3.0, 4.0, 6.0, 8.0]
GRID = np.round(np.arange(0.0, 0.951, 0.01), 2)


def rdir(p, s, tag):
    return X.P1 / f"L2_r15_p{p}_sg1.0_seed{s}" / f"gypsum__uncorrected_graph__{tag}"


def states(run):
    pat = pd.read_csv(run / "patterns.csv")
    c = clocks(run)
    pat["t_cap"] = [float(c.t_cap(t)) for t in pat.t_y]
    return pat


def bypass_one(arg):
    p, s, tag = arg
    run = rdir(p, s, tag)
    pat = states(run).set_index("k")
    nf = len(X.read_polygons(run / "polygons.dat"))
    V = read_uge(run / "full_mesh_vol_area.uge")[0][:nf, 4]
    rows = []
    for f in sorted((X.PV / f"{run.parent.name}__{run.name}").glob("fractures_*.vtu")):
        k = int(f.stem.split("_")[1])
        if k not in pat.index:
            continue
        a = read_vtu(f)
        q = np.abs(a["Q_frac"]).astype(float)
        g = 1 - np.clip(a["fraction_dissolved"].astype(float), 0, 1)
        vw = (V * g).sum() / V.sum()
        rows.append(dict(p32=p, seed=s, tag=tag, k=k, t_cap=pat.loc[k, "t_cap"], dissolved=pat.loc[k, "dissolved"],
                         I=float(((q * g).sum() / q.sum()) / vw) if vw > 0 else np.nan, remaining_vw=float(vw)))
    return rows


def bypass(pool):
    tags = ["ceilN2L", "ceilN3L"] + (["ceilN3XL"] if all((rdir(p, s, "ceilN3XL") / "patterns.csv").exists() for p, s in NETS) else [])
    res = pool.map(bypass_one, [(p, s, t) for p, s in NETS for t in tags])
    B = pd.DataFrame([r for rr in res for r in rr])
    B.to_csv(HERE / "gapA2_bypass_states.csv", index=False)
    out = []
    for (p, s, tag), h in B.groupby(["p32", "seed", "tag"]):
        h = h.sort_values("k")
        idx = [int((h.t_cap - t).abs().idxmin()) for t in TM]
        tc, dd, I = h.loc[idx, "t_cap"].to_numpy(), h.loc[idx, "dissolved"].to_numpy(), h.loc[idx, "I"].to_numpy()
        E = np.diff(dd) / np.diff(tc)
        out.append(dict(p32=p, seed=s, tag=tag, E_median=float(np.median(E)), I_median=float(np.median(I)),
                        t_cap_err=float(np.abs(tc - TM).max()), **{f"E_{TM[i]:g}_{TM[i + 1]:g}": float(E[i]) for i in range(len(E))},
                        **{f"I_{t:g}": float(v) for t, v in zip(TM, I)}))
    S = pd.DataFrame(out)
    S.to_csv(HERE / "gapA2_bypass.csv", index=False)
    a = S[S.tag == "ceilN2L"].set_index(["p32", "seed"])
    b = S[S.tag == "ceilN3L"].set_index(["p32", "seed"])
    lowE, lowI = int((b.E_median < a.E_median).sum()), int((b.I_median < a.I_median).sum())
    return [dict(test="A2_bypass", n2_E_median=float(a.E_median.median()), n3_E_median=float(b.E_median.median()),
                 n2_I_median=float(a.I_median.median()), n3_I_median=float(b.I_median.median()), networks_lower_E=lowE,
                 networks_lower_I=lowI, max_t_cap_err=float(S.t_cap_err.max()), pass_=bool(lowE >= 7 and lowI >= 7))]


def on_grid(d, y):
    d = np.maximum.accumulate(np.asarray(d, float))
    o = np.interp(GRID, d, y, left=np.nan, right=np.nan)
    o[GRID > d.max()] = np.nan
    return o


def stretch_one(p_s):
    return X.one(str(rdir(*p_s, "ceilN3XL")))


def completion(pool):
    res = pool.map(stretch_one, NETS)
    srows, nrows, crows = [], [], []
    for (p, s), rows in zip(NETS, res):
        run = rdir(p, s, "ceilN3XL")
        D = pd.DataFrame(rows)
        for b, h in D.groupby("bin"):
            h = h.sort_values("k")
            y = (h.prv / h.prv.iloc[0]).to_numpy()
            i = int(np.argmin(y))
            srows.append(dict(p32=p, seed=s, bin=b, min_rel=y[i], end_rel=y[-1], d_end=h.dissolved.iloc[-1],
                              recovered=(y[-1] - y[i]) / (1 - y[i]) if y[i] < 1 else np.nan))
        pat = states(run).set_index("k")
        c = pd.read_csv(run / "channelization.csv").sort_values("k")
        y = (c.pr_fracture_vol / c.pr_fracture_vol.iloc[0]).to_numpy()
        i = int(np.argmin(y))
        tc = pat.loc[c.k, "t_cap"].to_numpy()
        first = tc[np.argmax((y >= 0.9) & (np.arange(len(y)) > i))] if np.any((y >= 0.9) & (np.arange(len(y)) > i)) else np.nan
        nrows.append(dict(p32=p, seed=s, prv_min_rel=y[i], prv_end_rel=y[-1], recovered=(y[-1] - y[i]) / (1 - y[i]),
                          d_end=float(c.dissolved.iloc[-1]), t_cap_end=float(tc[-1]), t_cap_first_prv09=float(first),
                          keff_gain_end=float(c.k_eff_ratio.iloc[-1])))
        # consistency with ceilN3L (same deck to capacity time 8)
        L = rdir(p, s, "ceilN3L")
        a = pd.read_csv(L / "channelization.csv")[["t_y", "dissolved", "pr_fracture_vol"]]
        b = c[["t_y", "dissolved", "pr_fracture_vol"]]
        a["tr"], b = a.t_y.round(4), b.assign(tr=b.t_y.round(4))
        m = a.merge(b, on="tr", suffixes=("_L", "_XL"))
        crows.append(dict(p32=p, seed=s, n_matched=len(m), max_abs_d_diss=float((m.dissolved_L - m.dissolved_XL).abs().max()),
                          max_rel_d_prv=float(((m.pr_fracture_vol_L - m.pr_fracture_vol_XL) / m.pr_fracture_vol_L).abs().max())))
    S, N, Cn = pd.DataFrame(srows), pd.DataFrame(nrows), pd.DataFrame(crows)
    S.to_csv(HERE / "gapA2_stretch.csv", index=False)
    N.to_csv(HERE / "gapA2_network.csv", index=False)
    Cn.to_csv(HERE / "gapA2_consistency.csv", index=False)
    med = S.groupby("bin").recovered.median()
    # median network PR_V on a capacity-time grid: first time >= 0.9 after the minimum
    tg = np.linspace(0, 20, 401)
    Y = []
    for p, s in NETS:
        run = rdir(p, s, "ceilN3XL")
        c = pd.read_csv(run / "channelization.csv").sort_values("k")
        cl = clocks(run)
        Y.append(np.interp(tg, [float(cl.t_cap(t)) for t in c.t_y], c.pr_fracture_vol / c.pr_fracture_vol.iloc[0], right=np.nan))
    my = np.nanmedian(Y, 0)
    j0 = int(np.nanargmin(my))
    hit = np.where(my[j0:] >= 0.9)[0]
    t1 = [dict(test="A2_completion", stretch_recovered_min_of_medians=float(med.min()), stretches_ge_09=int((med >= 0.9).sum()),
               network_prv_end_median=float(N.prv_end_rel.median()), networks_prv_ge_09=int((N.prv_end_rel >= 0.9).sum()),
               d_end_median=float(N.d_end.median()), t_cap_end_median=float(N.t_cap_end.median()),
               t_cap_median_curve_reaches_09=float(tg[j0 + hit[0]]) if len(hit) else np.nan,
               pass_=bool(med.min() >= 0.9 and N.prv_end_rel.median() >= 0.9))]
    # paced: n = 3 (ceilN3XL) vs n = 2 (ceilN2L) at matched d
    cur = {}
    for tag in ("ceilN2L", "ceilN3XL"):
        Z = []
        for p, s in NETS:
            c = pd.read_csv(rdir(p, s, tag) / "channelization.csv").sort_values("k")
            Z.append(on_grid(c.dissolved.to_numpy(), (c.pr_fracture_vol / c.pr_fracture_vol.iloc[0]).to_numpy()))
        Z = np.array(Z)
        cur[tag] = (np.nanmedian(Z, 0), np.isfinite(Z).sum(0))
    ok = (GRID >= 0.5) & (cur["ceilN2L"][1] >= 6) & (cur["ceilN3XL"][1] >= 6)
    P = pd.DataFrame(dict(d=GRID, n2=cur["ceilN2L"][0], n3=cur["ceilN3XL"][0], cnt2=cur["ceilN2L"][1], cnt3=cur["ceilN3XL"][1], in_test=ok))
    P["gap"] = P.n3 - P.n2
    P.to_csv(HERE / "gapA2_paced.csv", index=False)
    t2 = [dict(test="A2_paced", d_from=0.5, d_to=float(GRID[ok].max()) if ok.any() else np.nan,
               max_abs_gap=float(P.gap[ok].abs().max()), median_gap=float(P.gap[ok].median()),
               pass_=bool(ok.any() and P.gap[ok].abs().max() <= 0.03))]
    return t1 + t2


def main():
    with Pool(6) as pool:
        T = bypass(pool)
        if "--bypass-only" not in sys.argv:
            T += completion(pool)
    T = pd.DataFrame(T)
    T.to_csv(HERE / ("gapA2_tests_bypass_only.csv" if "--bypass-only" in sys.argv else "gapA2_tests.csv"), index=False)
    pd.set_option("display.width", 250)
    print(T.T.to_string())


if __name__ == "__main__":
    main()
