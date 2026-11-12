#!/usr/bin/env bash
# Usage: bash mix.sh silent.mp4 audio.wav out.mp4
# Normalises loudness in two passes (target about -16 LUFS, true peak -2.5 dB) and muxes.
set -euo pipefail
V="${1:?silent video}"; A="${2:?audio wav}"; O="${3:?output mp4}"
J=$(ffmpeg -hide_banner -i "$A" -af loudnorm=I=-16:TP=-2.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g(){ python3 -c "import sys,json;print(json.load(sys.stdin)['$1'])" <<<"$J"; }
ffmpeg -y -hide_banner -loglevel error -i "$V" -i "$A" -map 0:v -map 1:a \
  -af "loudnorm=I=-16:TP=-2.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aformat=sample_rates=48000:channel_layouts=stereo" \
  -c:v libx264 -crf 20 -preset slow -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart "$O"
echo "wrote $O"
