# One-shot: one prompt, one video

"One-shot" here means you describe the whole video once, in a single structured prompt, and an AI coding assistant writes the project that renders it. You review, fix small things, and render. It is the same approach we use with HyperFrames and Remotion: the video is **code** (HTML or React), so an assistant can write it and a command renders it deterministically.

## What is verified and what is not
Verified by us while preparing this guide:
- HyperFrames `0.9.33` (installed on demand with `npx`) runs `check` and `render` on a local project and produces a 1080x1920, 30 fps mp4 from an HTML file. See `../explainer/template/`.
- The rest of the workflow below is a method, not a guarantee. Quality depends on your prompt, your assistant and your edits. Expect to iterate.

Not verified here: Remotion render commands against a fresh install (follow its docs), and any specific model's output quality.

## Official docs (use these for exact commands)
- HyperFrames: https://github.com/heygen-com/hyperframes (project page: https://hyperframes.heygen.com)
- Remotion: https://www.remotion.dev/docs
- Claude Code: https://code.claude.com/docs
- ffmpeg: https://ffmpeg.org/documentation.html

## The workflow
1. **Pick the tool.**
   - HyperFrames: HTML + CSS + GSAP animation, rendered to video. Good for title cards, kinetic text, diagrams.
   - Remotion: React components rendered to video. Good for data-driven or template videos.
2. **Write one prompt with a spec.** Include:
   - Goal and one-sentence message of the video.
   - Format: 1080x1920, 30 fps, length in seconds.
   - Scene list with a start and end time for each scene and the exact on-screen text.
   - Visual rules: palette (hex values), fonts you are licensed to use, safe area (keep text away from the bottom 12%).
   - Audio: voice-over script or none; sound effects; target loudness.
   - Output: a folder, plus the exact commands to check and render.
3. **Let the assistant build the project**, then run the tool's check command first. Fix every error before rendering.
4. **Look at stills** at each scene's midpoint before a full render. Fix overflow, overlap and unreadable text.
5. **Render**, then verify with `ffprobe` (size, fps, duration).
6. **Add audio** with your own voice, licensed music or generated sound, then normalise loudness (see `../explainer/template/mix.sh`).
7. **Watch the final once, with sound, on a phone.** Automated checks do not replace this.

## Prompt skeleton
```
Build a 1080x1920, 30 fps, 20 second vertical video in HyperFrames.
Message: <one sentence>.
Palette: background #09080A, text #E1E1DF, accent #34D961.
Scenes:
  0-5 s   hook: "<exact text>"
  5-15 s  <what appears, in order, with times>
  15-20 s end: "<exact text>"
No faces, no stock footage, no music. Keep text inside the safe area.
Then run the check command, fix all errors, and render to ./silent.mp4.
```

## Rights
Generate or write everything you use, or use licensed assets. Credit sources. Do not imitate a real person or organization. No income claims in your videos.

## Tips
- One job per step (build, fix, audio, QA) keeps each assistant run small and reviewable.
- Keep scripts parameterised (length, resolution) so you can re-run with one command.
- Pin tool versions (for example `hyperframes@0.9.33`) so a project keeps rendering the same way.
