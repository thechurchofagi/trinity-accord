"""Package completed timelines; never accept missing files or estimated cues."""
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parents[1];D=P/'dist';source=json.loads((D/'data/lyrics-source.json').read_text());items=[];audit=[]
for e in source['items']:
 f=D/e['timelineFile'];raw=f.read_bytes();timeline=json.loads(raw)
 if timeline['schemaVersion']!='word-alignment-v2':raise ValueError('Unfinished timeline '+e['exhibitId'])
 words=[w for line in timeline['lines'] for w in line['words']]
 if any(w['end']<=w['start'] for w in words):raise ValueError('Zero-duration word '+e['exhibitId'])
 items.append({k:e[k] for k in ['exhibitId','audioSha256','duration','timelineFile']}|{'timelineSha256':hashlib.sha256(raw).hexdigest(),'lineCount':len(timeline['lines']),'wordCount':len(words)})
 audit.append({'exhibitId':e['exhibitId'],'wordCount':len(words),'lineCount':len(timeline['lines']),'weakAcousticWords':sum(w['acousticScore']<.12 for w in words),'flaggedLines':[{'line':i,'start':l['start'],'end':l['end'],'flags':l['reviewFlags']} for i,l in enumerate(timeline['lines']) if l['reviewFlags']]})
index={'schemaVersion':'lyrics-index-v1','edition':source['edition'],'items':items}
(D/'data/lyrics-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n')
report={'schemaVersion':'lyrics-audit-v1','edition':source['edition'],'status':'automatic-audio-alignment','manualListeningReviewed':False,'limitations':['Speech models can misplace sung consonants and sustained vowels.','Acoustic scores and recognizer disagreement are review signals, not calibrated accuracy.','A 20 ms model frame does not imply 20 ms alignment accuracy.'],'items':audit}
(D/'data/lyrics-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(len(items),'tracks;',sum(e['wordCount'] for e in items),'word times;',sum(e['weakAcousticWords'] for e in audit),'weak acoustic words marked for listening review.')
