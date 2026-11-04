#!/usr/bin/env python3
"""
Readable names for reactive-run folders, used by every runner and analysis
script so folder names and code cannot drift apart.

A run folder is  <chemistry>__<model>__<case>,  for example
  gypsum__uncorrected_graph__quasi_steady
  quartz__dfn__to_5My_porosity0.10

Short codes (what the scripts pass around) -> readable names:
  chemistry  gyponly gypcal qtz acid co2cal
  model      dfn graph_raw graph_alpha graph_geo graph_mch graph_mchd graph_mchf graph_mc1 graph_mc4h graph_mc2h
  case       s1 k1e-5 k1e-6 qs my5 my5p01 pbc r100 (others pass through unchanged)

Shell use:  python3 run_names.py MODE MODEL TAG   ->  prints the folder name
"""
from __future__ import annotations

import sys
from pathlib import Path

CHEMISTRY = {"gyponly": "gypsum", "gypcal": "gypsum_calcite", "qtz": "quartz", "acid": "acid_calcite",
             "co2cal": "co2_calcite"}
MODEL = {"dfn": "dfn", "graph_raw": "uncorrected_graph", "graph_alpha": "alpha_corrected_graph",
         "graph_geo": "geometric_graph", "graph_mch": "multicell_graph",
         "graph_mchd": "multicell_graph_deadend_cells", "graph_mchf": "multicell_graph_flush_cells",
         # resolution series (multiport_lowda): one port per intersection, sub-ports of 4h and 2h
         "graph_mc1": "multicell_graph_1port", "graph_mc4h": "multicell_graph_4h", "graph_mc2h": "multicell_graph_2h", "graph_mc4hd": "multicell_graph_4h_deadend_cells"}
CASE = {"s1": "template_rate", "k1e-5": "rate_x1e-5", "k1e-6": "rate_x1e-6", "qs": "quasi_steady",
        "my5": "to_5My_porosity0.10", "my5p01": "to_5My_porosity0.01", "pbc": "paper_rate",
        "r100": "100x_paper_rate"}
# Track D sealing proxies (apply_sealing_proxy.py): derived multiport folders model_graph_mc4hd_<suffix>, run folders
# ...__multicell_graph_4h_deadend_cells_<suffix>__...  (e.g. graph_mc4hd_sv0.1, graph_mc4hd_sv0.1n3, graph_mc4hd_pc0.1)
SEALING_PROXY = ("sv0.3", "sv0.1", "sv0.03", "svh", "n3", "sv0.1n3", "sv0.03n6", "pc0.05", "pc0.1", "pc0.2", "pcall0.1",
                 "sv0.1pc0.2", "sv0.03pc0.2", "svhn3", "svhpc0.2",
                 "pp", "ppr")   # Track D2: per-port throat fractions (sealing_port_enrichment.py, --sv-per-port)
MODEL.update({f"graph_mc4hd_{s}": f"multicell_graph_4h_deadend_cells_{s}" for s in SEALING_PROXY})
MODEL.update({f"graph_mchd_{s}": f"multicell_graph_deadend_cells_{s}" for s in ("sv0.1", "svh")})   # throat split on sub-ports at h
# Track E (1 Nov) cheaper in-fracture topologies of mc4hd (build_multicell_graph.py --topology / --sparsify-mode threshold):
# graph_mc4hdhub (star per fracture), graph_mc4hdknn<k> (k strongest couplings), graph_mc4hdkh<k> (knn + hub remainder),
# graph_mc4hd_sp<eps> (threshold sparsification); model folders model_<code>
MODEL.update({"graph_mc4hdhub": "multicell_graph_4h_deadend_cells_hub"})
MODEL.update({f"graph_mc4hdknn{k}": f"multicell_graph_4h_deadend_cells_knn{k}" for k in (2, 3, 4, 6)})
MODEL.update({f"graph_mc4hdkh{k}": f"multicell_graph_4h_deadend_cells_knnhub{k}" for k in (1, 2, 3, 4)})
MODEL.update({f"graph_mc4hd_sp{e}": f"multicell_graph_4h_deadend_cells_sp{e}" for e in ("0.01", "0.03", "0.1", "0.3")})
# fitted sparse patterns (--topology knnfit): Delaunay + spanning tree (graph_mc4hddel), k strongest + tree (graph_mc4hdfit<k>)
MODEL.update({"graph_mc4hddel": "multicell_graph_4h_deadend_cells_delfit"})
# Track E3 (1 Nov): the frozen Delaunay model, built with the round-off guard (--lowmem --fit-p0-min-span 1e-12)
MODEL.update({"graph_mc4hddelg": "multicell_graph_4h_deadend_cells_delfitg"})
MODEL.update({f"graph_mc4hdfit{k}": f"multicell_graph_4h_deadend_cells_knnfit{k}" for k in (2, 3, 4, 6)})
# Track J (2 Nov): targeted throat split (docs/clog_probe/targeted_split.py): only the flagged lines' sub-ports split, h-band S;
# flag source s = throat surrogate, m = leave-one-seed-out GBT, r = post-hoc t_fill rule
MODEL.update({f"graph_mc4hd_tj{s}": f"multicell_graph_4h_deadend_cells_tj{s}" for s in ("s", "m", "r")})
MODEL_CODE = {v: k for k, v in MODEL.items()}


def run_dir_name(mode, model, tag):
    return f"{CHEMISTRY.get(mode, mode)}__{MODEL.get(model, model)}__{CASE.get(tag, tag)}"


def run_dir(seed_dir, mode, model, tag):
    return Path(seed_dir) / run_dir_name(mode, model, tag)


def parse_run_dir(name):
    """Inverse of run_dir_name: (mode, model, tag) short codes."""
    chem, model, case = name.split("__")
    inv = lambda d, v: {b: a for a, b in d.items()}.get(v, v)  # noqa: E731
    return inv(CHEMISTRY, chem), inv(MODEL, model), inv(CASE, case)


if __name__ == "__main__":
    print(run_dir_name(*sys.argv[1:4]))
