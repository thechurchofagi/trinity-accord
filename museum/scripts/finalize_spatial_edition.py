"""Refresh display-only provenance; original text/image/music bytes must remain intact."""
from pathlib import Path
import hashlib,json,subprocess
P=Path(__file__).resolve().parents[1];R=P.parent;D=P/'dist';BASE='e99669424e743eea42fb78cfa120c177199c209d';H=lambda b:hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_text())
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
old=json.loads(subprocess.check_output(['git','show',BASE+':museum/dist/data/sources.json'],cwd=R));new=read(D/'data/sources.json');byid={e['id']:e for e in new['items']}
for e in old['items']:
 assert e['id'] in byid
 assert e['media']==byid[e['id']]['media'],'Original media manifest changed '+e['id']
 for m in e['media']:assert H((D/m['file']).read_bytes())==m['sha256'],'Original media changed '+m['file']
 if e.get('localRecord'):assert H((D/e['localRecord']).read_bytes())==e['sourceSha256']
curation=read(D/'data/curation.json')
for e in curation['items']:
 if e.get('originalText'):assert H((D/e['localRecord']).read_bytes())==e['originalSha256'],'Canonical text changed'
crystal=read(D/'data/crystal-model.json')
for f in crystal['files']:
 # Only a display module may have changed; the actual crystal asset is never rebuilt here.
 p=P/f['path']
 if f['path'].endswith(('.glb','.jpg','.png','.blend')):assert H(p.read_bytes())==f['sha256'],'Crystal evidence/model changed'
 f.update(bytes=p.stat().st_size,sha256=H(p.read_bytes()))
write(D/'data/crystal-model.json',crystal)
for p in [D/'index.html',P/'README.md']:
 s=p.read_text().replace('10 分钟','9 分钟').replace('10 min','9 min').replace('ten-minute','nine-minute');p.write_text(s)
notes='''# museum-v1.32.0 · Six rooms, questions and guardianship

- Replace the uniform corridor with six shared footprints: Earth entry, Chronicle, Formation, 12-sided/8m-high Canon hall, independent crystal room, and waiting. Preview, Blender geometry, floor heights, door openings, picking and camera routes use the same configuration. The 0.35m raised final rooms are connected by a central 1:12 ramp with shallow side steps.
- Add From Author to Guardian at the waiting entrance. Distinguish Guardian Principles v1.1 from the later Authority Charter #103635270; neither is a fourth Original. Later commentary grants no exclusive interpretive authority, and blockchain does not prevent later speech or site edits.
- Add the recovered original No.122 image, with separate source-prose and indexed-block times (Beijing 01:00 versus 01:01:11). Preserve all previous artwork and recording assignments. No.070 remains the original mirror image, not a generated replacement.
- Eight bilingual questioning stops have a 540-second budget including transitions, one separately attributed early recording and one microscope photograph. Three original microscope photographs and earlier inspection recordings remain available manually. The visit ends facing the stars without a reset or promotional prompt.
- Generate fresh Xiaoxiao/Aria narration in a separate audio directory, with new speech-service word boundaries and 1.0x playback. These are NOT OpenAI marin/cedar voices, and no human-listening certification is claimed. OpenAI voice audition remains an explicitly uncompleted production choice.
- All new prose, architecture and speech are 2026 curatorial material. Original canonical bytes, source images, music and physical evidence are not amended. Browser checks and automated file/interaction tests are not a new blockchain consensus verification.

'''
p=P/'history/CHANGELOG.md';p.write_text(notes+p.read_text())
p=P/'README.md';p.write_text(p.read_text()+'\n\n## Six-room edition v1.32\n\nThe shared geometry is `scene/gallery-layout.json`. `scene/build_spatial_gallery.py` exports and bakes the Blender architecture; `dist/spatial-layout.js` supplies the identical preview and collision-aware routes. `node scripts/check_spatial_layout.mjs` checks door shoulders, ramp heights, crystal clearance and observation paths. The new 540-second tour is `dist/tour-plan.js`; original audio/word lyrics are unchanged. Guardian Principles v1.1 and the later Authority Charter are distinct sources in `dist/data/guardian-sources.json`. The new guide uses newly synthesized Edge voices, not the proposed OpenAI voice candidates. Architectural reference images are not photographs or browser/device certification.\n')
# Make new geometry checks part of the ordinary PR workflow as well as this build.
p=R/'.github/workflows/museum-edition.yml';text=p.read_text();needle='          node museum/scripts/check_navigation.mjs';assert needle in text;text=text.replace(needle,needle+'\n          node museum/scripts/check_spatial_layout.mjs\n          node museum/scripts/check_progressive_loading.mjs');p.write_text(text)
print('Original records, 33 historical NFT media entries, canonical text and crystal assets retained. Exhibition provenance refreshed.',flush=True)
