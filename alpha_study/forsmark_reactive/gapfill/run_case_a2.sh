#!/bin/zsh
# Copy of run_scripts/run_km_graph_case_hyman.sh for run A2 (8 Nov 2026): uses deck_gypsum_calcite_a2.py.
# Graph-only single-stage reactive run on a kilometre-scale network (no DFN),
# injecting ONE NETWORK PORE VOLUME PER YEAR (Hyman 2024 convention; residence
# time tau = 1 y), the standard for every reactive run from 28 Oct 2026 on.
#   usage: run_km_graph_case_hyman.sh NET_DIR MODEL MODE TAG "EXTRA_DECK_ARGS" [DT_OVER_TAU] [N_EXTRA_VTK] [C_CAP]
# Pore volume = sum of UGE cell volumes x (1 - mineral volume fraction vf0), i.e.
# the void volume that flows (0.23 x fracture volume for gypsum, 0.01 x for quartz).
# '--rate-mult X' in EXTRA scales the rate relative to one pore volume per year
# (Da ~ 1/X); the time-step cap is DT_OVER_TAU x tau = DT_OVER_TAU years / X.
# Modes: gyponly, acid, co2cal, qtz (same decks as run_km_graph_case_calcite.sh).
# Verified on seed21_sigma0: gypsum channelization vs dissolved fraction is the
# same as at the 0.1 MPa build rate to within 0.1% (linear) / 2% (cubic).
set -e
net=${1:A}; m=$2; mode=$3; tag=$4; extra=${5:-}; dtf=${6:-0.057}; nvtk=${7:-60}; ccap=${8:-}
# optional '--rate-mult X' (relative to one pore volume per year) is removed before the deck builder
rmult=$(echo "$extra" | sed -nE 's/.*--rate-mult ([^ ]+).*/\1/p'); rmult=${rmult:-1}; extra=$(echo "$extra" | sed -E 's/--rate-mult [^ ]+//')
here=/Users/collin/Projects/bipartite_pflotran/src/alpha_study   # A2 copy (8 Nov 2026): absolute alpha_study root
pflotran_exe=$(python3 -c "import json,os;print(json.load(open(os.path.expanduser('~/.dfnworksrc')))['PFLOTRAN_EXE'])")
src=$net/model_$m; dst=$net/$(python3 $here/run_names.py $mode $m $tag)
rm -rf $dst; mkdir -p $dst
for f in full_mesh_vol_area.uge dfn_properties.h5 boundary_left_w.ex boundary_right_e.ex altered_cells_df.dat; do cp $src/$f $dst/; done
cp $src/dfnGen_output/polygons.dat $dst/
python3 $here/add_inlet_manifold.py $dst > /dev/null
read rate dt xin xout <<< $(python3 -c "
import sys,json; sys.path.insert(0,'$here/physics_upscaling')
from write_corrected_bigrafv_inputs import read_uge
c,_=read_uge('$src/full_mesh_vol_area.uge'); x={int(r[0]):r[1] for r in c}
ids=lambda f:[int(l.split()[0]) for l in open(f).read().splitlines()[1:] if l.strip()]
import re; m=re.search(r'--(?:gypsum|quartz)-vf0 (\S+)', '''$extra'''); vf0=float(m.group(1)) if m else {'acid':0.77,'co2cal':0.77,'gyponly':0.77,'gypcal':0.77,'qtz':0.99}['$mode']
rate=c[:,4].sum()*(1-vf0)*$rmult   # m^3/y: one pore volume per year, times the multiplier
tau=c[:,4].sum()*(1-vf0)/rate        # = 1/$rmult years
print(rate, $dtf*tau, x[ids('$src/boundary_left_w.ex')[0]], x[ids('$src/boundary_right_e.ex')[0]])")
direct="--direct-transport"; if [ "${DIRECT:-1}" = 0 ]; then direct=""; fi   # DIRECT=0: iterative transport solver (dense graphs)
deck_py=deck_gypsum_calcite.py; if [ $mode = acid ] || [ $mode = co2cal ]; then deck_py=deck_acid_calcite.py; fi; if [ $mode = qtz ]; then deck_py=deck_quartz.py; fi
cc=""; if [ -n "$ccap" ]; then cc="--c-cap $ccap"; fi
python3 /Users/collin/Projects/bipartite_pflotran/src/alpha_study/forsmark_reactive/gapfill/deck_gypsum_calcite_a2.py --mode $mode --uge $src/full_mesh_vol_area.uge --rate $rate --manifold-json $dst/inlet_manifold.json \
    ${=direct} --dt $dt --n-extra-vtk $nvtk --inert-boundary-x $xin $xout --out $dst/single_stage.in $cc ${=extra} > /dev/null
if [ -n "${APERTURE_CAP_UM:-}" ]; then python3 $here/apply_aperture_cap.py $dst --cap-um $APERTURE_CAP_UM; fi   # per-cell exponent so b_T <= cap
# Outflow-face conductance fix (Track H2), DEFAULT ON from 3 Nov 2026: graph outflow faces are 1000 m^2 at 1e-4-1 m from the
# cell centre, which at one pore volume per year lets solute pile up in the outlet helper cells until the last fracture cell
# seals (forsmark_reactive/phase1/INTERVENTIONS.md).  EXFIX unset -> "--area-per-dist 1e-2"; EXFIX=none -> old faces.
exfix=${EXFIX:---area-per-dist 1e-2}
if [ "$exfix" != none ]; then python3 $here/exfix_outflow.py $dst ${=exfix} > /dev/null; fi
if [ -n "${STABILIZE:-}" ]; then python3 $here/stabilize_graph_run.py $dst ${=STABILIZE}; fi   # before the steady start: e.g. "--dirichlet-outflow 2e5"
if [ "${STEADY_INIT:-0}" = 1 ]; then python3 $here/init_steady_pressure.py $dst; fi
if [ -n "${TS_ACCEL:-}" ]; then   # transport: let the step grow up to TS_ACCEL Newton iterations (PFLOTRAN default 5)
  python3 - $dst/single_stage.in $TS_ACCEL <<'PY'
import sys
p, n = sys.argv[1], sys.argv[2]
s = open(p).read()
block = f"NUMERICAL_METHODS TRANSPORT\n  TIMESTEPPER\n    TS_ACCELERATION {n}\n  /\nEND\n\n"
if "NUMERICAL_METHODS TRANSPORT" in s:      # e.g. the quartz deck: add the timestepper inside its block
    s = s.replace("NUMERICAL_METHODS TRANSPORT\n", f"NUMERICAL_METHODS TRANSPORT\n  TIMESTEPPER\n    TS_ACCELERATION {n}\n  /\n", 1)
else:
    s = s.replace("END_SUBSURFACE", block + "END_SUBSURFACE", 1)
open(p, "w").write(s)
PY
fi   # start from the steady pressure field
cd $dst
start=$(date +%s)
# NP > 1: MPI ranks (iterative solver only).  Memory guard: kill the run if the
# system's free-memory percentage drops below MEM_FREE_MIN (default 15).
np_=${NP:-1}
if [ $np_ -gt 1 ]; then
  mpirun=$PETSC_DIR/$PETSC_ARCH/bin/mpirun; [ -x $mpirun ] || mpirun=mpirun
  $mpirun -np $np_ $pflotran_exe -pflotranin single_stage.in > pflotran.stdout 2>&1 &
else
  $pflotran_exe -pflotranin single_stage.in > pflotran.stdout 2>&1 &
fi
pid=$!
while kill -0 $pid 2>/dev/null; do
  free=$(memory_pressure 2>/dev/null | awk -F': ' '/free percentage/{gsub("%","",$2); print $2}')
  if [ -n "$free" ] && [ "$free" -lt ${MEM_FREE_MIN:-15} ]; then
    pkill -P $pid 2>/dev/null; kill $pid; echo "KILLED by memory guard (system free ${free}%)" >> pflotran.stdout; break
  fi
  sleep 30
done
wait $pid 2>/dev/null || true
echo "$(basename $net) $(basename $dst) seconds=$(( $(date +%s) - start )) rate=$rate dt=$dt"
