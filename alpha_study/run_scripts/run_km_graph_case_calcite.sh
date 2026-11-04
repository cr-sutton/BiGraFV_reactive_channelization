#!/bin/zsh
# Graph-only single-stage reactive run on a kilometre-scale network (no DFN).
#   usage: run_km.sh NET_DIR MODEL MODE TAG "EXTRA_DECK_ARGS" [DT_OVER_TAU] [N_EXTRA_VTK] [C_CAP]
# The injection rate is the geometric graph's steady Q at the build's boundary
# pressures (0.1 MPa over 1000 m), the same for every model; the time-step cap
# is DT_OVER_TAU x the initial pore-volume residence time (the TPL runs used
# 1e-5 y = 0.057 tau, where Ca/SO4 closure holds).
set -e
net=${1:A}; m=$2; mode=$3; tag=$4; extra=${5:-}; dtf=${6:-0.057}; nvtk=${7:-60}; ccap=${8:-}
# optional '--rate-mult X' in EXTRA scales the injection rate (Da ~ 1/Q); it is removed before the deck builder
rmult=$(echo "$extra" | sed -nE 's/.*--rate-mult ([^ ]+).*/\1/p'); rmult=${rmult:-1}; extra=$(echo "$extra" | sed -E 's/--rate-mult [^ ]+//')
here=${0:A:h}/..
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
s=json.load(open('$net/flow_summary.json')); rate=(s.get('Q_graph_geo') or s['Q_graph_raw'])*365.25*86400*$rmult
import re; m=re.search(r'--(?:gypsum|quartz)-vf0 (\S+)', '''$extra'''); vf0=float(m.group(1)) if m else {'acid':0.77,'co2cal':0.77,'gyponly':0.77,'qtz':0.99}['$mode']
tau=c[:,4].sum()*(1-vf0)/rate
print(rate, $dtf*tau, x[ids('$src/boundary_left_w.ex')[0]], x[ids('$src/boundary_right_e.ex')[0]])")
direct="--direct-transport"; if [ "${DIRECT:-1}" = 0 ]; then direct=""; fi   # DIRECT=0: iterative transport solver (dense graphs)
deck_py=deck_gypsum_calcite.py; if [ $mode = acid ] || [ $mode = co2cal ]; then deck_py=deck_acid_calcite.py; fi; if [ $mode = qtz ]; then deck_py=deck_quartz.py; fi
cc=""; if [ -n "$ccap" ]; then cc="--c-cap $ccap"; fi
python3 $here/$deck_py --mode $mode --uge $src/full_mesh_vol_area.uge --rate $rate --manifold-json $dst/inlet_manifold.json \
    ${=direct} --dt $dt --n-extra-vtk $nvtk --inert-boundary-x $xin $xout --out $dst/single_stage.in $cc ${=extra} > /dev/null
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
