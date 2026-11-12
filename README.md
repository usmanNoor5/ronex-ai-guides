# Ronex AI guides: clip, one-shot, explainer

Free, open workflows for making short vertical videos with an AI coding assistant and a few command-line tools. You got this link because you commented **CLIP**, **SHOT** or **EXPLAINER** on a Ronex AI video.

This repo contains scripts and written guides only. It contains no media, no accounts and no credentials.

## Who it is for
Creators who are comfortable running a few terminal commands and want a repeatable way to produce 9:16 videos (Shorts, Reels, TikTok) without a timeline editor.

## The three workflows

| You commented | Folder | What you get |
|---|---|---|
| CLIP | [`clip/`](clip/) | Long video to captioned 9:16 clips: transcribe, shortlist moments, cut, caption. Working scripts. |
| SHOT | [`oneshot/`](oneshot/) | One prompt to one finished video, using code-based video tools (HyperFrames or Remotion). Written guide. |
| EXPLAINER | [`explainer/`](explainer/) | A code-drawn explainer: a minimal HyperFrames template with placeholder text, palette tokens and a loudness-mix script. |

## Rights note (read this first)
- Only use footage and audio you **own** or are **licensed to use** (your own recordings, Creative Commons with the right attribution, written permission).
- **Always credit** the source in the description, with a link.
- **Add original commentary** of your own. A raw re-upload is not a clip.
- Platform rules and copyright law differ by country. Claims, demonetization or removal can still happen even with credit. Nothing here is legal advice.
- Do not download media in ways that break a site's terms of service.

## No income claims
These are production workflows. They do not promise views, followers or money.

## Independence
This project is independent. It is not affiliated with, endorsed by or sponsored by Anthropic, Google, Higgsfield, HeyGen, Remotion or any other company named in it. Product names belong to their owners and are used only to describe compatibility.

## Install the prerequisites

You need ffmpeg, Python 3.9+ (3.10+ recommended) and, for the explainer and one-shot guides, Node.js 18+.

**ffmpeg** (includes `ffprobe`):
- macOS (Homebrew): `brew install ffmpeg`
- Debian/Ubuntu: `sudo apt install ffmpeg`
- Windows: `winget install ffmpeg` (or download from https://ffmpeg.org/download.html)
- Check: `ffmpeg -version`

**Python and faster-whisper** (speech to text, used by the clip pipeline):
```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install faster-whisper numpy
```
faster-whisper runs on CPU by default (slow but works anywhere). Models download on first use. An NVIDIA GPU needs the matching CUDA libraries; if GPU start-up fails, use `--device cpu`. Docs: https://github.com/SYSTRAN/faster-whisper

**Node.js** (only for `oneshot/` and `explainer/`): install from https://nodejs.org, check with `node -v`.

## Quick start (clip)
```bash
cd clip
bash run_example.sh /path/to/your_own_video.mp4 30 ./work
```

## Layout
```
README.md
LICENSE
clip/        transcribe.py, pick_moments.py, cut_vertical.py, run_example.sh
oneshot/     README.md
explainer/   README.md, template/ (HyperFrames project), mix.sh lives in template/
```

## License
MIT, see [LICENSE](LICENSE). The license covers the code and text in this repo, not any video you process with it.
