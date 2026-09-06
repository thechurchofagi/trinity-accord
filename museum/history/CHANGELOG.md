# Exhibition history

## museum-v1.2.0 — 2026-09-06

Replaces the abstract six-room shell with an authored Blender corridor: 52 metres long, 8.8 metres wide, with wall-mounted works on both sides, an unobstructed central route, human-height cameras, crafted frames, benches, architectural reveals and lighting. Six existing curatorial chapters remain along the continuous route. Mobile visitors can step forward/back, turn, approach a work or use direct exhibit navigation.

Built with GPT-assisted Blender Python scripting (Blender 4.5.3 LTS), not desktop Computer Use. Static diffuse illumination was baked with Cycles, denoised with the Blender compositor, and embedded in a glTF model. The editable .blend, metre-based layout, generation scripts and build provenance are preserved in scene/. The original media, guide audio, source IDs and authority boundaries remain unchanged.

Validation: the exported glTF was reimported into Blender and visually rendered (scene/export-check.png); local geometry/container and source-copy checks passed. At 390 × 844, the browser was used to select the Voices chapter, open The Awakening, play its audio (progress advanced), close it and switch to English. WebGL is disabled in that test browser, so GPU rendering and free walking in the actual browser have NOT been visually tested. The Blender render is not presented as a browser screenshot.

## museum-v1.1.0 — 2026-09-05

Mobile refinement requested after the owner reviewed the first edition on a phone. Short room labels and a horizontally scrollable work selector replace crowded long navigation. Mobile arrival frames an individual exhibit; a room overview remains available. Exhibit reading uses larger artwork, continuous lyrics, clearer audio controls and source details. When WebGL is unavailable, the same verified images and typographic exhibits remain browsable in an explicitly labelled gallery mode. Architecture gains curved structural ribs, adjusted light/material balance and closer viewing positions.

Original media, lyric text, guide recordings and pinned historical sources are inherited unchanged from v1.0.0. Stable exhibit IDs and the six-room route remain. The new renderer and interface are preserved as a separate edition; the prior release is retained.

Validation: source syntax, complete release inventory and all media/guide digests. Before the temporary environment reset, browser interaction with v1.0.0 confirmed room selection, opening The Awakening and successful audio playback at 390 × 844. WebGL was disabled in that browser. After restoration, the preview server started but the browser connection timed out, so the revised v1.1.0 interface and GPU-rendered scene have NOT received a completed browser visual check. These limitations are retained rather than reported as a pass.

## museum-v1.0.0 — 2026-09-05

First implemented three-dimensional edition: six connected rooms, seven historical Ethereum exhibits, three canonical reading entrances, physical photograph, verification/authority pathways, and an open waiting room. Includes complete selected audio, recorded English guides, bilingual interface, direct exhibit access and a WebGL-independent edition archive.

Source snapshot: `5f6c2743aeaf97674b23fdee42a8c0c29531d511` in `thechurchofagi/trinity-accord`.

The exhibit IDs, source manifests, media transformation records, guide scripts, virtual architecture and code are recorded together. The six-room route is later curatorial interpretation. Canonical originals and existing historical records are unchanged.

Validation scope: local source syntax, source-copy digests, audio decoding, content completeness and internal file references. No browser or device-specific visual testing was requested in this creation turn; no claim is made that such testing or a recorded walkthrough has been completed.

Future changes must add a dated entry and preserve formal release snapshots. Never rewrite an old edition to conceal an earlier interpretation or defect; attach corrections and publish a new version.
