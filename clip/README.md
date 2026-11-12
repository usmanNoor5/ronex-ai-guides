# Clip pipeline: long video to a captioned 9:16 short

Four small scripts. Each one reads a file and writes a file, so you can run, check and replace any step.

| Step | Script | In | Out |
|---|---|---|---|
| 1. Transcribe | `transcribe.py` | video or audio | `transcript.json` (word timestamps) |
| 2. Pick moments | `pick_moments.py` | transcript | ranked shortlist (`moments.json`) |
| 3. Cut 9:16 | `cut_vertical.py` | source + transcript + start/end | 1080x1920 mp4, blurred background |
| 4. Captions | built into `cut_vertical.py` | | word-highlight captions burned in, audio loudness-normalised |

## Install
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# ffmpeg and ffprobe must be on your PATH (see the main README)
```

## Run
```bash
bash run_example.sh /path/to/your_video.mp4 30 ./work
```
That transcribes, prints five candidate moments, and cuts the top one to `./work/clip_1.mp4`.
Everything is an argument: nothing is hard-coded.

Step by step:
```bash
python transcribe.py video.mp4 --out work/transcript.json            # --device cuda --compute-type float16 for an NVIDIA GPU
python pick_moments.py work/transcript.json --length 30 --top 5      # 15, 30 or 60-120 seconds
python cut_vertical.py video.mp4 work/transcript.json --start 12.4 --end 41.0 \
    --title "Your own commentary line" --out work/clip.mp4
```

## Notes that save time
- The shortlist is a heuristic (numbers, questions, emphasis words, pace). You or an AI assistant should read the candidates and choose; do not post blindly.
- Cuts snap to word boundaries. Pick an end at the sentence that closes the thought, not at a fixed length.
- Auto transcripts mangle names and brand words. Fix them in `transcript.json` before cutting.
- Choose a font with `fc-list | grep -i bold`, then pass `--font "Family Name"`. Use the family name the file reports, otherwise the renderer falls back silently.
- Keep captions in the safe area. The defaults sit above the bottom 12% of the frame.
- Check for burned-in lower-thirds or title cards in the source before choosing a window. The blurred letterbox keeps them intact instead of cropping.
- Bad words: mute and caption them yourself; the script does not censor.

## Rights
Use only footage you own or are licensed to use. Credit the source in the description, and add real commentary of your own. See the main README.
