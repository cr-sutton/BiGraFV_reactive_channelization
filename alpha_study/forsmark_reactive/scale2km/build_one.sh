#!/bin/zsh
# build_one.sh P32_SCALE SIGMA SEED: one scale-up network (FFM01 layer 2, rmin 15 m, domain 2000 x 500 x 250 m) plus stats.
# Same builder and settings as phase1/build_one.sh except --domain-size (5 Nov 2026 scale test).
cd ${0:A:h}/../..
out=forsmark_reactive/scale2km/L2_r15_p$1_sg$2_seed$3
start=$(date +%s)
python3 build_km_graph_network.py --forsmark --domain-size 2000 500 250 --layer 2 --rmin 15 --p32-scale $1 --sigma $2 --seed $3 --no-geo --out $out > $out.build.log 2>&1
python3 forsmark_network_stats.py $out >> $out.build.log 2>&1
echo "BUILD_SECONDS $(( $(date +%s) - start ))" >> $out.build.log
