#!/usr/bin/env python3
"""
Gap-filling runs A, B, C (7-8 Nov 2026) scored against the rules locked in GAPFILL.md before any run.

A  Late-time relaxation at high gain: ceilN2L / ceilN3L (n = 2, 3, to capacity time 8) on the 9 sigma-1 sweep networks.
   Per run and 100 m stretch (xbin_channelization.one): lowest PR_V / start, last / start, recovered share
   (last - min) / (1 - min); network PR_V (channelization.csv pr_fracture_vol) last / start.  Consistency: up to capacity
   time 2 the L runs must reproduce ceilN2 / ceilN3 (same states, same dissolved fraction and PR_V).
B  Blind test of the frozen t10 line on 12 new 1 km networks (lenseries/L1000, P32 x4/x8, seeds 11-16): t10 / tau from
   snap_0 (early_arrival_predictor.arrivals), breakthrough from compare_scale.mech_2km (xout = 400 m, capacity time <= 2).
C  Depth against attainable gain C on the 9 sigma-0 networks: phase1 (n = 1), ceilN148, ceilN2, ceilN3, both chemistries.
   As R1 / R2 of ceilsweep/CEILING_SWEEP.md.
  DYLD_LIBRARY_PATH=/opt/homebrew/Cellar/freetype/2.14.1_1/lib python3 forsmark_reactive/gapfill/analyze_gapfill.py
  -> gapfill/gapA_stretch.csv, gapA_network.csv, gapA_consistency.csv, gapB_predictor.csv, gapC_runs.csv,
     gapC_residuals.csv, gapfill_tests.csv
"""
import re
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
FR = HERE.parent
sys.path[:0] = [str(FR / "scale2km"), str(FR), str(FR.parent), str(FR.parent / "physics_upscaling")]
import xbin_channelization as X  # noqa: E402
from compare_scale import TCAP_MAX, chan, events, mech_2km  # noqa: E402
from early_arrival_predictor import arrivals  # noqa: E402
from time_axes import clocks  # noqa: E402

GAMMA = 0.494
NETS = [(p, s) for p in (4.0, 6.0, 8.0) for s in (1, 2, 3)]
MD = {"gyponly": "gypsum", "gypcal": "gypsum_calcite"}
FROZEN = {"gyponly": (0.0292, 1.4483), "gypcal": (0.1113, 1.4924)}   # d_bt = a + b * t10/tau (GAPFILL.md)


def ceiling(mode, n, phi0=0.1):
    phi_end = 1.0 if mode == "gyponly" else 1 - (1 - phi0) * GAMMA
    return (phi_end / phi0) ** n


def tcap_states(run):
    pat = pd.read_csv(run / "patterns.csv")
    c = clocks(run)
    pat["t_cap"] = [float(c.t_cap(t)) for t in pat.t_y]
    return pat


# ---------------------------------------------------------------- A
def runA():
    out = []
    for p, s in NETS:
        for n, tag in ((2, "ceilN2L"), (3, "ceilN3L")):
            for mode in MD:
                out.append((str(X.P1 / f"L2_r15_p{p}_sg1.0_seed{s}" / f"{MD[mode]}__uncorrected_graph__{tag}"), p, s, n, mode))
    return out


def stretchA(arg):
    return X.one(arg[0])


