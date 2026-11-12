#!/usr/bin/env python3
"""Steps 3+4: cut one moment to 9:16 (1080x1920) with burned-in word captions.

Cuts snap to word boundaries (never mid-word). The source is placed on a blurred
copy of itself (letterbox), captions are generated as an ASS file with the
active word highlighted, audio is loudness-normalised in two passes.

Usage:
  python cut_vertical.py SOURCE TRANSCRIPT --start 12.4 --end 41.0 --out clip.mp4 \
      [--font "DejaVu Sans"] [--fontsdir DIR] [--title "My take: ..."] [--workdir DIR]

--title is optional on-screen text for YOUR OWN commentary line. Credit the
source in the post description.
"""
import argparse, json, os, re, subprocess, sys, tempfile


def sh(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode:
        sys.exit("command failed: " + " ".join(cmd[:3]) + "\n" + r.stderr[-600:])
    return r


def ts(t):
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def snap(words, start, end):
    """Move start to the first word starting at/after start, end to the last word ending at/before end."""
    inside = [w for w in words if w["s"] >= start - 0.05 and w["e"] <= end + 0.05]
    if not inside:
        sys.exit("no words in range; check --start/--end")
    return inside[0]["s"], inside[-1]["e"], inside


def chunks(ws, maxc=16, maxw=3):
    out, cur = [], []
    for w in ws:
        n = sum(len(x["t"]) + 1 for x in cur) + len(w["t"])
        if cur and (n > maxc or len(cur) >= maxw or w["s"] - cur[-1]["e"] > 0.5
                    or cur[-1]["t"][-1] in ".?!,"):
            out.append(cur); cur = []
        cur.append(w)
    if cur:
        out.append(cur)
    return out


def build_ass(words, dur, font, title):
    ev = []
    for ch in chunks(words):
        for i, w in enumerate(ch):
            st = w["s"]
            en = ch[i + 1]["s"] if i + 1 < len(ch) else w["e"] + 0.2
            txt = " ".join((r"{\c&H61D934&}%s{\r}" % x["t"]) if j == i else x["t"]
                           for j, x in enumerate(ch))
            ev.append([st, en, txt])
    ev.sort()
    for i in range(len(ev) - 1):          # clamp: overlapping events render garbled
        ev[i][1] = min(ev[i][1], ev[i + 1][0])
    lines = [f"Dialogue: 0,{ts(s)},{ts(e)},Cap,,0,0,0,,{{\\an5\\pos(540,1400)}}{t}"
             for s, e, t in ev if e - s >= 0.03]
    if title:
        t = title.replace("{", "").replace("}", "")
        lines.append(f"Dialogue: 1,{ts(0.3)},{ts(max(dur - 0.3, 0.4))},Title,,0,0,0,,"
                     f"{{\\an5\\pos(540,470)\\fad(300,300)}}{t}")
    return f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Cap,{font},70,&H00F6F6F6,&H00F6F6F6,&H00100E0E,&H90000000,1,0,0,0,100,100,0,0,1,6,3,5,100,100,0,1
Style: Title,{font},40,&H00F6F6F6,&H00F6F6F6,&H00100E0E,&H00100E0E,1,0,0,0,100,100,0,0,3,18,0,5,110,110,0,1
[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
""" + "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source"); ap.add_argument("transcript")
    ap.add_argument("--start", type=float, required=True)
    ap.add_argument("--end", type=float, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--font", default="DejaVu Sans", help="installed font family (check: fc-list)")
    ap.add_argument("--fontsdir", default=None, help="optional folder with extra .ttf files")
    ap.add_argument("--title", default=None)
    ap.add_argument("--workdir", default=None)
    a = ap.parse_args()

    tr = json.load(open(a.transcript))
    s, e, inside = snap(tr["words"], a.start, a.end)
    dur = e - s + 0.25
    words = []
    for w in inside:
        t = w["w"].strip()
        if not w["w"].startswith(" ") and words:   # glue sub-word pieces
            words[-1]["t"] += t; words[-1]["e"] = w["e"] - s; continue
        words.append({"t": t, "s": w["s"] - s, "e": min(w["e"] - s, dur)})

    work = a.workdir or tempfile.mkdtemp(prefix="clip_")
    os.makedirs(work, exist_ok=True)
    ass = os.path.join(work, "caps.ass")
    open(ass, "w").write(build_ass(words, dur, a.font, a.title))

    raw, norm = os.path.join(work, "raw.wav"), os.path.join(work, "norm.wav")
    sh(["ffmpeg", "-v", "error", "-y", "-ss", str(s), "-t", str(dur), "-i", a.source,
        "-vn", "-af", f"aresample=48000,afade=t=in:d=0.03,afade=t=out:st={dur-0.3:.2f}:d=0.3",
        "-ac", "2", raw])
    m = sh(["ffmpeg", "-hide_banner", "-i", raw, "-af",
            "loudnorm=I=-16:TP=-2.5:LRA=11:print_format=json", "-f", "null", "-"]).stderr
    j = json.loads(m[m.rindex("{"):])
    ln = (f"loudnorm=I=-16:TP=-2.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
          f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:"
          f"offset={j['target_offset']}:linear=true")
    sh(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", ln, "-ar", "48000", norm])

    # ass filter args are escaped by passing them as filter options
    assf = "ass=filename=" + re.sub(r"([:\\'])", r"\\\1", ass)
    if a.fontsdir:
        assf += ":fontsdir=" + re.sub(r"([:\\'])", r"\\\1", a.fontsdir)
    vf = ("[0:v]fps=30,split[a][b];"
          "[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=16[bg];"
          "[b]scale=1080:-2:flags=lanczos[fg];"
          f"[bg][fg]overlay=0:(H-h)/2,{assf},format=yuv420p[v]")
    sh(["ffmpeg", "-v", "error", "-y", "-ss", str(s), "-t", str(dur), "-i", a.source, "-i", norm,
        "-filter_complex", vf, "-map", "[v]", "-map", "1:a", "-c:v", "libx264", "-crf", "18",
        "-preset", "medium", "-r", "30", "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", "-t", str(dur), a.out])
    print(f"wrote {a.out}  ({dur:.1f}s, {s:.2f}-{e:.2f} of source)")


if __name__ == "__main__":
    main()
