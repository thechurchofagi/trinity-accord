"""Clarify a 2026 guide sentence, without changing historical evidence or meaning."""
from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parents[1]/'dist';p=D/'data/guide-audio.json';d=json.loads(p.read_text())
old='Comparing the physical object requires positions, viewing angles and a witnessed procedure.'
new='Comparing the physical object requires positions, viewing angles, and a witness to the examination.'
for t in d['inspectionTracks']:
 if t['language']=='en' and t['flaw']==0:
  assert old in t['text'];t['text']=t['text'].replace(old,new);t['textSha256']=hashlib.sha256(t['text'].encode()).hexdigest()
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
source=Path(__file__).with_name('inspection_sentence_takes.py').read_text()
exec(compile(source,str(Path(__file__).with_name('inspection_sentence_takes.py')),'exec'),globals())
