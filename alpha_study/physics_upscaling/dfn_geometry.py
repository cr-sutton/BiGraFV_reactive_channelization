"""Reconstruct planar fracture polygons and intersection segments from the
compact BiGraFV study archive (study/ directory).

Only archived dfnGen output is used: fracture centers, normals, radii, the
domain size, and intersection midpoints/lengths.  No DFN mesh or DFN flow
information is touched, so everything here is available at deployment.

Conventions (dfnGen):
  * rectangle vertices in local coordinates: (+-r, +-r*aspect), then rotated
    from e_z to the fracture normal with the Rodrigues rotation.
  * domain is an axis-aligned box centered on the origin.
"""

from __future__ import annotations

import gzip
import json
import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

EPS = 1.0e-12


def rotation_to_normal(n):
    """Rotation matrix taking e_z to unit normal n (dfnGen convention)."""
    n = np.asarray(n, float)
    n = n / np.linalg.norm(n)
    ez = np.array([0.0, 0.0, 1.0])
    v = np.cross(ez, n)
    s = np.linalg.norm(v)
    c = float(np.dot(ez, n))
    if s < 1.0e-12:
        return np.eye(3) if c > 0 else np.diag([1.0, -1.0, -1.0])
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + vx + vx @ vx * ((1.0 - c) / (s * s))


def clip_polygon_halfplane(poly, a, b):
    """Sutherland-Hodgman clip of a 2D polygon to {x : a.x <= b}."""
    out = []
    m = len(poly)
    for i in range(m):
        P = poly[i]
        Q = poly[(i + 1) % m]
        fp = float(np.dot(a, P) - b)
        fq = float(np.dot(a, Q) - b)
        if fp <= 0:
            out.append(P)
        if fp * fq < 0:
            t = fp / (fp - fq)
            out.append(P + t * (Q - P))
    return out


@dataclass
class Fracture:
    fid: int
    center: np.ndarray
    normal: np.ndarray
    R: np.ndarray            # columns e1, e2, n
    poly2d: np.ndarray       # clipped polygon, local coords
    radius: float
    transmissivity: float
    aperture: float
    # edges of the clipped polygon lying on the inflow / outflow faces
    boundary_segments: dict = field(default_factory=dict)

    def to_local(self, X):
        return (np.asarray(X, float) - self.center) @ self.R[:, :2]

    def to_global(self, uv):
        uv = np.atleast_2d(uv)
        return self.center + uv @ self.R[:, :2].T


def _polygon_local(shape, r, aspect=1.0, nvert=4):
    if shape == "rect":
        x, y = r, r * aspect
        return np.array([[-x, -y], [x, -y], [x, y], [-x, y]], float)
    # dfnGen ellipse: nvert points on the ellipse (in-plane rotation unknown
    # when beta is random; aspect 1 makes this a regular n-gon)
    th = 2.0 * np.pi * np.arange(nvert) / nvert
    return np.c_[r * np.cos(th), r * aspect * np.sin(th)]


def build_fractures(study: Path, domain, shape="rect", nvert=4, flow_axis=0):
    fr = pd.read_csv(study / "fractures.csv.gz")
    half = 0.5 * np.asarray(domain, float)
    out = {}
    for _, r in fr.iterrows():
        c = np.array([r.cx, r.cy, r.cz], float)
        n = np.array([r.nx, r.ny, r.nz], float)
        n /= np.linalg.norm(n)
        R = rotation_to_normal(n)
        rad = float(r.rx)
        aspect = float(r.ry) / max(float(r.rx), EPS)
        poly = list(_polygon_local(shape, rad, aspect, nvert))
        e1, e2 = R[:, 0], R[:, 1]
        bsegs = {}
        # clip by the 6 domain faces: for axis k, +-(c_k + u e1_k + v e2_k) <= half_k
        tags = []
        for k in range(3):
            for sgn in (+1.0, -1.0):
                a = sgn * np.array([e1[k], e2[k]])
                b = half[k] - sgn * c[k]
                if np.linalg.norm(a) < 1e-14:
                    continue
                poly = clip_polygon_halfplane(poly, a, b)
                tags.append((k, sgn, a, b))
                if len(poly) < 3:
                    break
        poly = np.array(poly, float)
        if len(poly) >= 3:
            # identify edges on inflow (-) / outflow (+) faces of the flow axis
            k = flow_axis
            for sgn, label in ((-1.0, "source"), (+1.0, "target")):
                a = sgn * np.array([e1[k], e2[k]])
                b = half[k] - sgn * c[k]
                if np.linalg.norm(a) < 1e-14:
                    continue
                on = np.abs(poly @ a - b) < 1e-7 * max(1.0, half[k])
                m = len(poly)
                segs = []
                for i in range(m):
                    j = (i + 1) % m
                    if on[i] and on[j]:
                        segs.append((poly[i].copy(), poly[j].copy()))
                if segs:
                    bsegs[label] = segs
        T = float(r.perm) * float(r.aperture)
        out[int(r.fracture_id)] = Fracture(int(r.fracture_id), c, n, R, poly, rad,
                                           T, float(r.aperture), bsegs)
    return out


