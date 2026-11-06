#!/usr/bin/env python3
"""
Single-stage, rate-controlled reactive deck (one injection water from t = 0),
following the coupled-injection design of the gypsum/calcite CO2-storage study
and the quartz-dissolution protocol (run, freeze the reacted state at
checkpoints, probe it with separate flow + tracer solves).

Built from constant_chemistry_small_kbias/gyp_and_calc.in by text edits only;
kinetics, database, characteristic curves are unchanged unless a rate
multiplier is requested.

  --mode gypcal   gypsum-saturated resident water, original Na2CO3 injection
                  water: gypsum dissolution coupled to calcite precipitation
  --mode gyponly  calcite removed from the chemistry (mineral list, kinetics,
                  constraints); dilute injection water: gypsum dissolution only

Checkpoint times are set from target fractions of the total gypsum inventory
dissolved (tau_d = dissolved / initial, the regimes-paper time proxy), using
the injection capacity c_cap (mol gypsum per m^3 injected water; measured
16.5 mol/m^3 for dilute water in the TPL graph pilot).  Stopping at tau_d well
below the accessible inventory keeps part of every flow path undissolved.
Pore volumes injected (tau = V/Q) are recorded alongside.

Writes <out> and <out>.schedule.json (checkpoint times, tau_d, tau, VTK index).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "physics_upscaling"))
from deck_staged_reactive_base import TEMPLATE, inert_graph_boundary_cells, rate_controlled  # noqa: E402
from write_corrected_bigrafv_inputs import read_uge  # noqa: E402

GYPSUM_VF0 = 0.77                 # template initial constraint
GYPSUM_MOLAR_VOLUME = 74.69e-6    # m^3/mol, hanford.dat
C_CAP = {"gyponly": 16.5, "gypcal": 116.5}   # gypcal: solubility + 0.1 M CO3 (Ca sink to calcite), an estimate

RESIDENT = ("    H+     7.d0  pH\n    Na+    1.d-3  T\n    CO3--  1.d-10  T\n"
            "    Ca++   1.d-3  M Gypsum\n    SO4--  1.5d-2  T\n")
INJECTION = {
    "gypcal": "    H+     11.11d0  pH\n    Na+    0.2d0  T\n    CO3--  0.1d0  T\n    Ca++   1.d-10  M Calcite\n    SO4--  1.d-10  T\n",
    "gyponly": "    H+     7.d0  pH\n    Na+    1.d-3  T\n    CO3--  1.d-10  T\n    Ca++   1.d-10  T\n    SO4--  1.d-10  T\n",
}
C_SAT_DILUTE = 16.5               # mol/m^3 gypsum capacity of dilute water (gyponly C_CAP)


def set_injected_co3(co3):
    """gypcal: injected total carbonate co3 (mol/L).  Na+ = 2 co3 (Na2CO3, as the template's 0.2/0.1);
    the template pH 11.11 is kept.  Returns the matching default c_cap = 16.5 + 1000 co3 mol/m^3."""
    if co3 <= 0:   # no-carbonate control: trace totals (template's 1e-10), and Ca as a total, since Ca at calcite
        # equilibrium with no carbonate is unbounded (Ksp / CO3)
        INJECTION["gypcal"] = INJECTION["gypcal"].replace("Ca++   1.d-10  M Calcite", "Ca++   1.d-10  T")
        co3_txt, na_txt = "1.d-10", "2.d-10"
    else:
        co3_txt, na_txt = f"{co3:.6e}", f"{2 * co3:.6e}"
    INJECTION["gypcal"] = INJECTION["gypcal"].replace("Na+    0.2d0  T", f"Na+    {na_txt}  T").replace(
        "CO3--  0.1d0  T", f"CO3--  {co3_txt}  T")
    return C_SAT_DILUTE + 1000.0 * co3


def set_injection_charge_balance():
    """gypcal: injected pH from charge balance (PFLOTRAN constraint type Z on H+) instead of the fixed pH 11.11;
    the value 1e-11 is only the initial guess of free H+.  Totals (Na = 2 CO3, CO3, SO4) and Ca at calcite
    equilibrium are unchanged.  Added 1 Nov 2026 for the Q3 test (Track G); default decks are untouched."""
    old = "    H+     11.11d0  pH\n"
    assert old in INJECTION["gypcal"]
    INJECTION["gypcal"] = INJECTION["gypcal"].replace(old, "    H+     1.d-11  Z\n")


def gypsum_inventory_mol(uge):
    cells, _ = read_uge(uge)
    return float(cells[:, 4].sum()) * GYPSUM_VF0 / GYPSUM_MOLAR_VOLUME


def build(mode, t_end, dt, vtk_times, checkpoint_times, k_gypsum_mult=1.0, k_calcite_mult=1.0):
    s = TEMPLATE.read_text()

    def sub(pattern, repl, flags=re.S | re.M):
        nonlocal s
        s, n = re.subn(pattern, repl, s, count=1, flags=flags)
        assert n == 1, f"edit failed: {pattern[:50]}"

    sub(r"^CONSTRAINT initial\n  CONCENTRATIONS\n.*?  /\n", "CONSTRAINT initial\n  CONCENTRATIONS\n" + RESIDENT + "  /\n")
    # w0 = resident water; rate_controlled() inserts the mineral-free well constraint before it
    sub(r"^CONSTRAINT injection_constraint\n.*?END\n",
        "CONSTRAINT w0\n  CONCENTRATIONS\n" + RESIDENT + "  /\nEND\n\n"
        "CONSTRAINT injection\n  CONCENTRATIONS\n" + INJECTION[mode] + "  /\nEND\n")
    sub(r"^TRANSPORT_CONDITION inflow_conc\n.*?^END\n",
        "TRANSPORT_CONDITION inflow_conc\n  TYPE ZERO_GRADIENT\n  CONSTRAINT_LIST\n    0.d0 injection\n  /\nEND\n")
    if k_gypsum_mult != 1.0:
        sub(r"(    Gypsum\n.*?RATE_CONSTANT )(\S+)", lambda m: f"{m.group(1)}{float(m.group(2)) * k_gypsum_mult:.12e}")
    if k_calcite_mult != 1.0:   # anchored: the MINERALS list also holds a "    Calcite" line
        sub(r"(^    Calcite\n(?:      [^\n]*\n)*?      RATE_CONSTANT )(\S+)",
            lambda m: f"{m.group(1)}{float(m.group(2)) * k_calcite_mult:.12e}")
    tt = [f"{t:.6e}" for t in vtk_times]          # PFLOTRAN reads <= 480 characters per line: wrap with "\\"
    times = " \\\n    ".join(" ".join(tt[i:i + 8]) for i in range(0, len(tt), 8))
    sub(r"^TIME\n.*?^END\n", f"TIME\n    MAXIMUM_TIMESTEP_SIZE {dt:.1e} y\n    FINAL_TIME {t_end:.6e} y\nEND\n")
    sub(r"^OUTPUT\n", f"OUTPUT\n  TIMES y {times}\n")
    sub(r"^  CHECKPOINT\n    FORMAT HDF5\n  /\n",
        "  CHECKPOINT\n    TIMES y " + " ".join(f"{t:.6e}" for t in checkpoint_times) + "\n    FORMAT HDF5\n  /\n")
    return s


def strip_calcite(s):
    """Gypsum-only chemistry: drop calcite from the mineral list, kinetics and
    every constraint (aqueous carbonate species stay; nothing precipitates)."""
    for pat in (r"^     Calcite\n", r"^    Calcite\n      SURFACE_AREA_FUNCTION.*?^    /\n",
                r"^    Calcite +0\.0?d0 +200 +m\^2/m\^3[^\n]*\n"):
        s, n = re.subn(pat, "", s, flags=re.S | re.M)
        assert n >= 1, f"calcite strip failed: {pat}"
    assert "Calcite" not in s, "calcite left in gypsum-only deck"
    return s


def well_fill_injection(deck, mode):
    """A second constraint/transport condition for the manifold cell only: the injection water (Ca as a total,
    no mineral equilibrium), so the well does not start with gypsum-saturated resident water.  Inlet and outlet
    boundary cells keep well_initial."""
    m = re.search(r"CONSTRAINT well_initial\n(.*?)\nEND\n", deck, re.S)
    assert m
    blk = m.group(0)
    inj = INJECTION[mode].replace("Ca++   1.d-10  M Calcite", "Ca++   1.d-10  T")
    blk2 = re.sub(r"(  CONCENTRATIONS\n)(.*?)(  /\n)", lambda mm: mm.group(1) + inj + mm.group(3), blk, count=1,
                  flags=re.S).replace("CONSTRAINT well_initial", "CONSTRAINT well_fill")
    deck = deck[: m.end()] + "\n" + blk2 + deck[m.end():]
    tc = re.search(r"TRANSPORT_CONDITION well_initial\n(.*?)\nEND\n", deck, re.S)
    assert tc
    deck = deck[: tc.end()] + "\n" + tc.group(0).replace("well_initial", "well_fill") + deck[tc.end():]
    old = "  TRANSPORT_CONDITION well_initial\n  REGION well\n"
    assert old in deck
    return deck.replace(old, "  TRANSPORT_CONDITION well_fill\n  REGION well\n")


def inert_helper_cells(deck, run_dir):
    """Helper cells (every cell after the n_fractures polygon cells: inlet manifold and the boundary helper
    cells on all six domain faces) hold no rock.  With minerals in them they clog: a top-face helper cell of
    2e-5 m3 reached calcite VF 5.8 and killed the coupled cubic run at 221 y (28 Oct 2026).  The inlet/outlet
    coordinate boxes of --inert-boundary-x miss helpers whose centre is not within 1e-3 m of the face plane
    and all of the y/z-face helpers, so this lists them by cell id (explicit-grid CELLS file)."""
    import re as _re
    run_dir = Path(run_dir)
    n_poly = int(open(run_dir / "polygons.dat").readline().split()[-1]) if False else sum(1 for _ in open(run_dir / "polygons.dat")) - 1
    with open(run_dir / "full_mesh_vol_area.uge") as fh:
        n_cells = int(fh.readline().split()[1])
    ids = list(range(n_poly + 1, n_cells + 1))
    # explicit grids reject CELLS files in REGION; the inline LIST (one cell id per line) is accepted
    region = "REGION helper_cells\n  LIST\n" + "".join(f"    {i}\n" for i in ids) + "  /\nEND\n\n"
    ic = "INITIAL_CONDITION\n  FLOW_CONDITION initial\n  TRANSPORT_CONDITION well_initial\n  REGION helper_cells\n/\n\n"
    # with a fixed calcite area, calcite would still nucleate in the mineral-free helper cells (2e-5 m3) and
    # fill them past VF 1 (8.8 observed); give the helper constraints zero calcite area
    for cname in ("well_initial", "well_fill"):
        blk = _re.search(r"CONSTRAINT %s\n.*?\nEND\n" % cname, deck, _re.S)
        if blk:
            fixed = _re.sub(r"(Calcite\s+0\.d0\s+)[0-9.de+-]+(\s+m\^2/m\^3)", r"\g<1>0.d0\2", blk.group(0))
            deck = deck.replace(blk.group(0), fixed)
    deck, n1 = _re.subn(r"^REGION well\n", region + "REGION well\n", deck, count=1, flags=_re.M)
    deck, n2 = _re.subn(r"^SOURCE_SINK inflow\n", ic + "SOURCE_SINK inflow\n", deck, count=1, flags=_re.M)
    assert n1 == 1 and n2 == 1, "inert helper edit failed (rate-controlled deck required)"
    return deck


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("gypcal", "gyponly"), required=True)
    ap.add_argument("--well-fill-injection", action="store_true",
                    help="start the inlet manifold cell full of the injection water (it is a well) instead of the "
                         "resident water; on the 500 m graphs the coupled gypcal case otherwise diverges at step 1 "
                         "(the 1e-6 m^3 manifold turns over ~50x in the default 1 s first step)")
    ap.add_argument("--initial-dt", type=float, default=None, help="INITIAL_TIMESTEP_SIZE (y); 1e-11 lets the coupled case start")
    ap.add_argument("--min-porosity", type=float, default=None,
                    help="CHEMISTRY MINIMUM_POROSITY: floor on the void fraction when precipitation fills a cell (clogging)")
    ap.add_argument("--perm-min-scale", type=float, default=None,
                    help="PERMEABILITY_MIN_SCALE_FACTOR: floor on k/k0 so a clogged cell keeps a tiny permeability")
    ap.add_argument("--calcite-fixed-area", action="store_true",
                    help="gypcal: keep the calcite reactive area at its initial 200 m^2/m^3 instead of VOLUME_FRACTION_RATIO; "
                         "with a zero initial volume fraction that function scales the area by (VF/eps)^(2/3) and reached "
                         "1e13 m^2/m^3 on the 500 m graph, which made the chemistry too stiff to step")
    ap.add_argument("--uge", type=Path, required=True, help="UGE of the reference model (sets the gypsum inventory; use the same for all models)")
    ap.add_argument("--rate", type=float, required=True, help="injection rate (m^3/y)")
    ap.add_argument("--manifold-json", type=Path, required=True)
    ap.add_argument("--dissolved-fractions", type=float, nargs="+", default=[0.05, 0.15, 0.30, 0.45])
    ap.add_argument("--c-cap", type=float, default=None, help="mol gypsum dissolved per m^3 injected (default by mode)")
    ap.add_argument("--dt", type=float, default=1e-5, help="max time step (y); 1e-3 broke Ca/SO4 closure")
    ap.add_argument("--n-extra-vtk", type=int, default=8, help="evenly spaced VTK between checkpoints, for inspection")
    ap.add_argument("--log-vtk", action="store_true",
                    help="space the extra VTK times logarithmically from t_end/1e4 to t_end instead of evenly")
    ap.add_argument("--k-gypsum-mult", type=float, default=1.0, help="gypsum rate-constant multiplier (Da sweep)")
    ap.add_argument("--k-calcite-mult", type=float, default=1.0,
                    help="gypcal: calcite rate-constant multiplier (Fogler number Fo = k_prec/k_diss sweep)")
    ap.add_argument("--inj-co3", type=float, default=None, metavar="MOL_PER_L",
                    help="gypcal: injected total CO3-- (template 0.1); Na+ set to 2x (Na2CO3), pH 11.11 kept, "
                         "default c_cap becomes 16.5 + 1000 x CO3 mol/m^3")
    ap.add_argument("--inj-charge-balance", action="store_true",
                    help="gypcal: injected pH from charge balance on H+ (constraint Z) instead of pH 11.11")
    ap.add_argument("--inj-ph", type=float, default=None,
                    help="gypcal: fixed injected pH instead of 11.11 (Hyman et al. 2024 IJGGC Table 2: 11.39 for 0.5 M CO3, 1.0 M Na)")
    ap.add_argument("--inert-boundary-x", type=float, nargs=2, default=None, metavar=("X_IN", "X_OUT"))
    ap.add_argument("--gypsum-area-porosity-power", type=float, default=None, metavar="P",
                    help="gypsum surface area also scales with (porosity/porosity0)^P (SURFACE_AREA_FUNCTION POROSITY_VOLUME_FRACTION_RATIO): "
                         "a cell closing by re-precipitation stops reacting instead of overshooting past zero porosity")
    ap.add_argument("--inert-helper-cells", action="store_true",
                    help="every UGE cell after the fracture cells (manifold and boundary helper cells on all six faces) starts mineral-free; "
                         "needs polygons.dat and full_mesh_vol_area.uge beside --out")
    ap.add_argument("--direct-transport", action="store_true")
    ap.add_argument("--gypsum-vf0", type=float, default=GYPSUM_VF0, help="mean initial gypsum volume fraction")
    ap.add_argument("--material-porosity", type=float, default=None,
                    help="reference porosity of the permeability update (default: template 0.9; use 1 - vf0 to start at the h5 k)")
    ap.add_argument("--perm-power", type=float, default=1.0, help="PERMEABILITY_POWER n, k ~ phi^n (3 = cubic law)")
    ap.add_argument("--perm-crit-por", type=float, default=None,
                    help="PERMEABILITY_CRITICAL_POROSITY phi_c (opt-in; may be negative): k/k0 = ((phi-phi_c)/(phi0-phi_c))^n")
    ap.add_argument("--fill-sigma", type=float, default=0.0, help="ln-std of per-fracture initial porosity (0 = uniform fill)")
    ap.add_argument("--fill-seed", type=int, default=1)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    c_cap_default = C_CAP[a.mode]
    if a.mode == "gyponly" and (a.k_calcite_mult != 1.0 or a.inj_co3 is not None):
        ap.error("--k-calcite-mult and --inj-co3 apply to --mode gypcal only")
    if a.inj_co3 is not None:
        c_cap_default = set_injected_co3(a.inj_co3)
    if a.inj_charge_balance:
        if a.mode != "gypcal":
            ap.error("--inj-charge-balance applies to --mode gypcal only")
        set_injection_charge_balance()
    if a.inj_ph is not None:
        if a.mode != "gypcal" or a.inj_charge_balance:
            ap.error("--inj-ph applies to --mode gypcal without --inj-charge-balance")
        INJECTION["gypcal"] = INJECTION["gypcal"].replace("    H+     11.11d0  pH\n", f"    H+     {a.inj_ph:.4f}d0  pH\n")

    cells, _ = read_uge(a.uge)
    vf_cells = np.full(len(cells), a.gypsum_vf0)
    if a.fill_sigma > 0:
        from deck_heterogeneity import fill_dataset, n_fracture_cells
        nf = n_fracture_cells(a.out.parent) or len(cells)
        vf_cells = fill_dataset(read_uge(a.out.parent / "full_mesh_vol_area.uge")[0], nf, 1 - a.gypsum_vf0,
                                a.fill_sigma, a.fill_seed, a.out.parent / "mineral_vf0.h5")[: len(cells)]
    inv = float((cells[:, 4] * vf_cells).sum()) / GYPSUM_MOLAR_VOLUME
    c_cap = a.c_cap or c_cap_default
    t_chk = [f * inv / (a.rate * c_cap) for f in a.dissolved_fractions]
    t_end = t_chk[-1]
    extra = np.linspace(0, t_end, a.n_extra_vtk + 2)[1:-1]
    if a.log_vtk:
        extra = np.geomspace(t_end * 1e-4, t_end, a.n_extra_vtk + 1)[:-1]
    vtk_times = sorted(set(np.round(np.r_[t_chk, extra], 10)))
    deck = build(a.mode, t_end, a.dt, vtk_times, t_chk, a.k_gypsum_mult, a.k_calcite_mult)
    box = json.loads(a.manifold_json.read_text())["region_box"]
    deck = rate_controlled(deck, a.rate, box)
    deck = re.sub(r"^    Tracer\d +1\.d-20  T\n", "", deck, flags=re.M)   # well_initial is written for the staged (tracer) deck
    if a.mode == "gyponly":
        deck = strip_calcite(deck)
    if a.inert_boundary_x is not None:
        deck = inert_graph_boundary_cells(deck, *a.inert_boundary_x)
    if a.inert_helper_cells:
        deck = inert_helper_cells(deck, a.out.parent)
    if a.gypsum_area_porosity_power is not None:
        blk = re.search(r"(    Gypsum\n(?:.*\n)*?    /\n)", deck)
        assert blk, "Gypsum kinetics block not found"
        g = blk.group(1).replace("SURFACE_AREA_FUNCTION VOLUME_FRACTION_RATIO", "SURFACE_AREA_FUNCTION POROSITY_VOLUME_FRACTION_RATIO")
        g = g.replace("    /\n", f"        SURFACE_AREA_POROSITY_POWER {a.gypsum_area_porosity_power:g}\n    /\n", 1)
        assert "POROSITY_VOLUME_FRACTION_RATIO" in g, "gypsum area function line not found"
        deck = deck.replace(blk.group(1), g)
    if a.direct_transport:
        deck, n = re.subn(r"^(TIME\n.*?^END\n)",
                          "\\1\nNUMERICAL_METHODS TRANSPORT\n  NEWTON_SOLVER\n    ATOL 1.d-15\n  /\n"
                          "  LINEAR_SOLVER\n    SOLVER DIRECT\n  /\nEND\n", deck, count=1, flags=re.S | re.M)
        assert n == 1
    if a.min_porosity is not None:
        deck, n = re.subn(r"^  UPDATE_POROSITY\n", f"  MINIMUM_POROSITY {a.min_porosity:.1e}\n  UPDATE_POROSITY\n", deck, count=1, flags=re.M)
        assert n == 1
    if a.perm_min_scale is not None:
        deck, n = re.subn(r"^(MATERIAL_PROPERTY .*?\n  ID \d+\n)", lambda m: f"{m.group(1)}  PERMEABILITY_MIN_SCALE_FACTOR {a.perm_min_scale:.1e}\n",
                          deck, flags=re.S | re.M)
        assert n >= 1
    if a.calcite_fixed_area and a.mode == "gypcal":
        deck, n = re.subn(r"(    Calcite\n)      SURFACE_AREA_FUNCTION VOLUME_FRACTION_RATIO\n(      RATE_CONSTANT [^\n]*\n)      SURFACE_AREA_VOL_FRAC_POWER 0\.6667\n",
                          r"\1\2", deck, count=1)
        assert n == 1, "calcite kinetics block not found"
    if a.well_fill_injection:
        deck = well_fill_injection(deck, a.mode)
    if a.initial_dt is not None:
        deck, n = re.subn(r"^TIME\n", f"TIME\n    INITIAL_TIMESTEP_SIZE {a.initial_dt:.1e} y\n", deck, count=1, flags=re.M)
        assert n == 1
    from deck_heterogeneity import set_constant_fill, set_material, use_fill_dataset
    deck = set_constant_fill(deck, "Gypsum", a.gypsum_vf0)
    if a.fill_sigma > 0:
        deck = use_fill_dataset(deck, "Gypsum", "mineral_vf0.h5")
    deck = set_material(deck, a.material_porosity, a.perm_power)
    if a.perm_crit_por is not None:   # opt-in (6 Nov 2026, k-phi shape test); default decks unchanged
        deck, n = re.subn(r"^(MATERIAL_PROPERTY .*?\n  ID \d+\n)",
                          lambda m: f"{m.group(1)}  PERMEABILITY_CRITICAL_POROSITY {a.perm_crit_por:.10g}\n", deck, count=1, flags=re.S | re.M)
        assert n == 1, "MATERIAL_PROPERTY ID line not found"
    a.out.write_text(deck)
    pv0 = float((cells[:, 4] * (1 - vf_cells)).sum())
    sched = dict(mode=a.mode, rate_m3y=a.rate, gypsum_inventory_mol=inv, c_cap=c_cap, pore_volume0_m3=pv0,
                 k_gypsum_mult=a.k_gypsum_mult, dt_max_y=a.dt, final_time_y=t_end, mineral="Gypsum", vf0=a.gypsum_vf0,
                 material_porosity=a.material_porosity, perm_power=a.perm_power, fill_sigma=a.fill_sigma, fill_seed=a.fill_seed,
                 checkpoints=[dict(tau_d=f, t_y=t, tau_pv=t * a.rate / pv0, vtk_index=1 + vtk_times.index(round(t, 10)))
                              for f, t in zip(a.dissolved_fractions, t_chk)],
                 vtk_times_y=vtk_times)
    if a.perm_crit_por is not None:
        sched["perm_crit_por"] = a.perm_crit_por
    if a.k_calcite_mult != 1.0 or a.inj_co3 is not None:   # keys only when used, so default schedules stay unchanged
        sched.update(k_calcite_mult=a.k_calcite_mult, inj_co3_M=a.inj_co3 if a.inj_co3 is not None else 0.1)
    if a.inj_charge_balance:
        sched.update(inj_charge_balance=True)
    if a.inj_ph is not None:
        sched.update(inj_ph=a.inj_ph)
    Path(str(a.out) + ".schedule.json").write_text(json.dumps(sched, indent=1))
    print(json.dumps({k: v for k, v in sched.items() if k != "vtk_times_y"}, indent=1))


if __name__ == "__main__":
    main()
