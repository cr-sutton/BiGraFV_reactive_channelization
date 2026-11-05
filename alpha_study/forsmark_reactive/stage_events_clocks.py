# Stage events (PR_pore minimum, outlet > 5 %, PR_V minimum, breakthrough = outlet >= 50 %) per run on every clock:
# pv, t_cap (theoretical cap), dissolved (fraction of the gypsum inventory = measured-cap clock), tau_H (Hyman Delta V / initial
# pore volume), tau_F (Delta V / initial fracture volume = phi0 x tau_H).  Window t_cap <= 3.  python3 forsmark_reactive/stage_events_clocks.py
import numpy as np, pandas as pd
d = pd.read_csv("phase1/phase1_mechanism.csv")
PHI0 = {"phase1": 0.1, "phase2_phi005": 0.05, "phase2_co3lo": 0.1, "phase3_phi0182": 0.182, "phase3_rate01": 0.1, "phase3_rate10": 0.1}
d["phi0"] = d.tag.map(PHI0)
d["tau_F"] = d.tau_H * d.phi0          # Delta V / initial FRACTURE (cell) volume
rows = []
for key, g in d.groupby(["tag", "mode", "p32", "sigma", "seed"]):
    g = g.sort_values("k").reset_index(drop=True)
    g = g[g.t_cap <= 3.0].reset_index(drop=True) if True else g
    ev = {}
    ev["PRpore_min"] = g.pr_pore.idxmin()
    ev["PRV_min"] = g.pr_frac.idxmin()
    o = g.index[g.outlet_diss > 0.05]; ev["outlet5"] = o[0] if len(o) else None
    o = g.index[g.outlet_diss >= 0.5]; ev["breakthrough"] = o[0] if len(o) else None
    for e, i in ev.items():
        if i is None: continue
        r = g.loc[i]
        rows.append(dict(zip(["tag","mode","p32","sigma","seed"], key), event=e, pv=r.pv, t_cap=r.t_cap, dissolved=r.dissolved, tau_H=r.tau_H, tau_F=r.tau_F))
e = pd.DataFrame(rows)
e.to_csv("phase1/stage_events_clocks.csv", index=False)
q = lambda s: f"{s.median():.3g} [{s.quantile(.25):.3g}-{s.quantile(.75):.3g}]"
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 30)
for ev in ["PRpore_min", "outlet5", "PRV_min", "breakthrough"]:
    x = e[e.event == ev]
    t = x.groupby(["tag", "mode"]).agg(n=("pv", "size"), pv=("pv", q), t_cap=("t_cap", q), dissolved=("dissolved", q), tau_H=("tau_H", q), tau_F=("tau_F", q))
    print("==", ev); print(t.to_string())
# Phase 1 per P32
x = e[(e.tag == "phase1")]
print(x.groupby(["event", "mode", "p32"])[["t_cap", "dissolved", "tau_H"]].median().round(3).unstack("p32").to_string())