def clip_line_to_polygon(p0, d, poly):
    """Return parameter interval [t0,t1] of line p0 + t d inside convex poly."""
    t0, t1 = -np.inf, np.inf
    m = len(poly)
    # ensure CCW
    area = 0.5 * np.sum(poly[:, 0] * np.roll(poly[:, 1], -1) - np.roll(poly[:, 0], -1) * poly[:, 1])
    P = poly if area > 0 else poly[::-1]
    for i in range(m):
        A = P[i]
        B = P[(i + 1) % m]
        e = B - A
        nrm = np.array([e[1], -e[0]])  # outward for CCW
        num = float(np.dot(nrm, A - p0))
        den = float(np.dot(nrm, d))
        if abs(den) < 1e-14:
            if num < 0:
                return None
            continue
        t = num / den
        if den > 0:
            t1 = min(t1, t)
        else:
            t0 = max(t0, t)
    if t1 <= t0:
        return None
    return t0, t1


def intersection_segments(study: Path, fracs, ints=None):
    """Rebuild 3D endpoints of every fracture-fracture intersection.

    Returns DataFrame with intersection_id, f1, f2, xa, xb (3-vectors), the
    reconstructed length and the archived length.
    """
    if ints is None:
        ints = pd.read_csv(study / "intersections.csv.gz")
    rows = []
    for _, r in ints.iterrows():
        if pd.isna(r.fracture2):
            continue
        f1, f2 = int(r.fracture1), int(r.fracture2)
        A, B = fracs.get(f1), fracs.get(f2)
        if A is None or B is None or len(A.poly2d) < 3 or len(B.poly2d) < 3:
            continue
        d = np.cross(A.normal, B.normal)
        nd = np.linalg.norm(d)
        if nd < 1e-10:
            continue
        d /= nd
        xm = np.array([r.x, r.y, r.z], float)
        ia = clip_line_to_polygon(A.to_local(xm)[0] if A.to_local(xm).ndim > 1 else A.to_local(xm),
                                  d @ A.R[:, :2], A.poly2d)
        ib = clip_line_to_polygon(B.to_local(xm), d @ B.R[:, :2], B.poly2d)
        L = float(r.length)
        if ia is None or ib is None:
            t0, t1 = -0.5 * L, 0.5 * L
            ok = False
        else:
            t0, t1 = max(ia[0], ib[0]), min(ia[1], ib[1])
            ok = t1 > t0
            if not ok:
                t0, t1 = -0.5 * L, 0.5 * L
        rows.append(dict(intersection_id=str(r.intersection_id), f1=f1, f2=f2,
                         xa=xm + t0 * d, xb=xm + t1 * d, length_rec=t1 - t0,
                         length_arch=L, recon_ok=ok))
    return pd.DataFrame(rows)


def read_domain(study: Path):
    ns = json.loads((study / "network_summary.json").read_text())
    return [ns["domain_x"], ns["domain_y"], ns["domain_z"]], ns.get("fracture_shape", "rect")


def read_polygons_dat(path):
    """Vertices of every final (clipped) fracture polygon written by dfnGen."""
    import re
    polys = []
    for line in Path(path).read_text().splitlines()[1:]:
        pts = re.findall(r"\{([^}]*)\}", line)
        if pts:
            polys.append(np.array([[float(v) for v in p.split(",")] for p in pts]))
    return polys


def fractures_from_dfngen(dfngen_dir, perm, aperture, domain, flow_axis=0):
    """Fractures straight from dfnGen output (exact clipped polygons, any shape).

    Uses polygons.dat (what dfnWorks meshes), normal_vectors.dat and the
    retained rows of translations.dat; perm/aperture are the per-fracture
    arrays of the DFN object (final numbering, 1-based ids).
    """
    g = Path(dfngen_dir)
    polys = read_polygons_dat(g / "polygons.dat")
    tr = [l.split() for l in (g / "translations.dat").read_text().splitlines()[1:] if l.strip()]
    centers = np.array([[float(v) for v in t[:3]] for t in tr if "R" not in t])
    normals = np.loadtxt(g / "normal_vectors.dat", ndmin=2)
    n = len(polys)
    assert len(centers) == len(normals) == len(perm) == len(aperture) == n, "fracture count mismatch"
    half = 0.5 * np.asarray(domain, float)
    out = {}
    for i in range(n):
        c = centers[i]
        nrm = normals[i] / np.linalg.norm(normals[i])
        R = rotation_to_normal(nrm)
        P = polys[i]
        poly2d = (P - c) @ R[:, :2]
        bsegs = {}
        k = flow_axis
        tol = 1e-6 * max(1.0, half[k])
        for sgn, label in ((-1.0, "source"), (1.0, "target")):
            on = np.abs(P[:, k] - sgn * half[k]) < tol
            segs = [(poly2d[a].copy(), poly2d[(a + 1) % len(P)].copy())
                    for a in range(len(P)) if on[a] and on[(a + 1) % len(P)]]
            if segs:
                bsegs[label] = segs
        rad = float(np.sqrt(np.abs(0.5 * np.sum(poly2d[:, 0] * np.roll(poly2d[:, 1], -1)
                                                   - np.roll(poly2d[:, 0], -1) * poly2d[:, 1])) / np.pi))
        out[i + 1] = Fracture(i + 1, c, nrm, R, poly2d, rad, float(perm[i]) * float(aperture[i]),
                              float(aperture[i]), bsegs)
    return out


def intersections_from_dfngen(dfngen_dir):
    """Fracture-fracture intersections (midpoint, length) from intersection_list.dat."""
    il = pd.read_csv(Path(dfngen_dir) / "intersection_list.dat", sep=r"\s+")
    il = il[il.f2 > 0]
    return pd.DataFrame(dict(intersection_id=[f"i{a}_{b}" for a, b in zip(il.f1, il.f2)],
                             fracture1=il.f1.astype(int), fracture2=il.f2.astype(float),
                             x=il.x, y=il.y, z=il.z, length=il.length))
