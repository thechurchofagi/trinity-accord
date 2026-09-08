# Guided visit and display repair

This follow-up preserves the canonical sources, source images, recordings and all
three public microscope photographs. It changes the exhibition and its controls.

- Only Close tour exits guidance. Mouse hover does not turn; left-button drag
  turns. Keyboard, wheel, joystick, room selection and Escape retain the guide.
  Keyboard letters are normalized by physical key and button focus is accepted.
- All automatic transfers use collision-aware walking at the existing walking
  speed, with the quiet distance-triggered footsteps. Reduced motion affects
  decorative motion; it no longer teleports the camera. Manual input can defer
  the next automatic camera movement without ending narration.
- Music preloads during its introduction and starts on narration completion.
  The three archived flaw images each receive their existing matching audio;
  inspection advances on completion, rather than dropping the explanations.
  The route budget is 580 seconds; loading, blocked audio or unfinished walking
  and narration may extend real elapsed time. No recording was re-synthesized.
- The numbered work/song strip is removed. Plaque width follows each actual
  frame; height is consistent, with chain date, event title and song title.
  Event labels are later concise labels in curation.json, not changes to records.
- Both short Originals display their complete original text, including bilingual
  passages and historical placeholders. The third retains a reading guide and
  direct full-text view. Text panels use inset metal/mineral backing.
- The shared architecture is rebaked with pale floors, pearl walls, brighter
  ceilings and substantially stronger fill in crystal and waiting rooms.
  Runtime mineral finishes add metre-scaled microdetail and restrained physical
  reflections; the original crystal retains its material and verified geometry.
- The user's phone screenshot showed empty legacy mounts in front of current
  paintings. Production serves the mutable GLB with max-age=86400. Runtime builds
  now pin model hashes in versioned requests, verify downloaded model bytes, and
  reject architecture that does not match the six-room layout. A stale model
  cannot silently replace the immediate six-room shell.

Validation: distribution/source verification and all 13 Node regression programs
pass locally. The updated CI additionally checks real keyboard/mouse behaviour,
desktop/mobile near views, and unaccelerated playback of eight tour recordings
plus all three microscope explanations. Cloud preview lacks WebGL; its gallery
fallback is not used as 3D acceptance. CI rendered results remain pending until
recorded against the final PR head.

Normal rebuild: node scripts/build_runtime.mjs, then python scripts/build_archive.py.
Architecture rebuild: Python 3.11 with bpy 4.5.3, scene/build_spatial_gallery.py.
Rollback: revert this PR as one change and regenerate the distribution, retaining
versioned model requests when serving any prior architecture.
