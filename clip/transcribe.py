#!/usr/bin/env python3
"""Step 1: transcribe a local video/audio file to word-level JSON.

Usage: python transcribe.py INPUT --out transcript.json [--model small.en] [--device cpu]
Output: {"duration": float, "words": [{"w": str, "s": float, "e": float}, ...]}
"""
import argparse, json, subprocess, sys
import numpy as np


def load_audio(path):
    """Decode to 16 kHz mono float32 with ffmpeg (works for any container)."""
    p = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", "16000",
         "-f", "f32le", "-"], capture_output=True)
    if p.returncode:
        sys.exit("ffmpeg failed: " + p.stderr.decode()[-300:])
    return np.frombuffer(p.stdout, dtype=np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="small.en", help="e.g. tiny.en, small.en, large-v3")
    ap.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    ap.add_argument("--compute-type", default="int8", help="int8 (cpu) or float16 (cuda)")
    a = ap.parse_args()

    from faster_whisper import WhisperModel
    audio = load_audio(a.input)
    model = WhisperModel(a.model, device=a.device, compute_type=a.compute_type)
    segs, _ = model.transcribe(audio, word_timestamps=True, vad_filter=True)
    words = []
    for seg in segs:
        for w in seg.words or []:
            if w.end > w.start:  # drop zero-length duplicates
                words.append({"w": w.word, "s": round(w.start, 3), "e": round(w.end, 3)})
    with open(a.out, "w") as f:
        json.dump({"duration": round(len(audio) / 16000, 2), "words": words}, f)
    print(f"{len(words)} words -> {a.out}")


if __name__ == "__main__":
    main()
