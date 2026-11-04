"""Physics-based (fit-free) multiport upscaling of each fracture.

For every fracture the steady 2D Darcy problem  div(T grad p) = 0  is solved
in its own clipped polygon, with every intersection segment (and every
inflow/outflow boundary edge) acting as an equipotential port.  The Schur
complement onto the ports gives the exact port-to-port conductance matrix
(Dirichlet-to-Neumann map) M_f.  This is the equivalent-pipe-network idea of
Dershowitz & Fidelibus (1999, WRR) and the local step of local-global
upscaling (Chen & Durlofsky), computed with a cheap per-fracture raster.

Assembling sum_f T_f M_f over shared intersection nodes gives a network that
retains in-plane 2D flow spreading, which BiGraFV's single-node star graph
removes.  Its effective conductance divided by the BiGraFV conductance is a
graph-only prediction of alpha = Q_DFN / Q_graph with no fitted parameter.
"""

from __future__ import annotations

import math
from collections import defaultdict

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.sparse.linalg import splu, spsolve

from dfn_geometry import Fracture


def _inside_convex(P, poly):
    area = 0.5 * np.sum(poly[:, 0] * np.roll(poly[:, 1], -1) - np.roll(poly[:, 0], -1) * poly[:, 1])
    Q = poly if area > 0 else poly[::-1]
    ok = np.ones(len(P), bool)
    m = len(Q)
    for i in range(m):
        A, B = Q[i], Q[(i + 1) % m]
        e = B - A
        ok &= (e[0] * (P[:, 1] - A[1]) - e[1] * (P[:, 0] - A[0])) >= -1e-12
    return ok


