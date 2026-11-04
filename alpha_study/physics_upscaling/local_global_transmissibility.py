"""Local-global upscaled transmissibilities for the BiGraFV graph.

The multiport solve (multiport_upscaling.py) provides, for the applied
pressure boundary conditions, every fracture's area-mean pressure Pbar_f and
the flux through every intersection / boundary edge.  Following local-global
upscaling (Chen, Durlofsky, Gerritsen & Wen 2003), each existing BiGraFV
connection receives

    T_e = q_e / (Pbar_f - Pbar_g)

so that the one-cell-per-fracture TPFA graph reproduces the multiport fluxes
and fracture pressures.  The result is expressed as a multiplier on the
existing BiGraFV connection conductance,

    c_e = T_e / G_e^graph   ->  UGE connection area *= c_e

so PFLOTRAN (or any TPFA solver) is used unchanged; cell volume, aperture and
permeability are untouched.

Connections where q_e and the mean-pressure drop disagree in sign (or the
drop is too small for a stable ratio) cannot be represented by a positive
TPFA transmissibility; they get the median multiplier of the well-posed
connections on the same fracture pair neighbourhood, and the graph is then
re-solved so the reported Q and pressures are the ones PFLOTRAN would see.
"""

from __future__ import annotations

import gzip
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve

EPS = 1.0e-30


def bigrafv_edges(study: Path, projection_clip=0.05):
    """Exact BiGraFV connection conductances (as in bigrafv_multiport_q_sweep)."""
    fr = pd.read_csv(study / "fractures.csv.gz").set_index("fracture_id")
    ints = pd.read_csv(study / "intersections.csv.gz")
    with gzip.open(study / "bipartite_graph.json.gz", "rt") as fh:
        gj = json.load(fh)
    area = {n["id"]: float(n["area"]) for n in gj.get("nodes", []) if isinstance(n.get("id"), str) and "area" in n}
    rows = []
    for _, r in ints.iterrows():
        iid = str(r.intersection_id)
        f1 = int(r.fracture1)
        xI = np.array([r.x, r.y, r.z], float)
        x1 = fr.loc[f1, ["cx", "cy", "cz"]].to_numpy(float)
        k1 = float(fr.loc[f1, "perm"])
        if pd.notna(r.fracture2):
            f2 = int(r.fracture2)
            x2 = fr.loc[f2, ["cx", "cy", "cz"]].to_numpy(float)
            k2 = float(fr.loc[f2, "perm"])
            delta = x2 - x1
            D = float(np.linalg.norm(delta))
            t = float(np.clip(np.dot(xI - x1, delta) / (D * D), projection_clip, 1 - projection_clip))
            dphys = float(np.linalg.norm(xI - x1) + np.linalg.norm(xI - x2))
            A = area[iid] * D / dphys
            g = A / (t * D / k1 + (1 - t) * D / k2)
            rows.append(dict(intersection_id=iid, u=f1, v=f2, G_graph=g))
        else:
            b = str(r.boundary).strip().lower()
            if b not in ("source", "target"):
                continue
            d = float(np.linalg.norm(xI - x1))
            g = float(r.length) * float(fr.loc[f1, "aperture"]) * k1 / d
            rows.append(dict(intersection_id=iid, u=f1, v=b, G_graph=g))
    return pd.DataFrame(rows)


def solve_graph(E, gcol, p_in=1.0, p_out=0.0):
    """Solve the one-node-per-fracture graph; returns Q (from source) and pressures."""
    nodes = sorted(set(E.u.tolist()) | set(x for x in E.v if not isinstance(x, str)))
    idx = {n: i for i, n in enumerate(nodes)}
    N = len(nodes)
    rows, cols, vals = [], [], []
    rhs = np.zeros(N)
    for u, v, g in zip(E.u, E.v, E[gcol]):
        i = idx[u]
        if isinstance(v, str):
            pb = p_in if v == "source" else p_out
            rows.append(i); cols.append(i); vals.append(g)
            rhs[i] += g * pb
        else:
            j = idx[v]
            rows += [i, j, i, j]; cols += [i, j, j, i]; vals += [g, g, -g, -g]
    L = coo_matrix((vals, (rows, cols)), shape=(N, N)).tocsr()
    # drop components without a boundary connection
    diag = L.diagonal()
    keep = diag > 0
    p = np.full(N, np.nan)
    from scipy.sparse.csgraph import connected_components
    nc, lab = connected_components(L, directed=False)
    anchored = np.zeros(nc, bool)
    for u, v in zip(E.u, E.v):
        if isinstance(v, str):
            anchored[lab[idx[u]]] = True
    act = np.where(anchored[lab] & keep)[0]
    p[act] = spsolve(L[act][:, act].tocsc(), rhs[act])
    P = {n: p[idx[n]] for n in nodes}
    Q = sum(g * (p_in - P[u]) for u, v, g in zip(E.u, E.v, E[gcol]) if v == "source" and np.isfinite(P[u]))
    return float(Q), P


def local_global_multipliers(E, det, min_drop=1e-4, min_rel_flux=1e-5, c_bounds=(1e-2, 1e2)):
    """Per-connection multiplier c_e from the multiport fluxes / mean pressures.

    Dead-end connections carry no steady flux, so any positive transmissibility
    reproduces them; they (and sign-inconsistent connections) get the median
    multiplier.  Multipliers are clamped to c_bounds so no connection becomes a
    near-disconnection that destabilizes the TPFA solve.
    """
    pbar = det["pbar"]
    flux = det["flux"]
    q_total = sum(abs(v) for (f, k), v in flux.items() if k == "source")
    c = np.full(len(E), np.nan)
    status = []
    for k, (iid, u, v, g) in enumerate(zip(E.intersection_id, E.u, E.v, E.G_graph)):
        if isinstance(v, str):
            # flux entering fracture u through its boundary port = T (p_bc - Pbar_u)
            q = flux.get((u, v), np.nan)
            drop = (1.0 if v == "source" else 0.0) - pbar.get(u, np.nan)
        else:
            q = flux.get((v, iid), np.nan)  # flux entering v through this intersection
            drop = pbar.get(u, np.nan) - pbar.get(v, np.nan)
        if not np.isfinite(q) or not np.isfinite(drop):
            status.append("missing"); continue
        if abs(q) < min_rel_flux * q_total:
            status.append("deadend"); continue
        if abs(drop) < min_drop or q * drop <= 0:
            status.append("illposed"); continue
        c[k] = float(np.clip((q / drop) / g, *c_bounds))
        status.append("ok")
    E = E.copy()
    E["c_raw"] = c
    E["status"] = status
    ok = E.status == "ok"
    fill = float(np.exp(np.median(np.log(E.loc[ok, "c_raw"])))) if ok.any() else 1.0
    E["c"] = E.c_raw.where(ok, fill)
    E["G_lg"] = E.G_graph * E.c
    return E, fill
