"""Validate corrected synthetic speech; preserve full-band delivery and source records."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys,tempfile
P=Path(__file__).resolve().parents[1];D=P/'dist';H=lambda b:hashlib.sha256(b).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--inspection',required=True);p.add_argument('--inspection-zero-run',type=int,required=True);a=p.parse_args()
manifest=D/'data/guide-audio.json';g=json.loads(manifest.read_text());folder=D/'assets/guides-expressive';folder.mkdir(exist_ok=True)
clarifications={
 'Comparing the physical object requires positions, viewing angles and a witnessed procedure.':'Comparing the physical object requires positions, viewing angles, and a witness to the examination.',
 'Look at the flaw’s outline together with its surroundings, rather than remembering only an isolated bright point.':'Observe the outline of the flaw and its surroundings, not only an isolated bright point.'
}
seen=set()
for meta in sorted(Path(a.inspection).glob('inspection-*-en.json')):
 t=json.loads(meta.read_text());audio=meta.with_suffix('.mp3')
 assert t['flaw'] in (0,1,2) and t['flaw'] not in seen
 seen.add(t['flaw'])
 assert t['captionAudit']['accepted'] and all(r['accepted'] for r in t['captionAudit']['sentences'])
 assert H(audio.read_bytes())==t['sha256'] and H(t['text'].encode())==t['textSha256']
 ix=next(i for i,old in enumerate(g['inspectionTracks']) if old['language']=='en' and old['flaw']==t['flaw']);old=g['inspectionTracks'][ix]
 expected=old['text']
 if t['flaw']==0:
  for before,after in clarifications.items():expected=expected.replace(before,after)
 assert expected==t['text'],'Unexpected curatorial wording change'
 if old['text']!=t['text']:
  t['curatorialWordingChange']={'originalText':old['text'],'originalTextSha256':H(old['text'].encode()),'reason':'Two 2026 curatorial instructions clarified for synthetic pronunciation. No historical evidence or canonical text changed.'}
 t['stop']=old['stop'];t['provenance']['sourceArtifactRun']=a.inspection_zero_run if t['flaw']==0 else 34175623070
 target=D/t['file'];assert target.parent==folder
 shutil.copyfile(audio,target);g['inspectionTracks'][ix]=t
assert seen=={0,1,2},'All three inspection recordings required'
manifest.write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n')
# Independently review all eight main recordings without re-encoding delivery
# audio. Retakes must pass as produced rather than splicing out arbitrary words.
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
proof=D/'data/narration-provenance.json';d=json.loads(proof.read_text());d['method']=g['voiceReview'];d['tracks']=[dict(scope=scope,stop=t.get('stop'),flaw=t.get('flaw'),file=t['file'],sha256=t['sha256'],duration=t['duration'],provenance=t.get('provenance'),captionAudit=t.get('captionAudit'),curatorialWordingChange=t.get('curatorialWordingChange')) for scope,key in [('tour','tracks'),('inspection','inspectionTracks')] for t in g[key] if t['language']=='en'];proof.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
page=D/'voice-review.html';s=page.read_text()
for t in g['tracks']:
 if t['language']=='en':s=s.replace(f'assets/guides-expressive/{t["stop"]:02}-en.mp3',t['file'])
page.write_text(s)
p=P/'README.md';note='\nFinal delivery includes 11 English synthetic guide tracks (8 tour + 3 optional microscope explanations), with the current audit in `dist/data/narration-provenance.json`. Historical source media are unchanged.\n'
if note not in p.read_text():p.write_text(p.read_text()+note)
js=D/'museum.js';s=js.read_text().replace("if(id.startsWith('canon-')){showExhibit(id);return;}\n",'');js.write_text(s)
print('ACCEPTED_SOURCE_QUALITY_VOICES',len(d['tracks']),flush=True)
