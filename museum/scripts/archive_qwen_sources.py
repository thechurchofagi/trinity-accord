"""Preserve exact PCM takes so future edits need not regenerate the whole visit."""
import argparse, hashlib, json, re, zipfile
from pathlib import Path

P=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('--cache',required=True);a.add_argument('--output',required=True);args=a.parse_args()
cache=Path(args.cache);provenance=json.loads((P/'dist/data/narration-provenance.json').read_text())
assert provenance['schema']=='trinity-museum.narration-provenance.v2'
files=[]
for review in provenance['paragraphReviews']:
 key=review['key'];assert re.fullmatch('[0-9a-f]{64}',key)
 wav=cache/(key+'.wav');assert hashlib.sha256(wav.read_bytes()).hexdigest()==review['audioSha256']
 files.extend([(wav,'takes/'+wav.name),(cache/(key+'.json'),'takes/'+key+'.json')])
for f in ['render_qwen_guides.py','audit_qwen_paragraphs.py','finalize_qwen_review.py','retake_qwen_paragraph.py','refresh_visit_voices.py','archive_qwen_sources.py']:
 files.append((P/'scripts'/f,'museum/scripts/'+f))
for f in ['scene/tour-script.json','scene/voice-review-zh.md','dist/data/guide-audio.json','dist/data/narration-provenance.json']:
 files.append((P/f,'museum/'+f))
manifest=[dict(path=name,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p,name in files]
readme='''# Museum v1.33 · Qwen narration sources

Exact 24 kHz mono PCM16 paragraph takes, supplied text, independent recognition
reviews and the scripts used to assemble 24 bilingual tour recordings and six
microscope recordings. The English voice is Aiden; Chinese is Serena.

The model weights are not included. The pinned model and revision are recorded
in museum/dist/data/narration-provenance.json. Retain unchanged takes when making
future edits. The producer reads the flaw-script literal from refresh_visit_voices.py;
do not run that legacy external-service producer to rebuild these local recordings.

Takes are concatenated with 0.16-second pauses and mastered to the documented MP3
settings by render_qwen_guides.py. Subtitle timings are measured paragraph bounds
with proportional short cues. Recognition reviews are not human listening certification.
The published MP3 recordings remain in the existing trinity-accord Git repository.
'''
with zipfile.ZipFile(args.output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p,name in files:z.write(p,name)
 z.writestr('README.md',readme);z.writestr('archive-manifest.json',json.dumps(manifest,indent=2)+'\n')
print('VOICE_SOURCE_ARCHIVE',args.output,Path(args.output).stat().st_size,'bytes',len(provenance['paragraphReviews']),'paragraphs')
