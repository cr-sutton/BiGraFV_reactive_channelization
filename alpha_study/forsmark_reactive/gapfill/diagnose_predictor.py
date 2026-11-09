#!/usr/bin/env python3
"""
Why did the t10 predictor miss on the blind 1 km networks (run B), and why does it rank 2 km weakly?  (8 Nov 2026)
Exploratory: run after the blind result was known; candidate explanations listed before computing:
  1  measurement: breakthrough is read at the first saved state with outlet_diss >= 0.5, so it carries the state spacing.
     Compare the state spacing in d at breakthrough between sets, and redo everything with d_bt interpolated linearly in
     outlet_diss between the bracketing states.
  2  probe: tracer recovery and t10 spread by set.
  3  structure: pre-run network statistics (network_stats.json) by set; residual against the frozen line vs each
     statistic on all 27 sigma-1 1 km networks (Spearman, Bonferroni over the statistics tested).
  4  luck: random 15 / 12 splits of the 27 sigma-1 1 km networks (fit on 15, test on 12): where do the blind R^2 and bias fall?
  5  2 km: expected R^2 from the 1 km residual scatter and the 2 km t10 spread (attenuation by a narrower spread).
Inputs: phase1/phase1_mechanism.csv, scale2km/scale_mechanism.csv, lenseries/L1000_*/gyp*__phase1/scale_mechanism_run.csv,
phase1/early_arrival_predictor.csv, gapfill/gapB_predictor.csv, */network_stats.json.
  python3 forsmark_reactive/gapfill/diagnose_predictor.py
  -> gapfill/diag_runs.csv, diag_sets.csv, diag_structure.csv, diag_splits.csv, diag_summary.json
"""
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, spearmanr

HERE = Path(__file__).resolve().parent
FR = HERE.parent
TCAP = 2.0
FROZEN = {"gyponly": (0.0292, 1.4483), "gypcal": (0.1113, 1.4924)}
STATS = ["n_fractures", "mean_degree", "n_inlet_fractures", "n_outlet_fractures", "node_disjoint_paths",
         "edge_disjoint_paths", "backbone_fraction", "dead_end_share"]


def bt(g):
    """First-state and interpolated breakthrough from per-state outlet_diss (capacity time <= 2, as compare_scale)."""
    g = g[g.t_cap <= TCAP].sort_values("k").reset_index(drop=True)
    i = g.index[g.outlet_diss >= 0.5]
    if not len(i):
        return dict(d_bt_step=np.nan, d_bt_interp=np.nan, dd_step=np.nan, n_states=len(g))
    i = int(i[0])
    if i == 0:
        return dict(d_bt_step=g.dissolved[0], d_bt_interp=g.dissolved[0], dd_step=0.0, n_states=len(g))
    o0, o1, d0, d1 = g.outlet_diss[i - 1], g.outlet_diss[i], g.dissolved[i - 1], g.dissolved[i]
    return dict(d_bt_step=d1, d_bt_interp=d0 + (0.5 - o0) / (o1 - o0) * (d1 - d0), dd_step=d1 - d0, n_states=len(g))


def netstats(path):
    j = json.loads(Path(path).read_text())
    j["dead_end_share"] = j["n_dead_end_fractures"] / j["n_fractures"]
    return {k: j[k] for k in STATS}


