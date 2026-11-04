#!/bin/zsh
# Tracer probes for the paused-pulse stage movie (network P32 x6, sigma 1, seed 1, both chemistries).
# Same pulse (0.1 tau_res), window (10 tau_res) and fine steps as the fine probes (run_fine_probes.sh), into new folders
# so the existing snap_k / snapfine_k probes are untouched:
#   snapanim_k  plume frames: extra VTK every 0.05 tau_res until 3 tau_res, at k = 0 and the four stage stills of
#               make_decoupling_movie.py (gyponly 35 42 47 55; gypcal 12 18 23 30)
#   snapseq_k   breakthrough curve only, at every movie frame (t_cap <= 3), for a continuous transport trace
# Run only after the reactive queue has finished.   zsh forsmark_reactive/phase1/run_anim_probes.sh
cd ${0:A:h}/../..
P=forsmark_reactive/phase1/L2_r15_p6.0_sg1.0_seed1
export PROBE_PULSE=0.1 PROBE_WINDOW=10 PROBE_DT=0.05 PROBE_DT_FINE=0.005 PROBE_FINE_UNTIL=3 PROBE_FEW_ABOVE=200000
frames() { python3 - $1 <<'EOF'
import sys, pandas as pd
m = pd.read_csv("forsmark_reactive/phase1/phase1_mechanism.csv")
m = m[(m["mode"] == sys.argv[1]) & (m.p32 == 6.0) & (m.sigma == 1.0) & (m.seed == 1) & (m.tag == "phase1") & (m.t_cap <= 3.0)]
print(" ".join(str(int(k)) for k in sorted(m.k)))
EOF
}
one() {   # $1 run dir, $2 prefix, $3.. states
  local r=$1 pre=$2; shift 2
  PROBE_DIR=$pre python3 probe_frozen_state_tracer.py setup $r --states $@ > /dev/null &&
  PROBE_DIR=$pre nice -n 10 python3 probe_frozen_state_tracer.py run $r --np 1 > $r/probes_$pre.log 2>&1
  echo "$r $pre $(grep -c ok $r/probes_$pre.log) of $# ok"
}
( PROBE_VTK_DT=0.05 PROBE_VTK_UNTIL=3 one $P/gypsum__uncorrected_graph__phase1 snapanim 0 35 42 47 55 ) &
( PROBE_VTK_DT=0.05 PROBE_VTK_UNTIL=3 one $P/gypsum_calcite__uncorrected_graph__phase1 snapanim 0 12 18 23 30 ) &
wait
ls $P/gypsum__uncorrected_graph__phase1/snapanim_35/snap-*.vtk | wc -l | xargs echo "plume frames per probe:"
( one $P/gypsum__uncorrected_graph__phase1 snapseq ${=$(frames gyponly)} ) &
( one $P/gypsum_calcite__uncorrected_graph__phase1 snapseq ${=$(frames gypcal)} ) &
wait
echo "anim probes done"
