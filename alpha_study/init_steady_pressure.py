#!/usr/bin/env python3
"""
Start a rate-controlled reactive run from its steady pressure field.

On the dense km graphs (~80 neighbours per fracture) PFLOTRAN's flow time step
spends hundreds of expensive steps pressurising the network from the
hydrostatic initial condition before it reaches the transport step size.  This
writes the steady pressure, hydrostatic + dynamic (direct TPFA solve with the
injection at the inlet manifold and the outflow faces at the seepage pressure,
analyze_km_dissolution_patterns.solve), to initial_pressure.h5 and points the deck's initial
flow condition at it.  The flow problem is unchanged; only its start is.

  python3 init_steady_pressure.py RUN_DIR
"""
import json
import re
import sys
from pathlib import Path

import h5py
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE / "physics_upscaling")]
from analyze_km_dissolution_patterns import solve  # noqa: E402
from compute_keff_tpfa import read_uge  # noqa: E402

RHO, G = 997.05, 9.8068


def main(run):
    run = Path(run)
    deck = (run / "single_stage.in").read_text()
    p0 = float(re.search(r"FLOW_CONDITION initial\n.*?LIQUID_PRESSURE ([0-9.eEd+-]+)", deck, re.S).group(1).replace("d", "e"))
    sched = json.loads((run / "single_stage.in.schedule.json").read_text())
    cells, conns = read_uge(run / "full_mesh_vol_area.uge")
    with h5py.File(run / "dfn_properties.h5") as h:
        ids = np.asarray(h["Cell Ids"]).astype(int)
        k = np.full(len(cells), np.nan)
        k[ids - 1] = np.asarray(h["Permeability"], float)
    k[np.isnan(k)] = np.nanmax(k)
    _, _, _, _, p_dyn = solve(run, cells, conns, k, sched["rate_m3y"] / 3.15576e7, return_pressure=True)
    gravity_off = re.search(r"^\s*GRAVITY 0\.d0 0\.d0 0\.d0", deck, re.M) is not None
    p = p0 + p_dyn if gravity_off else p0 - RHO * G * cells[:, 3] + p_dyn
    with h5py.File(run / "initial_pressure.h5", "w") as h:
        h["Cell Ids"] = np.arange(1, len(cells) + 1, dtype=np.int32)
        h["initial_pressure"] = p
    new = ("FLOW_CONDITION initial\n  TYPE\n    LIQUID_PRESSURE DIRICHLET\n  /\n  LIQUID_PRESSURE DATASET initial_pressure\nEND\n\n"
           "DATASET initial_pressure\n  FILENAME initial_pressure.h5\nEND\n")
    deck, n = re.subn(r"^FLOW_CONDITION initial\n.*?^END\n", new, deck, count=1, flags=re.S | re.M)
    assert n == 1
    (run / "single_stage.in").write_text(deck)
    print(f"{run.name}: steady start, dynamic pressure at manifold {p_dyn.max():.4g} Pa")


if __name__ == "__main__":
    main(sys.argv[1])
