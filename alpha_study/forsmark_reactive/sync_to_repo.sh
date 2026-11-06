#!/bin/zsh
# Copy the study's code, summaries, report and deck into the GitHub repo folder (no raw PFLOTRAN output) and,
# with --push, commit and push.   zsh forsmark_reactive/sync_to_repo.sh [--push "message"]
set -e
SRC=${0:A:h}/..; DST=/Users/collin/Projects/BiGraFV_reactive_channelization
rsync -a --prune-empty-dirs \
  --exclude '.venv/' --exclude 'deck/qa/' --exclude '_abandoned/' --exclude 'explore_olivine/test_short/' --exclude '__pycache__/' \
  --exclude 'phase1/figures/anim/' --exclude 'phase1/figures/anim2/*/' --exclude 'phase1/figures/anim3/*/' --exclude 'phase1/figures/anim3/*.mp4' --exclude 'phase1/figures/slices/' \
  --exclude 'report_phase1/index_v1.html' --exclude 'report_phase1/index_v2_tcap.html' --exclude 'report_phase1/index_pre_final*.html' \
  --exclude 'phase1/wormhole_regime.csv' --exclude 'phase1/channel_turnover.csv' \
  --include '*/' \
  --include 'phase1/L2_*/network_stats.json' --include 'phase1/L2_*/flow_summary.json' \
  --include 'phase1/L2_*/*/channelization.csv' --include 'phase1/L2_*/*/channel_fractures.csv' --include 'phase1/L2_*/*/patterns.csv' \
  --include 'phase1/L2_*/*/single_stage.in.schedule.json' --include 'phase1/L2_*/*/damkohler.json' --include 'phase1/L2_*/*/inlet_manifold.json' \
  --exclude 'phase1/L2_*/**' --exclude 'pilot/L*/**' --exclude 'pilot/*.log' \
  --include 'dfn_validation/rf_*/build_summary.json' --include 'dfn_validation/rf_*/network_stats.json' --include 'dfn_validation/rf_*/model_dfn/uge_repair.json' \
  --include 'dfn_validation/rf_*/*/smoke.json' --include 'dfn_validation/rf_*/*/smoke_trace.txt' --include 'dfn_validation/rf_*/*/patterns.csv' \
  --include 'dfn_validation/rf_*/*/channelization.csv' --include 'dfn_validation/rf_*/*/channel_fractures.csv' --include 'dfn_validation/rf_*/*/single_stage.in' \
  --include 'scale2km/L2_*/network_stats.json' --include 'scale2km/L2_*/flow_summary.json' \
  --include 'scale2km/L2_*/*/channelization.csv' --include 'scale2km/L2_*/*/patterns.csv' --include 'scale2km/L2_*/*/scale_mechanism_run.csv' \
  --include 'scale2km/L2_*/*/single_stage.in.schedule.json' --include 'scale2km/L2_*/*/damkohler.json' \
  --exclude 'scale2km/L2_*/**' --exclude 'scale2km/*.log' \
  --include 'dfn_validation/ex_*/build_summary.json' --include 'dfn_validation/ex_*/missing_phase1_fractures.txt' \
  --include 'dfn_validation/ex_*/model_graph_raw/phase1_fracture_id.txt' \
  --include 'dfn_validation/sm*/build_summary.json' --include 'dfn_validation/sm*/network_stats.json' \
  --include 'dfn_validation/ex_*/*/channelization.csv' --include 'dfn_validation/ex_*/*/patterns.csv' \
  --include 'dfn_validation/sm*/*/channelization.csv' --include 'dfn_validation/sm*/*/patterns.csv' \
  --include 'dfn_validation/sm*/*/single_stage.in.schedule.json' \
  --exclude 'dfn_validation/ex_*/**' --exclude 'dfn_validation/sm*/**' \
  --exclude 'dfn_validation/rf_*/**' --exclude 'dfn_validation/*.log' --exclude 'report_phase1/index_pre_x16.html' --exclude 'report_phase1/index_pre_scale2km.html' --exclude 'deck/numbers_x4x8.json' \
  --include 'explore_olivine/L2_*/*/clogging.csv' --include 'explore_olivine/L2_*/*/patterns.csv' --include 'explore_olivine/L2_*/*/channelization.csv' \
  --include 'explore_olivine/L2_*/*/single_stage.in' --include 'explore_olivine/L2_*/*/single_stage.in.schedule.json' --exclude 'explore_olivine/L2_*/**' \
  --exclude '*.vtk' --exclude '*.vtu' --exclude '*.h5' --exclude '*.stdout' --exclude 'single_stage.out' --exclude '*-mas.dat' \
  $SRC/forsmark_reactive/ $DST/alpha_study/forsmark_reactive/
for big in wormhole_regime channel_turnover; do gzip -9 -c $SRC/forsmark_reactive/phase1/$big.csv > $DST/alpha_study/forsmark_reactive/phase1/$big.csv.gz; done
for f in analyze_channelization.py analyze_km_dissolution_patterns.py probe_frozen_state_tracer.py deck_gypsum_calcite.py run_names.py build_km_graph_network.py build_network_dfn_and_graphs.py add_inlet_manifold.py exfix_outflow.py init_steady_pressure.py stabilize_graph_run.py; do cp $SRC/$f $DST/alpha_study/; done
cp $SRC/run_scripts/run_km_graph_case_hyman.sh $SRC/run_scripts/run_km_queue.py $DST/alpha_study/run_scripts/
if [ "$1" = "--push" ]; then
  cd $DST && git add -A && git commit -q -m "$2

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && git push -q && git log --oneline | head -1
fi
