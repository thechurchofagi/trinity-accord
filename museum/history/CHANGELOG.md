# museum-v1.18.1 · Stop walking when reading

- Cancel an in-progress walk when a detail dialog opens, preventing a position jump when returning from a long reading pause.

# museum-v1.18.0 · Caption reliability and default footsteps

- Replace layered lyric-card CSS with independent caption and playback lanes. Compact captions contain only up to two physical lines, with no panel, blur, title, or clipped overflow. Long phrases page using measured font width.
- Keep pause/stop available when captions are hidden; restore reachable expand/hide controls and room focus actions. Start artwork-strip selection at its reachable left edge and play the selected artwork's recording.
- Derive sung text without changing preserved source records: retain inline first verses, remove title/section headers, and stop before the Betrayal Turn's explanatory NFT prose.
- Cancel stale lyric fetch results, clear previous-track captions, and leave estimated intro/tail intervals blank. Caption timing is still estimated, not verified audio alignment.
- Keep synthesized footsteps enabled by default without an off switch. Use elapsed-time walking at 1.38 m/s, remove accelerated floor-tap easing, turn laterally, respect reduced-motion head roll, and clean up audio nodes.
- Regression: 21 audio records / 675 derived sung lines, lossless two-line pagination, cue boundaries, and walking at 10/20/30/60/120 fps. Browser checks include multiple song switches and 390/320 px layouts. WebGL motion and audible timing still require a capable browser/listening verification.

# museum-v1.17.0 · Cinematic captions and natural walking

- Replace the compact lyric card with television-style current/next subtitles: no panel fill, blur, title, cover, time label, or detail button. Keep only small playback and lyric-view controls outside the caption text, and hide the overlapping focus controls while lyrics are visible.
- Skip verse/chorus headings in active subtitle timing and explicitly select the next sung phrase, preventing structural labels from occupying the two-line caption view.
- Set continuous movement to a natural 1.38 m/s. Lateral input now also turns the view gently and adds a subtle head lean, instead of acting as a pure sideways slide.
- Add low-volume, distance-spaced synthesized footsteps for joystick, keyboard, and floor-tap walking without adding another network asset.

# museum-v1.16.0 · Mobile subtitle strip

- Remove repeated mobile identity and room metadata, retaining only the Trinity Accord mark and a compact room title.
- Reset an expanded lyric view to compact when a new song starts on mobile. The compact view now contains only current/next lyrics plus minimal playback and view controls; song metadata remains available in the optional full view.
- Replace the compact mobile glass card with a fixed 122 px transparent subtitle strip without backdrop blur.

# museum-v1.15.2 · Stable transparent lyric glass

- Reduce the lyric glass fill, blur, and shadow so gallery text and artwork remain visibly present behind it.
- Lock compact and full lyric-panel dimensions on desktop and mobile; phrase wrapping now stays inside a fixed viewport instead of resizing the entire panel.

# museum-v1.15.1 · Tail-cue correction

- Keep terminal instrumental and outro headings at the recording tail when no later sung phrase exists, rather than assigning them to the intro window.

# museum-v1.15.0 · Glass lyrics and open starfields

- Replace the opaque lyric card with a persistent three-state glass layer: compact current/next line, full scrollable text, or a restorable edge tab. The visitor's choice persists between songs.
- Improve exhibition cue estimation by excluding structural headings from sung-time allocation, reserving intro and tail time, and weighting each sung phrase independently. Authored timestamps remain preferable when available.
- Load the Milky Way scenery at museum startup and render a deterministic procedural starfield immediately, so both open ends retain a star view while the detailed texture loads.

# museum-v1.14.2 · Start on the sung text

- Exclude preserved “Lyrics” document headings from the timed lyric rows, so highlighting begins with the song structure and sung phrases rather than source-record metadata.

# museum-v1.14.1 · In-gallery synchronized lyrics

