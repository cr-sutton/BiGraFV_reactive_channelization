"""Property-independent geometric half-transmissibilities for BiGraFV.

Each fracture's port conductance matrix M_f (unit transmissibility, from
multiport_upscaling.fracture_dtn) is a purely geometric operator: Darcy flow,
molecular diffusion of any species and heat conduction in the fracture plane
all share it, because each is a Laplace problem with a coefficient that is
uniform within the fracture.

BiGraFV has one cell per fracture, i.e. a star: the fracture centre is linked
to each port k by a dimensionless half-conductance g_{f,k}.  A star's Schur
complement is diag(g) - g g^T / sum(g) and its centre pressure is
sum(g p)/sum(g).  Requiring the centre to carry the area-mean fracture pressure
(the quantity matched to the DFN) for every port state forces g_k = lam * w_k,
with w the mean-pressure weights from the 2D solve; lam is the least-squares
match to M_f.  (A free fit of g is kept as a diagnostic.)

Per connection f-g the TPFA half-transmissibilities are then
    k_f * b_f * g_{f,k}   (flow)       phi D * b_f * g_{f,k}   (diffusion)
so the geometric factor Gamma_f = b_f g_{f,k} (metres) is the only thing
written to the UGE: face position along the centre-centre segment and face
area.  Permeability, porosity, diffusion coefficients and cell volumes are
left to PFLOTRAN, which combines them harmonically per half as usual.
"""

from __future__ import annotations

from collections import defaultdict

import numpy as np
from scipy.optimize import least_squares

from multiport_upscaling import build_ports, fracture_dtn


def star_from_weights(M, w):
    """g = lam * w with lam the Frobenius least-squares match of the star to M."""
    S = np.diag(w) - np.outer(w, w)
    lam = float(np.sum(S * M) / max(np.sum(S * S), 1e-300))
    return lam * w


def star_free(M, g0):
    """Unconstrained (positive) star fit to M, for comparison."""
    n = len(g0)
    iu = np.triu_indices(n, 1)
    scale = max(np.abs(M[iu]).max(), 1e-300)

    def res(lg):
        g = np.exp(lg)
        St = np.diag(g) - np.outer(g, g) / g.sum()
        return (St[iu] - M[iu]) / scale

    sol = least_squares(res, np.log(np.maximum(g0, 1e-12)), method="trf")
    return np.exp(sol.x)


def port_name(key):
    return key[1] if isinstance(key, tuple) else key  # intersection id or 'source'/'target'


def star_diag_match(M, w):
    """g = lam * w with lam matching the summed port self-conductances (trace)."""
    S = np.diag(w) - np.outer(w, w)
    return float(np.trace(M) / max(np.trace(S), 1e-300)) * w


def aggregate(keys, M, w):
    """Tie the sub-ports of each intersection together (one graph connection each)."""
    names = [port_name(k) for k in keys]
    uniq = list(dict.fromkeys(names))
    P = np.zeros((len(keys), len(uniq)))
    for i, nm in enumerate(names):
        P[i, uniq.index(nm)] = 1.0
    return uniq, P.T @ M @ P, P.T @ w


def fracture_half_factors(fracs, isegs, ncell, n_sub, method="frob"):
    """Dimensionless half-conductances g[(fid, port)], one per intersection/boundary."""
    ports = build_ports(fracs, isegs, n_sub=n_sub)
    g = {}
    for fid, plist in ports.items():
        if len(plist) < 2:
            continue
        keys, M, w = fracture_dtn(fracs[fid], plist, ncell=ncell)
        names, Ma, wa = aggregate(keys, M, w)
        if len(names) < 2:
            continue
        if method == "frob":
            gk = star_from_weights(Ma, wa)
        elif method == "trace":
            gk = star_diag_match(Ma, wa)
        else:
            gk = star_free(Ma, star_from_weights(Ma, wa))
        for nm, v in zip(names, gk):
            g[(fid, nm)] = float(v)
    return g


def richardson(g_fine, g_coarse):
    """First-order extrapolation per half-connection, kept positive."""
    out = {}
    for k, vf in g_fine.items():
        vc = g_coarse.get(k, vf)
        v = 2.0 * vf - vc
        out[k] = v if v > 0 else vf
    return out


