#!/usr/bin/env python3
"""
Heterogeneity and dissolution-feedback options for the reactive decks, all as
PFLOTRAN input edits (used by deck_gypsum_calcite.py and deck_quartz.py):

  material porosity   the reference porosity of PFLOTRAN's permeability update;
                      set equal to the initial porosity so k starts at the
                      dfn_properties.h5 value
  permeability power  PERMEABILITY_POWER n:  k = k0 (phi / phi_ref)^n.  n = 3 is
                      the cubic law for a fracture cell of fixed thickness whose
                      open aperture grows with porosity (T ~ b^3)
  mineral fill        per-cell initial mineral volume fraction from a DATASET:
                      porosity lognormal about the mean, one value per fracture
                      (graph cell), so the reactive inventory, the open aperture
                      and the starting permeability all vary between fractures
"""
from __future__ import annotations

import re
from pathlib import Path

import h5py
import numpy as np


def set_material(deck, porosity=None, perm_power=None):
    """Edit the (single) MATERIAL_PROPERTY block."""
    if porosity is not None:
        deck, n = re.subn(r"^(MATERIAL_PROPERTY .*?^\s*POROSITY )\S+", lambda m: f"{m.group(1)}{porosity:.6g}d0",
                          deck, count=1, flags=re.S | re.M)
        assert n == 1, "material POROSITY not found"
    if perm_power is not None and perm_power != 1.0:
        deck, n = re.subn(r"^(MATERIAL_PROPERTY .*?\n  ID \d+\n)", lambda m: f"{m.group(1)}  PERMEABILITY_POWER {perm_power:g}\n",
                          deck, count=1, flags=re.S | re.M)
        assert n == 1, "MATERIAL_PROPERTY ID line not found"
    return deck


def fill_dataset(uge_cells, n_fractures, mean_porosity, sigma, seed, path, name="mineral_vf0"):
    """Per-cell initial mineral volume fraction: porosity lognormal about
    mean_porosity (ln-std sigma) on the first n_fractures cells (the fracture
    cells of a graph UGE), mean_porosity elsewhere.  Returns the per-cell VF."""
    rng = np.random.default_rng(seed)
    phi = np.full(len(uge_cells), mean_porosity)
    z = rng.normal(0.0, 1.0, n_fractures)
    phi[:n_fractures] = mean_porosity * np.exp(sigma * z - 0.5 * sigma ** 2)
    phi = np.clip(phi, 0.005, 0.95)
    vf = 1.0 - phi
    with h5py.File(path, "w") as h:
        h["Cell Ids"] = np.arange(1, len(uge_cells) + 1, dtype=np.int32)
        h[name] = vf
    return vf


def use_fill_dataset(deck, mineral, h5_name, name="mineral_vf0"):
    """Point the 'initial' constraint's mineral volume fraction at the dataset."""
    deck, n = re.subn(rf"^(CONSTRAINT initial\n.*?^\s*{mineral}\s+)\S+", lambda m: f"{m.group(1)}DATASET {name}",
                      deck, count=1, flags=re.S | re.M)
    assert n == 1, f"{mineral} volume fraction in CONSTRAINT initial not found"
    deck = deck.replace("END_SUBSURFACE", f"DATASET {name}\n  FILENAME {h5_name}\nEND\n\nEND_SUBSURFACE", 1)
    return deck


def set_constant_fill(deck, mineral, vf):
    deck, n = re.subn(rf"^(CONSTRAINT initial\n.*?^\s*{mineral}\s+)\S+", lambda m: f"{m.group(1)}{vf:.6g}d0",
                      deck, count=1, flags=re.S | re.M)
    assert n == 1, f"{mineral} volume fraction in CONSTRAINT initial not found"
    return deck


def n_fracture_cells(run_dir):
    """Fracture cells of a graph UGE = rows of altered_cells_df.dat with row_type 'internal'."""
    f = Path(run_dir) / "altered_cells_df.dat"
    if not f.exists():
        return None
    rows = f.read_text().splitlines()[1:]
    return sum(1 for r in rows if r.split()[5:6] == ["internal"])
