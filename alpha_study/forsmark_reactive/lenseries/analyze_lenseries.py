#!/usr/bin/env python3
"""
Length-series analysis, written 6 Nov 2026 before any run; the tests are those of LENGTH_SERIES.md and must not change.
Per finished run: flow re-solved at every saved state (scale2km/compare_scale.mech_2km with the outlet window at
x > L/2 - 100), events within capacity time <= 2, early peak = d(PRV_min) < d(outlet5), number of PR_V dips with
prominence >= 0.03 of the start value, depth, inheritance.
  python3 forsmark_reactive/lenseries/analyze_lenseries.py -> lenseries_runs.csv, lenseries_tests.csv
"""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import find_peaks
from scipy.stats import fisher_exact, norm

HERE = Path(__file__).resolve().parent
FR = HERE.parent
sys.path[:0] = [str(FR / "scale2km"), str(FR), str(FR.parent), str(FR.parent / "physics_upscaling")]
from compare_scale import TCAP_MAX, chan, events, mech_2km  # noqa: E402


def trend_test(x, k, n):
    """Cochran-Armitage test for a rising share with score x; one-sided p (H1: share rises with x)."""
    x, k, n = map(np.asarray, (x, k, n))
    N, K = n.sum(), k.sum()
    p = K / N
    if p in (0, 1):
        return np.nan, 1.0
    T = (x * (k - n * p)).sum()
    var = p * (1 - p) * ((n * x ** 2).sum() - (n * x).sum() ** 2 / N)
    z = T / np.sqrt(var)
    return float(z), float(1 - norm.cdf(z))


def main():
    rows = []
    for run in sorted(HERE.glob("L*_r15_p*_sg1.0_seed*/gyp*__phase1")):
        if not ((run / "patterns.csv").exists() and (run / "channelization.csv").exists()):
            continue
        m = re.search(r"L(\d+)_r15_p([\d.]+)_sg[\d.]+_seed(\d+)", str(run))
        L, p32, seed = float(m[1]), float(m[2]), int(m[3])
        g = mech_2km(run, xout=L / 2 - 100.0)
        g = g[g.t_cap <= TCAP_MAX].sort_values("k").reset_index(drop=True)
        ev = events(g)
        y = (g.pr_frac / g.pr_frac.iloc[0]).to_numpy()
        dips = len(find_peaks(-y, prominence=0.03)[0])
        rows.append(dict(L=L, p32=p32, seed=seed, mode=g["mode"].iloc[0], **ev, **chan(run, g),
                         early=bool(ev["PRV_min"] < ev["outlet5"]) if np.isfinite(ev["outlet5"]) else True, n_dips=dips,
                         t_cap_end=float(g.t_cap.max())))
    if not rows:
        print("no finished runs")
        return
    R = pd.DataFrame(rows).sort_values(["mode", "p32", "L", "seed"])
    R.to_csv(HERE / "lenseries_runs.csv", index=False)
    T = []
    for mode, h in R.groupby("mode"):
        c = h.groupby(["p32", "L"]).early.agg(["sum", "size"]).reset_index()
        x4 = c[c.p32 == 4.0]
        z, p = trend_test(np.log2(x4.L / 500.0), x4["sum"], x4["size"]) if len(x4) >= 2 else (np.nan, np.nan)
        a = c[(c.p32 == 4.0) & (c.L == 2000)]
        b = c[(c.p32 == 8.0) & (c.L == 2000)]
        if len(a) and len(b):
            fp = fisher_exact([[int(a["sum"].iloc[0]), int(a["size"].iloc[0] - a["sum"].iloc[0])],
                               [int(b["sum"].iloc[0]), int(b["size"].iloc[0] - b["sum"].iloc[0])]], alternative="greater").pvalue
        else:
            fp = np.nan
        T.append(dict(mode=mode, test1_trend_z=z, test1_p=p, test1_pass=bool(p < 0.05) if np.isfinite(p) else None,
                      test2_fisher_p=fp, test2_pass=bool(fp < 0.05) if np.isfinite(fp) else None,
                      counts="; ".join(f"x{r.p32:g} L{r.L:g}: {r['sum']}/{r['size']}" for _, r in c.iterrows()),
                      complete=bool(len(c) == 6 and (c["size"] == 6).all())))
    T = pd.DataFrame(T)
    T.to_csv(HERE / "lenseries_tests.csv", index=False)
    pd.set_option("display.width", 250)
    print(R.round(3).to_string(index=False))
    print(T.to_string(index=False))


if __name__ == "__main__":
    main()
