#!/usr/bin/env bash
# Run the whole pipeline on a local file you own or are licensed to use.
# Usage: bash run_example.sh /path/to/your_video.mp4 [target_seconds] [workdir]
set -euo pipefail
SRC="${1:?usage: run_example.sh VIDEO [seconds] [workdir]}"
LEN="${2:-30}"
WORK="${3:-./work}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="${PYTHON:-python3}"
mkdir -p "$WORK"

"$PY" "$HERE/transcribe.py" "$SRC" --out "$WORK/transcript.json"
"$PY" "$HERE/pick_moments.py" "$WORK/transcript.json" --length "$LEN" --top 5 --out "$WORK/moments.json"

# Cut the top-ranked moment. Review the printed list first and edit START/END if you prefer another.
read -r START END < <("$PY" -c "import json,sys;m=json.load(open(sys.argv[1]))[0];print(m['start'],m['end'])" "$WORK/moments.json")
"$PY" "$HERE/cut_vertical.py" "$SRC" "$WORK/transcript.json" \
  --start "$START" --end "$END" --title "My take: replace this with your own commentary" \
  --out "$WORK/clip_1.mp4" --workdir "$WORK/tmp"
ffprobe -v error -show_entries stream=width,height,duration -of csv=p=0 "$WORK/clip_1.mp4"
