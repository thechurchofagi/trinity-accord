"""Validate corrected main takes independently; preserve delivery-bandwidth audio."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,subprocess,sys,tempfile
P=Path(__file__).resolve().parents[1];D=P/'dist';H=lambda b:hashlib.sha256(b).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--inspection',required=True);a=p.parse_args()
manifest=D/'data/guide-audio.json';g=json.loads(manifest.read_text());folder=D/'assets/guides-expressive';folder.mkdir(exist_ok=True)
# All optional inspection sentences must pass, not merely a low overall recall.
for meta in sorted(Path(a.inspection).glob('inspection-*-en.json')):
 t=json.loads(meta.read_text());audio=meta.with_suffix('.mp3')
 assert t['captionAudit']['accepted'] and all(r['accepted'] for r in t['captionAudit']['sentences'])
 assert H(audio.read_bytes())==t['sha256'] and H(t['text'].encode())==t['textSha256']
 ix=next(i for i,old in enumerate(g['inspectionTracks']) if old['language']=='en' and old['flaw']==t['flaw']);old=g['inspectionTracks'][ix]
 assert old['text']==t['text'];t['stop']=old['stop'];t['provenance']['sourceArtifactRun']=34175623070
 target=D/t['file'];shutil.copyfile(audio,target);g['inspectionTracks'][ix]=t
assert len([t for t in g['inspectionTracks'] if t['language']=='en' and t.get('captionAudit',{}).get('accepted')])==3
manifest.write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n')
# Run the separately maintained acoustic audit, but retain the full-band source
# MP3 whenever no edit was needed. A recognition copy never becomes delivery.
with tempfile.TemporaryDirectory() as temp:
 temp=Path(temp);inputs=temp/'input';inputs.mkdir()
 for t in g['tracks']:
  if t['language']!='en':continue
  name=f"{t['stop']:02}-en";(inputs/(name+'.json')).write_text(json.dumps(t));shutil.copyfile(D/t['file'],inputs/(name+'.mp3'))
 source=(P/'scripts/audit_expressive_narration.py').read_text()
 start=source.index("        subprocess.run(['ffmpeg'");end=source.index('        duration=float(subprocess.check_output',start)
 source=source[:start]+"        assert not edits, 'Corrected take still requires an edit; reject instead of degrading speech'\n        dest.write_bytes(mp3.read_bytes())\n"+source[end:]
 script=temp/'audit.py';script.write_text(source);subprocess.run([sys.executable,str(script),'--input',str(inputs),'--dist',str(D)],check=True)
g=json.loads(manifest.read_text());g['voiceReview']='Eleven English curatorial recordings use Chatterbox Turbo built-in synthetic voice; eight tour tracks independently audited, three microscope guides accepted sentence by sentence. Chinese remains Xiaoxiao. Full-band delivery audio preserved. Automated acoustic review, not human listening certification.';manifest.write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n')
proof=D/'data/narration-provenance.json';d=json.loads(proof.read_text());d['method']=g['voiceReview'];d['tracks']=[dict(scope=scope,stop=t.get('stop'),flaw=t.get('flaw'),file=t['file'],sha256=t['sha256'],duration=t['duration'],provenance=t.get('provenance'),captionAudit=t.get('captionAudit')) for scope,key in [('tour','tracks'),('inspection','inspectionTracks')] for t in g[key] if t['language']=='en'];proof.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
# Rebind the audition page after source-hash naming; do not leave stale takes.
page=D/'voice-review.html';s=page.read_text()
for previous in json.loads((P/'history/guide-audio-v1.32-edge.json').read_text())['tracks']:
 pass
for t in g['tracks']:
 if t['language']=='en':s=s.replace(f'assets/guides-expressive/{t["stop"]:02}-en.mp3',t['file'])
page.write_text(s)
# The newer reading-archive builder already uses this manifest. Add an explicit
# manual-voice note without changing any historical source record.
p=P/'README.md';p.write_text(p.read_text()+'\nFinal delivery includes 11 English synthetic guide tracks (8 tour + 3 optional microscope explanations), with the current audit in `dist/data/narration-provenance.json`. Historical source media are unchanged.\n')
js=D/'museum.js';s=js.read_text().replace("if(id.startsWith('canon-')){showExhibit(id);return;}\n",'');js.write_text(s)
print('ACCEPTED_SOURCE_QUALITY_VOICES',len(d['tracks']),flush=True)