def analyzeA(pool):
    jobs = runA()
    res = pool.map(stretchA, jobs)
    srows, nrows, crows = [], [], []
    for (r, p, s, n, mode), rows in zip(jobs, res):
        r = Path(r)
        pat = tcap_states(r).set_index("k")
        D = pd.DataFrame(rows)
        for b, h in D.groupby("bin"):
            h = h.sort_values("k")
            y = (h.prv / h.prv.iloc[0]).to_numpy()
            i = int(np.argmin(y))
            srows.append(dict(mode=mode, n=n, p32=p, seed=s, bin=b, min_rel=y[i], d_min=h.dissolved.iloc[i], end_rel=y[-1],
                              d_end=h.dissolved.iloc[-1], recovered=(y[-1] - y[i]) / (1 - y[i]) if y[i] < 1 else np.nan))
        c = pd.read_csv(r / "channelization.csv").sort_values("k")
        y = (c.pr_fracture_vol / c.pr_fracture_vol.iloc[0]).to_numpy()
        i = int(np.argmin(y))
        kk = c.k.to_numpy()
        nrows.append(dict(mode=mode, n=n, p32=p, seed=s, prv_min_rel=y[i], d_at_min=float(pat.loc[kk[i], "dissolved"]),
                          prv_end_rel=y[-1], recovered=(y[-1] - y[i]) / (1 - y[i]), d_end=float(pat.loc[kk[-1], "dissolved"]),
                          t_cap_end=float(pat.loc[kk[-1], "t_cap"]), keff_gain_end=float(c.k_eff_ratio.iloc[-1])))
        # consistency with the capacity-time-2 run of the same law
        ref = r.parent / r.name[:-1]
        if ref.name.endswith("ceilN3") and not (ref / "patterns.csv").exists():
            ref = r.parent / r.name.replace("ceilN3L", "kphi_n3")
        if (ref / "patterns.csv").exists():
            a = tcap_states(ref)
            a = a[a.t_cap <= TCAP_MAX + 1e-9]
            cr = pd.read_csv(ref / "channelization.csv")[["k", "pr_fracture_vol"]]
            a = a.merge(cr, on="k").sort_values("k").reset_index(drop=True)
            b = pat.reset_index().merge(c[["k", "pr_fracture_vol"]], on="k").sort_values("k").reset_index(drop=True)
            a["tr"], b["tr"] = a.t_y.round(6), b.t_y.round(6)
            m = a.merge(b, on="tr", suffixes=("_ref", "_L"))
            crows.append(dict(mode=mode, n=n, p32=p, seed=s, ref=ref.name.split("__")[-1], n_ref=len(a), n_matched=len(m),
                              max_abs_d_diss=float((m.dissolved_ref - m.dissolved_L).abs().max()),
                              max_rel_d_prv=float(((m.pr_fracture_vol_ref - m.pr_fracture_vol_L) / m.pr_fracture_vol_ref).abs().max()),
                              depth_ref=float(a.pr_fracture_vol.min() / a.pr_fracture_vol.iloc[0]),
                              depth_L=float(b.pr_fracture_vol[b.t_cap <= TCAP_MAX + 1e-9].min() / b.pr_fracture_vol.iloc[0])))
    S, N, Cn = pd.DataFrame(srows), pd.DataFrame(nrows), pd.DataFrame(crows)
    S.to_csv(HERE / "gapA_stretch.csv", index=False)
    N.to_csv(HERE / "gapA_network.csv", index=False)
    Cn.to_csv(HERE / "gapA_consistency.csv", index=False)
    tests = []
    for (mode, n), h in S.groupby(["mode", "n"]):
        med = h.groupby("bin").recovered.median()
        nn = N[(N["mode"] == mode) & (N.n == n)]
        tests.append(dict(test="A", mode=mode, n=n, stretch_recovered_min_of_medians=float(med.min()),
                          stretches_ge_09=int((med >= 0.9).sum()), stretches=int(med.notna().sum()),
                          network_prv_end_median=float(nn.prv_end_rel.median()), networks_prv_ge_09=int((nn.prv_end_rel >= 0.9).sum()),
                          network_recovered_median=float(nn.recovered.median()), d_end_median=float(nn.d_end.median()),
                          t_cap_end_median=float(nn.t_cap_end.median()),
                          pass_=bool(med.min() >= 0.9 and nn.prv_end_rel.median() >= 0.9)))
    return tests


# ---------------------------------------------------------------- B
def runB():
    return sorted(str(r) for r in (FR / "lenseries").glob("L1000_r15_p*_sg1.0_seed*/gyp*__phase1"))


def oneB(r):
    r = Path(r)
    m = re.search(r"p([\d.]+)_sg([\d.]+)_seed(\d+)", str(r))
    g = mech_2km(r, xout=400.0)
    g = g[g.t_cap <= TCAP_MAX].sort_values("k").reset_index(drop=True)
    mode = "gypcal" if "calcite" in r.name else "gyponly"
    return dict(mode=mode, p32=float(m[1]), sigma=float(m[2]), seed=int(m[3]), t_cap_end=float(g.t_cap.max()),
                **events(g), **chan(r, g), **arrivals(r / "snap_0"))


