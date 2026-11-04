import sys
from pathlib import Path
import numpy as np, pandas as pd
from dfn_geometry import build_fractures, intersection_segments, read_domain
from multiport_upscaling import build_ports, assemble_and_solve

P_IN, P_OUT = 2.0e6, 1.0e6


def recentered_segments(st, F, ints=None):
    if ints is None:
        ints = pd.read_csv(st / "intersections.csv.gz")
    I = intersection_segments(st, F, ints)
    mid = ints.set_index(ints.intersection_id.astype(str))[["x", "y", "z"]]
    xa, xb = [], []
    for _, r in I.iterrows():
        a, b = np.asarray(r.xa), np.asarray(r.xb)
        d = (b - a) / max(np.linalg.norm(b - a), 1e-12)
        m = mid.loc[r.intersection_id].to_numpy(float)
        xa.append(m - 0.5 * r.length_arch * d); xb.append(m + 0.5 * r.length_arch * d)
    I["xa"], I["xb"] = xa, xb
    return I


def multiport_solution(st, ncell=96, n_sub=8):
    dom, shape = read_domain(st)
    F = build_fractures(st, dom, shape="rect" if shape == "rect" else "ell", nvert=4 if shape == "rect" else 8)
    I = recentered_segments(st, F)
    q, det = assemble_and_solve(F, build_ports(F, I, n_sub=n_sub), ncell=ncell, return_details=True)
    return F, I, q, det


if __name__ == "__main__":
    for s in sys.argv[1:]:
        st = Path(s)
        F, I, q, det = multiport_solution(st)
        mp = pd.read_csv(st / "matched_pressures_uncorrected.csv.gz")
        mp["p_mp"] = mp.fracture_id.map(lambda f: P_OUT + (P_IN - P_OUT) * det["pbar"].get(f, np.nan))
        ok = mp.p_mp.notna()
        e_g = (mp.pressure_graph - mp.pressure_fullDFN)[ok]
        e_m = (mp.p_mp - mp.pressure_fullDFN)[ok]
        print(st.parts[-3], st.parts[-2], "n=%d  RMSE graph %.1f kPa   RMSE multiport %.1f kPa  corr_mp %.5f" % (
            ok.sum(), np.sqrt(np.mean(e_g**2)) / 1e3, np.sqrt(np.mean(e_m**2)) / 1e3,
            np.corrcoef(mp.p_mp[ok], mp.pressure_fullDFN[ok])[0, 1]))