def flow_conditioned_half_factors(fracs, det, min_rel_flux=1e-5, min_drop=1e-6):
    """Per-half geometric factors from the 2D multiport solution.

    g_{f,k} = q_{f,k} / (T_f (Pbar_f - pbar_k)), with q_{f,k} the flux leaving
    fracture f through intersection (or boundary) k, Pbar_f the area-mean
    fracture pressure and pbar_k the mean pressure along intersection k.  T_f
    is divided out, so g is geometric (dimensionless) and PFLOTRAN re-applies
    k_f, phi_f, D_s, ... per half.  Halves with negligible flux or with flux
    against the centre-to-port drop cannot be represented by a positive
    two-point half-transmissibility; they are returned in `bad` for fallback.
    """
    p = det["p"]
    pk = defaultdict(list)
    for key, val in p.items():
        pk[port_name(key)].append(val)
    pbar_port = {k: float(np.mean(v)) for k, v in pk.items()}
    q_total = sum(abs(v) for (f, k), v in det["flux"].items() if k == "source")
    g, bad = {}, {}
    for (fid, k), q_in in det["flux"].items():
        if fid not in det["pbar"]:
            continue
        q_out = -q_in  # flux leaving fracture fid through port k
        drop = det["pbar"][fid] - pbar_port[k]
        T = fracs[fid].transmissivity
        if abs(q_out) < min_rel_flux * q_total:
            bad[(fid, k)] = "deadend"
        elif abs(drop) < min_drop or q_out * drop <= 0:
            bad[(fid, k)] = "illposed"
        else:
            g[(fid, k)] = q_out / (T * drop)
    return g, bad


def star_flow(fracs, isegs, g):
    """s->t flow of the one-cell-per-fracture graph built from half factors g.

    Connections whose halves are missing (single-port, dead-end fractures)
    carry no steady flux and are omitted.
    """
    import pandas as pd
    from local_global_transmissibility import solve_graph

    rows = []
    for iid, u, v in zip(isegs.intersection_id, isegs.f1, isegs.f2):
        gu, gv = g.get((u, iid)), g.get((v, iid))
        if gu and gv:
            rows.append(dict(u=u, v=v, G=1.0 / (1.0 / (fracs[u].transmissivity * gu) + 1.0 / (fracs[v].transmissivity * gv))))
    for (f, k), val in g.items():
        if k in ("source", "target"):
            rows.append(dict(u=f, v=k, G=fracs[f].transmissivity * val))
    q, _ = solve_graph(pd.DataFrame(rows), "G")
    return q


def match_flow_with_unrepresentable(fracs, isegs, g, bad, q_target, lo=1e-3, hi=1e3, iters=60):
    """REJECTED (kept for the record): scale only the unrepresentable halves so
    the graph carries q_target.  On the convergence sample the target was
    unreachable (scale pinned at the bound): those halves carry in-plane flux
    against the centre-to-port drop, so raising them pushes more flux the
    wrong way.  Not used by bigrafv_geometric_correction.


    The well-posed halves are fixed by the in-plane physics; the others are
    undetermined by it, and the one graph-only condition used to set them is
    that total flow equals the multiport (in-plane) flow at the same level.
    Returns (g, scale).  If q_target is unreachable the nearest bound is kept.
    """
    keys = [k for k in bad if k in g]
    if not keys:
        return g, 1.0

    def with_scale(s):
        out = dict(g)
        for k in keys:
            out[k] = g[k] * s
        return out

    f_lo, f_hi = star_flow(fracs, isegs, with_scale(lo)) - q_target, star_flow(fracs, isegs, with_scale(hi)) - q_target
    if f_lo * f_hi > 0:
        s = lo if abs(f_lo) < abs(f_hi) else hi
        return with_scale(s), s
    a, b = np.log(lo), np.log(hi)
    for _ in range(iters):
        m = 0.5 * (a + b)
        fm = star_flow(fracs, isegs, with_scale(np.exp(m))) - q_target
        if fm * f_lo > 0:
            a, f_lo = m, fm
        else:
            b = m
    s = float(np.exp(0.5 * (a + b)))
    return with_scale(s), s