def analyzeB(pool):
    B = pd.DataFrame(pool.map(oneB, runB()))
    B["d_bt_pred"] = [FROZEN[mo][0] + FROZEN[mo][1] * x for mo, x in zip(B["mode"], B.t10)]
    B.to_csv(HERE / "gapB_predictor.csv", index=False)
    tests = []
    for mo, h in B.groupby("mode"):
        h = h.dropna(subset=["breakthrough"])
        res = h.breakthrough - h.d_bt_pred
        r2 = 1 - (res ** 2).sum() / ((h.breakthrough - h.breakthrough.mean()) ** 2).sum()
        rho = spearmanr(h.t10, h.breakthrough).statistic
        bias = float(res.median())
        tests.append(dict(test="B", mode=mo, n_runs=int((B["mode"] == mo).sum()), n_breakthrough=len(h), r2=float(r2), rho=float(rho),
                          median_bias=bias, median_abs_err=float(res.abs().median()),
                          d_bt_range=f"{h.breakthrough.min():.3f}-{h.breakthrough.max():.3f}",
                          t10_range=f"{h.t10.min():.3f}-{h.t10.max():.3f}",
                          pass_=bool(r2 >= 0.5 and rho >= 0.7 and abs(bias) <= 0.03)))
    return tests


# ---------------------------------------------------------------- C
LAWS_C = [("phase1", 1.0), ("ceilN148", 1.4771), ("ceilN2", 2.0), ("ceilN3", 3.0)]


def runC():
    out = []
    for p, s in NETS:
        for tag, n in LAWS_C:
            for mode in MD:
                r = FR / "phase1" / f"L2_r15_p{p}_sg0.0_seed{s}" / f"{MD[mode]}__uncorrected_graph__{tag}"
                if (r / "patterns.csv").exists() and (r / "channelization.csv").exists():
                    out.append((str(r), p, s, tag, n, mode))
    return out


def oneC(arg):
    r, p, s, tag, n, mode = arg
    r = Path(r)
    g = mech_2km(r, xout=400.0)
    g = g[g.t_cap <= TCAP_MAX].sort_values("k").reset_index(drop=True)
    c = pd.read_csv(r / "channelization.csv")
    c = c[c.k.isin(g.k)].sort_values("k")
    return dict(p32=p, seed=s, mode=mode, tag=tag, n=n, C=ceiling(mode, n), **events(g), **chan(r, g),
                keff_gain_end=float(c.k_eff_ratio.iloc[-1]), t_cap_end=float(g.t_cap.max()))


def analyzeC(pool):
    R = pd.DataFrame(pool.map(oneC, runC()))
    R.to_csv(HERE / "gapC_runs.csv", index=False)
    rho, mono = [], 0
    for (p, s), h in R[R["mode"] == "gyponly"].groupby(["p32", "seed"]):
        h = h.sort_values("C")
        if len(h) >= 3:
            rho.append(spearmanr(np.log10(h.C), h.depth).statistic)
            mono += bool(np.all(np.diff(h.depth.to_numpy()) < 0))
    res = []
    for (p, s), h in R.groupby(["p32", "seed"]):
        gy = h[h["mode"] == "gyponly"].sort_values("C")
        for _, r in h[h["mode"] == "gypcal"].iterrows():
            if len(gy) >= 2 and gy.C.min() <= r.C <= gy.C.max():
                ref = np.interp(np.log10(r.C), np.log10(gy.C), gy.depth)
                res.append(dict(p32=p, seed=s, tag=r.tag, C=r.C, depth_cal=r.depth, depth_gyp_interp=ref, residual=r.depth - ref))
    res = pd.DataFrame(res)
    res.to_csv(HERE / "gapC_residuals.csv", index=False)
    med = R.groupby(["mode", "tag"]).agg(C=("C", "first"), depth=("depth", "median"), bt=("breakthrough", "median"),
                                         prv_min=("PRV_min", "median"), n_runs=("depth", "size"))
    print(med.round(3).to_string())
    return [dict(test="C", mode="gyponly", networks=len(rho), networks_falling=mono, rho_minus1=int(sum(np.isclose(r, -1) for r in rho)),
                 pass_=bool(mono >= 7)),
            dict(test="C", mode="gypcal_vs_gyponly", n_points=len(res), median_abs_residual=float(res.residual.abs().median()),
                 median_residual=float(res.residual.median()),
                 pass_=bool(res.residual.abs().median() <= 0.03 and abs(res.residual.median()) <= 0.03))]


def main():
    with Pool(6) as pool:
        T = analyzeB(pool) + analyzeC(pool) + analyzeA(pool)
    T = pd.DataFrame(T)
    T.to_csv(HERE / "gapfill_tests.csv", index=False)
    pd.set_option("display.width", 250)
    print(T.T.to_string())


if __name__ == "__main__":
    main()
