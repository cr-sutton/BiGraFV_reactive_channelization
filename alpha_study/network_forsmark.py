#!/usr/bin/env python3
"""
Forsmark FFM01 networks for the graph-only (BiGraFV) reactive study:
domain 1000 x 250 x 250 m, flow along x (left -> right).  No DFN mesh is built;
the graph comes straight from dfnGen's intersection list.

Fracture statistics: SKB FFM01 open-fracture sets by depth layer, as coded in
src/forsmark/driver.py (SKB R-07-46 / TR-10-52 Table 6-75): five sets NS, NE,
NW, EW, HZ with Fisher poles, kappa 12.9-17.8, truncated power-law radii with
k_r 2.38-3.10, r0 = 0.038 m, r_max = 564 m.  Layer 1 = 0-200 m depth,
2 = 200-400 m, 3 = below 400 m.

P32: the SKB value is the one-sided open-fracture area per volume over
[r0, 564] m; the part inside [rmin, rmax] is kept (restricted-range expression,
Hyman et al. 2016 Appendix A) and passed to dfnWorks unchanged.
src/forsmark/driver.py doubles it ("two-sided"); dfnWorks' p32 is area of the
polygons over volume, i.e. one-sided, so p32_scale = 2 reproduces that driver.

Transmissivity: SKB semi-correlated T = a r^b with a = 6.3e-9, b = 1.3 and
sigma = 1.0 (FFM01); sigma = 0 gives the fully correlated model.  dfnWorks
converts T to the hydraulic aperture with the cubic law.
"""
from __future__ import annotations

import numpy as np

H = 1.0
R0_TABLE = 0.038
RMAX_TABLE = 564.0
T_A, T_B = 6.3e-9, 1.3

# (pole trend, pole plunge, kappa, k_r) per set, and the SKB one-sided P32 per layer
SETS = {"NS": (292.0, 1.0, 17.8, 2.50), "NE": (326.0, 2.0, 14.3, 2.70), "NW": (60.0, 6.0, 12.9, 3.10),
        "EW": (15.0, 2.0, 14.0, 3.10), "HZ": (5.0, 86.0, 15.2, 2.38)}
P32_SKB = {1: dict(NS=0.073, NE=0.319, NW=0.107, EW=0.088, HZ=0.543),
           2: dict(NS=0.142, NE=0.345, NW=0.133, EW=0.081, HZ=0.316),
           3: dict(NS=0.094, NE=0.163, NW=0.098, EW=0.039, HZ=0.141)}
DOMAINS = {"km250": [1000.0, 250.0, 250.0]}


def restricted_p32(p32_skb, kr, rmin, rmax):
    """Share of the SKB P32 carried by fractures with rmin <= r <= rmax."""
    return p32_skb * (rmax ** (2 - kr) - rmin ** (2 - kr)) / (RMAX_TABLE ** (2 - kr) - R0_TABLE ** (2 - kr))


def configure(DFN, seed, domain, p32_scale=1.0, sigma=1.0, rmin=5.0, rmax=RMAX_TABLE, layer=2):
    DFN.params["domainSize"]["value"] = list(domain)
    DFN.params["h"]["value"] = H
    DFN.params["orientationOption"]["value"] = 1
    DFN.params["stopCondition"]["value"] = 1
    DFN.params["seed"]["value"] = int(seed)
    DFN.params["boundaryFaces"]["value"] = [1, 1, 0, 0, 0, 0]
    DFN.params["keepOnlyLargestCluster"]["value"] = True
    DFN.params["disableFram"]["value"] = True
    DFN.params["domainSizeIncrease"]["value"] = [10, 10, 10]
    np.random.seed(int(seed))
    if sigma > 0:
        hy = dict(hy_function="semi-correlated", hy_params={"alpha": T_A, "beta": T_B, "sigma": sigma})
    else:
        hy = dict(hy_function="correlated", hy_params={"alpha": T_A, "beta": T_B})
    for name, (trend, plunge, kappa, kr) in SETS.items():
        DFN.add_fracture_family(shape="ell", number_of_points=16, distribution="tpl", alpha=kr,
                                min_radius=rmin, max_radius=rmax, kappa=kappa, trend=trend, plunge=plunge,
                                aspect=1.0, beta_distribution=1, beta=0.0,
                                p32=p32_scale * restricted_p32(P32_SKB[layer][name], kr, rmin, rmax),
                                hy_variable="transmissivity", **hy)
