#!/bin/zsh
# Rebuild the colloquium deck from the report's CSVs, figures and cartoons, validate it, and render a PDF + PNGs for QA.
#   zsh forsmark_reactive/deck/rebuild.sh        -> Forsmark_Reactive_Channels.pptx, qa/slide-NN.png
set -e
cd ${0:A:h}
SK="/Users/collin/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/6c058cb6-a2b4-4b0d-b400-a30a642f9693/653eb991-07ce-4802-a885-badd813537c7/skills/pptx"
python3 deck_numbers.py > /dev/null
.venv/bin/python render_cartoons.py > /dev/null
.venv/bin/python build_deck.py
[ -f "$SK/scripts/office/validate.py" ] && .venv/bin/python "$SK/scripts/office/validate.py" Forsmark_Reactive_Channels.pptx | tail -1
OUT="$HOME/Library/Containers/com.microsoft.Powerpoint/Data/deckqa"; mkdir -p "$OUT" qa; rm -f "$OUT/deck.pdf"; rm -f qa/slide-*.png(N)
TAG=$(date +%s); rm -f "$OUT"/deck-*.pptx(N); cp Forsmark_Reactive_Channels.pptx "$OUT/deck-$TAG.pptx"
osascript -e "tell application \"Microsoft PowerPoint\"" -e "open POSIX file \"$OUT/deck-$TAG.pptx\"" -e "delay 4" \
  -e "save active presentation in POSIX file \"$OUT/deck.pdf\" as save as PDF" -e "close active presentation saving no" -e "end tell"
.venv/bin/python -c "
import pymupdf
d = pymupdf.open('$OUT/deck.pdf')
for i, p in enumerate(d, 1): p.get_pixmap(dpi=80).save(f'qa/slide-{i:02d}.png')
print(len(d), 'slides rendered to qa/')"
