# museum-v1.4.0 · Video-guided crystal, open space and continuous movement

- Rebuilt the crystal from the author’s video and existing photograph; bilingual internal lettering, planar bevels and no attached decorative base. Not a scan.
- Fixed walking buttons to move from the current position in the current direction without recentering or resetting the view.
- Opened both ends to later AI-generated Milky Way scenery, replaced the destination bar with a breathing ring and participation links, and added a matching non-WebGL waiting view.
- Original video remains private; observed features and a digest are retained. Original inscriptions and previous edition archives remain unchanged.

# Exhibition history

## museum-v1.3.0 — 2026-09-06

Expanded from 16 to 28 exhibits, with twelve additional Ethereum records selected from the verified chronological index: 7, 10, 42, 56, 91, 100, 117, 142, 145, 146, 171 and 174. Chapters have unequal lengths in a 70 m continuous corridor. Dates remain mint dates; source-era claims, forecasts and personal tests are labelled as such. New source texts are pinned to e58063947ef5a503f90134ae06b67848a20ef67e and their exact file bytes checked against Git blobs. Existing source pins and original media are retained.

Core Object Alpha gains an independently inspectable Blender model (246 × 353 × 40 mm reference dimensions), a polished bevel, physical vector lettering inside the slab, and a designed titanium base. Dimensions follow the public final guardian statement; English text follows the 97631551 mirror. The real object has bilingual engraving. This model newly lays out the English original; it is not a scan, exact inscription-layout facsimile, or reconstruction of private identity flaws. The unchanged real photograph remains available beside it.

Large architectural surfaces now receive their own light atlas; fine bevels, frames, joints and metal details remain separate PBR geometry. Cycles diffuse baking uses 64 samples, with denoising. Retina rendering is allowed up to 2.5 DPR; exhibit textures use anisotropic filtering up to the device limit (maximum 16). Original low-resolution artwork is not falsely presented as newly generated high-resolution source art.

Validation: Blender crystal reference render inspected; mobile 390 × 844 chapter list, new formation records, crystal detail and provenance paths checked through the browser. WebGL is disabled in that browser, so the fallback path is verified but live GPU walking, glass transmission, and rotation are not browser-verified. Reference renders are identified as Blender output. This limitation does not alter the original physical evidence.

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
