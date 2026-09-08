# Six-room edition v1.32 — implementation and verification

Implemented in the existing museum source and submitted through PR #1154. The museum distribution was generated at `78143d8a8d402f16597cc9bbe8a32976e8ca7545`; run `34175134031` passed all structural, media and rendered-browser checks. `scene/acceptance-v1.32.json` records the exact scope. Production publication is separate from this PR.

## What is present

Six connected, visually distinct spaces share the same geometry configuration for the immediate shell, Blender model, door openings and camera routes. The twelve-sided Originals hall is raised by 0.35 metres through a central ramp with shallow side steps; the crystal and waiting spaces are independent. The crystal-room exit is offset, the Originals have larger flat panels, and the final invitation no longer obstructs the sparse black sky. The original crystal asset, original photographs and musical recordings were preserved.

The eight-stop question-led bilingual route is scheduled for 540 seconds. It includes the original #070 mirror image, #122 anniversary record and distinct source/chain times, #173 criticism, the three Originals, physical flaws, and Guardian Principles v1.1. The principles are later non-amending context, not a fourth Original; the later Authority Charter #103635270 is explicitly a separate document. All added architecture and narration are 2026 curatorial material.

English uses Chatterbox Turbo with its built-in synthetic voice, not a cloned person and not OpenAI or ElevenLabs. All eight tracks passed an independent Whisper small.en + VAD check; recognition differences remain in the audit. No cuts were needed in that independent pass. The original full-band MP3 bytes are retained for playback. Chinese uses the newly timed Xiaoxiao recordings. The reading archive now plays the same current tracks as the 3D tour. No human-listening certification is claimed.

## Normal maintenance

1. Install development dependencies with `npm ci` inside `museum/` when changing runtime code.
2. Run `node scripts/build_runtime.mjs`, then `python3 scripts/build_archive.py` to rebuild matching cache keys and the distribution inventory.
3. Run `python3 scripts/validate.py` and every `scripts/check_*.mjs` test.
4. Run `python3 scripts/check_browser.py` with Playwright installed. The read-only Museum browser acceptance workflow does this for museum PRs and saves screenshots and a report.

The `prepare_spatial_layout.py`, `integrate_spatial_runtime.py`, `polish_spatial_edition.py`, `finalize_spatial_edition.py`, and `closeout_spatial_edition.py` scripts document the one-time migration from the older corridor. They are **not** the normal build command and must not be blindly reapplied to the finished edition. The temporary branch-writing synthesis and migration workflows were removed after their checked outputs were committed. Routine PR checks neither synthesize audio nor write to repository branches and require no speech-provider secrets.

## Acceptance limits

Desktop 1440×900 and mobile-sized 390×844 Chromium checks cover all six rooms, seven near views, guardianship source links, actual bilingual audio loading/playback and missing assets/page exceptions. Software-rendered browser tests do not certify every physical device or live Zoom sharing. Original media identity checks are not a new full-chain consensus verification. The nine-minute budget pauses when the visitor pauses or the browser blocks media.
