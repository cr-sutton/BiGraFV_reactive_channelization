#!/usr/bin/env python3
"""
Kilometre-scale networks for graph-only (BiGraFV) dissolution scoping:
domains 1000 x 250 x 250 m and 1000 x 500 x 500 m, flow along the 1000 m axis
(x, left -> right).  No DFN mesh is built (too large); the graph comes straight
from dfnGen's intersection list.

Fracture statistics (sources in docs/weekend_literature_log.md):
  three orthogonal-mean families, Fisher kappa 10
  truncated power-law radii, alpha 2.6, r = 15-250 m (field-scale, Forsmark-type
      power-law exponent; minimum radius well above the 1 m mesh resolution h)
  P32 per family set so the network percolates across 1000 m with a few
      thousand fractures (see the build log for the realised P32 and count)
  aperture correlated with radius, b = 1e-5 r^0.8 (0.09-0.8 mm), inside the
      0.05-0.5 mm range given by SKB's aperture-transmissivity relation
      b = 0.5 T^0.5 for T = 1e-8 - 1e-6 m^2/s (TR-10-52, section 6.6.12)
"""
from __future__ import annotations

import numpy as np

H = 1.0
P32_FAMILY = 0.012
FAMILY = dict(shape="rect", distribution="tpl", alpha=2.6, min_radius=15.0, max_radius=250.0,
              kappa=10.0, p32=P32_FAMILY, aspect=1.0, beta_distribution=1, beta=0.0,
              hy_variable="aperture", hy_function="correlated", hy_params={"alpha": 1.0e-5, "beta": 0.8})
DOMAINS = {"km250": [1000.0, 250.0, 250.0], "km500": [1000.0, 500.0, 500.0]}


def configure(DFN, seed, domain, p32=P32_FAMILY, sigma=0.0):
    """sigma > 0: semi-correlated apertures, ln b = ln(1e-5 r^0.8) + sqrt(sigma) N(0,1)
    (dfnWorks semi-correlated; sigma 0.15 / 0.6 give log10 T spreads of about 0.5 / 1.0, the
    range of SKB semi-correlated transmissivity fits, TR-10-52 Table 6-74)."""
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
    fam = dict(FAMILY, p32=p32)
    if sigma > 0:
        fam.update(hy_function="semi-correlated", hy_params={"alpha": 1.0e-5, "beta": 0.8, "sigma": sigma})
    DFN.add_fracture_family(**fam, trend=0.0, plunge=0.0)
    DFN.add_fracture_family(**fam, trend=0.0, plunge=90.0)
    DFN.add_fracture_family(**fam, trend=90.0, plunge=0.0)
