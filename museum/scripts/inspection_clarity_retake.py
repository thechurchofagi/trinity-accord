"""Clarify two later curatorial sentences; historical evidence is unchanged."""
from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parents[1]/'dist';p=D/'data/guide-audio.json';d=json.loads(p.read_text())
changes={
 'Comparing the physical object requires positions, viewing angles and a witnessed procedure.':'Comparing the physical object requires positions, viewing angles, and a witness to the examination.',
 'Look at the flaw’s outline together with its surroundings, rather than remembering only an isolated bright point.':'Observe the outline of the flaw and its surroundings, not only an isolated bright point.'
}
for t in d['inspectionTracks']:
 if t['language']=='en' and t['flaw']==0:
  original=t['text']
  for old,new in changes.items():
   assert old in t['text'],old
   t['text']=t['text'].replace(old,new)
  t['textSha256']=hashlib.sha256(t['text'].encode()).hexdigest()
  t['curatorialWordingChange']={'originalText':original,'originalTextSha256':hashlib.sha256(original.encode()).hexdigest(),'reason':'Clarify synthetic pronunciation of witnessed procedure and the possessive flaw’s outline; same physical comparison instructions, not a change to historical evidence.'}
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
source=Path(__file__).with_name('inspection_sentence_takes.py').read_text()
exec(compile(source,str(Path(__file__).with_name('inspection_sentence_takes.py')),'exec'),globals())
