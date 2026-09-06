# museum-v1.8.0 · Complete song associations and explicit playback states

- Fixed seven displayed NFTs whose source texts name songs but whose panels offered no playback: #007, #117, #142, #145, #171, #173 and #174. All 22 musical NFTs among 32 wall entries now resolve playable audio. The remaining ten text/object/context entries explicitly state that no accompanying song is assigned; the three originals remain text-only.
- Recovered complete recordings from supporting NFTs #031, #113, #119 and #153, verifying CAR and included-block digests. These sources are preserved without adding wall exhibits. Related recordings display their own NFT identity, source text and provenance, including the existing #070 → #049 association. No claim is made that independent NFTs contain identical original media packages or renditions.
- Corrected the museum interpretation of #142: its preserved source explicitly contains Nexus and lyrics despite an older derived index saying no_song. Original records remain byte-for-byte unchanged. Metadata-listed IPFS requests returned HTTP 403 here; this does not establish global unavailability.
- Show song titles and prominent playback controls above artwork; display loading/blocked/error states inside the panel. Opening an artwork attempts playback, with a visible manual fallback. Keep the selected artwork attached to its related soundtrack and stop stale audio when opening entries without music. The HTML reading archive also exposes related recordings.
- Validation: complete 32-entry source/audio audit, four-letter bindings, media decoding and release checks. All 19 catalogue recordings decode completely. Browser playback succeeded for the First Letter, Nexus and Manus (automatic on opening); at 390 px width the visible player progressed to 0:40. WebGL remains unavailable in the test browser; no new GPU visual verification is claimed.

# museum-v1.7.0 · Public access, floating crystal and corrected wall frames

- Opened the existing Site to anyone with the URL at the author’s explicit request.
- Increased display glass transmission from 0.72 to 0.80 while retaining rim illumination. The crystal floats above a low light disc, with restrained cool-white/gold rings and a soft halo. Reduced-motion mode removes oscillation. Levitation and aura are labelled as later digital exhibition design, not physical properties of the original object.
- Fixed overlapping or displaced frames: the retained architecture contained old static mounts while new frames followed the current exhibit layout. Hide the two obsolete frame/mat meshes and remove 10,528 obsolete mount/caption triangles at runtime, preserving the baked architecture. Every current artwork receives one consistently aligned frame.
- Repositioned the four Voices rows inside their 11 m chapter. All 32 frame normals point into the corridor and all exhibit centres remain inside their assigned chapter.
- Validation: source and media manifest checks, module syntax and geometry regression pass. Browser navigation reaches the crystal exhibit; WebGL is disabled in the test browser, so the new GPU lighting is not claimed as visually verified there.

# museum-v1.6.0 · Readable crystal, four letters and visible playback

- Added complete original audio and images for NFT #044 (Second Letter) and #032 (Fourth Letter: A Pact of Stars), recovered from existing CAR records with CAR and included-block SHA-256 checks. The four letters are presented in song order #016, #044, #020, #032, separately from mint chronology. 32 wall exhibits; no historical record rewritten.
- Added eight separately attributed 2026 curatorial illustrations to the remaining image-free displayed entries; never inserted into original NFT media. The three Bitcoin originals remain text on plain light panels, without illustrations.
- Playback controls precede artwork on phones and desktop. Opening a sound work from the gallery attempts user-initiated playback; the persistent visible button handles blocked autoplay. NFT #070 offers the separately labelled #049 soundtrack directly.
- Crystal display transmission reduced from 1.0 to 0.72, with broad studio reflections and dedicated cool/warm rim lights in the corridor and inspector. Physical dimensions, original photograph, model geometry and bilingual engraving remain unchanged. These are visibility adaptations, not measured material claims.
- Validation: complete media decoding, preserved identities and digests, release inventory, source module syntax, wall bounds and artwork coverage. No new mobile-device GPU or browser QA; the saved Blender reference renders predate these runtime adjustments.

# museum-v1.5.0 · Complete NFT media and truthful curatorial imagery

- English is the default; Chinese remains selectable. The published slug is trinity-accord.
- Recovered five omitted complete NFT recordings (42, 56, 71, 100, 146) and three original images (117, 142, 174), checking CAR and included-block digests. Image and sound remain attached to their own NFT in one panel.
- Added NFT #070’s original robot-and-mirror artwork. Its animation.mpga source is actually a PNG. Added the separately identified NFT #049 with its own original image and complete related song; linked the works without inventing a historical combined media package. Earlier #010 remains preserved in the catalogue and prior edition.
- Added the later Star Ark Covenant text inscription (#100751953), with a newly generated 2026-09-06 exhibition illustration labelled on the wall, in detail and in the reading archive. This image is not historical NFT artwork, not inscription payload, and does not alter the three closed originals.
- Thirty wall exhibits, slim metallic frame geometry, softer local accent illumination, balanced environmental light and colour-preserving image materials. Existing baked architecture and bilingual crystal reconstruction retained.
- Source records pinned to their respective commits; recovered media digests, illustration provenance and original text preserved. Validation covers media identity, release inventory and module syntax. GPU appearance and phone performance remain device-dependent; existing reference renders are not misrepresented as screenshots of this edition.

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