def fracture_dtn(frac: Fracture, ports, ncell=48, return_field=False, coef=None):
    """Port conductance matrix (unit transmissivity) for one fracture.

    coef: optional callable (frac, cell_centres_2d, ports) -> relative
    transmissivity per raster cell, for in-fracture heterogeneity (faces use
    the harmonic mean).  None keeps the uniform-fracture operator.

    ports: list of (key, [(a2d, b2d), ...], kind) with kind 'slit' or 'edge'.
    Returns keys, M (n x n, symmetric, zero row sums), and optionally the
    raster + per-port unit-potential basis fields.
    """
    poly = frac.poly2d
    lo = poly.min(0)
    hi = poly.max(0)
    ext = float(max(hi - lo))
    h = ext / ncell
    nx = max(int(math.ceil((hi[0] - lo[0]) / h)), 1)
    ny = max(int(math.ceil((hi[1] - lo[1]) / h)), 1)
    xc = lo[0] + (np.arange(nx) + 0.5) * h
    yc = lo[1] + (np.arange(ny) + 0.5) * h
    X, Y = np.meshgrid(xc, yc, indexing="ij")
    P = np.c_[X.ravel(), Y.ravel()]
    active = _inside_convex(P, poly)
    cid = -np.ones(nx * ny, int)
    cid[active] = np.arange(active.sum())
    ncel = int(active.sum())
    cen = P[active]

    owner = -np.ones(ncel, int)  # port index owning each cell
    centroid = cen.mean(0) if ncel else lo
    for pi, (_, segs, kind) in enumerate(ports):
        for a, b in segs:
            a = np.asarray(a, float)
            b = np.asarray(b, float)
            L = float(np.linalg.norm(b - a))
            ns = max(int(math.ceil(3.0 * L / h)), 2)
            t = np.linspace(0.0, 1.0, ns)
            S = a[None, :] + t[:, None] * (b - a)[None, :]
            if kind == "edge":
                # push samples half a cell into the polygon
                S = S + 0.5 * h * (centroid - S) / np.maximum(np.linalg.norm(centroid - S, axis=1, keepdims=True), 1e-12)
            ix = np.clip(((S[:, 0] - lo[0]) / h).astype(int), 0, nx - 1)
            iy = np.clip(((S[:, 1] - lo[1]) / h).astype(int), 0, ny - 1)
            c = cid[ix * ny + iy]
            if np.any(c < 0):
                # sample fell on an inactive cell: snap to nearest active cell
                bad = np.where(c < 0)[0]
                for k in bad:
                    d2 = np.sum((cen - S[k]) ** 2, axis=1)
                    c[k] = int(np.argmin(d2))
            for cc in np.unique(c):
                if owner[cc] < 0:
                    owner[cc] = pi
    n = len(ports)
    # ports with no cell (degenerate, very short): give them nearest cell
    for pi in range(n):
        if not np.any(owner == pi):
            (_, segs, _) = ports[pi]
            m = 0.5 * (np.asarray(segs[0][0]) + np.asarray(segs[0][1]))
            d2 = np.sum((cen - m) ** 2, axis=1)
            d2[owner >= 0] = np.inf
            if np.isfinite(d2.min()):
                owner[int(np.argmin(d2))] = pi

    # neighbor faces (unit conductance per face for square cells, 2D)
    I = cid.reshape(nx, ny)
    fa, fb = [], []
    a1, b1 = I[:-1, :].ravel(), I[1:, :].ravel()
    a2, b2 = I[:, :-1].ravel(), I[:, 1:].ravel()
    for a, b in ((a1, b1), (a2, b2)):
        m = (a >= 0) & (b >= 0)
        fa.append(a[m]); fb.append(b[m])
    fa = np.concatenate(fa); fb = np.concatenate(fb)

    # collapse port cells to port nodes: node index = n + free_idx, or port id
    free = owner < 0
    nf = int(free.sum())
    node = np.empty(ncel, int)
    node[~free] = owner[~free]
    node[free] = n + np.arange(nf)
    na, nb = node[fa], node[fb]
    keep = na != nb
    na, nb = na[keep], nb[keep]
    N = n + nf
    w = np.ones(len(na))
    if coef is not None:
        c = np.asarray(coef(frac, cen, ports), float)
        w = (2.0 * c[fa] * c[fb] / (c[fa] + c[fb]))[keep]
    A = coo_matrix((np.r_[w, w, -w, -w], (np.r_[na, nb, na, nb], np.r_[na, nb, nb, na])), shape=(N, N)).tocsr()
    App = A[:n, :n].toarray()
    if nf:
        Auu = A[n:, n:].tocsc()
        Aup = A[n:, :n].toarray()
        # isolated free components with no port contact -> singular blocks
        ncomp, lab = connected_components(A[n:, n:], directed=False)
        touches = np.zeros(ncomp, bool)
        touches[np.unique(lab[np.any(Aup != 0, axis=1)])] = True
        if not touches.all():
            fix = ~touches[lab]
            Auu = Auu.tolil()
            for k in np.where(fix)[0]:
                Auu[k, k] = Auu[k, k] + 1.0
            Auu = Auu.tocsc()
        lu = splu(Auu)
        X = lu.solve(-Aup)  # free potentials for unit port potentials
        M = App + (A[:n, n:] @ X)
    else:
        X = None
        M = App
    M = 0.5 * (M + M.T)
    keys = [p[0] for p in ports]
    # area-mean fracture pressure as a linear function of port pressures
    w = np.array([np.sum(owner == k) for k in range(n)], float)
    if X is not None:
        w += X.sum(axis=0)
    w /= max(ncel, 1)
    if return_field:
        return keys, M, w, dict(h=h, cen=cen, owner=owner, free=free, X=X, fa=fa, fb=fb)
    return keys, M, w


def build_ports(fracs, isegs, n_sub=1):
    """ports[fid] = list of (key, segments_local, kind)."""
    ports = defaultdict(list)
    for _, r in isegs.iterrows():
        xa, xb = np.asarray(r.xa), np.asarray(r.xb)
        for k in range(n_sub):
            pa = xa + (xb - xa) * (k / n_sub)
            pb = xa + (xb - xa) * ((k + 1) / n_sub)
            key = ("i", r.intersection_id, k)
            for f in (r.f1, r.f2):
                F = fracs[f]
                ports[f].append((key, [(F.to_local(pa), F.to_local(pb))], "slit"))
    for fid, F in fracs.items():
        for label, segs in F.boundary_segments.items():
            ports[fid].append((label, segs, "edge"))
    return ports


