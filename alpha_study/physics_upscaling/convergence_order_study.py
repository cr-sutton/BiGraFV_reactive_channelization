"""Convergence order of the per-half geometric factors (no DFN information).

For each network, the multiport solve is repeated at several raster levels
(cells across a fracture, sub-ports per intersection), both halved together:
    LEVELS = (32,3), (64,6), (128,12), (256,24)
At each level we record the flow-conditioned half factors g and the corrected
BiGraFV flow Q_star (star graph with those factors).  Each level is cached as
a pickle so later extrapolation schemes can be re-applied without re-solving.

The observed order from three successive levels a, b, c is
    p = log2( (Q_a - Q_b) / (Q_b - Q_c) )
and a generalized Richardson limit from the last two levels is
    X_inf = X_c + (X_c - X_b) / (2**p - 1).
"""
from __future__ import annotations

import json
import pickle
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from local_global_transmissibility import bigrafv_edges, solve_graph  # noqa: E402
from multiport_upscaling import assemble_and_solve, build_ports  # noqa: E402
from star_case import load, star_edges  # noqa: E402
from star_geometry import flow_conditioned_half_factors  # noqa: E402

CACHE = Path(__file__).resolve().parent / "g_cache"
ALL_LEVELS = ((32, 3), (64, 6), (128, 12), (256, 24))


def fill_bad(g, bad):
    """Unrepresentable halves get the median factor of the fracture's good halves."""
    out = dict(g)
    per = {}
    for (f, k), v in g.items():
        per.setdefault(f, []).append(v)
    med = float(np.median(list(g.values())))
    for (f, k) in bad:
        out[(f, k)] = float(np.median(per[f])) if f in per else med
    return out


def cache_path(study, level):
    key = str(Path(study).resolve()).split("alpha_study/")[-1].replace("/", "__")
    return CACHE / f"{key}__n{level[0]}_s{level[1]}.pkl"


def level_solution(study, F, I, E, level):
    """Half factors + Q's at one level (cached)."""
    p = cache_path(study, level)
    if p.exists():
        return pickle.loads(p.read_bytes())
    nc, ns = level
    q_mp, det = assemble_and_solve(F, build_ports(F, I, n_sub=ns), ncell=nc, return_details=True)
    g, bad = flow_conditioned_half_factors(F, det)
    Q_star, _ = solve_graph(star_edges(E, F, fill_bad(g, bad)), "G_star")
    rec = dict(level=level, q_mp=q_mp, Q_star=Q_star, g=g, bad=bad)
    CACHE.mkdir(exist_ok=True)
    p.write_bytes(pickle.dumps(rec))
    return rec


def run(study, levels=ALL_LEVELS):
    study = Path(study)
    F, I = load(study)
    E = bigrafv_edges(study)
    Qg, _ = solve_graph(E, "G_graph")
    recs = [level_solution(study, F, I, E, lv) for lv in levels]
    a_star = json.loads((study / "flow_targets.json").read_text())["alpha_q_ratio"]
    out = dict(study=str(study), alpha_star=a_star, Qg=Qg,
               **{f"alpha_star_graph_n{r['level'][0]}": r["Q_star"] / Qg for r in recs},
               **{f"alpha_mp_n{r['level'][0]}": r["q_mp"] / Qg for r in recs})
    return out


if __name__ == "__main__":
    lv = ALL_LEVELS if "--fine" in sys.argv else ALL_LEVELS[:3]
    for s in [a for a in sys.argv[1:] if not a.startswith("--")]:
        print(json.dumps(run(s, lv)), flush=True)
