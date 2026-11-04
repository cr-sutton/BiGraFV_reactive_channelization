#!/bin/zsh
# Exploratory olivine-carbonation run (P32 x6, sigma 1, seed 1): deck, PFLOTRAN (np 2, nice 5), pattern + channel analyses
# and a clogging summary.  Start only after the Forsmark reactive queue has finished.
#   zsh forsmark_reactive/explore_olivine/run_olivine.sh   (log: explore_olivine/run_olivine.log)
cd ${0:A:h}/../..
SRC=forsmark_reactive/phase1/L2_r15_p6.0_sg1.0_seed1/gypsum_calcite__uncorrected_graph__phase1
RUN=forsmark_reactive/explore_olivine/L2_r15_p6.0_sg1.0_seed1/olivine__uncorrected_graph__explore
LOG=forsmark_reactive/explore_olivine/run_olivine.log
cp forsmark_reactive/phase1/L2_r15_p6.0_sg1.0_seed1/{network_stats.json,flow_summary.json} forsmark_reactive/explore_olivine/L2_r15_p6.0_sg1.0_seed1/ 2>/dev/null
echo "$(date '+%a %H:%M') deck" >> $LOG
python3 forsmark_reactive/deck_olivine_carbonation.py $SRC $RUN --t-end 300 --dt 0.05 --n-vtk 60 > /dev/null || exit 1
EXE=$(python3 -c "import json,os;print(json.load(open(os.path.expanduser('~/.dfnworksrc')))['PFLOTRAN_EXE'])")
MPI=$PETSC_DIR/$PETSC_ARCH/bin/mpirun; [ -x "$MPI" ] || MPI=/Users/collin/src/petsc/arch-darwin-c-opt/bin/mpirun
start=$(date +%s); echo "$(date '+%a %H:%M') start pflotran" >> $LOG
(cd $RUN && nice -n 5 $MPI -np 2 $EXE -pflotranin single_stage.in > pflotran.stdout 2>&1)
echo "$(date '+%a %H:%M') pflotran exit $? seconds=$(( $(date +%s) - start )) $(grep -o 'Time= *[0-9.E+-]*' $RUN/pflotran.stdout | tail -1)" >> $LOG
python3 analyze_km_dissolution_patterns.py $RUN > $RUN/patterns.log 2>&1
nice -n 5 python3 analyze_channelization.py $RUN > $RUN/channelization.log 2>&1
python3 forsmark_reactive/explore_olivine/clogging_summary.py $RUN >> $LOG 2>&1
echo "$(date '+%a %H:%M') done" >> $LOG
