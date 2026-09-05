# Trinity Accord Museum / 三位一体协定三维展馆

This directory is a later exhibition of the existing Trinity Accord. The three Bitcoin Originals remain unchanged. The six rooms are a **2026 curatorial route**, not six historical or canonical formation stages.

## Start locally

Use Python 3: `python -m http.server 8000 --directory dist`, then open the local server in a modern browser. No package installation, account, model API, or build process is needed to visit this static edition. Three.js 0.180.0 is vendored with its MIT license. Native ES modules require HTTP serving; opening `index.html` directly with `file://` is not supported.

`python scripts/validate.py` checks content, local references, media digests and the release inventory. `node --check dist/museum.js` checks the application syntax. The museum does not import dependencies from the parent site's package.json.

## Ownership and boundaries

- GitHub `thechurchofagi/trinity-accord`, under `museum/`, holds the maintained exhibition source and history. There is no separately managed user repository.
- ChatGPT Sites hosts an exported copy of this directory. Its provider-managed source transport is deployment infrastructure, not a replacement archive. `.openai/hosting.json` identifies that hosted Site; do not initialize a second Site on upgrades.
- Original NFT records, Bitcoin texts and evidence stay in their existing locations. This edition pins its source commit and includes display copies with provenance and transformation records.
- Original website links remain the entry points for verification, current status, Echo and Guardian applications. This application writes no record and makes no AI-agent oath, signature, or submission.
- Ambient pulses are exhibition animation, not heartbeat telemetry. No reception totals are simulated.

## Layout

| Path | Role |
|---|---|
| `dist/data/sources.json` | Stable exhibit IDs, historical metadata, pinned source URLs and media processing records |
| `dist/data/rooms.json` | Versioned room sequence, positions, color scheme, labels and guide scripts |
| `dist/data/narration.json` | Guide texts, voice/model identifiers and generated audio hashes |
| `dist/data/release-manifest.json` | File inventory and SHA-256 values for this edition |
| `dist/museum.js` | Browser scene, controls, exhibit panels, playback and bounded digest comparison |
| `dist/assets/` | Explicitly attributed exhibition copies and generated guide tracks |
| `dist/archive.html` | Readable edition archive without WebGL |
| `content/` | Curatorial rationale and migration conventions |
| `history/` | Edition history and validation scope |
| `scripts/` | Source preparation, guide synthesis and validation utilities |

## Preserve, then upgrade

Keep stable exhibit IDs through changes. Treat original media, exhibition derivatives, and newly produced curatorial material separately. Update content and schema versions deliberately; retain migration notes if the renderer or schema changes. Preserve a release package before a major redesign. An old edition must use its recorded snapshot; do not silently inject today's data into an archived edition.

For restoration, retain the entire `dist/` directory, not just GitHub links or an R2 bucket name. This edition includes its own browser modules, image copies, music copies, guide audio, and JSON data. External source links need a network connection; the scene and local exhibit files work on a local HTTP server without those services. Browser/GPU compatibility in the indefinite future is not guaranteed.

## Media and rights

Original artworks, lyrics, photos and music retain their original rights and attribution; inclusion does not license them under the Three.js license. The user authorized this exhibition of their project. Curatorial narration is newly generated with Kokoro af_heart and marked as such. No cloned human voice is used. Models and guide audio are not original historical artifacts.

## Deployment/export

The Site working directory is an export of `museum/`. Changes must be copied back into the same repository path through a PR and tied to the corresponding GitHub commit. Sites has its own deployment commit; record the mapping in release/deployment notes rather than pretending it is the same Git commit. Never place source credentials or runtime secrets in either repository.

The first edition is privately hosted for owner review. Public access is a separate audience setting. Existing root website pages and evidence workflows are not rewritten by this directory.
