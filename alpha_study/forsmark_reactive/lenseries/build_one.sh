#!/bin/zsh
# build_one.sh LENGTH P32_SCALE SEED: one length-series network (FFM01 layer 2, rmin 15 m, sigma 1, domain L x 250 x 250 m)
# plus stats.  Same builder and settings as phase1/build_one.sh except --domain-size (6 Nov 2026, LENGTH_SERIES.md).
cd ${0:A:h}/../..
out=forsmark_reactive/lenseries/L$1_r15_p$2_sg1.0_seed$3
start=$(date +%s)
python3 build_km_graph_network.py --forsmark --domain-size $1 250 250 --layer 2 --rmin 15 --p32-scale $2 --sigma 1.0 --seed $3 --no-geo --out $out > $out.build.log 2>&1
python3 forsmark_network_stats.py $out >> $out.build.log 2>&1
echo "BUILD_SECONDS $(( $(date +%s) - start ))" >> $out.build.log
