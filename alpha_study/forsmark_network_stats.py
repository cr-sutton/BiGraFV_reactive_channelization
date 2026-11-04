#!/usr/bin/env python3
"""
Structure of a graph-only network build (dfnGen_output of build_km_graph_network.py):
fracture count, intersections, inlet/outlet fractures and how many separate
inlet -> outlet paths the fracture graph holds.

  python3 forsmark_network_stats.py NET_DIR [NET_DIR ...]   (writes NET_DIR/network_stats.json)

Paths are counted on the fracture graph (vertex = fracture, edge = intersection),
with a super source joined to every left-boundary fracture and a super sink to
every right-boundary one:
  node_disjoint_paths  paths sharing no fracture (Menger: the fewest fractures
                       whose removal disconnects inlet from outlet)
  edge_disjoint_paths  paths sharing no intersection
  backbone_fraction    share of fractures left after repeatedly removing dead
                       ends (degree-1 fractures that touch no boundary), the
                       topological primary network of Hyman et al. (2024 G-cubed)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import networkx as nx


def fracture_graph(gen: Path):
    G = nx.Graph()
    for i, line in enumerate((gen / "connectivity.dat").read_text().splitlines(), start=1):
        G.add_node(i)
        G.add_edges_from((i, int(j)) for j in line.split())
    ids = lambda f: {int(t) for t in (gen / f).read_text().split()}
    return G, ids("left.dat"), ids("right.dat")


def stats(net: Path):
    gen = net / "model_graph_raw" / "dfnGen_output"
    G, left, right = fracture_graph(gen)
    H = G.copy()
    H.add_edges_from(("s", f) for f in left)
    H.add_edges_from((f, "t") for f in right)
    core = G.copy()
    keep = left | right
    while True:
        dead = [n for n, d in core.degree() if d <= 1 and n not in keep]
        if not dead:
            break
        core.remove_nodes_from(dead)
    degrees = [d for _, d in G.degree()]
    s = dict(n_fractures=G.number_of_nodes(), n_intersections=G.number_of_edges(),
             mean_degree=sum(degrees) / len(degrees), n_inlet_fractures=len(left), n_outlet_fractures=len(right),
             node_disjoint_paths=nx.node_connectivity(H, "s", "t"),
             edge_disjoint_paths=nx.edge_connectivity(H, "s", "t"),
             backbone_fraction=core.number_of_nodes() / G.number_of_nodes(),
             n_dead_end_fractures=G.number_of_nodes() - core.number_of_nodes())
    summ = net / "flow_summary.json"
    if summ.exists():
        s.update({k: v for k, v in json.loads(summ.read_text()).items() if k in ("graph_nodes", "graph_edges", "Q_graph_raw")})
    (net / "network_stats.json").write_text(json.dumps(s, indent=2))
    return s


if __name__ == "__main__":
    for d in sys.argv[1:]:
        print(Path(d).name, json.dumps(stats(Path(d))))