def assemble_and_solve(fracs, ports, ncell=48, return_details=False, coef=None):
    """Effective s->t conductance of the multiport network (mu omitted)."""
    blocks = {}
    for fid, plist in ports.items():
        if len(plist) < 2:
            continue
        keys, M, w = fracture_dtn(fracs[fid], plist, ncell=ncell, coef=coef)
        blocks[fid] = (keys, fracs[fid].transmissivity * M, w)
    allkeys = {}
    for keys, _, _ in blocks.values():
        for k in keys:
            if k not in allkeys:
                allkeys[k] = len(allkeys)
    if "source" not in allkeys or "target" not in allkeys:
        return np.nan, None
    rows, cols, vals = [], [], []
    for keys, M, _ in blocks.values():
        idx = np.array([allkeys[k] for k in keys])
        rr, cc = np.meshgrid(idx, idx, indexing="ij")
        rows.append(rr.ravel()); cols.append(cc.ravel()); vals.append(M.ravel())
    N = len(allkeys)
    L = coo_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(N, N)).tocsr()
    s, t = allkeys["source"], allkeys["target"]
    # restrict to the component containing s and t
    ncomp, lab = connected_components(abs(L) > 0, directed=False)
    if lab[s] != lab[t]:
        return np.nan, None
    comp = np.where(lab == lab[s])[0]
    inner = np.array([i for i in comp if i not in (s, t)])
    p = np.zeros(N)
    p[s] = 1.0
    if len(inner):
        rhs = -(L[inner][:, [s]] @ np.array([1.0]))
        p[inner] = spsolve(L[inner][:, inner].tocsc(), rhs)
    q = float(L[s, :].dot(p)[0])
    if return_details:
        inv = {v: k for k, v in allkeys.items()}
        pk = {inv[i]: p[i] for i in comp}
        pbar, flux = {}, defaultdict(float)
        for fid, (keys, M, w) in blocks.items():
            pv = np.array([pk.get(k, np.nan) for k in keys])
            if np.any(np.isnan(pv)):
                continue
            pbar[fid] = float(w @ pv)
            inj = M @ pv  # flux entering fracture fid through each port
            for k, qk in zip(keys, inj):
                port = k[1] if isinstance(k, tuple) else k
                flux[(fid, port)] += float(qk)
        return q, dict(p=pk, pbar=pbar, flux=dict(flux), blocks=blocks, keys=allkeys)
    return q, None


def flow_partition(field, port_p):
    """Split one fracture into flowing and slow parts from its 2D field.

    port_p: port potentials (network solution) in fracture_dtn key order.
    Returns (phi_flow, q_ex, q_through) with fluxes for unit transmissibility:
      phi_flow  : flux participation ratio (Hyman et al. 2020) as an area fraction
      q_ex      : one-way advective flux crossing between fast and slow cells
      q_through : one-way flux entering the fracture through its ports
    """
    owner, free, X = field["owner"], field["free"], field["X"]
    u = np.empty(len(owner))
    u[~free] = np.asarray(port_p)[owner[~free]]
    if X is not None:
        u[free] = X @ np.asarray(port_p)
    fa, fb = field["fa"], field["fb"]
    F = u[fa] - u[fb]  # face flux (unit conductance per face)
    same_port = (~free[fa]) & (~free[fb]) & (owner[fa] == owner[fb])
    F[same_port] = 0.0
    s = np.zeros(len(u))
    np.add.at(s, fa, np.abs(F))
    np.add.at(s, fb, np.abs(F))
    s *= 0.5
    if s.sum() <= 0:
        return 1.0, 0.0, 0.0
    phi = float(s.sum() ** 2 / (len(s) * np.sum(s * s)))
    nfast = max(int(round(phi * len(s))), 1)
    fast = np.zeros(len(s), bool)
    fast[np.argsort(-s)[:nfast]] = True
    cross = fast[fa] != fast[fb]
    q_ex = 0.5 * float(np.abs(F[cross]).sum())
    port_face = (~free[fa]) != (~free[fb])
    q_through = 0.5 * float(np.abs(F[port_face]).sum())
    return phi, q_ex, q_through
