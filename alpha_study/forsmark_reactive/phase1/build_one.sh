#!/bin/zsh
# build_one.sh P32_SCALE SIGMA SEED: one Phase 1 network (layer 2, rmin 15 m) plus its structure stats
cd ${0:A:h}/../..
out=forsmark_reactive/phase1/L2_r15_p$1_sg$2_seed$3
python3 build_km_graph_network.py --forsmark --domain km250 --layer 2 --rmin 15 --p32-scale $1 --sigma $2 --seed $3 --no-geo --out $out > $out.build.log 2>&1
python3 forsmark_network_stats.py $out >> $out.build.log 2>&1