def collect():
    rows = []
    M = pd.read_csv(FR / "phase1" / "phase1_mechanism.csv")
    M = M[(M.tag == "phase1") & M.p32.isin([4.0, 6.0, 8.0])]
    for (mo, p, sg, s), g in M.groupby(["mode", "p32", "sigma", "seed"]):
        rows.append(dict(set="train1km", mode=mo, p32=p, sigma=sg, seed=int(s), **bt(g),
                         **netstats(FR / "phase1" / f"L2_r15_p{p}_sg{sg}_seed{int(s)}" / "network_stats.json")))
    S = pd.read_csv(FR / "scale2km" / "scale_mechanism.csv")
    for (mo, p, sg, s), g in S.groupby(["mode", "p32", "sigma", "seed"]):
        rows.append(dict(set="2km", mode=mo, p32=p, sigma=sg, seed=int(s), **bt(g),
                         **netstats(FR / "scale2km" / f"L2_r15_p{p}_sg{sg}_seed{int(s)}" / "network_stats.json")))
    for r in sorted((FR / "lenseries").glob("L1000_r15_p*_sg1.0_seed*/gyp*__phase1")):
        m = re.search(r"p([\d.]+)_sg([\d.]+)_seed(\d+)", str(r))
        g = pd.read_csv(r / "scale_mechanism_run.csv")
        rows.append(dict(set="blind1km", mode="gypcal" if "calcite" in r.name else "gyponly", p32=float(m[1]), sigma=float(m[2]),
                         seed=int(m[3]), **bt(g), **netstats(r.parent / "network_stats.json")))
    D = pd.DataFrame(rows)
    A = pd.read_csv(FR / "phase1" / "early_arrival_predictor.csv").rename(columns={"scale": "set"})
    A["set"] = A["set"].map({"1km": "train1km", "2km": "2km"})
    B = pd.read_csv(HERE / "gapB_predictor.csv").assign(set="blind1km")
    T = pd.concat([A[["set", "mode", "p32", "sigma", "seed", "t10", "t16", "recovery", "d_bt"]],
                   B[["set", "mode", "p32", "sigma", "seed", "t10", "t16", "recovery", "breakthrough"]].rename(columns={"breakthrough": "d_bt"})])
    D = D.merge(T, on=["set", "mode", "p32", "sigma", "seed"], how="inner")
    D["pred"] = [FROZEN[mo][0] + FROZEN[mo][1] * x for mo, x in zip(D["mode"], D.t10)]
    D["res_step"] = D.d_bt_step - D.pred
    return D


def r2(y, p):
    return float(1 - ((y - p) ** 2).sum() / ((y - y.mean()) ** 2).sum())


