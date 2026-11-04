"""Evaluate the geometric-star BiGraFV (per-half factors) against the DFN."""

from __future__ import annotations

import json
from collections import defaultdict
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from dfn_geometry import build_fractures, read_domain  # noqa: E402
from local_global_transmissibility import bigrafv_edges, solve_graph  # noqa: E402
from mp_pressure_check import recentered_segments  # noqa: E402
from star_geometry import fracture_half_factors, richardson  # noqa: E402

LEVELS = ((64, 6), (128, 12))


def load(study):
    dom, shape = read_domain(study)
    F = build_fractures(study, dom, shape="rect" if shape == "rect" else "ell", nvert=4 if shape == "rect" else 8)
    return F, recentered_segments(study, F)


def star_edges(E, F, g):
    """Replace BiGraFV conductances by series geometric half-conductances.

    Fractures with a single port have no steady DtN; their connection keeps
    the BiGraFV value (it carries no steady flux).
    """
    out = E.copy()
    G = []
    kept = []
    for iid, u, v, g0 in zip(E.intersection_id, E.u, E.v, E.G_graph):
        if isinstance(v, str):
            gu = g.get((u, v))
            G.append(F[u].transmissivity * gu if gu else g0)
            kept.append(gu is None)
            continue
        gu, gv = g.get((u, iid)), g.get((v, iid))
        if gu and gv:
            G.append(1.0 / (1.0 / (F[u].transmissivity * gu) + 1.0 / (F[v].transmissivity * gv)))
            kept.append(False)
        else:
            G.append(g0)
            kept.append(True)
    out["G_star"] = G
    out["kept_bigrafv"] = kept
    return out


def run(study, method="frob"):
    study = Path(study)
    t0 = time.time()
    F, I = load(study)
    E = bigrafv_edges(study)
    Qg, Pg = solve_graph(E, "G_graph")
    gs = [fracture_half_factors(F, I, nc, ns, method=method) for nc, ns in LEVELS]
    g_inf = richardson(gs[1], gs[0])
    ft = json.loads((study / "flow_targets.json").read_text())
    row = dict(study=str(study), alpha_star=float(ft["alpha_q_ratio"]), sigma_input=ft.get("aperture_sigma_input"),
               method=method)
    for name, g in (("fine", gs[1]), ("inf", g_inf)):
        Es = star_edges(E, F, g)
        Q, P = solve_graph(Es, "G_star")
        row[f"alpha_{name}"] = Q / Qg
        mp = study / "matched_pressures_uncorrected.csv.gz"
        if mp.exists():
            m = pd.read_csv(mp)
            p = m.fracture_id.map(lambda f: 1e6 + 1e6 * P.get(f, np.nan))
            row[f"prmse_{name}_kpa"] = float(np.sqrt(np.nanmean((p - m.pressure_fullDFN) ** 2)) / 1e3)
            row["prmse_raw_kpa"] = float(np.sqrt(np.mean((m.pressure_graph - m.pressure_fullDFN) ** 2)) / 1e3)
        row["frac_kept_bigrafv"] = float(Es.kept_bigrafv.mean())
    row["seconds"] = time.time() - t0
    return row


if __name__ == "__main__":
    method = next((a[2:] for a in sys.argv[1:] if a.startswith("--")), "frob")
    for s in [a for a in sys.argv[1:] if not a.startswith("--")]:
        print(json.dumps(run(s, method=method)), flush=True)


def run_flow_conditioned(study, fallback="fracture_median"):
    """Flow-conditioned per-half factors at two levels + Richardson."""
    from mp_pressure_check import multiport_solution
    from star_geometry import flow_conditioned_half_factors

    study = Path(study)
    t0 = time.time()
    E = bigrafv_edges(study)
    Qg, _ = solve_graph(E, "G_graph")
    gs, bads, Fs = [], [], None
    for nc, ns in LEVELS:
        F, I, q, det = multiport_solution(study, ncell=nc, n_sub=ns)
        g, bad = flow_conditioned_half_factors(F, det)
        gs.append(g); bads.append(bad); Fs = F
    g_inf = richardson(gs[1], gs[0])
    # fallback for halves that a positive TPFA half cannot represent:
    # the median geometric factor of the fracture's well-posed halves
    def fill(g):
        out = dict(g)
        per = defaultdict(list)
        for (f, k), v in g.items():
            per[f].append(v)
        allmed = float(np.median(list(g.values())))
        for (f, k) in bads[1]:
            out[(f, k)] = float(np.median(per[f])) if per.get(f) else allmed
        return out
    ft = json.loads((study / "flow_targets.json").read_text())
    row = dict(study=str(study), alpha_star=float(ft["alpha_q_ratio"]),
               n_half=len(gs[1]) + len(bads[1]),
               frac_bad=len(bads[1]) / max(len(gs[1]) + len(bads[1]), 1),
               frac_deadend=sum(v == "deadend" for v in bads[1].values()) / max(len(gs[1]) + len(bads[1]), 1))
    for name, g in (("fine", fill(gs[1])), ("inf", fill(g_inf))):
        Es = star_edges(E, Fs, g)
        Qs, P = solve_graph(Es, "G_star")
        row[f"alpha_{name}"] = Qs / Qg
        mp = study / "matched_pressures_uncorrected.csv.gz"
        if mp.exists():
            m = pd.read_csv(mp)
            pp = m.fracture_id.map(lambda f: 1e6 + 1e6 * P.get(f, np.nan))
            row[f"prmse_{name}_kpa"] = float(np.sqrt(np.nanmean((pp - m.pressure_fullDFN) ** 2)) / 1e3)
            row["prmse_raw_kpa"] = float(np.sqrt(np.mean((m.pressure_graph - m.pressure_fullDFN) ** 2)) / 1e3)
        row[f"frac_kept_bigrafv_{name}"] = float(Es.kept_bigrafv.mean())
    row["seconds"] = time.time() - t0
    return row, fill(g_inf), Fs, E
