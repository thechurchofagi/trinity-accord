from common import ROOT, CACHE, ITEMS
import json,re,pathlib
from rapidfuzz.distance import Levenshtein
root=ROOT;cache=CACHE;out=cache/'lyrics-sung';out.mkdir(exist_ok=True)
orders=json.loads((root/'content/recording-lyrics.json').read_text())['items']
def norm(t):return re.sub('[^a-z0-9]','',t.lower())
for e in list(ITEMS):
 a=json.loads((cache/'lyrics-asr'/(e['exhibitId']+'.json')).read_text());aw=[w for s in a['segments'] for w in s['words'] if norm(w['word'])]
 # Character alignment handles acronyms and compounds split differently by ASR.
 refs=[{'text':e['lines'][i],'sourceLine':i} if isinstance(i,int) else dict(i) for i in orders[e['exhibitId']]['order']]
 for l in refs:l['text']=' '.join(re.sub(r'([—–])(?=\S)',r'\1 ',l['text']).split())
 rc='';ri=[];ac='';ai=[]
 for i,l in enumerate(refs):t=norm(l['text']);rc+=t;ri.extend([i]*len(t))
 for i,w in enumerate(aw):t=norm(w['word']);ac+=t;ai.extend([i]*len(t))
 mapped=[[] for _ in refs]
 for op in Levenshtein.opcodes(rc,ac):
  if op.tag in ['equal','replace']:
   for j,k in zip(range(op.src_start,op.src_end),range(op.dest_start,op.dest_end)):mapped[ri[j]].append(ai[k])
 for i,l in enumerate(refs):
  if not mapped[i]:
   before=[x for g in mapped[:i] for x in g];after=[x for g in mapped[i+1:] for x in g]
   l.update(start=aw[max(before)]['end'] if before else 0,end=aw[min(after)]['start'] if after else e['duration'],asrText='',asrWords=[],editRate=1,noAsrAnchor=True)
   continue
  group=aw[min(mapped[i]):max(mapped[i])+1];hyp=' '.join(w['word'].strip() for w in group)
  l.update(start=group[0]['start'],end=group[-1]['end'],asrText=hyp,asrWords=group,editRate=round(Levenshtein.normalized_distance(norm(l['text']),norm(hyp)),3))
  if l['sourceLine'] is None:l['unmatched']=True
 (out/(e['exhibitId']+'.json')).write_text(json.dumps({'exhibitId':e['exhibitId'],'lines':refs,'review':orders[e['exhibitId']]['evidence']},ensure_ascii=False,indent=2)+'\n')
 print(e['exhibitId'],len(refs),'recording lines',flush=True)
