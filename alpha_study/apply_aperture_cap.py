#!/usr/bin/env python3
"""Cap the effective aperture a fracture cell can reach under the k-phi law, by giving large-aperture
fractures a smaller PERMEABILITY_POWER (input-file change only; PFLOTRAN has no k-phi ceiling keyword).

With k = k0 (phi/phi_ref)^n and k0 = b_h^2/12, the fully dissolved cell (phi = 1) carries the flow of a
parallel plate of aperture b_T = (12 k b_h)^(1/3) = b_h (1/phi_ref)^(n/3).  Requiring b_T <= b_cap gives
    n_f = min(n, 3 ln(b_cap / b_h) / ln(1 / phi_ref)),   floored at 0 (a fracture already wider than the cap
    keeps its initial permeability).
Every cell keeps its initial permeability (the factor is 1 at phi = phi_ref whatever n), so the unreacted
flow field and the Da are unchanged; only the growth of the wide fractures is limited.  Fractures are binned
by n_f (steps of 1/8) into extra MATERIAL_PROPERTY blocks, each assigned through a REGION LIST and a STRATA
block after the default one.

  python3 apply_aperture_cap.py RUN_DIR --cap-um 1000
Writes RUN_DIR/single_stage.in in place and RUN_DIR/aperture_cap.json (bins, counts, b_h statistics).
"""
import argparse
import json
import re
import sys
from pathlib import Path

import h5py
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "physics_upscaling"))
from write_corrected_bigrafv_inputs import read_uge  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir", type=Path)
    ap.add_argument("--cap-um", type=float, required=True, help="maximum effective aperture b_T (micrometres)")
    ap.add_argument("--step", type=float, default=0.125, help="binning step of the exponent")
    ap.add_argument("--deck", default="single_stage.in")
    a = ap.parse_args()
    run = a.run_dir
    deck_path = run / a.deck
    deck = deck_path.read_text()
    m = re.search(r"^MATERIAL_PROPERTY (\S+)\n  ID (\d+)\n(.*?)^END\n", deck, re.S | re.M)
    assert m, "default MATERIAL_PROPERTY block not found"
    mat_name, mat_id, body = m.group(1), int(m.group(2)), m.group(3)
    n0 = float(re.search(r"PERMEABILITY_POWER\s+([\d.eE+-]+)", body).group(1))
    phi_ref = float(re.search(r"POROSITY\s+([\d.eE+-]+)", body).group(1).replace("d", "e"))

    nf = sum(1 for _ in open(run / "polygons.dat")) - 1
    cells, _ = read_uge(run / "full_mesh_vol_area.uge")
    with h5py.File(run / "dfn_properties.h5") as h:
        ids = np.asarray(h["Cell Ids"]).astype(int)
        k = np.asarray(h["Permeability"], float)
    k0 = np.full(len(cells), np.nan)
    k0[ids - 1] = k
    bh = np.sqrt(12 * k0[:nf])                                   # dfnWorks hydraulic aperture = UGE thickness
    cap = a.cap_um * 1e-6
    n_f = np.clip(3 * np.log(cap / bh) / np.log(1 / phi_ref), 0, n0)
    n_bin = np.floor(n_f / a.step) * a.step                      # round down: never exceeds the cap
    bins = sorted(set(np.round(n_bin[n_bin < n0], 6)))
    blocks, regions, strata, info = [], [], [], []
    for j, nb in enumerate(bins, 1):
        sel = np.where(np.isclose(n_bin, nb))[0] + 1              # 1-based cell ids
        name = f"{mat_name}_cap{j}"
        b2 = re.sub(r"PERMEABILITY_POWER\s+[\d.eE+-]+", f"PERMEABILITY_POWER {nb:g}", body)
        blocks.append(f"MATERIAL_PROPERTY {name}\n  ID {mat_id + j}\n{b2}END\n")
        ids_txt = "\n".join(f"    {i}" for i in sel)                   # PFLOTRAN: one CELL_ID per line
        regions.append(f"REGION cap{j}\n  LIST\n{ids_txt}\n  /\nEND\n")
        strata.append(f"STRATA\n  REGION cap{j}\n  MATERIAL {name}\nEND\n")
        info.append(dict(bin=j, n=float(nb), cells=int(len(sel)), bh_um_min=float(bh[sel - 1].min() * 1e6), bh_um_max=float(bh[sel - 1].max() * 1e6),
                         bT_end_um_max=float((bh[sel - 1] * (1 / phi_ref) ** (nb / 3)).max() * 1e6)))
    # insert: material blocks after the default one, regions before the first REGION, strata after the default STRATA
    deck = deck[:m.end()] + "\n" + "\n".join(blocks) + deck[m.end():]
    i = deck.index("\nREGION ")
    deck = deck[:i + 1] + "\n".join(regions) + "\n" + deck[i + 1:]
    s = re.search(r"^STRATA\n.*?^END\n", deck, re.S | re.M)
    deck = deck[:s.end()] + "\n" + "\n".join(strata) + deck[s.end():]
    deck_path.write_text(deck)
    summary = dict(cap_um=a.cap_um, phi_ref=phi_ref, n_default=n0, n_fracture_cells=nf, cells_capped=int((n_bin < n0).sum()),
                   cells_frozen=int((n_bin <= 0).sum()), bh_um_p50=float(np.median(bh) * 1e6), bh_um_max=float(bh.max() * 1e6),
                   bT_end_um_max_uncapped=float(bh.max() * (1 / phi_ref) ** (n0 / 3) * 1e6), bins=info)
    (run / "aperture_cap.json").write_text(json.dumps(summary, indent=1))
    print(f"{run.name}: cap {a.cap_um:g} um, {summary['cells_capped']} of {nf} cells capped ({summary['cells_frozen']} frozen), {len(bins)} extra materials")


if __name__ == "__main__":
    main()