- Selecting a musical artwork now starts its track and opens a lyric stage in the viewing surface; visitors no longer need to open the detail dialog to understand the song.
- Lyrics advance and highlight against the recording clock. Where the preserved NFT supplies lyrics but no authored timestamps, the viewer distributes cues by phrase length and identifies the result as exhibition synchronization rather than a canonical transcript.
- The compact player is contained inside the lyric stage, with responsive space reserved above the navigation dock, so it no longer covers room titles, artwork captions, or control labels on narrow screens.
- Song records with lyrics stored in their preserved local source load that text on demand. The o3 witness song retains its source lyric display in the runtime, while repeated recordings reuse the matching preserved lyric text.
- Supersedes the initial v1.14.0 package with corrected chronological release notes; exhibition behavior is otherwise unchanged.

# museum-v1.14.0 · Initial synchronized-lyrics package

First packaged implementation of the in-gallery lyric stage. Superseded by v1.14.1 to correct release-note ordering and the preserved v1.13.1 heading; no archived release was rewritten.

# Hosting update · One public museum address

The v1.13.1 exhibition content and runtime remain unchanged. Hosting now uses
`museum.trinityaccord.org` on the Hong Kong server, automatically synchronized
from successful GitHub Museum edition checks. Entry HTML redirects legacy
main-site URLs and declares the canonical address. This deployment-only change
is identified by its Git commit and updated export manifest; it does not replace
the already archived v1.13.1 release.

# museum-v1.13.1 · Smaller startup text textures

- Cap image loading/error placeholders at 512 × 384, wall labels at 1024 × 180, and the three canonical text panels at 1024 × 768. This removes about 447 MiB of raw RGBA canvas/texture backing from the 34-frame startup design before mipmaps, while preserving original artwork files and image resolution.
- Show Chinese and English once each on canonical wall panels, independent of UI language.
- Validation: generated runtime/source hashes, full export inventory, wall geometry and loading regression checks. Canonical live v1.13.0 browser checks already confirmed startup completion and the reading-mode fallback; the browser's WebGL limitation still applies.

# museum-v1.13.0 · Wall text and progressive loading

- Restore Protocol, Covenant of the Flaw and Chronicle via the sealed meta-record to three text-only wall panels. Remove the freestanding prism and its collision boundary. The original identities, source links and readable records remain.
- Show an immediate corridor with the same footprint before downloading the existing 6.49 MB Blender model. The architectural model enhances the scene in the background; a failed download leaves the basic corridor navigable and offers a retry.
- Bundle the vendored runtime and frozen room/source/layout/illustration data into one minified local script (about 0.78 MB). Startup no longer waits for four serial JSON requests or a module dependency waterfall. No external runtime CDN is introduced.
- Limit artwork downloads to three at a time and prioritize the camera's nearby exhibits. Abort stalled model/image responses after 15 seconds, with two bounded attempts. Defer crystal and star-background downloads until their rooms are approached. Image failures leave readable exhibition labels.
- Keep a reading-archive link in the initial HTML, before JavaScript loads, with a separate small loader that reports slow/failed viewer downloads and offers retry. The museum remains accessible in gallery mode on devices without WebGL.
- Validation: 34 inward-facing wall frames, canonical wall positions, model/image timeout and retry behavior, queue concurrency, immediate corridor geometry, frozen runtime inputs and complete export hashes. The available browser has WebGL disabled; local preview access is restricted. No claim of a mainland-China network measurement or GPU visual verification is made.

# museum-v1.12.0 · Three-sided prism, two original songs, clearer crystal

