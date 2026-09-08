"""Finalize display metadata after the candidate passed acoustic review."""
from pathlib import Path
import json
P=Path(__file__).resolve().parents[1];D=P/'dist'
guides=json.loads((D/'data/guide-audio.json').read_text())
assert all(t.get('captionAudit',{}).get('accepted') for t in guides['tracks'] if t['language']=='en'),'English acceptance incomplete'
p=D/'museum.js';s=p.read_text()
s=s.replace("if(id.startsWith('canon-')){showExhibit(id);return;}\n",'')
s=s.replace('当前自动导览配音为 Xiaoxiao（中文）与 Aria（英文）；早期录音档案使用 Kokoro af_heart。','中文导览为 Xiaoxiao，英文导览采用 Chatterbox Turbo 内置合成声音；没有克隆真人声音。新英文录音经过独立语音识别复核，具体差异与处理记录可在配音清单中查看；这不是人工听审保证。早期录音保留为展览历史。')
s=s.replace('Recorded narration uses Xiaoxiao (Chinese) and Aria (English); earlier guides use Kokoro af_heart.','Chinese narration uses Xiaoxiao. English uses the built-in synthetic Chatterbox Turbo voice, not a cloned person. New English audio has independent speech-recognition checks with differences and edits recorded in the narration manifest; this is not human listening certification. Earlier recordings remain part of exhibition history.')
s=s.replace("${link('./data/sources.json',tx('查看素材清单','Inspect the source manifest'))}","${link('./data/sources.json',tx('查看素材清单','Inspect the source manifest'))}${link('./data/guide-audio.json',tx('配音模型、字幕与声学复核','Narration model, captions and acoustic review'))}")
s=s.replace('Blender corridor render','Blender architectural reference').replace('EXHIBITION 2026 · V1.29.0','EXHIBITION 2026 · V1.32.0')
p.write_text(s)
# Reading archive and 3D museum must describe the same eight spoken stops.
p=P/'scripts/build_archive.py';s=p.read_text()
s=s.replace("P=Path(__file__).resolve().parents[1];D=P/'dist';esc=html.escape", "P=Path(__file__).resolve().parents[1];D=P/'dist';esc=html.escape\nguides=json.loads((D/'data/guide-audio.json').read_text())['tracks']\nplan=(D/'tour-plan.js').read_text();stops=json.loads(plan.split('export const tourStops=',1)[1].split(';\\nexport const tourDuration',1)[0])")
s=s.replace("<audio controls preload=\"none\" src=\"assets/guide-'+r['id']+'.mp3\"></audio><small>2026 English AI narration / 英文 AI 配音 · Kokoro af_heart</small>","")
needle=" for id in r['exhibits']:"
insert=''' for stop_no,stop in enumerate(stops):
  if stop['room']!=rooms['rooms'].index(r):continue
  parts.append('<details class="guide-reading"><summary>提问式导览 / Question-led guide · '+str(stop_no+1)+'</summary>')
  for lang in ['zh','en']:
   track=next(t for t in guides if t['stop']==stop_no and t['language']==lang)
   model=track.get('provenance',{}).get('model',track['voice'])
   parts.append('<p lang="'+('zh-CN' if lang=='zh' else 'en')+'">'+esc(track['text'])+'</p><audio controls preload="none" src="'+esc(track['file'])+'"></audio><small>AI-generated narration · '+esc(model)+' · '+esc(track['voice'])+'</small>')
  parts.append('</details>')
 for id in r['exhibits']:'''
assert needle in s;s=s.replace(needle,insert)
s=s.replace('href="data/narration.json">配音记录','href="data/guide-audio.json">当前配音、字幕与声学核对')
p.write_text(s)
# Preserve the historical design notes; record what was actually produced now.
p=P/'history/CHANGELOG.md';old=p.read_text();p.write_text('''## v1.32 final candidate refinement

- Use the completed six-room shared Blender model with distinct palettes, denoised baked lighting, an offset crystal-room exit, larger readable Originals, a restrained crystal aura, and an unobstructed black-sky ending.
- Bind eight new English Chatterbox Turbo recordings by exact script hash after independent Whisper small.en + VAD review. Reordered tour stops cannot silently receive the wrong recording. The audio audit records recognition differences. This is not a human listening certificate or a guarantee of perfect recognition.
- Keep Chinese Xiaoxiao recordings, all original musical recordings/lyrics and microscope evidence. Replace stale voice credits and point the reading archive to the same current bilingual guide tracks.
- Keep the nine-minute tour, original mirror image, anniversary timing distinctions and later non-amending guardianship display. First clicks approach each Original consistently; details remain a deliberate second action.
- Validate the static distribution, geometry, source hashes and desktop/mobile Chromium viewports. Actual Android/iOS hardware and live Zoom transmission remain outside automated acceptance.

'''+old)
p=P/'README.md';p.write_text(p.read_text()+'''\n\n## Final narration and acceptance\n\nThe current English voice is **Chatterbox Turbo**, rendered offline with its built-in synthetic conditionals; no person was cloned. Chinese uses Xiaoxiao. `dist/data/guide-audio.json` identifies exact track hashes, model revisions and current captions. `dist/data/expressive-audio-audit.json` records the independent Whisper small.en + VAD pass; this is automated QA, not human listening certification. The audio model does not run in a visitor's browser.\n\n`python3 scripts/check_browser.py` checks six rooms, seven key near views, guardianship links, actual language switching and asset/page errors at desktop and phone-size viewports. `node scripts/check_spatial_layout.mjs` checks shared geometry and collision-safe observation routes. `python3 scripts/validate.py` verifies original sources and the frozen distribution. Keep the PR unmerged until its final head passes normal repository CI.\n''')
print('FINAL_DISPLAY_METADATA_UPDATED',flush=True)
