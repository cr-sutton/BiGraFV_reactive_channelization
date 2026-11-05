#!/bin/zsh
# DFN counterpart of run_scripts/run_km_graph_case_hyman.sh for the Forsmark DFN validation (5 Nov 2026).
# Same deck builder, rate convention (one DFN pore volume per year), dt cap (DTF x tau), steady start, stabiliser and TS
# acceleration as the Phase 1 graph runs; DFN-specific: no boundary helper cells (no --inert-boundary-x / --inert-helper-cells),
# outflow faces fixed with EXFIX_DFN="--area 1e-6" (Track H), iterative solver on NP ranks.
#   usage: run_dfn_case.sh NET_DIR MODE TAG "EXTRA_DECK_ARGS" [DTF] [SMOKE_STEPS]
#   SMOKE_STEPS > 0: stop PFLOTRAN after that many transport steps and write smoke.json (cost and memory per step).
set -e
net=${1:A}; mode=$2; tag=$3; extra=${4:-}; dtf=${5:-0.57}; smoke=${6:-0}
here=${0:A:h}/../..
pflotran_exe=$(python3 -c "import json,os;print(json.load(open(os.path.expanduser('~/.dfnworksrc')))['PFLOTRAN_EXE'])")
src=$net/model_dfn; dst=$net/$(python3 $here/run_names.py $mode dfn $tag)
rm -rf $dst; mkdir -p $dst
for f in full_mesh_vol_area.uge dfn_properties.h5 boundary_left_w.ex boundary_right_e.ex materialid.dat; do cp $src/$f $dst/; done
extra=${extra//--inert-helper-cells/}
python3 $here/add_inlet_manifold.py $dst > /dev/null
read rate dt <<< $(python3 -c "
import sys,re; sys.path.insert(0,'$here/physics_upscaling')
from write_corrected_bigrafv_inputs import read_uge
c,_=read_uge('$dst/full_mesh_vol_area.uge')
m=re.search(r'--gypsum-vf0 (\S+)', '''$extra'''); vf0=float(m.group(1)) if m else 0.77
rate=c[:,4].sum()*(1-vf0); print(rate, $dtf*1.0)")
python3 $here/deck_gypsum_calcite.py --mode $mode --uge $dst/full_mesh_vol_area.uge --rate $rate --manifold-json $dst/inlet_manifold.json \
    --dt $dt --n-extra-vtk 60 --out $dst/single_stage.in ${=extra} > /dev/null
python3 $here/exfix_outflow.py $dst ${=${EXFIX_DFN:---area 1e-6}} > /dev/null
if [ -n "${STABILIZE:-}" ]; then python3 $here/stabilize_graph_run.py $dst ${=STABILIZE}; fi
if [ "${STEADY_INIT:-1}" = 1 ]; then python3 $here/init_steady_pressure.py $dst; fi
if [ -n "${TS_ACCEL:-}" ]; then
  python3 - $dst/single_stage.in $TS_ACCEL <<'PY'
import sys
p, n = sys.argv[1], sys.argv[2]
s = open(p).read()
s = s.replace("END_SUBSURFACE", f"NUMERICAL_METHODS TRANSPORT\n  TIMESTEPPER\n    TS_ACCELERATION {n}\n  /\nEND\n\nEND_SUBSURFACE", 1)
open(p, "w").write(s)
PY
fi
cd $dst
mpirun=$PETSC_DIR/$PETSC_ARCH/bin/mpirun; [ -x $mpirun ] || mpirun=mpirun
start=$(date +%s)
$mpirun -np ${NP:-6} $pflotran_exe -pflotranin single_stage.in > pflotran.stdout 2>&1 &
pid=$!; peak=0
while kill -0 $pid 2>/dev/null; do
  rss=$(ps -Ao rss,comm | awk '/pflotran$/{s+=$1} END{print s+0}'); [ $rss -gt $peak ] && peak=$rss
  free=$(memory_pressure 2>/dev/null | awk -F': ' '/free percentage/{gsub("%","",$2); print $2}')
  if [ -n "$free" ] && [ "$free" -lt ${MEM_FREE_MIN:-15} ]; then pkill -P $pid; kill $pid; echo "KILLED by memory guard (free ${free}%)" >> pflotran.stdout; break; fi
  if [ $smoke -gt 0 ]; then
    n=$(grep "^ Step " pflotran.stdout 2>/dev/null | tail -1 | awk '{print $2}')
    echo "$(( $(date +%s) - start )) ${n:-0} $rss" >> smoke_trace.txt
    if [ ${n:-0} -ge $smoke ]; then pkill -P $pid 2>/dev/null; kill $pid 2>/dev/null; echo "SMOKE stop after $n steps" >> pflotran.stdout; break; fi
  fi
  sleep 10
done
wait $pid 2>/dev/null || true
end=$(date +%s)
python3 - $dst $start $end $peak $rate $dt <<'PY'
import sys, re, json
d, t0, t1, peak, rate, dt = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6])
s = open(f"{d}/pflotran.stdout").read()
steps = re.findall(r"^ Step\s+(\d+)\s+Time=\s*([\d.Ee+-]+)\s+Dt=\s*([\d.Ee+-]+)", s, re.M)
tr = [l.split() for l in open(f"{d}/smoke_trace.txt")] if __import__("os").path.exists(f"{d}/smoke_trace.txt") else []
half = [r for r in tr if int(r[1]) >= max(1, int(tr[-1][1]) // 2)] if tr else []
sps = (int(half[-1][0]) - int(half[0][0])) / max(1, int(half[-1][1]) - int(half[0][1])) if len(half) > 1 else None
out = dict(wall_s=t1 - t0, steps=int(steps[-1][0]) if steps else 0, s_per_step_2nd_half=sps, last_time_y=float(steps[-1][1]) if steps else None,
           last_dt_y=float(steps[-1][2]) if steps else None, peak_rss_GB=peak / 1e6, rate_m3y=rate, dt_cap_y=dt,
           cuts=int(re.findall(r"cuts =\s*\d+ \[\s*(\d+)\]", s)[-1]) if "cuts =" in s else 0, killed="KILLED" in s, error=bool(re.search(r"ERROR|NaN", s)))
json.dump(out, open(f"{d}/smoke.json", "w"), indent=1); print(json.dumps(out))
PY
