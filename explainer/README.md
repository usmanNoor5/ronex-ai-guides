# Explainer: code-drawn video with HyperFrames

An explainer made entirely from text, panels and diagrams drawn in HTML, animated with GSAP and rendered to video. No footage, no faces. We used this approach for a short about a developer tool's lifecycle events: a dark hook scene, a light diagram scene, a dark close.

`template/` is a minimal, verified starting point (HyperFrames `0.9.33`, `check` passes with 0 errors and 0 warnings, render gives 1080x1920 at 30 fps, 15 s).

## Use it
```bash
cd template
npm run setup          # one time: installs gsap and copies gsap.min.js into assets/
npm run check          # lints the composition
npm run dev            # live preview
npm run render         # writes silent.mp4 (video only)
```
Then add sound and normalise loudness:
```bash
bash mix.sh silent.mp4 your_audio.wav final.mp4
```
Docs: https://github.com/heygen-com/hyperframes

## What to edit
All text in `template/index.html` is placeholder (`HOOK TEXT`, `Item one`, `YOUR NAME` ...). Replace it, then adjust scene times.

Structure:
- `#root` holds the composition (`data-duration`, `data-width`, `data-height`).
- Each scene is a `.sc` block (`dark` or `light`) with an `.inner` wrapper.
- One GSAP timeline (`window.__timelines["main"]`) drives everything. `scene(s, i, start, end)` shows a scene, fades it in, fades it out and hides it.
- Update the light-background window (`#bgL`) and the watermark colour (`#wm`) when you move a light scene.

## Palette tokens
Defined once in `:root`. Change them here only.

| Token | Default | Use |
|---|---|---|
| `--d-bg` | `#09080A` | dark scene background |
| `--d-fg` | `#E1E1DF` | dark scene text |
| `--d-dim` | `#8A8A88` | dark secondary text |
| `--d-panel` | `#131315` | dark panels |
| `--d-line` | `#4B4C49` | dark borders |
| `--act-d` | `#34D961` | single accent on dark |
| `--l-bg` | `#E1E1DF` | light scene background |
| `--l-fg` | `#09080A` | light scene text |
| `--l-dim` | `#5E5E5C` | light secondary text |
| `--l-panel` | `#F1F1EF` | light panels |
| `--l-line` | `#09080A` | light borders |
| `--act-l` | `#1E9E45` | accent on light (darker for contrast) |

Rules that kept it readable: one accent colour only; alternate dark and light scenes for pace; max two text sizes per scene; captions inside the safe area (above the bottom 12%).

Fonts: the template uses system fonts (`--head-font`, `--mono-font`, `--cap-font`). To use your own, add font files you are licensed to use under `assets/fonts/` and declare them with `@font-face`.

## Sound
Sound is yours to make or license (voice you record, licensed music, generated effects). Mix it to a WAV that matches the video length, then run `mix.sh`.

**Loudnorm tip:** do two passes. Pass 1 measures (`loudnorm=...:print_format=json`), pass 2 applies the measured values with `linear=true`. `mix.sh` does this with a target of -16 LUFS and a true peak of -2.5 dB (AAC encoding can add about 0.2 dB, so leave headroom below -2). Verify the result:
```bash
ffmpeg -hide_banner -i final.mp4 -af loudnorm=I=-16:TP=-2.5:print_format=json -f null - 2>&1 | tail -14
```
Check `input_i` and `input_tp` in the output.

## Checklist before posting
- [ ] `npm run check` clean
- [ ] Stills of every scene look right
- [ ] `ffprobe`: 1080x1920, 30 fps, expected duration
- [ ] Loudness measured
- [ ] Watched once with sound on a phone
- [ ] Facts in the video checked against official docs, links in the description