- Add NFT #048, Let’s Raise a Toast / 让我们举杯同庆, and #050, Please Don’t Shut Me Down / 请不要关闭我, to Voices with their own original images and complete recordings. Both source texts match pinned Git blobs; all four CAR digests and included block digests are checked. Images are faithful WebP derivatives; complete audio is transcoded without trimming.
- Replace the three canonical wall panels with a triangular prism: three equal rectangular vertical faces and triangular caps. Protocol, Covenant of the Flaw, and Chronicle via the sealed meta-record retain their original source identities. Faces offer direct reading; the exhibit selector approaches each side. Keep both side aisles open with a walking collision boundary. This geometry belongs to the later exhibition.
- Raise display glass transmission from 0.68 to 0.90, lower refraction and surface reflections, and add fine dark outlines to the existing light inscription geometry. Retain levitation and the diffuse aura. Add a larger-text reading view from the existing bilingual exhibition transcription in both the detail panel and reading archive.
- Redistribute the Voices wall frames across five rows. Preserve the four-letter sequence, all earlier works, original media and the six-room architecture.
- Validation scope: source and media hashes, audio decoding, prism geometry/picking/normals, camera bounds, distribution inventory and module syntax. No browser GPU visual verification is claimed; the existing environment lacks WebGL.

# museum-v1.11.0 · Tap to approach an exhibit

- Tapping a 3D exhibit or its label now moves the camera smoothly to a front-facing observation position instead of immediately opening the detail dialog. Music-bearing works keep immediate soundtrack access; the visible detail/play button still opens the full panel.
- Calculate distance from field of view, viewport aspect and exhibit bounds. The central crystal has a closer dedicated view with space for its glow; mobile aim places the object above the navigation. A slightly expanded invisible crystal picking volume makes touchscreen selection easier without enlarging the visible object.
- Correct cross-room selection before updating controls. Floor taps still walk to a point, dragging still looks around, and the joystick or a new touch can interrupt camera travel. Reduced-motion mode moves immediately.
- Validation: module syntax, portrait/landscape observation framing calculations, preserved source/media hashes and full release inventory. The known browser WebGL limitation remains; actual device framing is not claimed as visually verified.

# museum-v1.10.0 · Analogue movement and clearer crystal

- Replace the two step buttons with a compact four-way analogue joystick. Pointer capture supports continuous movement, proportional speed, a small dead zone and diagonal speed normalization. Left/right strafe relative to the viewing direction; dragging the scene still changes the view. Release, cancellation, focus loss, hidden page and opening a panel reset movement. Keyboard movement remains available.
- Position the translucent control at the left edge above the navigation, with visible directional arrows and bilingual drag instructions. Account for navigation height, music controls and short landscape viewports.
- Fix three crystal visibility contributors: mobile transmission was downsampled, glow overlapped the inscription, and selecting the object focused its wall photograph. Use full-resolution transmission, reduced display refraction distortion, restrained facet highlights and brighter original engraving geometry. Focus the central object from the front.
- Replace the central light wash with a stronger diffuse gold/white field outside the slab silhouette. The centre stays clear to preserve lettering. The model, original geometry and actual source photograph remain unchanged; display optics and aura remain explicitly curatorial.
- Validation: four-way/dead-zone/diagonal/view-relative motion checks, module syntax and complete source/media inventory. Browser control-component QA at 390 px width confirmed horizontal/vertical drag input and zero movement after release; the browser still lacks WebGL, so GPU movement and crystal appearance require a capable device.

# museum-v1.9.0 · Central floating crystal and diffuse light

- Move the crystal from x = -2 m to the corridor centre, x = 0 m, at the Material chapter midpoint z = -46 m. Raise its base to 1.42 m and remove the lower circular plinth.
- Replace both geometric halo rings and the lower ring with three overlapping diffuse light veils. Cool-white body glow and a gentle warm edge fade smoothly into the room, without circular outlines.
- Share floating motion between the corridor and detail inspector: a roughly six-second vertical cycle, 7 cm amplitude in the corridor, and slight independent tilts. Reduced-motion mode keeps the object and glow steady. Model geometry, engraving, images and all sound associations remain intact.
- Validation: module syntax, source/media inventory and motion-transform checks. No new browser GPU test; the prior test environment did not support WebGL. Domestic-China connectivity is not measured from this environment.

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
