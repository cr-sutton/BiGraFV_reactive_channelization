#!/usr/bin/env python3
"""
Does each 100 m stretch relax behind the front at high gain? (7 Nov 2026; story items 2-3.)
Per-stretch PR_V (fracture centre bins, as xbin_channelization.py) for the 9 sweep networks at n = 1 (phase1), n = 2
(ceilN2) and n = 3 (ceilN3 / kphi_n3), both chemistries, every saved state of each run.  Per run and stretch: lowest
value / start, dissolved fraction there, last value / start and the recovered share (last - min) / (1 - min).
The n = 1 runs go to large dissolved fractions; the sweep runs stop at capacity time 2.
  DYLD_LIBRARY_PATH=/opt/homebrew/Cellar/freetype/2.14.1_1/lib python3 forsmark_reactive/ceilsweep/xbin_highgain.py
  -> ceilsweep/xbin_highgain.csv
"""
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

FR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FR))
import xbin_channelization as X  # noqa: E402


def runs():
    out = []
    for p in (4.0, 6.0, 8.0):
        for s in (1, 2, 3):
            for tag in ("phase1", "ceilN2", "ceilN3", "kphi_n3"):
                for mdir in ("gypsum", "gypsum_calcite"):
                    r = X.P1 / f"L2_r15_p{p}_sg1.0_seed{s}" / f"{mdir}__uncorrected_graph__{tag}"
                    if (r / "patterns.csv").exists() and (X.PV / f"{r.parent.name}__{r.name}").exists():
                        out.append(str(r))
    return out


def main():
    rr = runs()
    with Pool(4) as pool:
        res = pool.map(X.one, rr)
    rows = []
    for r, rs in zip(rr, res):
        tag = r.split("__")[-1].replace("kphi_n3", "ceilN3")
        for x in rs:
            rows.append({**x, "tag": tag})
    D = pd.DataFrame(rows)
    out = []
    for (mo, tag, p, s, b), h in D.groupby(["mode", "tag", "p32", "seed", "bin"]):
        h = h.sort_values("k")
        y = (h.prv / h.prv.iloc[0]).to_numpy()
        i = int(np.argmin(y))
        out.append(dict(mode=mo, tag=tag, p32=p, seed=s, bin=b, min_rel=y[i], d_min=h.dissolved.iloc[i], end_rel=y[-1],
                        d_end=h.dissolved.iloc[-1], recovered=(y[-1] - y[i]) / (1 - y[i]) if y[i] < 1 else np.nan))
    O = pd.DataFrame(out)
    O.to_csv(FR / "ceilsweep" / "xbin_highgain.csv", index=False)
    pd.set_option("display.width", 220)
    g = O.groupby(["mode", "tag", "bin"])[["min_rel", "end_rel", "recovered", "d_min"]].median().round(2)
    for c in ("min_rel", "end_rel", "recovered", "d_min"):
        print("==", c); print(g[c].unstack("bin").to_string())
    print(O.groupby(["mode", "tag"]).d_end.median().round(2))


if __name__ == "__main__":
    main()