def main():
    D = collect()
    D.to_csv(HERE / "diag_runs.csv", index=False)
    out = {"check_dbt_matches_events": float((D.d_bt_step - D.d_bt).abs().max())}
    # 1-2: sets
    sets = []
    for (st, mo), h in D.groupby(["set", "mode"]):
        h1 = h if st != "train1km" else h[h.sigma == 1.0]
        sets.append(dict(set=st, mode=mo, n=len(h1), dd_step_median=h1.dd_step.median(), dd_step_max=h1.dd_step.max(),
                         n_states_median=h1.n_states.median(), interp_minus_step_median=(h1.d_bt_interp - h1.d_bt_step).median(),
                         recovery_median=h1.recovery.median(), t10_sd=h1.t10.std(), dbt_sd=h1.d_bt_step.std(),
                         t10_median=h1.t10.median(), dbt_median=h1.d_bt_step.median()))
    S = pd.DataFrame(sets)
    S.to_csv(HERE / "diag_sets.csv", index=False)
    # interpolated breakthrough: refit on training (all sigma, as the frozen line), score blind and 2 km
    for mo in ("gyponly", "gypcal"):
        tr = D[(D.set == "train1km") & (D["mode"] == mo)]
        b, a = np.polyfit(tr.t10, tr.d_bt_interp, 1)
        for st in ("blind1km", "2km"):
            h = D[(D.set == st) & (D["mode"] == mo)]
            p = a + b * h.t10
            out[f"interp_{mo}_{st}"] = dict(r2=r2(h.d_bt_interp, p), rho=float(spearmanr(h.t10, h.d_bt_interp).statistic),
                                            bias=float((h.d_bt_interp - p).median()), line=[float(a), float(b)])
    # 3: structure (27 sigma-1 1 km networks, both chemistries share geometry: use gyponly residuals and coupled separately)
    P = D[(D.set.isin(["train1km", "blind1km"])) & (D.sigma == 1.0)]
    srows = []
    for mo in ("gyponly", "gypcal"):
        h = P[P["mode"] == mo]
        for k in STATS:
            rr = spearmanr(h[k], h.res_step)
            a_, b_ = h[h.set == "train1km"][k], h[h.set == "blind1km"][k]
            srows.append(dict(mode=mo, stat=k, rho_res=rr.statistic, p=rr.pvalue, p_bonf=min(1, rr.pvalue * len(STATS)),
                              train_median=a_.median(), blind_median=b_.median(), p_mw_train_vs_blind=mannwhitneyu(a_, b_).pvalue))
    St = pd.DataFrame(srows)
    St.to_csv(HERE / "diag_structure.csv", index=False)
    # residual shift blind vs sigma-1 training
    for mo in ("gyponly", "gypcal"):
        h = P[P["mode"] == mo]
        a_, b_ = h[h.set == "train1km"].res_step, h[h.set == "blind1km"].res_step
        out[f"res_shift_{mo}"] = dict(train_median=float(a_.median()), blind_median=float(b_.median()), p_mw=float(mannwhitneyu(a_, b_).pvalue))
    # 4: luck: random 15/12 splits of the 27 sigma-1 networks
    rng = np.random.default_rng(20261108)
    sp = []
    for mo in ("gyponly", "gypcal"):
        h = P[P["mode"] == mo].reset_index(drop=True)
        x, y = h.t10.to_numpy(), h.d_bt_step.to_numpy()
        for it in range(20000):
            idx = rng.permutation(len(h))
            tr, te = idx[:15], idx[15:]
            b, a = np.polyfit(x[tr], y[tr], 1)
            p = a + b * x[te]
            sp.append(dict(mode=mo, r2=r2(y[te], p), bias=float(np.median(y[te] - p)),
                           rho=float(spearmanr(x[te], y[te]).statistic)))
        tr = h.index[h.set == "train1km"]
        te = h.index[h.set == "blind1km"]
        b, a = np.polyfit(x[tr], y[tr], 1)
        p = a + b * x[te]
        obs = dict(r2=r2(y[te], p), bias=float(np.median(y[te] - p)), rho=float(spearmanr(x[te], y[te]).statistic))
        spm = pd.DataFrame([s for s in sp if s["mode"] == mo])
        out[f"splits_{mo}"] = dict(observed_sigma1_fit=obs, frac_r2_le_obs=float((spm.r2 <= obs["r2"]).mean()),
                                   frac_abs_bias_ge_obs=float((spm.bias.abs() >= abs(obs["bias"])).mean()),
                                   frac_rho_le_obs=float((spm.rho <= obs["rho"]).mean()),
                                   r2_median=float(spm.r2.median()), r2_q10=float(spm.r2.quantile(0.1)),
                                   r2_q90=float(spm.r2.quantile(0.9)), frac_r2_below_05=float((spm.r2 < 0.5).mean()))
    pd.DataFrame(sp).to_csv(HERE / "diag_splits.csv", index=False)
    # 5: 2 km attenuation: expected R^2 if the 1 km line and residual scatter held, given the 2 km t10 spread
    for mo in ("gyponly", "gypcal"):
        tr = D[(D.set == "train1km") & (D["mode"] == mo)]
        k2 = D[(D.set == "2km") & (D["mode"] == mo)]
        b, a = np.polyfit(tr.t10, tr.d_bt_step, 1)
        s_res = float((tr.d_bt_step - (a + b * tr.t10)).std(ddof=2))
        sig = (b * k2.t10.std()) ** 2
        b2, a2 = np.polyfit(k2.t10, k2.d_bt_step, 1)
        out[f"atten_{mo}"] = dict(res_sd_1km=s_res, t10_sd_1km=float(tr.t10.std()), t10_sd_2km=float(k2.t10.std()),
                                  expected_r2_2km=float(sig / (sig + s_res ** 2)), observed_r2_2km=r2(k2.d_bt_step, a + b * k2.t10),
                                  slope_1km=float(b), slope_2km_own_fit=float(b2), res_sd_2km_own_fit=float((k2.d_bt_step - (a2 + b2 * k2.t10)).std(ddof=2)),
                                  dd_step_2km_median=float(k2.dd_step.median()))
    (HERE / "diag_summary.json").write_text(json.dumps(out, indent=1))
    pd.set_option("display.width", 250)
    print(S.round(3).to_string())
    print(St.round(3).to_string())
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
