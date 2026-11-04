#!/bin/zsh
# Finish the breakthrough-only (snapseq_k) probes of run_anim_probes.sh in parallel: one PFLOTRAN per folder lacking
# snap-mas.dat, at most 6 at a time.
cd ${0:A:h}/../..
EXE=/Users/collin/src/pflotran/src/pflotran/pflotran
for d in $(ls -d forsmark_reactive/phase1/L2_r15_p6.0_sg1.0_seed1/*/snapseq_*); do
  [ -f $d/snap-mas.dat ] && continue
  while [ $(jobs -r | wc -l) -ge 6 ]; do sleep 2; done
  (cd $d && nice -n 10 $EXE -pflotranin snap.in > pflotran.stdout 2>&1) &
done
wait
echo "snapseq parallel done"
