#!/bin/zsh
# Rebuild the story deck, validate it, render PDF + PNGs for QA (same procedure as ../../deck/rebuild.sh).
set -e
cd ${0:A:h}
SK="/Users/collin/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/6c058cb6-a2b4-4b0d-b400-a30a642f9693/653eb991-07ce-4802-a885-badd813537c7/skills/pptx"
PY=../../deck/.venv/bin/python
$PY build_story_deck.py
[ -f "$SK/scripts/office/validate.py" ] && $PY "$SK/scripts/office/validate.py" Reactive_Channels_Story.pptx | tail -1
OUT="$HOME/Library/Containers/com.microsoft.Powerpoint/Data/deckqa"; mkdir -p "$OUT" qa; rm -f "$OUT/story.pdf"; rm -f qa/slide-*.png(N)
TAG=$(date +%s); rm -f "$OUT"/story-*.pptx(N); cp Reactive_Channels_Story.pptx "$OUT/story-$TAG.pptx"
osascript -e "tell application \"Microsoft PowerPoint\"" -e "open POSIX file \"$OUT/story-$TAG.pptx\"" -e "delay 5" \
  -e "save active presentation in POSIX file \"$OUT/story.pdf\" as save as PDF" -e "close active presentation saving no" -e "end tell"
$PY -c "
import pymupdf
d = pymupdf.open('$OUT/story.pdf')
for i, p in enumerate(d, 1): p.get_pixmap(dpi=80).save(f'qa/slide-{i:02d}.png')
print(len(d), 'slides rendered to qa/')"
